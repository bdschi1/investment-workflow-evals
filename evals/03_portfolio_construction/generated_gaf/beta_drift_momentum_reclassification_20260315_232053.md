

# Portfolio Construction Memo: Beta Drift & Position Re-Sizing

## Executive Summary

**Position**: Software stock (momentum darling)
**Action**: TRIM from 4.0% to ~2.7% of portfolio (~33% reduction)
**Rationale**: Risk character has fundamentally changed even though the thesis has not. The position is now a systematic risk vehicle masquerading as an alpha bet.

**One-sentence thesis**: Unchanged fundamental conviction (8/10) does not justify unchanged sizing when the position's risk contribution has increased ~50% via beta drift, 73% of returns are replicable factor exposure, and momentum loading creates acute reversal risk.

---

## 1. Risk Character Shift: Same Thesis, Different Animal

The position's risk profile has undergone a regime change:

| Metric | 8 Months Ago | Current | Change |
|---|---|---|---|
| Rolling Beta | 1.0 | 1.5 | +50% |
| Idiosyncratic Variance | 65% | 40% | -25pp |
| Systematic Variance | 35% | 60% | +25pp |
| Momentum Factor Loading | ~0 | 0.68 | Significant |
| Alpha Share of Returns | ~majority | 27% | Collapsed |
| Factor Share of Returns | ~minority | 73% | Dominant |

**What this means**: Eight months ago, owning this stock was primarily a bet on company-specific outcomes — management execution, product cycle, competitive positioning. Today, owning this stock is primarily a bet on the momentum factor, the growth factor, and broad market beta. The fundamental thesis is unchanged, but the *risk you are taking* has changed completely.

A position with 60% systematic variance is not an alpha source. It is a leveraged market/factor exposure with a thin alpha wrapper. The stock has been absorbed into the momentum trade — its price movements are now driven more by factor flows than by anything the company does.

**Critical distinction**: Conviction measures your belief in the thesis. Risk contribution measures what the position actually does to your portfolio. These are independent variables. An 8/10 conviction stock at beta 1.5 is a categorically different position than an 8/10 conviction stock at beta 1.0 — it is 50% "larger" in systematic risk terms.

---

## 2. Why Beta Drift Requires Re-Sizing Without a Conviction Change

The sizing anchor must be **risk contribution**, not conviction. Here's why:

When this position was initiated at 4.0% with beta 1.0, the implied systematic risk contribution was:

$$\text{Systematic risk contribution} \propto w \times \beta = 4.0\% \times 1.0 = 4.0\% \text{ beta-weighted}$$

Today at beta 1.5:

$$\text{Systematic risk contribution} \propto 4.0\% \times 1.5 = 6.0\% \text{ beta-weighted}$$

The position has effectively self-sized upward by 50% in risk terms without any deliberate decision. This is passive risk drift — the most dangerous kind because it feels like "doing nothing" while the portfolio's risk profile quietly transforms.

**The correct framework**: You sized this position for a specific risk budget. Beta drift has blown through that budget. The right response is mechanical: restore the original risk contribution.

| Sizing Approach | Weight | Beta-Weighted Exposure | Risk Contribution |
|---|---|---|---|
| Original position | 4.0% | 4.0% (β=1.0) | Baseline |
| Current (no action) | 4.0% | 6.0% (β=1.5) | ~50% above budget |
| Risk-contribution-matched | **~2.7%** | **4.0%** (β=1.5) | **Restored to baseline** |

Trimming to ~2.7% maintains the original risk contribution. This is not a conviction call — it is risk hygiene.

---

## 3. The Factor Attribution Problem: You're Paying Alpha Fees for Beta Returns

The factor attribution data is damning:

| Return Source | Share | Implication |
|---|---|---|
| Factor exposure (momentum, growth, beta) | 73% | Replicable via cheap ETFs at 3-10bps |
| Alpha (idiosyncratic) | 27% | The only return that justifies single-stock risk |

**The economic problem**: You are bearing single-stock concentration risk (earnings misses, management turnover, competitive disruption) to earn returns that are 73% obtainable through a momentum ETF or levered index position at a fraction of the idiosyncratic risk. This is a terrible trade on a risk-adjusted basis.

**Decomposing the value of the position**:
- If the position returns 20% over 6 months, ~14.6pp came from factor exposure and ~5.4pp came from alpha.
- You could have captured most of the 14.6pp through MTUM, a growth ETF, or simply higher net exposure — without the single-stock tail risk.
- The 5.4pp of alpha is real, but it only justifies a position sized to that alpha contribution, not to the total return.

This doesn't mean sell entirely. The 27% alpha component is still valuable and reflects your intact thesis. But the position should be sized to the alpha it generates, not the factor-inflated total return.

---

## 4. Portfolio-Level Impact: Net Beta Drift

| Portfolio Metric | Target/Prior | Current | Status |
|---|---|---|---|
| Net Beta | 0.30 | 0.38 | **27% above target** |
| Contribution from this position | Proportional | Outsized | Unintended drift |

