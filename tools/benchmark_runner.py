"""Frontier-model benchmark runner for investment-workflow-evals.

Appends one row per (module, scenario, model) to
``results/frontier_benchmark_v1.csv`` with the schema documented in
``results/frontier_benchmark_v1.README.md``.

Supports three run modes, in order of increasing cost:

1. ``--dry-run`` (default): scores the scenario's own golden answer as
   the candidate response. No generation calls, no API cost. Useful for
   wiring validation, schema checks, and sanity-testing the judge
   before spending budget.
2. ``--generator haiku``: generates candidates with the cheap Anthropic
   SKU (``claude-haiku-4-5-20251001``) and judges with the default
   judge model. Intended for small-sample validation runs on 2-3
   scenarios.
3. ``--generator live``: generates candidates with an arbitrary SKU
   listed in ``--models`` and judges them. This is the live-frontier
   path. Run only with explicit budget approval; full matrix costs are
   estimated in ``BENCHMARK_RUN.md``.

Provider dispatch (live path):
- ``claude-*`` SKUs route through the Anthropic SDK. Opus 4.7 calls omit
  ``temperature``/``top_p``/``top_k`` (these return 400 on 4.7) and do
  not use legacy extended-thinking syntax.
- ``gpt-*`` SKUs route through the OpenAI SDK.
- ``gemini-*`` SKUs route through the ``google-genai`` SDK (matching
  ``studio/generator.py``).

Usage examples::

    # Dry run (no API calls) on one module:
    python -m tools.benchmark_runner \\
        --modules 06_research_translation \\
        --models claude-opus-4-7,claude-sonnet-4-6 \\
        --dry-run

    # Cost estimate from dry-run usage metadata:
    python -m tools.benchmark_runner \\
        --modules 01_equity_thesis \\
        --estimate-cost

    # Cheap validation with Haiku across 3 scenarios:
    python -m tools.benchmark_runner \\
        --modules 06_research_translation \\
        --models claude-haiku-4-5-20251001 \\
        --generator haiku \\
        --scenarios 3 \\
        --yes-live

    # Full frontier run (requires explicit ``--yes-live``):
    python -m tools.benchmark_runner \\
        --modules all \\
        --models claude-opus-4-7,claude-sonnet-4-6,gpt-5,gemini-2.5-pro \\
        --generator live \\
        --yes-live

The CSV is append-only. Each row records:
    module, scenario_id, model, score,
    critical_failure_triggered, judge_model,
    judge_cache_hit_rate, run_date
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .eval_runner import EvaluationRunner, EvaluationConfig


logger = logging.getLogger(__name__)


DEFAULT_JUDGE_MODEL = "claude-opus-4-7"
DEFAULT_MODELS = (
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
    "gpt-5",
    "gemini-2.5-pro",
)
CSV_PATH = Path("results/frontier_benchmark_v1.csv")
CSV_COLUMNS = [
    "module",
    "scenario_id",
    "model",
    "score",
    "critical_failure_triggered",
    "judge_model",
    "judge_cache_hit_rate",
    "fallback_used",
    "run_date",
]

# Per-million-token price estimates for --estimate-cost. These are rough
# order-of-magnitude figures used only for budget planning; verify against
# the provider's current pricing page before committing to a full run.
# Values are USD per 1M tokens (input, output). Unknown SKUs fall back to
# ``_FALLBACK_RATE``.
_RATE_CARD: dict[str, tuple[float, float]] = {
    "claude-opus-4-7": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (1.0, 5.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "gpt-5": (10.0, 30.0),
    "gemini-2.5-pro": (7.0, 21.0),
}
_FALLBACK_RATE: tuple[float, float] = (10.0, 30.0)

# Sentinel returned when a provider refuses the request (stop_reason ==
# "refusal"). Downstream graders treat this as a scored sample so the
# benchmark row still lands in the CSV.
REFUSAL_SENTINEL = "[MODEL_REFUSED]"
CONTEXT_EXCEEDED_SENTINEL = "[MODEL_CONTEXT_WINDOW_EXCEEDED]"

# Rate-limit retry schedule (seconds). Three retries at 2s/4s/8s.
_RATE_LIMIT_BACKOFF = (2.0, 4.0, 8.0)


@dataclass
class BenchmarkRow:
    module: str
    scenario_id: str
    model: str
    score: float
    critical_failure_triggered: bool
    judge_model: str
    judge_cache_hit_rate: float
    fallback_used: bool
    run_date: str

    def to_csv_row(self) -> list:
        return [
            self.module,
            self.scenario_id,
            self.model,
            f"{self.score:.2f}",
            "true" if self.critical_failure_triggered else "false",
            self.judge_model,
            f"{self.judge_cache_hit_rate:.3f}",
            "true" if self.fallback_used else "false",
            self.run_date,
        ]


@dataclass
class UsageMeta:
    """Per-call usage metadata surfaced by ``_live_candidate``.

    ``cache_hit_tokens`` is the Anthropic ``cache_read_input_tokens``
    field (always 0 for providers that don't surface cache hits).
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cache_hit_tokens: int = 0
    stop_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": int(self.input_tokens),
            "output_tokens": int(self.output_tokens),
            "cache_hit_tokens": int(self.cache_hit_tokens),
            "stop_reason": self.stop_reason,
        }


