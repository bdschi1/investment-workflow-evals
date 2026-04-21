"""
AI-as-judge for investment workflow evaluation.

Replaces the hardcoded 75.0 stub in GradingEngine._score_with_llm with
a real Anthropic API call using tool_use for structured output.

prompt_version: 1.1.0
prompt_date: 2026-04-21

Changes in 1.1.0 (Tier-1 Issue #5 — fallback observability + model unhardcoding):
- Every fallback trigger (retry exhausted, JSON/parse error, validation error,
  tool-use missing, refusal, context-window exceeded) now emits a structured
  ``_logger.warning`` (or ``error``) with ``scenario``/``attempt``/``error_type``/``model``.
- ``JudgeResult.metadata`` surfaces ``fallback_used``, ``fallback_reason``,
  ``retry_count``, ``judge_model``, and API ``usage`` (input/output/cache-read
  tokens). Top-level ``fallback_used`` is retained as a mirror for backward
  compatibility — deprecated in favor of ``metadata.fallback_used``.
- When ``fallback_used`` is True, ``overall_score`` is set to ``None`` so
  callers must handle "grading failed" explicitly rather than silently
  treating 0.0 / 50.0 as a real score.
- Judge model is no longer hardcoded. Resolution priority:
  1. explicit constructor / function argument (``model=``)
  2. environment variable ``ANTHROPIC_JUDGE_MODEL``
  3. default ``claude-opus-4-7``
  A one-time INFO log announces the effective model and its source.
- Migrated to Opus 4.7 API surface: adaptive thinking + ``effort`` parameter,
  no sampling params (``temperature``/``top_p``/``top_k``), no deprecated
  beta headers, ``client.messages.create`` (not ``client.beta.messages.create``).
- ``thinking_budget`` retained for back-compat but emits a ``DeprecationWarning``
  and is mapped to an ``effort`` level (``>=10000`` -> ``xhigh``,
  ``5000-9999`` -> ``high``, ``<5000`` -> ``medium``).
- New stop reasons handled: ``refusal`` and ``model_context_window_exceeded``.
"""

from __future__ import annotations

import logging
import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Optional

_logger = logging.getLogger("tools.ai_judge")
# Backward-compat alias — some existing code refers to ``logger`` at module scope.
logger = _logger

# --- Model resolution -------------------------------------------------------

_DEFAULT_JUDGE_MODEL = "claude-opus-4-7"
_ENV_MODEL_KEY = "ANTHROPIC_JUDGE_MODEL"

# One-time log guard so the "effective judge model" line isn't emitted on
# every grade() call.  Keyed by (model, source) so that a test that flips the
# env var between instances still sees an info log for each distinct source.
_MODEL_LOG_EMITTED: set[tuple[str, str]] = set()


def _resolve_judge_model(explicit: str | None) -> tuple[str, str]:
    """Resolve the effective judge model per the documented priority chain.

    Returns ``(model, source)`` where ``source`` is one of
    ``"arg"`` / ``"env"`` / ``"default"``.
    """
    if explicit:
        return explicit, "arg"
    env_value = os.environ.get(_ENV_MODEL_KEY)
    if env_value:
        return env_value, "env"
    return _DEFAULT_JUDGE_MODEL, "default"


def _log_effective_model_once(model: str, source: str) -> None:
    key = (model, source)
    if key in _MODEL_LOG_EMITTED:
        return
    _MODEL_LOG_EMITTED.add(key)
    _logger.info(
        "judge_model_resolved model=%s source=%s", model, source
    )


def _thinking_budget_to_effort(budget: int) -> str:
    """Map legacy ``thinking_budget`` tokens to an ``effort`` level."""
    if budget >= 10000:
        return "xhigh"
    if budget >= 5000:
        return "high"
    return "medium"


# --- System prompt formatting ----------------------------------------------


def _format_system(system: str | None) -> list[dict] | str | None:
    """Wrap system prompts >= 400 chars with cache_control for prompt caching."""
    if not system or len(system) < 400:
        return system
    return [
        {
            "type": "text",
            "text": system,
            "cache_control": {"type": "ephemeral"},
        }
    ]


