"""Tests for the GRPO-aligned reward signal module."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


# ── Import tests ──────────────────────────────────────────────────────────

def test_import_rewards():
    """studio.rewards module imports correctly."""
    from studio.rewards import (  # noqa: F401
        RewardSignal,
        compute_reward,
        annotate_pair_with_rewards,
    )


def test_rewards_file_exists():
    """studio/rewards.py exists."""
    assert (REPO_ROOT / "studio" / "rewards.py").exists()


# ── RewardSignal dataclass ────────────────────────────────────────────────

class TestRewardSignal:
    def test_default_values(self):
        from studio.rewards import RewardSignal
        r = RewardSignal()
        assert r.accuracy == 0.5
        assert r.logic == 0.5
        assert r.format_quality == 0.5
        assert r.length == 0.5

    def test_composite_default_weights(self):
        from studio.rewards import RewardSignal
        r = RewardSignal(accuracy=1.0, logic=1.0, format_quality=1.0, length=1.0)
        # r = 0.4*1 + 0.3*1 + 0.15*1 + 0.15*(1*1) = 1.0
        assert r.composite() == pytest.approx(1.0)

    def test_composite_zero(self):
        from studio.rewards import RewardSignal
        r = RewardSignal(accuracy=0.0, logic=0.0, format_quality=0.0, length=0.0)
        assert r.composite() == pytest.approx(0.0)

    def test_length_gated_by_accuracy(self):
        """Length reward is multiplied by accuracy — verbose wrong answers score low."""
        from studio.rewards import RewardSignal
        # Good length but zero accuracy: length contribution should be 0
        r = RewardSignal(accuracy=0.0, logic=0.5, format_quality=0.5, length=1.0)
        composite = r.composite()
        # 0.4*0 + 0.3*0.5 + 0.15*0.5 + 0.15*(1.0*0.0) = 0.15 + 0.075 = 0.225
        assert composite == pytest.approx(0.225)

    def test_composite_custom_weights(self):
        from studio.rewards import RewardSignal
        r = RewardSignal(accuracy=0.8, logic=0.6, format_quality=0.4, length=0.9)
        # Equal weights: 0.25 each
        score = r.composite(
            alpha_acc=0.25, alpha_logic=0.25,
            alpha_format=0.25, alpha_length=0.25,
        )
        # 0.25*0.8 + 0.25*0.6 + 0.25*0.4 + 0.25*(0.9*0.8)
        # = 0.2 + 0.15 + 0.1 + 0.25*0.72 = 0.2 + 0.15 + 0.1 + 0.18 = 0.63
        assert score == pytest.approx(0.63)

    def test_to_dict(self):
        from studio.rewards import RewardSignal
        r = RewardSignal(accuracy=0.8, logic=0.7, format_quality=0.6, length=0.9)
        d = r.to_dict()
        assert "accuracy" in d
        assert "logic" in d
        assert "format_quality" in d
        assert "length" in d
        assert "composite" in d
        assert "explanations" in d
        assert isinstance(d["composite"], float)

    def test_composite_in_zero_one(self):
        """Composite should always be in [0, 1] for valid inputs."""
        from studio.rewards import RewardSignal
        import random
        random.seed(42)
        for _ in range(50):
            r = RewardSignal(
                accuracy=random.random(),
                logic=random.random(),
                format_quality=random.random(),
                length=random.random(),
            )
            assert 0.0 <= r.composite() <= 1.0


# ── Heuristic reward functions ────────────────────────────────────────────

class TestAccuracy:
    def test_neutral_without_reference(self):
        from studio.rewards import compute_accuracy
        assert compute_accuracy("Some analysis text") == 0.5

    def test_perfect_overlap(self):
        from studio.rewards import compute_accuracy
        ref = "revenue growth margin ebitda"
        assert compute_accuracy(ref, ref) == pytest.approx(1.0, abs=0.01)

    def test_partial_overlap(self):
        from studio.rewards import compute_accuracy
        ref = "revenue growth margin ebitda"
        text = "revenue growth but not the rest of the words"
        score = compute_accuracy(text, ref)
        assert 0.0 < score < 1.0

    def test_no_overlap(self):
        from studio.rewards import compute_accuracy
        ref = "alpha beta gamma delta"
        text = "xyz uvw rst qpo"
        score = compute_accuracy(text, ref)
        assert score < 0.2


class TestLogic:
    def test_empty_text(self):
        from studio.rewards import compute_logic
        assert compute_logic("") == 0.0

    def test_high_logic_density(self):
        from studio.rewards import compute_logic
        text = (
            "Because revenue grew 15%, therefore EBITDA expanded. "
            "Given the margin improvement, thus FCF increased. "
            "Since costs were controlled, assuming no one-time items, "
            "the results imply sustainable growth."
        )
        score = compute_logic(text)
        assert score > 0.5

    def test_numbered_steps_bonus(self):
        from studio.rewards import compute_logic
        text = (
            "1. First, we analyze revenue growth because of market expansion.\n"
            "2. Then, we assess margins therefore calculating EBITDA.\n"
            "3. Finally, we evaluate FCF since capex is stable."
        )
        score = compute_logic(text)
        assert score > 0.5


class TestFormat:
    def test_empty_text(self):
        from studio.rewards import compute_format
        assert compute_format("") == 0.0

    def test_structured_output(self):
        from studio.rewards import compute_format
        text = (
            "## Revenue Analysis\n\n"
            "- Revenue grew 15% YoY\n"
            "- Margins expanded 200bps\n\n"
            "## Risk Factors\n\n"
            "1. Competition increasing\n"
            "2. Regulatory overhang\n"
        )
        score = compute_format(text)
        assert score > 0.4

    def test_unstructured_wall_of_text(self):
        from studio.rewards import compute_format
        text = "Word " * 200  # monotone wall of text
        score = compute_format(text)
        assert score < 0.5


class TestLength:
    def test_ideal_range(self):
        from studio.rewards import compute_length
        text = " ".join(["word"] * 300)
        assert compute_length(text) == 1.0

    def test_too_short(self):
        from studio.rewards import compute_length
        text = " ".join(["word"] * 50)
        score = compute_length(text)
        assert score < 1.0

    def test_too_long(self):
        from studio.rewards import compute_length
        text = " ".join(["word"] * 1200)
        score = compute_length(text)
        assert score < 1.0

    def test_minimum_floor(self):
        from studio.rewards import compute_length
        assert compute_length("short") >= 0.1


# ── compute_reward integration ────────────────────────────────────────────

class TestComputeReward:
    def test_heuristic_mode(self):
        from studio.rewards import compute_reward
        text = (
            "## Analysis\n\n"
            "Because revenue grew 15%, therefore the company is improving. "
            "Given these factors, we recommend a BUY.\n\n"
            "## Risks\n\n"
            "- Competition is increasing\n"
            "- Regulatory uncertainty"
        )
        r = compute_reward(text, prompt="Analyze this stock")
        assert r.explanations["source"] == "heuristic"
        assert 0.0 <= r.composite() <= 1.0

    def test_rubric_mode(self):
        from studio.rewards import compute_reward
        rubric = {
            "accuracy": 85,
            "logic": 70,
            "format_quality": 90,
            "length": 80,
        }
        r = compute_reward("any text", rubric_scores=rubric)
        assert r.explanations["source"] == "rubric_scores"
        assert r.accuracy == pytest.approx(0.85)
        assert r.logic == pytest.approx(0.70)

    def test_with_reference(self):
        from studio.rewards import compute_reward
        ref = "The WACC of 10.5% is too low for a pre-revenue biotech company"
        text = "The WACC is too low at 10.5% given the pre-revenue biotech profile"
        r = compute_reward(text, reference=ref)
        assert r.accuracy > 0.5  # Should have decent overlap


# ── annotate_pair_with_rewards ────────────────────────────────────────────

class TestAnnotatePair:
    def test_adds_scores(self):
        from studio.rewards import annotate_pair_with_rewards
        pair = {
            "prompt": "Analyze revenue growth",
            "chosen": (
                "## Revenue Analysis\n\n"
                "Because organic growth accelerated, therefore revenue increased 15%. "
                "Given the market expansion and margin improvement, the outlook is positive."
            ),
            "rejected": "Revenue went up.",
        }
        result = annotate_pair_with_rewards(pair)
        assert "chosen_score" in result
        assert "rejected_score" in result
        assert "reward_details" in result
        assert result["reward_details"]["reward_type"] == "grpo_multifaceted"

    def test_chosen_scores_higher(self):
        """A well-structured chosen response should score higher than a terse rejection."""
        from studio.rewards import annotate_pair_with_rewards
        pair = {
            "prompt": "Evaluate the DCF model assumptions",
            "chosen": (
                "## Assumption Review\n\n"
                "1. Because the WACC of 10.5% uses a large-cap beta, therefore it understates risk.\n"
                "2. Given the 14-month cash runway, the model should assume dilution.\n"
                "3. Since PoA is not probability-weighted, thus revenue is overstated.\n\n"
                "## Sensitivity\n\n"
                "- At 14% WACC: NPV drops 37%\n"
                "- At 60% PoA: revenue halves\n"
            ),
            "rejected": "The assumptions look fine to me.",
        }
        result = annotate_pair_with_rewards(pair)
        assert result["chosen_score"] > result["rejected_score"]

    def test_preserves_existing_fields(self):
        from studio.rewards import annotate_pair_with_rewards
        pair = {
            "prompt": "Test",
            "chosen": "Good answer with some detail and reasoning.",
            "rejected": "Bad.",
            "tags": ["test"],
            "source": "studio_ranking",
        }
        result = annotate_pair_with_rewards(pair)
        assert result["tags"] == ["test"]
        assert result["source"] == "studio_ranking"


# ── Assumption validation eval module exists ──────────────────────────────

class TestAssumptionValidationModule:
    def test_directory_exists(self):
        path = REPO_ROOT / "evals" / "04_assumption_validation"
        assert path.is_dir()

    def test_rubric_exists(self):
        path = REPO_ROOT / "evals" / "04_assumption_validation" / "rubrics" / "assumption_validation.yaml"
        assert path.exists()

    def test_scenario_exists(self):
        scenarios = REPO_ROOT / "evals" / "04_assumption_validation" / "scenarios"
        assert scenarios.is_dir()
        yamls = list(scenarios.glob("*.yaml"))
        assert len(yamls) >= 1

    def test_golden_answer_exists(self):
        goldens = REPO_ROOT / "evals" / "04_assumption_validation" / "golden_answers"
        assert goldens.is_dir()
        mds = list(goldens.glob("*.md"))
        assert len(mds) >= 1

    def test_rubric_has_five_dimensions(self):
        import yaml
        path = REPO_ROOT / "evals" / "04_assumption_validation" / "rubrics" / "assumption_validation.yaml"
        with open(path) as f:
            rubric = yaml.safe_load(f)
        assert len(rubric["dimensions"]) == 5
        ids = {d["id"] for d in rubric["dimensions"]}
        assert ids == {"extraction", "reasonableness", "sensitivity", "red_flags", "alternatives"}

    def test_rubric_weights_sum_to_100(self):
        import yaml
        path = REPO_ROOT / "evals" / "04_assumption_validation" / "rubrics" / "assumption_validation.yaml"
        with open(path) as f:
            rubric = yaml.safe_load(f)
        total = sum(d["weight"] for d in rubric["dimensions"])
        assert total == 100
