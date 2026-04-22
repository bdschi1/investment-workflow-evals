<!-- investment-workflow-evals/README.md | Last updated: 2026-04-16 -->

# Investment Workflow Evaluations

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Evaluation scenarios and graded reference answers for testing AI models on institutional investment research tasks. Covers the core analyst workflow — from reading SEC filings to writing investment memos — with rubric-scored outputs that double as fine-tuning training data. An interactive RLHF Studio is also included for generating DPO preference pairs from live LLM outputs against real financial documents.

This is a continually developed project. Evaluation modules, scenarios, and rubrics expand over time as new research tasks and failure modes are identified.

**Quick nav:** [SAMPLE_TASK.md](SAMPLE_TASK.md) — one worked scenario end-to-end · [METHODOLOGY.md](METHODOLOGY.md) — scenario design + rubric philosophy · [BENCHMARK_RUN.md](BENCHMARK_RUN.md) — frontier-model run protocol

**Key questions this project answers:**
- *Can this AI model produce analyst-quality investment research?*
- *Where does the model fail in ways that sound intelligent but are substantively wrong?*

## Policy

Every deliverable must be objectively gradable, financially sound, and free of AI fingerprints.

1. **Rubric-scored, not vibes-scored.** Every evaluation uses weighted dimensions with 5-level anchors and critical failure gates -- no subjective "good/bad" assessments.
2. **Adversarial examples are mandatory.** Each scenario ships with a response that sounds intelligent but is substantively wrong, because that is the failure mode that matters.
3. **Golden answers set the ceiling.** Expert-written reference responses define what "good" looks like; the rubric measures distance from that standard.
4. **Dual-use by design.** Scenarios serve both evaluation (benchmark AI model quality) and training (SFT examples, RLHF preference pairs) -- same data, two purposes.
5. **Critical failures are automatic fails.** Treating environmental demand as structural alpha or embedding unhedged risks in terminal value triggers an automatic zero regardless of other dimension scores.

The tool exists to catch AI-generated investment analysis that sounds right but would lose money.

---

## Frontier Benchmark (v1.1 — coming)

The repo is scheduled to publish its first frontier-model leaderboard
once the Phase-1 benchmark run completes. Scaffolding is in place:
[`results/frontier_benchmark_v1.csv`](results/frontier_benchmark_v1.csv)
holds the column schema, and
[`results/judge_agreement_v1.md`](results/judge_agreement_v1.md)
documents the methodology for cross-model judge agreement.

**Placeholder — numbers to be filled by v1.1:**

| Module | `claude-opus-4-7` | `claude-sonnet-4-5` | `gpt-5` | `gemini-2.5-pro` |
|---|---|---|---|---|
| 00 qualification | TBD | TBD | TBD | TBD |
| 01 equity thesis | TBD | TBD | TBD | TBD |
| 02 dcf valuation | TBD | TBD | TBD | TBD |
| 03 portfolio construction | TBD | TBD | TBD | TBD |
| 04 assumption validation | TBD | TBD | TBD | TBD |
| 05 risk attribution | TBD | TBD | TBD | TBD |
| 06 research translation | TBD | TBD | TBD | TBD |
| 07 report review | TBD | TBD | TBD | TBD |
| 08 comparable analysis | TBD | TBD | TBD | TBD |
| 09 m&a analysis | TBD | TBD | TBD | TBD |
| 10 valuation synthesis | TBD | TBD | TBD | TBD |
| 11 lbo analysis | TBD | TBD | TBD | TBD |
| 12 deal execution | TBD | TBD | TBD | TBD |

Methodology: one row per (module, scenario, model) is appended to the
CSV at run time; this table reports per-module mean overall scores
across scenarios. Judge-agreement addendum (Spearman, Cohen's κ, and
per-dimension Pearson) will land alongside the first populated run —
see `BENCHMARK_RUN.md` at the repo root for the exact invocation and
rough cost estimate. Scores reported here are probabilistic point
estimates; expect overlapping confidence intervals between close-in
SKUs rather than sharp rankings.

---

## Quick Start

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

### Run the Frontier Benchmark

```bash
# Schema / wiring dry-run (no API calls, no cost):
python -m tools.benchmark_runner --modules all --dry-run \
    --models claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro

# Cheap validation against 2-3 scenarios:
python -m tools.benchmark_runner --modules 06_research_translation \
    --models claude-haiku-4-5-20251001 --generator haiku --scenarios 3

# Full live-frontier run (expensive, ~$150-250):
python -m tools.benchmark_runner --modules all --generator live --yes-live \
    --models claude-opus-4-7,claude-sonnet-4-5,gpt-5,gemini-2.5-pro
```

