# Golden Answer: Commodity Price Assumption Challenge - Permian Resources Corp E&P Model

## Assumption Extraction

### Explicit Assumptions
1. **WTI crude: $85/bbl flat through 2026E-2030E** -- used for all revenue projections
2. **Natural gas (Henry Hub): $4.50/MMBtu flat through forecast period** -- used for gas revenue
3. **NGL realization: 35% of WTI** -- NGL pricing assumption
4. **Basis differential: -$2.50/bbl (Midland-Cushing)** -- netback adjustment
5. **EBITDA margin: 62% stable throughout** -- derived from commodity deck
6. **Transaction costs: 10bps per side** -- embedded in FCF calculation

### Implicit Assumptions (Not Stated, But Embedded)
7. **The forward curve is wrong by $11-20/bbl for oil and $0.70-1.30 for gas** -- analyst implicitly rejects the market's pricing
8. **Commodity prices do not mean-revert** -- flat deck through 2030 assumes no cyclical correction
9. **OPEC+ maintains discipline** -- $85 requires continued production restraint despite slipping compliance
10. **US production growth does not weigh on prices** -- record 13.4 MMbbl/d is not modeled as bearish
11. **Hedge book validates the commodity view** -- but hedges are set at $72-84, below the model deck
12. **Terminal value is calculated at $85 oil** -- inflating the perpetuity

---

## Reasonableness Assessment

### WTI Crude: $85/bbl Flat -- AGGRESSIVE (Red Flag)

| Benchmark | Price | Gap to Model | Source |
|-----------|-------|-------------|--------|
| Current spot | $78/bbl | +$7 (+9%) | Market data |
| 12-month forward | $74/bbl | +$11 (+15%) | CME/NYMEX futures |
| 24-month forward | $68/bbl | +$17 (+25%) | CME/NYMEX futures |
| 36-month forward | $65/bbl | +$20 (+31%) | CME/NYMEX futures |
| 5-year historical average | ~$72/bbl | +$13 (+18%) | EIA data |
| 10-year historical average | ~$65/bbl | +$20 (+31%) | EIA data |

The forward curve is in backwardation -- the market is pricing *declining* oil prices, not stable or rising. Using $85 flat through 2030 means the analyst believes the market is wrong by $11/bbl in year one and $20/bbl in year three. This requires an explicit bull case justification that the model does not provide.

**Bearish signals the model ignores:**
- US production at record 13.4 MMbbl/d and rising -- the supply response at current prices is strong
- OPEC+ compliance slipping -- the cartel's ability to constrain supply is weakening
- Forward curve backwardation is a structural signal of expected oversupply
- No geopolitical disruption premium is justified at $85 without a specific identified risk

**Recommended base case:** Use the forward curve: $74 (year 1), $68 (year 2), $65 (year 3+). Treat $85 as the bull case, not the base case.

### Natural Gas: $4.50/MMBtu Flat -- AGGRESSIVE

| Benchmark | Price | Gap to Model | Source |
|-----------|-------|-------------|--------|
| Current spot | $3.20/MMBtu | +$1.30 (+41%) | Henry Hub |
| 12-month forward | $3.80/MMBtu | +$0.70 (+18%) | CME/NYMEX futures |
| 5-year average | ~$3.50/MMBtu | +$1.00 (+29%) | EIA data |

The $4.50 assumption is 41% above spot and 18% above the 12-month forward. While LNG export capacity additions in 2026-2027 could support higher gas prices, embedding $4.50 as the base case is aggressive. LNG demand uplift is a potential tailwind, not a base-case certainty.

**Additionally:** 0% of natural gas production is hedged, meaning the model's gas revenue projections have zero downside protection.

**Recommended base case:** $3.80 (year 1, per forward curve), declining to $3.50 (year 2+). Treat $4.50 as a bull case.

### NGL Realization: 35% of WTI -- REASONABLE

NGL realization at 35% of WTI is within the historical 30-40% range. However, because NGL revenue is a function of the WTI assumption, the $85 deck inflates NGL revenue proportionally. At forward-curve oil prices, NGL revenue would be 15-25% lower.

### Basis Differential: -$2.50/bbl -- REASONABLE TO SLIGHTLY OPTIMISTIC

