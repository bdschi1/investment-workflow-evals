"""Tests for CI mode in tools/eval_runner.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCIFlagLimitsScenarios(unittest.TestCase):
    """test_ci_flag_limits_scenarios: CI mode evaluates at most 10 scenarios."""

    def test_ci_flag_limits_scenarios(self):
        """_run_ci_mode collects at most _CI_LIMIT scenarios."""
        from tools.eval_runner import _CI_LIMIT, EvaluationRunner

        # Build a mock runner that returns > CI_LIMIT scenarios across modules
        mock_runner = MagicMock(spec=EvaluationRunner)

        modules = [{"id": f"mod_{i}", "scenario_count": 3} for i in range(6)]
        mock_runner.list_modules.return_value = modules

        # Each module returns 3 scenarios
        def list_scenarios_side(mod_id):
            return [{"id": f"{mod_id}_s{j}"} for j in range(3)]

        mock_runner.list_scenarios.side_effect = list_scenarios_side

        # run_evaluation always returns a passed result
        mock_result = MagicMock()
        mock_result.passed = True
        mock_runner.run_evaluation.return_value = mock_result
        mock_runner.load_golden_answer.return_value = "golden answer text"

        collected_scenarios: list[str] = []
        original_run_eval = mock_runner.run_evaluation.side_effect

        def track_run_eval(config, ai_output=None):
            collected_scenarios.append(config.scenario_name)
            return mock_result

        mock_runner.run_evaluation.side_effect = track_run_eval

        args = MagicMock()
        args.module = None
        args.threshold = 0.70

        with patch("sys.exit"), patch("sys.stdout", MagicMock()):
            from tools.eval_runner import _run_ci_mode
            _run_ci_mode(mock_runner, args)

        self.assertLessEqual(len(collected_scenarios), 10)
        self.assertLessEqual(len(collected_scenarios), _CI_LIMIT)


class TestCIOutputIsValidJSON(unittest.TestCase):
    """test_ci_output_is_valid_json: stdout must be parseable JSON."""

    def test_ci_output_is_valid_json(self):
        """Capture stdout and verify json.loads() succeeds."""
        import io
        from tools.eval_runner import EvaluationRunner

        mock_runner = MagicMock(spec=EvaluationRunner)
        mock_runner.list_modules.return_value = [{"id": "01_equity_thesis", "scenario_count": 2}]
        mock_runner.list_scenarios.return_value = [
            {"id": "scenario_a"},
            {"id": "scenario_b"},
        ]
        mock_runner.load_golden_answer.return_value = "Test golden answer."
        mock_result = MagicMock()
        mock_result.passed = True
        mock_runner.run_evaluation.return_value = mock_result

        args = MagicMock()
        args.module = None
        args.threshold = 0.70

        captured = io.StringIO()

        with patch("sys.exit"), patch("sys.stdout", captured):
            from tools.eval_runner import _run_ci_mode
            _run_ci_mode(mock_runner, args)

        output_text = captured.getvalue().strip()
        self.assertTrue(output_text, "stdout should not be empty")
        parsed = json.loads(output_text)
        self.assertTrue(parsed.get("ci_mode"))
        self.assertIn("scenarios_evaluated", parsed)
        self.assertIn("pass_rate", parsed)
        self.assertIn("pass", parsed)
        self.assertIn("summary", parsed)


class TestCIExits1OnThresholdFailure(unittest.TestCase):
    """test_ci_exits_1_on_threshold_failure: sys.exit(1) when pass_rate < threshold."""

    def test_ci_exits_1_on_threshold_failure(self):
        """When all scenarios fail, sys.exit(1) must be called."""
        from tools.eval_runner import EvaluationRunner

        mock_runner = MagicMock(spec=EvaluationRunner)
        mock_runner.list_modules.return_value = [{"id": "01_equity_thesis", "scenario_count": 3}]
        mock_runner.list_scenarios.return_value = [
            {"id": "s1"},
            {"id": "s2"},
            {"id": "s3"},
        ]
        mock_runner.load_golden_answer.return_value = "golden"

        # All scenarios fail
        mock_result = MagicMock()
        mock_result.passed = False
        mock_runner.run_evaluation.return_value = mock_result

        args = MagicMock()
        args.module = None
        args.threshold = 0.70

        exit_calls: list[int] = []

        def mock_exit(code=0):
            exit_calls.append(code)

        with patch("sys.exit", side_effect=mock_exit):
            from tools.eval_runner import _run_ci_mode
            try:
                _run_ci_mode(mock_runner, args)
            except SystemExit:
                pass

        self.assertTrue(exit_calls, "sys.exit should have been called")
        self.assertEqual(exit_calls[-1], 1, "Expected sys.exit(1) for failing threshold")


class TestModelsFlag(unittest.TestCase):
    """parse_models_flag + EvaluationConfig correctly handle --models."""

    def test_parse_models_flag_handles_none(self):
        from tools.eval_runner import parse_models_flag

        self.assertEqual(parse_models_flag(None), [])
        self.assertEqual(parse_models_flag(""), [])

    def test_parse_models_flag_splits_and_strips(self):
        from tools.eval_runner import parse_models_flag

        parsed = parse_models_flag(
            "claude-opus-4-7, claude-sonnet-4-5 , gpt-5 ,gemini-2.5-pro"
        )
        self.assertEqual(
            parsed,
            [
                "claude-opus-4-7",
                "claude-sonnet-4-5",
                "gpt-5",
                "gemini-2.5-pro",
            ],
        )

    def test_parse_models_flag_deduplicates_preserving_order(self):
        from tools.eval_runner import parse_models_flag

        parsed = parse_models_flag(
            "claude-opus-4-7,claude-sonnet-4-5,claude-opus-4-7"
        )
        self.assertEqual(parsed, ["claude-opus-4-7", "claude-sonnet-4-5"])

    def test_evaluation_config_defaults_models_to_empty_list(self):
        from tools.eval_runner import EvaluationConfig

        cfg = EvaluationConfig(module="01_equity_thesis", scenario_name="s1")
        self.assertEqual(cfg.models, [])

    def test_evaluation_config_accepts_models(self):
        from tools.eval_runner import EvaluationConfig

        cfg = EvaluationConfig(
            module="01_equity_thesis",
            scenario_name="s1",
            models=["claude-opus-4-7", "gpt-5"],
        )
        self.assertEqual(cfg.models, ["claude-opus-4-7", "gpt-5"])

    def test_default_frontier_models_constant(self):
        """DEFAULT_FRONTIER_MODELS matches the upgrade plan's Phase-1 SKU list."""
        from tools.eval_runner import DEFAULT_FRONTIER_MODELS

        expected = {
            "claude-opus-4-7",
            "claude-sonnet-4-5",
            "gpt-5",
            "gemini-2.5-pro",
        }
        self.assertEqual(set(DEFAULT_FRONTIER_MODELS), expected)


if __name__ == "__main__":
    unittest.main()
