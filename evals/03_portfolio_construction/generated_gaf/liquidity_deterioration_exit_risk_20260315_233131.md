

# Portfolio Construction Memo: Liquidity-Driven Position Resize

## Executive Summary

**Position**: Mid-Cap Industrial Component Maker (unnamed)
**Current Size**: $40M / 8% of NAV
**Recommendation**: TRIM to 4-5% of NAV ($20-25M) over 5-7 trading days
**Conviction Level**: Reduced from 8/10 → 6/10
**Thesis Status**: Intact but degraded; management credibility impaired, information ecosystem hollowed out

**One-sentence thesis**: The analyst may be right that destocking is cyclical, but the position is now materially mis-sized for a name where exit risk has doubled, volatility has jumped 73%, and the information ecosystem has lost a third of its coverage — trim first, re-evaluate second.

---

## The Core Sizing Problem

Holding $40M because "the thesis is intact" conflates investment merit with position appropriateness. These are separate decisions:

| Dimension | Pre-Event | Post-Event | Change |
|---|---|---|---|
| ADV (shares) | 1.2M | 780K | -35% |
| Days-to-exit (10% participation) | ~3 days | 10+ days | ~3x |
| Position as % of ADV | ~3.3% | ~5.1% | +55% |
| Realized vol | 22% | 38% | +73% |
| Sell-side coverage | 12 analysts | 8 analysts | -33% |
| Bid-ask spread | Baseline | ~3x wider | +200% |
| Daily VaR (1σ, simplified) | ~$140K | ~$242K | +73% |

The position didn't just lose value — it became structurally harder to manage. A $40M position at 5.1% of ADV in a 38-vol name with thinning coverage is a fundamentally different risk than a $52M position at 3.3% of ADV in a 22-vol name with full coverage. The fact that the dollar value shrank doesn't mean the risk shrank. It grew.

---

## Why Liquidity Is a Sizing Input, Not a Monitoring Metric

Liquidity determines the **cost and speed of changing your mind**. When you "monitor" liquidity, you're implicitly assuming you can act on what you observe. But liquidity deterioration is reflexive — by the time you decide to act, the exit may be worse than when you measured it.

**The math is unforgiving:**
- At 10% participation rate on 780K ADV → 78K shares/day capacity
- $40M position at ~$31/share (post-22% drop from ~$40) ≈ 1.29M shares
- Days to exit: **16.5 trading days** — over three calendar weeks
- At 15% participation (aggressive, likely to move price): ~11 days
- At 5% participation (stealth): ~33 days

If a second negative catalyst hits during that exit window, you're selling into your own wake. The position has become a roach motel: easy to stay in, hard to leave.

**Sizing rule of thumb**: For a concentrated fund, no single position should require more than 5 days to exit at a reasonable participation rate (10-15%). At current ADV, that caps the position at ~$18-24M, or roughly 4-5% of NAV.

---

## Information Content of Coverage Drops and Institutional Exits

### Sell-Side Departures Are Not Noise

When 4 of 12 analysts drop coverage after a guidance cut, the signal is threefold:

1. **Economics signal**: Their sales desks see insufficient institutional interest to justify the coverage cost. This is a revealed-preference indicator of buy-side abandonment.
2. **Information ecosystem degradation**: Fewer analysts = fewer earnings models, fewer channel checks, fewer management access points. Your own information advantage narrows because the baseline of public information production has shrunk by a third.
3. **Re-rating risk**: Stocks with declining coverage tend to trade at wider discounts to peers. The coverage loss itself becomes a valuation headwind independent of fundamentals.

### Block Trade Exits at 4-6% Discounts

Two institutional holders selling in block trades at 4-6% discounts to market is **urgent selling**. Nobody takes a 4-6% haircut on a $4B market cap name unless:
- They have a hard risk limit that was breached
- Their own LPs are redeeming and they need liquidity
- They've lost conviction and want certainty of exit over price optimization

Regardless of their reason, the market now has evidence that informed holders are willing to accept significant discounts to exit. This reprices the liquidity premium for everyone remaining.

---

## Management Credibility: The 180-Degree Problem

Ninety days ago, management guided for **acceleration**. They then cut guidance by **15%**. This is not a minor miss — it's a directional reversal in under one quarter.

| Credibility Factor | Assessment |
|---|---|
| Guidance accuracy | Failed — 180° reversal in 90 days |
| Visibility into own business | Questionable — couldn't see destocking 90 days out |
| Future guidance reliability | Degraded — market will apply a discount to next guide |
| Probability of further cuts | Elevated — first cut is rarely the last in industrial destocking |

The analyst's "cyclical destocking" thesis may be correct, but management's inability to forecast their own near-term trajectory means **we don't know when the cycle turns, and neither do they**. The base case should now include a wider range of outcomes and a longer timeline to recovery.

---

