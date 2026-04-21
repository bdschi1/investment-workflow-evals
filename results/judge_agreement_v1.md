# Judge Agreement v1 — Phase 1 Methodology Addendum

**Status:** scaffold with a simulated self-consistency floor populated
from the heuristic grader. Real frontier-model cross-judge numbers
remain TBD (require a live benchmark run; see the section below).

**Purpose:** quantify how closely two judges agree on the same held-out
sample, so readers can assess whether the rubrics produce calibrated
numerical evidence rather than noise. A Spearman correlation below
~0.5 is the Phase-1 abandon-signal per the upgrade plan — if the judges
do not agree with each other, the rubrics themselves probably need
tightening before publishing any leaderboard number.

## Metrics in This Report

Three complementary views of judge agreement are reported. Each answers
a different question, and none subsumes the others:

- **Pearson r** — linear correlation between continuous scores.
  Sensitive to scale and outliers. Best when both judges' scores are
  assumed to lie on the same linear scale and a small systematic shift
  is meaningful (e.g. one judge is 5 points more lenient on every item).
- **Spearman ρ** — rank correlation (Pearson r applied to ranks).
  Monotone-invariant: robust to non-linear but order-preserving
  differences in the two judges' scoring functions. Best when you care
  that the two judges order the memos the same way, regardless of
  scale. Phase-1 abandon-signal: ρ < 0.5.
- **Weighted Cohen's κ (linear, 5-bin)** — categorical agreement on
  scores binned into the five rubric levels (Fail 0–20, Poor 20–40,
  Acceptable 40–60, Good 60–80, Excellent 80–100), corrected for
  agreement expected by chance under each judge's marginal
  distribution. Best when you care that the two judges land in the
  same rubric bucket (pass/fail gates, bucket-level leaderboards).
  Soft bands: κ < 0.4 poor, 0.4–0.6 moderate, > 0.6 substantial.

Prefer r when comparing model deltas; prefer ρ when the underlying
scales may differ; prefer κ when reporting pass/fail or bucket-level
agreement.

## Methodology

- **Sample (planned).** 20 scenario-response pairs held out from the
  training distribution used to calibrate rubric anchors. Held-out
  list to be recorded in `results/judge_agreement_v1_sample.csv`
  alongside the first live run.
- **Judges (planned).** Two SKUs running the same system prompt:
  - `claude-opus-4-7` (primary)
  - `claude-sonnet-4-5` (secondary, cross-model)
- **Metrics.** Pearson r, Spearman ρ, weighted Cohen's κ — see above.

## Simulated Self-Consistency Floor

The tables in this section use the heuristic `GradingEngine` as a
stand-in for Judge A, and a Gaussian-noise-perturbed copy (same grader,
seed=42) as Judge B. They are a sanity floor showing the metric
pipeline is wired end-to-end; they are **not** inter-judge agreement
between two different models. Real cross-judge numbers require the
live run described at the bottom of this file.

<!-- BEGIN self-consistency floor (auto-generated) -->

### Simulated Self-Consistency Floor (seed=42) — NOT real inter-judge agreement

Judge A is the heuristic `GradingEngine` run against 33 golden-answer markdown files. Judge B is the same grader's output with additive Gaussian noise (σ = 4.0 points, `random.Random(42)`, clamped to [0, 100]). This is a sanity floor that confirms the metric pipeline is wired end-to-end. It is **not** a real cross-model comparison — see the frontier-model section below for that.

**Overall pooled pairs across all dimensions and modules:**

| Metric | Value | Notes |
|---|---|---|
| Pearson r            | 0.952 | Linear correlation on pooled dimension scores. |
| Spearman ρ           | 0.778 | Rank correlation; robust to monotone transforms. |
| Cohen's κ (weighted) | 0.939 | Linear-weighted κ on 5 rubric bins (Fail/Poor/Acceptable/Good/Excellent). |
| n (pooled pairs)     | 156 | 33 goldens × dimensions per rubric. |

**Per-module breakdown (pooled dimension scores within each module):**

| Module | n pairs | Pearson r | Spearman ρ | Weighted κ |
|---|---:|---|---|---|
| `01_equity_thesis` | 15 | 0.919 | 0.902 | n/a |
| `02_dcf_valuation` | 6 | 0.993 | 0.986 | 1.000 |
| `03_portfolio_construction` | 15 | 0.972 | 0.956 | 1.000 |
| `04_assumption_validation` | 15 | 0.000 | 0.000 | 1.000 |
| `05_risk_attribution` | 6 | 0.925 | 0.812 | 0.786 |
| `07_report_review` | 42 | 0.867 | 0.468 | 1.000 |
| `09_ma_analysis` | 15 | 0.935 | 0.694 | 1.000 |
| `10_valuation_synthesis` | 12 | 0.929 | 0.575 | 1.000 |
| `11_lbo_analysis` | 15 | 0.000 | 0.000 | 1.000 |
| `12_deal_execution` | 15 | 0.897 | 0.688 | 0.464 |

