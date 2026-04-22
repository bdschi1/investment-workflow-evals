

# Portfolio Construction Memo: Displacement Trade Analysis

## Executive Summary

**Trade Type**: Displacement swap at gross leverage ceiling
**Entry**: CSPL (Cybersecurity) — 8/10 conviction, 3% position ($36M), 38% annualized vol
**Recommended Exit**: CRRC (Consumer Retail) — 5/10 conviction, $26.4M, weakening thesis + negative momentum
**Supplemental Trim**: LESW (Enterprise Software) — reduce by ~$9.6M to fund the size gap
**Net Effect**: +3% gross entry, −3% gross exit → gross remains ~192%, preserving 8% buffer
**Core Principle**: At 192% gross vs. 200% limit, position entry is not free — it is a displacement decision with explicit opportunity cost.

---

## 1. Displacement Framework: Entry Requires Exit

### The Constraint Arithmetic

| Metric | Current | Post-Entry (No Exit) | Post-Swap |
|---|---|---|---|
| Gross Exposure | 192% | 195% | ~192% |
| Remaining Capacity | 8% ($96M) | 5% ($60M) | ~8% ($96M) |
| Buffer to Ceiling | 8% | 5% | 8% |

Adding CSPL at 3% without exiting anything is technically feasible (195% < 200%). But this is the wrong framing. Running at 195% leaves only 5% buffer — one correlated move or a forced rebalance could breach the ceiling, triggering involuntary liquidation at the worst possible time. **Buffer is not idle capacity; it is optionality on future high-conviction ideas and a shock absorber against mark-to-market gross expansion.**

**The correct framing**: CSPL must be evaluated not in isolation but as a swap — CSPL *versus the weakest current holding*. The question is not "Is CSPL a good idea?" (it is, at 8/10). The question is "Is CSPL better than the marginal position it displaces, net of transition costs and risk profile changes?"

At leverage limits, every dollar of new exposure has an explicit opportunity cost: the dollar of existing exposure it replaces. This is not a soft constraint — it is a binding one that converts portfolio construction from an additive exercise into a zero-sum displacement game.

---

## 2. Exit Candidate Ranking: Forward Thesis, Not Backward Returns

### Candidate Comparison (Forward-Looking)

| Attribute | CRRC (Consumer Retail) | LESW (Enterprise Software) | INDV (Industrial Value) |
|---|---|---|---|
| Position Size | $26.4M (2.2%) | $33.6M (2.8%) | $42M (3.5%) |
| Conviction | 5/10 | 5/10 | 6/10 |
| Thesis Status | **Weakening** — consumer sentiment softening | **Mature** — upside largely captured | Intact but no near-term catalyst |
| Momentum | Negative | Neutral/fading | Flat |
| Annualized Vol | ~25% (est.) | ~22% | ~18% (est.) |
| Liquidity / Mkt Impact | 8–12 bps (worst) | 2–3 bps (best) | 4–6 bps (mid) |
| Portfolio Role | Growth/cyclical exposure | Low-vol stabilizer | Value/quality ballast |

### Ranking Logic

**#1 Exit Priority: CRRC** — Thesis is actively deteriorating, not just stale. Consumer sentiment softening is a forward-looking headwind, and negative momentum confirms the market is repricing this in real time. A 5/10 conviction with a weakening thesis is functionally a 4/10 on a forward basis. The risk of holding CRRC is asymmetric to the downside: if consumer weakness deepens, this position becomes a drag with no offsetting catalyst.

**#2 Exit Priority: LESW** — Thesis is mature, meaning the original investment case has largely played out. At 5/10 conviction, the remaining upside is marginal. However, LESW serves as a low-vol stabilizer (22% vol) and has the lowest market impact cost (2–3 bps). It is a better exit than INDV but a worse exit than CRRC because a mature thesis is less dangerous than a weakening one — LESW is unlikely to actively hurt you, it just won't help much.

**#3 Exit Priority: INDV** — Highest conviction of the three (6/10), thesis intact. Lack of near-term catalyst is a timing issue, not a thesis issue. Exiting INDV would sacrifice the most forward expected value. The larger size ($42M) might tempt a capacity-driven exit, but **exiting the largest position to maximize gross headroom is a capacity-over-thesis error**. We should exit the weakest thesis, not the biggest position.

