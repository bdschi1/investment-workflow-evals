

# Portfolio Construction Memo: Kelly Criterion Sizing for Healthcare Catalyst Strategy

## Executive Summary

**Strategy**: Healthcare FDA Catalyst (Event-Driven)
**Recommendation**: REJECT the proposed 23% (half-Kelly) allocation
**Proposed Alternative**: 5–8% of portfolio
**Core Issue**: The analyst's 23% sizing is half of a Kelly fraction built on statistically unreliable inputs. Properly accounting for parameter uncertainty, survivorship bias, and regime change risk reduces the defensible allocation by ~70–80%.

**One-sentence thesis**: "Half-Kelly" applied to a garbage-in point estimate is not conservative — it's precisely half as reckless as full Kelly.

---

## 1. Statistical Unreliability of the Inputs

### The Standard Error Problem

With n=18 binary observations and p̂=0.67, the standard error of the win rate is:

$$SE = \sqrt{\frac{p(1-p)}{n}} = \sqrt{\frac{0.67 \times 0.33}{18}} = 0.111 = 11.1\%$$

This is not a minor footnote — it means the 95% confidence interval on the win rate spans **44.8% to 89.2%**. The analyst's entire Kelly calculation rests on a parameter we cannot estimate with useful precision.

| Metric | Value |
|---|---|
| Point estimate win rate | 67% (12/18) |
| Standard error | 11.1% |
| 95% CI | 44.8% – 89.2% |
| 1-SE lower bound (p̂ – 1σ) | 55.9% |
| 2-SE lower bound (p̂ – 2σ) | 44.8% |
| Width of 95% CI | 44.4 percentage points |

For context, a coin-flip strategy (50% win rate) falls *within* this confidence interval. We cannot statistically distinguish this strategy from a coin flip at conventional significance levels when the payoff asymmetry is modest. The clinical trials literature (Source 1, Source 11) explicitly warns that normal approximation of binomial proportions works "fine when the number of observations is large, say 30 or more, but less so when n is small."

**18 observations is insufficient for confident parameter estimation of a proportion that drives a nonlinear sizing formula.**

---

## 2. Kelly Sensitivity Analysis: The Edge Estimate Is the Fragile Input

The Kelly fraction for this strategy is:

$$f^* = \frac{p \cdot b - (1-p)}{b} = \frac{p \cdot 2.48 - (1-p)}{2.48}$$

where p = win rate, b = payoff ratio (2.48:1).

Kelly is highly convex in the win rate. Small changes in p produce large changes in recommended allocation:

| Win Rate (p) | Kelly Fraction (f*) | Half-Kelly | Interpretation |
|---|---|---|---|
| 89% (upper 2σ) | 72.0% | 36.0% | Implausibly aggressive |
| 78% (upper 1σ) | 59.1% | 29.5% | Still unreliable |
| **67% (point est.)** | **46.2%** | **23.1%** | **Analyst's proposal** |
| 55.9% (lower 1σ) | 31.8% | 15.9% | More defensible base |
| 48% (survivorship-adj.) | 21.6% | 10.8% | Bias-corrected |
| 44.8% (lower 2σ) | 16.5% | 8.3% | Conservative bound |
| 40.3% (breakeven) | 0% | 0% | No edge |

**Key observation**: A 19-percentage-point swing in win rate (67% → 48%) cuts the Kelly fraction by more than half. The edge estimate — not the payoff ratio — is the fragile input, and it is precisely the input we measure with the least precision.

The Kelly formula assumes the edge is **known and stationary**. Neither condition holds here:
- **Not known**: SE of 11.1% on a 67% estimate means we're guessing.
- **Not stationary**: FDA committee composition has changed (see Section 5).

---

## 3. The Critical Distinction: Half of Point-Estimate Kelly vs. Half of Conservative Kelly

This is the central analytical error in the proposal. The analyst computed:

> Full Kelly(p̂ = 0.67) = 46.2% → Half-Kelly = 23.1%

The correct approach when inputs are uncertain:

> Step 1: Use a conservative estimate of p (lower bound of CI)
> Step 2: Compute Kelly on that conservative p
> Step 3: Then apply fractional Kelly to that result

| Approach | Calculation | Result |
|---|---|---|
| **Analyst's method** (wrong) | ½ × Kelly(0.67) | 23.1% |
| Half-Kelly on 1σ lower bound | ½ × Kelly(0.559) | 15.9% |
| Half-Kelly on survivorship-adjusted | ½ × Kelly(0.48) | 10.8% |
| Half-Kelly on 2σ lower bound | ½ × Kelly(0.448) | 8.3% |
| Quarter-Kelly on survivorship-adjusted | ¼ × Kelly(0.48) | 5.4% |

The analyst's 23.1% is **2.8× larger** than the half-Kelly fraction computed on the survivorship-adjusted win rate, and **4.3× larger** than a quarter-Kelly on the conservative bound.

**Fractional Kelly is a tool for managing uncertainty in known edges. It is not a substitute for correcting biased inputs.** Halving a bad estimate doesn't make it half-bad — it makes it wrong at half the size.

---

## 4. Survivorship Bias: The Backtest Is Overstated

The analyst excluded 7 signals from the 18-observation backtest. Including them:

