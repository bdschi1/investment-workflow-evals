

# Portfolio Construction Memo: Sizing Asymmetric Restructuring Candidates

## Executive Summary

**Security Type**: Restructuring equity candidate
**Recommendation**: EXPRESS VIA CALL SPREADS, NOT OUTRIGHT EQUITY
**Max Equity Position Size**: 2.3% of NAV ($12.7M) — hard ceiling, not target
**Recommended Position Size**: 0.9% of NAV via call spreads (~$5M premium at risk)
**Expected Value**: +14.3% (positive but misleading as a sizing input)

**One-sentence thesis**: Positive expected value does not justify aggressive sizing when the return distribution is bimodal with a 15% probability of an unstoppable -65% gap loss; the correct approach is to cap position size at the loss-tolerance-implied maximum and preferentially express the thesis via defined-risk options structures.

---

## Distribution Analysis: Why Positive EV ≠ Size Aggressively

### The Return Distribution Is Not Normal — It's Trimodal With a Fat Left Tail

| Scenario | Probability | Return | Contribution to EV |
|---|---|---|---|
| Restructuring succeeds | 50% | +55% | +27.5% |
| Partial execution | 35% | -10% | -3.5% |
| Covenant breach / recap | 15% | -65% | -9.75% |
| **Weighted EV** | | | **+14.25%** |

The +14.3% EV is real. But the distribution that generates it has three critical properties that standard sizing frameworks cannot accommodate:

1. **Bimodality**: Outcomes cluster around +55% and -10%/-65%, not around the mean of +14.3%. The mean is not a likely outcome — it sits in a probability desert between the modes.

2. **Negative skew with extreme kurtosis**: The left tail extends to -65% with 15% probability. This is not a 2-sigma event in a normal distribution — it's a discrete state of the world with known, material probability.

3. **Discontinuity**: The -65% loss is a gap event (covenant breach triggers overnight recapitalization). There is no ability to stop out at -20% or -30% on the way down. The loss function is binary: you either avoid it entirely or absorb the full -65%.

**Key insight**: Vol-targeting and Kelly-criterion approaches both assume you can trade continuously through the loss distribution. When the worst-case outcome is a discontinuous gap, these frameworks systematically understate required position-size reductions.

---

## Why Vol-Targeting Fails Here

### The Distributional Assumption Error

Vol-targeting this position suggests ~2.2% of NAV. This is wrong for three reasons:

| Assumption | Vol-Targeting Model | This Position's Reality |
|---|---|---|
| Return distribution | Normal / lognormal | Trimodal with discrete gap |
| Loss path | Continuous (stoppable) | Discontinuous (unstoppable) |
| Tail probability | ~2.3% for -2σ event | 15% for -65% event |
| Implied stop-loss | Can exit at any loss level | Cannot exit before gap |
| Volatility stationarity | Assumed | Regime-dependent (pre/post covenant breach) |

**The core problem**: Realized volatility of this position will look moderate in 85% of outcomes (returns cluster around +55% and -10%, both relatively low-vol paths). The vol estimate is dominated by the high-probability, low-magnitude scenarios. It structurally underweights the 15%-probability catastrophic outcome because that outcome hasn't happened yet and won't show up in trailing vol.

A vol-targeted 2.2% position would produce a worst-case loss of 2.2% × 65% = **1.43% of NAV** — which technically fits the 1.5% tolerance but only barely, and with a 15% probability of occurring. That is not conservative sizing; it is backing into the constraint by accident.

---

## Loss Budget Application: Hard-Ceiling Position Size

### Derivation

The portfolio's max single-name loss tolerance is **1.5% of NAV**.

Assuming NAV = $550M (implied by the $12.7M / 2.3% relationship):

$$\text{Max Position} = \frac{\text{Max Acceptable Loss}}{\text{Worst-Case Loss Rate}} = \frac{1.5\% \times \$550M}{65\%} = \frac{\$8.25M}{0.65} = \$12.7M$$

$$\$12.7M = 2.3\% \text{ of NAV}$$

