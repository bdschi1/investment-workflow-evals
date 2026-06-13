<!-- investment-workflow-evals/README.md | Last updated: 2026-06-13 -->

# Investment Workflow Evaluations

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![tests](https://img.shields.io/badge/tests-321%20passing-brightgreen.svg)](tests/)

Evaluation scenarios and graded reference answers for testing AI models on institutional investment-research tasks. 13 modules across the analyst workflow — qualification, equity thesis, DCF, portfolio construction, assumption validation, risk attribution, research translation, report review, comps, M&A, valuation synthesis, LBO, deal execution — each with a rubric-scored output that doubles as fine-tuning data.

**Plain English:** A test bank plus answer key for AI investment research. Each scenario has a task prompt, a weighted rubric, an expert golden answer, and an adversarial "sounds smart but wrong" example. Includes a Streamlit RLHF Studio for generating DPO preference pairs from live model outputs.

## Install

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[studio]"     # RLHF Studio (optional)
```

## Usage

```
python -m tools.eval_runner list
python -m tools.eval_runner run --module 01_equity_thesis --scenario biotech_phase3_catalyst --input examples/sample_ai_response.md
python -m tools.grading_engine grade --submission examples/sample_ai_response.md --rubric evals/01_equity_thesis/rubrics/standard.yaml
streamlit run studio/app.py    # RLHF Studio
```

## What it does

- Rubrics are weighted YAML dimensions with 5-level anchors and critical-failure gates
- Two RLHF pipelines share one JSONL schema: rubric-anchored pairs and live K-ranking pairs
- RLHF Studio: section-aware 10-K/10-Q parsing, multi-provider generation (Anthropic / OpenAI / Gemini), K-way ranking, pairwise DPO extraction
- Frontier benchmark runner gated behind `--yes-live`; see `BENCHMARK_RUN.md`, `METHODOLOGY.md`, `SAMPLE_TASK.md`

## Tests

```
pytest tests/ -v
```

## License

MIT
