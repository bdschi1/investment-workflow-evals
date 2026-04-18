"""
Tests for tools/ai_judge.py — InvestmentWorkflowJudge.

All Anthropic API calls are mocked via unittest.mock.
"""

import types
import unittest
from unittest.mock import MagicMock, patch, call

from tools.ai_judge import InvestmentWorkflowJudge, JudgeResult


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


def _make_response(blocks: list) -> MagicMock:
    """Build a fake Anthropic messages.create response."""
    resp = MagicMock()
    resp.content = blocks
    return resp


def _make_rubric(dim_ids: list[str]) -> dict:
    """Build a minimal rubric with the given dimension ids."""
    return {
        "dimensions": [{"id": d, "name": d, "weight": 100 // len(dim_ids)} for d in dim_ids],
        "critical_failures": [],
        "pass_threshold": 70,
    }


def _make_scenario() -> dict:
    return {
        "id": "test_scenario",
        "title": "Test Scenario",
        "context": {"situation": "Test situation"},
        "task": {"prompt": "Evaluate this."},
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGradeReturnsDimensionScores(unittest.TestCase):
    """Test 1: mock returns valid tool_use; verify dimension_scores dict returned."""

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
    """Test 2: output has a score for every dimension passed in the rubric."""

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
    """Test 3: first call returns scores >100; second call returns valid scores; verify retry."""

    @patch("anthropic.Anthropic")
    def test_retry_on_validation_failure(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "risk_assessment"]

        # First call: one score out of range
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

        # Verify the API was called twice (retry happened)
        self.assertEqual(mock_client.messages.create.call_count, 2)
        # Verify final result uses the valid second response
        self.assertEqual(result.dimension_scores["factual_accuracy"], 85.0)
        self.assertFalse(result.fallback_used)


class TestFallbackOnExhaustedRetries(unittest.TestCase):
    """Test 4: all calls malformed; verify fallback_used=True and scores are 50.0."""

    @patch("anthropic.Anthropic")
    def test_fallback_on_exhausted_retries(self, MockAnthropic):
        dim_ids = ["factual_accuracy", "analytical_rigor"]

        # All responses have scores out of range
        bad_scores = {"factual_accuracy": 200.0, "analytical_rigor": -10.0}
        bad_response = _make_response([_make_tool_use_block(bad_scores)])

        mock_client = MagicMock()
        MockAnthropic.return_value = mock_client
        # Return bad response on all 3 attempts (initial + 2 retries)
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
    """Test 5: mock returns critical_failures list; verify propagated to JudgeResult."""

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


if __name__ == "__main__":
    unittest.main()