| Parameter | Value |
|---|---|
| NAV (implied) | ~$550M |
| Max single-name loss tolerance | 1.5% of NAV = $8.25M |
| Worst-case return | -65% |
| **Max position size (equity)** | **$12.7M (2.3% of NAV)** |
| Probability of hitting max loss | 15% |
| Expected loss from tail event alone | 15% × $8.25M = **$1.24M** |

### 2.3% Is the Ceiling, Not the Target

Even at the maximum permissible size, the portfolio faces a **15% probability of losing the full 1.5% of NAV** on a single name. This deserves scrutiny:

- **Expected loss contribution from the tail alone**: 0.15 × 1.5% = 0.225% of NAV. In a portfolio context, this is a meaningful drag if the tail materializes.
- **Frequency framing**: A 15% probability is roughly 1-in-7. If you run seven similar positions at max size, you should expect one to gap against you. This is not a remote tail — it is a plausible near-term outcome.
- **Portfolio-level impact**: If the fund holds 30-50 positions and one loses 1.5% of NAV in a single overnight gap, that likely represents the worst single-name loss in the book for the quarter. The PM must be comfortable that this restructuring thesis warrants consuming that entire single-name risk budget.

**Recommendation**: Size the equity position at **1.5-1.8% of NAV** ($8.3M-$9.9M), not the full 2.3% ceiling. This keeps the worst-case loss at 1.0-1.2% of NAV, preserving buffer for model error on the -65% estimate (which could be worse — recapitalizations sometimes exceed initial loss estimates).

---

## Options as a Sizing Tool: Eliminating Gap Risk

### Why Call Spreads Are the Superior Expression

The fundamental problem with equity ownership here is that the thesis is bullish (+55% upside) but the risk is asymmetric and unstoppable (-65% gap). Call spreads solve this by **converting an unbounded-loss equity position into a defined-risk options position**.

### Proposed Structure: Bull Call Spread

| Component | Detail |
|---|---|
| **Underlying** | Restructuring candidate equity |
| **Buy** | ATM calls (strike = current price) |
| **Sell** | OTM calls (strike = current + 40-50%) |
| **Expiry** | 6-9 months (aligned with restructuring timeline) |
| **Net premium (max loss)** | ~$5M |
| **Max gain** | ~$12-15M (depending on spread width and pricing) |
| **Payoff ratio** | 2.4-3.0x on premium risked |

### Comparison: Equity vs. Call Spread Expression

| Metric | Equity ($12.7M) | Call Spread ($5M premium) |
|---|---|---|
| Max loss (covenant breach) | $8.25M (65% × $12.7M) | $5.0M (100% of premium) |
| Max loss as % of NAV | 1.5% | 0.9% |
| Upside if +55% | $6.99M | ~$12-15M |
| Return on capital at risk | 55% on $12.7M | 140-200% on $5M |
| Gap risk exposure | **Full** — cannot stop out | **Zero** — max loss = premium |
| Probability of total loss | 15% (covenant breach) | ~50% (partial execution + breach) |
| Breakeven | Current price | Current price + premium paid |

### Key Advantages of the Options Expression

1. **Gap risk eliminated entirely**: If covenant breach occurs overnight, the call spread expires worthless. Loss = $5M, not $8.25M. No gap, no margin call, no forced selling.

2. **Better risk-adjusted upside**: The call spread captures most of the +55% upside scenario while risking less capital. The payoff ratio (max gain / max loss) is materially superior.

3. **Frees risk budget**: At $5M max loss (0.9% of NAV), the position consumes only 60% of the single-name loss budget, leaving room for other restructuring ideas or for adding if conviction increases.

4. **Honest about the partial-execution scenario**: In the -10% equity outcome, the call spread also likely loses (premium decay). But the loss is $5M vs. $1.27M on equity — this is the tradeoff. The call spread is more expensive in the middle scenario but dramatically cheaper in the tail.

### Tradeoffs and Limitations

- **Premium cost**: The call spread has a higher breakeven than equity. If the stock rises only 5-10%, equity wins and the call spread loses.
- **Liquidity**: Restructuring candidates often have illiquid options markets. Bid-ask spreads on the options may be wide, increasing effective cost by 10-20%.
- **Timing risk**: Options have expiry dates. If the restructuring takes longer than expected, the position may need to be rolled at additional cost.
- **Implied vol premium**: The market likely prices elevated implied vol on a restructuring candidate, making options relatively expensive. The PM should compare implied vol to the scenario-implied realized vol to assess whether the options are fairly priced.

