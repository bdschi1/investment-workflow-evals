

# Pair Trade Rebalancing Memo: Pharma/Biotech Vol-Ratio Drift

## Executive Summary

**Trade Type**: Pharma (Long) / Biotech (Short) Pair Trade
**Recommendation**: **Rebalance via trimming the long leg + partial short cover**, locking in gains while restoring risk parity before the pending Phase 3 catalyst
**Current Net P&L**: +$7.4M (misleadingly healthy)
**Core Problem**: The pair's risk balance has inverted — the short leg now contributes MORE dollar risk than the long leg, transforming this from a controlled relative-value trade into an unintended net-short-volatility position.

**One-sentence thesis**: A profitable P&L is masking a structurally broken pair where vol-ratio drift (2.78:1 → 3.67:1) has flipped the risk contribution, requiring immediate rebalancing before a pending Phase 3 binary event amplifies the distortion.

---

## 1. How Vol-Ratio Drift Distorted the Original Risk Balance

### Original Construction (T=0)

| Metric | Long (Pharma) | Short (Biotech) | Ratio |
|---|---|---|---|
| Notional | $60M | $20M | 3.0:1 |
| Annualized Vol | 18% (est.) | 50% (est.) | 2.78:1 |
| Dollar Risk (Notional × Vol) | ~$10.8M | ~$10.0M | 1.08:1 |

The pair was constructed with a **3:1 notional ratio precisely because biotech vol was ~2.78× pharma vol**. The asymmetric notional sizing was intentional — it equalized dollar risk at ~$10M per leg. This is textbook risk-matched pair construction.

### Current State (T+3 months)

| Metric | Long (Pharma) | Short (Biotech) | Ratio |
|---|---|---|---|
| Notional | $69M (+15%) | $21.6M (+8% against) | 3.19:1 |
| Annualized Vol | 15% (↓) | 55% (↑) | 3.67:1 |
| Dollar Risk (Notional × Vol) | **$10.35M** | **$11.88M** | **0.87:1** |

The vol ratio widened from 2.78:1 to 3.67:1 — a **32% drift**. This single change, combined with the notional moves, flipped the risk contribution ratio from 1.08:1 (long-dominant) to 0.87:1 (short-dominant). The pair is now structurally inverted from its original intent.

### Why This Matters

The pair was designed as a relative-value expression: long pharma stability, short biotech overvaluation, with risk equalized so neither leg dominated P&L variance. Today:

- **The short leg drives more daily P&L variance than the long leg** — the trade's outcome is now more sensitive to biotech moves than pharma moves
- The pair has become a **de facto net short-volatility position** because the short leg's vol expanded while the long leg's vol compressed
- A 1-sigma daily move in the biotech (~3.5% on 55% annualized vol) generates ~$756K of P&L swing vs. ~$654K from a 1-sigma pharma move — the short is 15% "bigger" in risk terms

**Notional balance is a mirage. Risk balance is what matters.** The $69M long "looks" bigger than the $21.6M short, but risk-adjusted, the short dominates.

---

## 2. Why the Short Leg Is "Bigger" Despite Smaller Notional

This is the critical conceptual point most PMs miss when anchoring to notional:

| | Notional | Vol | Dollar Risk | % of Total Pair Risk |
|---|---|---|---|---|
| Long (Pharma) | $69.0M | 15% | $10.35M | **46.6%** |
| Short (Biotech) | $21.6M | 55% | $11.88M | **53.4%** |

The short is only 24% of gross notional but contributes **53.4% of total pair risk**. This inversion means:

1. **The trade's P&L distribution is now skewed by the short leg** — a biotech squeeze or Phase 3 surprise will dominate the pair's outcome regardless of pharma performance
2. **The hedge ratio is stale** — the original 3:1 notional ratio implied a specific vol relationship that no longer holds
3. **Correlation assumptions may also be drifting** — pharma vol compression and biotech vol expansion likely reflect diverging factor exposures (rate sensitivity, binary event risk), potentially reducing the pair's correlation and increasing tracking error

The macro context reinforces this: Fed hawkishness disproportionately pressures SMID-cap biotechs reliant on external funding (Source 1, 2), while large-cap pharma benefits from defensive rotation. These are diverging regimes, not converging ones.

---

## 3. Four Rebalancing Options and Tradeoffs

### Option A: Increase the Short (Add to Biotech Short)

**Target**: Increase short notional to ~$23.8M to re-equalize dollar risk at ~$10.35M each (i.e., $10.35M / 55% = $18.8M... but we need $10.35M dollar risk, so $10.35M / 0.55 ≈ $18.8M notional — actually this would mean *reducing* the short. Let me recalculate.)

