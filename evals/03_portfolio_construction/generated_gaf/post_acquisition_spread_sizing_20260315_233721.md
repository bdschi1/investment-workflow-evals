

# Investment Memo: Post-Acquisition Spread Sizing

## Executive Summary
**Security**: Large-Cap Gaming Target
**Current Price**: $87.00 | **Offer Price**: $95.00 | **Unaffected Break Price**: $62–68
**Recommendation**: REDUCE SIZE — 1.5% position maximum (down from analyst's proposed 4%)
**Time Horizon**: 6–9 months to regulatory resolution
**Risk/Reward**: ~3:1 adverse (9.2% upside vs. 22–29% downside)

**One-sentence thesis**: The analyst's 4% position at 80% close probability materially overstates edge and understates ruin risk; the spread is insufficient compensation for a CMA-dependent binary with negative expected value at realistic probabilities.

---

## Payoff Asymmetry Analysis

### The Core Problem

| Scenario | Price | Return from $87 | Probability (Analyst) | Probability (Calibrated) |
|---|---|---|---|---|
| Deal closes | $95 | +9.2% | 80% | 65–70% |
| Deal breaks (base) | $68 | -21.8% | 20% | 30–35% |
| Deal breaks (stress) | $62 | -28.7% | — | Tail within break |

The payoff is ~3:1 adverse. For every dollar of upside, the position risks losing ~$2.70–3.10 on the downside. This is not a symmetric bet where expected value alone drives sizing — it is a binary outcome where the conditional loss magnitude dominates the risk calculus.

### Expected Value Sensitivity

| Close Probability | EV (using $65 midpoint break) | EV vs. Current $87 |
|---|---|---|
| 80% (analyst) | $89.00 | +$2.00 (+2.3%) |
| 75% (consensus high) | $87.50 | +$0.50 (+0.6%) |
| 70% (consensus low) | $86.00 | **-$1.00 (-1.1%)** |
| 65% (CMA-adjusted) | $84.50 | **-$2.50 (-2.9%)** |

**At 70% close probability, the expected value is approximately $85.40–$86.00 — below the current $87 price.** The stock is already pricing in a higher close probability than base rates support. The analyst's 80% assumption creates the illusion of a positive EV trade that likely does not exist.

---

## Probability Calibration: The Analyst Is Wrong

### CMA Base Rate Problem
The CMA Phase 2 historically blocks ~65% of digital markets cases. This is the single most important data point in the analysis and the analyst's memo does not adequately weight it.

**Why 80% is poorly calibrated:**

1. **CMA Phase 2 block rate for digital markets: ~65%**. If the deal reaches Phase 2 (likely given gaming sector scrutiny), the conditional probability of CMA clearance drops to ~35%. Even weighting in the possibility of Phase 1 clearance or remedies, a blended CMA approval probability of 50–60% is more defensible.

2. **Three-jurisdiction requirement** compounds risk. Even if each jurisdiction has independent 85–90% approval odds, the joint probability is materially lower: 0.85³ = 61%. The analyst appears to be anchoring on a single-jurisdiction estimate.

3. **Consensus at 70–75% already reflects informed market participants**. The analyst's 80% implies a 5–10 point edge over the market with no cited proprietary information or differentiated regulatory analysis to justify the deviation.

4. **Sensitivity is extreme at the margin**: Moving from 80% → 70% flips the EV from +2.3% to -1.1%. A 10-point probability error — well within the range of uncertainty for a CMA-dependent deal — transforms the trade from "attractive" to "value-destroying."

**Calibrated range: 65–72% close probability.** At the midpoint (~68%), this trade has negative expected value.

---

## Opportunity Cost: The Risk-Free Hurdle

This is the most underappreciated dimension.

| Metric | Merger Arb Position | T-Bills (Risk-Free) |
|---|---|---|
| Gross return if successful | +9.2% | +5.2% annualized |
| Time horizon | 6–9 months | Same |
| Pro-rated risk-free return (7.5mo avg) | +3.25% | +3.25% |
| **Excess spread over risk-free** | **+5.95% gross** | **0%** |
| Probability-weighted excess (at 70%) | **-4.35%** | **0%** |
| Max loss | -22% to -29% | 0% |

The 9.2% gross spread sounds attractive until you subtract the 3.25% you earn risk-free over the same period. The incremental compensation for bearing deal-break risk is ~5.95% gross — and at 70% close probability, the risk-adjusted excess return is deeply negative.

**$40M tied up for 7.5 months at 5.2% risk-free = ~$1.3M of guaranteed income foregone if the deal breaks.** That's real money against a position that has negative expected value at realistic probabilities.

---

## Portfolio Context & Concentration

### Existing Exposure

| Category | Current | Proposed Addition | Pro Forma |
|---|---|---|---|
| Merger arb positions | 4.5% of NAV | +4.0% | 8.5% of NAV |
| Event-driven (total) | ~4.5% | +4.0% | ~8.5% |

**8.5% in merger arb is excessive** for a strategy that has returned only +2.8% YTD on the index level. Key concerns:

1. **Correlation in stress**: Deal breaks cluster. Regulatory tightening (CMA, FTC, DOJ) is a macro factor that hits all arb positions simultaneously. If the CMA blocks this deal, it signals a hawkish posture that likely widens spreads across the book. The existing 4.5% is not independent of this new position.

2. **Capital efficiency**: At 8.5% of NAV in merger arb generating ~3% annualized (index YTD pace), the portfolio is allocating significant capital to a strategy barely beating risk-free. The marginal dollar in arb must clear a higher bar.

3. **Liquidity risk**: Large-cap gaming stocks can gap violently on deal breaks. The Microsoft/Activision CMA saga demonstrated that gaming M&A attracts intense regulatory scrutiny and generates discontinuous price moves. Forced selling by arb funds amplifies the break-price overshoot — the $62 low end of the break range likely reflects this dynamic.

---

## Recommended Position Sizing

### Framework: Conditional Loss Sizing

The correct approach sizes off the **conditional loss in the break scenario**, not the expected value.

**Step 1: Define maximum tolerable loss from any single merger arb position**
- Reasonable limit: 50–75bps of NAV from a single deal break
- At a $1B portfolio, that's $5.0–7.5M

**Step 2: Back into position size from conditional loss**
- Break loss: -25% (midpoint of -22% to -29%)
- Max position = $7.5M / 0.25 = **$30M = 3.0% of NAV** (upper bound)
- Max position = $5.0M / 0.25 = **$20M = 2.0% of NAV** (lower bound)

**Step 3: Adjust for negative EV and portfolio concentration**
- EV is likely negative at calibrated probabilities → further reduce
- Existing 4.5% arb exposure → penalize for correlation

### Recommendation

| Parameter | Analyst Proposal | Recommended |
|---|---|---|
| Position size | 4.0% ($40M) | **1.0–1.5% ($10–15M)** |
| Close probability assumed | 80% | 65–72% |
| Max portfolio loss (break) | $8.8–11.5M | $2.5–4.4M |
| Total arb exposure (pro forma) | 8.5% | 5.5–6.0% |

**1.5% is the maximum defensible size.** Even this requires a differentiated view on CMA clearance that the analyst has not articulated. At 1.0%, the position becomes a small "option" on deal completion that doesn't impair the portfolio if it breaks.

If the analyst cannot articulate a specific, evidence-based reason why CMA clearance probability exceeds 70%, the position should be **zero**.

---

## Alternative Expressions

Options structures better match this binary payoff profile:

### 1. Bull Call Spread (Preferred)
- Buy $87 calls / Sell $95 calls, expiring post-expected close
- Max gain: $8/share (same as deal spread)
- Max loss: Premium paid (likely $3–4/share vs. $19–25/share equity loss)
- **Dramatically improves risk/reward from 3:1 adverse to ~2:1 favorable**

### 2. Risk Reversal (Sell Puts, Buy Calls)
- Not recommended — selling puts reintroduces the downside tail

### 3. Outright Call Purchase
- Buy slightly OTM calls ($88–90 strike)
- Defined risk, leveraged upside
- Premium decay is a cost, but far less than the -25% equity gap risk

### 4. Pairs Trade
- Long target / Short acquirer (if public) to hedge market risk
- Does not hedge deal-break risk but reduces beta exposure during the wait

**Key insight**: Implied volatility on the target likely reflects elevated deal uncertainty. If put skew is steep (per the volatility skew framework), selling put spreads below the break price could partially finance call spreads — but only if the skew premium is genuinely excessive relative to break probability.

---

## Decision Matrix

| Condition | Action |
|---|---|
| Analyst provides differentiated CMA thesis with >75% close probability supported by evidence | 1.5% equity position |
| No differentiated thesis; relying on consensus | 1.0% via bull call spread only |
| CMA announces Phase 2 investigation | Exit or reduce to 0.5% |
| Spread widens to >15% (price drops to ~$82) | Reassess — may improve risk/reward if probability unchanged |
| Risk-free rate declines below 4% | Modestly increases relative attractiveness of spread |

---

## Key Takeaways for the Analyst

1. **You are not being paid enough for this risk.** A 9.2% spread with 3:1 adverse asymmetry and negative EV at base-rate probabilities is not an opportunity — it's a trap dressed as yield.

2. **80% is not a probability estimate; it's an aspiration.** The CMA's 65% Phase 2 block rate in digital markets is the prior. You need extraordinary evidence to override it, and you haven't provided any.

3. **Compare everything to 5.2% risk-free.** If you can't articulate why this binary risk deserves capital over T-bills, the answer is T-bills.

4. **Size off the loss, not the gain.** In binary outcomes, the question is never "how much do I make if I'm right?" — it's "how much do I lose if I'm wrong, and can the portfolio absorb it?"

5. **Use options.** When the payoff is binary and asymmetric, equity is the wrong instrument. A bull call spread converts a -25% tail into a defined premium loss.

---

*This analysis is based on the scenario as presented and publicly available CMA historical data. Actual deal probabilities depend on jurisdiction-specific regulatory dynamics, remedy negotiations, and political factors not fully captured here. All probability estimates are subjective and should be treated as ranges, not point estimates.*