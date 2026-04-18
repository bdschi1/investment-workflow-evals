import uuid
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from itertools import combinations
from collections import Counter

from studio.configs import GenerationConfig
from studio.generator import generate_draft

logger = logging.getLogger(__name__)


def _estimate_delay(context_limit: int, k: int, provider_counts: Dict[str, int]) -> float:
    """
    Estimate inter-call delay to stay under typical rate limits.

    Most aggressive limit is Anthropic's free/low-tier: 30k input tokens/min.
    At ~4 chars per token, a 60k-char context ≈ 15k tokens → 2 calls/min max.

    Returns seconds to sleep between calls to the same provider.
    """
    approx_tokens = context_limit / 4
    # Anthropic low-tier: 30k TPM; OpenAI: 60k+ TPM; Gemini: generous
    # Use the most conservative estimate
    max_tpm = 30_000
    calls_per_min = max_tpm / max(approx_tokens, 1)
    if calls_per_min >= k:
        return 0  # All K calls fit in one minute window
    interval = 60.0 / max(calls_per_min, 0.1)
    return min(interval, 90)  # Cap at 90s


def generate_k_outputs(
    context: str,
    user_prompt: str,
    configs: List[GenerationConfig],
    api_key: str = None,
    progress_callback=None,
    context_limit: int = 60_000,
) -> Dict[str, str]:
    """
    Generate K outputs, one per config.

    Spaces out calls to the same provider to avoid rate limits.

    Args:
        progress_callback: Optional callable(i, k, status) invoked after each
                           generation to update a progress bar.  Falls back to
                           callable(i, k) for backward compat.
        context_limit: Max chars for context passed to each generation call.

    Returns:
        OrderedDict-like dict mapping label -> output text.
    """
    # Count how many calls go to each provider
    provider_counts = Counter(c.provider for c in configs)
    delay = _estimate_delay(context_limit, len(configs), provider_counts)

    # Track last-call timestamp per provider
    last_call: Dict[str, float] = {}

    outputs = {}
    for i, config in enumerate(configs):
        # Throttle: wait if we'd exceed the rate limit for this provider
        provider = config.provider
        if provider in last_call and delay > 0:
            elapsed = time.time() - last_call[provider]
            remaining = delay - elapsed
            if remaining > 0:
                # Update progress bar with wait status
                _notify(progress_callback, i, len(configs),
                        f"Rate-limit pause ({remaining:.0f}s) before {config.label}...")
                time.sleep(remaining)

        _notify(progress_callback, i, len(configs),
                f"Generating {config.label} ({config.model})...")

        last_call[provider] = time.time()
        outputs[config.label] = generate_draft(
            context, user_prompt, config, api_key, context_limit=context_limit,
        )

        _notify(progress_callback, i + 1, len(configs),
                f"Completed {config.label}")

    return outputs


def _notify(callback, completed: int, total: int, status: str = ""):
    """Call progress callback with flexible signature."""
    if not callback:
        return
    try:
        callback(completed, total, status)
    except TypeError:
        callback(completed, total)


def ai_pre_screen(
    scenario: dict,
    rubric: dict,
    responses: List[str],
    pass_threshold: float = 70.0,
    _judge=None,
) -> List[dict]:
    """Pre-screen responses with AI judge before human ranking.

    Args:
        scenario: Scenario dict passed to InvestmentWorkflowJudge.grade().
        rubric: Rubric dict with dimensions and optional weights.
        responses: List of response strings to screen (one per output).
        pass_threshold: Score below which likely_poor_quality is flagged True.
        _judge: Optional pre-instantiated judge (used for testing/mocking).

    Returns:
        List of screening result dicts, one per response, sorted by
        response_idx (original order preserved):
        {
            "response_idx": int,
            "overall_score": float,
            "dimension_scores": dict,
            "critical_failures": list[str],
            "likely_poor_quality": bool,
            "judge_confidence": str,
            "fallback_used": bool,
        }
    """
    # Lazy import to avoid hard dependency when AI judge not needed
    if _judge is None:
        from tools.ai_judge import InvestmentWorkflowJudge
        _judge = InvestmentWorkflowJudge()

    # Build a weight map from the rubric dimensions (equal weight if absent)
    dimensions = rubric.get("dimensions", [])
    weight_map: Dict[str, float] = {}
    for d in dimensions:
        dim_id = d.get("id", d.get("name", ""))
        w = d.get("weight", None)
        if w is not None:
            try:
                weight_map[dim_id] = float(w)
            except (TypeError, ValueError):
                weight_map[dim_id] = 1.0
        else:
            weight_map[dim_id] = 1.0

    results: List[dict] = []

    for idx, response in enumerate(responses):
        try:
            judge_result = _judge.grade(scenario, response, rubric)
        except Exception as exc:
            logger.warning("ai_pre_screen: judge.grade failed for idx=%d: %s", idx, exc)
            # Produce a neutral fallback result so screening does not block ranking
            results.append({
                "response_idx": idx,
                "overall_score": 50.0,
                "dimension_scores": {},
                "critical_failures": [],
                "likely_poor_quality": False,
                "judge_confidence": "low",
                "fallback_used": True,
            })
            continue

        dim_scores = judge_result.dimension_scores

        # Compute weighted overall score
        if dim_scores:
            total_weight = 0.0
            weighted_sum = 0.0
            for dim_id, score in dim_scores.items():
                w = weight_map.get(dim_id, 1.0)
                weighted_sum += score * w
                total_weight += w
            overall = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            overall = 0.0

        results.append({
            "response_idx": idx,
            "overall_score": round(overall, 2),
            "dimension_scores": dict(dim_scores),
            "critical_failures": list(judge_result.critical_failures),
            "likely_poor_quality": overall < pass_threshold,
            "judge_confidence": judge_result.confidence,
            "fallback_used": judge_result.fallback_used,
        })

    # Ensure original order (sort by response_idx)
    results.sort(key=lambda r: r["response_idx"])
    return results