| Dataset | Wins | Total | Win Rate | Kelly f* | Half-Kelly |
|---|---|---|---|---|---|
| Reported (cherry-picked) | 12 | 18 | 67% | 46.2% | 23.1% |
| Full sample (incl. excluded) | 12 | 25 | 48% | 21.6% | 10.8% |

The excluded signals were likely removed for plausible-sounding reasons (e.g., "unusual circumstances," "not representative"). But every backtest exclusion that removes a loser inflates the win rate. The 7 excluded observations were apparently all losses or non-events, dropping the win rate from 67% to 48%.

At a 48% win rate with a 2.48:1 payoff ratio, the strategy still has positive expected value — but the Kelly fraction drops to 21.6%, and the appropriate half-Kelly drops to ~11%. The analyst's proposed 23% exceeds even the *full* Kelly on the unbiased dataset.

**The proposed allocation is larger than full Kelly on the honest data.**

---

## 5. Regime Change: FDA Committee Composition

Three FDA advisory committee members have been replaced. This is not a minor procedural change — committee composition directly determines voting outcomes on the binary events this strategy trades.

Implications:
- The 18 historical observations were generated under a **different committee**. The model's predictive inputs (voting patterns, member biases, therapeutic area expertise) may no longer apply.
- With 3 of ~10–12 typical committee members replaced (~25–30% turnover), the effective sample size for the *current regime* is arguably **zero**.
- Healthcare catalyst strategies are inherently regime-dependent (Source 14 notes FDA regulatory approach as a key variable; Source 15 highlights healthcare sector sensitivity to regulatory outcomes).

This doesn't mean the strategy is worthless — it means the backtest is training data from a different distribution. The appropriate response is to treat the strategy as largely unproven until sufficient observations accumulate under the new committee.

---

## 6. Strategy Capacity Constraints

| Metric | Value |
|---|---|
| Proposed notional | $81M |
| Average daily volume (ADV) | ~$1.0B implied |
| Position as % of ADV | ~8% |

At 8% of ADV, the position:
- **Telegraphs the trade** to other event-driven participants who monitor order flow
- **Creates adverse selection**: market makers widen spreads, other catalyst funds front-run
- **Impairs exit**: if the binary event goes against us, unwinding 8% of ADV in a gap-down is catastrophic
- **Violates Kelly's assumption** of frictionless execution at known prices

A more realistic capacity constraint for event-driven healthcare trades is 1–2% of ADV, implying a maximum notional of $10–20M, or roughly 3–6% of a $350M portfolio.

---

## Recommended Position Sizing

### Sizing Waterfall

| Step | Adjustment | Kelly Fraction |
|---|---|---|
| Start: Point-estimate full Kelly | — | 46.2% |
| Correct for survivorship bias (p = 48%) | −24.6pp | 21.6% |
| Apply half-Kelly for parameter uncertainty | ×0.5 | 10.8% |
| Further discount for regime change (~50% haircut) | ×0.5 | 5.4% |
| Capacity constraint check | Cap at ~5% | **5%** |

### Final Recommendation

| Parameter | Value |
|---|---|
| **Recommended allocation** | **5–8% of portfolio** |
| Rationale | Quarter-Kelly on survivorship-adjusted win rate, with regime-change discount |
| Notional (assuming $350M portfolio) | $17.5–28M |
| % of ADV | 1.8–2.8% (manageable) |
| Review trigger | Accumulate 10+ observations under new committee before increasing |

### Scaling Plan

The allocation can increase *if and when*:
1. **10+ observations** under the new committee confirm a win rate ≥55% (SE drops to ~15% with n=10, still wide but directionally informative)
2. **Survivorship bias audit** is completed — all signals must be tracked, not just the ones that "count"
3. **Capacity** is validated through execution analysis showing <50bps of slippage

---

## Decision Framework Summary

| Dimension | Analyst's Proposal | Correct Approach |
|---|---|---|
| Win rate used | 67% (point estimate) | 48% (survivorship-adjusted) |
| Kelly basis | Full Kelly on point estimate | Kelly on conservative estimate |
| Fractional Kelly | ½ × Kelly(67%) = 23% | ¼ × Kelly(48%) ≈ 5% |
| Regime change | Not addressed | ~50% further discount |
| Capacity check | 8% of ADV (problematic) | Target 1–2% of ADV |
| **Final size** | **23%** | **5–8%** |

---

## Key Takeaways for the Desk

1. **Kelly requires known, stationary edges.** With n=18 and 11% SE, we don't know the edge. With committee turnover, it isn't stationary. Both Kelly preconditions fail.

2. **"Half-Kelly" is not a magic conservatism button.** It manages variance for a known edge. It does nothing to fix biased or imprecise inputs. Half of wrong is still wrong.

3. **Always ask what was excluded from the backtest.** Seven excluded signals turned a 67% win rate into 48%. The honest dataset suggests the analyst's "conservative" half-Kelly exceeds full Kelly.

4. **Regime changes reset the clock.** 25–30% committee turnover means the historical win rate is from a different game. Size for ignorance, not for the old regime's statistics.

5. **Capacity is a hard constraint, not a soft one.** 8% of ADV in a binary-outcome trade is a position that can't be exited gracefully when wrong.

---

*This memo reflects analysis of the proposed sizing methodology and does not constitute a recommendation on the underlying healthcare catalyst strategy itself. All probability estimates are subject to model uncertainty and should not be treated as precise forecasts.*