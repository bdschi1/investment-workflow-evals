"""Judge agreement metrics for investment-workflow-evals.

Compares InvestmentWorkflowJudge (AI) vs GradingEngine (heuristic) on the same
responses. Computes three complementary agreement metrics:

- Pearson r   — linear correlation between continuous scores (original metric).
- Spearman ρ  — rank correlation; robust to monotone non-linear transforms.
- Cohen's κ   — weighted (linear) κ on scores binned into 5 rubric levels
                (Fail, Poor, Acceptable, Good, Excellent); measures
                categorical-like agreement on the discretised rubric.

Warnings are raised when Pearson r < 0.6, Spearman ρ < 0.5, or weighted
κ < 0.4. These thresholds are heuristic — treat them as soft signals that
the judge prompt or rubric anchors may need revision.

# module_version: 1.1.0
# date: 2026-04-21
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum number of comparison pairs required before computing correlation.
_MIN_PAIRS = 3


@dataclass
class IWEAgreementResult:
    """Agreement between AI judge and heuristic grader.

    Pearson r is retained as the primary overall_correlation for backward
    compatibility. Spearman ρ and weighted Cohen's κ are reported alongside
    as additional views of the same paired score data.
    """

    dimension_correlations: dict[str, float]  # dimension -> Pearson r
    overall_correlation: float  # overall Pearson r
    n_compared: int
    low_agreement_dimensions: list[str]  # dimensions with Pearson r < 0.6
    warning: str = ""
    # Additional metrics (v1.1). Default 0.0 so legacy callers that construct
    # IWEAgreementResult directly still work.
    spearman: float = 0.0
    kappa_weighted: float = 0.0


class WorkflowJudgeAgreement:
    """Computes multiple agreement metrics between AI judge and heuristic grader.

    IWE grading produces continuous 0-100 scores per dimension. Three metrics
    are reported:

    - **Pearson r**   — linear association; sensitive to scale and outliers.
    - **Spearman ρ**  — rank correlation; monotone-invariant.
    - **Cohen's κ (weighted, linear, 5-bin)** — agreement on discretised
      rubric levels, corrected for chance. Uses the rubric-aligned bins
      [0, 20, 40, 60, 80, 100] corresponding to Fail/Poor/Acceptable/Good/Excellent.

    Warning thresholds (heuristic):
    - Pearson r < 0.6   → review judge prompt / few-shot examples.
    - Spearman ρ < 0.5  → rank order disagrees; rubric anchors may be miscalibrated.
    - Weighted κ < 0.4  → poor categorical agreement on binned scores.

    Usage — single scenario::

        from tools.judge_agreement import WorkflowJudgeAgreement

        agreement = WorkflowJudgeAgreement()
        result = agreement.compare(
            scenario=scenario_dict,
            rubric=rubric_dict,
            ai_output="...",
            ai_scores={"factual_accuracy": 82.0, ...},
            heuristic_scores={"factual_accuracy": 75.0, ...},
        )
        print(result.overall_correlation, result.spearman, result.kappa_weighted)

    Usage — batch::

        result = agreement.batch_compare([
            {"ai_scores": {...}, "heuristic_scores": {...}},
            ...
        ])
    """

    CORRELATION_WARN_THRESHOLD = 0.6
    SPEARMAN_WARN_THRESHOLD = 0.5
    KAPPA_WARN_THRESHOLD = 0.4

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compare(
        self,
        scenario: dict,
        rubric: dict,
        ai_output: str,
        ai_scores: Optional[dict[str, float]] = None,
        heuristic_scores: Optional[dict[str, float]] = None,
    ) -> IWEAgreementResult:
        """Compare AI judge vs heuristic grader on one scenario.

        ``scenario``, ``rubric``, and ``ai_output`` are accepted for API
        consistency and future use (e.g., lazy grading) but are not consumed
        when pre-computed scores are supplied.

        Args:
            scenario: Scenario dict (kept for API symmetry).
            rubric: Rubric dict (kept for API symmetry).
            ai_output: AI response text (kept for API symmetry).
            ai_scores: dimension_id -> score (0-100) from the AI judge.
            heuristic_scores: dimension_id -> score (0-100) from the heuristic grader.

        Returns:
            IWEAgreementResult. Dimensions only present in both dicts are compared.
        """
        if ai_scores is None or heuristic_scores is None:
            return IWEAgreementResult(
                dimension_correlations={},
                overall_correlation=0.0,
                n_compared=0,
                low_agreement_dimensions=[],
                warning="Insufficient data: both ai_scores and heuristic_scores required.",
                spearman=0.0,
                kappa_weighted=0.0,
            )

        shared_dims = sorted(set(ai_scores.keys()) & set(heuristic_scores.keys()))
        if len(shared_dims) < _MIN_PAIRS:
            return IWEAgreementResult(
                dimension_correlations={},
                overall_correlation=0.0,
                n_compared=len(shared_dims),
                low_agreement_dimensions=[],
                warning=(
                    f"Insufficient comparison dimensions ({len(shared_dims)} < {_MIN_PAIRS}). "
                    "Need at least 3 shared dimensions to compute correlation."
                ),
                spearman=0.0,
                kappa_weighted=0.0,
            )

        all_ai = [ai_scores[d] for d in shared_dims]
        all_heuristic = [heuristic_scores[d] for d in shared_dims]

        metrics = compute_full_agreement(all_ai, all_heuristic)
        overall_r = metrics["pearson"]
        rho = metrics["spearman"]
        kappa = metrics["kappa_weighted"]

        # Per-dimension correlation requires multiple items — report NaN for single-item dims.
        # With a single comparison we only have the cross-dim correlation.
        dim_corr: dict[str, float] = {}

        low_dims: list[str] = []
        warning = self._build_warning(overall_r, rho, kappa)
        if warning:
            logger.warning(warning)

        return IWEAgreementResult(
            dimension_correlations=dim_corr,
            overall_correlation=overall_r,
            n_compared=len(shared_dims),
            low_agreement_dimensions=low_dims,
            warning=warning,
            spearman=rho,
            kappa_weighted=kappa,
        )

    def batch_compare(
        self,
        items: list[dict],
    ) -> IWEAgreementResult:
        """Aggregate agreement across multiple scenario comparisons.

        Each item should contain:
            - ``ai_scores``: dict[str, float]
            - ``heuristic_scores``: dict[str, float]

        Scores are collected per dimension across all items. Per-dimension
        Pearson r requires >= ``_MIN_PAIRS`` data points.

        Returns:
            IWEAgreementResult aggregated across all items, with Pearson,
            Spearman, and weighted κ computed on the pooled score pairs.
        """
        # dimension -> [ai_score, ...] and [heuristic_score, ...]
        dim_ai: dict[str, list[float]] = {}
        dim_heuristic: dict[str, list[float]] = {}

        for item in items:
            ai_s: Optional[dict[str, float]] = item.get("ai_scores")
            heur_s: Optional[dict[str, float]] = item.get("heuristic_scores")
            if ai_s is None or heur_s is None:
                continue
            shared = set(ai_s.keys()) & set(heur_s.keys())
            for dim in shared:
                dim_ai.setdefault(dim, []).append(ai_s[dim])
                dim_heuristic.setdefault(dim, []).append(heur_s[dim])

        if not dim_ai:
            return IWEAgreementResult(
                dimension_correlations={},
                overall_correlation=0.0,
                n_compared=0,
                low_agreement_dimensions=[],
                warning="No comparable dimension scores found across items.",
                spearman=0.0,
                kappa_weighted=0.0,
            )

        # Overall correlation: pool all (ai, heuristic) pairs across dimensions.
        all_ai: list[float] = []
        all_heuristic: list[float] = []
        for dim in dim_ai:
            all_ai.extend(dim_ai[dim])
            all_heuristic.extend(dim_heuristic[dim])

        n_total = len(all_ai)
        if n_total < _MIN_PAIRS:
            return IWEAgreementResult(
                dimension_correlations={},
                overall_correlation=0.0,
                n_compared=n_total,
                low_agreement_dimensions=[],
                warning=(
                    f"Insufficient comparison pairs ({n_total} < {_MIN_PAIRS}). "
                    "Collect more graded responses before interpreting correlation."
                ),
                spearman=0.0,
                kappa_weighted=0.0,
            )

        metrics = compute_full_agreement(all_ai, all_heuristic)
        overall_r = metrics["pearson"]
        rho = metrics["spearman"]
        kappa = metrics["kappa_weighted"]

        dim_corr: dict[str, float] = {}
        for dim in dim_ai:
            if len(dim_ai[dim]) >= _MIN_PAIRS:
                dim_corr[dim] = self.pearson_correlation(
                    dim_ai[dim], dim_heuristic[dim]
                )

        low_dims = [
            d for d, r in dim_corr.items() if r < self.CORRELATION_WARN_THRESHOLD
        ]
        warning = self._build_warning(overall_r, rho, kappa)
        if warning:
            logger.warning(warning)

        return IWEAgreementResult(
            dimension_correlations=dim_corr,
            overall_correlation=overall_r,
            n_compared=n_total,
            low_agreement_dimensions=low_dims,
            warning=warning,
            spearman=rho,
            kappa_weighted=kappa,
        )

    # ------------------------------------------------------------------
    # Warning helper
    # ------------------------------------------------------------------

    def _build_warning(
        self, pearson_r: float, spearman_rho_val: float, kappa: float
    ) -> str:
        """Aggregate warning messages for each metric that fell below threshold.

        κ is skipped when NaN (e.g. zero-variance non-identical inputs) since
        the test is not meaningful there.
        """
        parts: list[str] = []
        if pearson_r < self.CORRELATION_WARN_THRESHOLD:
            parts.append(
                f"Pearson r {pearson_r:.3f} is below the acceptable threshold "
                f"({self.CORRELATION_WARN_THRESHOLD}). Review the judge prompt or "
                "few-shot examples to improve AI/heuristic score alignment."
            )
        if spearman_rho_val < self.SPEARMAN_WARN_THRESHOLD:
            parts.append(
                f"Spearman rho {spearman_rho_val:.3f} is below the acceptable threshold "
                f"({self.SPEARMAN_WARN_THRESHOLD}). Rank order disagrees — rubric "
                "anchors may be miscalibrated."
            )
        if not math.isnan(kappa) and kappa < self.KAPPA_WARN_THRESHOLD:
            parts.append(
                f"Weighted kappa {kappa:.3f} is below the acceptable threshold "
                f"({self.KAPPA_WARN_THRESHOLD}). Categorical agreement on binned "
                "rubric levels is weak; consider revising anchor descriptions."
            )
        return " | ".join(parts)

    # ------------------------------------------------------------------
    # Static metric
    # ------------------------------------------------------------------

    @staticmethod
    def pearson_correlation(x: list[float], y: list[float]) -> float:
        """Compute Pearson r between two lists of floats.

        Returns 0.0 if:
        - Either list has fewer than 2 elements.
        - Either list has zero variance (constant values).

        Args:
            x: First series of continuous scores.
            y: Second series of continuous scores.

        Returns:
            Pearson r in range [-1, 1].

        Raises:
            ValueError: If x and y have different lengths.
        """
        if len(x) != len(y):
            raise ValueError(
                f"x and y must have the same length; got {len(x)} and {len(y)}"
            )
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)

        denom = math.sqrt(var_x * var_y)
        if denom < 1e-12:
            # Zero variance in one or both series — correlation undefined.
            return 0.0

        r = cov / denom
        # Clamp to [-1, 1] to guard against floating-point overshoot.
        return max(-1.0, min(1.0, r))


# ----------------------------------------------------------------------
# Module-level metric functions (v1.1)
# ----------------------------------------------------------------------


def _average_ranks(values: list[float]) -> list[float]:
    """Return average ranks for a list of floats (ties -> mean rank).

    Ranks are 1-indexed. For ties, each tied element gets the mean of the
    ranks they collectively cover.
    """
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        # Grow j while tied.
        while j + 1 < n and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        # Ranks i..j are tied; assign average rank (1-indexed).
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation coefficient.

    Equivalent to Pearson's r applied to the ranks of ``xs`` and ``ys``.
    Ties receive their average rank. Stdlib-only implementation; no scipy.

    Args:
        xs: First series of floats.
        ys: Second series of floats.

    Returns:
        Spearman ρ in [-1, 1]. Returns 0.0 if either series has zero variance
        (or length < 2), matching the Pearson behaviour.

    Raises:
        ValueError: If xs and ys have different lengths.
    """
    if len(xs) != len(ys):
        raise ValueError(
            f"xs and ys must have the same length; got {len(xs)} and {len(ys)}"
        )
    if len(xs) < 2:
        return 0.0

    rx = _average_ranks(xs)
    ry = _average_ranks(ys)
    return WorkflowJudgeAgreement.pearson_correlation(rx, ry)


