"""Tests for tools/judge_agreement.py — WorkflowJudgeAgreement + agreement metrics.

No network access required; all computations are pure Python.
"""

from __future__ import annotations

import math
import random
import unittest

from tools.judge_agreement import (
    IWEAgreementResult,
    WorkflowJudgeAgreement,
    cohens_kappa_weighted,
    compute_full_agreement,
    spearman_rho,
)


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

    def test_agreement_result_default_new_metrics(self) -> None:
        # Backward-compat: spearman and kappa_weighted default to 0.0 when
        # legacy callers construct IWEAgreementResult without them.
        result = IWEAgreementResult(
            dimension_correlations={},
            overall_correlation=0.7,
            n_compared=10,
            low_agreement_dimensions=[],
            warning="",
        )
        self.assertEqual(result.spearman, 0.0)
        self.assertEqual(result.kappa_weighted, 0.0)


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
            {
                "ai_scores": {"d1": 80.0, "d2": 70.0, "d3": 60.0},
                "heuristic_scores": {"d1": 20.0, "d2": 30.0, "d3": 40.0},
            },
            {
                "ai_scores": {"d1": 75.0, "d2": 65.0, "d3": 55.0},
                "heuristic_scores": {"d1": 25.0, "d2": 35.0, "d3": 45.0},
            },
            {
                "ai_scores": {"d1": 90.0, "d2": 80.0, "d3": 70.0},
                "heuristic_scores": {"d1": 10.0, "d2": 20.0, "d3": 30.0},
            },
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
            {
                "ai_scores": {"d1": 80.0, "d2": 70.0, "d3": 60.0},
                "heuristic_scores": {"d1": 79.0, "d2": 69.0, "d3": 59.0},
            },
            {
                "ai_scores": {"d1": 75.0, "d2": 65.0, "d3": 55.0},
                "heuristic_scores": {"d1": 74.0, "d2": 64.0, "d3": 54.0},
            },
            {
                "ai_scores": {"d1": 90.0, "d2": 85.0, "d3": 80.0},
                "heuristic_scores": {"d1": 89.0, "d2": 84.0, "d3": 79.0},
            },
        ]

        result = agreement.batch_compare(items)
        self.assertGreater(result.overall_correlation, 0.6)
        self.assertEqual(result.warning, "")

    def test_insufficient_data_returns_warning(self) -> None:
        agreement = WorkflowJudgeAgreement()
        result = agreement.batch_compare([])
        self.assertEqual(result.overall_correlation, 0.0)
        self.assertNotEqual(result.warning, "")


# ---------------------------------------------------------------------------
# New metric tests (v1.1)
# ---------------------------------------------------------------------------


class TestSpearmanRho(unittest.TestCase):
    """Spearman rank correlation."""

    def test_perfect_rank_equals_one(self) -> None:
        # Monotone-increasing but not linear — Spearman = 1 even though Pearson < 1.
        xs = [1.0, 2.0, 3.0, 4.0, 5.0]
        ys = [1.0, 4.0, 9.0, 16.0, 25.0]
        self.assertAlmostEqual(spearman_rho(xs, ys), 1.0, places=6)

    def test_reverse_rank_equals_minus_one(self) -> None:
        xs = [1.0, 2.0, 3.0, 4.0, 5.0]
        ys = [50.0, 40.0, 30.0, 20.0, 10.0]
        self.assertAlmostEqual(spearman_rho(xs, ys), -1.0, places=6)

    def test_near_zero_for_uncorrelated(self) -> None:
        # Deterministic permutation designed to have near-zero rank correlation.
        xs = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        ys = [5.0, 9.0, 2.0, 10.0, 1.0, 7.0, 3.0, 8.0, 4.0, 6.0]
        rho = spearman_rho(xs, ys)
        self.assertLess(abs(rho), 0.4)

    def test_handles_ties_with_average_ranks(self) -> None:
        # Both series have a tie; average-rank convention means ρ is still well defined.
        xs = [10.0, 20.0, 20.0, 40.0]
        ys = [1.0, 2.0, 2.0, 4.0]
        rho = spearman_rho(xs, ys)
        self.assertAlmostEqual(rho, 1.0, places=6)

    def test_length_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            spearman_rho([1.0, 2.0], [1.0])

    def test_short_series_returns_zero(self) -> None:
        self.assertEqual(spearman_rho([1.0], [1.0]), 0.0)
        self.assertEqual(spearman_rho([], []), 0.0)


