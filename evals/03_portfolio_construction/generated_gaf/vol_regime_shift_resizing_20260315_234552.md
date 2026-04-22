

# Vol Regime Shift Resizing: Implementation Framework

## Executive Summary

**Scenario**: VIX spike 15→32; portfolio vol at 18% (1.8x target); mechanical framework prescribes 44% gross reduction ($648M liquidation)
**Recommendation**: **Staged partial reduction with hedging overlay — NOT mechanical full execution**
**Day 1 Action**: Cut ~50% of prescribed amount ($324M) in most liquid names + buy 2-week index put spread for residual exposure
**Rationale**: Term structure backwardation (32/25/21) tilts toward transient spike, but 50/50 base rates preclude certainty. Full mechanical execution destroys $3.2-6.5M in market impact for a risk event that may self-correct within 30 days.

**One-sentence thesis**: The vol-targeting framework is directionally correct but the implementation prescription is a blunt instrument — in a liquidity-impaired market with ambiguous regime signals, a staged approach captures ~70% of the risk reduction at ~35% of the market impact cost.

---

## Framework vs. Mechanical Execution

### Why the Framework Is Right — and Wrong

The vol-targeting framework correctly identifies the problem: portfolio vol at 18% is 1.8x the 10% target, representing uncompensated risk. But the framework is a **risk measurement tool, not a trading algorithm**. It assumes infinite liquidity and zero transaction costs.

### Cost of Cutting vs. Cost of Not Cutting

| Scenario | Cost | Probability-Weighted Cost |
|---|---|---|
| **Full mechanical cut** — $648M liquidation | $3.2-6.5M market impact (midpoint $4.85M) | $4.85M (certain) |
| **No cut, vol normalizes in 30 days** | Temporary elevated vol, ~0 realized loss if positions recover | ~$0 × 50% = $0 |
| **No cut, regime shift persists** | Portfolio at 18% vol for extended period; potential 2-3σ drawdown = $12-24M | $18M × 50% = $9M |
| **Staged 50% cut + hedges** | ~$1.7M impact + ~$1.2M put premium = $2.9M | $2.9M (certain) + residual tail ≈ $4-5M expected |

The expected cost of doing nothing (~$9M probability-weighted) exceeds the cost of full mechanical execution (~$4.85M), which confirms the framework's directional signal. But the staged approach dominates both: ~$4-5M total expected cost with better tail protection than inaction and lower certain cost than full execution.

### The Nuanced Response

**Reject the binary.** Neither "execute the full 44% cut immediately" nor "override the framework and wait" is optimal. The correct answer is a **conditional, staged reduction** calibrated to:
1. Liquidity conditions (spreads 3-5x, depth down 40-60%)
2. Regime probability (ambiguous — see below)
3. Marginal cost of each incremental dollar of risk reduction

---

## Regime Classification

### What the Term Structure Tells Us

| VIX Tenor | Level | Signal |
|---|---|---|
| Spot VIX | 32 | Elevated — 2σ+ event |
| 1-month futures | 25 | Market expects mean reversion |
| 3-month futures | 21 | Near pre-shock levels |
| **Term structure shape** | **Steep backwardation** | **Historically associated with transient spikes** |

Steep backwardation (32/25/21) means the options market is pricing a ~30% vol decline over the next month. This is a meaningful signal — when VIX futures are in steep backwardation, the spike resolves within 30 days roughly 60-65% of the time historically. But this is **not certainty**.

### What the Term Structure Doesn't Tell Us

- Backwardation was also present at the start of several genuine regime shifts (Aug 2015, Feb 2018 initial spike) before the curve flattened as the shock persisted
- The 50/50 historical base rate for VIX spikes to 30+ (transient vs. regime shift) is the unconditional prior; backwardation shifts this modestly toward transient (~60/40) but not decisively
- The geopolitical nature of the shock adds uncertainty — geopolitical vol spikes have fatter tails than earnings/data-driven spikes

### Assessment

**Probability of transient spike (normalizes <30 days): ~55-60%**
**Probability of regime shift (persists >30 days): ~40-45%**

We do not know which this is. The implementation plan must be robust to both outcomes.

---

## Implementation Plan: Staged Reduction with Triggers

### Day 1 Actions (Immediate — First 2 Hours of Trading)

