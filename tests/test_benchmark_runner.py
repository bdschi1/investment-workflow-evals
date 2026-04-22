"""Tests for tools/benchmark_runner.py live-generation path.

All provider SDKs are mocked via unittest.mock — no real network calls.
"""

from __future__ import annotations

import io
import subprocess
import sys
import types
from pathlib import Path
from unittest import mock

import pytest

from tools import benchmark_runner as br

# ---------------------------------------------------------------------------
# Helpers: fake response objects for each provider SDK
# ---------------------------------------------------------------------------


def _make_anthropic_response(
    text: str = "analyst response",
    stop_reason: str = "end_turn",
    input_tokens: int = 120,
    output_tokens: int = 80,
    cache_read: int = 0,
):
    block = types.SimpleNamespace(type="text", text=text)
    usage = types.SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read,
    )
    return types.SimpleNamespace(
        content=[block],
        stop_reason=stop_reason,
        usage=usage,
    )


def _make_openai_response(
    text: str = "analyst response",
    finish_reason: str = "stop",
    refusal: str | None = None,
    prompt_tokens: int = 100,
    completion_tokens: int = 50,
):
    message = types.SimpleNamespace(content=text, refusal=refusal)
    choice = types.SimpleNamespace(message=message, finish_reason=finish_reason)
    usage = types.SimpleNamespace(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
    )
    return types.SimpleNamespace(choices=[choice], usage=usage)


def _make_gemini_response(
    text: str = "analyst response",
    finish_reason_name: str = "STOP",
    prompt_token_count: int = 90,
    candidates_token_count: int = 60,
):
    finish = types.SimpleNamespace(name=finish_reason_name)
    candidate = types.SimpleNamespace(finish_reason=finish)
    usage = types.SimpleNamespace(
        prompt_token_count=prompt_token_count,
        candidates_token_count=candidates_token_count,
    )
    return types.SimpleNamespace(
        text=text,
        candidates=[candidate],
        usage_metadata=usage,
    )


SCENARIO_FIXTURE = {
    "id": "test_scenario",
    "title": "Test Scenario",
    "context": {
        "company": {"name": "TestCo", "ticker": "TEST", "sector": "Tech"},
        "situation": "Hypothetical test situation.",
        "market_conditions": "Calm market.",
        "as_of_date": "2026-01-01",
    },
    "task": {
        "prompt": "Assess the thesis.",
        "constraints": "Brief.",
        "time_horizon": "12 months",
    },
}


# ---------------------------------------------------------------------------
# Provider dispatch + prompt shape
# ---------------------------------------------------------------------------


def test_provider_dispatch_claude_routes_to_anthropic():
    with mock.patch.object(br, "_generate_anthropic") as gen_anth, mock.patch.object(
        br, "_generate_openai"
    ) as gen_oai, mock.patch.object(br, "_generate_gemini") as gen_gem:
        gen_anth.return_value = (
            "hello from claude",
            br.UsageMeta(100, 50, 10, "end_turn"),
        )
        text, usage = br._live_candidate("claude-opus-4-7", SCENARIO_FIXTURE)
        gen_anth.assert_called_once()
        gen_oai.assert_not_called()
        gen_gem.assert_not_called()
        assert text == "hello from claude"
        assert usage["input_tokens"] == 100
        assert usage["output_tokens"] == 50
        assert usage["cache_hit_tokens"] == 10
        assert usage["stop_reason"] == "end_turn"


def test_provider_dispatch_gpt_routes_to_openai():
    with mock.patch.object(br, "_generate_anthropic") as gen_anth, mock.patch.object(
        br, "_generate_openai"
    ) as gen_oai, mock.patch.object(br, "_generate_gemini") as gen_gem:
        gen_oai.return_value = ("hello from gpt", br.UsageMeta(80, 40, 0, "stop"))
        text, usage = br._live_candidate("gpt-5", SCENARIO_FIXTURE)
        gen_oai.assert_called_once()
        gen_anth.assert_not_called()
        gen_gem.assert_not_called()
        assert text == "hello from gpt"
        assert usage["cache_hit_tokens"] == 0


