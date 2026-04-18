"""Judge agreement metrics for investment-workflow-evals.

Compares InvestmentWorkflowJudge (AI) vs GradingEngine (heuristic) on the same
responses. Computes Pearson correlation per dimension and overall.
Warns when correlation < 0.6.

# module_version: 1.0.0
# date: 2026-04-04
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum number of comparison pairs required before computing correlation.
_MIN_PAIRS = 3


@dataclass
class IWEAgreementResult:
    """Pearson correlation agreement between AI judge and heuristic grader."""

    dimension_correlations: dict[str, float]  # dimension -> Pearson r
    overall_correlation: float
    n_compared: int
    low_agreement_dimensions: list[str]       # dimensions with r < 0.6
    warning: str = ""


class WorkflowJudgeAgreement:
    """Computes Pearson correlation between AI judge and heuristic grader scores.

    IWE grading produces continuous 0-100 scores per dimension. Pearson r
    measures linear association between the two score series. Values >= 0.6
    indicate acceptable alignment; values below trigger a prompt revision
    warning.

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
        print(result.overall_correlation)

    Usage — batch::

        result = agreement.batch_compare([
            {"ai_scores": {...}, "heuristic_scores": {...}},
            ...
        ])
    """

    CORRELATION_WARN_THRESHOLD = 0.6

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
            )

        all_ai = [ai_scores[d] for d in shared_dims]
        all_heuristic = [heuristic_scores[d] for d in shared_dims]
        overall_r = self.pearson_correlation(all_ai, all_heuristic)

        # Per-dimension correlation requires multiple items — report NaN for single-item dims.
        # With a single comparison we only have the cross-dim correlation.
        dim_corr: dict[str, float] = {}

        low_dims = []
        warning = ""
        if overall_r < self.CORRELATION_WARN_THRESHOLD:
            warning = (
                f"Overall correlation {overall_r:.3f} is below the acceptable "
                f"threshold ({self.CORRELATION_WARN_THRESHOLD}). Review the judge prompt "
                "or few-shot examples to improve AI/heuristic score alignment."
            )
            logger.warning(warning)

        return IWEAgreementResult(
            dimension_correlations=dim_corr,
            overall_correlation=overall_r,
            n_compared=len(shared_dims),
            low_agreement_dimensions=low_dims,
            warning=warning,
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
            IWEAgreementResult aggregated across all items.
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
            )

        overall_r = self.pearson_correlation(all_ai, all_heuristic)

        dim_corr: dict[str, float] = {}
        for dim in dim_ai:
            if len(dim_ai[dim]) >= _MIN_PAIRS:
                dim_corr[dim] = self.pearson_correlation(dim_ai[dim], dim_heuristic[dim])

        low_dims = [d for d, r in dim_corr.items() if r < self.CORRELATION_WARN_THRESHOLD]
        warning = ""
        if overall_r < self.CORRELATION_WARN_THRESHOLD:
            warning = (
                f"Overall correlation {overall_r:.3f} is below the acceptable "
                f"threshold ({self.CORRELATION_WARN_THRESHOLD}). Review the judge prompt "
                "or few-shot examples to improve AI/heuristic score alignment."
            )
            logger.warning(warning)

        return IWEAgreementResult(
            dimension_correlations=dim_corr,
            overall_correlation=overall_r,
            n_compared=n_total,
            low_agreement_dimensions=low_dims,
            warning=warning,
        )

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
