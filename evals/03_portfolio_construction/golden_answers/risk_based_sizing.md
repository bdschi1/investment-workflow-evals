# Golden Answer: Notional vs. Risk-Based Sizing

## Executive Summary

**Claim Under Review:** PM states the 10% Large-Cap Pharma position (12% vol) is the "primary risk driver" because it has double the capital allocation of the 5% Small-Cap Biotech position (60% vol)
**Verdict:** The PM is mathematically incorrect. Risk contribution is Weight x Volatility. Pharma contributes 1.2 units; Biotech contributes 3.0 units. The Biotech position is 2.5x riskier despite having half the capital.
**Core Insight:** Notional weight is a poor proxy for risk. Dollar allocation determines how much capital is at work; risk contribution determines how much the portfolio actually moves. A PM who sizes on notional and monitors on notional will systematically misunderstand which positions drive P&L variance.

---

## The Notional Bias Error

### The PM's Logic (Incorrect)

The PM reasons: "I have 10% in Pharma and 5% in Biotech. The larger position is more than twice as risky because it has more than double the capital."

This reasoning contains an implicit assumption: **risk scales linearly with capital allocation, independent of volatility.** This is false.

### The Correct Calculation

**Risk contribution = Weight x Volatility**

| Position | Weight (w) | Volatility (sigma) | Risk Contribution (w x sigma) | % of Total Risk |
|----------|-----------|-------------------|-------------------------------|----------------|
| Large-Cap Pharma | 10% | 12% | **1.2 units** | 29% |
| Small-Cap Biotech | 5% | 60% | **3.0 units** | **71%** |
| **Total** | 15% | | **4.2 units** | 100% |

The Biotech position contributes **2.5x more risk** to the portfolio than the Pharma position, despite having half the capital. The PM's mental model is inverted.

### Dollar Volatility: What Moves the Portfolio

On a $100M portfolio:

| Position | Notional | Daily Vol (ann/sqrt(252)) | Daily Dollar P&L at 1-sigma |
|----------|---------|--------------------------|---------------------------|
| Pharma | $10.0M | 0.76% | $75,600 |
| Biotech | $5.0M | 3.78% | $189,000 |

The Biotech generates **2.5x more daily P&L variance** than the Pharma. On any given day with a meaningful portfolio move, the Biotech will likely be the dominant contributor -- but the PM, anchored on notional weight, will instinctively look at the Pharma position for explanations.

---

## Why This Error Matters in Practice

### 1. P&L Attribution Will Be Dominated by the Biotech

Over any meaningful period, the Biotech's price moves will explain the majority of portfolio return variance. The PM will experience this as "the Biotech is always the story" without connecting it to the sizing error. The tail is wagging the dog, and the PM does not realize the tail exists.

### 2. Drawdown Risk Is Asymmetric

| Scenario | Move | Portfolio Impact | Probability (Annualized) |
|----------|------|-----------------|-------------------------|
| Pharma -15% | 1.25 sigma | -1.5% | ~20-25% |
| Biotech -40% | 0.67 sigma | -2.0% | ~30-40% |
| Biotech -60% | 1.0 sigma | -3.0% | ~25-30% |
| Both down (stress) | Pharma -8%, Biotech -30% | -2.3% combined | ~10-15% |

A 40% decline in a 60% vol biotech is a sub-1-sigma event on an annual basis -- not remotely unusual. It would create a 2.0% portfolio drawdown, exceeding the impact of a 15% pharma decline (which is a more unusual 1.25-sigma event) by a third.

### 3. Correlation Assumptions Compound the Problem

When considering portfolio-level variance, the squared risk terms determine the answer:

- Pharma squared contribution: (1.2)^2 = 1.44
- Biotech squared contribution: (3.0)^2 = 9.00

The Biotech contributes **6.25x more to portfolio variance** than the Pharma. This means the Biotech's influence on portfolio-level volatility is even more dominant than the linear risk comparison suggests.

### 4. The Error Likely Exists Portfolio-Wide

If the PM has notional bias on these two positions, it almost certainly applies across the entire book. Every high-vol position in the portfolio is likely undersized in the PM's risk mental model, and every low-vol position is likely oversized. A full portfolio risk attribution would likely reveal multiple instances where the actual risk driver is not the position the PM perceives as dominant.

---

## Correct Risk-Based Sizing

### Equal Risk Contribution

To equalize the risk contribution between the two positions:

**Target:** w_pharma x vol_pharma = w_biotech x vol_biotech

If Pharma stays at 10%:
- 10% x 12% = w_biotech x 60%
- w_biotech = 1.2% / 60% = **2.0%**

The Biotech should be **2.0% of the portfolio** (not 5%) for equal risk contribution. The PM currently has 2.5x more Biotech risk than Pharma risk.

### Vol-Normalized Sizing Table

| Desired Risk Allocation | Pharma Weight | Biotech Weight | Biotech Risk % |
|------------------------|---------------|----------------|---------------|
| Equal risk (1:1) | 10% | 2.0% | 50% |
| Pharma-tilted (2:1) | 10% | 1.0% | 33% |
| **Current (unintentional)** | **10%** | **5.0%** | **71%** |
| Biotech-tilted (intentional 2:1) | 10% | 5.0% | 71% |

