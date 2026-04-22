

# Portfolio Construction Memo: Drawdown Budget as Binding Constraint

## Executive Summary

**Situation**: PM at multi-manager platform, down 3.8% YTD against -5.0% hard stop-loss
**Remaining Drawdown Budget**: 1.2%
**Proposed Trade**: Factory automation idea, 8/10 conviction, analyst recommends 3% position
**Recommendation**: **DO NOT SIZE AT 3%. Maximum new position ≈ 0.5–0.7%, and even that is questionable given existing portfolio risk already threatens the budget.**

**One-sentence thesis**: The stop-loss is a survival constraint, not an optimization input — the question is not "how much should we own" but "how much can we own without risking forced liquidation."

---

## Constraint Hierarchy: Survival Dominates Optimization

### The Stop-Loss Is a Hard Wall, Not a Guideline

The -5.0% drawdown limit triggers **mandatory 50% gross reduction within 48 hours** (source: context.risk_limits). This is not a risk preference — it is an institutional rule with career-ending asymmetry. The hierarchy is unambiguous:

| Priority | Constraint | Status |
|----------|-----------|--------|
| 1 (absolute) | Survive: stay above -5.0% | **1.2% remaining — critical** |
| 2 | Optimize: maximize risk-adjusted returns | Subordinate to #1 |
| 3 | Express conviction: size to Kelly/edge | Irrelevant near hard stop |

Gross exposure has already been reduced from 200% to 160% at the warning level (source: context.risk_limits). The platform is already signaling that this book is in the danger zone. Adding a full-sized position into this context is not bold — it is reckless.

### Why Conviction and Kelly Are Irrelevant Here

The analyst's argument has three flaws, each independently fatal:

**1. Kelly criterion assumes no hard constraints.**
Kelly optimizes the geometric growth rate of wealth over an infinite horizon. It explicitly assumes you can always play the next round. A hard stop-loss violates this foundational assumption. Near a binding constraint, Kelly-optimal sizing can be the fastest route to forced liquidation. As noted in the autonomous trading literature: "Without [risk constraints], the trading portfolio becomes like the 'fx daytrader', with monster-sized profits on Wednesday, and monster losses on Thursday" (source: Artificial_Intelligence_Powered_Finance.pdf, §4.5).

**2. Conviction scores are sizing inputs for unconstrained portfolios.**
An 8/10 conviction score determines where a position falls in the sizing hierarchy *when you have room to express it*. With 1.2% of drawdown budget remaining, the binding input is not conviction — it is the distance to the wall. A 10/10 idea would face the same constraint.

**3. "The drawdown is from macro, not stock-picking" is attribution rationalization.**
The stop-loss does not distinguish between sources of loss. The platform's risk system does not care whether your -3.8% came from macro, factor exposure, or bad stock picks. P&L is P&L. The analyst is constructing a narrative to justify ignoring the constraint — this is precisely the cognitive bias that blows up books.

---

## Risk Quantification

### The Proposed 3% Position Exceeds the Budget