def cohens_kappa_weighted(
    xs: list[float],
    ys: list[float],
    n_bins: int = 5,
    max_score: float = 100.0,
) -> float:
    """Linear-weighted Cohen's κ on scores binned into ``n_bins`` rubric levels.

    Binning (for ``n_bins=5``, ``max_score=100``):
        [0, 20)  → 0 (Fail)
        [20, 40) → 1 (Poor)
        [40, 60) → 2 (Acceptable)
        [60, 80) → 3 (Good)
        [80, 100] → 4 (Excellent)

    Linear weights: ``w_ij = 1 - |i - j| / (n_bins - 1)``. Weighted κ is:

        κ = 1 - (Σ w_dis_ij · O_ij) / (Σ w_dis_ij · E_ij)

    where ``w_dis_ij = |i - j| / (n_bins - 1)`` (the disagreement weight),
    ``O_ij`` is the observed joint frequency, and ``E_ij`` is the product
    of the marginal frequencies.

    Edge cases:
    - Length mismatch → ValueError.
    - Both inputs zero-variance and identical (all scores in same bin) → 1.0.
    - One input zero-variance and the other not → NaN (expected disagreement
      is zero; κ undefined).
    - n < 2 → NaN.

    Args:
        xs: First series of scores in [0, max_score].
        ys: Second series of scores in [0, max_score].
        n_bins: Number of rubric bins (default 5).
        max_score: Upper bound of score range (default 100).

    Returns:
        Weighted κ in [-1, 1], or float('nan') if undefined.

    Raises:
        ValueError: If xs and ys have different lengths, or n_bins < 2.
    """
    if len(xs) != len(ys):
        raise ValueError(
            f"xs and ys must have the same length; got {len(xs)} and {len(ys)}"
        )
    if n_bins < 2:
        raise ValueError(f"n_bins must be >= 2; got {n_bins}")
    n = len(xs)
    if n < 2:
        return float("nan")

    def _bin(score: float) -> int:
        # Clamp to [0, max_score], then map to [0, n_bins - 1].
        clamped = max(0.0, min(max_score, score))
        # For scores exactly at max_score the raw index would equal n_bins;
        # subtract one so the top bin stays inclusive.
        idx = int(clamped / (max_score / n_bins))
        return min(idx, n_bins - 1)

    bx = [_bin(v) for v in xs]
    by = [_bin(v) for v in ys]

    # Zero-variance short-circuit: if both raters land in the same single bin
    # for all items, agreement is perfect. If at least one rater is constant
    # but they disagree, κ is undefined (no variance in one marginal means
    # expected-disagreement and chance correction break down).
    x_constant = len(set(bx)) == 1
    y_constant = len(set(by)) == 1
    if x_constant and y_constant:
        return 1.0 if bx[0] == by[0] else float("nan")
    if x_constant or y_constant:
        return float("nan")

    # Observed joint distribution (counts).
    observed = [[0 for _ in range(n_bins)] for _ in range(n_bins)]
    row_marg = [0] * n_bins
    col_marg = [0] * n_bins
    for i, j in zip(bx, by):
        observed[i][j] += 1
        row_marg[i] += 1
        col_marg[j] += 1

    denom = n_bins - 1
    # Weighted observed disagreement and expected disagreement (both normalised by n).
    obs_dis = 0.0
    exp_dis = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            w_dis = abs(i - j) / denom
            obs_dis += w_dis * observed[i][j]
            exp_dis += w_dis * (row_marg[i] * col_marg[j] / n)
    # Normalise by n so we have per-item weighted disagreement.
    obs_dis /= n
    exp_dis /= n

    if exp_dis < 1e-12:
        # Expected disagreement is effectively zero; κ undefined.
        return float("nan")

    return 1.0 - (obs_dis / exp_dis)


def compute_full_agreement(xs: list[float], ys: list[float]) -> dict:
    """Compute Pearson r, Spearman ρ, and weighted Cohen's κ in one pass.

    Args:
        xs: First series of scores (0-100).
        ys: Second series of scores (0-100).

    Returns:
        Dict with keys:
            - ``pearson``        — Pearson r (float)
            - ``spearman``       — Spearman ρ (float)
            - ``kappa_weighted`` — linear-weighted κ on 5 rubric bins (float; may be NaN)
            - ``n``              — number of paired observations (int)

    Raises:
        ValueError: If xs and ys have different lengths.
    """
    if len(xs) != len(ys):
        raise ValueError(
            f"xs and ys must have the same length; got {len(xs)} and {len(ys)}"
        )
    return {
        "pearson": WorkflowJudgeAgreement.pearson_correlation(xs, ys),
        "spearman": spearman_rho(xs, ys),
        "kappa_weighted": cohens_kappa_weighted(xs, ys),
        "n": len(xs),
    }
