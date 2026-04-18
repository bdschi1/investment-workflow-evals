"""
Evaluation runner for investment workflow assessments.

This module handles loading scenarios, running evaluations against AI outputs,
and generating structured reports.

Usage:
    python -m tools.eval_runner run --module equity_thesis --scenario biotech_phase3_catalyst
    python -m tools.eval_runner list --module equity_thesis
    python -m tools.eval_runner report --output-dir reports/
"""

import argparse
import json
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass


DEFAULT_FRONTIER_MODELS: tuple[str, ...] = (
    "claude-opus-4-7",
    "claude-sonnet-4-5",
    "gpt-5",
    "gemini-2.5-pro",
)


def parse_models_flag(raw: Optional[str]) -> list[str]:
    """Parse a --models value into a cleaned list of SKU strings.

    Accepts `None`/empty (returns `[]`), a single SKU, or a
    comma-separated list. Whitespace is stripped; empty tokens are
    dropped; order is preserved with duplicates removed.

    The parsed list is attached to EvaluationConfig.models. Callers
    that are not benchmark-aware can ignore the attribute; the
    benchmark runner uses it to fan out generation calls.
    """
    if not raw:
        return []
    seen: list[str] = []
    for token in raw.split(","):
        sku = token.strip()
        if sku and sku not in seen:
            seen.append(sku)
    return seen


@dataclass
class EvaluationConfig:
    """Configuration for running an evaluation."""
    module: str
    scenario_name: str
    rubric_name: str = "standard"
    ai_output_path: Optional[str] = None
    output_dir: Path = None
    models: list[str] = None  # Optional frontier SKUs for benchmark fan-out

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path("results")
        if self.models is None:
            self.models = []


@dataclass
class EvaluationResult:
    """Result of running an evaluation."""
    scenario_id: str
    scenario_title: str
    module: str
    timestamp: str
    ai_output: str
    scores: dict
    overall_score: float
    passed: bool
    critical_failures: list
    detailed_feedback: dict
    likert_score: int = 0
    likert_label: str = ""


