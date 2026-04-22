

# Portfolio Construction Memo: Post-Earnings Position Doubling Proposal

## Executive Summary

**Recommendation**: REJECT the proposed doubling. Approve a modest notional add of ~$15M (to $65M / 8.1% NAV), contingent on execution over 5-7 trading days.

**One-sentence thesis**: The analyst's fundamental conviction may be correct, but the position has already doubled in risk-contribution terms from volatility expansion alone — doubling notional on top would create ~4x the original risk budget allocation, breach sector limits, and convert a differentiated alpha bet into a concentrated systematic factor exposure.

---

## Risk Contribution Analysis: Why 2x Notional ≈ 4x Risk

### The Math the Analyst Is Missing

Risk contribution scales with both notional and volatility. The standard approximation:

**Risk Contribution ≈ Notional × Volatility × Correlation to Portfolio**

| Metric | Pre-Earnings | Post-Earnings (No Add) | Proposed (Doubled) |
|---|---|---|---|
| Notional ($M) | $50 | $50 | $100 |
| Annualized Vol | 35% | 65% | 65% |
| Dollar Vol ($M) | $17.5 | $32.5 | $65.0 |
| Beta to SPY | 1.3 | 1.8 | 1.8 |
| Relative Risk Contribution (indexed) | 1.0x | ~1.9x | ~3.7x |
| Approximate VaR Contribution (95%, 1-day, $M)¹ | $2.9 | $5.3 | $10.7 |

¹ Simplified: 1.65 × daily vol × notional. Daily vol = annual vol / √252.

**Key insight**: The vol expansion from 35% to 65% has *already* nearly doubled the position's risk contribution without any trade. The position is already "oversized" relative to its original risk budget. Doubling notional on top of that produces ~3.7x the original risk contribution — approximately **4x** when accounting for the increased beta and correlation effects at the portfolio level.

The analyst is proposing to quadruple the risk allocation to a single name. That requires a fundamentally different approval threshold than "the quarter was good."

### Vol-Adjusted Equivalent Sizing

To maintain the **same risk contribution** as the original $50M / 35% vol position, the correct notional at 65% vol is:

> $50M × (35% / 65%) = **~$26.9M**

The position should arguably be *trimmed* to hold risk constant. At minimum, the vol expansion must be acknowledged as an implicit position increase.

---

## Systematic Risk Shift: The Character of the Bet Has Changed

### Idiosyncratic → Factor Exposure

| Risk Decomposition | Pre-Earnings | Post-Earnings |
|---|---|---|
| Idiosyncratic variance share | 65% | 40% |
| Systematic variance share | 35% | 60% |
| Correlation to AI basket | 0.45 | 0.78 |
| Beta to SPY | 1.3 | 1.8 |

This is not a cosmetic shift. Pre-earnings, the position was majority-idiosyncratic — the fund was being paid for stock-specific insight. Post-earnings, 60% of the variance is systematic. The stock now moves largely in lockstep with the AI basket (ρ = 0.78).

**Three consequences the analyst must confront:**

1. **Diversification benefit collapsed.** At ρ = 0.78 to the AI basket, this position is no longer additive to a portfolio that likely already has AI exposure through other semiconductor, cloud, or infrastructure holdings. Every dollar added here is ~$0.78 correlated to the AI theme.

2. **Factor risk is not alpha.** The analyst's thesis — strong revenue, raised guidance — may be correct. But the market has re-priced this stock as an AI-beta vehicle. The fund is no longer capturing idiosyncratic mispricing; it is taking a leveraged bet on the AI investment cycle. That bet can be obtained more cheaply and liquidly via index/ETF instruments or options.

3. **Beta amplification.** At β = 1.8, a 5% SPY drawdown translates to a ~9% hit on this name. On a $100M position, that is $9M or ~113bps of NAV from a single broad-market move — before any stock-specific risk.

**The fundamental thesis may be intact, but the risk character of the position has materially changed.** The analyst is implicitly proposing to increase the fund's AI-factor loading by ~4x, not just its exposure to one company.

---

## Portfolio Constraint Check

### Sector Concentration

| Constraint | Current | Post-Add (Proposed) | Limit |
|---|---|---|---|
| Tech sector (% gross) | 26% | ~32.25%¹ | 30% |
| Single-name (% NAV) | 6.25% | 12.5% | Likely 10%² |

¹ Assumes $800M gross, adding $50M tech notional: (208 + 50) / 800 = 32.25%. Even adjusting for gross expansion, this likely breaches.
² Most institutional mandates cap single-name at 10% NAV; scenario implies $800M NAV.

**The proposed add breaches the 30% tech sector limit.** This is a hard constraint, not a guideline. Full stop — the trade as proposed is not permissible without either (a) reducing other tech exposure by at least ~$18M, or (b) obtaining a formal limit exception from the risk committee.

Even a partial add to $75M (9.4% NAV) would push tech to ~29.1%, leaving essentially zero headroom for any other tech position adjustment.

### Single-Name Concentration

At 12.5% of NAV, this would likely be the fund's largest position by a wide margin. Concentration at this level in a name with 65% realized vol implies the position alone could generate daily P&L swings of ±$4.2M (1σ) or ±$10.7M (2.5σ) — representing 53bps to 134bps of NAV from a single holding on any given day.

---

## Market Impact & Execution

### Execution Realities for a $50M Add

