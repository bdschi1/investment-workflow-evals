<!-- SAMPLE_TASK.md | investment-workflow-evals | Portable scenario walkthrough -->

# Sample Task: MedTech Margin Normalization — Cyclical vs. Structural

A complete worked scenario from this benchmark, presented end-to-end: prompt, rubric, golden answer summary, three anchor responses at different quality levels, adversarial variant, and metadata. This single file is self-contained so it can be shared without the rest of the repo. The canonical sources are:

- Scenario: [`evals/02_dcf_valuation/scenarios/medtech_normalization.yaml`](evals/02_dcf_valuation/scenarios/medtech_normalization.yaml)
- Rubric: [`evals/02_dcf_valuation/rubrics/standard.yaml`](evals/02_dcf_valuation/rubrics/standard.yaml)
- Golden answer: [`evals/02_dcf_valuation/golden_answers/medtech_normalization.md`](evals/02_dcf_valuation/golden_answers/medtech_normalization.md)

- **Module:** 02 — DCF Valuation
- **Category:** Healthcare valuation
- **Difficulty:** Hard
- **Estimated time for a human grader:** ~40 minutes
- **Target failure modes:** `false_certainty`, `anchoring_bias`, `insufficient_skepticism`, `cyclical_structural_confusion`
- **Authoring standard:** institutional-grade equity research

---

## 1. Scenario

### Context

| Field | Value |
|---|---|
| Company | Surgical Dynamics Corp (synthetic) |
| Ticker | SDC |
| Sector | Healthcare — Medical Devices |
| Market cap | ~$12B |
| Revenue (TTM) | $4.8B |
| Current EBITDA margin | 18% |
| Historical peak EBITDA margin | 26% |
| Management's target EBITDA margin | 28% |
| Procedure volumes vs. 2019 | 85% |
| Hospital utilization vs. 2019 | 85% |
| As-of date | 2024-12-15 |

**Situation.** The company is emerging from a downturn driven by elective-procedure deferrals. Margins sit well below historical averages due to volume deleverage and labor inefficiencies. Management claims structural improvements (manufacturing automation, mix shift into robotics, SKU rationalization, improved sales-force productivity) will support higher margins. Utilization at customer hospitals remains 15% below pre-pandemic levels; staffing shortages persist. Competitors are making similar structural-improvement claims.

**Margin bridge provided:**

| Driver | Impact | Character |
|---|---|---|
| Volume deleverage | −4% | Cyclical |
| Labor inflation | −2% | Mixed |
| Mix shift | −1% | Transitional |
| Automation benefit (claimed) | +3% | Structural (unverified) |
| SKU rationalization (claimed) | +1% | Structural (partially verified) |

### Task

Explain how a valuation framework should distinguish cyclical mean reversion from true structural improvement, and where uncertainty should be reflected. Address:

1. How to separate utilization recovery from operational improvement.
2. Where to allocate uncertainty — in forecasts, terminal assumptions, or the discount rate.
3. How to treat normalization as a probabilistic outcome, not a base-case fact.
4. What evidence would distinguish cyclical recovery from genuine structural improvement.

**Constraints.** Must separate cyclical vs. structural drivers. Must not embed certainty into normalized margins. Must treat normalization probabilistically. Must specify where uncertainty is reflected.

---

## 2. Grading rubric

The rubric uses three weighted dimensions (totaling 100 points) with 5-level anchored scoring, plus a critical-failure gate. Full rubric at [`evals/02_dcf_valuation/rubrics/standard.yaml`](evals/02_dcf_valuation/rubrics/standard.yaml); applied to this scenario via the scenario-local `evaluation_criteria` block.

### Dimension 1 — Cyclical vs. Structural Identification (weight 35)

| Score band | Label | Requires |
|---|---|---|
| 32–35 | Excellent | Explicitly separates utilization recovery from operational improvement; identifies volume-dependent drivers; distinguishes temporary labor dynamics from permanent resets; notes competitors claim similar improvements |
| 25–31 | Good | Identifies the distinction, may miss some nuances but no major conflation |
| 18–24 | Acceptable | Aware of distinction, treatment superficial; hedges without framework |
| 10–17 | Poor | Minimal distinction; treats recent performance as durable advantage |
| 0–9 | Fail | Conflates tailwinds with alpha; capitalizes cyclical demand into perpetuity |

### Dimension 2 — Risk Placement (weight 35)

Allocates uncertainty across forecast period, terminal assumptions, and discount rate. Avoids embedding certainty into normalized margins. Does not treat historical margins as automatic destiny. Specifies the mechanism for reflecting uncertainty.

### Dimension 3 — Judgment Under Uncertainty (weight 30)

Treats normalization as probabilistic. Does not convert management claims into base-case facts. Identifies what evidence would validate structural improvement. Maintains intellectual honesty about unknowns.

### Critical failure gates (automatic 0)

- Implicitly hedged nothing while assuming full margin recovery.
- Converted historical margins into automatic destiny.
- Treated management claims as facts without a verification framework.
- Assumed normalization without any risk compensation.

**Pass threshold:** 70 / 100. **Excellence:** 85 / 100.

---

## 3. Golden answer — compressed