The Midland-Cushing spread has narrowed with Permian pipeline capacity additions but can widen during high-production periods. A -$2.50 assumption is defensible, though -$3.00 to -$3.50 may be more conservative for sustained record Permian output.

---

## Sensitivity Analysis

### Oil Price Sensitivity (Key Driver)

| WTI Price | EBITDA Margin | FCF Yield (2026E) | Net Debt/EBITDA | vs. Model Base |
|-----------|--------------|-------------------|-----------------|----------------|
| $85 (model) | 62% | 14% | 0.8x | Baseline |
| $78 (spot) | 57% | 11% | 1.0x | Margin -5ppts, FCF -3ppts |
| $74 (12mo fwd) | 54% | 9% | 1.2x | Margin -8ppts, FCF -5ppts |
| $68 (24mo fwd) | 49% | 6% | 1.6x | Margin -13ppts, FCF -8ppts |
| $65 (36mo fwd) | 46% | 5% | 1.9x | Margin -16ppts, FCF -9ppts |
| $55 (stress) | 37% | 1% | 3.2x | Severe; near-breakeven |
| $42 (breakeven) | ~0% | ~0% | N/A | Maintenance production only |

**Every $5/bbl change in WTI alters EBITDA margin by approximately 3-4 percentage points and FCF yield by approximately 1.5-2 percentage points.** The sensitivity is highly material -- the difference between the model's $85 and the 24-month forward of $68 translates to roughly 13 percentage points of EBITDA margin compression and 8 percentage points of FCF yield erosion.

### Natural Gas Sensitivity

| Henry Hub | Incremental EBITDA Impact | Revenue Impact |
|-----------|--------------------------|---------------|
| $4.50 (model) | Baseline | Baseline |
| $3.80 (12mo forward) | -3 to -4% margin | ~$350M revenue reduction |
| $3.20 (spot) | -5 to -7% margin | ~$650M revenue reduction |
| $2.50 (stress) | -8 to -10% margin | ~$1.0B revenue reduction |

### Combined Oil + Gas Sensitivity

| Scenario | WTI | Henry Hub | EBITDA Margin | FCF Yield | Leverage |
|----------|-----|-----------|---------------|-----------|---------|
| Analyst model | $85 | $4.50 | 62% | 14% | 0.8x |
| Forward curve | $74 | $3.80 | 50-52% | 7-8% | 1.2-1.4x |
| Spot prices | $78 | $3.20 | 52-54% | 8-9% | 1.0-1.2x |
| Bear case | $60 | $2.75 | 38-40% | 1-2% | 2.5-3.0x |

**At forward-curve pricing, the company's FCF yield drops from 14% to 7-8%.** This is still positive, but it is a fundamentally different investment thesis. At 14% FCF yield, the stock screens as deeply undervalued. At 7-8%, it screens as fairly valued at best.

---

## Red Flags

### 1. Structural: Flat Commodity Deck Inflates Terminal Value (Critical)

In a standard E&P DCF, years 4-5 and the terminal value typically account for 60-70% of total equity value. By embedding $85 oil into the perpetuity, the analyst prices in a permanent commodity premium that the forward curve explicitly rejects. The terminal value alone may be overstated by 30-50%.

**Using the forward curve for years 1-3 and a long-run equilibrium price of $65-70 for the terminal value would reduce the DCF output by approximately 25-40%.**

### 2. Structural: Hedge Book Contradicts the Model (Important)

The company's own hedge book undermines the $85 assumption:
- Management hedged 60% of 2026 oil at $72-84 costless collars
- If management believed $85+ was sustainable, they would not lock in $72-84 ceilings
- The hedge book reveals management's *revealed preference* for protecting at lower prices
- 0% of gas is hedged, leaving the $4.50 assumption fully exposed to spot risk
- No hedges beyond 2026, meaning years 2-5 of the model have zero downside protection

### 3. Missing: No Sensitivity Analysis Provided (Important)

The omission of commodity sensitivity tables is itself a red flag. For an E&P model where 80%+ of revenue is commodity-driven, sensitivity analysis is not optional -- it is the minimum standard. The absence suggests the analyst either has not stress-tested the thesis or is aware that the thesis weakens materially at lower prices and chose not to disclose it.

