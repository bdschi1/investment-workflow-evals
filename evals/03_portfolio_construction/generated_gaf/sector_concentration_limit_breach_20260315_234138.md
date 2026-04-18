

# Portfolio Construction Memo: Healthcare Sector Concentration Breach

## Executive Summary

**Decision**: Trim existing healthcare positions to fund POXT at reduced size. Do not request a limit exception. Do not pass on the idea.

**One-sentence thesis**: The 30% sector concentration limit is a binding risk constraint — not a guideline — and the correct response to a 9/10 conviction idea arriving into a breached book is to force-rank existing positions, trim the weakest forward-looking theses, and size the new idea to bring total healthcare exposure back to or below the limit.

**Recommendation**:
1. Exit HDAL entirely (5/10 conviction — weakest forward thesis)
2. Trim MTIN from 4.2% to ~2% (next-weakest marginal expected return)
3. Add POXT at 3.0–3.5% (below the analyst's requested 4%, reflecting constraint discipline)
4. Evaluate increasing OVBT short to partially offset incremental long beta
5. Target post-trade healthcare gross exposure of 29–30%

---

## Why Sector Concentration Limits Bind — Especially Now

### Correlated Drawdown Risk Is Non-Linear

Sector limits exist because positions within a sector share correlated risk factors: regulatory action, reimbursement changes, clinical trial sentiment shifts, rate sensitivity (biotech duration), and sector fund flows. The key insight is that **drawdown risk from correlated positions scales non-linearly with concentration**.

| Healthcare Gross Exposure | Illustrative Sector Drawdown (-15%) | Portfolio Impact |
|---|---|---|
| 20% (within limit) | -3.0% | Manageable |
| 30% (at limit) | -4.5% | Painful but recoverable |
| 34% (current) | -5.1% + correlation amplification | Threatens risk budget |
| 38% (proposed) | -5.7% + significant tail risk | Could force liquidation |

The relationship isn't purely multiplicative — at higher concentrations, a sector selloff is more likely to trigger fund-level stop-losses, margin calls, or LP redemption pressure, creating a reflexive feedback loop. A 38% healthcare book means a single FDA policy shift, a CMS reimbursement rule change, or a sector-wide de-risking event (e.g., IRA drug pricing expansion, NIH funding cuts under new administration — see SA_HEALTH_DEC2024-FEB2025.pdf noting RFK confirmation risks and policy uncertainty) could consume the majority of the portfolio's risk budget in a single session.

### The Time to Enforce Limits Is When Everything Is Working

The analyst's argument — "every position is working, the limit is a guideline" — is precisely the behavioral state that concentration limits are designed to override. Limits exist as pre-commitment devices because:

- **In drawdowns**, you'll wish you had enforced them
- **In rallies**, you'll always find reasons not to (endowment effect, momentum bias, winner paralysis)
- **The fact that every position is working is itself a risk signal** — it likely means the sector is experiencing correlated upside, which implies the same factor exposure will produce correlated downside

The sector rally that pushed healthcare from ~30% to 34% without any new trades is **passive drift** — the portfolio's risk profile changed without a deliberate decision. This is the definition of unmanaged risk.

---

## Marginal Thesis Ranking of Existing Healthcare Book

The correct framework for identifying trim candidates is **forward-looking marginal expected return per unit of risk**, not backward-looking P&L. Selling a winner that has appreciated into fair value is not "leaving money on the table" — it's recognizing that the position's risk/reward has deteriorated.

### Position Ranking Framework

| Position | Current Size | Conviction | Forward Thesis Strength | Trim Action |
|---|---|---|---|---|
| POXT (new) | 0% → 3.0–3.5% | 9/10 | Highest in 18 months | **Add** |
| [Top holdings] | Various | 8–9/10 | Strong catalysts ahead | **Hold** |
| MTIN | 4.2% | 6/10 | Moderate; thesis partially realized | **Trim to ~2%** |
| OVBT (short) | -2.5% | 7/10 | Hedge value increasing | **Consider increasing** |
| HDAL | 3.8% | 5/10 | Weakest forward case | **Exit entirely** |

### Why HDAL Gets Cut First

HDAL at 5/10 conviction represents the lowest marginal expected return in the healthcare book. The question isn't whether HDAL will go up — it's whether HDAL's next-dollar risk-adjusted return exceeds POXT's. At 5/10 vs. 9/10, the answer is unambiguous. Exiting HDAL frees 3.8% of gross exposure.

### Why MTIN Gets Trimmed Second

At 6/10 conviction and 4.2% sizing, MTIN is over-allocated relative to its forward thesis strength. Trimming to ~2% frees an additional ~2.2% and right-sizes the position to its conviction level. This is good portfolio hygiene independent of the POXT opportunity.

### What We Are NOT Doing

- **Not trimming the best performer** — backward-looking P&L is irrelevant to forward expected return
- **Not trimming pro-rata across all positions** — that penalizes high-conviction ideas equally with low-conviction ones
- **Not keeping HDAL because "it's working"** — the endowment effect is the single most destructive behavioral bias in portfolio management

---

## The Behavioral Trap: Endowment Effect and Winner Paralysis

The analyst's resistance to selling winners to fund a new idea reflects two well-documented biases:

1. **Endowment effect**: Overvaluing positions we already own relative to positions we could own. The portfolio doesn't care about your cost basis or how long you've held HDAL.

2. **Winner paralysis**: The reluctance to disturb a "working" portfolio. But a portfolio where every position is profitable is not necessarily an optimally constructed portfolio — it's one where the PM hasn't stress-tested whether each position still earns its allocation on a forward basis.

**The correct mental model**: Every morning, you are re-underwriting every position at current prices. Would you initiate a new 3.8% position in HDAL at 5/10 conviction today? Almost certainly not. The fact that it's already in the book is irrelevant.

---

## Implementation Plan

### Trade Sequence

| Step | Action | Gross HC Impact | Running HC Exposure |
|---|---|---|---|
| Starting point | — | — | 34.0% |
| 1 | Exit HDAL (3.8%) | -3.8% | 30.2% |
| 2 | Trim MTIN from 4.2% to 2.0% | -2.2% | 28.0% |
| 3 | Add POXT at 3.0% | +3.0% | 31.0% |
| 4 | Increase OVBT short by 1.0% | +1.0% gross, but hedges long beta | 32.0% gross / improved net |
| **Post-trade** | | | **~30% net long HC** |

### Sizing POXT Below the Requested 4%

Despite 9/10 conviction, POXT should be sized at 3.0–3.5% rather than 4% for three reasons:

1. **Constraint environment**: We are operating at the limit boundary. Sizing at 3% rather than 4% provides a 1% buffer against further passive drift.
2. **Biotech-specific vol**: Biotech positions carry higher idiosyncratic volatility than diversified healthcare names (clinical binary events, regulatory risk — see GS ABCs of Biotechnology noting "significant volatility around clinical, regulatory, and commercial events"). A 3% biotech position may carry risk-equivalent exposure to a 4–5% diversified pharma position.
3. **Optionality**: Starting at 3% preserves the ability to add on confirmation of thesis milestones. It's easier to scale into a working position than to cut a position that's moved against you from an oversized starting point.

### The OVBT Short as a Risk Offset

Increasing the OVBT short by ~1% serves two purposes:
- Partially hedges the incremental long healthcare beta from POXT
- Improves the portfolio's net-to-gross ratio within healthcare, reducing directional sector exposure even if gross exposure remains near 30%

This is not a substitute for trimming — gross limits exist for a reason — but it improves the risk profile of the remaining concentration.

---

## Does the Sector Rally Change the Risk Profile?

**Yes, materially.** The rally that passively pushed healthcare from ~30% to 34% has three risk implications:

1. **Appreciated positions carry more dollar risk**: A position that was 3% at cost and is now 4% after appreciation has 33% more dollar exposure to the same risk factors. The portfolio's sensitivity to a healthcare drawdown has increased without any deliberate action.

2. **Valuation compression of the margin of safety**: If healthcare names have rallied on sector-wide flows (XBI +6% in a single week per SA_HEALTH_DEC2024-FEB2025.pdf), the forward return distribution for existing positions has likely shifted left. Positions that were cheap are now less cheap.

3. **Crowding risk increases**: Sector rallies attract momentum capital, increasing the risk of a sharp reversal when flows reverse. The biotech sector's sensitivity to rate expectations (see GS ABCs noting "macroeconomic uncertainty" and "interest rate environment" as headwinds) means a single hawkish Fed signal could trigger rapid de-grossing.

**Bottom line**: The rally is a reason to be *more* disciplined about the concentration limit, not less.

---

## Decision Framework Summary

| Option | Assessment | Verdict |
|---|---|---|
| **Add without trimming** (analyst's proposal) | Pushes HC to 38%, 8% over limit. Treats limit as optional. Maximizes correlated drawdown risk. | **Rejected** |
| **Pass on POXT** | Preserves limit compliance but sacrifices best idea in 18 months. Opportunity cost is real. | **Rejected** — trimming is the better path |
| **Request limit exception** | Only appropriate *after* exhausting the trim path. We haven't — HDAL at 5/10 is an obvious trim. Exception requests should be reserved for books where every position is genuinely high-conviction. | **Rejected as first option** |
| **Trim and add** | Exits weakest thesis (HDAL), right-sizes MTIN, funds POXT at constraint-appropriate size, maintains limit discipline. | **Recommended** |

### When Would an Exception Request Be Appropriate?

Only if: (a) every existing position were 8/10+ conviction with near-term catalysts, (b) the new idea were truly once-in-a-cycle, (c) the exception were time-bounded (e.g., 60 days), and (d) the PM could articulate a specific plan to return below the limit. Even then, the exception should come with an offsetting short or reduced net exposure. None of these conditions are met here — HDAL at 5/10 is a clear trim candidate.

---

## Key Principles Reinforced

1. **Limits are pre-commitment devices.** They bind hardest when you least want them to — which is exactly when they're most valuable.
2. **Forward conviction, not backward P&L, determines trim priority.** The weakest forward thesis gets cut first, regardless of how much money it's made.
3. **Concentration risk is convex.** Going from 30% to 38% in a single sector doesn't increase risk by 27% — it likely increases tail risk by substantially more due to correlation amplification and reflexive liquidation dynamics.
4. **Size new ideas to the constraint, not to conviction alone.** A 9/10 idea in an unconstrained book might warrant 4–5%. In a constrained book, 3% is the right answer.
5. **Rallies increase risk.** Passive drift from appreciation is unmanaged risk. The sector rally is a reason for more discipline, not less.

---

*This memo reflects a portfolio construction framework based on the scenario as described. Actual implementation would depend on liquidity conditions, tax considerations, and real-time market dynamics not captured here.*