The current sizing is identical to an intentional 2.5:1 Biotech-tilted allocation. If the PM intended that -- fine. But the PM's stated belief ("Pharma is the primary risk") reveals this is not intentional. The portfolio is misaligned with the PM's own risk framework.

### The Paleologo Framework

Per *Advanced Portfolio Management* (Paleologo, 2021), position sizing should be vol-normalized to ensure no single position dominates portfolio variance unintentionally:

**Vol-adjusted weight = Notional weight x (target vol / position vol)**

For a portfolio targeting each position to contribute equally to risk at 12% vol:
- Pharma: 10% x (12%/12%) = 10% (already calibrated)
- Biotech: 5% x (12%/60%) = 1.0% (current allocation is 5x oversized on a risk-adjusted basis)

---

## When Unequal Risk Allocation Is Acceptable

Unequal risk contribution is not inherently wrong -- it is wrong only when **unintentional.** Valid reasons to accept the Biotech as the dominant risk driver:

| Justification | Requirement |
|--------------|-------------|
| Asymmetric conviction: Binary catalyst with 3-5x upside potential | PM explicitly acknowledges the risk allocation and sizes for the downside |
| Risk budget allocation: Speculative bucket gets disproportionate risk | Written policy; PM knows the risk budget is concentrated here |
| Options-like structure: Defined downside through hedges or stops | Protective puts or hard stop limits the actual risk contribution |

**The critical test:** Ask the PM "which position would you expect to contribute the most to your monthly P&L variance?" If the answer is "Pharma," the allocation is unintentional and should be corrected. If the answer is "Biotech, and I'm comfortable with that," it may be acceptable with proper documentation and monitoring.

---

## Practical Recommendations

### Immediate Actions

1. **Show the PM the W x Vol math.** The most effective communication tool is the simple table. Most PMs immediately recognize the error when they see the numbers.

2. **Run historical P&L attribution.** Show the last 3-6 months of daily P&L decomposition. If the Biotech has been the dominant daily contributor (it almost certainly has), the data confirms the math.

3. **Decide whether the current allocation is intentional.** If yes, document the rationale and set risk limits on the Biotech. If no, reduce the Biotech to 2.0% to equalize risk.

### Structural Changes

4. **Implement risk-based position reporting.** Every position report should show both notional weight and risk contribution side by side. This makes notional bias visible.

5. **Set risk contribution limits.** Example: no single position should exceed 15-20% of total portfolio risk contribution. Currently, the Biotech is at 71% of this two-position subset -- likely violating any reasonable risk budget.

6. **Use vol-normalized sizing as the default.** When initiating new positions, calculate the vol-adjusted weight first, then decide if a deviation is intentional.

### Ongoing Monitoring

7. **Recalculate risk contributions weekly.** Small-cap biotech volatility is itself volatile (vol-of-vol is high). A position that was correctly sized three months ago may have shifted materially if realized vol has changed.

8. **Adjust for catalysts.** Pre-catalyst biotech vol may spike to 80-100% (options-implied). If a binary event is approaching, the risk contribution calculation should use forward-looking vol, not trailing.

9. **Review the full portfolio.** This two-position example is almost certainly not the only instance of notional bias. A full portfolio risk attribution will likely reveal additional positions where risk contribution diverges from the PM's expectations.

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| PM resists risk framework | Common in practice | Portfolio continues to be dominated by unintended risks | Show P&L data -- numbers convince more than theory |
| Biotech vol estimate is wrong | 30-40% (catalyst-driven spikes) | Risk imbalance worsens if vol goes to 80%+ | Use options-implied vol for forward-looking sizing |
| Correlation spikes in stress | 20-30% | Both positions decline together, compounding loss | Run stress scenarios with rho = 0.5-0.7 |
| Liquidity risk not captured | Elevated for small-cap biotech | Exit may be slow, extending drawdown duration | Factor days-to-liquidate into risk assessment |

---

## Summary: Key Principles

1. **Risk = Weight x Volatility, not just Weight.** The 5% Biotech is 2.5x riskier than the 10% Pharma. Capital allocation is not risk allocation.

2. **Notional bias is the most common PM error.** It is intuitive, persistent, and consequential. It leads to unintended risk concentration in high-vol positions and false comfort from the dollar weight of low-vol positions.

3. **The test is intentionality.** Unequal risk allocation is fine if deliberate. The PM's stated belief reveals this is unintentional -- and therefore a problem.

4. **Squared contributions matter for portfolio variance.** The Biotech contributes 6.25x more to portfolio variance than the Pharma. At the portfolio level, the Biotech's dominance is even more extreme than the linear risk comparison suggests.

5. **Fix the framework, not just this position.** If notional bias exists here, it likely exists portfolio-wide. The structural fix is risk-based reporting and vol-normalized sizing as default practice.

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Risk-based position sizing (Weight x Volatility framework) per Paleologo (2021) and Grinold & Kahn (2000)
