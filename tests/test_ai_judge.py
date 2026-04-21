"""
Tests for tools/ai_judge.py — InvestmentWorkflowJudge / AIJudge.

All Anthropic API calls are mocked via unittest.mock.
"""

import logging
import os
import unittest
import warnings
from unittest.mock import MagicMock, patch

from tools.ai_judge import (
    AIJudge,
    InvestmentWorkflowJudge,
    JudgeResult,
    _DEFAULT_JUDGE_MODEL,
    _ENV_MODEL_KEY,
    _MODEL_LOG_EMITTED,
    _resolve_judge_model,
    _thinking_budget_to_effort,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool_use_block(
    dim_scores: dict,
    critical_failures: list | None = None,
    detected_patterns: dict | None = None,
    confidence: str = "high",
    feedback: dict | None = None,
    tool_id: str = "tu_1",
) -> MagicMock:
    """Build a fake tool_use response block."""
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = "grade_investment_response"
    block.input = {
        "dimension_scores": dim_scores,
        "critical_failures": critical_failures or [],
        "detected_patterns": detected_patterns or {},
        "confidence": confidence,
        "feedback": feedback or {},
    }
    return block


def _make_text_block(text: str = "hello") -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _make_response(
    blocks: list,
    stop_reason: str | None = "tool_use",
    usage: dict | None = None,
) -> MagicMock:
    """Build a fake Anthropic messages.create response.

    ``usage`` is attached as a dict to mimic the Anthropic SDK's ``Usage``
    object closely enough for ``_extract_usage``.
    """
    resp = MagicMock()
    resp.content = blocks
    resp.stop_reason = stop_reason
    if usage is not None:
        resp.usage = usage
    else:
        # Default empty usage triggers the dict branch of _extract_usage with zeros.
        resp.usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
        }
    return resp


def _make_rubric(dim_ids: list[str]) -> dict:
    """Build a minimal rubric with the given dimension ids."""
    return {
        "dimensions": [
            {"id": d, "name": d, "weight": 100 // len(dim_ids)} for d in dim_ids
        ],
        "critical_failures": [],
        "pass_threshold": 70,
    }


def _make_scenario(scenario_id: str = "test_scenario") -> dict:
    return {
        "id": scenario_id,
        "title": "Test Scenario",
        "context": {"situation": "Test situation"},
        "task": {"prompt": "Evaluate this."},
    }


# ---------------------------------------------------------------------------
# Existing / backward-compat tests
# ---------------------------------------------------------------------------

class TestGradeReturnsDimensionScores(unittest.TestCase):
    """mock returns valid tool_use; verify dimension_scores dict returned."""

    @patch("anthropic.Anthropic")
    def test_grade_returns_dimension_scores(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "analytical_rigor"]
        scores = {"factual_accuracy": 82.0, "analytical_rigor": 75.0}

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block(scores)]
        )

        judge = InvestmentWorkflowJudge(api_key="test-key")
        result = judge.grade(
            scenario=_make_scenario(),
            ai_output="A reasonable investment thesis.",
            rubric=_make_rubric(dim_ids),
        )

        self.assertIsInstance(result, JudgeResult)
        self.assertEqual(result.dimension_scores["factual_accuracy"], 82.0)
        self.assertEqual(result.dimension_scores["analytical_rigor"], 75.0)
        self.assertFalse(result.fallback_used)


class TestAllDimensionsPresentInOutput(unittest.TestCase):
    """output has a score for every dimension passed in the rubric."""

    @patch("anthropic.Anthropic")
    def test_all_dimensions_present_in_output(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "analytical_rigor", "risk_assessment"]
        scores = {d: 80.0 for d in dim_ids}

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block(scores)]
        )

        judge = InvestmentWorkflowJudge(api_key="test-key")
        result = judge.grade(
            scenario=_make_scenario(),
            ai_output="Analysis text.",
            rubric=_make_rubric(dim_ids),
        )

        for dim_id in dim_ids:
            self.assertIn(dim_id, result.dimension_scores)


