

# Portfolio Construction Memo: Earnings Cluster Aggregate Risk

## Executive Summary

**Subject**: Aggregate earnings-week risk across 5 concurrent reporting positions
**Recommendation**: TRIM weakest-conviction position (ADAT) + add index put protection to cap aggregate earnings exposure at ≤1.5% of NAV worst-case
**Core Problem**: 18% of NAV faces binary outcomes in a single week. Individual sizing (3-4% each) is correct, but correlated downside scenarios create portfolio-level risk that breaches the 2.0% weekly drawdown tolerance with ~25-30% probability in a bad quarter.

**One-sentence thesis**: Individually correct position sizes do not guarantee portfolio-level safety when binary outcomes share common macro drivers and correlation regimes shift from 0.30 to 0.70 during adverse earnings environments.

---

## The Composition Fallacy: Why Individual ≠ Aggregate

### Core Problem

Each position is sized at 3-4% with appropriate individual risk budgets. A PM reviewing any single name would approve the sizing. But the portfolio is not five independent bets — it is one concentrated exposure to "this week's earnings go well."

This is a textbook composition fallacy: properties true of parts are not necessarily true of the whole. Per Paleologo's framework on effective breadth (Source 2), a portfolio's true diversification depends on the covariance structure, not the count of positions. Five 3.6% positions with 0.70 pairwise correlation in the tail have far lower effective breadth than five independent 3.6% positions.

**The math is simple**: 5 × 3.6% avg = 18% of NAV exposed to binary outcomes in a single week. If the bad scenario hits all five, the portfolio absorbs the full 18% exposure's downside simultaneously.

### Why Individual Risk Budgets Miss This

| Dimension | Individual View | Aggregate View |
|---|---|---|
| Position size | 3-4% each ✓ | 18% total exposed |
| Expected gap on miss | -8% to -12% | -8% to -12% across all 5 |
| Single-position loss | 0.24-0.48% of NAV | — |
| Aggregate loss (all miss) | — | **1.4-2.2% of NAV** |
| Weekly tolerance | Easily within | **Breaches 2.0% ceiling** |
| Risk budget consumed | ~15-25% of weekly budget | **70-110% of weekly budget** |

The individual risk assessment is correct but incomplete. It answers "is this position sized right?" without asking "what happens when this position's outcome is correlated with four others reporting the same week?"

---

## Correlation Regime Change: The Hidden Amplifier

### Asymmetric Correlation Around Earnings

Earnings-period correlations are not symmetric. In normal quarters, pairwise correlation among these five names runs ~0.30 — manageable, and consistent with the individual sizing decisions. But in bad quarters, common macro factors (demand slowdowns, credit tightening, guidance cuts driven by shared end-market weakness) drive correlation to ~0.70.

This is not a theoretical concern. Goldman Sachs research on dispersion and correlation (Source 10) and the GS/JPM earnings season analyses (Sources 1, 3, 4) consistently document that miss rates cluster: when macro deteriorates, beats become rarer and misses become correlated. The Jefferies note (Source 13) reinforces that markets focus beyond individual results to macro backdrop, meaning a weak macro print can drag all reporters simultaneously.

### Probability Analysis: Independent vs. Correlated

| Scenario | Pairwise ρ | P(3+ misses out of 5) | P(all 5 miss) | Expected aggregate loss |
|---|---|---|---|---|
| Independent (normal quarter) | 0.30 | ~5% | <1% | Negligible in expectation |
| Correlated (bad quarter) | 0.70 | **25-30%** | ~8-12% | **1.4-2.2% of NAV** |
| Ratio (correlated/independent) | — | **5-6x higher** | **~10x higher** | — |

The 5x jump in the probability of 3+ simultaneous misses is the critical number. This is not a remote tail — a 25-30% probability event is roughly one-in-four earnings seasons. A PM who runs this cluster unhedged four times will likely breach the weekly tolerance at least once.

### What Drives the Correlation Spike