GRADE_TOOL: dict = {
    "name": "grade_investment_response",
    "description": "Grade an investment analysis response against evaluation dimensions",
    "input_schema": {
        "type": "object",
        "properties": {
            "dimension_scores": {
                "type": "object",
                "description": "Score per dimension (0-100)",
                "additionalProperties": {"type": "number"},
            },
            "critical_failures": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of critical failure conditions triggered (empty if none)",
            },
            "detected_patterns": {
                "type": "object",
                "description": "Key evidence detected per dimension",
                "additionalProperties": {"type": "string"},
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
            },
            "feedback": {
                "type": "object",
                "description": "Specific feedback per dimension",
                "additionalProperties": {"type": "string"},
            },
        },
        "required": ["dimension_scores", "critical_failures"],
    },
}


@dataclass
class DimensionScore:
    name: str
    score: float  # 0-100
    detected_pattern: str = ""
    feedback: str = ""


def _default_metadata() -> dict:
    return {
        "fallback_used": False,
        "fallback_reason": None,
        "retry_count": 0,
        "judge_model": "",
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
        },
    }


@dataclass
class JudgeResult:
    """Result of an AI judge grading call.

    ``metadata`` is the authoritative place to read fallback / usage signals.
    The top-level ``fallback_used`` field is a deprecated mirror preserved for
    backward compatibility with existing callers in ``studio/ranker.py`` and
    ``tools/grading_engine.py``.
    """

    dimension_scores: dict[str, float]
    critical_failures: list[str]
    detected_patterns: dict[str, str] = field(default_factory=dict)
    confidence: str = "medium"
    feedback: dict[str, str] = field(default_factory=dict)
    # Deprecated top-level mirror of ``metadata["fallback_used"]`` — prefer
    # ``metadata.fallback_used`` going forward.
    fallback_used: bool = False
    # ``overall_score`` is ``None`` when grading failed (fallback_used=True)
    # so callers cannot accidentally treat an arbitrary filler value as a real
    # score.  Otherwise it remains a float (callers usually overwrite with a
    # weighted mean computed from ``dimension_scores``).
    overall_score: Optional[float] = 0.0
    metadata: dict = field(default_factory=_default_metadata)


