"""Tools for running evaluations and grading submissions."""

from .grading_engine import GradingEngine

__all__ = ["EvaluationRunner", "GradingEngine"]


def __getattr__(name):
    if name == "EvaluationRunner":
        from .eval_runner import EvaluationRunner
        return EvaluationRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