### Heuristic Grader vs Perturbed Heuristic — per-golden overall scores

For each of the 33 goldens, we compute a weighted overall score (unweighted mean across rubric dimensions for simplicity) for both Judge A and Judge B, then compute metrics across goldens. This tests agreement at the _memo_ granularity rather than the _dimension_ granularity.

| Metric | Value |
|---|---|
| Pearson r            | 0.986 |
| Spearman ρ           | 0.929 |
| Cohen's κ (weighted) | 0.796 |
| n (goldens)          | 33 |


<!-- END self-consistency floor (auto-generated) -->

## Real Frontier-Model Cross-Judge Results — TBD

These tables are the load-bearing leaderboard results and remain empty
until a live benchmark run is executed. Populating them requires paid
API calls and is out of scope for the offline self-consistency step
above.

> **To populate:** run `python -m tools.benchmark_runner --yes-live`
> with valid API credentials for both judge models. Estimated cost
> is governed by the sample size × model pricing; see
> `docs/BENCHMARK_RUN.md` for the current estimate. Run separately
> from the offline pipeline.

### Results — Overall

| Metric | Opus vs Sonnet | Notes |
|---|---|---|
| Spearman rank ρ      | TBD | Abandon-signal threshold: < 0.5. |
| Exact pass/fail match | TBD / 20 | — |
| Cohen's κ (5-bucket) | TBD | < 0.4 = poor; 0.4–0.6 = moderate; > 0.6 = substantial. |

### Results — Per-Module

Per-module breakdown, same three metrics. Modules with fewer than 3
scenarios in the 20-item sample are reported but flagged as
small-sample.

| Module | n | Spearman ρ | Pass/fail match | Cohen's κ | Flag |
|---|---:|---|---|---|---|
| `00_qualification` | TBD | TBD | TBD | TBD | |
| `01_equity_thesis` | TBD | TBD | TBD | TBD | |
| `02_dcf_valuation` | TBD | TBD | TBD | TBD | |
| `03_portfolio_construction` | TBD | TBD | TBD | TBD | |
| `04_assumption_validation` | TBD | TBD | TBD | TBD | |
| `05_risk_attribution` | TBD | TBD | TBD | TBD | |
| `06_research_translation` | TBD | TBD | TBD | TBD | may be n<3 |
| `07_report_review` | TBD | TBD | TBD | TBD | |
| `08_comparable_analysis` | TBD | TBD | TBD | TBD | may be n<3 |
| `09_ma_analysis` | TBD | TBD | TBD | TBD | may be n<3 |
| `10_valuation_synthesis` | TBD | TBD | TBD | TBD | may be n<3 |
| `11_lbo_analysis` | TBD | TBD | TBD | TBD | may be n<3 |
| `12_deal_execution` | TBD | TBD | TBD | TBD | may be n<3 |

### Dimension-Level Agreement — TBD

Useful for diagnosing which rubric dimensions are least calibrated.
Report Pearson r on dimension-level scores (0-100) between the two
judges, aggregated across all 20 samples.

| Dimension | Pearson r | 95% CI | Interpretation |
|---|---|---|---|
| factual_accuracy | TBD | TBD | |
| analytical_rigor | TBD | TBD | |
| risk_assessment | TBD | TBD | |
| evidence_quality | TBD | TBD | |
| completeness | TBD | TBD | |

Dimensions with Pearson r below ~0.5 are candidates for rubric-anchor
tightening in the Phase 2 recalibration step.

## Known Limitations

- The "Real Frontier-Model" section above is currently TBD. The
  self-consistency block is a pipeline sanity check, not inter-model
  agreement.
- When the live run happens, two Claude-family judges will be the
  first pairing. Cross-family agreement (e.g. Claude vs GPT-5) is a
  stronger test and is tracked for Phase 2.
- A 20-item sample yields wide confidence intervals on per-module
  metrics; treat the overall row as the primary read.
- Self-review bias: Opus may be slightly more lenient scoring Opus
  outputs than Sonnet outputs. A 2x2 design (Opus judges Opus +
  Sonnet; Sonnet judges Opus + Sonnet) is planned for Phase 2.
- The self-consistency floor is trivially high by construction (same
  grader both sides); it lower-bounds the plumbing, not the ceiling.

## How to Populate

### Offline sanity floor (no API calls)

```bash
python scripts/populate_judge_agreement.py
```

Overwrites the auto-generated block between the HTML comment markers
above. Safe to re-run. Uses `random.Random(42)` so numbers are
reproducible.

### Live frontier-model run (paid API)

```bash
python -m tools.benchmark_runner \
  --sample results/judge_agreement_v1_sample.csv \
  --judge-a claude-opus-4-7 \
  --judge-b claude-sonnet-4-5 \
  --out results/judge_agreement_v1.json \
  --yes-live
```

Then fill the TBD cells in the "Real Frontier-Model" section from the
JSON output. Do not overwrite without bumping the version suffix
(`v2`, `v3`, …) so prior runs remain auditable.
