"""Inter-annotator agreement (IAA) metrics for rubric grading.

Pure-stdlib implementations of:
- Weighted Cohen's kappa (linear weights) for ordinal rubric scores
- Krippendorff's alpha (interval level) for continuous scores across >=2 raters
- Pairwise Pearson correlation

Standard references:
- Cohen, J. (1968). "Weighted kappa: Nominal scale agreement provision for
  scaled disagreement or partial credit." Psychological Bulletin.
- Krippendorff, K. (2011). "Computing Krippendorff's Alpha-Reliability."
  University of Pennsylvania.
- Landis, J.R. & Koch, G.G. (1977). "The measurement of observer agreement
  for categorical data." Biometrics 33(1): 159-174.

All formulas derived from first principles — no dependency on numpy/scipy.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from typing import Union

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class IAAResult:
    """Single inter-annotator agreement measurement.

    Attributes:
        method: Which metric was computed.
        dimension: Rubric dimension id, or "overall".
        raters: Tuple of two rater ids (for pairwise) or list (alpha over >=2).
        agreement: Agreement score. Typically [-1, 1] for kappa/Pearson,
            [0, 1] for alpha. May be NaN if insufficient data.
        n_items: Number of items compared (after filtering missing).
        interpretation: Human-readable Landis-Koch (or similar) band.
    """

    method: str
    dimension: str
    raters: Union[tuple, list]
    agreement: float
    n_items: int
    interpretation: str = ""


# ---------------------------------------------------------------------------
# Interpretation (Landis & Koch 1977)
# ---------------------------------------------------------------------------


def interpret_kappa(k: float) -> str:
    """Landis-Koch interpretation bands for kappa-family statistics.

    Bands (Landis & Koch 1977, Biometrics 33:159-174):
        < 0.00       poor
        0.00 - 0.20  slight
        0.21 - 0.40  fair
        0.41 - 0.60  moderate
        0.61 - 0.80  substantial
        0.81 - 1.00  near-perfect
    """
    if math.isnan(k):
        return "undefined (insufficient or degenerate data)"
    if k < 0.0:
        band = "poor"
    elif k <= 0.20:
        band = "slight"
    elif k <= 0.40:
        band = "fair"
    elif k <= 0.60:
        band = "moderate"
    elif k <= 0.80:
        band = "substantial"
    else:
        band = "near-perfect"
    return f"{band} agreement (k={k:.2f})"


# ---------------------------------------------------------------------------
# Binning helpers
# ---------------------------------------------------------------------------


def _bin_score(
    score: float, n_bins: int = 5, lo: float = 0.0, hi: float = 100.0
) -> int:
    """Bin a continuous score into an integer level in [0, n_bins-1].

    Default mapping for a 0-100 rubric into 5 bands (Excellent/Good/Acceptable/
    Poor/Fail) splits at 20/40/60/80. Values outside [lo, hi] are clipped.
    """
    if n_bins < 2:
        raise ValueError("n_bins must be >= 2")
    if score <= lo:
        return 0
    if score >= hi:
        return n_bins - 1
    width = (hi - lo) / n_bins
    idx = int((score - lo) / width)
    if idx >= n_bins:
        idx = n_bins - 1
    return idx


# ---------------------------------------------------------------------------
# Weighted Cohen's kappa
# ---------------------------------------------------------------------------


def cohen_kappa_weighted(
    scores_a: list,
    scores_b: list,
    n_bins: int = 5,
    lo: float = 0.0,
    hi: float = 100.0,
) -> float:
    """Weighted Cohen's kappa (linear weights) for continuous ordinal scores.

    Bins each score into n_bins ordinal levels then computes:

        kappa_w = 1 - (sum w_ij * O_ij) / (sum w_ij * E_ij)

    where w_ij = |i - j| / (n_bins - 1) are linear disagreement weights,
    O_ij is the observed joint frequency, and E_ij is the chance-expected
    joint frequency under marginal independence.

    Returns:
        kappa in [-1, 1]. Returns 1.0 if all observations agree exactly.
        Returns NaN if n<3 or if expected disagreement is zero (degenerate).
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("scores_a and scores_b must have the same length")
    n = len(scores_a)
    if n < 3:
        return float("nan")

    # Bin both rater arrays.
    a = [_bin_score(s, n_bins, lo, hi) for s in scores_a]
    b = [_bin_score(s, n_bins, lo, hi) for s in scores_b]

    # Exact agreement on all -> kappa = 1 by convention.
    if a == b:
        return 1.0

    # Build confusion matrix (n_bins x n_bins).
    conf = [[0 for _ in range(n_bins)] for _ in range(n_bins)]
    for ai, bi in zip(a, b):
        conf[ai][bi] += 1

    # Marginals.
    row = [sum(conf[i]) for i in range(n_bins)]
    col = [sum(conf[i][j] for i in range(n_bins)) for j in range(n_bins)]

    # Linear weights: w_ij = |i - j| / (n_bins - 1).
    denom_k = n_bins - 1
    total = float(n)

    num = 0.0  # sum_{i,j} w_ij * O_ij
    den = 0.0  # sum_{i,j} w_ij * E_ij
    for i in range(n_bins):
        for j in range(n_bins):
            w = abs(i - j) / denom_k
            o = conf[i][j] / total
            e = (row[i] / total) * (col[j] / total)
            num += w * o
            den += w * e

    if den == 0.0:
        # No expected disagreement. If also no observed disagreement, perfect.
        return 1.0 if num == 0.0 else float("nan")

    return 1.0 - (num / den)


