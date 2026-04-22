# Frontier Benchmark v1 — Schema

`frontier_benchmark_v1.csv` is the append-only output target for the
Phase 1 leaderboard run.

## Columns

| Column | Type | Description |
|---|---|---|
| `module` | string | Module id, e.g. `01_equity_thesis`, `09_ma_analysis`. |
| `scenario_id` | string | Scenario stem (filename without `.yaml`). |
| `model` | string | SKU string passed to the provider (e.g. `claude-opus-4-7`, `claude-sonnet-4-5`, `gpt-5`, `gemini-2.5-pro`). |
| `score` | float | Overall rubric score on 0-100. |
| `critical_failure_triggered` | bool | `true` if any rubric `critical_failures` condition fired. |
| `judge_model` | string | SKU used to grade (separate from the generator `model`). |
| `judge_cache_hit_rate` | float | Prompt-cache hit rate reported by the judge (0.0-1.0); blank if not tracked by the provider. |
| `run_date` | ISO-8601 string | UTC timestamp of the run. |

## Conventions

- One row per (module, scenario_id, model, run_index). Multiple runs per
  model per scenario are appended, not overwritten; downstream summary
  scripts aggregate with mean/median and report variance.
- The schema is intentionally flat so `pandas.read_csv` works with no
  type coercion. Booleans written as `true` / `false` lowercase.
- Rows MUST preserve column order above for deterministic diffs.

## Provenance

The benchmark runner lives in `tools/eval_runner.py`. The leaderboard
invocation is documented in `BENCHMARK_RUN.md` at the repo root.
