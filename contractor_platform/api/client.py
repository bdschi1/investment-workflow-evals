"""Python client for the Investment Workflow Evaluations API."""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class GoldenAnswer:
    """A golden answer from the platform."""
    id: str
    module: str
    scenario_name: str
    content: str
    quality_score: float
    metadata: dict


@dataclass
class EvaluationResult:
    """Result of evaluating AI output against a scenario."""
    scenario_id: str
    overall_score: float
    dimension_scores: dict
    passed: bool
    critical_failures: list
    feedback: str


@dataclass
class PreferencePair:
    """A preference pair for DPO training."""
    prompt: str
    chosen: str
    rejected: str
    scenario_id: str
    metadata: dict


class EvalClient:
    """
    Client for interacting with the Investment Workflow Evaluations platform.

    This client provides methods for:
    - Fetching approved golden answers for training
    - Evaluating AI outputs against scenarios
    - Getting preference pairs for DPO training
    - Managing evaluation tasks

    Usage:
        client = EvalClient(api_key="your-api-key")

        # Get golden answers for training
        golden_answers = client.get_golden_answers(
            module="equity_thesis",
            min_quality_score=90
        )

        # Evaluate AI output
        result = client.evaluate(
            scenario_id="biotech_phase3_catalyst",
            ai_output=model_response
        )

        # Get preference pairs for DPO
        pairs = client.get_preference_pairs(
            module="equity_thesis",
            limit=1000
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the client.

        Args:
            api_key: API key for authentication (for remote API)
            base_url: Base URL of the API server
            data_dir: Local data directory (for local mode)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "data"

        # Use local mode if no API key provided
        self.local_mode = api_key is None

    def get_golden_answers(
        self,
        module: Optional[str] = None,
        scenario_name: Optional[str] = None,
        min_quality_score: float = 0.0,
        status: str = "approved",
        limit: int = 100,
    ) -> list[GoldenAnswer]:
        """
        Fetch approved golden answers for training.

        Args:
            module: Filter by evaluation module (e.g., "equity_thesis")
            scenario_name: Filter by specific scenario
            min_quality_score: Minimum quality score (0-100)
            status: Filter by status (default: approved)
            limit: Maximum number of results

        Returns:
            List of GoldenAnswer objects
        """
        if self.local_mode:
            return self._get_golden_answers_local(
                module, scenario_name, min_quality_score, limit
            )

        # Remote API call would go here
        raise NotImplementedError("Remote API not yet implemented")

    def _get_golden_answers_local(
        self,
        module: Optional[str],
        scenario_name: Optional[str],
        min_quality_score: float,
        limit: int,
    ) -> list[GoldenAnswer]:
        """Get golden answers from local files."""
        results = []
        evals_dir = Path(__file__).parent.parent.parent / "evals"

        # Find all golden answer files
        for module_dir in evals_dir.iterdir():
            if not module_dir.is_dir():
                continue

            if module and module not in module_dir.name:
                continue

            golden_dir = module_dir / "golden_answers"
            if not golden_dir.exists():
                continue

            for ga_file in golden_dir.glob("*.md"):
                if scenario_name and scenario_name not in ga_file.stem:
                    continue

                with open(ga_file) as f:
                    content = f.read()

                # Create golden answer object
                ga = GoldenAnswer(
                    id=f"{module_dir.name}/{ga_file.stem}",
                    module=module_dir.name,
                    scenario_name=ga_file.stem,
                    content=content,
                    quality_score=95.0,  # Assume high quality for committed answers
                    metadata={"file_path": str(ga_file)},
                )
                results.append(ga)

                if len(results) >= limit:
                    break

        return results

    def evaluate(
        self,
        scenario_id: str,
        ai_output: str,
        rubric_id: Optional[str] = None,
        return_detailed_scores: bool = False,
    ) -> EvaluationResult:
        """
        Evaluate AI output against a scenario.

        Args:
            scenario_id: ID of the scenario to evaluate against
            ai_output: The AI-generated response to evaluate
            rubric_id: Specific rubric to use (default: standard)
            return_detailed_scores: Include dimension-level scores

        Returns:
            EvaluationResult with scores and feedback
        """
        if self.local_mode:
            return self._evaluate_local(
                scenario_id, ai_output, rubric_id, return_detailed_scores
            )

        raise NotImplementedError("Remote API not yet implemented")

    def _evaluate_local(
        self,
        scenario_id: str,
        ai_output: str,
        rubric_id: Optional[str],
        return_detailed_scores: bool,
    ) -> EvaluationResult:
        """Run evaluation locally using scenario and rubric files."""
        # This would integrate with the grading engine
        # For now, return a placeholder

        return EvaluationResult(
            scenario_id=scenario_id,
            overall_score=0.0,
            dimension_scores={},
            passed=False,
            critical_failures=[],
            feedback="Local evaluation not yet fully implemented. Use grading_engine.py directly.",
        )

    def get_preference_pairs(
        self,
        module: Optional[str] = None,
        limit: int = 1000,
        min_score_delta: float = 10.0,
    ) -> list[PreferencePair]:
        """
        Get preference pairs for DPO training.

        Pairs are constructed from:
        - Chosen: Golden answers or high-scoring submissions
        - Rejected: Lower-scoring submissions for the same scenario

        Args:
            module: Filter by evaluation module
            limit: Maximum number of pairs
            min_score_delta: Minimum score difference between chosen/rejected

        Returns:
            List of PreferencePair objects for training
        """
        if self.local_mode:
            return self._get_preference_pairs_local(module, limit, min_score_delta)

        raise NotImplementedError("Remote API not yet implemented")

    def _get_preference_pairs_local(
        self,
        module: Optional[str],
        limit: int,
        min_score_delta: float,
    ) -> list[PreferencePair]:
        """Get preference pairs from local data."""
        # This would construct pairs from submissions data
        # For now, return empty list
        return []

    def get_scenario(self, scenario_id: str) -> dict:
        """
        Get a scenario definition by ID.

        Args:
            scenario_id: The scenario ID (e.g., "biotech_phase3_catalyst")

        Returns:
            Scenario definition as dictionary
        """
        if self.local_mode:
            return self._get_scenario_local(scenario_id)

        raise NotImplementedError("Remote API not yet implemented")

    def _get_scenario_local(self, scenario_id: str) -> dict:
        """Get scenario from local files."""
        import yaml

        evals_dir = Path(__file__).parent.parent.parent / "evals"

        # Search for scenario file
        for module_dir in evals_dir.iterdir():
            if not module_dir.is_dir():
                continue

            scenario_file = module_dir / "scenarios" / f"{scenario_id}.yaml"
            if scenario_file.exists():
                with open(scenario_file) as f:
                    return yaml.safe_load(f)

        raise FileNotFoundError(f"Scenario not found: {scenario_id}")

    def get_rubric(self, rubric_id: str) -> dict:
        """
        Get a rubric definition by ID.

        Args:
            rubric_id: The rubric ID (e.g., "standard")

        Returns:
            Rubric definition as dictionary
        """
        if self.local_mode:
            return self._get_rubric_local(rubric_id)

        raise NotImplementedError("Remote API not yet implemented")

    def _get_rubric_local(self, rubric_id: str) -> dict:
        """Get rubric from local files."""
        import yaml

        evals_dir = Path(__file__).parent.parent.parent / "evals"

        # Search for rubric file
        for module_dir in evals_dir.iterdir():
            if not module_dir.is_dir():
                continue

            rubric_file = module_dir / "rubrics" / f"{rubric_id}.yaml"
            if rubric_file.exists():
                with open(rubric_file) as f:
                    return yaml.safe_load(f)

        raise FileNotFoundError(f"Rubric not found: {rubric_id}")

    def list_scenarios(self, module: Optional[str] = None) -> list[dict]:
        """
        List available scenarios.

        Args:
            module: Filter by evaluation module

        Returns:
            List of scenario summaries
        """
        scenarios = []
        evals_dir = Path(__file__).parent.parent.parent / "evals"

        for module_dir in evals_dir.iterdir():
            if not module_dir.is_dir():
                continue

            if module and module not in module_dir.name:
                continue

            scenarios_dir = module_dir / "scenarios"
            if not scenarios_dir.exists():
                continue

            for scenario_file in scenarios_dir.glob("*.yaml"):
                scenarios.append({
                    "id": scenario_file.stem,
                    "module": module_dir.name,
                    "file_path": str(scenario_file),
                })

        return scenarios

    def list_modules(self) -> list[dict]:
        """
        List available evaluation modules.

        Returns:
            List of module information
        """
        modules = []
        evals_dir = Path(__file__).parent.parent.parent / "evals"

        for module_dir in evals_dir.iterdir():
            if not module_dir.is_dir():
                continue

            readme_path = module_dir / "README.md"
            description = ""
            if readme_path.exists():
                with open(readme_path) as f:
                    # Get first paragraph as description
                    lines = f.read().split("\n\n")
                    if len(lines) > 1:
                        description = lines[1].strip()

            modules.append({
                "id": module_dir.name,
                "name": module_dir.name.replace("_", " ").title(),
                "description": description,
                "scenario_count": len(list((module_dir / "scenarios").glob("*.yaml")))
                    if (module_dir / "scenarios").exists() else 0,
            })

        return modules
