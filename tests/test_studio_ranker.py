"""
Tests for Phase 4A additions to studio/ranker.py:
  - ai_pre_screen()
  - position_presented field in extract_pairwise_preferences()
  - ai_judge_scores field in extract_pairwise_preferences()

All tests mock InvestmentWorkflowJudge to avoid API calls.
"""

from unittest.mock import MagicMock, patch
from typing import List

import pytest

from studio.ranker import ai_pre_screen, extract_pairwise_preferences
from studio.configs import GenerationConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_judge_result(overall: float, dimensions: dict | None = None, confidence: str = "high") -> MagicMock:
    """Return a mock JudgeResult with the given overall score distributed across dimensions."""
    jr = MagicMock()
    jr.dimension_scores = dimensions or {"quality": overall}
    jr.critical_failures = []
    jr.confidence = confidence
    jr.fallback_used = False
    return jr


def _make_configs(labels: List[str]) -> dict:
    """Create minimal GenerationConfig objects keyed by label."""
    configs = {}
    for lbl in labels:
        cfg = GenerationConfig(label=lbl, model="claude-sonnet-4-20250514")
        configs[lbl] = cfg
    return configs


_SCENARIO = {"title": "Test Scenario", "context": "ctx", "task": "task"}
_RUBRIC = {
    "dimensions": [
        {"id": "quality", "name": "Quality", "weight": 1.0, "description": "Overall quality"}
    ]
}


# ---------------------------------------------------------------------------
# Test 1: ai_pre_screen returns one result per response
# ---------------------------------------------------------------------------

def test_pre_screen_returns_result_per_response():
    """3 responses → 3 screening results, one per response_idx."""
    mock_judge = MagicMock()
    mock_judge.grade.side_effect = [
        _make_judge_result(80.0),
        _make_judge_result(60.0),
        _make_judge_result(45.0),
    ]

    responses = ["response A text", "response B text", "response C text"]
    results = ai_pre_screen(
        scenario=_SCENARIO,
        rubric=_RUBRIC,
        responses=responses,
        pass_threshold=70.0,
        _judge=mock_judge,
    )

    assert len(results) == 3
    assert [r["response_idx"] for r in results] == [0, 1, 2]
    assert mock_judge.grade.call_count == 3


# ---------------------------------------------------------------------------
# Test 2: likely_poor_quality flagged True when score < threshold
# ---------------------------------------------------------------------------

def test_likely_poor_quality_flag_below_threshold():
    """Judge returns overall score=45, threshold=70 → likely_poor_quality=True."""
    mock_judge = MagicMock()
    mock_judge.grade.return_value = _make_judge_result(45.0)

    results = ai_pre_screen(
        scenario=_SCENARIO,
        rubric=_RUBRIC,
        responses=["some response"],
        pass_threshold=70.0,
        _judge=mock_judge,
    )

    assert len(results) == 1
    result = results[0]
    assert result["likely_poor_quality"] is True
    assert result["overall_score"] < 70.0


# ---------------------------------------------------------------------------
# Test 3: likely_poor_quality False when score >= threshold
# ---------------------------------------------------------------------------

def test_likely_poor_quality_false_above_threshold():
    """Judge returns overall score=85, threshold=70 → likely_poor_quality=False."""
    mock_judge = MagicMock()
    mock_judge.grade.return_value = _make_judge_result(85.0)

    results = ai_pre_screen(
        scenario=_SCENARIO,
        rubric=_RUBRIC,
        responses=["strong response"],
        pass_threshold=70.0,
        _judge=mock_judge,
    )

    assert len(results) == 1
    result = results[0]
    assert result["likely_poor_quality"] is False
    assert result["overall_score"] >= 70.0


# ---------------------------------------------------------------------------
# Test 4: position_presented field present in extracted pairs
# ---------------------------------------------------------------------------

def test_position_tracking_in_pairs():
    """
    extract_pairwise_preferences with labels_order supplied should populate
    position_presented for each pair.
    """
    labels = ["A", "B", "C"]
    outputs = {lbl: f"text {lbl}" for lbl in labels}
    configs = _make_configs(labels)

    # Rank order: A > C > B (A=best, B=worst)
    ranked = ["A", "C", "B"]

    pairs = extract_pairwise_preferences(
        ranked_labels=ranked,
        outputs=outputs,
        configs_by_label=configs,
        prompt="test prompt",
        source="test",
        tags=[],
        labels_order=labels,  # original display order: A=1, B=2, C=3
    )

    # Should produce C(3,2)=3 pairs
    assert len(pairs) == 3

    # Every pair must have position_presented with chosen and rejected keys
    for pair in pairs:
        assert "position_presented" in pair
        pp = pair["position_presented"]
        assert "chosen" in pp
        assert "rejected" in pp
        # Positions must be 1-indexed integers
        assert isinstance(pp["chosen"], int)
        assert isinstance(pp["rejected"], int)

    # Verify one specific pair: A(pos=1) > C(pos=3)
    ac_pair = next(p for p in pairs if p["chosen"] == outputs["A"] and p["rejected"] == outputs["C"])
    assert ac_pair["position_presented"]["chosen"] == 1   # A is position 1
    assert ac_pair["position_presented"]["rejected"] == 3  # C is position 3


# ---------------------------------------------------------------------------
# Test 5: ai_judge_scores attached to pairs when pre_screen_results provided
# ---------------------------------------------------------------------------

def test_ai_judge_scores_attached_to_pairs():
    """
    When pre_screen_results is provided to extract_pairwise_preferences,
    ai_judge_scores should be populated with the pre-screened scores.
    """
    mock_judge = MagicMock()
    mock_judge.grade.side_effect = [
        _make_judge_result(88.0),
        _make_judge_result(52.0),
    ]

    labels = ["A", "B"]
    outputs = {lbl: f"text {lbl}" for lbl in labels}
    configs = _make_configs(labels)
    responses = [outputs["A"], outputs["B"]]

    # Run pre-screening
    pre_screen = ai_pre_screen(
        scenario=_SCENARIO,
        rubric=_RUBRIC,
        responses=responses,
        pass_threshold=70.0,
        _judge=mock_judge,
    )

    # Extract pairs with pre-screen results attached
    ranked = ["A", "B"]
    pairs = extract_pairwise_preferences(
        ranked_labels=ranked,
        outputs=outputs,
        configs_by_label=configs,
        prompt="test prompt",
        source="test",
        tags=[],
        pre_screen_results=pre_screen,
        labels_order=labels,
    )

    assert len(pairs) == 1
    pair = pairs[0]

    assert "ai_judge_scores" in pair
    ajs = pair["ai_judge_scores"]
    assert "chosen" in ajs
    assert "rejected" in ajs

    # A was scored ~88, B was scored ~52
    assert ajs["chosen"] is not None
    assert ajs["rejected"] is not None
    assert ajs["chosen"] > ajs["rejected"]