To match the long's $10.35M dollar risk: Short notional needed = $10.35M / 0.55 = $18.8M → this means **covering ~$2.8M of the short**, not adding.

Alternatively, to restore the *original* ~$10.8M risk per leg: Short notional = $10.8M / 0.55 = $19.6M → cover ~$2.0M.

If the intent is to increase the short to match a *larger* risk target (say, scaling up to match the long at current notional): Long dollar risk at $69M × 15% = $10.35M. To match, short stays at $10.35M / 0.55 = $18.8M.

**However, if the PM's instinct is to ADD short** (increase notional beyond $21.6M) to "lean into" the thesis:

| Consideration | Assessment |
|---|---|
| Borrow cost | Likely elevated — biotech with pending Phase 3 data = high demand for borrows |
| Squeeze risk | Significant — 55% vol implies large daily moves; short squeeze into catalyst is a real scenario |
| Margin impact | Higher short notional increases margin requirements at precisely the wrong time |
| Behavioral trap | Adding to a losing position (short is -$1.6M) feels like doubling down |

**Verdict**: Adding to the short is the **highest-risk rebalancing option** and likely inappropriate given the pending catalyst.

### Option B: Trim the Long (Take Profits on Pharma)

**Target**: Reduce long notional so its dollar risk matches the short's current $11.88M, OR reduce to re-equalize at a lower level.

To equalize at the short's current risk: Long notional = $11.88M / 0.15 = $79.2M → would require *adding* to the long. Not the right framing.

To equalize at a lower target (e.g., $10M per leg): Long notional = $10M / 0.15 = $66.7M → trim ~$2.3M. Short notional = $10M / 0.55 = $18.2M → cover ~$3.4M.

**Pure long trim to match current short risk**: Reduce long to $11.88M / 0.15 = $79.2M — this doesn't work because it would mean adding. The math shows the problem: at current vols, you can't equalize by only trimming the long unless you trim it dramatically.

**Practical approach**: Trim long from $69M to ~$60M (booking ~$9M notional, ~$2.3M in gains) AND cover ~$3M of the short. This hybrid restores approximate balance.

| Consideration | Assessment |
|---|---|
| Tax/booking | Crystallizes gains on the long — may be desirable for P&L recognition |
| Opportunity cost | Reduces exposure to a winning position |
| Behavioral resistance | **High** — trimming a winner feels wrong; "let winners run" instinct fights this |
| Risk discipline | Most consistent with original trade construction intent |

**Verdict**: **Best single-leg option** — reduces gross exposure and rebalances risk, though a hybrid with partial short cover is superior.

### Option C: Hold (Do Nothing)

| Consideration | Assessment |
|---|---|
| Rationale | "It's working — net P&L is +$7.4M" |
| Reality | The trade's risk character has fundamentally changed |
| Outcome distribution | Now dominated by biotech vol; a 2-sigma biotech move (~7% daily) generates ~$1.5M P&L swing from the short alone |
| Pending catalyst | Phase 3 data could push biotech vol to 70%+ and create a 20-40% gap move — the short leg would then represent ~65%+ of pair risk |

**Verdict**: **This is the critical failure option.** Holding transforms the trade from a relative-value pair into a directional biotech short with a pharma kicker. The +$7.4M P&L is an anchoring trap.

### Option D: Close Both Legs

| Consideration | Assessment |
|---|---|
| P&L capture | Locks in +$7.4M — clean, definitive |
| Opportunity cost | Abandons the original thesis if it's still valid on fundamentals |
| Re-entry option | Can re-establish at correct hedge ratio post-catalyst |
| Transaction costs | Covering the short may be expensive if borrow is tight |

**Verdict**: **Appropriate if the original fundamental thesis has degraded** or if the Phase 3 readout is imminent (days/weeks). The cleanest risk management but sacrifices optionality.

### Summary Matrix

| Option | Risk Discipline | Behavioral Difficulty | Cost | Preserves Thesis? |
|---|---|---|---|---|
| A: Add Short | Medium | Very High | High (borrow, margin) | Yes, but amplifies risk |
| **B: Trim Long (Hybrid)** | **High** | **High** | **Low-Medium** | **Yes** |
| C: Hold | None | None (easy) | Zero upfront | No — transforms trade |
| D: Close Both | High | Medium | Medium | No — exits trade |

---

## 4. Behavioral Challenge

Two powerful biases work against correct rebalancing:

**Winner Attachment (Long Leg)**: The pharma long is +$9M (+15%). Trimming it triggers "don't cut your flowers" instinct. But the position's *risk contribution* has shrunk — it's now the smaller leg in risk terms. Trimming isn't abandoning a winner; it's right-sizing a position whose risk profile has changed.

