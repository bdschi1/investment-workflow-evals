

# Portfolio Construction Memo: Marginal VaR Sizing Analysis — EAIP Position

## Executive Summary

**Recommendation**: REJECT proposed 3% EAIP position. Size down to ≤0.20% or restructure the portfolio first.

**One-sentence thesis**: The proposed EAIP position has a standalone VaR of 0.80% but a marginal VaR of 2.10% — a 2.6x amplification driven by 0.65 correlation with MCLD — which would blow the portfolio's 2.0% VaR limit by nearly 2x. The position must be sized to marginal VaR, not standalone VaR.

| Metric | Value | Status |
|---|---|---|
| Current Portfolio VaR | 1.85% | 92% of limit |
| VaR Limit | 2.00% | Hard constraint |
| Remaining VaR Budget | 0.15% | Binding |
| EAIP Standalone VaR | 0.80% | Misleading input |
| EAIP Marginal VaR (at 3% size) | 2.10% | Correct sizing input |
| Portfolio VaR Post-Addition (3%) | ~3.95% | **197% of limit — breach** |
| MCLD Contribution to Portfolio VaR | 18% | Concentration risk |
| EAIP–MCLD Correlation | 0.65 | Primary risk driver |

**Verdict**: The position looks fine alone. It is not fine in this portfolio. Marginal VaR is the only valid sizing input, and it says this trade at proposed size is a limit breach by ~2x.

---

## 1. VaR Decomposition: Why Standalone VaR Is the Wrong Input

### Three Distinct Measures

| VaR Type | Definition | EAIP Value | Use Case |
|---|---|---|---|
| **Standalone VaR** | Risk of the position in isolation, ignoring all other holdings | 0.80% | Screening only — tells you nothing about portfolio impact |
| **Component VaR** | Portion of current portfolio VaR attributable to a position already held | N/A (EAIP not yet in portfolio) | Monitoring existing positions; sums to total portfolio VaR |
| **Marginal VaR** | Incremental change in total portfolio VaR from adding the position | 2.10% | **The correct sizing input for new positions** |

### Why Marginal VaR Governs

Standalone VaR assumes the position exists in a vacuum — zero correlation with everything else. This is never true and is especially misleading when the new position correlates 0.65 with the portfolio's largest VaR contributor (MCLD at 18% of portfolio VaR).

Marginal VaR captures the full interaction: the new position's own volatility **plus** the covariance terms with every existing holding. When correlation is high with a concentrated existing position, these covariance terms dominate. Here, they amplify the risk contribution by 2.6x (2.10% / 0.80%).

**The 0.80% standalone figure is not conservative — it is wrong as a sizing input.** Using it would be equivalent to treating two correlated bets as independent, which is the canonical portfolio construction error.

---

## 2. The Correlation-Driven Compounding Effect

### Mechanism

Portfolio variance is not additive — it follows:

$$\sigma_p^2 = \sum_i \sum_j w_i w_j \sigma_i \sigma_j \rho_{ij}$$

The cross-term between EAIP and MCLD is proportional to:

$$2 \cdot w_{EAIP} \cdot w_{MCLD} \cdot \sigma_{EAIP} \cdot \sigma_{MCLD} \cdot 0.65$$

At 0.65 correlation, this cross-term is large. Because MCLD already contributes 18% of portfolio VaR (itself a concentrated position), adding a correlated asset doesn't just add risk — it **amplifies the existing MCLD risk** while simultaneously introducing its own. The two positions reinforce each other's drawdowns roughly 65% of the time.

### Why This Is Compounding, Not Additive

| Scenario | Expected Behavior |
|---|---|
| ρ = 0.00 (uncorrelated) | Marginal VaR ≈ standalone VaR. Diversification benefit offsets. |
| ρ = 0.65 (actual) | Marginal VaR = 2.6x standalone. Cross-terms dominate. |
| ρ = 1.00 (perfect) | Marginal VaR would be even higher — pure concentration. |