# ---------------------------------------------------------------------------
# Krippendorff's alpha (interval level)
# ---------------------------------------------------------------------------


def krippendorff_alpha(
    ratings: dict,
    level: str = "interval",
) -> float:
    """Krippendorff's alpha for reliability across >=2 raters.

    Args:
        ratings: {item_id: {rater_id: score}}. Missing cells are allowed;
            they are simply excluded from pair counts for that item.
        level: "interval" (squared differences) or "nominal" (0/1).

    Returns:
        alpha in roughly [-inf, 1]; practically [0, 1] for usable data.
        NaN if fewer than 2 items have >=2 raters, or if expected
        disagreement is zero (all-identical inputs -> returns 1.0 if
        observed disagreement is also zero).

    Formula (Krippendorff 2011):
        alpha = 1 - D_o / D_e

    with D_o = observed disagreement averaged over all coincident pairs,
    and D_e = expected disagreement under random pairing of all values.

    For interval level the distance function is delta^2 = (v1 - v2)^2.
    """
    if level not in ("interval", "nominal"):
        raise ValueError("level must be 'interval' or 'nominal'")

    # Filter items with at least 2 raters (coincidences require pairs).
    usable = {item: r for item, r in ratings.items() if len(r) >= 2}
    if len(usable) < 2:
        return float("nan")

    # Observed disagreement: average over item-internal pairs.
    #   D_o = (1 / sum_u m_u*(m_u-1)) * sum_u sum_{pairs in item u} delta^2
    # where m_u is number of raters on item u.
    # Equivalent: build coincidence matrix weighted by 1/(m_u - 1).
    #
    # Simpler: accumulate numerator / denominator directly.
    num_o = 0.0
    den_o = 0.0
    all_values = []
    for item, r in usable.items():
        vals = list(r.values())
        m = len(vals)
        # Every unordered pair contributes; normalization for item u is 1/(m-1).
        if m < 2:
            continue
        inv = 1.0 / (m - 1)
        for v1, v2 in combinations(vals, 2):
            d = _alpha_distance(v1, v2, level)
            # Each unordered pair counted once; weight accordingly.
            # Coincidence matrix form counts ordered pairs (2x). Scale cancels.
            num_o += 2.0 * inv * d
            den_o += 2.0 * inv
        all_values.extend(vals)

    if den_o == 0.0:
        return float("nan")

    D_o = num_o / den_o

    # Expected disagreement: average delta^2 over all distinct value pairs
    # pooled across items.
    N = len(all_values)
    if N < 2:
        return float("nan")
    num_e = 0.0
    # Pairwise sum over all pooled values.
    # Efficient form: sum_{i<j} delta(v_i, v_j) * 2 / (N*(N-1)).
    total_pairs = N * (N - 1)
    if total_pairs == 0:
        return float("nan")
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            num_e += _alpha_distance(all_values[i], all_values[j], level)
    D_e = num_e / total_pairs

    if D_e == 0.0:
        return 1.0 if D_o == 0.0 else float("nan")

    return 1.0 - (D_o / D_e)