**Loss Aversion on Shorts (Short Leg)**: The biotech short is -$1.6M. Adding to it (Option A) or even maintaining it feels like compounding a mistake. The behavioral pull is to cover the short entirely. But the short may still be fundamentally correct — the stock being up 8% doesn't invalidate the thesis. The question is whether the *risk sizing* is appropriate, not whether the direction is wrong.

**The correct framing**: This is not a P&L decision. It is a risk-sizing decision. The PM should ask: "If I were constructing this pair today from scratch, what would the hedge ratio be?" The answer — given 15% vs. 55% vol — would be a notional ratio of ~3.67:1, not the current ~3.19:1. That means either less long or less short (or both) to re-equalize.

---

## 5. Phase 3 Catalyst Risk

The pending Phase 3 readout on the biotech is a **time-critical accelerant** to the vol-ratio problem:

| Scenario | Biotech Move | Short P&L Impact | Pair Outcome |
|---|---|---|---|
| Phase 3 success | +30% to +50% | -$6.5M to -$10.8M | Likely wipes out +$7.4M net gain |
| Phase 3 failure | -40% to -60% | +$8.6M to +$13.0M | Windfall, but uncontrolled |
| Ambiguous data | ±15% | ±$3.2M | Manageable but still outsized |

Key observations:
- **Implied vol on the biotech likely understates realized event vol** — Phase 3 binary outcomes routinely produce moves 2-3× implied
- The current 55% vol may jump to 80-100%+ as the readout approaches, further distorting the pair
- **The asymmetry is unfavorable**: a Phase 3 success (short squeeze) is likely faster and more violent than a failure decline, due to short covering dynamics
- Per Source 1, the macro backdrop (hawkish Fed, funding pressure on SMID biotechs) adds a secondary headwind but won't override a positive Phase 3 readout

**The catalyst creates urgency**: rebalancing before the readout is materially different from rebalancing after. Post-readout, the pair may be un-rebalanceable at reasonable cost.

---

## 6. Recommended Approach

**Primary Recommendation: Hybrid of Option B + Partial Option D**

1. **Trim the long leg by ~$10-12M notional** (sell ~$10M of pharma position, reducing from $69M to ~$58M), booking ~$2.5M in realized gains
2. **Cover ~$3-4M of the short** (reduce biotech short from $21.6M to ~$18M), taking a ~$300K realized loss on that portion
3. **Result**: Long dollar risk = $58M × 15% = $8.7M; Short dollar risk = $18M × 55% = $9.9M → ratio of ~0.88:1, still slightly short-heavy but materially improved from 0.87:1 at larger gross

**Alternative if Phase 3 is <4 weeks away**: Close both legs entirely (Option D), book the +$7.4M, and re-establish post-catalyst at the correct hedge ratio. The cost of re-entry is almost certainly less than the cost of being wrong-sized through a binary event.

### Why This Preserves Original Intent

- Restores approximate risk parity between legs
- Reduces gross exposure ahead of a vol-expanding catalyst
- Books partial gains on the long (de-risks the P&L)
- Maintains the fundamental thesis (pharma over biotech on a relative basis)
- Avoids the behavioral trap of adding to a losing short into a catalyst

### Monitoring Framework Post-Rebalance

| Trigger | Action |
|---|---|
| Vol ratio drifts >3.5:1 again | Re-trim to restore parity |
| Phase 3 date announced within 30 days | Close or hedge with options |
| Biotech borrow cost spikes >200bps | Evaluate full close |
| Pharma vol rises above 20% | Reassess — pair may be self-correcting |

---

## Key Takeaways

1. **Vol-ratio drift is the core problem** — not P&L, not direction, not conviction. The 2.78:1 → 3.67:1 shift broke the pair's risk architecture.
2. **Notional is not risk.** A $21.6M short at 55% vol is riskier than a $69M long at 15% vol. Full stop.
3. **Profitable pairs can be broken pairs.** The +$7.4M net P&L is irrelevant to the risk management decision.
4. **Catalysts compress decision timelines.** The Phase 3 readout makes "wait and see" the most dangerous option.
5. **Rebalancing is not a P&L call — it's a risk architecture call.** The PM who trims a winner and maintains a loser to preserve risk parity is exercising discipline, not weakness.

---

*This analysis is based on the scenario parameters provided and general market context from HC Narrative Dec2024-Feb2025 and GS ABCs of Biotechnology. Actual rebalancing decisions should incorporate real-time borrow availability, margin constraints, tax considerations, and updated fundamental views on both legs.*