def test_provider_dispatch_gemini_routes_to_google():
    with mock.patch.object(br, "_generate_anthropic") as gen_anth, mock.patch.object(
        br, "_generate_openai"
    ) as gen_oai, mock.patch.object(br, "_generate_gemini") as gen_gem:
        gen_gem.return_value = ("hello from gemini", br.UsageMeta(70, 30, 0, "STOP"))
        text, _ = br._live_candidate("gemini-2.5-pro", SCENARIO_FIXTURE)
        gen_gem.assert_called_once()
        gen_anth.assert_not_called()
        gen_oai.assert_not_called()
        assert text == "hello from gemini"


def test_unknown_model_prefix_raises_clear_error():
    with pytest.raises(ValueError) as exc_info:
        br._live_candidate("mistral-large", SCENARIO_FIXTURE)
    assert "Unknown model SKU prefix" in str(exc_info.value)
    assert "claude-*" in str(exc_info.value)


def test_analyst_prompt_does_not_leak_rubric_dimensions():
    """Prompt must not include evaluation_criteria or rubric structure."""
    scenario = dict(SCENARIO_FIXTURE)
    scenario["evaluation_criteria"] = {
        "factual_accuracy": {"weight": 0.3},
        "risk_classification": {"weight": 0.4},
    }
    system, user = br._build_analyst_prompt(scenario)
    combined = (system + "\n" + user).lower()
    assert "evaluation_criteria" not in combined
    assert "factual_accuracy" not in combined
    assert "weight" not in combined


# ---------------------------------------------------------------------------
# Anthropic provider — prompt caching + stop-reason handling
# ---------------------------------------------------------------------------


def test_anthropic_enables_prompt_caching_on_system_block():
    fake_client = mock.MagicMock()
    fake_client.messages.create.return_value = _make_anthropic_response(cache_read=300)
    fake_module = types.SimpleNamespace(
        Anthropic=lambda: fake_client, RateLimitError=type("RL", (Exception,), {})
    )
    with mock.patch.dict(sys.modules, {"anthropic": fake_module}):
        text, meta = br._generate_anthropic(
            "claude-opus-4-7", "system prompt", "user prompt", max_tokens=1024
        )
    call_kwargs = fake_client.messages.create.call_args.kwargs
    # System must be a list with cache_control ephemeral on the text block
    assert isinstance(call_kwargs["system"], list)
    assert call_kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}
    # No sampling params on Opus 4.7 — omit temperature/top_p/top_k
    for banned in ("temperature", "top_p", "top_k", "thinking"):
        assert banned not in call_kwargs
    # Usage dict folds cache read into total input tokens
    assert meta.input_tokens == 120 + 300
    assert meta.cache_hit_tokens == 300
    assert text == "analyst response"


def test_anthropic_refusal_returns_sentinel():
    fake_client = mock.MagicMock()
    fake_client.messages.create.return_value = _make_anthropic_response(
        text="I cannot help with that.", stop_reason="refusal"
    )
    fake_module = types.SimpleNamespace(
        Anthropic=lambda: fake_client, RateLimitError=type("RL", (Exception,), {})
    )
    with mock.patch.dict(sys.modules, {"anthropic": fake_module}):
        text, meta = br._generate_anthropic(
            "claude-opus-4-7", "sys", "usr", max_tokens=512
        )
    assert text == br.REFUSAL_SENTINEL
    assert meta.stop_reason == "refusal"
    # Usage metadata preserved even on refusal
    assert meta.input_tokens == 120
    assert meta.output_tokens == 80


