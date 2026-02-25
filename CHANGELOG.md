# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-02-16

### Added
- Six evaluation modules: equity thesis, DCF valuation, portfolio construction, assumption validation, risk attribution (scaffolded), and research translation
- YAML-based scenario format with context, task prompts, adversarial examples, and anchor answers
- Weighted rubrics with 5-level scoring, critical failure conditions, and calibration examples
- Golden answers demonstrating expert-level analytical workflow for each active module
- CLI eval runner (`tools/eval_runner.py`) for listing modules/scenarios and running evaluations
- Grading engine (`tools/grading_engine.py`) with dimension-specific scoring against rubrics
- RLHF preference pair extraction from scenario anchors (`src/extract_pairs.py`)
- Dataset statistics summarizer (`src/summarize_dataset.py`)
- RLHF Studio (`studio/`) — Streamlit UI for interactive DPO preference data generation
- Studio features: section-aware PDF parsing (10-K/10-Q), multi-provider LLM generation (Anthropic/OpenAI/Gemini), K-ranking with pairwise pair extraction, persona sweeps
- Unified JSONL preference pair schema (`schemas/preference_pair.json`) shared across batch and interactive pipelines
- Adversarial test variants targeting common AI failure modes (alpha/environment confusion, false certainty, backward-looking risk, narrative attribution)
- `run_all.sh` full-pipeline script