| Parameter | Estimate |
|---|---|
| Post-earnings ADV multiple | ~3x normal (elevated) |
| Normalization timeline | 5-7 trading days |
| Estimated participation rate at $50M / 5 days | Depends on ADV, but likely 5-15% of daily volume |
| Estimated market impact (elevated vol regime) | 30-80bps adverse, potentially higher as volume normalizes |
| Spread widening post-earnings | Likely 20-40% wider than normal |

**Critical execution risk**: The analyst likely assumes current elevated volume persists, enabling clean execution. Post-earnings volume spikes are transient — typically normalizing within 5-7 days. If the fund attempts to build the full $50M add in the first 2-3 days of elevated volume, it may achieve reasonable fills. But if execution extends beyond the volume normalization window, the remaining shares will be purchased into thinner books at wider spreads, with the fund's own buying pressure contributing to adverse price movement.

At 65% realized vol, the stock is moving ~4.1% per day (1σ). Execution slippage compounds rapidly in this regime.

**Recommendation**: Any approved add should be executed via VWAP/TWAP algorithms over 5-7 days, front-loaded into the elevated-volume window, with a hard stop if realized vol exceeds 75% or if the stock appreciates more than 8% during the execution window (reducing the remaining risk/reward).

---

## Recommended Sizing Framework

### Step 1: Determine Risk Budget, Not Conviction Budget

The original position was sized at $50M / 35% vol, implying a dollar-vol allocation of ~$17.5M. The risk committee approved this level of risk contribution.

### Step 2: Vol-Adjust for Current Regime

| Sizing Approach | Notional | Dollar Vol | Risk vs. Original |
|---|---|---|---|
| Maintain original risk budget | $26.9M | $17.5M | 1.0x |
| Current position (no trade) | $50.0M | $32.5M | 1.86x |
| Modest conviction add (+$15M) | $65.0M | $42.3M | 2.4x |
| Analyst proposal | $100.0M | $65.0M | 3.7x |

### Step 3: Apply Constraints

- Tech sector headroom: ~$32M before breaching 30% limit (assuming no offsets)
- Single-name soft cap at 10% NAV: implies max ~$80M
- Binding constraint: **sector limit at ~$32M add**

### Step 4: Recommended Position

**Add $15M (to $65M total / 8.1% NAV)**, subject to:

| Condition | Requirement |
|---|---|
| Execution window | 5-7 trading days, TWAP |
| Vol trigger to halt | Realized vol > 75% → pause |
| Price ceiling | If stock +8% during execution → reassess remaining add |
| Tech sector post-trade | ~28% (within limit, with ~$16M buffer) |
| Risk contribution vs. original | ~2.4x (elevated but manageable) |
| Mandatory review | 30-day post-trade risk review; trim if vol doesn't mean-revert toward 45% |

This size reflects a genuine increase in conviction (+30% notional) while acknowledging that the vol expansion has already effectively doubled the position's risk footprint. The net result is ~2.4x the original risk contribution — a meaningful increase that rewards the analyst's correct call without creating a portfolio-dominating concentration.

### What Would Justify the Full Double?

The analyst could re-propose the full add if:
1. Realized vol mean-reverts below 45% (position self-sizes down in risk terms)
2. Correlation to AI basket drops below 0.55 (restoring idiosyncratic character)
3. Other tech positions are reduced by ≥$18M to create sector headroom
4. Risk committee grants explicit exception for >10% single-name and >30% sector

---

## Reconciling Conviction with Risk: Decision Framework

The analyst's error is **conflating thesis confirmation with sizing justification**. These are separate questions:

| Question | Answer |
|---|---|
| Is the fundamental thesis stronger post-earnings? | Likely yes — 18% revenue beat, raised guidance |
| Does stronger thesis automatically justify larger position? | No — size is a function of risk budget, not conviction |
| Has the risk profile improved? | No — it has materially deteriorated (vol, beta, correlation) |
| Is the expected return higher? | Unclear — the stock has likely re-rated post-earnings, compressing forward return |
| Is the risk-adjusted return higher? | Almost certainly not — even if expected return rose 20%, risk roughly doubled |

**The right mental model**: The vol expansion already "added" to the position. The fund is already more exposed to this name than it was pre-earnings. The question is not "should we add?" but "are we already overexposed, and if so, by how much?"

Strong conviction is necessary but not sufficient for large position sizes. The risk characteristics must also support concentration. Here, they do not — the position has become a high-beta, high-correlation, high-vol AI-factor bet that reduces portfolio diversification and threatens hard constraints.

---

## Sources & Data Quality

| Data Point | Source | Confidence |
|---|---|---|
| Vol expansion 35% → 65% | context.risk_profile_change | High — realized vol directly observable |
| Beta increase 1.3 → 1.8 | context.risk_profile_change | Moderate — short lookback post-earnings |
| Idiosyncratic share 65% → 40% | context.risk_profile_change | Moderate — factor decomposition model-dependent |
| Tech sector at 26% / 30% limit | context.portfolio | High — internal constraint |
| Volume normalization 5-7 days | context.market_impact_estimate | Moderate — empirical pattern, not guaranteed |
| AI-related semiconductor revenue growth expectations ~38-50% | GS AI Adoption Tracker, GS research | Moderate — sell-side consensus |

---

*This analysis reflects scenario data as provided; actual position sizing decisions require real-time risk system outputs, compliance pre-trade checks, and portfolio manager approval. Not investment advice.*