def test_anthropic_context_exceeded_returns_sentinel():
    fake_client = mock.MagicMock()
    fake_client.messages.create.return_value = _make_anthropic_response(
        stop_reason="model_context_window_exceeded"
    )
    fake_module = types.SimpleNamespace(
        Anthropic=lambda: fake_client, RateLimitError=type("RL", (Exception,), {})
    )
    with mock.patch.dict(sys.modules, {"anthropic": fake_module}):
        text, meta = br._generate_anthropic(
            "claude-opus-4-7", "sys", "usr", max_tokens=512
        )
    assert text == br.CONTEXT_EXCEEDED_SENTINEL
    assert meta.stop_reason == "model_context_window_exceeded"


def test_anthropic_rate_limit_retry_then_success():
    class FakeRateLimitError(Exception):
        status_code = 429

    call_count = {"n": 0}

    def flaky_create(**_kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise FakeRateLimitError("429 Too Many Requests")
        return _make_anthropic_response(text="finally", stop_reason="end_turn")

    fake_client = mock.MagicMock()
    fake_client.messages.create.side_effect = flaky_create
    fake_module = types.SimpleNamespace(
        Anthropic=lambda: fake_client, RateLimitError=FakeRateLimitError
    )
    with mock.patch.dict(sys.modules, {"anthropic": fake_module}), mock.patch.object(
        br.time, "sleep"
    ) as sleeper:
        text, _ = br._generate_anthropic(
            "claude-opus-4-7", "sys", "usr", max_tokens=512
        )
    assert text == "finally"
    assert call_count["n"] == 3
    # Three retries: first failure triggers 2s sleep, second triggers 4s sleep
    assert sleeper.call_count == 2
    assert sleeper.call_args_list[0].args[0] == 2.0
    assert sleeper.call_args_list[1].args[0] == 4.0


def test_anthropic_non_rate_limit_error_propagates():
    class OtherError(Exception):
        pass

    fake_client = mock.MagicMock()
    fake_client.messages.create.side_effect = OtherError("boom")
    fake_module = types.SimpleNamespace(
        Anthropic=lambda: fake_client,
        RateLimitError=type("RL", (Exception,), {}),
    )
    with mock.patch.dict(sys.modules, {"anthropic": fake_module}):
        with pytest.raises(OtherError):
            br._generate_anthropic("claude-opus-4-7", "sys", "usr", max_tokens=512)


# ---------------------------------------------------------------------------
# OpenAI provider
# ---------------------------------------------------------------------------


def test_openai_refusal_via_message_refusal_returns_sentinel():
    fake_client = mock.MagicMock()
    fake_client.chat.completions.create.return_value = _make_openai_response(
        text="", refusal="I cannot assist with that."
    )
    fake_module = types.SimpleNamespace(
        OpenAI=lambda: fake_client, RateLimitError=type("RL", (Exception,), {})
    )
    with mock.patch.dict(sys.modules, {"openai": fake_module}):
        text, meta = br._generate_openai("gpt-5", "sys", "usr", max_tokens=1024)
    assert text == br.REFUSAL_SENTINEL
    assert meta.input_tokens == 100


def test_openai_content_filter_returns_sentinel():
    fake_client = mock.MagicMock()
    fake_client.chat.completions.create.return_value = _make_openai_response(
        text="", finish_reason="content_filter"
    )
    fake_module = types.SimpleNamespace(
        OpenAI=lambda: fake_client, RateLimitError=type("RL", (Exception,), {})
    )
    with mock.patch.dict(sys.modules, {"openai": fake_module}):
        text, _ = br._generate_openai("gpt-5", "sys", "usr", max_tokens=1024)
    assert text == br.REFUSAL_SENTINEL


def test_openai_rate_limit_retry_with_retries_exhausted():
    class FakeRateLimitError(Exception):
        status_code = 429

    fake_client = mock.MagicMock()
    fake_client.chat.completions.create.side_effect = FakeRateLimitError("429")
    fake_module = types.SimpleNamespace(
        OpenAI=lambda: fake_client, RateLimitError=FakeRateLimitError
    )
    with mock.patch.dict(sys.modules, {"openai": fake_module}), mock.patch.object(
        br.time, "sleep"
    ):
        with pytest.raises(FakeRateLimitError):
            br._generate_openai("gpt-5", "sys", "usr", max_tokens=512)
    # Initial call + three retries = four invocations total
    assert fake_client.chat.completions.create.call_count == 4


# ---------------------------------------------------------------------------
# Gemini provider
# ---------------------------------------------------------------------------


def test_gemini_uses_google_genai_client():
    fake_client = mock.MagicMock()
    fake_client.models.generate_content.return_value = _make_gemini_response(
        text="gemini says hi"
    )
    fake_genai = types.SimpleNamespace(Client=lambda api_key=None: fake_client)
    fake_types = types.SimpleNamespace(
        GenerateContentConfig=lambda **kw: types.SimpleNamespace(**kw)
    )
    fake_google = types.ModuleType("google")
    fake_google_genai = types.ModuleType("google.genai")
    fake_google_genai_types = types.ModuleType("google.genai.types")
    fake_google_genai.Client = fake_genai.Client
    fake_google_genai_types.GenerateContentConfig = fake_types.GenerateContentConfig
    fake_google.genai = fake_google_genai
    with mock.patch.dict(
        sys.modules,
        {
            "google": fake_google,
            "google.genai": fake_google_genai,
            "google.genai.types": fake_google_genai_types,
        },
    ):
        text, meta = br._generate_gemini(
            "gemini-2.5-pro", "sys", "usr", max_tokens=2048
        )
    assert text == "gemini says hi"
    assert meta.input_tokens == 90
    assert meta.output_tokens == 60
    assert meta.stop_reason == "STOP"


def test_gemini_safety_block_returns_refusal_sentinel():
    fake_client = mock.MagicMock()
    fake_client.models.generate_content.return_value = _make_gemini_response(
        text="", finish_reason_name="SAFETY"
    )
    fake_google = types.ModuleType("google")
    fake_google_genai = types.ModuleType("google.genai")
    fake_google_genai_types = types.ModuleType("google.genai.types")
    fake_google_genai.Client = lambda api_key=None: fake_client
    fake_google_genai_types.GenerateContentConfig = lambda **kw: types.SimpleNamespace(
        **kw
    )
    fake_google.genai = fake_google_genai
    with mock.patch.dict(
        sys.modules,
        {
            "google": fake_google,
            "google.genai": fake_google_genai,
            "google.genai.types": fake_google_genai_types,
        },
    ):
        text, meta = br._generate_gemini(
            "gemini-2.5-pro", "sys", "usr", max_tokens=2048
        )
    assert text == br.REFUSAL_SENTINEL
    assert meta.stop_reason == "SAFETY"


def test_gemini_missing_sdk_raises_runtime_error():
    # Make importing google.genai fail to simulate missing package
    with mock.patch.dict(sys.modules, {"google.genai": None}):
        with pytest.raises(RuntimeError) as exc:
            br._generate_gemini("gemini-2.5-pro", "sys", "usr", max_tokens=512)
    assert "google-generativeai" in str(exc.value)


# ---------------------------------------------------------------------------
# CLI: --yes-live gate, --estimate-cost, dry-run still works
# ---------------------------------------------------------------------------


def _venv_python() -> str:
    """Locate the venv python so subprocess tests pick up installed deps."""
    repo_root = Path(__file__).resolve().parent.parent
    venv_py = repo_root / ".venv" / "bin" / "python"
    return str(venv_py) if venv_py.exists() else sys.executable


def test_yes_live_gate_refuses_without_flag():
    """--generator live without --yes-live must not write rows."""
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            _venv_python(),
            "-m",
            "tools.benchmark_runner",
            "--modules",
            "01_equity_thesis",
            "--generator",
            "live",
            "--models",
            "claude-haiku-4-5-20251001",
            "--scenarios",
            "1",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    combined = result.stdout + result.stderr
    assert "Refusing to run live-frontier generation without --yes-live" in combined


def test_estimate_cost_output_parses():
    """--estimate-cost prints a table with module/model/est_usd lines."""
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            _venv_python(),
            "-m",
            "tools.benchmark_runner",
            "--modules",
            "01_equity_thesis",
            "--models",
            "claude-opus-4-7,gpt-5",
            "--scenarios",
            "1",
            "--estimate-cost",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "module" in result.stdout
    assert "est_usd" in result.stdout
    assert "TOTAL (est)" in result.stdout
    assert "claude-opus-4-7" in result.stdout
    assert "gpt-5" in result.stdout


def test_help_advertises_estimate_cost_flag():
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [_venv_python(), "-m", "tools.benchmark_runner", "--help"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "--estimate-cost" in result.stdout


# ---------------------------------------------------------------------------
# Cost estimation aggregation
# ---------------------------------------------------------------------------


def test_estimate_cost_aggregation_uses_rate_card():
    rows = [
        (
            "01_equity_thesis",
            "claude-opus-4-7",
            {
                "input_tokens": 1_000_000,
                "output_tokens": 500_000,
                "cache_hit_tokens": 0,
            },
        ),
        (
            "01_equity_thesis",
            "claude-opus-4-7",
            {"input_tokens": 500_000, "output_tokens": 200_000, "cache_hit_tokens": 0},
        ),
        (
            "02_competitive_analysis",
            "gpt-5",
            {"input_tokens": 100_000, "output_tokens": 50_000, "cache_hit_tokens": 0},
        ),
    ]
    agg = br._estimate_cost_from_usage(rows)
    opus_bucket = agg[("01_equity_thesis", "claude-opus-4-7")]
    # Opus 4.7: 1.5M input @ $5 + 0.7M output @ $25 = $7.50 + $17.50 = $25.00
    assert opus_bucket["input_tokens"] == 1_500_000
    assert opus_bucket["output_tokens"] == 700_000
    assert opus_bucket["est_usd"] == pytest.approx(7.5 + 17.5)
    gpt_bucket = agg[("02_competitive_analysis", "gpt-5")]
    # GPT-5: 100k input @ $0.625 + 50k output @ $5 = $0.0625 + $0.25 = $0.3125
    assert gpt_bucket["est_usd"] == pytest.approx(0.0625 + 0.25)


def test_estimate_cost_unknown_sku_uses_fallback_rate():
    rows = [
        (
            "mod",
            "unknown-model-xyz",
            {
                "input_tokens": 1_000_000,
                "output_tokens": 1_000_000,
                "cache_hit_tokens": 0,
            },
        )
    ]
    agg = br._estimate_cost_from_usage(rows)
    bucket = agg[("mod", "unknown-model-xyz")]
    # Fallback is (3, 15) — Sonnet 4.6 tier: 1M * 3 + 1M * 15 = $18
    assert bucket["est_usd"] == pytest.approx(18.0)


# ---------------------------------------------------------------------------
# Integration: run_benchmark respects dry_run + estimate_cost paths
# ---------------------------------------------------------------------------


def test_run_benchmark_live_without_yes_live_writes_zero_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(br, "CSV_PATH", tmp_path / "out.csv")
    rows = br.run_benchmark(
        modules=["01_equity_thesis"],
        models=["claude-haiku-4-5-20251001"],
        dry_run=False,
        generator="live",
        scenario_cap=1,
        judge_model="claude-opus-4-7",
        yes_live=False,
    )
    assert rows == 0
    # CSV path should not be created when the gate blocks execution
    assert not (tmp_path / "out.csv").exists()


def test_run_benchmark_estimate_cost_writes_no_rows(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(br, "CSV_PATH", tmp_path / "out.csv")
    rows = br.run_benchmark(
        modules=["01_equity_thesis"],
        models=["claude-opus-4-7"],
        dry_run=True,
        generator="dry",
        scenario_cap=1,
        judge_model="claude-opus-4-7",
        yes_live=False,
        estimate_cost=True,
    )
    assert rows == 0
    captured = capsys.readouterr()
    assert "est_usd" in captured.out
    assert not (tmp_path / "out.csv").exists()
