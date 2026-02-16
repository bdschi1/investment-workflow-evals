"""Smoke tests for the RLHF Studio package (ported from financial-rlhf-studio)."""

import os
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_studio_directory_exists():
    """studio/ package directory exists."""
    assert (REPO_ROOT / "studio").is_dir()


def test_studio_files_present():
    """All expected studio module files are present."""
    expected = [
        "__init__.py",
        "app.py",
        "configs.py",
        "generator.py",
        "ranker.py",
        "document.py",
        "storage.py",
    ]
    for fname in expected:
        assert (REPO_ROOT / "studio" / fname).exists(), f"Missing studio/{fname}"


def test_preference_pair_schema_exists():
    """Unified preference pair JSON schema exists and is valid JSON."""
    schema_path = REPO_ROOT / "schemas" / "preference_pair.json"
    assert schema_path.exists()
    data = json.loads(schema_path.read_text())
    assert "prompt" in data["required"]
    assert "chosen" in data["required"]
    assert "rejected" in data["required"]


def test_import_configs():
    """studio.configs module imports correctly."""
    from studio.configs import GenerationConfig, PRESETS  # noqa: F401
    from studio.configs import provider_for_model

    assert provider_for_model("claude-sonnet-4-20250514") == "anthropic"
    assert provider_for_model("gemini-2.0-flash") == "gemini"
    assert provider_for_model("gpt-4o-mini") == "openai"


def test_import_ranker():
    """studio.ranker module imports correctly."""
    from studio.ranker import extract_pairwise_preferences, count_pairs  # noqa: F401


def test_count_pairs():
    """K(K-1)/2 formula is correct."""
    from studio.ranker import count_pairs

    assert count_pairs(2) == 1
    assert count_pairs(3) == 3
    assert count_pairs(4) == 6
    assert count_pairs(5) == 10
    assert count_pairs(9) == 36


def test_extract_pairwise_preferences():
    """extract_pairwise_preferences produces correct number of pairs."""
    from studio.configs import GenerationConfig
    from studio.ranker import extract_pairwise_preferences

    configs = {
        "A": GenerationConfig(label="A", model="gpt-4o-mini"),
        "B": GenerationConfig(label="B", model="gpt-4o-mini"),
        "C": GenerationConfig(label="C", model="gpt-4o-mini"),
    }
    outputs = {
        "A": "Output A text",
        "B": "Output B text",
        "C": "Output C text",
    }

    pairs = extract_pairwise_preferences(
        ranked_labels=["A", "B", "C"],
        outputs=outputs,
        configs_by_label=configs,
        prompt="Analyze this",
        source="studio_ranking",
        tags=["test"],
    )

    # K=3 → 3 pairs
    assert len(pairs) == 3

    # Check structure of first pair
    pair = pairs[0]
    assert pair["prompt"] == "Analyze this"
    assert pair["chosen"] == "Output A text"
    assert pair["rejected"] == "Output B text"
    assert pair["source"] == "studio_ranking"
    assert pair["mode"] == "ranking"
    assert pair["ranking_metadata"]["rank_margin"] == 1


def test_generation_config_dataclass():
    """GenerationConfig has expected fields and methods."""
    from studio.configs import GenerationConfig

    cfg = GenerationConfig(label="X", model="claude-sonnet-4-20250514", temperature=0.5)
    assert cfg.provider == "anthropic"
    assert cfg.label == "X"

    d = cfg.to_dict()
    assert d["model"] == "claude-sonnet-4-20250514"
    assert d["temperature"] == 0.5
    assert d["provider"] == "anthropic"