The 0.65 correlation means that in a broad selloff of cloud/AI infrastructure, both MCLD and EAIP likely draw down together. The portfolio's tail risk becomes concentrated in a single thematic factor. This is not a diversifying addition — it is a doubling down.

**Critical point**: The danger is context-dependent, not inherent to EAIP. EAIP is not an inherently "risky" position. Its 0.80% standalone VaR is moderate. The problem is *this portfolio's* existing exposure to correlated risk via MCLD.

---

## 3. The Same Position in a Different Portfolio

In a portfolio without significant cloud/AI infrastructure exposure, EAIP's marginal VaR would converge toward its standalone VaR of 0.80%.

| Portfolio Context | Estimated EAIP Marginal VaR | Rationale |
|---|---|---|
| Current portfolio (MCLD = 18% of VaR) | ~2.10% | High correlation amplification |
| Portfolio with no tech/cloud concentration | ~0.85–0.95% | Minimal cross-terms; slight positive correlation with broad equity |
| Portfolio short cloud infrastructure | Potentially <0.80% | Negative cross-term could make EAIP a *hedge*, reducing total VaR |

This demonstrates a foundational principle: **position sizing is a portfolio-level decision, not a security-level decision.** The same security at the same weight can be risk-reducing in one portfolio and limit-breaching in another. Any sizing framework that ignores marginal contribution is structurally flawed.

---

## 4. Maximum Tolerable Size Given VaR Budget

### Budget Arithmetic

- Remaining VaR budget: 2.00% − 1.85% = **0.15%**
- Marginal VaR at 3% position size: 2.10%
- Marginal VaR per unit of position size (linear approximation): 2.10% / 3.0% = 0.70% per 1% of portfolio weight

### Maximum Size Calculation

Assuming approximate linearity of marginal VaR in position size near zero (reasonable for small positions):

$$\text{Max Size} = \frac{0.15\%}{0.70\% \text{ per 1\% weight}} \approx 0.21\%$$

| Size | Estimated Marginal VaR | Total Portfolio VaR | vs. Limit |
|---|---|---|---|
| 3.00% (proposed) | 2.10% | ~3.95% | **Breach — 197%** |
| 1.00% | ~0.70% | ~2.55% | Breach — 128% |
| 0.50% | ~0.35% | ~2.20% | Breach — 110% |
| **0.21%** | **~0.15%** | **~2.00%** | **At limit — maximum** |
| 0.15% | ~0.11% | ~1.96% | Within limit with buffer |

**Recommendation**: Maximum position size is ~0.20%, which provides negligible portfolio-level alpha contribution. At this size, the position is likely not worth the operational overhead and monitoring cost unless conviction is exceptionally high.

---

## 5. Trimming MCLD to Create VaR Budget for EAIP

### The Trade-Off Framework

