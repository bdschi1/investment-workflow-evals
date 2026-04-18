

# Short Position Restructuring Memo: Consumer Discretionary Name

## Executive Summary

**Position**: Short, consumer discretionary equity
**Current Size**: -2% of portfolio (~$9M notional at entry; ~$7.4M current market value)
**Unrealized P&L**: +$1.59M (+17.7%)
**Recommendation**: **Close 75% of equity short, roll remaining downside thesis into put spreads**
**Rationale**: At 22% annualized borrow, the carry consumes 37% of remaining expected profit over 6 months. Squeeze risk at 30% SI / 8 DTC is asymmetric and uncompensable. Put spreads deliver 80% of the thesis payoff with zero borrow, zero squeeze risk, and defined loss.

**One-sentence thesis**: The fundamental short thesis remains intact, but the cost structure and squeeze dynamics of the equity expression no longer offer attractive risk-adjusted returns — restructure into options.

---

## Carry Cost Analysis: The Hurdle Rate Has Tripled

### Before vs. After Borrow Spike

| Metric | At 2% Borrow | At 22% Borrow | Delta |
|---|---|---|---|
| Monthly carry cost | $15K | $165K | +11x |
| Annualized carry | $180K | $1.98M | +11x |
| 6-month carry | $90K | $990K | +11x |
| Carry as % of remaining expected profit ($2.7M) | 3.3% | 36.7% | +33 pp |
| Carry as % of unrealized gain ($1.59M) | 5.7% | 62.3% | +57 pp |
| Monthly portfolio drag | ~0.3 bps | ~3.7 bps | +3.4 bps |

*Source: context.borrow_cost_change, context.hurdle_rate_analysis*

### Hurdle Rate Recalculation

At 2% borrow, the short needed to decline ~2% annualized just to break even on carry — trivial against a 30% downside thesis. At 22% borrow, the stock must decline **22% annualized** (roughly 11% over 6 months) before the position generates any net profit beyond carry costs.

**Effective hurdle rate math (6-month horizon):**
- Remaining expected move: -30% (from $59.90 to ~$41.93)
- Expected gross profit on remaining move: ~$2.7M
- 6-month carry at 22%: $990K
- **Net expected profit: $1.71M** (vs. $2.61M at old borrow)
- **Carry tax on thesis: 37%**

The carry doesn't kill the thesis — a 30% move still dominates a 11% carry drag over 6 months. But the margin of safety has collapsed. If the thesis takes 9-12 months instead of 6, carry consumes 55-73% of expected profit. The position is now a race against time, which is exactly the wrong posture for a fundamental short.

### Carry Relative to Unrealized Gain

The $165K/month carry will erode the existing $1.59M unrealized gain at a rate of ~10.4% per month. In 9.6 months of flat stock price, the entire unrealized gain is consumed by borrow. This is the critical framing: **you are now paying $165K/month for the privilege of staying in a winning trade.**

---

## Squeeze Risk Assessment

### Quantitative Framework

| Squeeze Indicator | Current Level | Threshold for Elevated Risk | Assessment |
|---|---|---|---|
| Short interest / float | 30% | >20% | **Critical** |
| Days to cover | 8 days | >5 days | **Critical** |
| Borrow cost | 22% annualized | >10% | **Critical** |
| Recent catalyst | Failed secondary | — | Supply constrained |
| Free float availability | Declining (implied by borrow spike) | — | Deteriorating |

*Source: context.borrow_cost_change.post_event*

All three primary squeeze indicators are simultaneously in the danger zone. This is not a theoretical risk — it is a loaded spring.

### Squeeze Magnitude Estimation

Historical squeeze analogs at 25-35% SI with >5 DTC suggest:
- **Base case squeeze**: +15-25% in 2-5 trading days (probability: ~25-35% over next 3 months)
- **Severe squeeze**: +30-50% in 1-2 weeks (probability: ~10-15%)
- **Tail scenario**: +50%+ if forced covering cascades (probability: ~5%)