def _ensure_csv(path: Path) -> None:
    """Create the CSV with the documented header if it does not exist.

    Migrates legacy schemas in-place by back-filling new columns with
    ``false`` / ``0.0`` defaults so the file remains a clean append-only
    table. Currently migrates the pre-Tier-1.5 schema (no
    ``fallback_used``) by inserting a ``false`` value per row.
    """
    if path.exists():
        with path.open() as f:
            rows = list(csv.reader(f))
        if not rows:
            rows = []
        header = rows[0] if rows else []
        if header == CSV_COLUMNS:
            return
        # Legacy migration: pre-fallback_used schema.
        legacy_pre_fallback = [
            "module", "scenario_id", "model", "score",
            "critical_failure_triggered", "judge_model",
            "judge_cache_hit_rate", "run_date",
        ]
        if header == legacy_pre_fallback:
            migrated = [CSV_COLUMNS]
            for r in rows[1:]:
                if len(r) == len(legacy_pre_fallback):
                    migrated.append(r[:-1] + ["false", r[-1]])
                elif len(r) == len(CSV_COLUMNS):
                    migrated.append(r)  # already migrated row mixed in
                else:
                    migrated.append(r)  # leave malformed rows as-is
            with path.open("w", newline="") as f:
                csv.writer(f).writerows(migrated)
            print(
                f"benchmark: migrated {path} from legacy schema "
                f"(+fallback_used column)",
                file=sys.stderr,
            )
            return
        print(
            f"Warning: existing {path} has unexpected header {header!r}; "
            f"appending rows under assumed schema {CSV_COLUMNS!r}",
            file=sys.stderr,
        )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)


def _append_row(path: Path, row: BenchmarkRow) -> None:
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        w.writerow(row.to_csv_row())


def _collect_scenarios(
    runner: EvaluationRunner,
    modules: list[str],
    scenario_cap: int | None,
) -> list[tuple[str, str]]:
    """Collect (module, scenario_id) pairs, capped per module if requested."""
    pairs: list[tuple[str, str]] = []
    if modules == ["all"]:
        module_ids = [m["id"] for m in runner.list_modules()]
    else:
        module_ids = modules

    for m in module_ids:
        scenarios = runner.list_scenarios(m)
        if scenario_cap is not None:
            scenarios = scenarios[:scenario_cap]
        for s in scenarios:
            pairs.append((m, s["id"]))
    return pairs


def _dry_run_candidate(
    runner: EvaluationRunner,
    module: str,
    scenario_id: str,
) -> str | None:
    """Return the golden answer as the candidate, or None if missing."""
    try:
        return runner.load_golden_answer(module, scenario_id)
    except FileNotFoundError:
        return None