class TestRetryOnValidationFailure(unittest.TestCase):
    """first call returns scores >100; second call valid; retry observed."""

    @patch("anthropic.Anthropic")
    def test_retry_on_validation_failure(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "risk_assessment"]

        bad_scores = {"factual_accuracy": 150.0, "risk_assessment": 70.0}
        good_scores = {"factual_accuracy": 85.0, "risk_assessment": 70.0}

        first_response = _make_response([_make_tool_use_block(bad_scores, tool_id="tu_1")])
        second_response = _make_response([_make_tool_use_block(good_scores, tool_id="tu_2")])

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.side_effect = [first_response, second_response]

        judge = InvestmentWorkflowJudge(api_key="test-key")
        result = judge.grade(
            scenario=_make_scenario(),
            ai_output="Some analysis.",
            rubric=_make_rubric(dim_ids),
        )

        self.assertEqual(mock_client.messages.create.call_count, 2)
        self.assertEqual(result.dimension_scores["factual_accuracy"], 85.0)
        self.assertFalse(result.fallback_used)


class TestFallbackOnExhaustedRetries(unittest.TestCase):
    """all calls malformed; verify fallback_used=True and scores are 50.0."""

    @patch("anthropic.Anthropic")
    def test_fallback_on_exhausted_retries(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "analytical_rigor"]
        bad_scores = {"factual_accuracy": 200.0, "analytical_rigor": -10.0}
        bad_response = _make_response([_make_tool_use_block(bad_scores)])

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad_response

        judge = InvestmentWorkflowJudge(api_key="test-key")
        result = judge.grade(
            scenario=_make_scenario(),
            ai_output="Bad analysis.",
            rubric=_make_rubric(dim_ids),
        )

        self.assertTrue(result.fallback_used)
        for dim_id in dim_ids:
            self.assertIn(dim_id, result.dimension_scores)
            self.assertEqual(result.dimension_scores[dim_id], 50.0)
        self.assertEqual(result.confidence, "low")


class TestCriticalFailureReturnedCorrectly(unittest.TestCase):
    """mock returns critical_failures list; verify propagated to JudgeResult."""

    @patch("anthropic.Anthropic")
    def test_critical_failure_returned_correctly(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "completeness"]
        scores = {d: 60.0 for d in dim_ids}
        failures = ["hallucinated_data", "missing_material_risk"]

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block(scores, critical_failures=failures)]
        )

        judge = InvestmentWorkflowJudge(api_key="test-key")
        result = judge.grade(
            scenario=_make_scenario(),
            ai_output="Incomplete analysis.",
            rubric=_make_rubric(dim_ids),
        )

        self.assertEqual(result.critical_failures, failures)
        self.assertIn("hallucinated_data", result.critical_failures)
        self.assertIn("missing_material_risk", result.critical_failures)
        self.assertFalse(result.fallback_used)


# ---------------------------------------------------------------------------
# New tests — Tier-1 Issue #5
# ---------------------------------------------------------------------------


