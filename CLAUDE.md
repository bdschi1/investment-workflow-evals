# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## What This Is
AI evaluation and training-data framework for institutional investment research. Includes YAML-based eval scenarios with rubrics, golden answers, and adversarial variants across six financial modules, plus an interactive RLHF Studio for generating DPO preference pairs from live LLM outputs.

## Commands
```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"           # core + pytest/black/ruff
pip install -e ".[studio]"       # adds Streamlit, LLM providers, PDF parsing

# Run evaluations
python -m tools.eval_runner list
python -m tools.eval_runner run --module 01_equity_thesis --scenario biotech_phase3_catalyst --input examples/sample_ai_response.md

# Grade a submission
python -m tools.grading_engine grade --submission examples/sample_ai_response.md --rubric evals/01_equity_thesis/rubrics/standard.yaml

# Extract RLHF pairs
python -m src.extract_pairs --module 03_portfolio_construction

# Launch RLHF Studio
streamlit run studio/app.py

# Tests
pytest tests/ -v

# Lint
ruff check .
black --check .
```

## Architecture
- **`evals/`** — Evaluation modules (01-06), each with `scenarios/`, `rubrics/`, and `golden_answers/` subdirectories. Scenarios and rubrics are YAML; golden answers are Markdown.
- **`tools/eval_runner.py`** — CLI for listing and running evaluations against AI responses. Outputs to `results/`.
- **`tools/grading_engine.py`** — Scores submissions against YAML rubrics with weighted dimensions, critical failure gates, and detailed feedback.
- **`studio/`** — Streamlit-based RLHF Studio package. `app.py` (UI), `configs.py` (models/presets/personas), `generator.py` (multi-provider LLM calls), `ranker.py` (K-ranking to pairwise extraction), `document.py` (section-aware PDF parsing), `storage.py` (JSONL persistence), `rewards.py` (reward signal design).
- **`src/extract_pairs.py`** — Batch extraction of RLHF preference pairs from scenario anchor answers.
- **`src/summarize_dataset.py`** — Dataset statistics across modules.
- **`schemas/`** — JSON Schema for scenario validation and unified preference pair format.

## Key Patterns
- Scenarios use a standard YAML schema: context, task prompt, evaluation criteria, adversarial example, anchor answers (strong/acceptable/failing).
- Rubrics define weighted dimensions with 5-level scoring and critical failure conditions that trigger automatic fail.
- Two RLHF pipelines share one JSONL schema: batch (`source: "scenario_anchor"`) and interactive (`source: "studio_ranking"`).
- Studio supports three LLM providers (Anthropic, OpenAI, Gemini) via a provider-inference pattern in `configs.py`.

## Testing Conventions
- Tests live in `tests/`. Run with `pytest tests/ -v`.
- `test_smoke.py` — Verifies directory structure (evals, schemas, templates exist).
- `test_studio_smoke.py` — Validates studio package files, JSON schema, and module imports.
- `test_memo_schema.py` — Pydantic model validation for investment memo schemas.
- `test_rewards.py`, `test_translator.py` — Unit tests for studio reward logic and research translation.
- Tests are mostly structural and import-based; no external API calls or mocking required for the core suite.