| Metric | Value | Source |
|--------|-------|--------|
| Position size (proposed) | 3.0% of NAV | Analyst recommendation |
| Single-name annualized vol | 28% | context.risk_math |
| Daily vol (28% / √252) | ~1.76% | Derived |
| 2-sigma daily loss on 3% position | 3.0% × 1.76% × 2 = **1.06%** | Derived (daily) |
| 2-sigma move (context's framing) | **1.68%** | context.risk_math |
| Remaining drawdown budget | **1.20%** | context.risk_limits |
| Overshoot | **0.48%** (40% over budget) | Derived |

The 1.68% figure from context likely reflects a multi-day or slightly different vol window, but the conclusion is identical: a 2-sigma event in a 3% position **blows through the stop-loss by ~40%**.

### Existing Portfolio Risk Already Threatens the Budget

This is the dimension the analyst is ignoring entirely:

| Metric | Value | Source |
|--------|-------|--------|
| Existing portfolio daily vol | 0.65% | context.existing_portfolio_risk |
| 2-sigma daily loss (existing book) | **1.30%** | Derived |
| Remaining drawdown budget | **1.20%** | context.risk_limits |
| Deficit | **(0.10%)** | **Already exceeded** |

**The existing portfolio, with zero new positions, already has a 2-sigma daily loss (1.30%) that exceeds the remaining budget (1.20%).** This means:

- On any given day, there is roughly a **2.3% probability** (one-tail of normal beyond 2σ) that the existing book alone breaches the stop-loss
- Over 20 trading days, the probability of at least one 2-sigma down day is approximately **37%** (1 - 0.977^20)
- Adding *any* new risk makes this worse, not better

The correct first-order action is likely **reducing existing gross exposure further**, not adding new positions.

---

## Maximum Position Size Calculation

### Working Backward from the Constraint

The question is: given the remaining 1.2% budget and existing portfolio risk, how large can a new position be such that the combined portfolio's 2-sigma loss stays within budget?

**Simplified approach (assuming zero correlation with existing book — optimistic):**

Total portfolio 2σ loss = √(existing_2σ² + new_position_2σ²) ≤ 1.20%

Existing 2σ = 1.30% → Already exceeds 1.20%. **Under this framework, the maximum incremental risk is zero.**

**Practical approach (acknowledging we won't fully de-risk the existing book):**

If we reduce existing gross by 10-15% (bringing daily vol to ~0.55-0.58%) and assume low correlation:

| Scenario | Existing 2σ | New Position Size | New 2σ | Combined 2σ | Within Budget? |
|----------|-------------|-------------------|--------|-------------|----------------|
| A: No new position, reduce gross | 1.10% | 0% | 0% | 1.10% | ✅ Marginal |
| B: Small position, reduce gross | 1.05% | 0.5% | 0.50% | ~1.16% | ✅ Barely |
| C: Medium position, reduce gross | 1.05% | 1.0% | 0.99% | ~1.44% | ❌ |
| D: Analyst's recommendation | 1.30% | 3.0% | 1.68% | ~2.13% | ❌❌ |

*New position 2σ calculated as: position_size × 28% vol / √252 × 2. Combined assumes ~0.2 correlation.*

**Maximum defensible position: ~0.5% of NAV**, and only if accompanied by a reduction in existing gross exposure. Even this carries meaningful risk of breaching the stop-loss.

---

## Platform Consequences: Asymmetric Payoffs

### Breach vs. Opportunity Cost

| Outcome | Probability | Consequence | Reversibility |
|---------|-------------|-------------|---------------|
| **Stop-loss breach** | Material (>5% over 1 month given current vol) | 50% forced gross reduction in 48 hours; probable probation; potential termination of allocation | **Largely irreversible** — forced selling at worst prices, reputation damage, loss of seat |
| **Miss the factory automation trade** | 100% if we pass | Forgo potential alpha on a high-conviction idea | **Fully recoverable** — idea can be revisited when budget replenishes; other ideas will emerge |
| **Small position (0.5%)** | Compromise | Capture ~1/6th of intended exposure; limited P&L impact either way | Preserves optionality |

The expected value calculation is overwhelmingly in favor of survival:

- **Upside of 3% position**: If the idea works (say +20% over 6 months), the P&L contribution is +0.6%. Meaningful but not transformative.
- **Downside of stop-loss breach**: Forced 50% gross reduction crystallizes losses, eliminates ability to recover through the rest of the year, triggers probation, and likely ends the PM's allocation at the platform. The NPV of a PM seat at a multi-manager platform dwarfs any single trade's alpha.

This is not a close call. The analyst is optimizing for one trade's P&L; the PM must optimize for the survival of the entire book.

---

## Recommended Action Plan

### Immediate Steps

1. **Do not add the factory automation position at 3%.** This is non-negotiable given the constraint math.

2. **Audit existing portfolio risk.** Daily vol of 0.65% at 160% gross means the book is already in the danger zone. Identify positions that can be trimmed to bring 2σ daily loss below 1.0%.

3. **If adding factory automation, size at 0.5% maximum** — and only after reducing existing gross to bring combined 2σ daily loss to ≤1.0% (leaving a 0.2% buffer against the 1.2% budget).

4. **Communicate to the analyst** that the constraint hierarchy is: survive → recover → optimize. The factory automation idea is noted and will be sized appropriately when the drawdown budget replenishes. If the idea is truly durable (factory automation is a secular theme), it will still be there in Q2/Q3.

5. **Consider whether the right trade is actually reducing risk**, not adding it. The highest-EV action for the book right now may be cutting gross to 130-140% and waiting for the drawdown to recover organically.

### Decision Framework for Near-Stop-Loss Sizing

```
IF remaining_budget < existing_portfolio_2σ_daily:
    → REDUCE existing risk first
    → New positions only if they REPLACE risk (hedges, lower-vol substitutions)

IF remaining_budget > existing_portfolio_2σ_daily (with margin):
    → Size new positions such that:
      combined_2σ ≤ remaining_budget × 0.80  (20% safety margin)
    → Never size any single position where its standalone 2σ > remaining_budget

ALWAYS:
    → Stop-loss is a hard constraint, not a target to approach
    → Kelly/conviction are inputs to the sizing function ONLY in unconstrained regime
    → Near the stop-loss, the objective function changes from max(returns) to max(P(survival))
```

---

## Key Takeaways

| Principle | Application |
|-----------|-------------|
| Survival > Optimization | Stop-loss breach consequences are asymmetric and largely irreversible |
| Budget is binding | 1.2% remaining; existing book's 2σ daily (1.30%) already exceeds it |
| Kelly is irrelevant | Kelly assumes infinite horizon with no hard stops — inapplicable here |
| Attribution doesn't matter | "Macro-driven" losses count the same as stock-picking losses at the stop |
| Opportunity cost is recoverable | Missing one trade is recoverable; losing your seat is not |
| Max position ≈ 0.5% | And only with concurrent reduction in existing gross exposure |

---

*This analysis assumes normal distribution of returns for 2-sigma calculations; actual tail risk is likely higher given documented gain/loss asymmetry in equity markets (source: Revisiting Cont's Stylized Facts, §3). All position sizing recommendations are illustrative and should be validated against the platform's specific risk system and correlation assumptions.*