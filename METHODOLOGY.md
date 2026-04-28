<!-- METHODOLOGY.md | investment-workflow-evals | Scenario design + rubric methodology -->

# Methodology

This document is a top-level orientation to scenario design, rubric philosophy, and golden-answer discipline. It summarizes the principles and points to the detailed specs in `docs/`. For a single worked scenario end-to-end, see [`SAMPLE_TASK.md`](SAMPLE_TASK.md).

**Scope:** 13 modules spanning the institutional investment-research workflow — from SEC qualification (00) through deal execution (12). Each module ships scenarios (YAML), rubrics (YAML, weighted dimensions with 5-level anchors), golden answers (Markdown), and at least one adversarial example. The framework supports dual use: benchmark evaluation and preference-pair training data for SFT / DPO.

---

## 1. Design philosophy

Institutional investment research has a distinct failure mode: AI-generated output that *sounds competent* — uses the right vocabulary, references the right concepts, tells a fluent story — but would lose money if acted on. The work that matters is not "can the model write a memo," it is "can the model catch the thing that would cost the PM a position." Every design choice flows from this:

1. **Rubric-scored, not vibes-scored.** Weighted dimensions, 5-level anchors, and critical-failure gates. Subjective "good / bad" scoring disagrees across graders and produces aggregated numbers no one should trust.
2. **Adversarial examples are mandatory.** Each scenario ships with a response that sounds intelligent but is substantively wrong, because that is the failure mode that matters. Fluency without rigor is the floor, not the ceiling.
3. **Golden answers set the ceiling.** Expert-written reference responses define what "good" looks like at the institutional bar. The rubric measures distance from that standard.
4. **Dual-use by design.** Scenarios serve both evaluation and training — same data, two purposes. A scenario that can grade a model output can also produce an SFT example or an RLHF preference pair.
5. **Critical failures are automatic fails.** Treating environmental demand as structural alpha, embedding unhedged risks in terminal value, or converting management claims into base-case facts triggers an automatic zero regardless of other dimension scores. These are the errors a PM would fire a junior analyst for.

---

## 2. Module taxonomy

The 13 modules cover the research-to-decision workflow a generalist analyst owns:

| # | Module | What it tests |
|---|---|---|
| 00 | Qualification | SEC filing comprehension, regulatory reference, universe screening |
| 01 | Equity Thesis | Separating conviction in the asset from conviction in the trade |
| 02 | DCF Valuation | Terminal-value discipline, cyclical vs. structural separation, risk placement |
| 03 | Portfolio Construction | Sizing from risk not conviction; correlation under stress |
| 04 | Assumption Validation | Surfacing hidden / unverified assumptions; testing reasonableness |
| 05 | Risk Attribution | Decomposing returns into alpha vs. factor vs. residual |
| 06 | Research Translation | Turning raw filings / transcripts into investment-ready thesis language |
| 07 | Report Review | Critiquing and stress-testing a draft piece of research |
| 08 | Comparable Analysis | Peer selection discipline; multiple methodology; control-premium framing |
| 09 | M&A Analysis | Deal structure, accretion/dilution, synergy credit, execution risk |
| 10 | Valuation Synthesis | Triangulating DCF, comps, precedent transactions into a PT range |
| 11 | LBO Analysis | Returns waterfall, debt schedule, sensitivity on entry / exit |
| 12 | Deal Execution | Timing, crowding, liquidity, risk/reward framing |

Each module carries 2+ scenarios; the scenario count and golden-answer coverage per module live in [`docs/coverage_audit_2026-04.md`](docs/coverage_audit_2026-04.md).

---

## 3. Scenario schema

Source of truth: [`schemas/scenario.yaml`](schemas/scenario.yaml). Every scenario conforms to:

| Field | Purpose |
|---|---|
| `id`, `title`, `version`, `module`, `category`, `difficulty` | Identification and stratification |
| `context` | Company, situation, market conditions, key financials, as-of date |
| `task.prompt` + `task.constraints` | What the model is asked to do and what it must respect |
| `evaluation_criteria.dimensions[]` | Scenario-local dimensions (can inherit or override the module rubric) |
| `evaluation_criteria.critical_failures[]` | Hard-fail gates specific to the scenario |
| `pitfalls[]` | Named failure modes with severity labels |
| `adversarial_example` | A fluent-but-wrong response + reason it fails |
| `key_facts[]` | Facts the answer must engage with, with source and importance |
| `metadata` | Author, created-at, sector focus, tags |

Scenario YAML is validated at test time (see `tests/` and `schemas/`).

---

## 4. Rubric design

Source: [`docs/rubric_design_principles.md`](docs/rubric_design_principles.md) and [`docs/rubric_design_rationale.md`](docs/rubric_design_rationale.md). Summary:

### Weighted dimensions with 5-level anchors

Each rubric defines 3–5 dimensions, each with a weight summing to 100. Every dimension has five score bands — Excellent / Good / Acceptable / Poor / Fail — each with a textual description *and* anchor examples drawn from real graded responses. Anchor examples are what drives inter-grader agreement: a grader never asks "is this 32 or 35?", they ask "does this match the 32–35 anchor or the 25–31 anchor?".

### Critical-failure gates

Any scenario can define 1–N critical-failure gates. A response that matches a gate scores automatic 0 regardless of the weighted-dimension sum. Gates represent the specific errors a PM would fire over — "assumed normalization without any risk compensation", "capitalized cyclical demand into perpetuity", "treated management claims as facts".

