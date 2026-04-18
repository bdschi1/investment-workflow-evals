"""
AI-as-judge for investment workflow evaluation.

Replaces the hardcoded 75.0 stub in GradingEngine._score_with_llm with
a real Anthropic API call using tool_use for structured output.

prompt_version: 1.0.0
prompt_date: 2026-04-04
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


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


@dataclass
class JudgeResult:
    dimension_scores: dict[str, float]
    critical_failures: list[str]
    detected_patterns: dict[str, str] = field(default_factory=dict)
    confidence: str = "medium"
    feedback: dict[str, str] = field(default_factory=dict)
    fallback_used: bool = False
    overall_score: float = 0.0  # computed as weighted sum by caller


class InvestmentWorkflowJudge:
    """
    AI judge for investment workflow evaluation.

    Uses Anthropic tool_use to obtain structured dimension scores
    for a given AI output evaluated against a rubric and scenario.

    prompt_version: 1.0.0
    prompt_date: 2026-04-04
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
        model: str = "claude-opus-4-6",
        api_key: Optional[str] = None,
        thinking_budget: int | None = None,
    ) -> None:
        self.model = model
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.thinking_budget = thinking_budget
        self._client = None  # lazy init

    def _get_client(self):
        """Lazily initialise the Anthropic client."""
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def grade(
        self,
        scenario: dict,
        ai_output: str,
        rubric: dict,
    ) -> JudgeResult:
        """
        Grade an AI output against a scenario and rubric.

        Args:
            scenario: Full scenario dict (context, task, dimensions, critical_failures).
            ai_output: The AI-generated response to evaluate.
            rubric: Rubric dict with dimensions list and their weights/levels.

        Returns:
            JudgeResult with per-dimension scores, critical failures, and feedback.
        """
        messages = self._build_messages(scenario, ai_output, rubric)
        return self._call_with_retry(messages, max_retries=2)

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

    def _call_with_retry(
        self,
        messages: list[dict],
        max_retries: int = 2,
    ) -> JudgeResult:
        """
        Call the API with retry-with-error-feedback.

        On validation failure, appends the error message to the conversation
        and retries so the model can self-correct.
        """
        client = self._get_client()
        current_messages = list(messages)

        for attempt in range(max_retries + 1):
            try:
                kwargs = dict(
                    model=self.model,
                    max_tokens=2048,
                    system=_format_system(self.SYSTEM_PROMPT),
                    tools=[GRADE_TOOL],
                    tool_choice={"type": "any"},
                    messages=current_messages,
                )
                if self.thinking_budget:
                    kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.thinking_budget}
                    # Ensure max_tokens accommodates thinking budget
                    current_max = kwargs.get("max_tokens", 4096)
                    if current_max < self.thinking_budget + 1024:
                        kwargs["max_tokens"] = self.thinking_budget + 4096
                else:
                    kwargs["temperature"] = 1.0
                response = client.messages.create(**kwargs)
            except Exception as exc:
                logger.warning("API call failed on attempt %d: %s", attempt + 1, exc)
                if attempt >= max_retries:
                    # Identify dimension ids from the original messages to build fallback
                    dimensions = self._extract_dimensions_from_messages(messages)
                    return self._fallback_judgments(dimensions)
                continue

            try:
                result = self._parse_tool_use(response)
            except Exception as exc:
                logger.warning("Parse failed on attempt %d: %s", attempt + 1, exc)
                if attempt >= max_retries:
                    dimensions = self._extract_dimensions_from_messages(messages)
                    return self._fallback_judgments(dimensions)
                # Append error feedback and retry
                error_feedback = (
                    f"The previous tool call could not be parsed: {exc}. "
                    "Please return a valid grade_investment_response tool call."
                )
                current_messages = self._append_error_feedback(
                    current_messages, response, error_feedback
                )
                continue

            # Validate the result
            dimensions = self._extract_dimensions_from_messages(messages)
            error_msg = self._validate_result(result, dimensions)
            if error_msg is None:
                return result

            logger.warning(
                "Validation failed on attempt %d: %s", attempt + 1, error_msg
            )
            if attempt >= max_retries:
                return self._fallback_judgments(dimensions)

            # Append error feedback and retry
            current_messages = self._append_error_feedback(
                current_messages, response, error_msg
            )

        dimensions = self._extract_dimensions_from_messages(messages)
        return self._fallback_judgments(dimensions)

    def _append_error_feedback(
        self,
        messages: list[dict],
        previous_response,
        error_msg: str,
    ) -> list[dict]:
        """
        Append the model's previous response and an error correction turn
        to the message list for retry-with-error-feedback.
        """
        updated = list(messages)

        # Add the assistant's previous response to the conversation
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

        # Add tool result if there was a tool_use block
        tool_use_blocks = [b for b in previous_response.content if getattr(b, "type", None) == "tool_use"]
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
            # No tool call was made — just add a user correction message
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
        """
        Validate a JudgeResult.

        Returns an error message string if invalid, None if valid.
        Checks: all dimension ids present, all scores in [0, 100].
        """
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

    def _fallback_judgments(self, dimensions: list[str]) -> JudgeResult:
        """
        Return neutral scores (50.0) per dimension with fallback_used=True.

        Used when all retries are exhausted or API is unavailable.
        """
        return JudgeResult(
            dimension_scores={d: 50.0 for d in dimensions},
            critical_failures=[],
            detected_patterns={},
            confidence="low",
            feedback={d: "Fallback score — AI judge unavailable" for d in dimensions},
            fallback_used=True,
            overall_score=0.0,
        )

    def _extract_dimensions_from_messages(self, messages: list[dict]) -> list[str]:
        """
        Extract dimension ids from the user message content.

        Parses lines of the form "  - id: 'dim_id', ..." that were
        written by _build_messages.
        """
        import re

        dims: list[str] = []
        for msg in messages:
            content = msg.get("content", "")
            if not isinstance(content, str):
                continue
            # Match lines like:   - id: 'factual_accuracy', ...
            for m in re.finditer(r"id:\s*['\"]?(\w+)['\"]?", content):
                dims.append(m.group(1))
        return dims
