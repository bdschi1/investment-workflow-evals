# Investment Workflow Evaluations

Evaluation scenarios and graded reference answers for testing AI models on institutional investment research tasks. Covers the core analyst workflow — from reading SEC filings to writing investment memos — with rubric-scored outputs that double as fine-tuning training data. An interactive RLHF Studio is also included for generating DPO preference pairs from live LLM outputs against real financial documents.

This is a continually developed project. Evaluation modules, scenarios, and rubrics expand over time as new research tasks and failure modes are identified.

**Key questions this project answers:**
- *Can this AI model produce analyst-quality investment research?*
- *Where does the model fail in ways that sound intelligent but are substantively wrong?*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About This Project

This repository contains evaluation scenarios, scoring rubrics, golden reference answers, and adversarial test cases for investment research tasks. The evaluation modules cover equity thesis construction, DCF valuation, portfolio construction, assumption validation, and research translation. Each module includes:

- **Scenarios** with task prompts and domain context drawn from realistic investment situations
- **Rubrics** with weighted dimensions and multi-level scoring anchors
- **Golden answers** representing expert-level analytical responses
- **Adversarial examples** — responses that use correct-sounding language but contain substantive analytical errors

## Purpose

The materials serve two related uses: benchmarking AI model performance on investment research tasks, and producing training data (SFT examples and RLHF preference pairs) for fine-tuning. The `studio/` package extends this to interactive preference data collection from live model outputs.

## Evaluation Modules

| Module | Scenarios | Rubric | Focus |
|--------|-----------|--------|-------|
| **Equity Thesis** | 2 | [standard.yaml](evals/01_equity_thesis/rubrics/standard.yaml) | Thesis construction, catalyst analysis, risk/reward |
| **DCF Valuation** | 2 | [standard.yaml](evals/02_dcf_valuation/rubrics/standard.yaml) | Alpha vs environment, terminal value, margin normalization |
| **Portfolio Construction** | 2 | [standard.yaml](evals/03_portfolio_construction/rubrics/standard.yaml) | Risk-based sizing, hedging, policy risk |
| **Assumption Validation** | 2 | [assumption_validation.yaml](evals/04_assumption_validation/rubrics/assumption_validation.yaml) | Discount rate stress-testing, commodity price assumptions |
| **Risk Attribution** | — | — | Factor decomposition, hypothesis testing *(scaffolded, content pending)* |
| **Research Translation** | 1 | [translation_quality.yaml](evals/06_research_translation/rubrics/translation_quality.yaml) | IC memo to retail-readable summary |

## Sample Scenarios

Each scenario includes context, task prompt, evaluation criteria, and an adversarial example ("sounds smart but is wrong"):

| Module | Scenario | Key Challenge |
|--------|----------|---------------|
| **Equity Thesis** | [Biotech Phase 3 Catalyst](evals/01_equity_thesis/scenarios/biotech_phase3_catalyst.yaml) | Probability estimation, asymmetric risk/reward |
| **Equity Thesis** | [Cyclical Trough Valuation](evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml) | Through-cycle valuation, margin normalization |
| **DCF Valuation** | [Life Sciences Tools](evals/02_dcf_valuation/scenarios/life_sciences_tools_valuation.yaml) | Alpha vs environment separation, terminal value discipline |
| **DCF Valuation** | [MedTech Normalization](evals/02_dcf_valuation/scenarios/medtech_normalization.yaml) | Cyclical vs structural, uncertainty placement |
| **Portfolio Construction** | [Pharma/Biotech Pair](evals/03_portfolio_construction/scenarios/pharma_biotech_pair.yaml) | Risk-based sizing, hedging environmental exposure |
| **Portfolio Construction** | [Policy Risk Sizing](evals/03_portfolio_construction/scenarios/healthcare_services_policy_risk.yaml) | Forward-looking risk, tail risk recognition |
| **Assumption Validation** | [Biotech Discount Rate](evals/04_assumption_validation/scenarios/biotech_discount_rate.yaml) | Discount rate stress-testing under uncertainty |
| **Assumption Validation** | [Commodity Price Assumption](evals/04_assumption_validation/scenarios/commodity_price_assumption.yaml) | Forward curve vs mean-reversion assumptions |
| **Research Translation** | [IC Memo to Blog](evals/06_research_translation/scenarios/ic_memo_to_blog.yaml) | Institutional-to-retail content adaptation |

## Golden Answers

Expert-level reference responses demonstrating proper analytical workflow:

| Module | Golden Answer | Key Concepts |
|--------|---------------|--------------|
| **Equity Thesis** | [Biotech Phase 3 Catalyst](evals/01_equity_thesis/golden_answers/biotech_phase3_catalyst.md) | Probability framework, scenario analysis, position sizing |
| **DCF Valuation** | [Life Sciences Tools](evals/02_dcf_valuation/golden_answers/life_sciences_tools_valuation.md) | Alpha/environment decomposition, terminal value discipline |
| **Portfolio Construction** | [Pharma/Biotech Pair](evals/03_portfolio_construction/golden_answers/pharma_biotech_pair.md) | Volatility-adjusted sizing, environmental hedging |
| **Assumption Validation** | [Biotech Discount Rate](evals/04_assumption_validation/golden_answers/biotech_discount_rate.md) | Sensitivity analysis, uncertainty quantification |
| **Research Translation** | [ABBV Retail Summary](evals/06_research_translation/golden_answers/abbv_retail_summary.md) | Jargon simplification, actionable takeaways |

## Rubric Structure

Each rubric provides:

- **Weighted dimensions** (e.g., Alpha vs Environment 35%, Risk Treatment 35%, Terminal Value 30%)
- **5-level scoring** with anchor examples (Excellent → Fail)
- **Critical failure conditions** that trigger automatic fail
- **Calibration examples** at multiple score levels

Example from DCF Valuation rubric:

```yaml
critical_failures:
  - condition: "Treats environmental demand as structural alpha"
    automatic_fail: true
  - condition: "Embeds unhedged funding-cycle growth into terminal value"
    automatic_fail: true
```

## Common AI Failure Modes Tested

Each scenario includes adversarial examples - responses that "sound smart but are wrong":

- **Alpha/Environment Confusion** - Treating environmental tailwinds as company-specific alpha
- **False Certainty** - Embedding unhedged risks into base-case assumptions
- **Backward-Looking Risk** - Using trailing volatility when forward risks dominate
- **Mechanical Responses** - De-risking without diagnosing what risk is being taken
- **Narrative Attribution** - Declaring alpha failure without factor decomposition
- **Notional vs Risk Symmetry** - Dollar-neutral sizing ignoring volatility differentials
- **Hallucinated Data** - Fabricated financial metrics or company facts

## Running Locally

```bash
# Setup virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# List available modules
python -m tools.eval_runner list

# List scenarios in a module
python -m tools.eval_runner list --module 02_dcf_valuation

# Run evaluation against AI response (outputs to results/)
python -m tools.eval_runner run \
  --module 01_equity_thesis \
  --scenario biotech_phase3_catalyst \
  --input examples/sample_ai_response.md

# Grade a submission against rubric (basic)
python -m tools.grading_engine grade \
  --submission examples/sample_ai_response.md \
  --rubric evals/01_equity_thesis/rubrics/standard.yaml

# Grade with scenario context (enables dimension-specific scoring)
python -m tools.grading_engine grade \
  --submission evals/01_equity_thesis/golden_answers/biotech_phase3_catalyst.md \
  --rubric evals/01_equity_thesis/rubrics/standard.yaml \
  --scenario evals/01_equity_thesis/scenarios/biotech_phase3_catalyst.yaml

# Extract RLHF preference pairs (outputs to results/)
python -m src.extract_pairs --module 03_portfolio_construction

# Summarize dataset statistics
python -m src.summarize_dataset
```

### Run Everything

```bash
# One-liner to run the full pipeline
./run_all.sh
```

### Example Output

```
==================================================
GRADING RESULTS
==================================================

Overall Score: 96.5/100
Status: PASS

--- Dimension Scores ---
  attribution_discipline: 100.0
  hypothesis_testing: 90.0
  contextual_evaluation: 100.0

--- Detailed Feedback ---
  attribution_discipline: Strong factor decomposition; Calculates residual alpha; Shows calculation methodology
  hypothesis_testing: Strong hypothesis testing; Shows appropriate skepticism
  contextual_evaluation: Evaluates skill conditionally; Addresses intentionality question
```

## Project Structure