- **Common macro sensitivity**: All five names likely share exposure to consumer/enterprise spending cycles, rate sensitivity, or sector-level demand
- **Guidance contagion**: Early reporters missing and guiding down reprices expectations for later reporters in the same week
- **Risk-off positioning**: Institutional de-risking after early misses amplifies moves in remaining reporters
- **Volatility feedback**: Implied vol expansion after early misses increases realized gaps for later reporters

---

## Aggregate Loss Quantification

### Stress Scenarios

| Scenario | Positions affected | Avg gap down | NAV impact | vs. 2.0% tolerance |
|---|---|---|---|---|
| 2 of 5 miss, -8% avg | 2 × 3.6% | -8% | -0.58% | Within tolerance |
| 3 of 5 miss, -10% avg | 3 × 3.6% | -10% | -1.08% | Within tolerance |
| 4 of 5 miss, -10% avg | 4 × 3.6% | -10% | -1.44% | Approaching limit |
| 5 of 5 miss, -8% avg | 5 × 3.6% | -8% | -1.44% | Approaching limit |
| 5 of 5 miss, -10% avg | 5 × 3.6% | -10% | **-1.80%** | **90% of tolerance** |
| 5 of 5 miss, -12% avg | 5 × 3.6% | -12% | **-2.16%** | **Breaches tolerance** |

The expected loss in the correlated bad-quarter scenario (weighting by probability across outcomes) is approximately **1.0-1.5% of NAV** — not a breach in expectation, but with a fat right tail that reaches 2.2%. The problem is the conditional distribution: given we're in a bad quarter (which we may not know until the first reporter misses), the probability of breaching 2.0% is material (~10-15%).

---

## Mitigation Strategy Evaluation

### Option A: Trim Positions

**Candidate: ADAT (6/10 conviction, most uncertain outcome)**

| Action | Pre-trim | Post-trim | Impact |
|---|---|---|---|
| ADAT position | 3.6% | 1.5% (-2.1%) | Reduces cluster to ~15.9% |
| Aggregate exposure | 18% | ~15.9% | -12% reduction |
| Worst-case loss (all 5, -12%) | 2.16% | 1.91% | Still tight vs. tolerance |
| Worst-case loss (all 5, -10%) | 1.80% | 1.59% | Comfortable |

**Pros**: No cost, reduces exposure directly, ADAT is the rational trim candidate (lowest conviction, highest uncertainty)
**Cons**: Sacrifices upside if ADAT beats, may trigger tax events, re-entry after earnings creates transaction costs and potential slippage

**Enhanced trim**: Cut ADAT to 1.5% AND trim the second-weakest conviction by 1% → aggregate drops to ~14.9%, worst-case to ~1.79%. This keeps all positions active while materially reducing aggregate risk.

### Option B: Portfolio Hedges

**Sector puts or index protection**:

| Hedge instrument | Approximate cost | Protection provided | Efficiency |
|---|---|---|---|
| Sector ETF puts (1-week, 5% OTM) | 0.15-0.25% of NAV | Covers correlated sector move | Moderate — basis risk if names diverge from sector |
| Index puts (SPX, 1-week, 3% OTM) | 0.08-0.15% of NAV | Covers broad risk-off | Low — only helps if earnings misses coincide with market selloff |
| Single-name puts on weakest 2 names | 0.20-0.40% of NAV | Direct protection | High — but expensive due to elevated pre-earnings IV |

**Key concern**: Pre-earnings implied volatility is elevated, making single-name puts expensive. The EE data (Source 9) on average implied 1-day moves confirms that options markets price earnings binary risk aggressively. Buying puts at peak IV is often a negative-EV trade in isolation.

**Cost-benefit**: If sector puts cost ~0.20% and protect against ~1.0% of the tail loss, the breakeven requires the bad-quarter scenario to occur >20% of the time. Given the 25-30% correlated-miss probability, this is marginally positive EV but not compelling after accounting for basis risk.

### Option C: Recommended Hybrid Approach

