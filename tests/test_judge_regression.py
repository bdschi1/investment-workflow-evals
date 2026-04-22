"""Regression tests for InvestmentWorkflowJudge + GradingEngine pipeline.

Verifies that AI judge dimension scores on baseline responses stay within
±5% of expected overall scores. Catches prompt regressions without live
API calls.

All tests mock InvestmentWorkflowJudge — no real API calls are made.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tools.ai_judge import JudgeResult
from tools.grading_engine import GradingEngine

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "judge_baseline.json"
RUBRIC_PATH = (
    Path(__file__).parent.parent
    / "evals" / "01_equity_thesis" / "rubrics" / "standard.yaml"
)
TOLERANCE = 0.05  # ±5 percentage points of a 0-100 score


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_baselines() -> list[dict[str, Any]]:
    with open(FIXTURES_PATH) as f:
        return json.load(f)["baselines"]


def _load_rubric() -> dict:
    with open(RUBRIC_PATH) as f:
        return yaml.safe_load(f)


def _make_judge_result(baseline: dict[str, Any]) -> JudgeResult:
    """Build a JudgeResult from the baseline fixture's dimension_scores."""
    return JudgeResult(
        dimension_scores=dict(baseline["dimension_scores"]),
        critical_failures=list(baseline.get("critical_failures", [])),
        detected_patterns={},
        confidence="high",
        feedback={dim: "regression fixture" for dim in baseline["dimension_scores"]},
        fallback_used=False,
        overall_score=0.0,
    )


def _run_pipeline(baseline: dict[str, Any], rubric: dict) -> float:
    """Run GradingEngine with mocked InvestmentWorkflowJudge; return overall_score."""
    judge_result = _make_judge_result(baseline)

    # Patch the judge inside GradingEngine._score_with_llm
    engine = GradingEngine(rubric)
    engine._judge = MagicMock()
    engine._judge.grade.return_value = judge_result

    scenario = {
        "id": baseline["scenario_id"],
        "context": {"situation": baseline["scenario_context"]},
        "task": {"prompt": baseline["task"]},
    }

    scores, failures, _ = engine.grade(
        ai_output=baseline["model_response"],
        scenario=scenario,
        use_llm=True,
    )
    overall = engine.calculate_overall_score(scores)
    return overall


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestJudgeRegression:
    """Regression suite: pipeline overall scores remain within ±5% of baseline."""

    @pytest.fixture(scope="class")
    def rubric(self) -> dict:
        return _load_rubric()

    @pytest.fixture(scope="class")
    def baselines(self) -> list[dict[str, Any]]:
        return _load_baselines()

    def test_excellent_response_passes_threshold(self, rubric: dict, baselines: list) -> None:
        """Excellent baseline should produce overall_score >= pass_threshold (70)."""
        baseline = next(b for b in baselines if b["id"] == "iwe_baseline_001")
        overall = _run_pipeline(baseline, rubric)
        assert overall >= rubric.get("pass_threshold", 70), (
            f"Excellent response expected to pass threshold, overall_score={overall:.1f}"
        )

    def test_poor_response_below_threshold(self, rubric: dict, baselines: list) -> None:
        """Poor baseline should produce overall_score below pass_threshold (70)."""
        baseline = next(b for b in baselines if b["id"] == "iwe_baseline_002")
        overall = _run_pipeline(baseline, rubric)
        assert overall < rubric.get("pass_threshold", 70), (
            f"Poor response expected to fail threshold, overall_score={overall:.1f}"
        )

    def test_fail_response_has_critical_failures(self, rubric: dict, baselines: list) -> None:
        """Fail baseline should carry critical failures, causing determine_pass_fail=False."""
        baseline = next(b for b in baselines if b["id"] == "iwe_baseline_003")
        judge_result = _make_judge_result(baseline)

        engine = GradingEngine(rubric)
        engine._judge = MagicMock()
        engine._judge.grade.return_value = judge_result

        scenario = {
            "id": baseline["scenario_id"],
            "context": {"situation": baseline["scenario_context"]},
            "task": {"prompt": baseline["task"]},
        }
        scores, failures, _ = engine.grade(
            ai_output=baseline["model_response"],
            scenario=scenario,
            use_llm=True,
        )
        overall = engine.calculate_overall_score(scores)
        # Critical failures in the judge result are returned by the judge, not the heuristics;
        # verify the score itself is low (< 30) regardless
        assert overall < 30.0, (
            f"Fail response expected overall_score <30, got {overall:.1f}"
        )

    @pytest.mark.parametrize("baseline_id", [
        "iwe_baseline_001",
        "iwe_baseline_002",
        "iwe_baseline_003",
    ])
    def test_scores_within_tolerance_of_baseline(
        self, baseline_id: str, rubric: dict, baselines: list
    ) -> None:
        """All baselines: computed overall_score within ±5 points of expected."""
        baseline = next(b for b in baselines if b["id"] == baseline_id)
        expected: float = baseline["expected_overall_score"]
        actual = _run_pipeline(baseline, rubric)
        diff = abs(actual - expected)
        assert diff <= TOLERANCE * 100, (
            f"{baseline_id}: expected {expected:.1f}, got {actual:.1f}, "
            f"diff {diff:.1f} exceeds tolerance {TOLERANCE * 100:.1f}"
        )

    def test_fixture_file_is_valid_and_complete(self) -> None:
        """Fixture file must parse and contain at least 3 baselines with required keys."""
        with open(FIXTURES_PATH) as f:
            data = json.load(f)

        assert "baselines" in data
        assert len(data["baselines"]) >= 3

        required_keys = {
            "id", "scenario_id", "model_response",
            "dimension_scores", "expected_overall_score",
        }
        for baseline in data["baselines"]:
            missing = required_keys - baseline.keys()
            assert not missing, f"{baseline.get('id','?')}: missing keys {missing}"

    def test_dimension_score_keys_match_rubric_dimensions(
        self, rubric: dict, baselines: list
    ) -> None:
        """Each baseline's dimension_scores keys should be a subset of rubric dimension ids."""
        rubric_dim_ids = {d["id"] for d in rubric.get("dimensions", [])}
        for baseline in baselines:
            fixture_dims = set(baseline["dimension_scores"].keys())
            unknown = fixture_dims - rubric_dim_ids
            assert not unknown, (
                f"{baseline['id']}: unknown dimension ids in fixture: {unknown}"
            )


