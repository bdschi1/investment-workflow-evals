# Investment Workflow Evaluations

**Domain expertise demonstration for AI training and evaluation in institutional investment research.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About This Project

This repository demonstrates capabilities in AI evaluation and training data creation for financial domains. It showcases:

- **Scenario design** for testing AI financial reasoning
- **Rubric development** with institutional-grade scoring criteria
- **Golden answer writing** that models expert-level analysis
- **Adversarial testing** to expose common AI failure modes
- **Evaluation tooling** for automated assessment pipelines

## Why This Matters

AI labs and platforms need domain experts who can:

1. **Create evaluation scenarios** - Design realistic test cases that probe AI capabilities
2. **Write reference answers** - Produce institutional-quality responses for model training (SFT, RLHF)
3. **Score AI outputs** - Apply consistent rubrics to identify strengths and failure modes
4. **Design adversarial tests** - Craft edge cases that expose hallucinations and errors

This repo demonstrates all four capabilities with working examples.

## Evaluation Modules

| Module | Scenarios | Rubric | Focus |
|--------|-----------|--------|-------|
| **Equity Thesis** | 2 | [standard.yaml](evals/01_equity_thesis/rubrics/standard.yaml) | Thesis construction, catalyst analysis, risk/reward |
| **DCF Valuation** | 2 | [standard.yaml](evals/02_dcf_valuation/rubrics/standard.yaml) | Alpha vs environment, terminal value, margin normalization |
| **Portfolio Construction** | 2 | [standard.yaml](evals/03_portfolio_construction/rubrics/standard.yaml) | Risk-based sizing, hedging, policy risk |
| **Risk Attribution** | 2 | [standard.yaml](evals/05_risk_attribution/rubrics/standard.yaml) | Factor decomposition, hypothesis testing |

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
| **Risk Attribution** | [Alpha vs Environment](evals/05_risk_attribution/scenarios/alpha_vs_environment_attribution.yaml) | Factor decomposition, hypothesis testing |
| **Risk Attribution** | [Capital vs Risk](evals/05_risk_attribution/scenarios/capital_vs_risk_concentration.yaml) | Intentional vs accidental exposure |

## Golden Answers

Expert-level reference responses demonstrating proper analytical workflow:

| Module | Golden Answer | Key Concepts |
|--------|---------------|--------------|
| **Equity Thesis** | [Biotech Phase 3 Catalyst](evals/01_equity_thesis/golden_answers/biotech_phase3_catalyst.md) | Probability framework, scenario analysis, position sizing |
| **DCF Valuation** | [Life Sciences Tools](evals/02_dcf_valuation/golden_answers/life_sciences_tools_valuation.md) | Alpha/environment decomposition, terminal value discipline |
| **Portfolio Construction** | [Pharma/Biotech Pair](evals/03_portfolio_construction/golden_answers/pharma_biotech_pair.md) | Volatility-adjusted sizing, environmental hedging |
| **Risk Attribution** | [Alpha vs Environment](evals/05_risk_attribution/golden_answers/alpha_vs_environment_attribution.md) | Factor decomposition, hypothesis falsification |

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
├── src/
│   ├── extract_pairs.py           # Extract RLHF preference pairs
│   └── summarize_dataset.py       # Dataset statistics
├── results/                       # Evaluation outputs (gitignored)
├── examples/
│   └── sample_ai_response.md      # Test input
├── schemas/
│   └── scenario.yaml              # JSON Schema for scenario validation
├── templates/
│   ├── scenario_template.yaml     # Template for new scenarios
│   └── investment_memo_template.md
├── docs/
│   ├── methodology.md             # Evaluation methodology
│   └── CONTRIBUTING.md            # Contribution guidelines
├── adversarial/                   # Adversarial test variants
└── run_all.sh                     # Run full pipeline
```

## Use Cases

- **RLHF preference data** - Paired comparisons for reward model training
- **SFT training data** - High-quality examples for supervised fine-tuning
- **Model evaluation** - Standardized benchmarks for financial AI
- **Red teaming** - Adversarial testing for hallucination detection

## Skills & Expertise

| Domain | Areas |
|--------|-------|
| **Investment** | Equity research, portfolio management, DCF/comparables valuation, earnings analysis |
| **Sectors** | Healthcare, Technology, Industrials, Consumer |
| **Technical** | Python, ML/deep learning, quantitative analysis |
| **AI Training** | Scenario design, rubric calibration, RLHF data creation, red teaming |

## Contact

- GitHub: [@bdschi1](https://github.com/bdschi1)
- LinkedIn: - [LinkedIn](https://linkedin.com/in/brad-schonhoft-cfa)

## License

MIT License