class TestCohensKappaWeighted(unittest.TestCase):
    """Weighted Cohen's κ on 5-bin discretised scores."""

    def test_perfect_agreement_returns_one(self) -> None:
        xs = [10.0, 30.0, 50.0, 70.0, 90.0]
        ys = [10.0, 30.0, 50.0, 70.0, 90.0]
        self.assertAlmostEqual(cohens_kappa_weighted(xs, ys), 1.0, places=6)

    def test_zero_variance_identical_returns_one(self) -> None:
        xs = [50.0, 50.0, 50.0]
        ys = [50.0, 50.0, 50.0]
        self.assertAlmostEqual(cohens_kappa_weighted(xs, ys), 1.0, places=6)

    def test_zero_variance_nonidentical_returns_nan(self) -> None:
        # Both series constant but in different bins.
        xs = [50.0, 50.0, 50.0]
        ys = [70.0, 70.0, 70.0]
        result = cohens_kappa_weighted(xs, ys)
        self.assertTrue(math.isnan(result))

    def test_one_constant_other_varying_returns_nan(self) -> None:
        xs = [50.0, 50.0, 50.0, 50.0]
        ys = [10.0, 30.0, 50.0, 90.0]
        self.assertTrue(math.isnan(cohens_kappa_weighted(xs, ys)))

    def test_every_prediction_off_by_one_bin_range(self) -> None:
        # Rater A bins span 0-3, Rater B bins span 1-4 — each off by exactly
        # one bin. With linear weights on 5 bins this yields κ ≈ 0.33, not
        # 0.75 (0.75 is the per-item weighted-agreement value
        # 1 - |i-j|/(k-1), not κ itself, which divides by chance-expected
        # disagreement). Tight band around the analytic value.
        xs = [10.0, 30.0, 50.0, 70.0]  # bins 0,1,2,3
        ys = [30.0, 50.0, 70.0, 90.0]  # bins 1,2,3,4
        kappa = cohens_kappa_weighted(xs, ys)
        self.assertGreater(kappa, 0.2)
        self.assertLess(kappa, 0.5)

    def test_diagonal_weighted_agreement_partial(self) -> None:
        # When some predictions match exactly and others are off by one bin,
        # κ should lie strictly between the off-by-one value and 1.0.
        xs = [10.0, 30.0, 50.0, 70.0, 90.0]
        ys = [10.0, 30.0, 70.0, 70.0, 90.0]  # one off-by-one mismatch
        kappa = cohens_kappa_weighted(xs, ys)
        self.assertGreater(kappa, 0.5)
        self.assertLess(kappa, 1.0)

    def test_length_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            cohens_kappa_weighted([1.0, 2.0], [1.0])

    def test_invalid_n_bins_raises(self) -> None:
        with self.assertRaises(ValueError):
            cohens_kappa_weighted([10.0, 20.0], [30.0, 40.0], n_bins=1)

    def test_short_series_returns_nan(self) -> None:
        self.assertTrue(math.isnan(cohens_kappa_weighted([10.0], [20.0])))

    def test_scores_at_upper_bound_stay_in_top_bin(self) -> None:
        # Edge case: 100.0 should bin to 4 (the top bin), not overflow to 5.
        xs = [100.0, 100.0, 80.0, 80.0]
        ys = [100.0, 100.0, 80.0, 80.0]
        self.assertAlmostEqual(cohens_kappa_weighted(xs, ys), 1.0, places=6)

    def test_max_disagreement_gives_negative_kappa(self) -> None:
        # Anti-correlated pattern across the full bin range: κ should be
        # well below zero once marginals are spread out enough for the
        # chance correction to penalise systematic disagreement.
        xs = [10.0, 30.0, 50.0, 70.0, 90.0]  # bins 0,1,2,3,4
        ys = [90.0, 70.0, 50.0, 30.0, 10.0]  # bins 4,3,2,1,0
        kappa = cohens_kappa_weighted(xs, ys)
        self.assertLess(kappa, 0.0)


