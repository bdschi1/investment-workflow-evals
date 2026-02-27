# Golden Answer: Capital vs. Risk - The High-Vol Trap

## Executive Summary

**Claim Under Review:** PM states Position A (10% in Mega-Cap Pharma, 15% vol) is "more than twice as risky" as Position B (4% in Small-Cap Biotech, 60% vol) because it has more than double the capital
**Verdict:** The PM's assessment is incorrect. Position B contributes 60% more risk to the portfolio despite having less than half the capital allocation.
**Core Insight:** The PM is caught in the high-vol trap: they see a small-looking 4% allocation and conclude it is the smaller risk. But the 60% volatility transforms that 4% into a risk contribution of 2.4 units, versus 1.5 units for the 10% Pharma position. The position that looks small in notional terms is the one that will dominate P&L.

---

## Correcting the PM's Error

### The Math

| Position | Weight | Volatility | Risk Contribution (W x Vol) |
|----------|--------|------------|---------------------------|
| Position A: Mega-Cap Pharma | 10% | 15% | **1.5%** |
| Position B: Small-Cap Biotech | 4% | 60% | **2.4%** |

Position B contributes **60% more risk** than Position A. The PM's claim that Position A is "more than twice as risky" is not just wrong -- it is inverted. Position B is the dominant risk driver.

### Why the PM Gets This Wrong

The PM's error has a specific cognitive source: **notional anchoring.** The brain naturally defaults to comparing dollar amounts because they are concrete and intuitive. "10% is bigger than 4%" is immediately obvious. "15% vol versus 60% vol" requires a multiplication step that is not intuitive.

This is not a sign of incompetence. It is one of the most common errors in professional portfolio management. Studies of PM behavior consistently find that capital allocation is conflated with risk allocation, even among experienced practitioners.

### The Dollar Volatility Reality

On a $100M portfolio:

| Position | Notional | Annual Vol | Annual Dollar Vol | Daily Dollar Vol (~1/16 ann) |
|----------|---------|-----------|-------------------|---------------------------|
| Pharma | $10.0M | 15% | $1,500,000 | $93,750 |
| Biotech | $4.0M | 60% | $2,400,000 | $150,000 |

Every day, the Biotech position will generate roughly 60% more P&L variance than the Pharma position. Over a month, the Biotech's expected range of outcomes is far wider. The PM will repeatedly find themselves explaining portfolio performance by reference to the Biotech -- the "smaller" position -- rather than the Pharma.

---

## Why This Matters: Practical Consequences

### 1. P&L Attribution Is Dominated by the "Small" Position

Run this portfolio for any 30-day period and attribute daily P&L to each position. The Biotech will be the top contributor to portfolio variance on approximately 70% of days, despite the PM perceiving it as the minor position. The PM's daily portfolio narrative is disconnected from reality.

### 2. Drawdown Scenarios Reveal the Inversion

| Scenario | Position Move | Portfolio Impact | Event Probability |
|----------|-------------|-----------------|------------------|
| Pharma -10% (0.67 sigma) | -10% x 10% | -1.0% NAV | ~30-35% annually |
| Biotech -30% (0.5 sigma) | -30% x 4% | -1.2% NAV | ~35-40% annually |
| Biotech -50% (0.83 sigma) | -50% x 4% | -2.0% NAV | ~25-30% annually |
| Pharma -20% (1.33 sigma) | -20% x 10% | -2.0% NAV | ~10-15% annually |

A 30% Biotech decline (a half-sigma event -- very common for a 60% vol stock) produces a larger portfolio drawdown than a 10% Pharma decline. And a 50% Biotech decline (still less than 1 sigma) equals the impact of a 20% Pharma decline (a 1.33-sigma event that is far less likely).

### 3. Variance Attribution Amplifies the Gap

For portfolio-level volatility, **squared risk contributions** determine the answer:

- Pharma: (1.5)^2 = 2.25
- Biotech: (2.4)^2 = 5.76

The Biotech contributes **2.56x more to portfolio variance.** This means its influence on portfolio-level volatility statistics (Sharpe ratio, drawdown expectations, VaR) is even greater than the linear 60% gap suggests.

### 4. Volatility of Volatility Compounds the Problem

Small-cap biotech volatility is itself volatile. The 60% trailing estimate may understate risk during catalyst periods:

| Period | Expected Biotech Vol | Risk Contribution | Pharma Multiple |
|--------|---------------------|-------------------|----------------|
| Normal | 60% | 2.4% | 1.6x |
| Pre-catalyst | 80-100% | 3.2-4.0% | 2.1-2.7x |
| Post-binary event (spike) | 100-120% | 4.0-4.8% | 2.7-3.2x |

During catalyst periods, the Biotech's risk contribution could reach 3x the Pharma's. The PM's mental model becomes increasingly wrong precisely when accuracy matters most.

---

## Correct Sizing for Equal Risk

### To Equalize Risk Contribution

**Target:** Position A risk = Position B risk
- w_A x vol_A = w_B x vol_B
- 10% x 15% = w_B x 60%
- w_B = 1.5% / 60% = **2.5%**

At **2.5% weight** (not 4%), the Biotech would contribute equal risk to the 10% Pharma position. The PM currently allocates 60% more risk to the Biotech than to the Pharma without realizing it.

### Sizing Options

| Approach | Pharma Weight | Biotech Weight | Risk Ratio (B:A) |
|----------|--------------|----------------|-----------------|
| Equal risk | 10% | 2.5% | 1.0:1.0 |
| Pharma-tilted risk | 10% | 1.25% | 0.5:1.0 |
| **Current (unintentional)** | **10%** | **4.0%** | **1.6:1.0** |
| Intentional biotech tilt | 10% | 4.0% | 1.6:1.0 |

The current allocation looks identical to an intentional Biotech-tilted strategy. The PM's stated belief reveals it is unintentional.

---

## The Trap: Why "High-Vol" Sounds Like "Small Position"

The PM's error has a subtle behavioral component. "4% in Small-Cap Biotech" *sounds* small. The label "small-cap" reinforces the perception of a minor position. The 60% volatility figure, while stated, does not register as a sizing-relevant input because the PM's framework is notional-based.

This is the "high-vol trap": high-volatility positions *look* small because they typically receive lower capital allocations. But their risk contribution is disproportionately large. The small notional weight creates a false sense of containment.

**The corrective mental model:** Think in P&L contribution, not dollar allocation. Ask: "If both positions move by one standard deviation, which one hurts more?" For the Pharma, one sigma is $150,000. For the Biotech, it is $240,000. The Biotech is the bigger position in the only dimension that matters for risk management.

---

## Recommended Actions

### Immediate

1. **Correct the PM's risk perception** with the W x Vol calculation and the dollar P&L comparison. Show, don't tell.
2. **Run 90-day P&L attribution** to demonstrate which position has actually been driving portfolio returns. The data will confirm the math.

### Near-Term

3. **Decide on intentional risk allocation:**
   - If equal risk is intended: Reduce Biotech from 4.0% to 2.5%
   - If Biotech dominance is intended (high conviction): Keep at 4.0%, but document the risk allocation and set explicit limits
   - If risk reduction is desired: Reduce Biotech to 1.25% (risk-tilted toward Pharma)

### Structural

4. **Implement dual reporting:** Every position report should show notional weight AND risk contribution. This makes the gap visible by default.
5. **Set risk contribution limits:** No single position above 15-20% of total portfolio risk contribution without explicit approval.
6. **Run full portfolio risk attribution** to identify all positions where notional weight diverges from risk contribution. This is unlikely to be the only instance.

---

## Summary: Key Principles

1. **Risk contribution = Weight x Volatility.** The 4% Biotech at 60% vol contributes 2.4 units; the 10% Pharma at 15% vol contributes 1.5 units. The "small" position is the "big" risk.

2. **Notional weight is not risk weight.** Capital allocation tells you how much money is at work. Risk contribution tells you how much the portfolio moves. These are different questions with different answers.

3. **The PM's error is inverted, not approximate.** The PM claims A is more than twice as risky as B. In reality, B is 60% riskier than A. The PM's risk ranking is backwards.

4. **Squared contributions amplify the gap.** At the variance level, the Biotech contributes 2.56x more than the Pharma, meaning its impact on portfolio-level risk metrics is even more dominant.

5. **Vol-of-vol makes it worse over time.** Small-cap biotech vol is unstable. During catalysts, the risk contribution gap widens further -- to 2-3x the Pharma -- precisely when getting it right matters most.

6. **The fix is framework-level, not position-level.** This is not about one pair of positions. It is about installing risk-based thinking as the default portfolio construction lens.

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Risk-based sizing (Weight x Volatility) per Paleologo (2021)