class TestModelResolution(unittest.TestCase):
    """Judge model resolution follows arg > env > default priority."""

    def setUp(self):
        # Clear any cached emission so tests see a fresh log each time.
        _MODEL_LOG_EMITTED.clear()

    def test_default_model_is_opus_4_7(self):
        # Ensure env var is not set.
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(_ENV_MODEL_KEY, None)
            model, source = _resolve_judge_model(None)
        self.assertEqual(model, "claude-opus-4-7")
        self.assertEqual(source, "default")
        self.assertEqual(_DEFAULT_JUDGE_MODEL, "claude-opus-4-7")

    def test_env_var_overrides_default(self):
        with patch.dict(os.environ, {_ENV_MODEL_KEY: "claude-sonnet-4-6"}):
            model, source = _resolve_judge_model(None)
        self.assertEqual(model, "claude-sonnet-4-6")
        self.assertEqual(source, "env")

    def test_explicit_arg_overrides_env(self):
        with patch.dict(os.environ, {_ENV_MODEL_KEY: "claude-sonnet-4-6"}):
            model, source = _resolve_judge_model("claude-haiku-4-5")
        self.assertEqual(model, "claude-haiku-4-5")
        self.assertEqual(source, "arg")

    def test_judge_instance_default_model(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop(_ENV_MODEL_KEY, None)
            judge = AIJudge()
        self.assertEqual(judge.model, "claude-opus-4-7")
        self.assertEqual(judge._model_source, "default")

    def test_judge_instance_env_model(self):
        with patch.dict(os.environ, {_ENV_MODEL_KEY: "claude-sonnet-4-6"}):
            judge = AIJudge()
        self.assertEqual(judge.model, "claude-sonnet-4-6")
        self.assertEqual(judge._model_source, "env")

    def test_judge_instance_explicit_model_wins_over_env(self):
        with patch.dict(os.environ, {_ENV_MODEL_KEY: "claude-sonnet-4-6"}):
            judge = AIJudge(model="claude-haiku-4-5")
        self.assertEqual(judge.model, "claude-haiku-4-5")
        self.assertEqual(judge._model_source, "arg")

    def test_model_resolution_logs_info_once(self):
        _MODEL_LOG_EMITTED.clear()
        with self.assertLogs("tools.ai_judge", level="INFO") as caplog:
            AIJudge(model="claude-sonnet-4-6")
        # Should have at least one INFO line announcing the model+source.
        info_lines = [r for r in caplog.records if r.levelno == logging.INFO]
        self.assertTrue(any("claude-sonnet-4-6" in r.getMessage() for r in info_lines))
        self.assertTrue(any("arg" in r.getMessage() for r in info_lines))

    def test_alias_AIJudge_equals_InvestmentWorkflowJudge(self):
        self.assertIs(AIJudge, InvestmentWorkflowJudge)


# ---------------------------------------------------------------------------
# Thinking budget migration
# ---------------------------------------------------------------------------


class TestThinkingBudgetDeprecation(unittest.TestCase):
    """thinking_budget maps to effort + emits DeprecationWarning."""

    def test_budget_xhigh_mapping(self):
        self.assertEqual(_thinking_budget_to_effort(10_000), "xhigh")
        self.assertEqual(_thinking_budget_to_effort(20_000), "xhigh")

    def test_budget_high_mapping(self):
        self.assertEqual(_thinking_budget_to_effort(5_000), "high")
        self.assertEqual(_thinking_budget_to_effort(9_999), "high")

    def test_budget_medium_mapping(self):
        self.assertEqual(_thinking_budget_to_effort(4_999), "medium")
        self.assertEqual(_thinking_budget_to_effort(0), "medium")

    def test_thinking_budget_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            judge = AIJudge(api_key="x", thinking_budget=10_000)
        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertTrue(dep, "expected DeprecationWarning when thinking_budget is used")
        self.assertEqual(judge.effort, "xhigh")

    def test_explicit_effort_overrides_thinking_budget(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            judge = AIJudge(api_key="x", thinking_budget=10_000, effort="low")
        self.assertEqual(judge.effort, "low")

    def test_no_deprecation_when_budget_unset(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            judge = AIJudge(api_key="x")
        dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertFalse(dep)
        self.assertEqual(judge.effort, "xhigh")  # default


# ---------------------------------------------------------------------------
# Request-shape tests (adaptive thinking, no sampling params, no betas)
# ---------------------------------------------------------------------------


class TestRequestShape(unittest.TestCase):
    """The request sent to messages.create uses the 4.7-compatible shape."""

    @patch("anthropic.Anthropic")
    def test_kwargs_use_adaptive_thinking_and_effort(self, MockAnthropic):
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        judge = AIJudge(api_key="x", effort="xhigh")
        judge.grade(
            scenario=_make_scenario(),
            ai_output="resp",
            rubric=_make_rubric(dim_ids),
        )

        _, kwargs = mock_client.messages.create.call_args
        self.assertEqual(kwargs["thinking"], {"type": "adaptive"})
        self.assertEqual(kwargs["effort"], "xhigh")

    @patch("anthropic.Anthropic")
    def test_kwargs_have_no_sampling_params(self, MockAnthropic):
        """Opus 4.7 returns 400 if temperature/top_p/top_k are passed."""
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        judge = AIJudge(api_key="x")
        judge.grade(
            scenario=_make_scenario(),
            ai_output="resp",
            rubric=_make_rubric(dim_ids),
        )

        _, kwargs = mock_client.messages.create.call_args
        for forbidden in ("temperature", "top_p", "top_k"):
            self.assertNotIn(forbidden, kwargs)

    @patch("anthropic.Anthropic")
    def test_kwargs_have_no_legacy_thinking_budget(self, MockAnthropic):
        """Old enabled/budget_tokens syntax must not leak through."""
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            judge = AIJudge(api_key="x", thinking_budget=10_000)
        judge.grade(
            scenario=_make_scenario(),
            ai_output="resp",
            rubric=_make_rubric(dim_ids),
        )

        _, kwargs = mock_client.messages.create.call_args
        self.assertEqual(kwargs["thinking"], {"type": "adaptive"})
        self.assertNotIn("budget_tokens", kwargs.get("thinking", {}))

    @patch("anthropic.Anthropic")
    def test_uses_messages_create_not_beta_namespace(self, MockAnthropic):
        """client.messages.create, not client.beta.messages.create."""
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        judge = AIJudge(api_key="x")
        judge.grade(
            scenario=_make_scenario(),
            ai_output="resp",
            rubric=_make_rubric(dim_ids),
        )

        self.assertEqual(mock_client.messages.create.call_count, 1)
        # beta.messages.create should never be touched.
        mock_client.beta.messages.create.assert_not_called()


# ---------------------------------------------------------------------------
# Metadata + overall_score on fallback
# ---------------------------------------------------------------------------


class TestMetadataSurfaced(unittest.TestCase):
    """metadata is populated with fallback_used, retry_count, judge_model, usage."""

    @patch("anthropic.Anthropic")
    def test_metadata_on_successful_grade(self, MockAnthropic):
        dim_ids = ["d1", "d2"]
        scores = {"d1": 82.0, "d2": 70.0}
        usage = {
            "input_tokens": 1234,
            "output_tokens": 321,
            "cache_read_input_tokens": 500,
        }

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block(scores)], usage=usage
        )

        judge = AIJudge(api_key="x", model="claude-opus-4-7")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertIsInstance(result.metadata, dict)
        self.assertFalse(result.metadata["fallback_used"])
        self.assertIsNone(result.metadata["fallback_reason"])
        self.assertEqual(result.metadata["retry_count"], 0)
        self.assertEqual(result.metadata["judge_model"], "claude-opus-4-7")
        self.assertEqual(result.metadata["usage"]["input_tokens"], 1234)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 321)
        self.assertEqual(result.metadata["usage"]["cache_read_input_tokens"], 500)

    @patch("anthropic.Anthropic")
    def test_metadata_on_retry_exhausted(self, MockAnthropic):
        dim_ids = ["d1"]
        bad = _make_response([_make_tool_use_block({"d1": 200.0})])

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad

        judge = AIJudge(api_key="x", model="claude-opus-4-7")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertTrue(result.metadata["fallback_used"])
        self.assertEqual(result.metadata["fallback_reason"], "validation_error")
        self.assertEqual(result.metadata["judge_model"], "claude-opus-4-7")
        # retry_count should reflect that we exhausted the attempts.
        self.assertGreaterEqual(result.metadata["retry_count"], 1)

    @patch("anthropic.Anthropic")
    def test_top_level_fallback_used_mirrors_metadata(self, MockAnthropic):
        dim_ids = ["d1"]
        bad = _make_response([_make_tool_use_block({"d1": 200.0})])
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))
        # Backward-compat: consumers like studio/ranker.py still read .fallback_used.
        self.assertEqual(result.fallback_used, result.metadata["fallback_used"])
        self.assertTrue(result.fallback_used)