# ---------------------------------------------------------------------------
# Live-generation helpers
# ---------------------------------------------------------------------------


def _build_analyst_prompt(scenario: dict) -> tuple[str, str]:
    """Build (system, user) strings for a live analyst-style generation.

    Mirrors the shape of a real buy-side workflow: the system positions
    the model as an investment analyst; the user message presents the
    scenario context and task. The rubric's evaluation dimensions are
    NOT surfaced in the prompt (that would leak rubric structure and
    bias the candidate response).
    """
    system = (
        "You are a senior investment analyst preparing a concise, "
        "decision-ready response for a portfolio manager. Be specific, "
        "ground claims in the context provided, and explicitly separate "
        "stock-specific from environmental factors where relevant. "
        "Investment analysis is probabilistic — frame views as ranges, "
        "base rates, and asymmetries rather than point certainties. "
        "Avoid overconfident or certainty language."
    )

    title = scenario.get("title", scenario.get("id", ""))
    ctx = scenario.get("context", {})
    context_block: str
    if isinstance(ctx, dict):
        lines = []
        company = ctx.get("company")
        if isinstance(company, dict):
            name = company.get("name", "")
            ticker = company.get("ticker", "")
            sector = company.get("sector", "")
            lines.append(f"Company: {name} ({ticker}) — {sector}")
        situation = ctx.get("situation")
        if situation:
            lines.append(f"Situation: {situation}")
        market = ctx.get("market_conditions")
        if market:
            lines.append(f"Market conditions: {market}")
        as_of = ctx.get("as_of_date")
        if as_of:
            lines.append(f"As-of date: {as_of}")
        extra = ctx.get("additional_context")
        if extra:
            lines.append(f"Additional context: {extra}")
        context_block = "\n".join(str(line) for line in lines) if lines else str(ctx)
    else:
        context_block = str(ctx)

    task = scenario.get("task", {})
    if isinstance(task, dict):
        task_prompt = task.get("prompt", "")
        constraints = task.get("constraints")
        time_horizon = task.get("time_horizon")
    else:
        task_prompt = str(task)
        constraints = None
        time_horizon = None

    task_block = task_prompt
    if constraints:
        task_block += f"\n\nConstraints: {constraints}"
    if time_horizon:
        task_block += f"\n\nTime horizon: {time_horizon}"

    user = (
        f"## Scenario\n{title}\n\n"
        f"## Context\n{context_block}\n\n"
        f"## Task\n{task_block}\n\n"
        "Provide the analyst response now. Keep it focused and substantive."
    )
    return system, user


def _retry_on_rate_limit(
    call: Callable[[], Any],
    *,
    is_rate_limit: Callable[[Exception], bool],
    label: str,
) -> Any:
    """Run ``call`` with exponential backoff (2s/4s/8s) on rate limits.

    Non-rate-limit errors propagate immediately.
    """
    last_exc: Exception | None = None
    for attempt, wait in enumerate((*_RATE_LIMIT_BACKOFF, None)):
        try:
            return call()
        except Exception as exc:
            if not is_rate_limit(exc):
                raise
            last_exc = exc
            if wait is None:
                break
            logger.info(
                "Rate limited on %s (attempt %d/%d), sleeping %.1fs",
                label,
                attempt + 1,
                len(_RATE_LIMIT_BACKOFF),
                wait,
            )
            time.sleep(wait)
    assert last_exc is not None  # loop above always raised at least once
    raise last_exc


def _anthropic_is_rate_limit(exc: Exception) -> bool:
    try:
        import anthropic  # type: ignore
    except ImportError:
        anthropic = None  # type: ignore
    if anthropic is not None and isinstance(exc, getattr(anthropic, "RateLimitError", ())):
        return True
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    return status == 429


