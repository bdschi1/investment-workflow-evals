

# Portfolio Construction Memo: Options vs. Equity Expression for Precision Oncology Thesis

## Executive Summary

**Position**: Bullish thesis on precision oncology company ahead of data readout
**Expression A**: $40M equity (5.3% of NAV) — linear risk, no expiry
**Expression B**: $6M in 4-month ATM calls (~$36M delta exposure) — non-linear risk, time-bounded
**Recommendation**: **Hybrid — 3.5% NAV in equity ($26M) + $3M in 6-month calls (~$18M delta)**
**Rationale**: The 4-month options as structured are fatally flawed — they expire one month before the 5-month catalyst. Neither pure expression is optimal.

**One-sentence thesis**: Same directional view, but the instrument choice fundamentally alters the portfolio's risk topology, capital at risk, and probability of capturing the catalyst.

---

## Instrument Comparison

### Head-to-Head Tradeoff Matrix

| Dimension | Expression A: Equity ($40M) | Expression B: 4-Mo ATM Calls ($6M) |
|---|---|---|
| **Capital deployed** | $40M (5.3% NAV) | $6M (0.8% NAV) |
| **Initial delta exposure** | $40M | ~$36M (0.90 × $40M notional) |
| **Max loss** | $40M (theoretical; ~$20M realistic) | $6M (defined, total premium) |
| **Time decay** | Zero | $18K/day → $2.16M over 4 months (36% of premium) |
| **Delta stability** | Constant 1.0 per share | Starts 0.90, decays daily as theta erodes and gamma shifts |
| **Survives catalyst delay** | Yes — indefinitely | **No — expires 1 month before 5-month readout** |
| **Stock-flat P&L** | $0 | **-$2.16M** (36% of premium destroyed) |
| **Gamma exposure** | None | Significant — creates path-dependent, non-linear P&L |
| **Vega exposure** | None | Long vega — benefits from IV expansion pre-catalyst |
| **Capital efficiency** | Low (5.3% NAV consumed) | High (0.8% NAV) — but misleading without theta context |

### The Timeline Mismatch Is Disqualifying for 4-Month Options

This is the single most important fact in the analysis: **the 4-month options expire before the 5-month data readout**. This means:

1. The options must generate returns from pre-catalyst price appreciation or IV expansion alone — they will never capture the binary event itself.
2. If the stock is flat or modestly higher at expiry, the position loses $2.16M (36% of premium) to theta alone.
3. Biotech data readouts frequently delay by weeks to months. A 5-month expected readout could easily become 6–8 months. Equity survives this; 4-month options do not.
4. Even if the readout occurs on schedule at month 5, the options are already expired and settled at month 4.

**Buying 4-month options for a 5-month catalyst is not a risk management choice — it is a timing error.**

### Theta Drag Quantified

| Period | Cumulative Theta Cost | % of Premium Consumed |
|---|---|---|
| Month 1 | ~$540K | 9% |
| Month 2 | ~$1.08M | 18% |
| Month 3 | ~$1.62M | 27% |
| Month 4 (expiry) | ~$2.16M | 36% |

Theta accelerates as expiry approaches. By month 3, the position has lost over a quarter of its value to time decay alone, and delta has likely deteriorated well below 0.90 — meaning the position no longer provides the intended exposure.

---

## Portfolio-Level Risk Analysis

### How Each Expression Changes the Portfolio

| Risk Metric | Equity Impact | Options Impact |
|---|---|---|
| **Portfolio delta** | +$40M linear, stable | +$36M initially, declining daily as delta erodes |
| **Portfolio beta** | Adds ~5.3% NAV of biotech beta (likely β > 1.5) | Adds leveraged, decaying beta exposure; effective beta contribution shrinks over time |
| **Gamma** | Zero | Positive gamma — small moves generate accelerating P&L; portfolio becomes path-dependent |
| **Vega** | Zero | Long vega — portfolio becomes sensitive to implied volatility changes across the vol surface |
| **Theta** | Zero | -$18K/day drag on portfolio returns; ~$540K/month of negative carry |
| **Tail risk profile** | Symmetric downside to zero | Asymmetric — max loss capped at $6M, but probability of total loss is material |

### Non-Linear Delta: Why Options ≠ Stock Over Time

At entry, 0.90 delta creates the illusion of equivalence. This is a **static delta error**. In reality:

- **Delta decays with time**: As expiry approaches with no stock movement, delta on ATM options drifts toward 0.50, halving effective exposure.
- **Delta shifts with price**: A 15% stock decline could push delta to 0.50–0.60, meaning the options provide only 55–67% of the intended downside hedge/exposure.
- **Gamma creates daily rebalancing needs**: The portfolio's effective biotech exposure changes every day, requiring active monitoring. Equity exposure is set-and-forget.
- **Vega adds a second variable**: Pre-catalyst IV expansion could temporarily offset theta losses, but this is speculative and depends on market sentiment toward the readout. Post-catalyst (if options were still alive), IV crush would destroy remaining time value.

**Net effect**: The options position starts as a ~$36M biotech bet and degrades into something materially smaller, less predictable, and more expensive to maintain — all while never reaching the catalyst.

---

## When Defined-Loss Is Worth the Theta Cost

Options' defined-risk feature is genuinely valuable in specific circumstances:

| Scenario | Defined Loss Worth It? | Rationale |
|---|---|---|
| Binary event within option life | **Yes** | Cap downside on known catalyst; pay theta as insurance premium |
| High portfolio concentration risk | **Yes** | Limit max drawdown contribution from single name |
| Conviction is moderate, sizing would otherwise be smaller | **Yes** | Options allow meaningful delta with limited capital at risk |
| Catalyst is after expiry | **No** | Paying insurance premium for coverage that lapses before the event |
| Stock-flat scenario is likely | **No** | Theta destroys capital with no offsetting benefit |
| Thesis requires patience | **No** | Time decay punishes waiting; equity does not |

In this specific case, the $2.16M theta cost buys protection that **expires before the risk event occurs**. The insurance analogy: you're paying for a 4-month homeowner's policy when the hurricane season starts in month 5.

---

## Recommendation: Hybrid Structure with Corrected Tenor

### Proposed Structure

| Component | Size | % NAV | Purpose |
|---|---|---|---|
| **Equity position** | $26M | 3.5% | Core exposure — survives delays, no time decay, stable delta |
| **6-month ATM calls** | $3M premium (~$18M delta at 0.90) | 0.4% | Leveraged upside capture through and beyond the catalyst |
| **Total initial delta** | ~$44M | — | Slightly above original $40M target; options delta will decay |
| **Total capital at risk** | $29M max ($26M equity + $3M premium) | 3.9% | vs. $40M in pure equity or $6M in pure options |

### Why This Structure

1. **Fixes the timeline mismatch**: 6-month calls survive to the 5-month readout with 1 month of buffer for delays. This is the minimum acceptable tenor — 7–8 month options would be preferable if available and liquid.

2. **Reduces theta drag**: $3M in 6-month calls generates roughly $7–9K/day in theta (vs. $18K/day for $6M in 4-month calls), and the longer tenor means theta acceleration is less severe during the holding period.

3. **Preserves defined-loss benefit**: Max loss on the options tranche is $3M (0.4% NAV) — meaningful but not portfolio-damaging. The equity tranche's max loss is theoretically $26M but practically bounded by stop-loss discipline.

4. **Maintains capital efficiency**: Total capital deployed is $29M vs. $40M for pure equity, freeing ~$11M (1.5% NAV) for other positions.

5. **Equity core survives delays**: If the readout slips to month 7 or 8, the $26M equity position is unaffected. The 6-month calls may still be alive or can be rolled.

6. **Portfolio risk profile is more manageable**: Gamma and vega exposure from $3M in options is modest vs. $6M. The portfolio's daily delta fluctuation from this position is dampened.

### Alternative Structures Considered

| Structure | Verdict | Reason |
|---|---|---|
| 100% equity ($40M) | Acceptable but suboptimal | No defined loss; 5.3% NAV concentration in single biotech name is aggressive |
| 100% 4-month calls ($6M) | **Rejected** | Expires before catalyst; $2.16M theta drag for coverage that doesn't reach the event |
| 100% 6-month calls ($6M) | Viable but fragile | Entire position is time-decaying; stock-flat scenario still costly; no delay buffer beyond 1 month |
| 50/50 equity + 4-month calls | **Rejected** | Still has the 4-month expiry problem on half the position |
| Equity + 6-month calls (recommended) | **Selected** | Best balance of catalyst capture, delay resilience, defined loss, and capital efficiency |

---

## Risk Management Framework

### Position Monitoring Triggers

| Trigger | Action |
|---|---|
| Stock declines >20% | Reassess thesis; consider trimming equity to 2% NAV |
| Options delta falls below 0.60 | Evaluate rolling to higher-delta strike or adding equity |
| Catalyst delayed beyond 6 months | Options at risk — roll if possible; equity position unaffected |
| IV expands >30% pre-catalyst | Consider selling portion of calls to monetize vega gain |
| Competitor data changes landscape | Full thesis reassessment regardless of expression |

### P&L Scenarios at Month 5 (Hybrid Structure)

| Stock Move | Equity P&L ($26M) | 6-Mo Call P&L ($3M premium) | Total P&L | Pure Equity P&L ($40M) |
|---|---|---|---|---|
| +40% | +$10.4M | ~+$7.5M | **+$17.9M** | +$16.0M |
| +20% | +$5.2M | ~+$2.8M | **+$8.0M** | +$8.0M |
| Flat | $0 | ~-$1.5M (theta) | **-$1.5M** | $0 |
| -20% | -$5.2M | ~-$2.5M | **-$7.7M** | -$8.0M |
| -50% | -$13.0M | -$3.0M (max) | **-$16.0M** | -$20.0M |

The hybrid outperforms pure equity in large up-moves (convexity from calls) and large down-moves (defined loss on options tranche). It underperforms in flat scenarios due to theta. This is the correct tradeoff for a catalyst-driven thesis.

---

## Key Principles for Expression Selection

1. **Options tenor must exceed catalyst timeline by ≥1 month** — biotech delays are the norm, not the exception.
2. **Theta is not free leverage** — $2.16M over 4 months is a real cost that must be justified by the risk profile improvement.
3. **Initial delta equivalence is meaningless** — delta at entry ≠ delta over the holding period. Options' effective exposure degrades daily.
4. **Capital efficiency is only valuable if the position survives to the catalyst** — a cheap position that expires worthless before the event has infinite effective cost.
5. **Portfolio-level greeks matter** — adding $6M in options changes the portfolio's gamma, vega, and theta profile in ways that $40M in equity does not. Both must be evaluated at the portfolio level, not in isolation.
6. **Hybrid structures resolve false binary choices** — the question is rarely "options OR equity" but rather "what blend optimizes for thesis expression, risk management, and catalyst timing?"

---

*This analysis is for institutional discussion purposes. All scenarios are probabilistic estimates; actual outcomes depend on clinical data, market conditions, and catalyst timing, none of which can be predicted with certainty.*