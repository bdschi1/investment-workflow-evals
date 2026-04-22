"""Tests for src/iaa_report.py — inter-annotator agreement metrics."""

from __future__ import annotations

import math

import pytest

from src.iaa_report import (
    IAAResult,
    cohen_kappa_weighted,
    compute_iaa_report,
    format_iaa_markdown,
    interpret_kappa,
    krippendorff_alpha,
    pairwise_pearson,
)

# ---------------------------------------------------------------------------
# Cohen's weighted kappa
# ---------------------------------------------------------------------------


class TestCohenKappaWeighted:
    def test_perfect_agreement_yields_one(self):
        # Identical scores across 5 items.
        a = [10.0, 30.0, 50.0, 70.0, 90.0]
        b = [10.0, 30.0, 50.0, 70.0, 90.0]
        assert cohen_kappa_weighted(a, b) == pytest.approx(1.0)

    def test_exact_match_binary_bins(self):
        # With n_bins=2, identical labels.
        a = [5.0, 60.0, 10.0, 80.0, 95.0]
        b = [1.0, 70.0, 20.0, 99.0, 88.0]
        # After binning at 50: [0,1,0,1,1] vs [0,1,0,1,1].
        assert cohen_kappa_weighted(a, b, n_bins=2) == pytest.approx(1.0)

    def test_worked_example_binary_confusion_matrix(self):
        """Worked example derived from first principles.

        Build a 2-bin confusion matrix:
                   B=0   B=1   row
            A=0     5     3     8
            A=1     2    10    12
            col     7    13    20

        Observed agreement p_o = (5+10)/20 = 0.75
        Expected p_e = (8*7 + 12*13) / 400 = 212/400 = 0.53
        kappa = (p_o - p_e) / (1 - p_e) = 0.22 / 0.47 ~ 0.4681

        With 2 bins the linear-weighted kappa reduces to unweighted kappa
        because w_ij in {0, 1}. Derivation checked by hand; no external
        reference value hardcoded.
        """
        # 0 represents scores <= 50, 1 represents scores > 50 with n_bins=2
        # Binning uses width 50 over [0, 100], so <50 -> bin 0, >=50 -> bin 1.
        # Use 25 (bin 0) and 75 (bin 1) to keep it unambiguous.
        a_labels = [0] * 5 + [0] * 3 + [1] * 2 + [1] * 10
        b_labels = [0] * 5 + [1] * 3 + [0] * 2 + [1] * 10
        a = [25.0 if x == 0 else 75.0 for x in a_labels]
        b = [25.0 if x == 0 else 75.0 for x in b_labels]
        k = cohen_kappa_weighted(a, b, n_bins=2)
        assert k == pytest.approx(0.22 / 0.47, abs=1e-4)

    def test_systematic_disagreement_negative(self):
        # Rater A calls every item low, rater B calls every item high
        # across alternating items -> negative kappa expected.
        a = [10.0, 90.0, 10.0, 90.0, 10.0, 90.0]
        b = [90.0, 10.0, 90.0, 10.0, 90.0, 10.0]
        k = cohen_kappa_weighted(a, b, n_bins=2)
        assert k < 0.0
        assert k >= -1.0

    def test_chance_level_near_zero(self):
        # Constructed so observed ~ expected agreement.
        # Both raters split roughly 50/50 but independently.
        a = [10.0, 90.0, 10.0, 90.0, 10.0, 90.0, 10.0, 90.0]
        b = [10.0, 10.0, 90.0, 90.0, 10.0, 10.0, 90.0, 90.0]
        k = cohen_kappa_weighted(a, b, n_bins=2)
        # Should be near zero, tolerate a broad band.
        assert abs(k) < 0.5

    def test_mismatched_lengths_raise(self):
        with pytest.raises(ValueError):
            cohen_kappa_weighted([1.0, 2.0], [1.0, 2.0, 3.0])

    def test_n_less_than_three_returns_nan(self):
        assert math.isnan(cohen_kappa_weighted([50.0, 60.0], [50.0, 60.0]))

    def test_all_identical_scores_returns_one(self):
        # Degenerate: all same score on both sides.
        a = [50.0] * 5
        b = [50.0] * 5
        assert cohen_kappa_weighted(a, b) == pytest.approx(1.0)

    def test_ordinal_near_miss_better_than_far_miss(self):
        """Linear weights: a one-bin off mistake penalizes less than a
        far-off mistake. Verify by construction."""
        # Case A: each disagreement is adjacent bins (off by 1).
        a_near = [10.0, 30.0, 50.0, 70.0, 90.0, 10.0, 30.0, 50.0, 70.0, 90.0]
        b_near = [30.0, 10.0, 70.0, 50.0, 70.0, 30.0, 10.0, 70.0, 50.0, 70.0]
        # Case B: same number of disagreements but extreme (off by 4).
        a_far = [10.0, 10.0, 10.0, 10.0, 10.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        b_far = [90.0, 90.0, 90.0, 90.0, 90.0, 10.0, 10.0, 10.0, 10.0, 10.0]
        k_near = cohen_kappa_weighted(a_near, b_near)
        k_far = cohen_kappa_weighted(a_far, b_far)
        # "Closer" disagreements yield a higher (less-negative) kappa.
        assert k_near > k_far


# ---------------------------------------------------------------------------
# Krippendorff's alpha
# ---------------------------------------------------------------------------


class TestKrippendorffAlpha:
    def test_two_raters_perfect_agreement(self):
        ratings = {
            "item1": {"rA": 10.0, "rB": 10.0},
            "item2": {"rA": 50.0, "rB": 50.0},
            "item3": {"rA": 90.0, "rB": 90.0},
        }
        assert krippendorff_alpha(ratings, level="interval") == pytest.approx(1.0)

    def test_three_raters_partial_agreement(self):
        ratings = {
            "item1": {"rA": 10.0, "rB": 12.0, "rC": 11.0},
            "item2": {"rA": 50.0, "rB": 48.0, "rC": 52.0},
            "item3": {"rA": 90.0, "rB": 88.0, "rC": 92.0},
            "item4": {"rA": 70.0, "rB": 72.0, "rC": 68.0},
        }
        alpha = krippendorff_alpha(ratings, level="interval")
        # Tight agreement on well-spread items -> high alpha.
        assert alpha > 0.95

    def test_missing_data_handled(self):
        # One rater missing for some items; alpha should still compute.
        ratings = {
            "item1": {"rA": 10.0, "rB": 12.0, "rC": 11.0},
            "item2": {"rA": 50.0, "rB": 48.0},  # rC missing
            "item3": {"rA": 90.0, "rC": 92.0},  # rB missing
            "item4": {"rA": 70.0, "rB": 72.0, "rC": 68.0},
        }
        alpha = krippendorff_alpha(ratings, level="interval")
        assert not math.isnan(alpha)
        assert alpha > 0.9

    def test_single_rater_returns_nan(self):
        ratings = {
            "item1": {"rA": 10.0},
            "item2": {"rA": 20.0},
        }
        assert math.isnan(krippendorff_alpha(ratings))

    def test_all_identical_returns_one(self):
        ratings = {
            "item1": {"rA": 50.0, "rB": 50.0, "rC": 50.0},
            "item2": {"rA": 50.0, "rB": 50.0, "rC": 50.0},
        }
        # D_o = 0 and D_e = 0 -> convention returns 1.0.
        assert krippendorff_alpha(ratings) == pytest.approx(1.0)

    def test_nominal_level(self):
        ratings = {
            "item1": {"rA": 1, "rB": 1},
            "item2": {"rA": 2, "rB": 2},
            "item3": {"rA": 3, "rB": 3},
            "item4": {"rA": 1, "rB": 2},
        }
        alpha = krippendorff_alpha(ratings, level="nominal")
        assert not math.isnan(alpha)
        assert alpha > 0.0
        assert alpha < 1.0

    def test_pinned_hand_computed_interval_example(self):
        """Worked example with exact expected value, derived from first principles.

        4 items, 2 raters; interval distance = (v1 - v2)^2.

            Item 1: A=1, B=1   d^2 = 0
            Item 2: A=2, B=3   d^2 = 1
            Item 3: A=3, B=3   d^2 = 0
            Item 4: A=3, B=2   d^2 = 1

        D_o (observed) = sum_ordered d^2 / sum m*(m-1) = (2*2) / (4*2) = 0.5
        Pooled values = [1, 1, 2, 2, 3, 3, 3, 3];  N = 8;  N*(N-1) = 56
        Ordered cross-pair squared distances:
            (1,2): 2*2*2 = 8 ordered pairs * 1 = 8
            (1,3): 2*4*2 = 16 ordered pairs * 4 = 64
            (2,3): 2*4*2 = 16 ordered pairs * 1 = 16
        D_e = (8 + 64 + 16) / 56 = 88/56 = 11/7
        alpha = 1 - (1/2) / (11/7) = 1 - 7/22 = 15/22 = 0.6818...
        """
        ratings = {
            1: {"A": 1, "B": 1},
            2: {"A": 2, "B": 3},
            3: {"A": 3, "B": 3},
            4: {"A": 3, "B": 2},
        }
        alpha = krippendorff_alpha(ratings, level="interval")
        assert alpha == pytest.approx(15.0 / 22.0, abs=1e-9)

    def test_perfect_negative_symmetry(self):
        """Reversed ordering on a linear scale yields alpha = -0.8 (hand-verifiable).

        5 items with A=[1..5] and B=[5..1]. By symmetry of squared distance
        around the pooled mean, alpha should be exactly the negative of
        constant-shift alpha (0.8), i.e. -0.8.
        """
        ratings = {
            1: {"A": 1, "B": 5},
            2: {"A": 2, "B": 4},
            3: {"A": 3, "B": 3},
            4: {"A": 4, "B": 2},
            5: {"A": 5, "B": 1},
        }
        alpha = krippendorff_alpha(ratings, level="interval")
        assert alpha == pytest.approx(-0.8, abs=1e-9)

    def test_permutation_invariance(self):
        """Swapping which rater is labelled 'A' vs 'B' must not change alpha."""
        original = {
            1: {"A": 10.0, "B": 12.0},
            2: {"A": 50.0, "B": 55.0},
            3: {"A": 80.0, "B": 78.0},
            4: {"A": 30.0, "B": 35.0},
        }
        swapped = {k: {"A": v["B"], "B": v["A"]} for k, v in original.items()}
        assert krippendorff_alpha(original) == pytest.approx(
            krippendorff_alpha(swapped)
        )

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError):
            krippendorff_alpha({"i": {"a": 1, "b": 2}}, level="ordinal")