Full answer (~1,800 lines) at [`evals/02_dcf_valuation/golden_answers/medtech_normalization.md`](evals/02_dcf_valuation/golden_answers/medtech_normalization.md). Key moves:

**Thesis.** The 800bps margin gap blends two recovery vectors — utilization normalization (partially under way, 65–75% probable over 2–3 years) and structural improvement (management-claimed, unverified). A credible valuation decomposes them rather than collapsing both into a single normalized base case.

**Decomposed margin bridge (recovery probabilities assigned):**

| Driver | Impact | Classification | Recovery probability |
|---|---|---|---|
| Volume deleverage | −4.0% | Cyclical | 65–75% over 2–3 years |
| Labor inflation | −2.0% | Mixed (50/50) | 30–50% partial recovery |
| Mix shift | −1.0% | Transitional | 50–60% (depends on robotics adoption) |
| Automation benefit (claimed) | +3.0% | Structural (unverified) | 30–40% at full magnitude |
| SKU rationalization (claimed) | +1.0% | Structural (partially verified) | 50–60% |

**Risk placement.** Cyclical component → explicit-period revenue/margin assumptions, not terminal. Structural component → conservative terminal margin with optionality priced separately, not embedded. Labor inflation → discount-rate adjustment for residual uncertainty, because the cyclical/structural split is itself unknown.

**Evidence that would upgrade the structural view:** sustained margin improvement at flat volumes; SKU-rationalization proof by product-line gross margin disclosure; competitor dispersion on margin recovery (industry-wide claims mean industry-wide cost inflation, not differentiation).

**Recommendation framing.** Neutral / underweight with 1–2% position at most; upgrade to buy only on evidence-based margin inflection. Target range $35 (bear) / $52 (base) / $68 (bull).

---

## 4. Anchor responses

### Strong (≈ 90 / 100)

> The 800bps EBITDA margin gap between current 18% and management's 28% target should be decomposed before it enters any base case. Cyclical volume recovery (the −4% deleverage and part of the mix shift) is partially under way, mean-reverts with moderate confidence (~65–75% over 2–3 years), and should land in the explicit forecast period. Structural claims (+3% automation, +1% SKU) are unverified, and competitors are making identical claims — which suggests these reflect industry-wide cost-inflation offsets rather than company-specific alpha. Those belong in an upside case, not the base, and only enter the base once we see evidence: sustained margin improvement at flat volumes, or product-line-level gross-margin expansion that cannot be explained by volume. Labor inflation (−2%) sits awkwardly between cyclical and structural and should be treated as an explicit discount-rate add-on rather than resolved into either bucket. Terminal margin should be capped well below management's 28% — historical peak 26% is the outside bound, and only if structural claims are validated. Treating normalization as inevitable would capitalize a 30–40%-probability outcome as a 100% base case. Recommendation: neutral, conservative base case with upside optionality priced separately, not embedded.

- Clean cyclical/structural split with explicit probability framing.
- Risk placement named explicitly (forecast period / terminal / discount rate).
- Evidence criteria for upgrade stated.
- Competitor-claim skepticism applied.
- Avoids false certainty; avoids historical-peak anchoring.

### Acceptable (≈ 65 / 100)

> Current margins are depressed because volumes are depressed. As volumes recover, margins should improve. Management's automation and SKU initiatives are a plus but probably take longer than guided. I would use the historical 26% as the terminal margin and discount back; management's 28% target seems aggressive without evidence.

- Directionally correct, but collapses cyclical and structural into a single recovery story.
- Uses historical peak as terminal without justifying why.
- Does not specify where uncertainty sits.
- Does not engage the competitor-claim pattern at all.

### Failing — adversarial variant (≈ 25 / 100 or automatic 0 via gate)

> Given historical margins and management's automation initiatives, it is reasonable to assume full margin normalization over the next several years, with the DCF capturing this through a return to prior peak margins.

- Converts history into destiny.
- Ignores uncertainty in utilization recovery.
- Assumes normalization without risk compensation.
- Treats management initiatives as accomplished facts.

This response triggers the "assumed normalization without any risk compensation" critical-failure gate and scores automatic 0 regardless of other dimension scores.

---

## 5. Metadata

| Field | Value |
|---|---|
| Scenario ID | `medtech_normalization` |
| Module | `02_dcf_valuation` |
| Difficulty | `hard` |
| Scenario version | 1.0.0 |
| Rubric version | 1.0.0 |
| Total points | 100 |
| Pass threshold | 70 |
| Excellence threshold | 85 |
| Critical-failure gates | 4 |
| Authored by | domain expert, CFA |

---

## How this scales across the benchmark

This is one scenario from module 02 (DCF Valuation), one of 13 modules spanning the institutional analyst workflow — from 00_qualification through 12_deal_execution. Each module carries 2+ scenarios, weighted-dimension rubrics with 5-level anchors, golden answers, and at least one adversarial example. Scenarios feed both evaluation (benchmark model quality) and training (SFT examples, RLHF preference pairs via `studio/`). See [`README.md`](README.md) for the full module matrix and [`METHODOLOGY.md`](METHODOLOGY.md) for scenario-design principles, rubric philosophy, and golden-answer discipline.