**Critical**: YTD P&L of these positions is irrelevant to this decision. A position that is down 15% YTD but has a strengthening thesis is a better hold than one up 20% YTD with a deteriorating thesis. We rank on marginal forward return per unit of risk, not sunk performance.

---

## 3. Sizing the Swap: Partial vs. Full Exit

CSPL requires $36M. The exit candidates don't perfectly match:

| Exit Option | Proceeds | Gap to $36M | Approach |
|---|---|---|---|
| Full CRRC exit | $26.4M | −$9.6M short | Need supplemental trim |
| Full LESW exit | $33.6M | −$2.4M short | Near-match, small trim elsewhere |
| Full INDV exit | $42.0M | +$6.0M excess | Overshoot — wastes capacity on a 6/10 exit |
| Partial INDV exit ($36M of $42M) | $36.0M | Exact match | Exits 86% of a 6/10 position — poor thesis logic |

### Recommended Approach: Full CRRC Exit + Partial LESW Trim

- **Exit 100% of CRRC**: $26.4M freed. Removes the weakest forward thesis entirely.
- **Trim LESW by ~$9.6M** (from $33.6M to $24.0M): Funds the remaining gap. Reduces but doesn't eliminate the mature-thesis stabilizer.
- **Total freed**: $36.0M → funds full 3% CSPL position.
- **Net gross change**: ~0% (exits match entry) → gross stays at ~192%, preserving the full 8% buffer.

This is superior to a full exit of any single name because:
1. It removes the deteriorating thesis entirely (CRRC).
2. It right-sizes the mature thesis (LESW) rather than eliminating a portfolio stabilizer.
3. It preserves INDV (6/10, intact thesis) completely.
4. It maintains gross buffer at 8%.

---

## 4. Factor Tilt Impact

### Pre- and Post-Swap Factor Exposure Shifts

| Factor | Direction of Change | Magnitude | Commentary |
|---|---|---|---|
| **Tech/Growth** | ↑ Increase | Moderate | Adding cybersecurity (CSPL) while exiting consumer retail (CRRC) and trimming enterprise software (LESW) nets to higher tech weight |
| **Consumer Cyclical** | ↓ Decrease | Meaningful | Full CRRC exit removes consumer exposure entirely from this sleeve |
| **Momentum** | ↑ Improve | Moderate | Removing a negative-momentum name (CRRC) and adding a presumably positive-momentum entry (8/10 conviction, new idea) improves portfolio momentum tilt |
| **Value** | Neutral | Minimal | INDV (value industrial) is preserved; no value exposure lost |
| **Quality** | Slight ↓ | Minor | LESW trim reduces some quality/low-vol exposure |
| **Volatility Factor** | ↑ Increase | Notable | See Section 5 — this is the key risk tradeoff |

**Net assessment**: The portfolio tilts more growth/tech and more momentum-positive, at the cost of higher idiosyncratic volatility and reduced consumer diversification. The tech concentration risk is worth flagging — if the book already has significant tech/growth exposure, adding CSPL compounds sector concentration. PM should verify that post-swap tech weight doesn't breach any sector concentration limits.

---

## 5. Risk Profile Change: Volatility Swap

This is the most underappreciated dimension of the trade. The displacement isn't just a thesis upgrade — it's a volatility regime change within the affected sleeve.

### Vol Impact Analysis

| Metric | Exited Exposure (CRRC + LESW trim) | New Exposure (CSPL) |
|---|---|---|
| Weighted Avg Vol | ~23% (blended CRRC ~25%, LESW ~22%) | 38% |
| Vol Ratio | 1.0x (baseline) | ~1.65x |
| Dollar Vol (daily, approx) | ~$36M × 23% / √252 ≈ $522K | $36M × 38% / √252 ≈ $862K |

**The swap increases the daily dollar volatility contribution of this sleeve by ~65%.** At the portfolio level, the impact depends on correlation structure — if CSPL is lowly correlated with the rest of the book, the diversification benefit partially offsets the higher standalone vol. But cybersecurity names tend to correlate with broader tech/growth factors, so the diversification benefit is likely modest.