# ---------------------------------------------------------------------------
# Pearson
# ---------------------------------------------------------------------------


class TestPairwisePearson:
    def test_perfect_correlation(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [2.0, 4.0, 6.0, 8.0, 10.0]
        assert pairwise_pearson(a, b) == pytest.approx(1.0)

    def test_perfect_negative_correlation(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [5.0, 4.0, 3.0, 2.0, 1.0]
        assert pairwise_pearson(a, b) == pytest.approx(-1.0)

    def test_zero_variance_returns_nan(self):
        a = [5.0, 5.0, 5.0]
        b = [1.0, 2.0, 3.0]
        assert math.isnan(pairwise_pearson(a, b))


# ---------------------------------------------------------------------------
# Interpretation (Landis & Koch 1977)
# ---------------------------------------------------------------------------


class TestInterpretKappa:
    def test_poor_band(self):
        assert "poor" in interpret_kappa(-0.1)

    def test_slight_band(self):
        assert "slight" in interpret_kappa(0.1)

    def test_fair_band(self):
        assert "fair" in interpret_kappa(0.3)

    def test_moderate_band(self):
        assert "moderate" in interpret_kappa(0.5)

    def test_substantial_band(self):
        assert "substantial" in interpret_kappa(0.72)

    def test_near_perfect_band(self):
        assert "near-perfect" in interpret_kappa(0.9)

    def test_nan_handled(self):
        out = interpret_kappa(float("nan"))
        assert "undefined" in out or "insufficient" in out


# ---------------------------------------------------------------------------
# compute_iaa_report
# ---------------------------------------------------------------------------


class TestComputeIAAReport:
    def _sample_records(self):
        # 2 raters, 5 scenarios, 3 dimensions.
        dims = ["alpha_environment", "risk_framework", "communication"]
        raters = ["rater_A", "rater_B"]
        scores = {
            "rater_A": {
                "s1": [85.0, 70.0, 90.0],
                "s2": [60.0, 55.0, 65.0],
                "s3": [40.0, 50.0, 45.0],
                "s4": [75.0, 80.0, 70.0],
                "s5": [30.0, 35.0, 25.0],
            },
            "rater_B": {
                "s1": [82.0, 72.0, 88.0],
                "s2": [62.0, 58.0, 63.0],
                "s3": [45.0, 48.0, 42.0],
                "s4": [78.0, 80.0, 72.0],
                "s5": [32.0, 38.0, 28.0],
            },
        }
        records = []
        for r in raters:
            for item, vec in scores[r].items():
                records.append(
                    {
                        "item_id": item,
                        "annotator_id": r,
                        "dimension_scores": dict(zip(dims, vec)),
                    }
                )
        return records, dims

    def test_two_raters_three_dims_produces_three_kappa_rows(self):
        records, dims = self._sample_records()
        results = compute_iaa_report(records)
        kappa_rows = [r for r in results if r.method == "cohen_kappa_weighted"]
        assert len(kappa_rows) == 3
        for row in kappa_rows:
            assert row.dimension in dims
            assert row.n_items == 5
            assert row.raters == ("rater_A", "rater_B")

    def test_two_raters_also_emit_pearson(self):
        records, _ = self._sample_records()
        results = compute_iaa_report(records)
        pearson_rows = [r for r in results if r.method == "pairwise_pearson"]
        assert len(pearson_rows) == 3

    def test_no_krippendorff_with_two_raters(self):
        records, _ = self._sample_records()
        results = compute_iaa_report(records)
        alpha_rows = [r for r in results if r.method == "krippendorff_alpha"]
        assert alpha_rows == []

    def test_three_raters_produce_alpha(self):
        records, _ = self._sample_records()
        # Add a third rater with similar scores.
        for i, item in enumerate(["s1", "s2", "s3", "s4", "s5"]):
            vec = [80.0 - i * 5, 75.0 - i * 5, 85.0 - i * 5]
            records.append(
                {
                    "item_id": item,
                    "annotator_id": "rater_C",
                    "dimension_scores": {
                        "alpha_environment": vec[0],
                        "risk_framework": vec[1],
                        "communication": vec[2],
                    },
                }
            )
        results = compute_iaa_report(records)
        alpha_rows = [r for r in results if r.method == "krippendorff_alpha"]
        # One alpha per dimension.
        assert len(alpha_rows) == 3

    def test_empty_records_returns_empty_list(self):
        assert compute_iaa_report([]) == []

    def test_single_rater_returns_no_kappa(self):
        records = [
            {"item_id": "s1", "annotator_id": "rA", "dimension_scores": {"d": 50.0}},
            {"item_id": "s2", "annotator_id": "rA", "dimension_scores": {"d": 60.0}},
        ]
        results = compute_iaa_report(records)
        # No rater pairs possible.
        assert all(r.method != "cohen_kappa_weighted" for r in results)

    def test_n_less_than_three_reported_as_insufficient(self):
        records = [
            {"item_id": "s1", "annotator_id": "rA", "dimension_scores": {"d": 50.0}},
            {"item_id": "s1", "annotator_id": "rB", "dimension_scores": {"d": 55.0}},
            {"item_id": "s2", "annotator_id": "rA", "dimension_scores": {"d": 60.0}},
            {"item_id": "s2", "annotator_id": "rB", "dimension_scores": {"d": 62.0}},
        ]
        results = compute_iaa_report(records)
        kappa_rows = [r for r in results if r.method == "cohen_kappa_weighted"]
        assert len(kappa_rows) == 1
        assert math.isnan(kappa_rows[0].agreement)
        assert "insufficient" in kappa_rows[0].interpretation

    def test_dimensions_filter_applied(self):
        records, _ = self._sample_records()
        results = compute_iaa_report(records, dimensions=["alpha_environment"])
        dims_seen = {r.dimension for r in results}
        assert dims_seen == {"alpha_environment"}

    def test_result_objects_are_iaaresult(self):
        records, _ = self._sample_records()
        results = compute_iaa_report(records)
        for r in results:
            assert isinstance(r, IAAResult)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


class TestFormatMarkdown:
    def test_empty_produces_placeholder(self):
        out = format_iaa_markdown([])
        assert "Inter-Annotator Agreement" in out
        assert "No results" in out

    def test_markdown_contains_header_and_body(self):
        results = [
            IAAResult(
                method="cohen_kappa_weighted",
                dimension="alpha",
                raters=("rA", "rB"),
                agreement=0.75,
                n_items=5,
                interpretation="substantial agreement (k=0.75)",
            ),
            IAAResult(
                method="pairwise_pearson",
                dimension="alpha",
                raters=("rA", "rB"),
                agreement=0.88,
                n_items=5,
                interpretation="Pearson r=0.88",
            ),
        ]
        md = format_iaa_markdown(results)
        # Table header present.
        assert "| Rater Pair | Weighted Cohen's k" in md
        # One body row (one pair, both metrics collapsed).
        rA_vs_rB_rows = [line for line in md.splitlines() if "rA vs rB" in line]
        assert len(rA_vs_rB_rows) == 1
        assert "0.750" in rA_vs_rB_rows[0]
        assert "0.880" in rA_vs_rB_rows[0]

    def test_markdown_renders_alpha_section(self):
        results = [
            IAAResult(
                method="krippendorff_alpha",
                dimension="alpha",
                raters=["rA", "rB", "rC"],
                agreement=0.81,
                n_items=10,
                interpretation="alpha=0.81",
            ),
        ]
        md = format_iaa_markdown(results)
        assert "Krippendorff" in md
        assert "0.810" in md

    def test_multiple_dimensions_are_grouped(self):
        results = [
            IAAResult(
                "cohen_kappa_weighted",
                "alpha",
                ("rA", "rB"),
                0.7,
                5,
                "substantial agreement (k=0.70)",
            ),
            IAAResult(
                "cohen_kappa_weighted",
                "risk",
                ("rA", "rB"),
                0.5,
                5,
                "moderate agreement (k=0.50)",
            ),
        ]
        md = format_iaa_markdown(results)
        assert "## Dimension: `alpha`" in md
        assert "## Dimension: `risk`" in md