A 20% squeeze on a $7.4M short position = **$1.48M loss**, nearly wiping out the entire $1.59M unrealized gain. A 30% squeeze puts the position underwater.

### Squeeze Catalysts to Monitor

1. **Short-covering cascade**: At 8 DTC, even modest buying pressure forces multi-day covering
2. **Positive earnings surprise**: Consumer discretionary names can gap 10-15% on beats
3. **Takeover/activist rumor**: Failed secondary may attract opportunistic buyers at depressed levels
4. **Broker recall**: At 22% borrow, lenders may recall shares to re-lend at higher rates, forcing involuntary covering
5. **Index rebalance flows**: Mechanical buying in a low-float name amplifies moves

### Expected Loss from Squeeze Risk (Probability-Weighted)

| Scenario | Probability | Stock Move | P&L Impact | Weighted Impact |
|---|---|---|---|---|
| No squeeze | 55% | 0% | $0 | $0 |
| Moderate squeeze (+20%) | 25% | +20% | -$1.48M | -$370K |
| Severe squeeze (+35%) | 13% | +35% | -$2.59M | -$337K |
| Extreme squeeze (+50%) | 7% | +50% | -$3.70M | -$259K |
| **Probability-weighted squeeze cost** | | | | **-$966K** |

Adding the probability-weighted squeeze cost ($966K) to the 6-month carry ($990K), the **all-in expected friction of maintaining the equity short is ~$1.96M** — consuming 73% of the $2.7M remaining expected profit.

---

## Information Content of the Borrow Spike

The spike from 2% to 22% is itself a signal worth decomposing:

**Bearish signal (thesis-confirming):** Heavy short demand indicates other informed investors share the bearish view. Academic evidence shows elevated short interest predicts negative future returns (Paleologo, *Advanced Portfolio Management*; Source 7). The crowding validates the fundamental thesis.

**Dangerous signal (execution-threatening):** The same crowding that validates the thesis creates the squeeze risk that can destroy the trade. When 30% of float is short, the trade is no longer contrarian — it is consensus among the short-selling community. Consensus shorts with high DTC are precisely the positions that generate the most violent squeezes.