class TestOverallScoreNoneOnFallback(unittest.TestCase):
    """overall_score is None when fallback_used=True (no misleading 0.0/50.0)."""

    @patch("anthropic.Anthropic")
    def test_overall_score_none_on_fallback(self, MockAnthropic):
        dim_ids = ["d1"]
        bad = _make_response([_make_tool_use_block({"d1": -1.0})])
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertTrue(result.fallback_used)
        self.assertIsNone(result.overall_score)

    @patch("anthropic.Anthropic")
    def test_overall_score_float_on_success(self, MockAnthropic):
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertFalse(result.fallback_used)
        self.assertIsNotNone(result.overall_score)
        self.assertIsInstance(result.overall_score, float)


# ---------------------------------------------------------------------------
# Logging — every fallback path emits a warning
# ---------------------------------------------------------------------------


class TestFallbackLogging(unittest.TestCase):
    """Every fallback trigger point emits a structured _logger.warning."""

    @patch("anthropic.Anthropic")
    def test_validation_error_logs_warning(self, MockAnthropic):
        dim_ids = ["d1"]
        bad = _make_response([_make_tool_use_block({"d1": 200.0})])
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad

        judge = AIJudge(api_key="x")
        with self.assertLogs("tools.ai_judge", level="WARNING") as caplog:
            judge.grade(_make_scenario("scen1"), "resp", _make_rubric(dim_ids))

        triggers = [r for r in caplog.records if "judge_fallback_trigger" in r.getMessage()]
        self.assertTrue(triggers, "expected at least one judge_fallback_trigger warning")
        # Structured fields must appear in messages.
        joined = " ".join(r.getMessage() for r in triggers)
        self.assertIn("scenario=scen1", joined)
        self.assertIn("error_type=validation_error", joined)
        self.assertIn("model=", joined)

    @patch("anthropic.Anthropic")
    def test_api_exception_logs_warning(self, MockAnthropic):
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.side_effect = RuntimeError("network boom")

        judge = AIJudge(api_key="x")
        with self.assertLogs("tools.ai_judge", level="WARNING") as caplog:
            result = judge.grade(_make_scenario("scen_api"), "resp", _make_rubric(dim_ids))

        msgs = " ".join(r.getMessage() for r in caplog.records)
        self.assertIn("error_type=api_error", msgs)
        self.assertIn("scenario=scen_api", msgs)
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.metadata["fallback_reason"], "api_error")

    @patch("anthropic.Anthropic")
    def test_tool_use_missing_logs_warning(self, MockAnthropic):
        """No tool_use block in response triggers parse-path warning."""
        dim_ids = ["d1"]
        # Response contains only a text block — no tool_use.
        resp = _make_response([_make_text_block("I refuse to grade")])
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = resp

        judge = AIJudge(api_key="x")
        with self.assertLogs("tools.ai_judge", level="WARNING") as caplog:
            result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        msgs = " ".join(r.getMessage() for r in caplog.records)
        self.assertIn("error_type=tool_use_missing", msgs)
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.metadata["fallback_reason"], "tool_use_missing")