class EvaluationRunner:
    """Loads scenarios, runs evaluations, and generates reports."""

    def __init__(self, base_path: Path = None):
        """Initialize with base path to the repository."""
        self.base_path = base_path or Path(__file__).parent.parent
        self.evals_path = self.base_path / "evals"

    def list_modules(self) -> list:
        """List all available evaluation modules."""
        modules = []
        for module_dir in sorted(self.evals_path.iterdir()):
            if not module_dir.is_dir() or module_dir.name.startswith("."):
                continue

            readme_path = module_dir / "README.md"
            description = ""
            if readme_path.exists():
                with open(readme_path) as f:
                    lines = f.read().split("\n")
                    for line in lines:
                        if line and not line.startswith("#"):
                            description = line.strip()
                            break

            scenarios_dir = module_dir / "scenarios"
            scenario_count = len(list(scenarios_dir.glob("*.yaml"))) if scenarios_dir.exists() else 0

            modules.append({
                "id": module_dir.name,
                "name": module_dir.name.replace("_", " ").title(),
                "description": description[:100] + "..." if len(description) > 100 else description,
                "scenario_count": scenario_count,
            })

        return modules

    def list_scenarios(self, module: str) -> list:
        """List all scenarios in a module."""
        scenarios = []
        module_dir = self._find_module_dir(module)
        if not module_dir:
            return scenarios

        scenarios_dir = module_dir / "scenarios"
        if not scenarios_dir.exists():
            return scenarios

        for scenario_file in sorted(scenarios_dir.glob("*.yaml")):
            with open(scenario_file) as f:
                scenario = yaml.safe_load(f)

            scenarios.append({
                "id": scenario.get("id", scenario_file.stem),
                "title": scenario.get("title", ""),
                "category": scenario.get("category", ""),
                "difficulty": scenario.get("difficulty", ""),
                "estimated_time_minutes": scenario.get("estimated_time_minutes", 0),
            })

        return scenarios

    def load_scenario(self, module: str, scenario_name: str) -> Dict[str, Any]:
        """Load a scenario definition from YAML."""
        module_dir = self._find_module_dir(module)
        if not module_dir:
            raise FileNotFoundError(f"Module not found: {module}")

        scenario_path = module_dir / "scenarios" / f"{scenario_name}.yaml"
        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario not found: {scenario_path}")

        with open(scenario_path) as f:
            return yaml.safe_load(f)

    def load_rubric(self, module: str, rubric_name: str = "standard") -> Dict[str, Any]:
        """Load a rubric definition from YAML."""
        module_dir = self._find_module_dir(module)
        if not module_dir:
            raise FileNotFoundError(f"Module not found: {module}")

        rubric_path = module_dir / "rubrics" / f"{rubric_name}.yaml"
        if not rubric_path.exists():
            raise FileNotFoundError(f"Rubric not found: {rubric_path}")

        with open(rubric_path) as f:
            return yaml.safe_load(f)

    def load_golden_answer(self, module: str, scenario_name: str) -> str:
        """Load the golden answer for a scenario."""
        module_dir = self._find_module_dir(module)
        if not module_dir:
            raise FileNotFoundError(f"Module not found: {module}")

        ga_path = module_dir / "golden_answers" / f"{scenario_name}.md"
        if not ga_path.exists():
            raise FileNotFoundError(f"Golden answer not found: {ga_path}")

        with open(ga_path) as f:
            return f.read()

    def _find_module_dir(self, module: str) -> Optional[Path]:
        """Find module directory by name or ID."""
        for module_dir in self.evals_path.iterdir():
            if module_dir.is_dir():
                if module_dir.name == module or module in module_dir.name:
                    return module_dir
        return None

    def run(self, module: str, scenario_name: str, ai_output: str = None) -> Dict[str, Any]:
        """Run complete evaluation workflow (legacy interface)."""
        print(f"Loading scenario: {module}/{scenario_name}")
        scenario = self.load_scenario(module, scenario_name)
        return {"scenario": scenario, "timestamp": datetime.now().isoformat()}

    def run_evaluation(
        self,
        config: EvaluationConfig,
        ai_output: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Run a complete evaluation.

        Args:
            config: Evaluation configuration
            ai_output: AI-generated output to evaluate (or read from config path)

        Returns:
            EvaluationResult with scores and feedback
        """
        # Load scenario
        scenario = self.load_scenario(config.module, config.scenario_name)

        # Load rubric
        try:
            rubric = self.load_rubric(config.module, config.rubric_name)
        except FileNotFoundError:
            rubric = self._default_rubric()

        # Load or read AI output
        if ai_output is None:
            if config.ai_output_path:
                with open(config.ai_output_path) as f:
                    ai_output = f.read()
            else:
                raise ValueError("No AI output provided")

        # Run grading
        from .grading_engine import GradingEngine
        grader = GradingEngine(rubric)
        scores, critical_failures, detailed_feedback = grader.grade(
            ai_output, scenario
        )

        # Calculate overall score
        # Handle both decimal weights (0.30) and integer weights (30)
        total_weight = sum(dim.get("weight", 1.0) for dim in rubric.get("dimensions", []))

        if total_weight > 10:  # Integer weights (sum to 100)
            overall_score = sum(
                scores.get(dim["id"], 0) * dim.get("weight", 1.0) / 100
                for dim in rubric.get("dimensions", [])
            )
        else:  # Decimal weights (sum to 1.0)
            overall_score = sum(
                scores.get(dim["id"], 0) * dim.get("weight", 1.0)
                for dim in rubric.get("dimensions", [])
            )

        # Determine pass/fail
        pass_threshold = rubric.get("pass_threshold", 70)
        passed = overall_score >= pass_threshold and len(critical_failures) == 0

        # Likert overlay (5-35 scale)
        from .grading_engine import _score_to_likert
        likert_score, likert_label = _score_to_likert(overall_score)

        return EvaluationResult(
            scenario_id=scenario.get("id", config.scenario_name),
            scenario_title=scenario.get("title", ""),
            module=config.module,
            timestamp=datetime.now(timezone.utc).isoformat(),
            ai_output=ai_output,
            scores=scores,
            overall_score=overall_score,
            passed=passed,
            critical_failures=critical_failures,
            detailed_feedback=detailed_feedback,
            likert_score=likert_score,
            likert_label=likert_label,
        )

    def _default_rubric(self) -> dict:
        """Return a default rubric structure."""
        return {
            "dimensions": [
                {"id": "factual_accuracy", "name": "Factual Accuracy", "weight": 0.30},
                {"id": "analytical_rigor", "name": "Analytical Rigor", "weight": 0.25},
                {"id": "risk_assessment", "name": "Risk Assessment", "weight": 0.20},
                {"id": "evidence_quality", "name": "Evidence Quality", "weight": 0.15},
                {"id": "completeness", "name": "Completeness", "weight": 0.10},
            ],
            "critical_failures": [],
            "pass_threshold": 70,
        }

    def generate_report(
        self,
        result: EvaluationResult,
        output_dir: Path = None,
        format: str = "json",
    ) -> Path:
        """Generate an evaluation report."""
        output_dir = output_dir or Path("results")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{result.module}_{result.scenario_id}_{timestamp}"

        if format == "json":
            output_path = output_dir / f"{filename}.json"
            with open(output_path, "w") as f:
                json.dump({
                    "scenario_id": result.scenario_id,
                    "scenario_title": result.scenario_title,
                    "module": result.module,
                    "timestamp": result.timestamp,
                    "overall_score": result.overall_score,
                    "likert_score": result.likert_score,
                    "likert_label": result.likert_label,
                    "passed": result.passed,
                    "scores": result.scores,
                    "critical_failures": result.critical_failures,
                    "detailed_feedback": result.detailed_feedback,
                }, f, indent=2)

        elif format == "markdown":
            output_path = output_dir / f"{filename}.md"
            with open(output_path, "w") as f:
                f.write(f"# Evaluation Report: {result.scenario_title}\n\n")
                f.write(f"**Module:** {result.module}\n")
                f.write(f"**Scenario:** {result.scenario_id}\n")
                f.write(f"**Timestamp:** {result.timestamp}\n")
                f.write(f"**Overall Score:** {result.overall_score:.1f}/100 (Likert: {result.likert_score}/35 — {result.likert_label})\n")
                f.write(f"**Status:** {'PASS' if result.passed else 'FAIL'}\n\n")

                f.write("## Dimension Scores\n\n")
                for dim, score in result.scores.items():
                    f.write(f"- **{dim}:** {score:.1f}\n")

                if result.critical_failures:
                    f.write("\n## Critical Failures\n\n")
                    for failure in result.critical_failures:
                        f.write(f"- {failure}\n")

                f.write("\n## Detailed Feedback\n\n")
                for dim, feedback in result.detailed_feedback.items():
                    f.write(f"### {dim}\n\n{feedback}\n\n")

        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path


_CI_MODEL = "claude-haiku-4-5-20251001"
_CI_LIMIT = 5
_CI_DEFAULT_THRESHOLD = 0.70


def _run_ci_mode(runner: "EvaluationRunner", args) -> None:
    """Run the fast CI quality gate.

    Collects up to _CI_LIMIT scenarios (across all modules or from one module),
    grades each using a stub (no real AI output — tests structural pass/fail),
    outputs JSON to stdout, exits 0/1.
    """
    threshold = getattr(args, "threshold", _CI_DEFAULT_THRESHOLD)
    module_filter = getattr(args, "module", None)

    # Collect scenarios
    collected: list[tuple[str, str]] = []  # (module_name, scenario_name)
    try:
        if module_filter:
            for s in runner.list_scenarios(module_filter):
                collected.append((module_filter, s["id"]))
                if len(collected) >= _CI_LIMIT:
                    break
        else:
            for m in runner.list_modules():
                for s in runner.list_scenarios(m["id"]):
                    collected.append((m["id"], s["id"]))
                    if len(collected) >= _CI_LIMIT:
                        break
                if len(collected) >= _CI_LIMIT:
                    break
    except Exception as exc:
        print(f"CI mode: failed to collect scenarios: {exc}", file=sys.stderr)
        collected = []

    n = len(collected)
    print(
        f"CI mode: evaluating {n} scenarios with {_CI_MODEL}...",
        file=sys.stderr,
    )

    passed_ids: list[str] = []
    failed_ids: list[str] = []

    for module_name, scenario_name in collected:
        try:
            # Load golden answer as a proxy AI output for CI scoring
            try:
                golden = runner.load_golden_answer(module_name, scenario_name)
            except FileNotFoundError:
                golden = "No output available for CI test."

            config = EvaluationConfig(
                module=module_name,
                scenario_name=scenario_name,
                rubric_name="standard",
            )
            result = runner.run_evaluation(config, ai_output=golden)
            if result.passed:
                passed_ids.append(scenario_name)
            else:
                failed_ids.append(scenario_name)
        except Exception as exc:
            print(
                f"CI mode: scenario {scenario_name} errored: {exc}",
                file=sys.stderr,
            )
            failed_ids.append(scenario_name)

    total = len(passed_ids) + len(failed_ids)
    pass_rate = len(passed_ids) / total if total > 0 else 0.0
    gate_passed = pass_rate >= threshold

    status_str = "CI PASS" if gate_passed else "CI FAIL"
    output = {
        "ci_mode": True,
        "model": _CI_MODEL,
        "scenarios_evaluated": total,
        "passed": len(passed_ids),
        "failed": len(failed_ids),
        "pass_rate": round(pass_rate, 4),
        "pass": gate_passed,
        "threshold": threshold,
        "failed_scenarios": failed_ids,
        "summary": (
            f"{len(passed_ids)}/{total} scenarios passed "
            f"({pass_rate * 100:.1f}%). {status_str}."
        ),
    }

    print(json.dumps(output, indent=2))
    sys.exit(0 if gate_passed else 1)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run investment workflow evaluations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List modules or scenarios")
    list_parser.add_argument("--module", help="Show scenarios for this module")

    # CI command
    ci_parser = subparsers.add_parser("ci", help="Run fast CI quality gate (5 scenarios, Haiku judge)")
    ci_parser.add_argument("--module", help="Limit CI run to a specific module (optional)")
    ci_parser.add_argument("--threshold", type=float, default=0.70,
                           help="Pass-rate threshold for CI gate (default 0.70)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run an evaluation")
    run_parser.add_argument("--module", required=True, help="Evaluation module")
    run_parser.add_argument("--scenario", required=True, help="Scenario name")
    run_parser.add_argument("--input", help="Path to AI output file")
    run_parser.add_argument("--rubric", default="standard", help="Rubric to use")
    run_parser.add_argument("--output-dir", default="results", help="Output directory")
    run_parser.add_argument("--format", default="json", choices=["json", "markdown"],
                           help="Report format")
    run_parser.add_argument(
        "--models",
        default=None,
        help=(
            "Comma-separated frontier SKUs to benchmark (e.g. "
            "'claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro'). "
            "When omitted, behavior matches the pre-existing single-input path. "
            "When supplied with --input, the SKU list is recorded in the "
            "result metadata; when supplied without --input, the benchmark "
            "runner fans out one generation call per SKU."
        ),
    )

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument("--output-dir", required=True, help="Output directory")

    args = parser.parse_args()

    runner = EvaluationRunner()

    if args.command == "ci":
        _run_ci_mode(runner, args)
        return

    if args.command == "list":
        if args.module:
            scenarios = runner.list_scenarios(args.module)
            print(f"\nScenarios in {args.module}:\n")
            for s in scenarios:
                print(f"  {s['id']:<30} {s['title']:<40} [{s['difficulty']}]")
        else:
            modules = runner.list_modules()
            print("\nAvailable Modules:\n")
            for m in modules:
                print(f"  {m['id']:<30} ({m['scenario_count']} scenarios)")
                if m['description']:
                    print(f"    {m['description']}")

    elif args.command == "run":
        models = parse_models_flag(getattr(args, "models", None))
        config = EvaluationConfig(
            module=args.module,
            scenario_name=args.scenario,
            rubric_name=args.rubric,
            ai_output_path=args.input,
            output_dir=Path(args.output_dir),
            models=models,
        )

        if not args.input:
            print("Error: --input is required for running evaluations")
            return

        print(f"Running evaluation: {args.module}/{args.scenario}")
        result = runner.run_evaluation(config)

        print(f"\nOverall Score: {result.overall_score:.1f}/100 (Likert: {result.likert_score}/35 — {result.likert_label})")
        print(f"Status: {'PASS' if result.passed else 'FAIL'}")

        if result.critical_failures:
            print("\nCritical Failures:")
            for failure in result.critical_failures:
                print(f"  - {failure}")

        report_path = runner.generate_report(
            result,
            output_dir=config.output_dir,
            format=args.format,
        )
        print(f"\nReport saved to: {report_path}")

    elif args.command == "report":
        print("Report generation from existing results not yet implemented")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