**Failed secondary signal:** The failed offering means the company could not dilute — which is bearish for fundamentals (they need capital and can't get it) but bullish for squeeze mechanics (no new share supply to ease the borrow). This is the core tension: the worse the fundamental outlook, the more crowded the short, the higher the squeeze risk.

**Net interpretation:** The borrow spike confirms the thesis but degrades the expression. The right response is to maintain the view while changing the vehicle.

---

## Alternative Expression Evaluation

### Put Spread vs. Equity Short Comparison

| Dimension | Equity Short (current) | Put Spread (proposed) |
|---|---|---|
| Maximum gain on 30% decline | ~$2.7M | $2.25M (max payoff) |
| Cost to hold 6 months | $990K (borrow) | $1.2M (premium, one-time) |
| Squeeze risk | Unlimited upside exposure | Zero — max loss = premium |
| Borrow cost | 22% annualized, variable | Zero |
| Margin requirement | ~$7.4M+ | $1.2M premium |
| Forced covering risk | Yes (broker recall) | No |
| Probability-weighted all-in cost | ~$1.96M (carry + squeeze) | $1.2M (premium only) |
| Capital efficiency | Poor (high margin, high carry) | Superior (defined risk) |
| Gamma exposure | None | Positive (accelerating gains on decline) |

*Source: context.alternative_expressions*

### Key Insight

The put spread costs $1.2M upfront vs. $990K in borrow over 6 months — only $210K more in direct cost. But the put spread eliminates ~$966K in probability-weighted squeeze cost and removes the risk of involuntary covering. **The put spread is cheaper on a risk-adjusted basis by ~$756K.**

The put spread captures $2.25M / $2.7M = **83% of the thesis payoff** with zero tail risk. The equity short captures 100% of the payoff but at 73% expected friction.

### Why Not Just Buy Puts Outright?

At 22% borrow, implied volatility is likely elevated (borrow cost feeds into put-call parity). Buying outright puts means paying inflated vol premium. The put *spread* mitigates this by selling a lower-strike put, partially offsetting the elevated IV. The spread structure is the correct instrument in a high-borrow regime.

---

## Recommended Action Plan

### Step 1: Harvest 75% of Equity Short (Immediate)

- Cover 75% of the position, realizing ~$1.19M in gains
- Reduces borrow cost from $165K/month to ~$41K/month
- Reduces squeeze exposure by 75%
- Retains 25% equity short as a "stub" for unlimited downside participation

### Step 2: Establish Put Spread (Same Day)

- Buy 6-month ATM/OTM put spread struck near $60/$40
- Premium: ~$1.2M (funded from realized gains)
- Max payoff: $2.25M if stock reaches $40 or below
- Net cost after using realized gains: effectively self-funding

### Step 3: Manage the Stub (Ongoing)

- Remaining 25% equity short: ~$1.85M notional
- Reduced borrow: ~$41K/month (~$34K annualized drag on reduced notional)
- Set hard stop-loss at $70.50 (original entry) on the stub — if the squeeze erases the gain, exit
- The stub provides unlimited downside beyond the put spread's lower strike

### Resulting Position Profile

| Metric | Current Structure | Proposed Structure |
|---|---|---|
| Notional short exposure | $7.4M (equity) | $1.85M equity + $1.2M put spread |
| Monthly carry | $165K | ~$41K |
| Max loss (squeeze to +50%) | $3.7M | ~$925K (stub) + $1.2M (premium) = $2.1M |
| Max gain (stock to $42) | $2.7M | ~$675K (stub) + $2.25M (spread) = $2.93M |
| Squeeze risk | Severe | Moderate (stub only) |
| Capital at risk | $7.4M+ margin | ~$3.05M |

The restructured position has a **better max gain ($2.93M vs $2.7M)**, **lower max loss ($2.1M vs $3.7M+)**, and **90% lower carry cost**. The risk/reward improves from roughly 0.7:1 to 1.4:1.

---

## Decision Framework: When to Keep vs. Restructure Equity Shorts

| Condition | Keep Equity Short | Restructure to Options |
|---|---|---|
| Borrow cost | <5% annualized | >10% annualized |
| Short interest / float | <15% | >25% |
| Days to cover | <3 | >5 |
| Thesis timeline | <3 months to catalyst | >6 months |
| Unrealized gain | Small / none | Large (>15%) |
| IV level | Elevated (options expensive) | Moderate (spreads viable) |

This position fails every "keep" criterion and meets every "restructure" criterion.

---

## Risk to the Recommendation

1. **IV is too high to make put spreads attractive**: If implied vol has spiked alongside borrow, the put spread may cost more than $1.2M. Mitigation: use wider spreads or longer-dated options to reduce vol sensitivity.
2. **Stock gaps down before restructuring**: Covering 75% locks in gains but sacrifices participation. Mitigation: execute simultaneously — cover equity and buy puts in the same session.
3. **Thesis accelerates and stock drops 30% in weeks**: The equity short would have captured more. Mitigation: the 25% stub + put spread still captures ~$2.93M — only marginally less than the full equity short's $2.7M, and with far less risk carried to get there.

---

## Summary Verdict

| Dimension | Assessment |
|---|---|
| Thesis quality | Intact — 30% further downside well-supported |
| Expression quality | Severely degraded — 22% borrow, 30% SI, 8 DTC |
| Carry cost | Unacceptable at full size — 37% of expected profit over 6 months |
| Squeeze risk | Elevated — probability-weighted cost ~$966K |
| Alternative available | Yes — put spread captures 83% of payoff at lower all-in cost |
| **Action** | **Cover 75%, roll to put spreads, keep 25% stub with hard stop** |

The thesis is right. The trade structure is wrong. Fix the structure, keep the thesis.

---

*This analysis reflects a point-in-time assessment. Borrow costs, short interest, and option pricing are dynamic; all figures should be verified at execution. Probability estimates are subjective and based on historical analogs, not predictive models.*