```
investment-workflow-evals/
├── evals/                         # Evaluation modules
│   ├── 00_qualification/          # Onboarding assessment
│   │   ├── scenarios/
│   │   └── rubrics/
│   ├── 01_equity_thesis/          # Investment thesis evaluation
│   │   ├── scenarios/
│   │   ├── rubrics/
│   │   └── golden_answers/
│   ├── 02_dcf_valuation/          # Valuation framework evaluation
│   │   ├── scenarios/
│   │   ├── rubrics/
│   │   └── golden_answers/
│   ├── 03_portfolio_construction/ # Position sizing & hedging
│   │   ├── scenarios/
│   │   ├── rubrics/
│   │   └── golden_answers/
│   └── 05_risk_attribution/       # Performance attribution
│       └── rubrics/
├── tools/
│   ├── eval_runner.py             # Run evaluations
│   └── grading_engine.py          # Score submissions
├── studio/                        # RLHF Studio (interactive DPO data)
│   ├── app.py                     # Streamlit UI
│   ├── configs.py                 # Models, presets, personas
│   ├── generator.py               # Multi-provider LLM generation
│   ├── ranker.py                  # K-ranking → pairwise extraction
│   ├── document.py                # Section-aware PDF parsing
│   └── storage.py                 # JSONL persistence
├── src/
│   ├── extract_pairs.py           # Extract RLHF preference pairs
│   └── summarize_dataset.py       # Dataset statistics
├── results/                       # Evaluation outputs (gitignored)
├── examples/
│   └── sample_ai_response.md      # Test input
├── schemas/
│   ├── scenario.yaml              # JSON Schema for scenario validation
│   └── preference_pair.json       # Unified DPO pair schema
├── templates/
│   ├── scenario_template.yaml     # Template for new scenarios
│   └── investment_memo_template.md
├── docs/
│   ├── methodology.md             # Evaluation methodology
│   └── CONTRIBUTING.md            # Contribution guidelines
├── adversarial/                   # Adversarial test variants
└── run_all.sh                     # Run full pipeline
```

## RLHF Studio (Interactive Preference Data)

The `studio/` package provides a Streamlit-based interactive workflow for generating DPO preference pairs from live LLM outputs. Upload a financial PDF, select sections, generate K outputs across different models/temperatures/personas, then rank them to produce training data.

**Two annotation modes:**
- **Single Pair:** Generate one draft → correct it → 1 preference pair
- **K-Ranking:** Generate K outputs (2–9) → rank best→worst → up to K(K-1)/2 pairs per session (e.g., K=4 → 6 pairs)

**Features:** Section-aware PDF parsing (10-K/10-Q), boilerplate filtering, auto-chunking, multi-provider generation (Anthropic/OpenAI/Gemini), rate-limit handling, drag-and-drop ranking.

```bash
# Install studio dependencies
pip install -e ".[studio]"

# Launch the studio
streamlit run studio/app.py
```

Both pipelines emit a unified JSONL schema (see `schemas/preference_pair.json`):
- `src/extract_pairs.py` → `source: "scenario_anchor"` (batch, from YAML scenarios)
- `studio/ranker.py` → `source: "studio_ranking"` (interactive, from live LLM outputs)

## Use Cases

- **RLHF preference data** - Paired comparisons for reward model training
- **SFT training data** - High-quality examples for supervised fine-tuning
- **Model evaluation** - Standardized benchmarks for financial AI
- **Red teaming** - Adversarial testing for hallucination detection
- **Interactive DPO data** - Live K-ranking across models and personas via RLHF Studio

## Contributing

Contributions welcome. Areas for improvement:
- Additional evaluation modules and scenarios
- New rubric dimensions and scoring anchors
- Extended adversarial test cases
- RLHF Studio enhancements and new annotation modes

## Status

This project is under active, ongoing development. Core evaluation modules, grading engine, and RLHF Studio are stable. New scenarios, rubrics, and adversarial variants are added as new investment tasks and AI failure modes are identified.

## License

MIT License

## Related Work

This project draws on several recent academic contributions to financial AI evaluation and alignment:

- **Fin-o1** (Qian et al., 2025) — First systematic comparison of PPO, DPO, and GRPO reinforcement learning methods for financial reasoning. GRPO's multi-faceted reward function (accuracy + logic + format + length) directly informs the `studio/rewards.py` reward signal design. [arXiv:2502.08127](https://arxiv.org/abs/2502.08127)
- **FinanceQA** (Mateega et al., 2025) — Benchmark exposing that frontier LLMs fail ~60% of realistic analyst tasks, with near-zero accuracy on assumption-based questions. Motivates the `04_assumption_validation` eval category. [arXiv:2501.18062](https://arxiv.org/abs/2501.18062)
- **PRBench** (Akyurek et al., 2025) — 19,356 expert-curated binary criteria with integer weights across 7 finance rubric categories. Informs our rubric-based evaluation methodology and YAML rubric schema design. [arXiv:2511.11562](https://arxiv.org/abs/2511.11562)
- **FLaME** (Matlin et al., 2025) — First holistic benchmarking suite for financial NLP, evaluating 23 models across 20 datasets and 6 task categories. Provides the taxonomy framework for cross-benchmark comparability. [arXiv:2506.15846](https://arxiv.org/abs/2506.15846)