class TestComputeFullAgreement(unittest.TestCase):
    """compute_full_agreement returns all three metrics."""

    def test_returns_all_keys(self) -> None:
        xs = [10.0, 20.0, 30.0, 40.0, 50.0]
        ys = [12.0, 19.0, 31.0, 42.0, 48.0]
        metrics = compute_full_agreement(xs, ys)
        self.assertIn("pearson", metrics)
        self.assertIn("spearman", metrics)
        self.assertIn("kappa_weighted", metrics)
        self.assertIn("n", metrics)
        self.assertEqual(metrics["n"], 5)

    def test_perfect_identical_all_one(self) -> None:
        xs = [10.0, 30.0, 50.0, 70.0, 90.0]
        metrics = compute_full_agreement(xs, xs)
        self.assertAlmostEqual(metrics["pearson"], 1.0, places=6)
        self.assertAlmostEqual(metrics["spearman"], 1.0, places=6)
        self.assertAlmostEqual(metrics["kappa_weighted"], 1.0, places=6)

    def test_length_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            compute_full_agreement([1.0, 2.0], [1.0])


class TestIntegrationCompareAndBatch(unittest.TestCase):
    """compare() and batch_compare() include the new metrics and warnings."""

    def test_compare_includes_new_metrics(self) -> None:
        agreement = WorkflowJudgeAgreement()
        ai_scores = {"d1": 80.0, "d2": 70.0, "d3": 60.0, "d4": 90.0, "d5": 50.0}
        heur_scores = {"d1": 78.0, "d2": 72.0, "d3": 65.0, "d4": 88.0, "d5": 52.0}
        result = agreement.compare({}, {}, "", ai_scores, heur_scores)
        # High correlation — no warning expected.
        self.assertGreater(result.overall_correlation, 0.6)
        self.assertGreater(result.spearman, 0.5)
        self.assertGreaterEqual(result.kappa_weighted, 0.0)
        self.assertLessEqual(result.kappa_weighted, 1.0)

    def test_batch_compare_on_10_item_synthetic_sample(self) -> None:
        # Synthetic sample where heuristic tracks AI with small noise.
        rng = random.Random(42)
        items = []
        for _ in range(10):
            ai = {
                "factual_accuracy": rng.uniform(50, 95),
                "analytical_rigor": rng.uniform(40, 90),
                "risk_assessment": rng.uniform(30, 85),
                "evidence_quality": rng.uniform(45, 95),
                "completeness": rng.uniform(50, 90),
            }
            heur = {
                k: max(0.0, min(100.0, v + rng.gauss(0, 5.0))) for k, v in ai.items()
            }
            items.append({"ai_scores": ai, "heuristic_scores": heur})
        agreement = WorkflowJudgeAgreement()
        result = agreement.batch_compare(items)
        # Low-noise tracking — all three metrics should be comfortably high.
        self.assertGreater(result.overall_correlation, 0.8)
        self.assertGreater(result.spearman, 0.8)
        self.assertGreater(result.kappa_weighted, 0.5)
        self.assertEqual(result.n_compared, 50)  # 10 items × 5 dims

    def test_kappa_warning_triggered_on_poor_agreement(self) -> None:
        # Flipped magnitudes → all three metrics should be poor.
        agreement = WorkflowJudgeAgreement()
        items = [
            {
                "ai_scores": {"d1": 90.0, "d2": 85.0, "d3": 80.0, "d4": 95.0},
                "heuristic_scores": {"d1": 10.0, "d2": 15.0, "d3": 20.0, "d4": 5.0},
            },
            {
                "ai_scores": {"d1": 75.0, "d2": 70.0, "d3": 65.0, "d4": 80.0},
                "heuristic_scores": {"d1": 25.0, "d2": 30.0, "d3": 35.0, "d4": 20.0},
            },
        ]
        result = agreement.batch_compare(items)
        self.assertLess(result.kappa_weighted, 0.4)
        self.assertTrue(
            "Pearson" in result.warning
            or "Spearman" in result.warning
            or "kappa" in result.warning.lower(),
        )


if __name__ == "__main__":
    unittest.main()
