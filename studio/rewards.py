"""
GRPO-aligned multi-faceted reward signal for RLHF preference data.

Implements a composite reward function inspired by Fin-o1 (NeurIPS 2025):
    r = alpha_acc * r_acc + alpha_logic * r_logic
      + alpha_format * r_format + alpha_length * (r_length * r_acc)

The length reward is gated by accuracy to prevent rewarding verbose but
wrong responses — a key insight from the Fin-o1 paper's multi-faceted
reward design for financial reasoning tasks.

References:
    - Fin-o1 (2025): "Fin-o1: A Multi-Stage Financial Reasoning Model
      with Group Relative Policy Optimization"
    - FinanceQA (2025): "FinanceQA: A Benchmark for Evaluating Financial
      Analysis Capabilities of LLMs"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Reward signal dataclass
# ---------------------------------------------------------------------------

@dataclass
class RewardSignal:
    """Multi-faceted reward for GRPO-aligned preference scoring.

    Each dimension is in [0, 1].  The composite score follows the Fin-o1
    formula: length is gated by accuracy so concise-but-wrong answers
    are not rewarded.
    """

    accuracy: float = 0.5
    logic: float = 0.5
    format_quality: float = 0.5
    length: float = 0.5

    # Per-dimension explanations (optional, for annotation UI)
    explanations: Dict[str, str] = field(default_factory=dict)

    def composite(
        self,
        alpha_acc: float = 0.40,
        alpha_logic: float = 0.30,
        alpha_format: float = 0.15,
        alpha_length: float = 0.15,
    ) -> float:
        """GRPO-aligned composite reward.

        r = α₁·r_acc + α₂·r_logic + α₃·r_format + α₄·(r_length · r_acc)

        Default weights mirror Fin-o1: accuracy-dominant with length gated
        by accuracy.
        """
        return (
            alpha_acc * self.accuracy
            + alpha_logic * self.logic
            + alpha_format * self.format_quality
            + alpha_length * (self.length * self.accuracy)
        )

    def to_dict(self) -> dict:
        return {
            "accuracy": round(self.accuracy, 4),
            "logic": round(self.logic, 4),
            "format_quality": round(self.format_quality, 4),
            "length": round(self.length, 4),
            "composite": round(self.composite(), 4),
            "explanations": self.explanations,
        }


# ---------------------------------------------------------------------------
# Heuristic reward functions
# ---------------------------------------------------------------------------

_LOGIC_KEYWORDS = frozenset([
    "therefore", "because", "thus", "assuming", "given", "since",
    "implies", "consequently", "however", "although", "whereas",
    "if", "then", "leads to", "results in", "due to",
])

_STRUCTURE_MARKERS = re.compile(
    r"(?:^|\n)(?:#{1,4}\s|[-*]\s|\d+\.\s|>\s|\|)", re.MULTILINE
)

_FINANCIAL_TERMS = frozenset([
    "revenue", "ebitda", "margin", "eps", "fcf", "wacc", "dcf",
    "pe ratio", "ev/ebitda", "beta", "alpha", "sharpe", "volatility",
    "growth rate", "discount rate", "terminal value", "npv", "irr",
    "roe", "roa", "roic", "debt", "equity", "leverage", "cash flow",
])


def compute_accuracy(text: str, reference: Optional[str] = None) -> float:
    """Accuracy reward: overlap with reference answer.

    Returns 0.5 (neutral) when no reference is available.
    """
    if not reference:
        return 0.5

    text_tokens = set(text.lower().split())
    ref_tokens = set(reference.lower().split())

    if not ref_tokens:
        return 0.5

    overlap = len(text_tokens & ref_tokens) / len(ref_tokens)
    # Scale to [0, 1] — full overlap → 1.0
    return min(overlap * 1.2, 1.0)


def compute_logic(text: str) -> float:
    """Logic/reasoning chain coherence reward.

    Measures density of logical connectives and explicit reasoning steps.
    """
    words = text.lower().split()
    if not words:
        return 0.0

    keyword_hits = sum(1 for w in words if w in _LOGIC_KEYWORDS)
    sentences = max(len(re.split(r'[.!?]+', text)), 1)

    # Ratio of logical connectives per sentence (ideal: ~1 per sentence)
    density = keyword_hits / sentences
    score = min(density / 1.0, 1.0)

    # Bonus for numbered reasoning steps
    numbered_steps = len(re.findall(r'(?:^|\n)\s*\d+[.)]\s', text))
    if numbered_steps >= 2:
        score = min(score + 0.15, 1.0)

    return score


def compute_format(text: str) -> float:
    """Format/structure quality reward.

    Checks for structured output: headers, bullets, tables, consistent
    paragraph length.
    """
    if not text.strip():
        return 0.0

    structure_hits = len(_STRUCTURE_MARKERS.findall(text))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    n_paras = max(len(paragraphs), 1)

    # Structure score: at least some formatting used
    structure_score = min(structure_hits / max(n_paras, 3), 1.0)

    # Paragraph consistency: penalize very uneven paragraph lengths
    if n_paras >= 2:
        lengths = [len(p) for p in paragraphs]
        avg_len = sum(lengths) / n_paras
        variance = sum((l - avg_len) ** 2 for l in lengths) / n_paras
        cv = (variance ** 0.5) / max(avg_len, 1)
        consistency = max(1.0 - cv, 0.0)
    else:
        consistency = 0.5

    return 0.6 * structure_score + 0.4 * consistency


def compute_length(text: str, ideal_min: int = 150, ideal_max: int = 600) -> float:
    """Length/conciseness reward.

    Ideal range for financial analysis: 150-600 words.  Too short
    or too long is penalized.
    """
    word_count = len(text.split())

    if word_count < ideal_min:
        return max(word_count / ideal_min, 0.1)
    elif word_count > ideal_max:
        return max(ideal_max / word_count, 0.2)
    return 1.0


def compute_reward(
    output_text: str,
    prompt: str = "",
    reference: Optional[str] = None,
    rubric_scores: Optional[Dict[str, float]] = None,
) -> RewardSignal:
    """Compute multi-faceted reward from an LLM output.

    If rubric_scores are provided (e.g., from human eval or grading engine),
    they are used directly.  Keys should be 'accuracy', 'logic',
    'format_quality', 'length' — each in [0, 100].

    Otherwise, heuristic functions estimate each dimension.
    """
    explanations: Dict[str, str] = {}

    if rubric_scores:
        accuracy = rubric_scores.get("accuracy", 50) / 100
        logic = rubric_scores.get("logic", 50) / 100
        fmt = rubric_scores.get("format_quality", 50) / 100
        length = rubric_scores.get("length", 50) / 100
        explanations["source"] = "rubric_scores"
    else:
        accuracy = compute_accuracy(output_text, reference)
        logic = compute_logic(output_text)
        fmt = compute_format(output_text)
        length = compute_length(output_text)
        explanations["source"] = "heuristic"

    return RewardSignal(
        accuracy=accuracy,
        logic=logic,
        format_quality=fmt,
        length=length,
        explanations=explanations,
    )


def annotate_pair_with_rewards(
    pair: dict,
    reference: Optional[str] = None,
) -> dict:
    """Add GRPO reward scores to an existing preference pair dict.

    Modifies the pair in-place, adding chosen_score and rejected_score
    as composite reward values, plus a reward_details sub-dict.
    """
    chosen_reward = compute_reward(pair["chosen"], pair.get("prompt", ""), reference)
    rejected_reward = compute_reward(pair["rejected"], pair.get("prompt", ""), reference)

    pair["chosen_score"] = round(chosen_reward.composite(), 4)
    pair["rejected_score"] = round(rejected_reward.composite(), 4)
    pair["reward_details"] = {
        "chosen": chosen_reward.to_dict(),
        "rejected": rejected_reward.to_dict(),
        "reward_type": "grpo_multifaceted",
    }

    return pair