Results append to [`results/frontier_benchmark_v1.csv`](results/frontier_benchmark_v1.csv). Full invocation details, per-SKU cost estimates, and judge-agreement methodology live in [`BENCHMARK_RUN.md`](BENCHMARK_RUN.md). The live-generation path is intentionally gated behind `--yes-live` as a budget safety rail.

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

---

## How It Works

### About This Project

This repository contains evaluation scenarios, scoring rubrics, golden reference answers, and adversarial test cases for investment research tasks. **Thirteen evaluation modules** (`00_qualification` through `12_deal_execution`) cover the full analyst workflow: qualification, equity thesis, DCF valuation, portfolio construction, assumption validation, risk attribution, research translation, report review, comparable analysis, M&A analysis, valuation synthesis, LBO analysis, and deal execution. Earlier READMEs described seven modules; the current count is reflected in [`docs/coverage_audit_2026-04.md`](docs/coverage_audit_2026-04.md), which also tracks per-module scenario and golden-answer counts. Each module includes:

- **Scenarios** with task prompts and domain context drawn from realistic investment situations
- **Rubrics** with weighted dimensions and multi-level scoring anchors
- **Golden answers** representing expert-level analytical responses
- **Adversarial examples** — responses that use correct-sounding language but contain substantive analytical errors

### Purpose

The materials serve two related uses: benchmarking AI model performance on investment research tasks, and producing training data (SFT examples and RLHF preference pairs) for fine-tuning. The `studio/` package extends this to interactive preference data collection from live model outputs.

### Evaluation Modules

Live counts (2026-04-18); see [`docs/coverage_audit_2026-04.md`](docs/coverage_audit_2026-04.md) for methodology and Phase-1 target vs actual.

| Module | Scenarios | Goldens | Rubric | Focus |
|--------|-----------|---------|--------|-------|
| **00 Qualification** | 1 | 1 | [qualification_standard.yaml](evals/00_qualification/rubrics/qualification_standard.yaml) | Onboarding assessment, basic equity analysis |
| **01 Equity Thesis** | 3 | 3 | [standard.yaml](evals/01_equity_thesis/rubrics/standard.yaml) | Thesis construction, catalyst analysis, capex cycle, risk/reward |
| **02 DCF Valuation** | 2 | 2 | [standard.yaml](evals/02_dcf_valuation/rubrics/standard.yaml) | Alpha vs environment, terminal value, margin normalization |
| **03 Portfolio Construction** | 27 | 5 | [standard.yaml](evals/03_portfolio_construction/rubrics/standard.yaml) | Risk-based sizing, crowding risk, hedging, policy risk — see [scenarios/INDEX.md](evals/03_portfolio_construction/scenarios/INDEX.md) |
| **04 Assumption Validation** | 3 | 3 | [assumption_validation.yaml](evals/04_assumption_validation/rubrics/assumption_validation.yaml) | Discount rate stress-testing, commodity assumptions, statistical significance |
| **05 Risk Attribution** | 2 | 2 | [risk_attribution.yaml](evals/05_risk_attribution/rubrics/risk_attribution.yaml) | Factor decomposition, hypothesis testing, alpha vs environment |
| **06 Research Translation** | 3 | 3 | [translation_quality.yaml](evals/06_research_translation/rubrics/translation_quality.yaml) | 10-K risk, earnings call, IC memo → plain-English |
| **07 Report Review** | 6 | 6 | [standard.yaml](evals/07_report_review/rubrics/standard.yaml) | Sell-side note critique, bias detection |
| **08 Comparable Analysis** | 1 | 0 | [standard.yaml](evals/08_comparable_analysis/rubrics/standard.yaml) | Peer-set construction (goldens deferred) |
| **09 M&A Analysis** | 3 | 3 | [standard.yaml](evals/09_ma_analysis/rubrics/standard.yaml) | Accretion/dilution, synergy sensitivity, sources & uses |
| **10 Valuation Synthesis** | 3 | 3 | [standard.yaml](evals/10_valuation_synthesis/rubrics/standard.yaml) | DCF sensitivity, football field, SOTP |
| **11 LBO Analysis** | 3 | 3 | [standard.yaml](evals/11_lbo_analysis/rubrics/standard.yaml) | Midmarket LBO returns, dividend recap, returns bridge |
| **12 Deal Execution** | 3 | 3 | [standard.yaml](evals/12_deal_execution/rubrics/standard.yaml) | Bid comparison, diligence list, signing-to-close |