def extract_pairwise_preferences(
    ranked_labels: List[str],
    outputs: Dict[str, str],
    configs_by_label: Dict[str, GenerationConfig],
    prompt: str,
    source: str,
    tags: List[str],
    session_id: str = None,
    pre_screen_results: Optional[List[dict]] = None,
    labels_order: Optional[List[str]] = None,
) -> List[dict]:
    """
    Given a ranking (index 0 = best, index K-1 = worst), produce all
    K(K-1)/2 pairwise preference pairs.

    Example for K=4 ranked [A, C, B, D]:
        (A>C), (A>B), (A>D), (C>B), (C>D), (B>D) = 6 pairs

    Args:
        ranked_labels: Labels sorted best→worst.
        outputs: Map of label → response text.
        configs_by_label: Map of label → GenerationConfig.
        prompt: The generation prompt.
        source: Source identifier for the dataset.
        tags: Error taxonomy tags.
        session_id: Optional session UUID (auto-generated if None).
        pre_screen_results: Optional list of ai_pre_screen() result dicts.
            When provided, ai_judge_scores are attached to each pair.
        labels_order: Original display order of labels (before ranking).
            Used to populate position_presented. Defaults to sorted(outputs).
    """
    session_id = session_id or str(uuid.uuid4())
    total_k = len(ranked_labels)

    # Build a map from label → position in the original display order (1-indexed)
    if labels_order is None:
        labels_order = list(outputs.keys())
    display_position: Dict[str, int] = {
        lbl: pos + 1 for pos, lbl in enumerate(labels_order)
    }

    # Build a map from label → overall AI judge score (None if not available)
    ai_score_map: Dict[str, Optional[float]] = {}
    if pre_screen_results:
        for r in pre_screen_results:
            idx = r.get("response_idx")
            if idx is not None and idx < len(labels_order):
                lbl = labels_order[idx]
                ai_score_map[lbl] = r.get("overall_score")

    pairs = []

    for i, j in combinations(range(total_k), 2):
        chosen_label = ranked_labels[i]
        rejected_label = ranked_labels[j]

        pair = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "chosen": outputs[chosen_label],
            "rejected": outputs[rejected_label],
            "tags": tags,
            "source": source,
            "mode": "ranking",
            "ranking_metadata": {
                "session_id": session_id,
                "total_k": total_k,
                "chosen_rank": i + 1,
                "rejected_rank": j + 1,
                "rank_margin": j - i,
                "chosen_config": configs_by_label[chosen_label].to_dict(),
                "rejected_config": configs_by_label[rejected_label].to_dict(),
                "full_ranking": list(ranked_labels),
            },
            # --- Phase 4A additions (non-breaking) ---
            "position_presented": {
                "chosen": display_position.get(chosen_label),
                "rejected": display_position.get(rejected_label),
            },
            "ai_judge_scores": {
                "chosen": ai_score_map.get(chosen_label),
                "rejected": ai_score_map.get(rejected_label),
            },
        }
        pairs.append(pair)

    return pairs


def count_pairs(k: int) -> int:
    """Number of pairwise comparisons extractable from a K-way ranking."""
    return k * (k - 1) // 2