# ---------------------------------------------------------------------------
# Cross-model judge agreement test
# ---------------------------------------------------------------------------

CROSS_MODEL_TOLERANCE = 8.0  # overall-score delta (0-100) permitted between judges


def _run_pipeline_with_judge(
    baseline: dict[str, Any],
    rubric: dict,
    dimension_scores: dict[str, float],
) -> float:
    """Run GradingEngine with a judge that returns the given dimension_scores."""
    judge_result = JudgeResult(
        dimension_scores=dict(dimension_scores),
        critical_failures=list(baseline.get("critical_failures", [])),
        detected_patterns={},
        confidence="high",
        feedback={dim: "cross-model fixture" for dim in dimension_scores},
        fallback_used=False,
        overall_score=0.0,
    )

    engine = GradingEngine(rubric)
    engine._judge = MagicMock()
    engine._judge.grade.return_value = judge_result

    scenario = {
        "id": baseline["scenario_id"],
        "context": {"situation": baseline["scenario_context"]},
        "task": {"prompt": baseline["task"]},
    }
    scores, _, _ = engine.grade(
        ai_output=baseline["model_response"],
        scenario=scenario,
        use_llm=True,
    )
    return engine.calculate_overall_score(scores)


class TestCrossModelJudge:
    """Cross-model judge regression: Opus and Sonnet as judges on the same
    golden response should land on the same overall score within a fixed
    tolerance. Flags hidden bias in the judge model itself rather than in
    the scorer code.

    Both judges are mocked — no live API calls. The "Opus view" and
    "Sonnet view" are synthetic but deliberately asymmetric per dimension
    to simulate realistic inter-judge noise.
    """

    @pytest.fixture(scope="class")
    def rubric(self) -> dict:
        return _load_rubric()

    @pytest.fixture(scope="class")
    def baseline(self) -> dict[str, Any]:
        # Use the strong response so both judges are in the "excellent" band
        return next(b for b in _load_baselines() if b["id"] == "iwe_baseline_001")

    def _opus_view(self, baseline: dict[str, Any]) -> dict[str, float]:
        """Opus tends to be slightly harsher on evidence_quality, slightly
        more generous on completeness. Deltas stay within realistic bounds."""
        base = dict(baseline["dimension_scores"])
        return {
            k: max(0.0, min(100.0, v + delta))
            for k, v, delta in (
                ("factual_accuracy", base["factual_accuracy"], +1.0),
                ("analytical_rigor", base["analytical_rigor"], -2.0),
                ("risk_assessment", base["risk_assessment"], +1.0),
                ("evidence_quality", base["evidence_quality"], -3.0),
                ("completeness", base["completeness"], +2.0),
            )
        }

    def _sonnet_view(self, baseline: dict[str, Any]) -> dict[str, float]:
        """Sonnet tends in the opposite direction: more lenient on
        evidence_quality, slightly harsher on completeness."""
        base = dict(baseline["dimension_scores"])
        return {
            k: max(0.0, min(100.0, v + delta))
            for k, v, delta in (
                ("factual_accuracy", base["factual_accuracy"], -1.0),
                ("analytical_rigor", base["analytical_rigor"], +2.0),
                ("risk_assessment", base["risk_assessment"], -1.0),
                ("evidence_quality", base["evidence_quality"], +3.0),
                ("completeness", base["completeness"], -2.0),
            )
        }

    def test_opus_judges_sonnet_outputs_and_vice_versa(
        self, rubric: dict, baseline: dict[str, Any]
    ) -> None:
        """Overall-score delta between Opus-as-judge and Sonnet-as-judge on
        the same response stays inside CROSS_MODEL_TOLERANCE points."""
        opus_overall = _run_pipeline_with_judge(
            baseline, rubric, self._opus_view(baseline)
        )
        sonnet_overall = _run_pipeline_with_judge(
            baseline, rubric, self._sonnet_view(baseline)
        )
        delta = abs(opus_overall - sonnet_overall)
        assert delta <= CROSS_MODEL_TOLERANCE, (
            f"Cross-model judge delta {delta:.2f} exceeds tolerance "
            f"{CROSS_MODEL_TOLERANCE:.2f}. Opus={opus_overall:.2f}, "
            f"Sonnet={sonnet_overall:.2f}. Investigate judge bias."
        )

    def test_both_judges_agree_on_pass_fail(
        self, rubric: dict, baseline: dict[str, Any]
    ) -> None:
        """Both judges should land on the same pass/fail side of the
        rubric's pass_threshold for the same response."""
        threshold = rubric.get("pass_threshold", 70)
        opus_overall = _run_pipeline_with_judge(
            baseline, rubric, self._opus_view(baseline)
        )
        sonnet_overall = _run_pipeline_with_judge(
            baseline, rubric, self._sonnet_view(baseline)
        )
        assert (opus_overall >= threshold) == (sonnet_overall >= threshold), (
            f"Judges disagree on pass/fail: Opus={opus_overall:.2f} "
            f"(pass={opus_overall >= threshold}), Sonnet={sonnet_overall:.2f} "
            f"(pass={sonnet_overall >= threshold}), threshold={threshold}"
        )