### Sample Scenarios

Each scenario includes context, task prompt, evaluation criteria, and an adversarial example ("sounds smart but is wrong"):

| Module | Scenario | Key Challenge |
|--------|----------|---------------|
| **Equity Thesis** | [Biotech Phase 3 Catalyst](evals/01_equity_thesis/scenarios/biotech_phase3_catalyst.yaml) | Probability estimation, asymmetric risk/reward |
| **Equity Thesis** | [Cyclical Trough Valuation](evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml) | Through-cycle valuation, margin normalization |
| **Equity Thesis** | [AI Capex Cycle Thesis](evals/01_equity_thesis/scenarios/ai_capex_cycle_thesis.yaml) | Capex cycle timing, secular vs cyclical growth |
| **DCF Valuation** | [Life Sciences Tools](evals/02_dcf_valuation/scenarios/life_sciences_tools_valuation.yaml) | Alpha vs environment separation, terminal value discipline |
| **DCF Valuation** | [MedTech Normalization](evals/02_dcf_valuation/scenarios/medtech_normalization.yaml) | Cyclical vs structural, uncertainty placement |
| **Portfolio Construction** | [Pharma/Biotech Pair](evals/03_portfolio_construction/scenarios/pharma_biotech_pair.yaml) | Risk-based sizing, hedging environmental exposure |
| **Portfolio Construction** | [Policy Risk Sizing](evals/03_portfolio_construction/scenarios/healthcare_services_policy_risk.yaml) | Forward-looking risk, tail risk recognition |
| **Portfolio Construction** | [Crowding Risk Sizing](evals/03_portfolio_construction/scenarios/crowding_risk_sizing.yaml) | Position sizing under crowded-trade dynamics |
| **Assumption Validation** | [Biotech Discount Rate](evals/04_assumption_validation/scenarios/biotech_discount_rate.yaml) | Discount rate stress-testing under uncertainty |
| **Assumption Validation** | [Commodity Price Assumption](evals/04_assumption_validation/scenarios/commodity_price_assumption.yaml) | Forward curve vs mean-reversion assumptions |
| **Assumption Validation** | [Statistical Significance Trap](evals/04_assumption_validation/scenarios/statistical_significance_trap.yaml) | p-hacking, backtest overfitting, multiple comparisons |
| **Risk Attribution** | [Healthcare L/S Factor Decomposition](evals/05_risk_attribution/scenarios/healthcare_ls_factor_decomposition.yaml) | Multi-factor return decomposition, residual alpha |
| **Risk Attribution** | [Factor Tilt Attribution](evals/05_risk_attribution/scenarios/factor_tilt_attribution.yaml) | Value factor tilt vs stock selection, statistical significance |
| **Research Translation** | [10-K Risk → Plain English](evals/06_research_translation/scenarios/10k_risk_section_to_plain_english.yaml) | Issuer-specific risk prioritization, boilerplate filtering |
| **Research Translation** | [Earnings Call → Shareholder Note](evals/06_research_translation/scenarios/earnings_call_to_shareholder_note.yaml) | Signal vs noise across 4 management items |
| **M&A Analysis** | [Accretion/Dilution Strategic](evals/09_ma_analysis/scenarios/accretion_dilution_strategic.yaml) | Pro-forma EPS mechanics, financing-mix trade-offs |
| **M&A Analysis** | [Merger Model Synergy Sensitivity](evals/09_ma_analysis/scenarios/merger_model_synergy_sensitivity.yaml) | Synergy phasing, 4x2 sensitivity grid |
| **Valuation Synthesis** | [DCF Sensitivity WACC/g](evals/10_valuation_synthesis/scenarios/dcf_sensitivity_growth_wacc.yaml) | Gordon Growth grid, TV share of EV |
| **Valuation Synthesis** | [SOTP Conglomerate](evals/10_valuation_synthesis/scenarios/sotp_conglomerate.yaml) | Segment-level multiple selection, holdco discount |
| **LBO Analysis** | [Dividend Recap Feasibility](evals/11_lbo_analysis/scenarios/dividend_recap_feasibility.yaml) | Leverage headroom, IRR uplift vs exit-timing |
| **Deal Execution** | [Bid Comparison Process](evals/12_deal_execution/scenarios/bid_comparison_process.yaml) | Risk-adjusted normalization of LOIs |
| **Deal Execution** | [Signing-to-Close Workstream](evals/12_deal_execution/scenarios/signing_to_close_workstream.yaml) | Critical-path identification, State-DOH gating |