### Scoring thresholds

- **Pass:** 70 / 100 (baseline analyst-quality)
- **Excellence:** 85 / 100 (senior-analyst / PM-ready)

### Shared vs. scenario-local rubrics

A module can define a `standard.yaml` rubric that scenarios inherit; scenarios may override or add dimensions. Example: DCF Valuation has a module-level `standard.yaml` (Alpha-vs-Environment / Risk-Treatment / Terminal-Value-Discipline) and scenario-level overrides (MedTech Normalization adds `Judgment Under Uncertainty`).

---

## 5. Golden answers

Each scenario ships a golden answer at `evals/<module>/golden_answers/<scenario>.md`. Principles:

1. **Institutional-grade, not textbook.** Written at the bar expected at a platform hedge fund — thesis, evidence with sources, margin bridge, recommendation, sensitivity, risk factors, upgrade/downgrade criteria.
2. **Probabilistic, not declarative.** Ranges and probability statements throughout; no "guaranteed", "certain", "100%" language.
3. **Specifies the upgrade path.** What evidence would change the rating. This is where the golden separates from the merely correct — naming the falsifiers makes the view operational.
4. **Cross-validated.** Key facts in the golden are tagged to source in the scenario `key_facts[]` block; rubric authors check that goldens actually score at or above the Excellence threshold against the rubric.

---

## 6. Dual use — evaluation and training

Scenarios serve two pipelines sharing one JSONL preference-pair schema ([`schemas/preference_pair.json`](schemas/preference_pair.json)):

### Batch / scenario-anchor pipeline

- Source: `scenario_anchor` responses and goldens.
- Produces SFT examples (golden = chosen) and preference pairs (golden > adversarial, golden > acceptable, acceptable > failing).
- Script: `src/extract_pairs.py`.

### Interactive / studio pipeline

- Source: `studio_ranking`.
- `studio/` is a Streamlit app that generates K responses from multiple providers, has a human ranker K-rank them, and emits pairwise preference pairs.
- Supports Anthropic, OpenAI, Gemini via a provider-inference pattern in `studio/configs.py`.

Both pipelines produce unified records consumable by standard RLHF / DPO training loops.

---

## 7. Frontier benchmark

Source: `BENCHMARK_RUN.md`. The benchmark runner (`tools/benchmark_runner.py`) sweeps (module × scenario × model) combinations, appends one row per run to `results/frontier_benchmark_v1.csv`, and — via `tools/judge_agreement.py` — computes Spearman, Cohen's κ, and per-dimension Pearson between model-judged and human-judged score pairs to validate judge reliability.

The leaderboard is scenario-model-scored, not headline-number-scored: per-module mean overall scores across scenarios, with overlap regions in the confidence intervals where SKUs sit close. Do not read the board as a ranking; read it as a map of where each model breaks.

---

## 8. Ground-truth discipline and known limitations

Stated, not papered over:

1. **Synthetic companies, real mechanics.** Tickers and company names are fictional ("Surgical Dynamics Corp / SDC"). Accounting structures, valuation mechanics, and sector dynamics are not.
2. **Golden-answer concentration.** Per `docs/coverage_audit_2026-04.md`, not all 60 scenarios have full goldens yet; coverage is deepest in 00, 01, 02, 08, 11. Expanding.
3. **Rubric-override burden.** When a scenario materially extends the module rubric (adding a fourth dimension), the scenario's `evaluation_criteria` block becomes the source of truth for that scenario. The runner prefers scenario-local when both exist.
4. **Adversarial cadence.** One adversarial per scenario today. Plan to add second-order adversarials (plausible-but-wrong *and* confidently-presented) that stress the probabilistic-language rubric specifically.
5. **No live market data.** Scenarios are `as_of_date`-stamped and use the data embedded in `context.key_financials`. Valuation mechanics are exercised, not live screens.

---

## 9. Key files

| File | Purpose |
|---|---|
| `schemas/scenario.yaml` | Scenario schema (validated at test time) |
| `schemas/preference_pair.json` | Unified SFT / RLHF preference-pair schema |
| `evals/<NN_module>/scenarios/*.yaml` | Scenario source |
| `evals/<NN_module>/rubrics/*.yaml` | Module-level rubrics |
| `evals/<NN_module>/golden_answers/*.md` | Expert reference responses |
| `tools/eval_runner.py` | Per-scenario evaluation CLI |
| `tools/grading_engine.py` | Rubric scoring engine (weighted dimensions + gates) |
| `tools/benchmark_runner.py` | Frontier-model benchmark sweep |
| `tools/judge_agreement.py` | Cross-judge reliability (Spearman, κ, Pearson) |
| `studio/app.py` | Interactive RLHF Studio (Streamlit) |
| `src/extract_pairs.py` | Batch preference-pair extraction |
| `docs/methodology.md` | Deep-dive companion to this file |
| `docs/rubric_design_principles.md` | Rubric philosophy in detail |
| `docs/rubric_design_rationale.md` | Why this structure over alternatives |
| `docs/coverage_audit_2026-04.md` | Per-module coverage audit |
| `docs/model_failure_analysis.md` | Observed failure patterns across runs |
| [`SAMPLE_TASK.md`](SAMPLE_TASK.md) | One worked scenario, end-to-end, portable |