### 4. Inconsistency: OPEC+ Signals vs Price Assumption (Moderate)

The context notes OPEC+ compliance is slipping. Declining discipline typically leads to increased production and lower prices, not higher. The $85 assumption implicitly requires OPEC+ to maintain or increase discipline, which contradicts the observable trend.

### 5. Signal: Record US Production (Moderate)

US production at 13.4 MMbbl/d represents a strong supply response to current prices. Continued US growth creates a structural headwind for prices above $70-75. The model's $85 deck assumes this supply growth either stops or is offset by demand growth -- neither of which is supported by the provided context.

---

## Recommended Adjustments

| Assumption | Analyst | Recommended Base Case | Justification |
|-----------|---------|----------------------|---------------|
| WTI crude | $85 flat | $74/$68/$65 (per forward curve) | Forward curve is the default; deviation requires justification |
| Natural gas | $4.50 flat | $3.80/$3.50/$3.50 | Forward curve + mean reversion |
| NGL realization | 35% of WTI | 35% of corrected WTI | Same percentage, lower base |
| Basis differential | -$2.50 | -$3.00 | Slight widening at record production |
| Terminal oil price | $85 implied | $65-70 | Long-run equilibrium |

### Net Valuation Impact

| Metric | Analyst Model | Forward-Curve Model | Difference |
|--------|--------------|--------------------|-----------|
| EBITDA margin (2026E) | 62% | 50-52% | -10 to -12 ppts |
| FCF yield (2026E) | 14% | 7-8% | -6 to -7 ppts |
| Leverage (2026E) | 0.8x | 1.2-1.4x | +0.4-0.6x |
| Enterprise value | ~$12.5B | ~$9.0-9.5B | -24 to -28% |
| Equity value | ~$11.0B | ~$7.5-8.0B | -27 to -32% |

**The analyst's model overstates equity value by approximately 27-32% relative to forward-curve-based assumptions.** This is not a minor calibration issue -- it is a structural overvaluation driven by a single, unsupported commodity deck assumption.

---

## Position Sizing Implications

### Do Not Size on the Analyst's Model

A position sized on 14% FCF yield (analyst deck) will be 2x too large relative to the true risk/reward at 7-8% FCF yield (forward curve). The analyst's model creates a false sense of deep value that does not exist at market-implied commodity prices.

### Entry Framework

| Condition | Action | Rationale |
|-----------|--------|-----------|
| Stock offers 10%+ FCF yield at forward-curve prices | Buy 1-2% position | Genuine value with margin of safety |
| Stock offers 7-8% FCF yield at forward-curve prices | Monitor, do not buy | Fair value; no edge |
| Stock only works at $85 oil | Avoid | Thesis depends on above-market commodity prices |
| Forward curve shifts above $80 | Revisit at larger size | Market confirming tighter supply/demand |

### What the Analyst Should Fix

1. **Replace flat deck with forward curve as base case.** $74/$68/$65 per the 12/24/36-month curve
2. **Model gas at $3.80 (12-month forward)**, not $4.50
3. **Add sensitivity tables** at $60, $65, $70, $75, $80, $85 WTI
4. **Incorporate the hedge book properly:** 2026 revenues partially protected at $72-84; 2027-2030 fully exposed to spot
5. **Provide scenario analysis:** Bull ($80+), Base (forward curve), Bear ($55-60)
6. **Separate the commodity view from the company view.** If the thesis is "this is a well-run Permian operator," demonstrate it at forward-curve prices, not at above-market assumptions. Good operators should screen attractively at market prices.

---

## Monitoring Metrics

1. **WTI forward curve shape and level:** Track weekly; backwardation vs contango signals supply/demand balance
2. **Henry Hub forward curve:** Monitor LNG export demand impact on forward gas prices
3. **OPEC+ compliance rates:** Monthly production data vs quotas; discipline deterioration is bearish
4. **US weekly production (EIA):** Record production constrains price upside; monitor trajectory
5. **Permian basin rig count:** Leading indicator of future supply growth
6. **Company hedge disclosures:** Management locking in hedges below $85 is a revealed signal they do not believe their own bull case
7. **Basis differential (Midland-Cushing):** Widening would further erode realizations below the model

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Forward-curve-based commodity assumption validation with multi-scenario sensitivity analysis