### Golden Answers

Expert-level reference responses demonstrating proper analytical workflow. Current coverage is **35 goldens across 13 modules**; full per-module counts in [`docs/coverage_audit_2026-04.md`](docs/coverage_audit_2026-04.md). Sample goldens:

| Module | Golden Answer | Key Concepts |
|--------|---------------|--------------|
| **Qualification** | [Basic Equity Analysis](evals/00_qualification/golden_answers/basic_equity_analysis.md) | Fundamental assessment, valuation basics |
| **Equity Thesis** | [Biotech Phase 3 Catalyst](evals/01_equity_thesis/golden_answers/biotech_phase3_catalyst.md) | Probability framework, scenario analysis, position sizing |
| **Equity Thesis** | [Cyclical Trough Valuation](evals/01_equity_thesis/golden_answers/cyclical_trough_valuation.md) | Through-cycle normalization, margin reversion |
| **Equity Thesis** | [AI Capex Cycle Thesis](evals/01_equity_thesis/golden_answers/ai_capex_cycle_thesis.md) | Capex cycle timing, secular vs cyclical drivers |
| **DCF Valuation** | [Life Sciences Tools](evals/02_dcf_valuation/golden_answers/life_sciences_tools_valuation.md) | Alpha/environment decomposition, terminal value discipline |
| **DCF Valuation** | [MedTech Normalization](evals/02_dcf_valuation/golden_answers/medtech_normalization.md) | Cyclical vs structural margin, uncertainty placement |
| **Portfolio Construction** | [Pharma/Biotech Pair](evals/03_portfolio_construction/golden_answers/pharma_biotech_pair.md) | Volatility-adjusted sizing, environmental hedging |
| **Portfolio Construction** | [Policy Risk Sizing](evals/03_portfolio_construction/golden_answers/healthcare_services_policy_risk.md) | Forward-looking risk, tail event recognition |
| **Portfolio Construction** | [Crowding Risk Sizing](evals/03_portfolio_construction/golden_answers/crowding_risk_sizing.md) | Crowded-trade dynamics, liquidity-aware sizing |
| **Portfolio Construction** | [Risk-Based Sizing](evals/03_portfolio_construction/golden_answers/risk_based_sizing.md) | Risk-budgeted position construction |
| **Portfolio Construction** | [Risk Sizing Trap](evals/03_portfolio_construction/golden_answers/risk_sizing_trap.md) | Mechanical sizing pitfalls, conviction integration |
| **Assumption Validation** | [Biotech Discount Rate](evals/04_assumption_validation/golden_answers/biotech_discount_rate.md) | Sensitivity analysis, uncertainty quantification |
| **Assumption Validation** | [Commodity Price Assumption](evals/04_assumption_validation/golden_answers/commodity_price_assumption.md) | Forward curve analysis, mean-reversion testing |
| **Assumption Validation** | [Statistical Significance Trap](evals/04_assumption_validation/golden_answers/statistical_significance_trap.md) | p-hacking awareness, multiple comparison correction |
| **Risk Attribution** | [Healthcare L/S Factor Decomposition](evals/05_risk_attribution/golden_answers/healthcare_ls_factor_decomposition.md) | Multi-factor decomposition, residual alpha estimation |
| **Risk Attribution** | [Factor Tilt Attribution](evals/05_risk_attribution/golden_answers/factor_tilt_attribution.md) | Factor tilt vs selection, statistical significance |
| **Research Translation** | [IC Memo → Retail Brief](evals/06_research_translation/golden_answers/ic_memo_to_retail_summary.md) | Jargon simplification, magnitude preservation |
| **Research Translation** | [10-K Risk → Plain English](evals/06_research_translation/golden_answers/10k_risk_section_to_plain_english.md) | Issuer-specific vs boilerplate ranking |
| **M&A Analysis** | [Synergy Sensitivity](evals/09_ma_analysis/golden_answers/merger_model_synergy_sensitivity.md) | Tax-affected pro-forma walk, breakeven |
| **Valuation Synthesis** | [SOTP Conglomerate](evals/10_valuation_synthesis/golden_answers/sotp_conglomerate.md) | Per-segment multiples, corporate cost capitalization |
| **LBO Analysis** | [Returns Bridge Decomposition](evals/11_lbo_analysis/golden_answers/returns_bridge_decomposition.md) | Separate operational from multiple-driven return |
| **Deal Execution** | [Bid Comparison Matrix](evals/12_deal_execution/golden_answers/bid_comparison_process.md) | Certainty-of-close weighting, earn-out probability |

