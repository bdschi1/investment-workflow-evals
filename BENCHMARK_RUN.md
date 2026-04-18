# BENCHMARK_RUN.md — Frontier-Model Benchmark

This document describes how to run the full frontier-model benchmark
described in Phase 1 of the upgrade plan. The runner is
`tools/benchmark_runner.py`. Rows are appended to
`results/frontier_benchmark_v1.csv` using the schema documented in
`results/frontier_benchmark_v1.README.md`.

## Modes

1. **Dry run** — scores each scenario's golden answer through the
   rubric engine (no API calls). Wiring / schema validation only.
2. **Haiku validation** — generates candidates with a cheap SKU
   (e.g. `claude-haiku-4-5-20251001`) and judges with the default
   judge model (`claude-opus-4-6`). Use for small-sample validation
   before spending frontier-model budget.
3. **Live frontier** — generates candidates across the frontier SKUs
   specified by `--models`. Requires `--yes-live` as a guard rail.

The live-frontier path is intentionally not wired to call the provider
SDKs in this session; invoking `--generator live` raises
`NotImplementedError` with a pointer back to this file. That is a
safety rail against accidental frontier-model spend. To enable it,
implement `_live_candidate()` in `tools/benchmark_runner.py` (the stub
is one function; wire each provider SDK path there).

## Commands

### Dry run (no API calls, no cost)

```bash
python -m tools.benchmark_runner \
    --modules all \
    --models claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro \
    --dry-run
```

This scores every golden answer in every module under each declared
SKU label. Output rows are seeded with
`judge_model = "rubric-engine-dry-run"` so the live run can be
distinguished from the wiring seed.

### Haiku validation (cheap, ~$0.10-0.30)

```bash
python -m tools.benchmark_runner \
    --modules 06_research_translation \
    --models claude-haiku-4-5-20251001 \
    --generator haiku \
    --scenarios 3
```

Run on 2-3 scenarios in one module to confirm the generate-and-judge
path works end-to-end.

### Full frontier benchmark (expensive, ~$150-250)

```bash
python -m tools.benchmark_runner \
    --modules all \
    --models claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro \
    --generator live \
    --yes-live
```

Expected wall-clock: roughly 8-15 hours of API time depending on
concurrency, scenario count, and per-scenario retries. Run off-peak
if possible; prompt caching engages automatically when the judge
system prompt is reused across scenarios.

## Estimated cost per SKU (full benchmark, ~45 scenarios, 1 run each)

Costs are rough order-of-magnitude estimates using publicly quoted
pricing as of 2026-04; actual cost varies with output length, prompt
caching hit rate, and retry behavior. Treat these as ceilings, not
targets.

| Model | Input $ / 1M tok | Output $ / 1M tok | Est. cost (gen + judge) |
|---|---:|---:|---:|
| `claude-opus-4-7` | 15 | 75 | $60-90 |
| `claude-sonnet-4-5` | 3 | 15 | $15-25 |
| `gpt-5` | 12-15 | 60-75 | $50-80 |
| `gemini-2.5-pro` | 7-10 | 21-30 | $25-45 |
| `claude-opus-4-6` (judge) | 15 | 75 | (already included above) |
| **Total** | | | **~$150-250** |

Assumptions:
- ~45 scenarios, 4 candidate models, 1 run per (scenario, model) pair.
- Average candidate output length ~2,500 tokens.
- Average scenario/rubric context ~4,000 input tokens (cached after
  first call per scenario).
- Judge output (tool call) ~500 tokens.

To reduce cost, lower the number of runs per scenario (default 1),
cut `--models`, or cap `--scenarios` per module. If budget crosses
$350 per the plan's sanity check, drop from 4 runs to 2 per scenario
and/or drop the lowest-priority module.

## Judge-agreement addendum

After the first populated run, rerun the agreement tool on a 20-item
held-out sample with a second judge SKU (cross-model). Report
Spearman and exact-match rate:

```bash
python -m tools.judge_agreement \
    --sample-size 20 \
    --primary-judge claude-opus-4-6 \
    --cross-judge claude-sonnet-4-5 \
    --out results/judge_agreement_v1.md
```

If Spearman across judge pairs falls below ~0.5, stop publishing the
leaderboard; the rubrics are probably under-specified and need anchor
tightening before any external-facing number goes out.

## What ships in this session

Only the dry-run path has been executed. Three seed rows were written
to `results/frontier_benchmark_v1.csv` covering the three Module 06
scenarios against the Haiku SKU label. Live-frontier rows are
deliberately deferred pending explicit budget approval.