**Target: Reduce gross from 185% to ~145% (cut ~$320M, roughly half the prescription)**

| Priority | Action | Size | Rationale |
|---|---|---|---|
| 1 | Sell most liquid long positions (mega-cap, top-of-book >$50M daily) | ~$200M | Minimal market impact; these names have deepest books even in stress |
| 2 | Cover most profitable short positions | ~$80M | Shorts are working in a selloff — take profit, reduce gross |
| 3 | Buy 2-week SPX put spread (e.g., 95/90% strikes) | ~$40M notional | Provides tail protection on remaining exposure while vol is elevated |
| **Total Day 1 impact cost estimate** | | | **~$1.5-2.0M** (vs. $3.2-6.5M for full execution) |

**Why this sequencing:**
- Most liquid names first: bid/ask impact is 1-2x normal vs. 5-10x for small/mid-cap
- Covering profitable shorts reduces gross without selling longs into weakness
- Put spread (not outright puts) manages the cost of buying protection at VIX 32 — the spread offsets some of the elevated premium

### Days 2-5: Monitor and Conditionally Execute

**Watch these signals daily:**

| Signal | Transient Indicator | Regime Shift Indicator |
|---|---|---|
| VIX level | Declining toward 25 | Holding above 28 or rising |
| Term structure | Backwardation steepening or normalizing | Flattening or inverting to contango |
| Realized vol (5-day) | Declining from peak | Matching or exceeding implied |
| Credit spreads (HY OAS) | Stable or tightening | Widening >50bps from pre-shock |
| Correlation regime | Single-stock dispersion returning | Correlation spike (>0.7 avg pairwise) |
| Geopolitical catalyst | De-escalation signals | Escalation or contagion |

### Trigger Points for Follow-On Cuts

| Trigger | Action | Target Gross |
|---|---|---|
| **VIX holds >28 for 3 consecutive sessions** | Cut additional $160M (next liquidity tier) | ~125% |
| **VIX rises above 35** | Immediate additional $160M cut + roll put spreads | ~105% (near mechanical target) |
| **Term structure flattens** (1M futures converge to spot) | Cut additional $160M regardless of VIX level | ~125% |
| **Realized vol exceeds 25% annualized** over 5 days | Full mechanical target — execute remaining cuts | 104% |
| **VIX declines below 24** | Halt further cuts; begin re-risking most liquid positions | Hold at ~145% |
| **VIX declines below 20** | Restore gross toward 165-170% over 5-7 sessions | 165-170% |

---

## Hedging Alternatives: Puts vs. Selling

### Cost Comparison

| Approach | Cost | Risk Reduction | Pros | Cons |
|---|---|---|---|---|
| Sell $648M positions | $3.2-6.5M impact | Full — gross to 104% | Permanent risk reduction | Irreversible; may sell at lows; massive impact |
| Buy ATM 2-week SPX puts ($648M notional) | ~$4.5-5.5M premium (VIX at 32) | Tail only — no gross reduction | Reversible; no position disruption | Expensive at current vol; theta decay; doesn't reduce gross |
| **Buy 2-week put spread (95/90%)** | **~$1.0-1.5M premium** | **Moderate tail protection** | **Cost-effective; reversible** | **Capped protection; gap risk below 90%** |
| Sell $324M + put spread on remainder | ~$1.7M impact + $1.2M premium = **$2.9M** | Substantial | Balanced cost/protection | More complex to manage |

**Key insight**: Outright puts at VIX 32 are prohibitively expensive for full-notional hedging. Put *spreads* are the right instrument — they sacrifice protection below the lower strike but cost 60-70% less. The combination of partial selling + put spread on residual exposure is the dominant strategy.

**Critical**: Hedging alone without any position reduction is insufficient. Puts expire, theta bleeds, and if this is a regime shift, you'll be rolling expensive hedges indefinitely. Position reduction must be the primary tool; hedges are supplementary.

---

## Position Sequencing: What to Cut and When

### Liquidity Tiering

