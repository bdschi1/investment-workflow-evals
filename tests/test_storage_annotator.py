"""Tests for studio/storage.py annotator-id schema upgrade."""

from __future__ import annotations

import json
import logging

import pytest

pytest.importorskip("pandas")

from studio import storage  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_warning_flag():
    storage.reset_legacy_warning_flag()
    yield
    storage.reset_legacy_warning_flag()


def _read_jsonl(path):
    out = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# ---------------------------------------------------------------------------
# Required field
# ---------------------------------------------------------------------------


def test_annotator_id_required_missing_raises(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    with pytest.raises(TypeError):
        # annotator_id is a required keyword-only arg; no value -> TypeError.
        storage.save_interaction(
            prompt="p",
            original_ai_response="draft",
            corrected_response="fixed",
            comments="",
            tags=[],
            data_file=data_file,
        )


def test_legacy_annotator_kwarg_raises_helpful_typeerror(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    with pytest.raises(TypeError) as exc:
        storage.save_interaction(
            prompt="p",
            original_ai_response="draft",
            corrected_response="fixed",
            comments="",
            tags=[],
            annotator="Expert_v1",
            data_file=data_file,
        )
    assert "annotator_id" in str(exc.value)


def test_empty_string_annotator_id_raises(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    with pytest.raises(TypeError):
        storage.save_interaction(
            prompt="p",
            original_ai_response="draft",
            corrected_response="fixed",
            comments="",
            tags=[],
            annotator_id="",
            data_file=data_file,
        )


# ---------------------------------------------------------------------------
# Happy path: write + read
# ---------------------------------------------------------------------------


def test_save_and_read_preserves_fields(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    storage.save_interaction(
        prompt="What is EV/EBITDA?",
        original_ai_response="draft text",
        corrected_response="corrected text",
        comments="looks fine",
        tags=["valuation"],
        annotator_id="rater_001",
        annotator_role="grader_senior",
        data_file=data_file,
    )
    records = storage.load_records(data_file)
    assert len(records) == 1
    rec = records[0]
    assert rec["prompt"] == "What is EV/EBITDA?"
    assert rec["chosen"] == "corrected text"
    assert rec["rejected"] == "draft text"
    assert rec["meta"]["annotator_id"] == "rater_001"
    assert rec["meta"]["annotator_role"] == "grader_senior"
    assert rec["meta"]["tags"] == ["valuation"]
    assert "session_id" in rec


def test_annotator_role_optional_defaults_none(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    storage.save_interaction(
        prompt="p",
        original_ai_response="a",
        corrected_response="b",
        comments="c",
        tags=[],
        annotator_id="r1",
        data_file=data_file,
    )
    records = storage.load_records(data_file)
    assert records[0]["meta"]["annotator_role"] is None


def test_multiple_annotators_same_file_retain_ids(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    for rid in ["rA", "rB", "rC"]:
        storage.save_interaction(
            prompt=f"q for {rid}",
            original_ai_response="draft",
            corrected_response="fixed",
            comments="",
            tags=[],
            annotator_id=rid,
            data_file=data_file,
        )
    records = storage.load_records(data_file)
    assert [r["meta"]["annotator_id"] for r in records] == ["rA", "rB", "rC"]


def test_session_id_accepted_when_provided(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    storage.save_interaction(
        prompt="p",
        original_ai_response="a",
        corrected_response="b",
        comments="",
        tags=[],
        annotator_id="r1",
        session_id="fixed-session-123",
        data_file=data_file,
    )
    records = storage.load_records(data_file)
    assert records[0]["session_id"] == "fixed-session-123"


# ---------------------------------------------------------------------------
# Backward compatibility: legacy records
# ---------------------------------------------------------------------------


def test_legacy_record_upgraded_on_read(tmp_path, caplog):
    """Legacy shape: meta.annotator = 'Expert_v1', no annotator_id."""
    data_file = str(tmp_path / "legacy.jsonl")
    legacy_entry = {
        "timestamp": "2026-01-01T00:00:00",
        "prompt": "legacy prompt",
        "chosen": "good",
        "rejected": "bad",
        "meta": {
            "comments": "legacy record",
            "tags": [],
            "annotator": "Expert_v1",
        },
    }
    with open(data_file, "w") as f:
        f.write(json.dumps(legacy_entry) + "\n")

    with caplog.at_level(logging.WARNING, logger="studio.storage"):
        records = storage.load_records(data_file)

    assert len(records) == 1
    assert records[0]["meta"]["annotator_id"] == "Expert_v1"
    assert records[0]["meta"]["annotator_role"] is None
    assert any("Legacy record" in msg for msg in caplog.messages)


def test_legacy_warning_emitted_only_once(tmp_path, caplog):
    data_file = str(tmp_path / "legacy.jsonl")
    legacy = {
        "timestamp": "2026-01-01T00:00:00",
        "prompt": "p",
        "chosen": "g",
        "rejected": "b",
        "meta": {"comments": "", "tags": [], "annotator": "Expert_v1"},
    }
    with open(data_file, "w") as f:
        for _ in range(4):
            f.write(json.dumps(legacy) + "\n")

    with caplog.at_level(logging.WARNING, logger="studio.storage"):
        records = storage.load_records(data_file)

    assert len(records) == 4
    warnings = [m for m in caplog.messages if "Legacy record" in m]
    assert len(warnings) == 1


def test_legacy_record_missing_session_id_backfilled(tmp_path):
    data_file = str(tmp_path / "legacy.jsonl")
    legacy = {
        "timestamp": "2026-01-01T00:00:00",
        "prompt": "p",
        "chosen": "g",
        "rejected": "b",
        "meta": {"comments": "", "tags": [], "annotator": "Expert_v1"},
    }
    with open(data_file, "w") as f:
        f.write(json.dumps(legacy) + "\n")

    records = storage.load_records(data_file)
    assert "session_id" in records[0]
    assert records[0]["session_id"]  # non-empty


def test_mixed_legacy_and_new_records(tmp_path):
    data_file = str(tmp_path / "mixed.jsonl")
    # Write one legacy record.
    legacy = {
        "timestamp": "2026-01-01T00:00:00",
        "prompt": "old",
        "chosen": "g",
        "rejected": "b",
        "meta": {"comments": "", "tags": [], "annotator": "Expert_v1"},
    }
    with open(data_file, "w") as f:
        f.write(json.dumps(legacy) + "\n")

    # Append new record via API.
    storage.save_interaction(
        prompt="new",
        original_ai_response="d",
        corrected_response="c",
        comments="",
        tags=[],
        annotator_id="rater_new",
        annotator_role="reviewer",
        data_file=data_file,
    )
    records = storage.load_records(data_file)
    assert len(records) == 2
    assert records[0]["meta"]["annotator_id"] == "Expert_v1"
    assert records[1]["meta"]["annotator_id"] == "rater_new"
    assert records[1]["meta"]["annotator_role"] == "reviewer"


# ---------------------------------------------------------------------------
# load_stats compatibility
# ---------------------------------------------------------------------------


def test_load_stats_handles_missing_file(tmp_path):
    data_file = str(tmp_path / "nope.jsonl")
    count, df = storage.load_stats(data_file)
    assert count == 0
    assert df.empty


def test_load_stats_after_write(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    storage.save_interaction(
        prompt="p",
        original_ai_response="a",
        corrected_response="b",
        comments="",
        tags=[],
        annotator_id="r1",
        data_file=data_file,
    )
    count, df = storage.load_stats(data_file)
    assert count == 1
    assert len(df) == 1


def test_unexpected_kwarg_rejected(tmp_path):
    data_file = str(tmp_path / "ds.jsonl")
    with pytest.raises(TypeError):
        storage.save_interaction(
            prompt="p",
            original_ai_response="a",
            corrected_response="b",
            comments="",
            tags=[],
            annotator_id="r1",
            not_a_real_field="oops",
            data_file=data_file,
        )