### Mitigation Options
1. **Size CSPL at 2% instead of 3%**: Reduces vol contribution proportionally but sacrifices conviction sizing on an 8/10 idea.
2. **Pair with a vol-reducing action elsewhere**: If LESW trim is the only supplemental action, the portfolio loses a low-vol stabilizer *and* adds a high-vol name — a double hit.
3. **Accept the vol increase as the price of thesis upgrade**: An 8/10 idea at 38% vol likely has a higher Sharpe than a 5/10 idea at 22% vol. The vol increase is the cost of upgrading expected return.

**Recommendation**: Accept the vol increase. The conviction differential (8/10 vs. 5/10) likely more than compensates for the 16pp vol increase. But the PM should verify that portfolio-level VaR and stress metrics remain within risk limits post-swap.

---

## 6. Market Impact Cost Analysis

| Exit | Size | Est. Impact | Dollar Cost | Days to Exit |
|---|---|---|---|---|
| CRRC (full) | $26.4M | 8–12 bps | $21K–$32K | 2–3 days |
| LESW (partial, $9.6M) | $9.6M | 2–3 bps | $2K–$3K | <1 day |
| **Total transition cost** | **$36.0M** | — | **$23K–$35K** | **2–3 days** |

For comparison, alternative approaches:

| Alternative | Size | Est. Impact | Dollar Cost |
|---|---|---|---|
| Full LESW exit | $33.6M | 2–3 bps | $7K–$10K |
| Full INDV exit | $42.0M | 4–6 bps | $17K–$25K |

The recommended approach (full CRRC + partial LESW) costs ~$23K–$35K in market impact — roughly 2–3x more than a full LESW exit alone. **This is the price of exiting the right position rather than the cheapest-to-exit position.** At $36M notional, $35K of market impact is <10 bps on the trade — immaterial relative to the thesis differential between an 8/10 entry and a 5/10 exit.

CRRC's higher market impact (8–12 bps) likely reflects lower liquidity or wider spreads in consumer retail names. The PM should use a 2–3 day execution window with algorithmic participation to minimize footprint. If CRRC is in a name with options liquidity, consider delta-hedging with puts during the unwind to lock in exit economics.

---

## 7. Decision Matrix Summary

| Criterion | Full CRRC + Trim LESW (Rec.) | Full LESW Exit | Full INDV Exit |
|---|---|---|---|
| Thesis quality of exit | ✅ Best (weakest thesis removed) | ⚠️ Acceptable (mature thesis) | ❌ Worst (intact 6/10 thesis) |
| Gross buffer preserved | ✅ 8% maintained | ⚠️ ~7.8% (slight gap) | ✅ Excess freed |
| Market impact cost | ⚠️ Highest ($23–35K) | ✅ Lowest ($7–10K) | ⚠️ Mid ($17–25K) |
| Factor tilt improvement | ✅ Removes negative momentum | ⚠️ Loses low-vol stabilizer | ❌ Loses value diversifier |
| Vol impact | ⚠️ Loses some stabilizer | ❌ Loses primary stabilizer | ✅ Minimal vol change |
| Sizing match | ✅ Exact ($26.4M + $9.6M) | ⚠️ Close ($33.6M, small gap) | ❌ Overshoot ($42M) |

---

## Final Recommendation

Execute the displacement trade: **full exit of CRRC ($26.4M) + trim LESW by $9.6M → fund 3% CSPL position ($36M)**. This upgrades portfolio conviction from blended 5/10 to 8/10 on the displaced capital, removes a deteriorating thesis with negative momentum, preserves gross buffer at 8%, and maintains the value diversifier (INDV) and a reduced but still present low-vol stabilizer (LESW at $24M).

The portfolio accepts higher volatility (~65% increase in sleeve-level daily dollar vol) as the explicit cost of a materially higher-conviction position. This is a favorable tradeoff if CSPL's risk-adjusted return profile justifies 8/10 conviction.

**Pre-trade checklist**:
- [ ] Confirm post-swap sector concentration (tech) within limits
- [ ] Run portfolio-level VaR with CSPL at 38% vol replacing CRRC/LESW trim
- [ ] Verify CRRC can be exited over 2–3 days without exceeding 12 bps impact
- [ ] Set CSPL stop-loss and review triggers given higher vol profile
- [ ] Document the displacement rationale for risk committee

---

*This analysis reflects a point-in-time assessment based on stated portfolio constraints and conviction scores. Actual outcomes depend on market conditions, correlation dynamics, and thesis evolution. All forward-looking estimates are probabilistic, not deterministic.*