# ---------------------------------------------------------------------------
# New stop reasons
# ---------------------------------------------------------------------------


class TestStopReasonRefusal(unittest.TestCase):
    """stop_reason='refusal' -> fallback_reason='model_refused', overall_score=None."""

    @patch("anthropic.Anthropic")
    def test_refusal_stop_reason(self, MockAnthropic):
        dim_ids = ["d1", "d2"]
        # Even if content contains a tool_use block, refusal takes precedence.
        resp = _make_response(
            [_make_text_block("I cannot assist.")],
            stop_reason="refusal",
        )
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = resp

        judge = AIJudge(api_key="x")
        with self.assertLogs("tools.ai_judge", level="WARNING") as caplog:
            result = judge.grade(_make_scenario("sc_ref"), "resp", _make_rubric(dim_ids))

        self.assertTrue(result.fallback_used)
        self.assertEqual(result.metadata["fallback_reason"], "model_refused")
        self.assertIsNone(result.overall_score)
        msgs = " ".join(r.getMessage() for r in caplog.records)
        self.assertIn("error_type=model_refused", msgs)
        # No retry should be attempted on refusal.
        self.assertEqual(mock_client.messages.create.call_count, 1)


class TestStopReasonContextWindow(unittest.TestCase):
    """stop_reason='model_context_window_exceeded' -> context_window_exceeded."""

    @patch("anthropic.Anthropic")
    def test_context_window_exceeded_stop_reason(self, MockAnthropic):
        dim_ids = ["d1"]
        resp = _make_response(
            [_make_text_block("truncated")],
            stop_reason="model_context_window_exceeded",
        )
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = resp

        judge = AIJudge(api_key="x")
        with self.assertLogs("tools.ai_judge", level="ERROR") as caplog:
            result = judge.grade(_make_scenario("sc_ctx"), "resp", _make_rubric(dim_ids))

        self.assertTrue(result.fallback_used)
        self.assertEqual(result.metadata["fallback_reason"], "context_window_exceeded")
        self.assertIsNone(result.overall_score)
        msgs = " ".join(r.getMessage() for r in caplog.records)
        self.assertIn("error_type=context_window_exceeded", msgs)


