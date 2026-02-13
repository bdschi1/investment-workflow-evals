"""Smoke tests for investment-workflow-evals."""
import os
def test_evals_exist():
    assert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "evals"))
def test_schemas_exist():
    assert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "schemas"))
def test_templates_exist():
    assert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "templates"))