def _alpha_distance(v1: float, v2: float, level: str) -> float:
    if level == "interval":
        d = float(v1) - float(v2)
        return d * d
    # nominal
    return 0.0 if v1 == v2 else 1.0


# ---------------------------------------------------------------------------
# Pairwise Pearson
# ---------------------------------------------------------------------------


def pairwise_pearson(scores_a: list, scores_b: list) -> float:
    """Pearson correlation coefficient.

    Returns NaN for n<2 or zero variance in either input.
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("scores_a and scores_b must have the same length")
    n = len(scores_a)
    if n < 2:
        return float("nan")
    mean_a = sum(scores_a) / n
    mean_b = sum(scores_b) / n
    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(scores_a, scores_b))
    var_a = sum((a - mean_a) ** 2 for a in scores_a)
    var_b = sum((b - mean_b) ** 2 for b in scores_b)
    if var_a == 0.0 or var_b == 0.0:
        return float("nan")
    return cov / math.sqrt(var_a * var_b)


# ---------------------------------------------------------------------------
# Report orchestration
# ---------------------------------------------------------------------------


def compute_iaa_report(
    records: list,
    dimensions: list | None = None,
) -> list:
    """Compute IAA across all rater pairs (and group-level alpha if >=3 raters).

    Args:
        records: list of dicts of shape
            {"item_id": str, "annotator_id": str, "dimension_scores": {dim: score, ...}}
        dimensions: optional allow-list of dimensions to compute. If None,
            uses the union of dimensions seen in records.

    Returns:
        List of IAAResult objects. One weighted-kappa result per
        (dimension, rater-pair) plus one Krippendorff alpha per dimension
        when there are >=3 raters.
    """
    if not records:
        return []

    # Pivot: per-dimension -> item -> rater -> score.
    by_dim: dict = defaultdict(lambda: defaultdict(dict))
    rater_set = set()
    dim_set = set()
    for rec in records:
        item = rec.get("item_id")
        rater = rec.get("annotator_id")
        dscores = rec.get("dimension_scores") or {}
        if item is None or rater is None:
            continue
        rater_set.add(rater)
        for dim, score in dscores.items():
            dim_set.add(dim)
            by_dim[dim][item][rater] = float(score)

    if dimensions is not None:
        dim_list = [d for d in dimensions if d in dim_set]
    else:
        dim_list = sorted(dim_set)

    raters = sorted(rater_set)
    results: list = []

    for dim in dim_list:
        item_map = by_dim[dim]

        # Pairwise kappa + Pearson for every pair.
        for r1, r2 in combinations(raters, 2):
            paired_a = []
            paired_b = []
            for item, rmap in item_map.items():
                if r1 in rmap and r2 in rmap:
                    paired_a.append(rmap[r1])
                    paired_b.append(rmap[r2])
            n = len(paired_a)
            if n < 3:
                results.append(
                    IAAResult(
                        method="cohen_kappa_weighted",
                        dimension=dim,
                        raters=(r1, r2),
                        agreement=float("nan"),
                        n_items=n,
                        interpretation="insufficient data (n<3)",
                    )
                )
                results.append(
                    IAAResult(
                        method="pairwise_pearson",
                        dimension=dim,
                        raters=(r1, r2),
                        agreement=float("nan"),
                        n_items=n,
                        interpretation="insufficient data (n<3)",
                    )
                )
                continue
            k = cohen_kappa_weighted(paired_a, paired_b)
            r = pairwise_pearson(paired_a, paired_b)
            results.append(
                IAAResult(
                    method="cohen_kappa_weighted",
                    dimension=dim,
                    raters=(r1, r2),
                    agreement=k,
                    n_items=n,
                    interpretation=interpret_kappa(k),
                )
            )
            results.append(
                IAAResult(
                    method="pairwise_pearson",
                    dimension=dim,
                    raters=(r1, r2),
                    agreement=r,
                    n_items=n,
                    interpretation=(
                        "undefined" if math.isnan(r) else f"Pearson r={r:.2f}"
                    ),
                )
            )

        # Krippendorff alpha (interval) when >=3 raters.
        if len(raters) >= 3:
            alpha = krippendorff_alpha(item_map, level="interval")
            results.append(
                IAAResult(
                    method="krippendorff_alpha",
                    dimension=dim,
                    raters=list(raters),
                    agreement=alpha,
                    n_items=sum(1 for v in item_map.values() if len(v) >= 2),
                    interpretation=(
                        "insufficient data (n<2 items with >=2 raters)"
                        if math.isnan(alpha)
                        else f"alpha={alpha:.2f}"
                    ),
                )
            )

    return results


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def format_iaa_markdown(results: list) -> str:
    """Render results as a markdown report grouped by dimension.

    Columns: rater pair, kappa, Pearson r, n_items, interpretation.
    A trailing section lists Krippendorff alpha rows when present.
    """
    if not results:
        return "# Inter-Annotator Agreement Report\n\n_No results to report._\n"

    # Group by dimension.
    by_dim = defaultdict(list)
    for res in results:
        by_dim[res.dimension].append(res)

    lines = ["# Inter-Annotator Agreement Report", ""]

    for dim in sorted(by_dim.keys()):
        lines.append(f"## Dimension: `{dim}`")
        lines.append("")
        lines.append(
            "| Rater Pair | Weighted Cohen's k | Pearson r | n | Interpretation |"
        )
        lines.append("|---|---|---|---|---|")

        # Build pair -> (kappa, pearson, n, interp).
        pair_rows: dict[tuple, dict] = {}
        alpha_rows: list = []
        for res in by_dim[dim]:
            if res.method == "krippendorff_alpha":
                alpha_rows.append(res)
                continue
            if isinstance(res.raters, tuple):
                key = res.raters
            else:
                key = tuple(res.raters)
            row = pair_rows.setdefault(
                key,
                {
                    "kappa": float("nan"),
                    "pearson": float("nan"),
                    "n": res.n_items,
                    "interp": "",
                },
            )
            if res.method == "cohen_kappa_weighted":
                row["kappa"] = res.agreement
                row["interp"] = res.interpretation
            elif res.method == "pairwise_pearson":
                row["pearson"] = res.agreement

        for pair, row in sorted(pair_rows.items()):
            k_str = _fmt(row["kappa"])
            r_str = _fmt(row["pearson"])
            lines.append(
                f"| {pair[0]} vs {pair[1]} | {k_str} | {r_str} | "
                f"{row['n']} | {row['interp']} |"
            )

        if alpha_rows:
            lines.append("")
            lines.append("**Krippendorff's alpha (interval, all raters):**")
            for res in alpha_rows:
                a_str = _fmt(res.agreement)
                lines.append(
                    f"- alpha = {a_str} over n={res.n_items} items "
                    f"({len(res.raters)} raters) — {res.interpretation}"
                )
        lines.append("")

    return "\n".join(lines) + "\n"


def _fmt(x: float) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.3f}"