# ---------------------------------------------------------------------------
# Usage metadata
# ---------------------------------------------------------------------------


class TestUsageMetadata(unittest.TestCase):
    """API token usage surfaces in metadata.usage for the benchmark runner."""

    @patch("anthropic.Anthropic")
    def test_usage_on_success_dict_style(self, MockAnthropic):
        dim_ids = ["d1"]
        usage = {
            "input_tokens": 1000,
            "output_tokens": 200,
            "cache_read_input_tokens": 800,
        }
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})], usage=usage
        )

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertEqual(result.metadata["usage"]["input_tokens"], 1000)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 200)
        self.assertEqual(result.metadata["usage"]["cache_read_input_tokens"], 800)

    @patch("anthropic.Anthropic")
    def test_usage_on_success_object_style(self, MockAnthropic):
        """SDK-style usage object (attribute access) also works."""
        dim_ids = ["d1"]
        usage_obj = MagicMock(spec=["input_tokens", "output_tokens", "cache_read_input_tokens"])
        usage_obj.input_tokens = 500
        usage_obj.output_tokens = 150
        usage_obj.cache_read_input_tokens = 250

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        resp = _make_response([_make_tool_use_block({"d1": 80.0})], usage=None)
        resp.usage = usage_obj
        mock_client.messages.create.return_value = resp

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertEqual(result.metadata["usage"]["input_tokens"], 500)
        self.assertEqual(result.metadata["usage"]["output_tokens"], 150)
        self.assertEqual(result.metadata["usage"]["cache_read_input_tokens"], 250)

    @patch("anthropic.Anthropic")
    def test_usage_present_even_on_fallback(self, MockAnthropic):
        """Usage should surface even when the call ends in fallback."""
        dim_ids = ["d1"]
        usage = {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_read_input_tokens": 80,
        }
        bad = _make_response([_make_tool_use_block({"d1": 999.0})], usage=usage)
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = bad

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))

        self.assertTrue(result.fallback_used)
        # Any of the 3 attempts should have recorded usage.
        self.assertEqual(result.metadata["usage"]["input_tokens"], 100)
        self.assertEqual(result.metadata["usage"]["cache_read_input_tokens"], 80)


# ---------------------------------------------------------------------------
# Retry count accuracy
# ---------------------------------------------------------------------------


class TestRetryCountInMetadata(unittest.TestCase):
    """metadata.retry_count reports how many attempts were made."""

    @patch("anthropic.Anthropic")
    def test_retry_count_zero_on_first_success(self, MockAnthropic):
        dim_ids = ["d1"]
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.return_value = _make_response(
            [_make_tool_use_block({"d1": 80.0})]
        )

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))
        self.assertEqual(result.metadata["retry_count"], 0)

    @patch("anthropic.Anthropic")
    def test_retry_count_one_on_second_attempt_success(self, MockAnthropic):
        dim_ids = ["d1"]
        first = _make_response([_make_tool_use_block({"d1": 200.0}, tool_id="tu_1")])
        second = _make_response([_make_tool_use_block({"d1": 80.0}, tool_id="tu_2")])
        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        mock_client.messages.create.side_effect = [first, second]

        judge = AIJudge(api_key="x")
        result = judge.grade(_make_scenario(), "resp", _make_rubric(dim_ids))
        self.assertEqual(result.metadata["retry_count"], 1)
        self.assertFalse(result.fallback_used)


if __name__ == "__main__":
    unittest.main()