---

## Is 15% Probability of -65% Acceptable at Any Size?

### Yes — But Only With Defined Risk

The question is not whether 15% × -65% is "too risky" in the abstract. It's whether the **expected value of the full distribution justifies the capital at risk**, given the portfolio's loss constraints.

| Test | Equity Expression | Call Spread Expression |
|---|---|---|
| Positive EV? | Yes (+14.3%) | Yes (depends on premium, but likely +EV if premium < ~20% of notional) |
| Worst case within loss budget? | Yes at ≤2.3% of NAV | Yes at any reasonable premium size |
| Risk/reward acceptable? | Marginal (0.85x at max size) | Strong (2.4-3.0x on premium) |
| Gap risk manageable? | **No** — cannot stop out | **Yes** — loss = premium |

**Conclusion on acceptability**: The 15% probability of -65% is acceptable **only if**:

1. Position size is capped at the loss-budget-implied maximum (2.3% equity, or preferably smaller)
2. The PM explicitly accepts that ~1-in-7 times this trade will produce the maximum single-name loss
3. The position is not correlated with other restructuring bets in the book (otherwise, the 15% tail is not independent across positions)
4. Preferably, the thesis is expressed via call spreads to eliminate the gap risk entirely

It is **not acceptable** if the PM sizes based on the +14.3% EV, uses vol-targeting to justify a larger position, or treats the 15% tail as a "monitoring risk" that can be managed in real-time. The covenant breach is binary and overnight — there is nothing to monitor.

---

## Decision Framework Summary

```
Step 1: Is EV positive?                    → Yes (+14.3%). Proceed.
Step 2: Is the loss path continuous?        → No. Gap risk. Cannot vol-target.
Step 3: Max position = Loss budget / Worst case → $8.25M / 0.65 = $12.7M (2.3%)
Step 4: Is 15% × max loss acceptable?      → Marginal. Consider sizing below ceiling.
Step 5: Can options eliminate gap risk?     → Yes. Call spread caps loss at premium.
Step 6: Is options expression +EV?          → Likely yes. Compare premium to scenario payoffs.
Step 7: Final sizing decision               → Call spread at 0.9% NAV risk preferred.
                                               Equity at 1.5-1.8% NAV if options unavailable.
                                               Never exceed 2.3% NAV under any circumstance.
```

---

## Position Sizing Recommendation

| Expression | Size | Max Loss | Max Loss % NAV | Preferred? |
|---|---|---|---|---|
| **Call spread** | $5M premium | $5.0M | 0.9% | **Yes** |
| Equity (conservative) | $9.5M (1.7% NAV) | $6.2M | 1.1% | Acceptable |
| Equity (max permissible) | $12.7M (2.3% NAV) | $8.25M | 1.5% | Hard ceiling only |
| Equity (vol-targeted) | $12.1M (2.2% NAV) | $7.9M | 1.4% | **No — wrong framework** |

---

## Key Principles Codified

1. **Positive EV is necessary but not sufficient for sizing.** The shape of the distribution — not just its mean — determines appropriate position size.
2. **Discontinuous losses require worst-case sizing, not volatility-based sizing.** If you can't stop out, your position size must assume the full loss materializes.
3. **Loss budgets are hard constraints, not guidelines.** The 1.5% max loss tolerance divided by the worst-case loss rate gives the absolute ceiling.
4. **Options convert unbounded risk into defined risk.** When the thesis is directional but the risk is asymmetric, call spreads are a structurally superior expression.
5. **A 15% probability is not a tail — it's a scenario.** Size for it, don't monitor for it.

---

*This analysis assumes scenario probabilities and loss magnitudes as provided. Actual covenant breach losses could exceed -65% in severe recapitalization scenarios. Options pricing, liquidity, and availability are assumed but not verified. This framework is illustrative and should be adapted to specific portfolio constraints and risk tolerances.*