class InvestmentWorkflowJudge:
    """
    AI judge for investment workflow evaluation.

    Uses Anthropic tool_use to obtain structured dimension scores
    for a given AI output evaluated against a rubric and scenario.

    prompt_version: 1.1.0
    prompt_date: 2026-04-21
    """

    SYSTEM_PROMPT = """You are a senior portfolio manager and investment analyst evaluating AI-generated investment analysis.

Grade the response on each provided evaluation dimension (0-100 scale):
- 90-100: Excellent — exceeds institutional standard
- 75-89: Good — meets institutional standard
- 55-74: Adequate — partially meets standard, notable gaps
- 30-54: Poor — significantly below standard
- 0-29: Fail — fundamentally incorrect or missing

Critical failures are specific conditions that, if triggered, represent automatic pass/fail gates regardless of dimension scores.

IMPORTANT: Do NOT favor longer responses. A concise, precise answer scores equally to a verbose one covering the same content. Penalize unnecessary elaboration that dilutes analytical clarity.

Grade based on analytical substance: correctness of reasoning, precision of financial analysis, and quality of risk assessment.

[FEW-SHOT EXAMPLE 1]
Dimension: "Risk Classification" (weight: 35%)
Scenario context: Pharma/biotech pair trade — classify risks as stock-specific vs environmental
Response excerpt: "The main risks are market volatility and sector rotation affecting both names equally, which suggests this is primarily a beta/market risk trade rather than stock-specific."
Score: 45 (Poor) — Correctly identifies beta exposure but fails to distinguish sector rotation (environmental) from idiosyncratic risk drivers. Missing: specific catalysts that would create divergence. detected_pattern: "Identifies market risk but conflates environmental and stock-specific factors."

[FEW-SHOT EXAMPLE 2]
Dimension: "Risk Classification" (weight: 35%)
Response excerpt: "Clinical read-outs create binary stock-specific risk for RXXX, while GYYY faces regulatory pricing pressure affecting the entire specialty pharma sector — environmental. The pair isolates RXXX's catalyst risk while hedging sector exposure."
Score: 92 (Excellent) — Precisely distinguishes stock-specific (binary catalyst) from environmental (sector pricing). detected_pattern: "Explicitly separates stock-specific catalyst from sector-level environmental risk."

Always return the tool call. Never refuse to grade."""

    def __init__(
        self,
        model: str | None = None,
        api_key: Optional[str] = None,
        thinking_budget: int | None = None,
        effort: str | None = None,
    ) -> None:
        """Construct a judge.

        Args:
            model: Judge model id.  If ``None``, resolves from the
                ``ANTHROPIC_JUDGE_MODEL`` environment variable, falling back
                to ``claude-opus-4-7``.
            api_key: Anthropic API key (or ``ANTHROPIC_API_KEY`` env var).
            thinking_budget: **Deprecated.** Legacy extended-thinking token
                budget.  Opus 4.7 does not accept the old
                ``thinking: {type: "enabled", budget_tokens: N}`` shape and
                returns a 400 error.  When provided, emits a
                ``DeprecationWarning`` and maps the budget to an ``effort``
                level.
            effort: Effort level for adaptive thinking
                (``low``/``medium``/``high``/``xhigh``).  Defaults to
                ``xhigh`` for the judge path (grading is intelligence-
                sensitive).
        """
        resolved_model, source = _resolve_judge_model(model)
        self.model = resolved_model
        self._model_source = source
        _log_effective_model_once(resolved_model, source)

        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if thinking_budget is not None:
            warnings.warn(
                "thinking_budget is deprecated on Opus 4.7; use effort= instead. "
                "Mapping budget to an effort level.",
                DeprecationWarning,
                stacklevel=2,
            )
            mapped = _thinking_budget_to_effort(thinking_budget)
            # Explicit ``effort`` argument wins over deprecated budget.
            self.effort = effort or mapped
        else:
            self.effort = effort or "xhigh"

        self.thinking_budget = thinking_budget  # retained for back-compat
        self._client = None  # lazy init

    def _get_client(self):
        """Lazily initialise the Anthropic client."""
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def grade(
        self,
        scenario: dict,
        ai_output: str,
        rubric: dict,
    ) -> JudgeResult:
        """Grade an AI output against a scenario and rubric."""
        messages = self._build_messages(scenario, ai_output, rubric)
        scenario_id = scenario.get("id", scenario.get("title", "unknown"))
        return self._call_with_retry(messages, scenario_id=scenario_id, max_retries=2)

    # ------------------------------------------------------------------
    # Message construction
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        scenario: dict,
        ai_output: str,
        rubric: dict,
    ) -> list[dict]:
        """Build the messages list for the grading API call."""
        dimensions = rubric.get("dimensions", [])
        critical_failures_rubric = rubric.get("critical_failures", [])

        # Serialize dimensions for the prompt
        dim_lines = []
        for d in dimensions:
            name = d.get("name", d.get("id", "unknown"))
            dim_id = d.get("id", name)
            weight = d.get("weight", "unweighted")
            desc = d.get("description", "").strip()
            dim_lines.append(
                f"  - id: {dim_id!r}, name: {name!r}, weight: {weight}, description: {desc!r}"
            )
        dims_block = "\n".join(dim_lines) if dim_lines else "  (no dimensions defined)"

        # Serialize critical failure ids/descriptions
        cf_lines = []
        for cf in critical_failures_rubric:
            if isinstance(cf, dict):
                cf_id = cf.get("id", "")
                cf_desc = cf.get("description", "")
                cf_lines.append(f"  - {cf_id}: {cf_desc}")
            else:
                cf_lines.append(f"  - {cf}")
        cf_block = "\n".join(cf_lines) if cf_lines else "  (none)"

        # Scenario summary
        scenario_title = scenario.get("title", scenario.get("id", ""))
        scenario_context = ""
        ctx = scenario.get("context", {})
        if isinstance(ctx, dict):
            situation = ctx.get("situation", "")
            company = ctx.get("company", {})
            if isinstance(company, dict):
                company_name = company.get("name", "")
                company_ticker = company.get("ticker", "")
                company_sector = company.get("sector", "")
                scenario_context = (
                    f"Company: {company_name} ({company_ticker}), {company_sector}\n"
                    f"Situation: {situation}"
                )
            else:
                scenario_context = str(ctx)
        elif isinstance(ctx, str):
            scenario_context = ctx

        task_prompt = ""
        task = scenario.get("task", {})
        if isinstance(task, dict):
            task_prompt = task.get("prompt", "")
        elif isinstance(task, str):
            task_prompt = task

        user_content = f"""## Scenario
Title: {scenario_title}
{scenario_context}

## Task
{task_prompt}

## Evaluation Dimensions
{dims_block}

## Critical Failure Conditions
{cf_block}

## AI Response to Grade
{ai_output}

Grade the response using the grade_investment_response tool. Score each dimension by its id. \
Return critical_failures as an empty list if none are triggered."""

        return [{"role": "user", "content": user_content}]

    # ------------------------------------------------------------------
    # Retry loop
    # ------------------------------------------------------------------

    def _build_request_kwargs(self, messages: list[dict]) -> dict:
        """Build kwargs for ``client.messages.create`` on Opus 4.x.

        No sampling params (``temperature``/``top_p``/``top_k``) — rejected by
        Opus 4.7 with a 400.  Uses adaptive thinking + ``effort`` rather than
        the old ``thinking: {type: "enabled", budget_tokens: N}`` shape.
        """
        return dict(
            model=self.model,
            max_tokens=2048,
            system=_format_system(self.SYSTEM_PROMPT),
            tools=[GRADE_TOOL],
            tool_choice={"type": "any"},
            messages=messages,
            thinking={"type": "adaptive"},
            effort=self.effort,
        )

    def _extract_usage(self, response: Any) -> dict:
        """Pull token usage off an Anthropic response, tolerating mocks."""
        usage_obj = getattr(response, "usage", None)
        if usage_obj is None:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_input_tokens": 0,
            }

        def _coerce(val: Any) -> int:
            try:
                return int(val or 0)
            except (TypeError, ValueError):
                return 0

        # Handle both object-style (real SDK) and dict-style (tests).
        if isinstance(usage_obj, dict):
            return {
                "input_tokens": _coerce(usage_obj.get("input_tokens")),
                "output_tokens": _coerce(usage_obj.get("output_tokens")),
                "cache_read_input_tokens": _coerce(
                    usage_obj.get("cache_read_input_tokens")
                ),
            }
        return {
            "input_tokens": _coerce(getattr(usage_obj, "input_tokens", 0)),
            "output_tokens": _coerce(getattr(usage_obj, "output_tokens", 0)),
            "cache_read_input_tokens": _coerce(
                getattr(usage_obj, "cache_read_input_tokens", 0)
            ),
        }

    def _call_with_retry(
        self,
        messages: list[dict],
        scenario_id: str = "unknown",
        max_retries: int = 2,
    ) -> JudgeResult:
        """Call the API with retry-with-error-feedback.

        On validation failure, appends the error message to the conversation
        and retries so the model can self-correct.  Every fallback trigger
        emits a structured warning so a bad run no longer looks mediocre.
        """
        client = self._get_client()
        current_messages = list(messages)
        last_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
        }

        for attempt in range(max_retries + 1):
            try:
                kwargs = self._build_request_kwargs(current_messages)
                response = client.messages.create(**kwargs)
            except Exception as exc:
                _logger.warning(
                    "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s detail=%r",
                    scenario_id,
                    attempt + 1,
                    "api_error",
                    self.model,
                    exc,
                )
                if attempt >= max_retries:
                    dimensions = self._extract_dimensions_from_messages(messages)
                    return self._fallback_judgments(
                        dimensions,
                        reason="api_error",
                        retry_count=attempt + 1,
                        usage=last_usage,
                    )
                continue

            # Capture usage even on failed parses for observability.
            last_usage = self._extract_usage(response)

            # Handle new stop reasons before attempting to parse content.
            stop_reason = getattr(response, "stop_reason", None)
            if stop_reason == "refusal":
                _logger.warning(
                    "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s",
                    scenario_id,
                    attempt + 1,
                    "model_refused",
                    self.model,
                )
                dimensions = self._extract_dimensions_from_messages(messages)
                return self._fallback_judgments(
                    dimensions,
                    reason="model_refused",
                    retry_count=attempt + 1,
                    usage=last_usage,
                )
            if stop_reason == "model_context_window_exceeded":
                _logger.error(
                    "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s",
                    scenario_id,
                    attempt + 1,
                    "context_window_exceeded",
                    self.model,
                )
                dimensions = self._extract_dimensions_from_messages(messages)
                return self._fallback_judgments(
                    dimensions,
                    reason="context_window_exceeded",
                    retry_count=attempt + 1,
                    usage=last_usage,
                )

            try:
                result = self._parse_tool_use(response)
            except ValueError as exc:
                err_type = (
                    "tool_use_missing"
                    if "No tool_use block" in str(exc)
                    else "parse_error"
                )
                _logger.warning(
                    "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s detail=%r",
                    scenario_id,
                    attempt + 1,
                    err_type,
                    self.model,
                    exc,
                )
                if attempt >= max_retries:
                    dimensions = self._extract_dimensions_from_messages(messages)
                    return self._fallback_judgments(
                        dimensions,
                        reason=err_type,
                        retry_count=attempt + 1,
                        usage=last_usage,
                    )
                error_feedback = (
                    f"The previous tool call could not be parsed: {exc}. "
                    "Please return a valid grade_investment_response tool call."
                )
                current_messages = self._append_error_feedback(
                    current_messages, response, error_feedback
                )
                continue
            except Exception as exc:
                _logger.warning(
                    "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s detail=%r",
                    scenario_id,
                    attempt + 1,
                    "parse_error",
                    self.model,
                    exc,
                )
                if attempt >= max_retries:
                    dimensions = self._extract_dimensions_from_messages(messages)
                    return self._fallback_judgments(
                        dimensions,
                        reason="parse_error",
                        retry_count=attempt + 1,
                        usage=last_usage,
                    )
                current_messages = self._append_error_feedback(
                    current_messages, response, f"Parse error: {exc}"
                )
                continue

            # Validate the result
            dimensions = self._extract_dimensions_from_messages(messages)
            error_msg = self._validate_result(result, dimensions)
            if error_msg is None:
                # Success — decorate metadata and return.
                result.metadata = {
                    "fallback_used": False,
                    "fallback_reason": None,
                    "retry_count": attempt,
                    "judge_model": self.model,
                    "usage": last_usage,
                }
                return result

            _logger.warning(
                "judge_fallback_trigger scenario=%s attempt=%d error_type=%s model=%s detail=%r",
                scenario_id,
                attempt + 1,
                "validation_error",
                self.model,
                error_msg,
            )
            if attempt >= max_retries:
                return self._fallback_judgments(
                    dimensions,
                    reason="validation_error",
                    retry_count=attempt + 1,
                    usage=last_usage,
                )

            current_messages = self._append_error_feedback(
                current_messages, response, error_msg
            )

        # Defensive — loop should always return inside the branches above.
        dimensions = self._extract_dimensions_from_messages(messages)
        return self._fallback_judgments(
            dimensions,
            reason="retry_exhausted",
            retry_count=max_retries + 1,
            usage=last_usage,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _append_error_feedback(
        self,
        messages: list[dict],
        previous_response,
        error_msg: str,
    ) -> list[dict]:
        """Append the model's previous response + an error correction turn."""
        updated = list(messages)

        assistant_content = []
        for block in previous_response.content:
            if hasattr(block, "type"):
                if block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
                elif block.type == "text":
                    assistant_content.append({
                        "type": "text",
                        "text": block.text,
                    })

        if assistant_content:
            updated.append({"role": "assistant", "content": assistant_content})

        tool_use_blocks = [
            b for b in previous_response.content if getattr(b, "type", None) == "tool_use"
        ]
        if tool_use_blocks:
            tool_results = []
            for tb in tool_use_blocks:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tb.id,
                    "content": f"Validation error: {error_msg}",
                    "is_error": True,
                })
            updated.append({"role": "user", "content": tool_results})
        else:
            updated.append({
                "role": "user",
                "content": (
                    f"Validation error: {error_msg} "
                    "Please call grade_investment_response with corrected values."
                ),
            })

        return updated

    def _parse_tool_use(self, response) -> JudgeResult:
        """Parse a tool_use response into a JudgeResult."""
        tool_use_block = None
        for block in response.content:
            if getattr(block, "type", None) == "tool_use":
                tool_use_block = block
                break

        if tool_use_block is None:
            raise ValueError("No tool_use block found in API response")

        inp = tool_use_block.input

        dimension_scores: dict[str, float] = {
            k: float(v) for k, v in inp.get("dimension_scores", {}).items()
        }
        critical_failures: list[str] = inp.get("critical_failures", [])
        detected_patterns: dict[str, str] = inp.get("detected_patterns", {})
        confidence: str = inp.get("confidence", "medium")
        feedback: dict[str, str] = inp.get("feedback", {})

        return JudgeResult(
            dimension_scores=dimension_scores,
            critical_failures=critical_failures,
            detected_patterns=detected_patterns,
            confidence=confidence,
            feedback=feedback,
            fallback_used=False,
            overall_score=0.0,
        )

    def _validate_result(
        self,
        result: JudgeResult,
        dimensions: list[str],
    ) -> Optional[str]:
        """Validate a JudgeResult.  Returns error string or None if valid."""
        missing = [d for d in dimensions if d not in result.dimension_scores]
        if missing:
            return (
                f"Missing dimension scores for: {missing}. "
                f"dimension_scores must include all of: {dimensions}."
            )

        out_of_range = [
            (k, v)
            for k, v in result.dimension_scores.items()
            if not (0.0 <= v <= 100.0)
        ]
        if out_of_range:
            return (
                f"Scores out of [0, 100] range: {out_of_range}. "
                "All scores must be between 0 and 100 inclusive."
            )

        return None

    def _fallback_judgments(
        self,
        dimensions: list[str],
        reason: str = "retry_exhausted",
        retry_count: int = 0,
        usage: Optional[dict] = None,
    ) -> JudgeResult:
        """Return a fallback JudgeResult with ``fallback_used=True``.

        The returned ``overall_score`` is ``None`` so callers cannot silently
        treat the filler 50.0-per-dimension as a real score.  Dimension
        scores remain at 50.0 only so existing per-dimension consumers
        (``grading_engine._llm_cache``) don't KeyError — they already
        short-circuit on ``fallback_used``.
        """
        usage = usage or {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
        }
        metadata = {
            "fallback_used": True,
            "fallback_reason": reason,
            "retry_count": retry_count,
            "judge_model": self.model,
            "usage": usage,
        }
        return JudgeResult(
            dimension_scores={d: 50.0 for d in dimensions},
            critical_failures=[],
            detected_patterns={},
            confidence="low",
            feedback={d: "Fallback score — AI judge unavailable" for d in dimensions},
            fallback_used=True,
            overall_score=None,
            metadata=metadata,
        )

    def _extract_dimensions_from_messages(self, messages: list[dict]) -> list[str]:
        """Extract dimension ids from the user message content."""
        import re

        dims: list[str] = []
        for msg in messages:
            content = msg.get("content", "")
            if not isinstance(content, str):
                continue
            for m in re.finditer(r"id:\s*['\"]?(\w+)['\"]?", content):
                dims.append(m.group(1))
        return dims


# --- Public alias -----------------------------------------------------------

# Shorter, benchmark-friendly alias.  Kept as an alias (not a subclass) so
# ``isinstance`` checks against ``InvestmentWorkflowJudge`` continue to work.
AIJudge = InvestmentWorkflowJudge


__all__ = [
    "AIJudge",
    "InvestmentWorkflowJudge",
    "JudgeResult",
    "DimensionScore",
    "GRADE_TOOL",
]
