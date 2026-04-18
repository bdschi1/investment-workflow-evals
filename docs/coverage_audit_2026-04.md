# Coverage Audit — 2026-04

Snapshot of per-module scenario and golden-answer counts. This document
is the ground truth the Phase 1 balance work plans against — it is NOT
auto-generated and is expected to drift until a coverage-check test is
wired into CI. Refresh manually whenever new scenarios or goldens are
added.

## Summary

The repo currently contains **13 evaluation modules** (`00_qualification`
through `12_deal_execution`). Earlier READMEs cited seven modules; the
discrepancy is tracked in the root `README.md` module count reconciliation
and in `PHASE1_NOTES.md`.

Phase 1 target: **each module at least 3 scenarios and at least 2
golden answers**. Modules missing that bar are flagged below.

## Per-Module Counts

| Module | Scenarios | Golden answers | Rubric files | Status vs Phase-1 target | Notes |
|---|---:|---:|---:|---|---|
| `00_qualification` | 1 | 1 | 1 | below (scenarios, goldens) | Intentionally thin — onboarding sanity check rather than a full module. |
| `01_equity_thesis` | 3 | 3 | 1 | meets target | Covers catalyst, cyclical-trough, AI capex cycle. |
| `02_dcf_valuation` | 2 | 2 | 1 | below (scenarios, goldens) | Needs one more scenario + golden to hit the bar. |
| `03_portfolio_construction` | 27 | 5 | 1 | meets target, over-weighted | 27 scenarios with only 5 goldens leaves most scenarios un-anchored. Prioritize golden-answer backfill over new scenarios. Breakdown of recent scenarios is staged in `scenarios/INDEX.md`. |
| `04_assumption_validation` | 3 | 3 | 1 | meets target | Discount rate, commodity price, statistical significance. |
| `05_risk_attribution` | 2 | 2 | 2 | below (scenarios, goldens) | Two rubric variants (`standard.yaml`, `risk_attribution.yaml`). |
| `06_research_translation` | 0 | 0 | 1 | **empty** | Rubric present; scenarios and goldens to be authored in Phase 1. |
| `07_report_review` | 6 | 6 | 1 | meets target | Recently added; six paired scenarios + goldens. |
| `08_comparable_analysis` | 1 | 0 | 1 | below (scenarios, goldens) | One scenario, no goldens. |
| `09_ma_analysis` | 2 | 0 | 1 | below (scenarios, goldens) | Accretion-dilution + sources-and-uses; no goldens. |
| `10_valuation_synthesis` | 3 | 0 | 1 | below (goldens) | DCF sensitivity, football field, SOTP. |
| `11_lbo_analysis` | 1 | 0 | 1 | below (scenarios, goldens) | Mid-market LBO returns only. |
| `12_deal_execution` | 2 | 0 | 1 | below (scenarios, goldens) | Bid comparison + diligence request list. |
| **Totals** | **53** | **27** | **15** | | |

Last-modified timestamps are intentionally omitted from this table; the
filesystem mtimes were reset when unversioned work was first committed
to a feature branch on 2026-04-18, so `git log --format=%ad -1 -- <path>`
is the authoritative source for when any single file last changed.

## Phase-1 Work Implied

- **High priority — author goldens:** modules 08, 09, 10, 11, 12 each
  need at least two golden answers to be benchmark-able.
- **High priority — author scenarios:** module 06 has zero scenarios; it
  is the most conspicuous hole.
- **Medium priority — close to bar:** modules 02, 05, 08, 09, 11 need
  one additional scenario each.
- **Lower priority — already meets bar:** modules 01, 03, 04, 07. Do not
  add to 03 until more goldens are in place.

## Sanity Checks

- Every scenario in every module parses as valid YAML (spot-checked; a
  `test_scenario_yaml_valid` parametric test is tracked as a Phase-2
  hardening item).
- Every rubric file is present for each module.
- Golden-answer filename stems should match scenario stems 1:1. This
  check is on the Phase-2 CI gate list but has not been wired yet.

## Out-of-Scope

Adversarial variants, judge-agreement numbers, and frontier-model
benchmark rows are deliberately not tracked here; they belong in
`results/frontier_benchmark_v1.csv`, `results/judge_agreement_v1.md`,
and the Phase-3 adversarial atlas respectively.
