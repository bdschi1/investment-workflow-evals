# Judge Agreement v1 — Phase 1 Methodology Addendum

**Status:** scaffold. Numbers are intentionally blank until the Phase 1
benchmark run completes.

**Purpose:** quantify how closely two judge models (Opus and Sonnet)
agree on the same 20-item held-out sample, so readers can assess whether
the rubrics produce calibrated numerical evidence rather than noise. A
Spearman correlation below ~0.5 is the Phase-1 abandon-signal per the
upgrade plan — if the judges do not agree with each other, the rubrics
themselves need tightening before publishing any leaderboard number.

## Methodology

- **Sample.** 20 scenario-response pairs held out from the training
  distribution used to calibrate rubric anchors. Held-out list is
  recorded in `results/judge_agreement_v1_sample.csv` (to be created
  alongside the first run).
- **Judges.** Two SKUs running the same system prompt:
  - `claude-opus-4-7` (primary)
  - `claude-sonnet-4-5` (secondary, cross-model)
- **Metric 1 — Spearman rank correlation** over the 20 overall scores.
- **Metric 2 — Exact-match pass/fail agreement** (both judges land on
  the same side of the rubric `pass_threshold`).
- **Metric 3 — Cohen's kappa** on discretized 5-bucket score (fail,
  poor, acceptable, good, excellent) for a more-robust agreement read.

## Results — Overall

| Metric | Opus vs Sonnet | Notes |
|---|---|---|
| Spearman rank ρ | TBD | Abandon-signal threshold: < 0.5 |
| Exact pass/fail match | TBD / 20 | — |
| Cohen's κ (5-bucket) | TBD | < 0.4 = poor agreement; 0.4-0.6 = moderate; > 0.6 = substantial |

## Results — Per-Module

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

## Dimension-Level Agreement

Useful for diagnosing which rubric dimensions are least calibrated.
Report Pearson correlation on dimension-level scores (0-100) between
the two judges, aggregated across all 20 samples.

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

- This uses two Claude-family judges. Cross-family agreement (e.g.
  Claude vs GPT-5) is a stronger test and is tracked for Phase 2.
- A 20-item sample yields wide confidence intervals on per-module
  metrics; treat the overall row as the primary read.
- Self-review bias: Opus may be slightly more lenient scoring Opus
  outputs than Sonnet outputs. A 2x2 design (Opus judges Opus +
  Sonnet; Sonnet judges Opus + Sonnet) is planned for Phase 2.

## How to Populate

Run the judge-agreement harness:

```bash
python -m tools.judge_agreement \
  --sample results/judge_agreement_v1_sample.csv \
  --judge-a claude-opus-4-7 \
  --judge-b claude-sonnet-4-5 \
  --out results/judge_agreement_v1.json
```

Then fill the `TBD` cells in this file from the JSON output. Do not
overwrite without bumping the version suffix (`v2`, `v3`, …) so prior
runs remain auditable.