| Tier | Characteristics | Day 1 Action | Days 2-5 Action |
|---|---|---|---|
| **Tier 1** (most liquid) | Mega-cap, >$1B ADV, spreads <2x normal | Sell/cover ~$200M | Additional $100M if triggers hit |
| **Tier 2** | Large-cap, $200M-$1B ADV, spreads 2-3x normal | Sell ~$80M (profitable shorts) | $80-100M if triggers hit |
| **Tier 3** | Mid-cap, $50-200M ADV, spreads 3-5x normal | Hold — too expensive to trade Day 1 | Sell only if regime shift confirmed |
| **Tier 4** (least liquid) | Small-cap, <$50M ADV, spreads >5x normal | Do not touch | Consider only in extreme scenario; use hedges instead |

### Additional Sequencing Principles

- **Cut positions with highest beta first** — they contribute most to portfolio vol per dollar
- **Cut positions with weakest conviction first** — use the forced selling as a portfolio quality upgrade
- **Preserve positions with near-term catalysts** — selling a name 2 weeks before a catalyst that could gap 15% is value-destructive
- **Reduce correlated clusters** — if you hold 5 names in the same sector moving in lockstep, cutting 2-3 reduces vol more efficiently than cutting across uncorrelated positions

---

## Decision Tree Summary

```
VIX spikes to 32
│
├─ Day 1: Cut 50% of prescription (~$320M) in Tier 1/2 names
│         Buy 2-week put spread on residual exposure
│         Total cost: ~$2.9M
│
├─ Days 2-5: Monitor VIX, term structure, realized vol, credit
│   │
│   ├─ VIX < 24 → STOP cutting, begin measured re-risk
│   │
│   ├─ VIX 24-28, backwardation intact → HOLD current positioning
│   │                                      Let puts roll off
│   │
│   ├─ VIX > 28 for 3 sessions OR term structure flattens
│   │   → Cut additional $160M (Tier 2/3)
│   │     Roll put spreads
│   │
│   └─ VIX > 35 OR realized vol > 25%
│       → Execute to full mechanical target (104% gross)
│         Accept market impact as justified
│
└─ Day 10+: Reassess framework parameters
            Consider whether 10% vol target is appropriate
            for current macro regime
```

---

## Key Quantitative Summary

| Metric | Mechanical Approach | Recommended Staged Approach |
|---|---|---|
| Day 1 gross reduction | 185% → 104% | 185% → 145% |
| Day 1 liquidation | $648M | $320M |
| Day 1 market impact | $3.2-6.5M | $1.5-2.0M |
| Hedging cost | $0 | $1.0-1.5M (put spread) |
| Total Day 1 cost | $3.2-6.5M | $2.5-3.5M |
| Portfolio vol (post Day 1) | ~10% (target) | ~13-14% (above target but manageable) |
| Exposure to further drawdown | Minimal | Moderate, but hedged below 95% SPX |
| Cost if spike is transient | $3.2-6.5M (wasted) + re-entry costs | $2.5-3.5M (partially wasted) |
| Protection if regime shift | Full | ~70% of full, with triggers for completion |

---

## What Could Go Wrong

| Risk | Probability | Mitigation |
|---|---|---|
| Spike worsens to VIX 45+ before Day 2 cuts | ~10-15% | Put spread provides protection; triggers accelerate cuts |
| Spike reverses overnight, we sold at the lows | ~20-25% | Only sold 50% of prescription; preserved higher-conviction positions |
| Liquidity deteriorates further, Tier 2/3 become untradeable | ~15-20% | Hedge with index instruments instead of single-name selling |
| Framework parameters were wrong (10% target too tight) | Ongoing | Post-event review of vol target appropriateness |

---

## Conclusion

The vol-targeting framework is a valuable risk management tool, not a trading instruction. In this scenario, it correctly identifies that portfolio risk is nearly 2x target and action is required. But executing the full $648M liquidation into a panicked, illiquid market is the financial equivalent of running for the exit in a crowded theater — you'll get out, but you'll pay dearly and may trample your own positions.

The staged approach — 50% cut Day 1 in liquid names, put spread overlay, trigger-based follow-on — captures the majority of the risk reduction benefit at roughly half the implementation cost, while preserving optionality for both outcomes (transient spike or regime shift). It respects the framework's signal without being enslaved by its prescription.

---

*This analysis reflects probabilistic assessments based on historical patterns and current market signals; actual outcomes may differ materially. Vol regime classification is inherently uncertain and all trigger levels should be treated as guidelines subject to real-time judgment.*