| Action | Detail | Effect |
|---|---|---|
| **Trim ADAT to 1.5%** | Reduce lowest-conviction position by ~2.1% | Aggregate drops to ~15.9% |
| **Buy sector put spread** | 1-week, 3-5% OTM put spread on most relevant sector ETF | Caps correlated downside at ~0.10-0.15% cost |
| **Stagger if possible** | If any position reports Mon/Tue vs. Thu/Fri, evaluate early results before later reports | Allows dynamic response |
| **Set pre-commitment rule** | If first 2 reporters both miss, trim remaining 3 by 25% intraday | Limits cascade |

**Post-mitigation aggregate risk**:

| Metric | Pre-mitigation | Post-mitigation |
|---|---|---|
| Aggregate earnings exposure | 18.0% | ~15.9% |
| Worst-case (all 5, -12%) | 2.16% | ~1.79% + hedge offset ≈ **1.5-1.6%** |
| Worst-case (all 5, -10%) | 1.80% | ~1.49% + hedge offset ≈ **1.3%** |
| P(breach 2.0% tolerance) | ~10-15% | **<5%** |
| Cost | $0 | ~0.10-0.15% of NAV |

---

## Framework: Managing Aggregate Binary Risk

### Principles for Earnings Cluster Management

1. **Aggregate audit before every earnings season**: Sum all positions reporting in any single week. If >12-15% of NAV, flag for review regardless of individual sizing quality.

2. **Use stressed correlation, not normal correlation**: For earnings-week risk, assume ρ = 0.60-0.70, not the 0.30 observed in normal periods. This is the relevant parameter for the scenario that matters.

3. **Trim conviction-weighted, not equal-weighted**: When reducing aggregate exposure, cut from the bottom of the conviction stack. ADAT at 6/10 is the clear candidate — preserving high-conviction positions maintains portfolio quality.

4. **Hedges complement trims, they don't replace them**: Puts are expensive pre-earnings. Use them for residual risk after trimming, not as the primary tool.

5. **Pre-commit to intra-week escalation rules**: Define in advance what happens if early reporters miss. "If 2 of first 3 miss, trim remaining positions by X%" removes emotional decision-making during the stress event.

6. **Track effective earnings concentration as a portfolio metric**: Add "max single-week earnings exposure" to the risk dashboard alongside sector concentration, factor exposure, and single-name limits.

### What NOT to Do

- ❌ Maintain all positions because "each thesis is strong" — thesis quality is an individual metric; aggregate risk is a portfolio metric
- ❌ Use normal-period correlation for earnings-week stress testing
- ❌ Buy expensive single-name puts at peak pre-earnings IV without comparing to the trim alternative
- ❌ Assume earnings outcomes are independent when positions share macro drivers
- ❌ Ignore the weekly drawdown tolerance because "it's only one week"

---

## Decision Summary

| Decision | Action | Rationale |
|---|---|---|
| **ADAT** | Trim to 1.5% from ~3.6% | Lowest conviction (6/10), most uncertain, rational first cut |
| **Remaining 4 positions** | Hold at current size | Individual sizing correct, high conviction |
| **Sector hedge** | Buy 1-week put spread, ~0.10-0.15% cost | Caps correlated tail beyond what trimming achieves |
| **Intra-week rule** | If 2+ early reporters miss, trim remaining by 25% | Pre-committed escalation prevents emotional paralysis |
| **Post-earnings** | Re-evaluate ADAT for re-entry if results are clean | Don't permanently sacrifice position quality for temporary risk management |

**Net effect**: Aggregate earnings exposure drops from 18% to ~15.9%, worst-case NAV impact drops from 2.2% to ~1.5-1.6%, probability of breaching weekly tolerance drops from ~10-15% to <5%. Cost: ~0.10-0.15% of NAV in hedge premium plus forgone upside on ~2.1% of ADAT exposure.

This is the right trade-off: modest cost to eliminate a portfolio-level risk that individual position analysis cannot see.

---

*This analysis reflects probabilistic assessments based on historical correlation patterns and scenario modeling; actual outcomes may differ materially. Sources: context.earnings_cluster, context.correlation_analysis, context.aggregate_risk_analysis, context.stress_test, Paleologo (2025), GS/Jefferies earnings research.*