## The Asymmetry Argument for Trimming

This is the crux of the decision. The analyst frames it as binary: hold (thesis intact) or sell (thesis broken). But sizing is continuous, not binary.

| Scenario | Full Position (8% NAV) | Trimmed Position (4.5% NAV) |
|---|---|---|
| **Thesis right, stock +40%** | +$16M (+3.2% NAV) | +$9M (+1.8% NAV) |
| **Thesis right, stock +25%** | +$10M (+2.0% NAV) | +$5.6M (+1.1% NAV) |
| **Thesis wrong, stock -30%** | -$12M (-2.4% NAV) | -$6.8M (-1.4% NAV) |
| **Thesis wrong, forced exit at -40% (illiquidity penalty)** | -$16M (-3.2% NAV) | -$9M (-1.8% NAV) |

**Key insight**: If the thesis is right, you still make meaningful money on a smaller position. If it's wrong, the illiquidity penalty on a full-sized position creates asymmetric downside. The expected value of trimming is positive because it reduces the tail risk of the worst outcomes disproportionately.

The forgone upside from trimming (~1-1.4% of NAV in the bull case) is the **insurance premium** you pay against the illiquidity-amplified downside.

---

## Combined Risk: Vol × Illiquidity

These two factors are multiplicative, not additive:

- **Vol up 73%** means daily P&L swings are ~73% larger
- **Liquidity down 35%** means your ability to respond to those swings is ~35% slower
- **Combined effect**: The position's "risk per dollar of exit capacity" has roughly **tripled**

A simple risk-adjusted sizing framework:

```
Adjusted Position Size = Current Size × (Old Vol / New Vol) × (New ADV / Old ADV)
                       = $40M × (22/38) × (780K/1.2M)
                       = $40M × 0.579 × 0.65
                       = $40M × 0.376
                       = ~$15M (floor — may be too aggressive a cut)
```

Blending this mechanical output with conviction and practical execution, a target of **$20-25M (4-5% of NAV)** is the right zone.

---

## Execution Plan for the Trim

| Parameter | Specification |
|---|---|
| Target position | $22M (4.4% of NAV), reducing by ~$18M |
| Shares to sell | ~580K shares |
| Participation rate | 8-10% of ADV (62-78K shares/day) |
| Estimated execution time | 7-9 trading days |
| VWAP vs. arrival benchmark | Target VWAP; accept modest slippage |
| Urgency | Moderate — begin within 1 trading day |
| Block trade option | Explore with 1-2 brokers for $8-10M chunk at 2-3% discount; execute remainder algorithmically |

**Do not** wait for a bounce to trim. The bounce may not come, and if it does, liquidity may not improve with it. Trim into whatever liquidity exists now.

---

## Behavioral Framing: Trimming ≠ Locking In a Loss

The analyst's instinct to hold (and add) likely reflects two biases:

1. **Disposition effect**: Reluctance to realize a loss, framing the trim as "making the loss permanent." But the loss is already real — it's in your NAV today. Selling doesn't create the loss; it already happened.

2. **Commitment escalation**: Having advocated for the position, the analyst's identity is tied to the thesis. Adding to a deteriorating-liquidity name feels like conviction; it's actually doubling down on a position where the risk/reward of the *sizing* has changed even if the thesis hasn't.

**The correct frame**: "We are right-sizing for a name where the liquidity profile, information ecosystem, and management credibility have all deteriorated. If the thesis plays out, we will still benefit meaningfully at 4.5% of NAV. We can re-add if ADV recovers, coverage stabilizes, and management rebuilds credibility."

---

## Re-Entry Criteria

The trim is not permanent abandonment. Conditions for rebuilding toward 6-8% of NAV:

| Trigger | Threshold |
|---|---|
| ADV recovery | Sustained >1.0M shares/day for 20+ trading days |
| Coverage stabilization | No further drops; ideally 1+ new initiations |
| Management credibility | Next earnings guide met or beaten; no further cuts |
| Vol normalization | Trailing 30-day vol below 28% |
| Fundamental confirmation | Channel checks confirm destocking trough; orders inflecting |

Until at least 3 of 5 triggers are met, the position stays at 4-5% of NAV.

---

## Summary Decision Framework

```
Thesis intact?          → Probably (6/10 conviction, down from 8/10)
Position appropriately sized? → No. Liquidity, vol, and info ecosystem all degraded.
Action:                 → Trim to 4-5% of NAV over 7-9 days
Thesis abandoned?       → No. Smaller position, same thesis, better risk management.
Adding?                 → Not until re-entry criteria met.
```

The door got smaller. Size the position for the door that exists, not the one that existed three weeks ago.

---

*This memo reflects a point-in-time assessment based on the scenario as described. Actual execution and sizing should incorporate real-time market conditions, portfolio-level risk constraints, and updated fundamental analysis.*