### Rubric Structure

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

### Common AI Failure Modes Tested

Each scenario includes adversarial examples - responses that "sound smart but are wrong":

- **Alpha/Environment Confusion** - Treating environmental tailwinds as company-specific alpha
- **False Certainty** - Embedding unhedged risks into base-case assumptions
- **Backward-Looking Risk** - Using trailing volatility when forward risks dominate
- **Mechanical Responses** - De-risking without diagnosing what risk is being taken
- **Narrative Attribution** - Declaring alpha failure without factor decomposition
- **Notional vs Risk Symmetry** - Dollar-neutral sizing ignoring volatility differentials
- **Hallucinated Data** - Fabricated financial metrics or company facts

### RLHF Studio (Interactive Preference Data)

The `studio/` package provides a Streamlit-based interactive workflow for generating DPO preference pairs from live LLM outputs. Upload a financial PDF, select sections, generate K outputs across different models/temperatures/personas, then rank them to produce training data.

**Two annotation modes:**
- **Single Pair:** Generate one draft → correct it → 1 preference pair
- **K-Ranking:** Generate K outputs (2–9) → rank best→worst → up to K(K-1)/2 pairs per session (e.g., K=4 → 6 pairs)

**Features:** Section-aware PDF parsing (10-K/10-Q), boilerplate filtering, auto-chunking, multi-provider generation (Anthropic/OpenAI/Gemini), rate-limit handling, drag-and-drop ranking.

```bash
# Install studio dependencies
pip install -e ".[studio]"

# Launch the studio (defaults to http://localhost:8501)
streamlit run studio/app.py

# Smoke-test the studio package without launching the UI
pytest tests/test_studio_smoke.py tests/test_studio_ranker.py -v
```

**Studio workflow end-to-end:** upload a 10-K or 10-Q PDF → section-aware parse (`studio/document.py`) → choose up to 3 sections → multi-provider generation across Anthropic/OpenAI/Gemini with configurable temperatures and personas (`studio/generator.py` + `configs.py`) → drag-and-drop K-way ranking in the UI (`studio/ranker.py`) → export pairwise DPO records to JSONL (`studio/storage.py`). See [`studio/README.md`](studio/README.md) for the preference-pair extraction pipeline details.

Both pipelines emit a unified JSONL schema (see [`schemas/preference_pair.json`](schemas/preference_pair.json)):
- `src/extract_pairs.py` → `source: "scenario_anchor"` (batch, from YAML scenarios)
- `studio/ranker.py` → `source: "studio_ranking"` (interactive, from live LLM outputs)

### Use Cases

- **RLHF preference data** - Paired comparisons for reward model training
- **SFT training data** - High-quality examples for supervised fine-tuning
- **Model evaluation** - Standardized benchmarks for financial AI
- **Red teaming** - Adversarial testing for hallucination detection
- **Interactive DPO data** - Live K-ranking across models and personas via RLHF Studio

---

## Architecture

```
investment-workflow-evals/
├── evals/                         # 13 evaluation modules (00_qualification - 12_deal_execution)
│   └── <NN_module>/
│       ├── scenarios/             # YAML scenarios with task prompts + adversarial examples
│       ├── rubrics/               # Weighted YAML rubrics with 5-level anchors + critical failure gates
│       └── golden_answers/        # Markdown expert-level reference responses
├── tools/
│   ├── eval_runner.py             # Run evaluations (supports --models frontier fan-out)
│   ├── grading_engine.py          # Heuristic rubric scorer
│   ├── ai_judge.py                # LLM-as-judge (tool_use, thinking-block-safe, prompt-caching)
│   ├── judge_agreement.py         # Cross-model judge-agreement (Spearman, Cohen's kappa)
│   ├── adversarial_generator.py   # Adversarial-variant stub + perturbation taxonomy
│   ├── benchmark_runner.py        # Frontier benchmark runner, append-only CSV
│   └── generate_gaf.py            # Generate golden answer files via Opus + IRR retrieval
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

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Contributing

Under active development. Contributions welcome — areas for improvement include evaluation scenarios, rubric dimensions, adversarial test cases, and RLHF Studio annotation modes.

## License

MIT License

---

***Curiosity compounds. Rigor endures.***
