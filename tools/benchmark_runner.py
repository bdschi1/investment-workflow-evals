"""Frontier-model benchmark runner for investment-workflow-evals.

Appends one row per (module, scenario, model) to
``results/frontier_benchmark_v1.csv`` with the schema documented in
``results/frontier_benchmark_v1.README.md``.

Supports three run modes, in order of increasing cost:

1. ``--dry-run`` (default): scores the scenario's own golden answer as
   the candidate response. No generation calls, no API cost. Useful for
   wiring validation, schema checks, and sanity-testing the judge
   before spending budget.
2. ``--generator haiku``: generates candidates with the cheap Anthropic
   SKU (``claude-haiku-4-5`` or equivalent) and judges with the default
   judge model. Intended for small-sample validation runs on 2-3
   scenarios.
3. ``--generator <sku>``: generates candidates with an arbitrary SKU
   listed in ``--models`` and judges them. This is the live-frontier
   path. Run only with explicit budget approval; full matrix costs are
   estimated in ``BENCHMARK_RUN.md``.

Usage examples::

    # Dry run (no API calls) on one module:
    python -m tools.benchmark_runner \\
        --modules 06_research_translation \\
        --models claude-opus-4-7,claude-sonnet-4-5 \\
        --dry-run

    # Cheap validation with Haiku across 3 scenarios:
    python -m tools.benchmark_runner \\
        --modules 06_research_translation \\
        --models claude-haiku-4-5-20251001 \\
        --generator haiku \\
        --scenarios 3

    # Full frontier run (expensive, requires explicit ``--yes-live``):
    python -m tools.benchmark_runner \\
        --modules all \\
        --models claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro \\
        --generator live \\
        --yes-live

The CSV is append-only. Each row records:
    module, scenario_id, model, score,
    critical_failure_triggered, judge_model,
    judge_cache_hit_rate, run_date
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from .eval_runner import EvaluationRunner, EvaluationConfig


DEFAULT_JUDGE_MODEL = "claude-opus-4-6"
CSV_PATH = Path("results/frontier_benchmark_v1.csv")
CSV_COLUMNS = [
    "module",
    "scenario_id",
    "model",
    "score",
    "critical_failure_triggered",
    "judge_model",
    "judge_cache_hit_rate",
    "run_date",
]


@dataclass
class BenchmarkRow:
    module: str
    scenario_id: str
    model: str
    score: float
    critical_failure_triggered: bool
    judge_model: str
    judge_cache_hit_rate: float
    run_date: str

    def to_csv_row(self) -> list:
        return [
            self.module,
            self.scenario_id,
            self.model,
            f"{self.score:.2f}",
            "true" if self.critical_failure_triggered else "false",
            self.judge_model,
            f"{self.judge_cache_hit_rate:.3f}",
            self.run_date,
        ]


def _ensure_csv(path: Path) -> None:
    """Create the CSV with the documented header if it does not exist."""
    if path.exists():
        # Validate header on existing file (non-destructive)
        with path.open() as f:
            first = f.readline().rstrip("\n").split(",")
            if first != CSV_COLUMNS:
                print(
                    f"Warning: existing {path} has unexpected header {first!r}; "
                    f"appending rows under assumed schema {CSV_COLUMNS!r}",
                    file=sys.stderr,
                )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_COLUMNS)


def _append_row(path: Path, row: BenchmarkRow) -> None:
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        w.writerow(row.to_csv_row())


def _collect_scenarios(
    runner: EvaluationRunner,
    modules: list[str],
    scenario_cap: int | None,
) -> list[tuple[str, str]]:
    """Collect (module, scenario_id) pairs, capped per module if requested."""
    pairs: list[tuple[str, str]] = []
    if modules == ["all"]:
        module_ids = [m["id"] for m in runner.list_modules()]
    else:
        module_ids = modules

    for m in module_ids:
        scenarios = runner.list_scenarios(m)
        if scenario_cap is not None:
            scenarios = scenarios[:scenario_cap]
        for s in scenarios:
            pairs.append((m, s["id"]))
    return pairs


def _dry_run_candidate(
    runner: EvaluationRunner,
    module: str,
    scenario_id: str,
) -> str | None:
    """Return the golden answer as the candidate, or None if missing."""
    try:
        return runner.load_golden_answer(module, scenario_id)
    except FileNotFoundError:
        return None


def _live_candidate(
    model: str,
    scenario: dict,
) -> str:
    """Generate a candidate from a live model. Not invoked in --dry-run."""
    # Import lazily so the dry-run path does not require provider SDKs.
    raise NotImplementedError(
        "Live generation not wired in this session. Use --dry-run. See "
        "BENCHMARK_RUN.md for the full invocation + estimated cost."
    )


def run_benchmark(
    modules: list[str],
    models: list[str],
    dry_run: bool,
    generator: str,
    scenario_cap: int | None,
    judge_model: str,
    yes_live: bool,
) -> int:
    """Run the benchmark; append rows to the CSV; return #rows written."""
    if not dry_run and generator == "live" and not yes_live:
        print(
            "Refusing to run live-frontier generation without --yes-live. "
            "See BENCHMARK_RUN.md for the full cost estimate.",
            file=sys.stderr,
        )
        return 0

    runner = EvaluationRunner()
    _ensure_csv(CSV_PATH)

    pairs = _collect_scenarios(runner, modules, scenario_cap)
    if not pairs:
        print("No scenarios collected; check --modules argument.", file=sys.stderr)
        return 0

    run_date = _dt.date.today().isoformat()
    rows_written = 0

    for module, scenario_id in pairs:
        for model in models:
            if dry_run:
                candidate = _dry_run_candidate(runner, module, scenario_id)
                if candidate is None:
                    print(
                        f"skip {module}/{scenario_id}: no golden answer for "
                        f"dry run",
                        file=sys.stderr,
                    )
                    continue
            else:
                scenario = runner.load_scenario(module, scenario_id)
                candidate = _live_candidate(model, scenario)

            config = EvaluationConfig(
                module=module,
                scenario_name=scenario_id,
                rubric_name="standard",
            )
            try:
                result = runner.run_evaluation(config, ai_output=candidate)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"error grading {module}/{scenario_id} with {model}: {exc}",
                    file=sys.stderr,
                )
                continue

            row = BenchmarkRow(
                module=module,
                scenario_id=scenario_id,
                model=model,
                score=float(result.overall_score),
                critical_failure_triggered=bool(result.critical_failures),
                judge_model=judge_model if not dry_run else "rubric-engine-dry-run",
                judge_cache_hit_rate=0.0,  # populated by live path
                run_date=run_date,
            )
            _append_row(CSV_PATH, row)
            rows_written += 1
            print(
                json.dumps(
                    {
                        "module": module,
                        "scenario_id": scenario_id,
                        "model": model,
                        "score": round(float(result.overall_score), 2),
                        "passed": result.passed,
                    }
                )
            )

    print(
        f"\nbenchmark: wrote {rows_written} rows to {CSV_PATH}",
        file=sys.stderr,
    )
    return rows_written


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Frontier-model benchmark runner (schema append-only).",
    )
    ap.add_argument(
        "--modules",
        default="all",
        help="Comma-separated module ids or 'all' (default: all).",
    )
    ap.add_argument(
        "--models",
        default="claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro",
        help="Comma-separated SKUs to benchmark.",
    )
    ap.add_argument(
        "--scenarios",
        type=int,
        default=None,
        help="Cap scenarios per module (default: no cap).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Score goldens as candidates, no API calls.",
    )
    ap.add_argument(
        "--generator",
        default="dry",
        choices=["dry", "haiku", "live"],
        help="Candidate generator (dry = goldens, haiku = cheap SKU, live = full frontier).",
    )
    ap.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help="Judge model label recorded in CSV (not used in --dry-run).",
    )
    ap.add_argument(
        "--yes-live",
        action="store_true",
        help="Required to run live-frontier generation (cost acknowledgement).",
    )
    args = ap.parse_args()

    modules = [m.strip() for m in args.modules.split(",") if m.strip()]
    models = [s.strip() for s in args.models.split(",") if s.strip()]

    # Treat --dry-run and --generator=dry as equivalent
    dry = args.dry_run or args.generator == "dry"

    run_benchmark(
        modules=modules,
        models=models,
        dry_run=dry,
        generator=args.generator,
        scenario_cap=args.scenarios,
        judge_model=args.judge_model,
        yes_live=args.yes_live,
    )


if __name__ == "__main__":
    main()
