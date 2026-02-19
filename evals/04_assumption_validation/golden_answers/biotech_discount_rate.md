# Golden Answer: Biotech Discount Rate Assumption Challenge

## Assumption Extraction

### Explicit Assumptions
1. **WACC: 10.5%** — derived from CAPM (beta 1.2, Rf 4.3%, ERP 5.5%)
2. **Terminal growth: 3.0%** — applied to drug portfolio cash flows
3. **Revenue onset: 2027E** — Phase 3 drug only in base case
4. **Peak revenue: $2.8B by 2032E** — single drug driving all revenue
5. **R&D spend: 35% → 18%** — declining as percentage of revenue
6. **Cash runway: 14 months** at $180M/quarter burn

### Implicit Assumptions (Not Stated but Embedded)
7. **Probability of approval: 100%** — full revenue in base case with no probability weighting
8. **No equity dilution** — despite 14-month runway, WACC does not adjust for dilution cost
9. **No pipeline attrition** — Phase 2 candidates not modeled but also not written down
10. **Partnership value: $0** — management guided to ex-US partnership but model ignores

---

## Reasonableness Assessment

### WACC: 10.5% — **Aggressive (Red Flag)**

| Benchmark | Value | Source |
|-----------|-------|--------|
| Pre-revenue biotech peer discount rates | 12–18% | Comparable set provided |
| CAPM-implied with clinical-stage beta (2.0–2.5x) | 15.3–18.0% | Beta adjustment |
| Venture capital implied rates for Phase 2/3 | 20–30% | Industry standard |

The 10.5% WACC uses a beta of 1.2, which is appropriate for a large-cap diversified biotech (Amgen, Gilead), not a pre-revenue clinical-stage company. Clinical-stage biotechs exhibit idiosyncratic binary risk (approval/rejection) that CAPM beta does not capture. A more defensible WACC range is **14–16%**, using a beta of 2.0–2.5x.

### Terminal Growth: 3.0% — **Aggressive**

A 3% terminal growth rate on a single-drug portfolio with patent expiration is structurally flawed. Biologics face biosimilar competition 12–15 years post-launch. With revenue onset in 2027 and patent expiry likely in 2037–2040, the terminal value should reflect declining revenue, not perpetual growth. A defensible terminal growth rate is **0–1%**, or alternatively, use an explicit patent-cliff terminal year rather than a Gordon Growth Model.

### Revenue: $2.8B Peak, 100% PoA — **Structural Flaw**

The base case embeds 100% probability of approval without stating it. Historical Phase 3 success rates for rare disease drugs are approximately 55–65%. Without probability weighting:
- The model implicitly values the drug as if it is already approved
- A probability-adjusted base case should use **60% PoA**, reducing expected peak revenue to ~$1.7B

### Cash Runway: 14 Months — **Red Flag (Ignored in WACC)**

At $180M/quarter burn ($720M annualized) and 14-month runway, the company must raise capital within 6–8 months (allowing for deal timeline). This means:
- Equity dilution is near-certain and not reflected in the share count or WACC
- A secondary offering at current levels could dilute shareholders by 15–25%
- The CFO sold 40% of holdings in Q4 — a negative signal about near-term outlook

---

## Sensitivity Analysis

### WACC Sensitivity (Holding All Else Constant)

| WACC | NPV Index (Base = 100) | Implied Change |
|------|------------------------|----------------|
| 10.5% (base) | 100 | — |
| 12% | 82 | -18% |
| 14% | 63 | -37% |
| 16% | 49 | -51% |

**WACC dominates valuation uncertainty.** A 3.5 percentage point increase (10.5% → 14%) reduces NPV by approximately 37%.

### Probability of Approval Sensitivity

| PoA | Expected Peak Revenue | NPV Index |
|-----|----------------------|-----------|
| 100% (base) | $2.8B | 100 |
| 75% | $2.1B | 75 |
| 60% | $1.7B | 60 |
| 45% | $1.3B | 45 |

At a more realistic 60% PoA combined with 14% WACC, the implied NPV is approximately **36% of the analyst's base case** (0.60 × 0.63 ≈ 0.38).

---

## Red Flags

1. **Structural: 100% PoA in base case** — This is not an aggressive assumption; it is a methodology error. All biotech DCFs should probability-weight clinical outcomes.

2. **Structural: WACC sourced from wrong peer set** — Using large-cap biotech beta (1.2) for a pre-revenue company produces a discount rate disconnected from the company's risk profile.

3. **Inconsistency: Cash runway vs. no dilution** — The model assumes 14-month runway but does not model the required equity raise. This creates an internal inconsistency: either the company raises capital (diluting shareholders) or it runs out of cash (zero value).

4. **Signal: CFO insider selling** — 40% of holdings sold in Q4 is a negative signal that should increase skepticism about near-term catalysts, not decrease it.

5. **RTF history** — A prior Refuse-to-File letter increases regulatory risk above base rates. PoA should be adjusted downward from the 60% starting point.

---

## Recommended Adjustments

| Assumption | Analyst | Recommended | Justification |
|-----------|---------|-------------|---------------|
| WACC | 10.5% | 14–16% | Pre-revenue biotech peer range |
| Beta | 1.2 | 2.0–2.5 | Clinical-stage, binary outcome |
| PoA | 100% (implicit) | 50–55% | Phase 3 base rate minus RTF penalty |
| Terminal growth | 3.0% | 0–1% | Patent cliff on single-drug portfolio |
| Dilution | None | 15–25% | 14-month runway requires near-term raise |
| Peak revenue | $2.8B | $1.4–1.5B (PoA-adjusted) | 50–55% × $2.8B |

**Net impact:** These adjustments would reduce the analyst's NPV by approximately **60–70%**, suggesting the current model significantly overstates fair value.
