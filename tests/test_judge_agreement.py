"""Tests for tools/judge_agreement.py — WorkflowJudgeAgreement.

No network access required; all computations are pure Python.
"""

from __future__ import annotations

import unittest

from tools.judge_agreement import IWEAgreementResult, WorkflowJudgeAgreement


class TestIWEAgreementResultFields(unittest.TestCase):
    """Test 1: IWEAgreementResult has all required fields."""

    def test_agreement_result_has_required_fields(self) -> None:
        result = IWEAgreementResult(
            dimension_correlations={"factual_accuracy": 0.85},
            overall_correlation=0.82,
            n_compared=15,
            low_agreement_dimensions=[],
            warning="",
        )
        self.assertIsInstance(result.dimension_correlations, dict)
        self.assertIsInstance(result.overall_correlation, float)
        self.assertIsInstance(result.n_compared, int)
        self.assertIsInstance(result.low_agreement_dimensions, list)
        self.assertIsInstance(result.warning, str)
        self.assertEqual(result.overall_correlation, 0.82)
        self.assertEqual(result.n_compared, 15)


class TestPearsonCorrelation(unittest.TestCase):
    """Test 2: pearson_correlation produces correct values for known inputs."""

    def test_perfect_positive_correlation(self) -> None:
        x = [10.0, 20.0, 30.0, 40.0, 50.0]
        y = [10.0, 20.0, 30.0, 40.0, 50.0]
        r = WorkflowJudgeAgreement.pearson_correlation(x, y)
        self.assertAlmostEqual(r, 1.0, places=6)

    def test_perfect_negative_correlation(self) -> None:
        x = [10.0, 20.0, 30.0, 40.0, 50.0]
        y = [50.0, 40.0, 30.0, 20.0, 10.0]
        r = WorkflowJudgeAgreement.pearson_correlation(x, y)
        self.assertAlmostEqual(r, -1.0, places=6)

    def test_known_correlation_value(self) -> None:
        """Verify against manually computed Pearson r."""
        # x = [1, 2, 3, 4, 5], y = [2, 4, 5, 4, 5]
        # mean_x = 3, mean_y = 4
        # cov = (1-3)(2-4) + (2-3)(4-4) + (3-3)(5-4) + (4-3)(4-4) + (5-3)(5-4)
        #      = (-2)(-2) + (-1)(0) + (0)(1) + (1)(0) + (2)(1)
        #      = 4 + 0 + 0 + 0 + 2 = 6
        # var_x = 4 + 1 + 0 + 1 + 4 = 10
        # var_y = 4 + 0 + 1 + 0 + 1 = 6
        # r = 6 / sqrt(60) ≈ 0.7746
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 5.0, 4.0, 5.0]
        r = WorkflowJudgeAgreement.pearson_correlation(x, y)
        import math
        expected = 6.0 / math.sqrt(60.0)
        self.assertAlmostEqual(r, expected, places=4)

    def test_zero_variance_returns_zero(self) -> None:
        # Constant series — correlation undefined, should return 0.
        x = [50.0, 50.0, 50.0, 50.0, 50.0]
        y = [10.0, 20.0, 30.0, 40.0, 50.0]
        r = WorkflowJudgeAgreement.pearson_correlation(x, y)
        self.assertEqual(r, 0.0)

    def test_raises_on_length_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            WorkflowJudgeAgreement.pearson_correlation([1.0, 2.0], [1.0])


class TestWarningTriggered(unittest.TestCase):
    """Test 3: warning is populated when overall correlation < 0.6."""

    def test_warning_triggered_below_threshold(self) -> None:
        agreement = WorkflowJudgeAgreement()

        # Build items with low correlation: AI scores high where heuristic scores low.
        items = [
            {"ai_scores": {"d1": 80.0, "d2": 70.0, "d3": 60.0},
             "heuristic_scores": {"d1": 20.0, "d2": 30.0, "d3": 40.0}},
            {"ai_scores": {"d1": 75.0, "d2": 65.0, "d3": 55.0},
             "heuristic_scores": {"d1": 25.0, "d2": 35.0, "d3": 45.0}},
            {"ai_scores": {"d1": 90.0, "d2": 80.0, "d3": 70.0},
             "heuristic_scores": {"d1": 10.0, "d2": 20.0, "d3": 30.0}},
        ]

        result = agreement.batch_compare(items)
        # Correlation between high AI and low heuristic should be strongly negative
        # or very low — in either case below 0.6, triggering the warning.
        self.assertLess(result.overall_correlation, 0.6)
        self.assertNotEqual(result.warning, "")
        self.assertIn("threshold", result.warning.lower())

    def test_no_warning_when_correlation_high(self) -> None:
        agreement = WorkflowJudgeAgreement()

        # Perfect positive correlation → r = 1.0 → no warning.
        items = [
            {"ai_scores": {"d1": 80.0, "d2": 70.0, "d3": 60.0},
             "heuristic_scores": {"d1": 79.0, "d2": 69.0, "d3": 59.0}},
            {"ai_scores": {"d1": 75.0, "d2": 65.0, "d3": 55.0},
             "heuristic_scores": {"d1": 74.0, "d2": 64.0, "d3": 54.0}},
            {"ai_scores": {"d1": 90.0, "d2": 85.0, "d3": 80.0},
             "heuristic_scores": {"d1": 89.0, "d2": 84.0, "d3": 79.0}},
        ]

        result = agreement.batch_compare(items)
        self.assertGreater(result.overall_correlation, 0.6)
        self.assertEqual(result.warning, "")

    def test_insufficient_data_returns_warning(self) -> None:
        agreement = WorkflowJudgeAgreement()
        result = agreement.batch_compare([])
        self.assertEqual(result.overall_correlation, 0.0)
        self.assertNotEqual(result.warning, "")


if __name__ == "__main__":
    unittest.main()