A net beta move from 0.30 to 0.38 is not trivial — it represents a 27% increase in market directionality. For a portfolio targeting 0.30 beta, this means:
- In a -10% market drawdown, expected loss goes from -3.0% to -3.8% (80bps of additional downside)
- The portfolio is taking uncompensated directional risk it didn't sign up for

**Attribution**: While this single position isn't solely responsible for the 8bp drift, its beta expansion from 1.0 to 1.5 at a 4.0% weight contributed meaningfully. The position's beta contribution went from 4bp (4.0% × 1.0) to 6bp (4.0% × 1.5) — a 2bp increase that likely accounts for roughly 25% of the total drift.

**Restoration plan**:

| Action | Beta Impact | Sufficient Alone? |
|---|---|---|
| Trim position to 2.7% | Reduces contribution from 6.0bp to 4.0bp (-2.0bp) | Partially |
| Add index hedge (e.g., short SPX futures) | Adjustable to close remaining gap | Yes, as complement |
| Combination approach | Trim + small hedge | **Recommended** |

Trimming alone recovers ~2bp of the 8bp drift. The remaining ~6bp likely comes from beta drift in other positions or net exposure creep, requiring a portfolio-wide beta audit.

---

## 5. Recommended Position Size: 2.7%

**The anchor is risk contribution, not conviction.**

| Parameter | Value | Rationale |
|---|---|---|
| Target weight | **2.7%** | Restores original beta-weighted contribution (2.7% × 1.5 ≈ 4.0%) |
| Trim size | ~1.3% (33% of position) | Mechanical, not discretionary |
| Conviction adjustment | None | Thesis unchanged at 8/10 |
| Residual alpha exposure | Maintained | 27% alpha component still captured |

**Why risk contribution is the right anchor**:
1. It is what you originally underwrote when you sized at 4.0%/β=1.0
2. It is objective and observable, unlike conviction which is subjective
3. It maintains portfolio-level risk budget discipline
4. It correctly distinguishes between "I like this stock" and "how much portfolio risk should this stock represent"

**What you preserve**: Full expression of the alpha thesis at the appropriate risk level. You are not reducing conviction — you are right-sizing the vehicle to its changed risk characteristics.

---

## 6. Momentum Reversal Risk

A momentum factor loading of 0.68 is a distinct, material risk that compounds the beta drift problem.

**Historical context for momentum reversals**:
- Momentum crashes are fat-tailed events — they are rare but severe
- The March 2009 momentum reversal saw the long-short momentum factor lose ~40% in two months
- Momentum reversals typically coincide with market regime changes (rate pivots, sector rotations, risk-off events)
- Positions with high momentum loading experience drawdowns that are *correlated with each other*, amplifying portfolio impact

**Current environment**: The retrieved research (Jefferies, Goldman) highlights ongoing rotation dynamics, narrowing breadth, and sector leadership shifts — exactly the conditions that precede momentum factor stress. Tech/growth concentration at elevated levels increases the probability of a crowding-driven unwind.

**Quantifying the risk**: With 60% systematic variance and a 0.68 momentum loading, a momentum factor reversal of 2 standard deviations could contribute a position-level drawdown of 15-25% beyond what the fundamental thesis would imply. At 4.0% weight, that's 60-100bps of portfolio drag from a single factor bet you didn't intentionally take.

**At 2.7% weight**: The same reversal contributes 40-68bps — still painful but within acceptable bounds for a high-conviction name.

---

## Implementation

| Step | Action | Timing |
|---|---|---|
| 1 | Trim 33% of position (4.0% → 2.7%) | Immediately, over 2-3 days to minimize impact |
| 2 | Conduct portfolio-wide beta audit | Same week |
| 3 | Evaluate incremental index hedge if net beta still >0.32 post-trim | Within 1 week |
| 4 | Set beta monitoring alert at 1.6 for further trim trigger | Ongoing |
| 5 | Re-run factor attribution monthly | Ongoing |
| 6 | Reassess if alpha share recovers above 50% (potential re-size up) | Quarterly |

**Re-entry criteria for full size**: Beta reverts below 1.15 AND idiosyncratic variance share recovers above 55% AND momentum loading falls below 0.35. All three conditions required — any one alone is insufficient.

---

## Decision Framework Summary

```
Conviction unchanged (8/10)     →  Does NOT justify maintaining size
Beta +50% (1.0 → 1.5)          →  Position is 50% "larger" in risk terms
Variance: 65% idio → 40% idio  →  Majority of risk is now systematic
Alpha share: 27%                →  73% of returns are cheap factor exposure
Momentum loading: 0.68         →  Acute reversal tail risk
Net beta: 0.30 → 0.38          →  Portfolio drift requires correction

ACTION: Trim to 2.7% to restore original risk contribution
```

The core error to avoid: treating "conviction hasn't changed" as equivalent to "position size shouldn't change." These are independent decisions governed by different inputs. Conviction governs whether you own the stock. Risk contribution governs how much.

---

*This analysis reflects position-level and portfolio-level risk assessment based on the data provided. Factor exposures and beta are backward-looking and may not predict future risk characteristics. All sizing recommendations are probabilistic and subject to revision as risk metrics evolve.*