Reducing MCLD accomplishes two things simultaneously:
1. Frees VaR budget directly (MCLD's own component VaR decreases)
2. Reduces the cross-term that amplifies EAIP's marginal VaR (lower MCLD weight → smaller covariance contribution)

This is a double benefit — the VaR budget opens faster than a linear trim would suggest.

### Should You Do It?

| Consideration | Assessment |
|---|---|
| **Alpha comparison** | Does EAIP offer higher risk-adjusted alpha than the MCLD position being trimmed? If EAIP's expected return per unit of marginal VaR exceeds MCLD's, the swap improves the portfolio's Sharpe ratio. |
| **Diversification** | Replacing some MCLD with EAIP at equal marginal VaR slightly diversifies the AI/cloud thesis across two names — modestly beneficial if idiosyncratic risks differ. |
| **Correlation stability** | The 0.65 correlation is a point estimate. If the true structural correlation is higher (plausible for AI platform + cloud infra), the benefit of the swap is smaller than modeled. |
| **Transaction costs** | Trimming MCLD and adding EAIP incurs frictional costs on both legs. |

**Illustrative swap**: Trim MCLD by 2% of portfolio weight → frees approximately 0.35–0.50% of VaR budget (component VaR reduction plus reduced cross-term) → allows EAIP sizing of ~0.50–0.70% while staying within the 2.0% limit.

**Net assessment**: The swap likely improves the portfolio modestly *if and only if* EAIP's expected alpha per unit of marginal risk is competitive with MCLD's. The PM should run the marginal Sharpe ratio comparison before executing. Simply swapping to "get the name in" without an alpha advantage is not justified.

---

## 6. Alternative Expressions With Lower Marginal VaR

### Option 1: Call Spread on EAIP
- Buy ATM call, sell 20% OTM call
- **Advantage**: Capped downside = premium paid. Marginal VaR contribution limited to premium at risk (~0.10–0.15% of portfolio if sized at 0.20% notional equivalent). Eliminates left-tail correlation amplification.
- **Disadvantage**: Time decay; capped upside; requires liquid options market on EAIP.

### Option 2: Pair Trade — Long EAIP / Short Partial MCLD
- Express the view that EAIP outperforms MCLD (relative value)
- **Advantage**: The short MCLD leg *offsets* the correlation cross-term. Marginal VaR could be near zero or even negative if sized correctly. Isolates the alpha differential between the two names.
- **Disadvantage**: Gives up MCLD upside; introduces short-specific risks; requires the thesis to be relative, not absolute.

### Option 3: Smaller Direct Position + Defined-Risk Overlay
- Take 0.15–0.20% direct equity position (within VaR budget)
- Add small OTM call position for convex upside exposure beyond the VaR-constrained size
- **Advantage**: Stays within VaR limit on the equity leg; options add asymmetric upside with bounded risk.

### Option 4: Express via a Less-Correlated AI Name
- If the thesis is "AI platforms will outperform," identify an AI company with lower correlation to MCLD (e.g., an AI-native company in a different vertical — healthcare AI, industrial AI)
- Lower ρ → marginal VaR converges toward standalone VaR → larger position possible within budget

| Alternative | Est. Marginal VaR | Max Feasible Size | Thesis Fidelity |
|---|---|---|---|
| Direct equity (proposed) | 2.10% at 3% | 0.20% | High |
| Call spread | ~0.10–0.15% | 0.15–0.20% notional | Medium (capped) |
| Long EAIP / Short MCLD pair | ~0.05–0.10% | 1.0–1.5% gross | Relative only |
| Lower-correlation AI name | ~0.50–0.80% at 1% | 0.20–0.30% | Lower |

---

## Decision Framework Summary

```
┌─────────────────────────────────────────────────┐
│  PROPOSED: 3% EAIP direct equity                │
│  Standalone VaR: 0.80% ← WRONG sizing input     │
│  Marginal VaR: 2.10% ← CORRECT sizing input     │
│  Portfolio VaR post-add: ~3.95% ← LIMIT BREACH  │
│  VERDICT: REJECT                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  ALTERNATIVES (ranked by preference):            │
│  1. Trim MCLD 2% + add EAIP 0.50-0.70%         │
│     (requires alpha comparison to justify)       │
│  2. Call spread at 0.15-0.20% notional equiv.   │
│  3. Direct equity at 0.15-0.20% max             │
│  4. Long/short pair if thesis is relative        │
└─────────────────────────────────────────────────┘
```

### Key Principles Reinforced

1. **Marginal VaR is the only valid sizing input for new positions.** Standalone VaR is a screening tool, not a portfolio construction tool.
2. **Correlation with existing holdings is the dominant risk driver** when the portfolio already has concentrated factor exposure.
3. **Position danger is portfolio-context-dependent.** The same position can be fine elsewhere and catastrophic here.
4. **VaR budgets are binding constraints**, not guidelines. At 92% utilization, every new position must be sized to the remaining 0.15% of marginal capacity.
5. **When the direct expression doesn't fit, restructure the expression** — options, pairs, or portfolio rebalancing can unlock the thesis within risk limits.

---

*This analysis uses point-in-time VaR estimates and correlation assumptions that may shift under stress conditions; tail correlations in risk-off environments frequently exceed steady-state estimates, meaning the 0.65 figure likely understates crisis-period co-movement. All sizing recommendations should be validated against current risk system output before execution.*