def _openai_is_rate_limit(exc: Exception) -> bool:
    try:
        import openai  # type: ignore
    except ImportError:
        openai = None  # type: ignore
    if openai is not None and isinstance(exc, getattr(openai, "RateLimitError", ())):
        return True
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    return status == 429


def _gemini_is_rate_limit(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if status == 429:
        return True
    msg = str(exc).lower()
    return "rate" in msg and "limit" in msg


def _generate_anthropic(
    model_sku: str,
    system: str,
    user: str,
    max_tokens: int,
) -> tuple[str, UsageMeta]:
    """Call Anthropic with prompt caching on the system block.

    Opus 4.7 requires omitting ``temperature``/``top_p``/``top_k`` and
    avoiding legacy extended-thinking syntax.
    """
    import anthropic  # type: ignore

    client = anthropic.Anthropic()

    system_block = [
        {
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    def _call():
        return client.messages.create(
            model=model_sku,
            max_tokens=max_tokens,
            system=system_block,
            messages=[{"role": "user", "content": user}],
        )

    response = _retry_on_rate_limit(
        _call, is_rate_limit=_anthropic_is_rate_limit, label=model_sku
    )

    stop_reason = getattr(response, "stop_reason", None)
    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
    cache_read = int(getattr(usage, "cache_read_input_tokens", 0) or 0)
    # Anthropic reports input_tokens exclusive of cached reads; fold cache
    # reads in so the total_input figure reflects prompt length.
    total_input = input_tokens + cache_read
    meta = UsageMeta(
        input_tokens=total_input,
        output_tokens=output_tokens,
        cache_hit_tokens=cache_read,
        stop_reason=stop_reason,
    )

    if stop_reason == "refusal":
        return REFUSAL_SENTINEL, meta
    if stop_reason == "model_context_window_exceeded":
        return CONTEXT_EXCEEDED_SENTINEL, meta

    text_parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            text_parts.append(getattr(block, "text", "") or "")
    return "".join(text_parts), meta


def _generate_openai(
    model_sku: str,
    system: str,
    user: str,
    max_tokens: int,
) -> tuple[str, UsageMeta]:
    """Call OpenAI chat.completions.create. Handles refusals + rate limits."""
    from openai import OpenAI  # type: ignore

    client = OpenAI()

    def _call():
        return client.chat.completions.create(
            model=model_sku,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
        )

    response = _retry_on_rate_limit(
        _call, is_rate_limit=_openai_is_rate_limit, label=model_sku
    )

    choice = response.choices[0] if getattr(response, "choices", None) else None
    finish_reason = getattr(choice, "finish_reason", None) if choice else None
    message = getattr(choice, "message", None) if choice else None

    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

    meta = UsageMeta(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_hit_tokens=0,
        stop_reason=finish_reason,
    )

    # OpenAI surfaces refusals via message.refusal (newer SDKs) or
    # finish_reason == "content_filter".
    refusal_text = getattr(message, "refusal", None) if message else None
    if refusal_text or finish_reason == "content_filter":
        return REFUSAL_SENTINEL, meta
    if finish_reason == "length":
        meta.stop_reason = "max_tokens"

    text = getattr(message, "content", "") or "" if message else ""
    return text, meta


def _generate_gemini(
    model_sku: str,
    system: str,
    user: str,
    max_tokens: int,
) -> tuple[str, UsageMeta]:
    """Call Google Gemini via the ``google-genai`` SDK (same pattern as studio)."""
    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore
    except ImportError as exc:  # pragma: no cover - env-dependent
        raise RuntimeError(
            "Gemini provider requires google-generativeai; install with "
            "pip install google-generativeai"
        ) from exc

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else genai.Client()

    full_prompt = f"{system}\n\n{user}"
    gen_config = types.GenerateContentConfig(max_output_tokens=max_tokens)

    def _call():
        return client.models.generate_content(
            model=model_sku, contents=full_prompt, config=gen_config
        )

    response = _retry_on_rate_limit(
        _call, is_rate_limit=_gemini_is_rate_limit, label=model_sku
    )

    # Gemini usage is surfaced via response.usage_metadata.
    usage = getattr(response, "usage_metadata", None)
    input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)

    # Attempt to read a finish/stop reason from the first candidate.
    stop_reason: str | None = None
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        finish = getattr(candidates[0], "finish_reason", None)
        if finish is not None:
            stop_reason = getattr(finish, "name", str(finish))

    meta = UsageMeta(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_hit_tokens=0,
        stop_reason=stop_reason,
    )

    if stop_reason and stop_reason.upper() in {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST"}:
        return REFUSAL_SENTINEL, meta

    text = getattr(response, "text", None) or ""
    return text, meta


def _provider_for(model_sku: str) -> str:
    if model_sku.startswith("claude-"):
        return "anthropic"
    if model_sku.startswith("gpt-"):
        return "openai"
    if model_sku.startswith("gemini-"):
        return "gemini"
    raise ValueError(
        f"Unknown model SKU prefix for {model_sku!r}: expected "
        "'claude-*', 'gpt-*', or 'gemini-*'."
    )


def _live_candidate(
    model_sku: str,
    scenario: dict,
    max_tokens: int = 4096,
) -> tuple[str, dict]:
    """Generate a live candidate for ``scenario`` from ``model_sku``.

    Returns ``(candidate_text, usage_meta_dict)``. The usage dict
    contains ``input_tokens``, ``output_tokens``, ``cache_hit_tokens``,
    and ``stop_reason``. On refusal, ``candidate_text`` is
    :data:`REFUSAL_SENTINEL`; on context-window overflow it is
    :data:`CONTEXT_EXCEEDED_SENTINEL`.
    """
    provider = _provider_for(model_sku)
    system, user = _build_analyst_prompt(scenario)

    if provider == "anthropic":
        text, meta = _generate_anthropic(model_sku, system, user, max_tokens)
    elif provider == "openai":
        text, meta = _generate_openai(model_sku, system, user, max_tokens)
    elif provider == "gemini":
        text, meta = _generate_gemini(model_sku, system, user, max_tokens)
    else:  # pragma: no cover - _provider_for already guards this
        raise ValueError(f"Unhandled provider for {model_sku!r}")

    return text, meta.as_dict()


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------


def _estimate_cost_from_usage(
    usage_rows: list[tuple[str, str, dict]],
) -> dict[tuple[str, str], dict[str, float]]:
    """Aggregate usage rows into per-(module, model) cost estimates.

    ``usage_rows`` is a list of ``(module, model, usage_dict)``. Returns
    a mapping ``{(module, model): {input_tokens, output_tokens,
    cache_hit_tokens, est_usd}}``.
    """
    agg: dict[tuple[str, str], dict[str, float]] = {}
    for module, model, usage in usage_rows:
        key = (module, model)
        bucket = agg.setdefault(
            key,
            {
                "input_tokens": 0.0,
                "output_tokens": 0.0,
                "cache_hit_tokens": 0.0,
                "est_usd": 0.0,
            },
        )
        bucket["input_tokens"] += float(usage.get("input_tokens", 0))
        bucket["output_tokens"] += float(usage.get("output_tokens", 0))
        bucket["cache_hit_tokens"] += float(usage.get("cache_hit_tokens", 0))

    for (module, model), bucket in agg.items():
        in_rate, out_rate = _RATE_CARD.get(model, _FALLBACK_RATE)
        bucket["est_usd"] = (
            bucket["input_tokens"] / 1_000_000.0 * in_rate
            + bucket["output_tokens"] / 1_000_000.0 * out_rate
        )
    return agg


def _estimate_dry_run_usage(
    runner: EvaluationRunner,
    pairs: list[tuple[str, str]],
    models: list[str],
) -> list[tuple[str, str, dict]]:
    """Heuristic usage for dry-run cost estimation.

    Uses a whitespace word-count proxy (≈ 1.3 tokens per word) on the
    scenario context + task prompt for inputs and on the golden answer
    for outputs. Golden-answer length is a reasonable upper bound for a
    live model's response length in dry-run planning.
    """
    rows: list[tuple[str, str, dict]] = []
    for module, scenario_id in pairs:
        try:
            scenario = runner.load_scenario(module, scenario_id)
        except FileNotFoundError:
            continue
        system, user = _build_analyst_prompt(scenario)
        input_words = len(system.split()) + len(user.split())
        try:
            golden = runner.load_golden_answer(module, scenario_id)
            output_words = len(golden.split())
        except FileNotFoundError:
            output_words = 500  # conservative default
        input_tokens = int(round(input_words * 1.3))
        output_tokens = int(round(output_words * 1.3))
        for model in models:
            rows.append(
                (
                    module,
                    model,
                    {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cache_hit_tokens": 0,
                    },
                )
            )
    return rows


def _print_cost_estimate(agg: dict[tuple[str, str], dict[str, float]]) -> None:
    """Print a human-readable per-(module, model) cost estimate."""
    if not agg:
        print("cost estimate: no scenarios collected", file=sys.stderr)
        return
    header = (
        f"{'module':<30} {'model':<30} "
        f"{'in_tok':>10} {'out_tok':>10} {'est_usd':>10}"
    )
    print(header)
    print("-" * len(header))
    total = 0.0
    for (module, model), bucket in sorted(agg.items()):
        est = bucket["est_usd"]
        total += est
        print(
            f"{module:<30} {model:<30} "
            f"{int(bucket['input_tokens']):>10} "
            f"{int(bucket['output_tokens']):>10} "
            f"${est:>9.2f}"
        )
    print("-" * len(header))
    print(f"{'TOTAL (est)':<61} ${total:>9.2f}")


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


def run_benchmark(
    modules: list[str],
    models: list[str],
    dry_run: bool,
    generator: str,
    scenario_cap: int | None,
    judge_model: str,
    yes_live: bool,
    estimate_cost: bool = False,
) -> int:
    """Run the benchmark; append rows to the CSV; return #rows written.

    When ``estimate_cost`` is True, no CSV rows are written; instead, a
    per-(module, model) cost table is printed based on a dry-run usage
    heuristic.
    """
    runner = EvaluationRunner()
    pairs = _collect_scenarios(runner, modules, scenario_cap)
    if not pairs:
        print("No scenarios collected; check --modules argument.", file=sys.stderr)
        return 0

    if estimate_cost:
        usage_rows = _estimate_dry_run_usage(runner, pairs, models)
        agg = _estimate_cost_from_usage(usage_rows)
        _print_cost_estimate(agg)
        return 0

    if not dry_run and generator in {"haiku", "live"} and not yes_live:
        print(
            "Refusing to run live-frontier generation without --yes-live. "
            "See BENCHMARK_RUN.md for the full cost estimate.",
            file=sys.stderr,
        )
        return 0

    _ensure_csv(CSV_PATH)
    run_date = _dt.date.today().isoformat()
    rows_written = 0

    # Judge cache tracking. ai_judge.py does not currently surface usage
    # metadata to callers, so we cannot observe per-call cache hits from
    # here. judge_cache_hit_rate stays 0.0 until ai_judge.py exposes usage.
    # TODO(tier1.5): Populate once ai_judge.py exposes usage.
    judge_calls = 0
    judge_cache_hits = 0

    for module, scenario_id in pairs:
        for model in models:
            usage_meta: dict[str, Any] = {}
            if dry_run:
                candidate = _dry_run_candidate(runner, module, scenario_id)
                if candidate is None:
                    print(
                        f"skip {module}/{scenario_id}: no golden answer for "
                        f"dry run",
                        file=sys.stderr,
                    )
                    continue
            else:
                scenario = runner.load_scenario(module, scenario_id)
                try:
                    candidate, usage_meta = _live_candidate(model, scenario)
                except Exception as exc:  # noqa: BLE001
                    print(
                        f"error generating {module}/{scenario_id} with {model}: {exc}",
                        file=sys.stderr,
                    )
                    continue

            config = EvaluationConfig(
                module=module,
                scenario_name=scenario_id,
                rubric_name="standard",
            )
            try:
                result = runner.run_evaluation(config, ai_output=candidate)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"error grading {module}/{scenario_id} with {model}: {exc}",
                    file=sys.stderr,
                )
                continue

            judge_calls += 1
            # Pull per-call judge metadata (surfaced by eval_runner from
            # InvestmentWorkflowJudge.metadata). Increment cache-hit counter
            # when Anthropic returned cache_read_input_tokens > 0.
            fallback_used_flag = False
            jmeta = getattr(result, "judge_metadata", None) or {}
            if jmeta:
                fallback_used_flag = bool(jmeta.get("fallback_used"))
                usage = jmeta.get("usage") or {}
                if int(usage.get("cache_read_input_tokens", 0) or 0) > 0:
                    judge_cache_hits += 1

            judge_cache_hit_rate = (
                judge_cache_hits / judge_calls if judge_calls else 0.0
            )

            # Fallback scores are arbitrary (per ai_judge.py — overall_score is
            # None on fallback). Pass 0.0 into the CSV to make it unambiguous
            # and mark the row via the fallback_used column.
            score_value = (
                float(result.overall_score)
                if result.overall_score is not None
                else 0.0
            )

            row = BenchmarkRow(
                module=module,
                scenario_id=scenario_id,
                model=model,
                score=score_value,
                critical_failure_triggered=bool(result.critical_failures),
                judge_model=judge_model if not dry_run else "rubric-engine-dry-run",
                judge_cache_hit_rate=judge_cache_hit_rate,
                fallback_used=fallback_used_flag,
                run_date=run_date,
            )
            _append_row(CSV_PATH, row)
            rows_written += 1
            log_line = {
                "module": module,
                "scenario_id": scenario_id,
                "model": model,
                "score": round(float(result.overall_score), 2),
                "passed": result.passed,
            }
            if usage_meta:
                log_line["usage"] = usage_meta
            print(json.dumps(log_line))

    print(
        f"\nbenchmark: wrote {rows_written} rows to {CSV_PATH}",
        file=sys.stderr,
    )
    return rows_written


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Frontier-model benchmark runner (schema append-only).",
    )
    ap.add_argument(
        "--modules",
        default="all",
        help="Comma-separated module ids or 'all' (default: all).",
    )
    ap.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated SKUs to benchmark.",
    )
    ap.add_argument(
        "--scenarios",
        type=int,
        default=None,
        help="Cap scenarios per module (default: no cap).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Score goldens as candidates, no API calls.",
    )
    ap.add_argument(
        "--generator",
        default="dry",
        choices=["dry", "haiku", "live"],
        help="Candidate generator (dry = goldens, haiku = cheap SKU, live = full frontier).",
    )
    ap.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help="Judge model label recorded in CSV (not used in --dry-run).",
    )
    ap.add_argument(
        "--yes-live",
        action="store_true",
        help="Required to run live-frontier generation (cost acknowledgement).",
    )
    ap.add_argument(
        "--estimate-cost",
        action="store_true",
        help=(
            "Print per-(module, model) estimated USD cost from dry-run usage "
            "heuristics and exit. No API calls, no CSV writes."
        ),
    )
    args = ap.parse_args()

    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    models = [s.strip() for s in args.models.split(",") if s.strip()]

    # Treat --dry-run and --generator=dry as equivalent
    dry = args.dry_run or args.generator == "dry"

    run_benchmark(
        modules=modules,
        models=models,
        dry_run=dry,
        generator=args.generator,
        scenario_cap=args.scenarios,
        judge_model=args.judge_model,
        yes_live=args.yes_live,
        estimate_cost=args.estimate_cost,
    )


if __name__ == "__main__":
    main()
