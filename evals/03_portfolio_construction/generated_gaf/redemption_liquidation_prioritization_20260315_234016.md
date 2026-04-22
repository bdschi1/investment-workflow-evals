

# Redemption Liquidation Memo: $72M / T+5 Settlement

## Executive Summary

**Situation**: $72M redemption (12% of AUM ~$600M) across 70 positions, T+5 hard deadline.
**Recommendation**: Hybrid liquidation — overweight liquid names (~65% of proceeds), tactical trims on medium-liquidity (~30%), minimal illiquid selling (~5%), with full exits on low-conviction positions and tax-loss harvesting.
**Estimated all-in cost**: ~$200-300K market impact vs. $800K-1.5M for naive pro-rata.

**One-sentence thesis**: A conviction-weighted hybrid approach raises $72M within 5 days at ~15-25 bps of total cost while preserving portfolio quality and minimizing follow-on redemption risk.

---

## The Three Approaches and Why Each Fails Alone

### 1. Pro-Rata: Theoretically Clean, Practically Expensive

Pro-rata preserves portfolio weights — every position shrinks by 12%. Elegant on paper. Disastrous in execution.

| Tier | AUM | 12% Sell | Est. ADV Coverage | Market Impact |
|------|-----|----------|-------------------|---------------|
| Highly Liquid (15 names) | $320M | $38.4M | <5% ADV | 5-10 bps |
| Medium Liquidity (20 names) | $280M | $33.6M | 10-20% ADV | 15-30 bps |
| Low Liquidity (15 names) | $105M | $12.6M | 25-50% ADV | 40-100 bps |

**SpecialtyPharma alone** at 35% of ADV would require 3+ days to exit just 12% of the position, consuming 40-80 bps in market impact. Multiply this across 15 illiquid names and pro-rata costs $800K-1.5M in market impact — 4-7x the cost of a hybrid approach. Pro-rata also risks failing the T+5 deadline: several illiquid names simply cannot be liquidated at 12% within 5 business days without catastrophic price impact.

**Verdict**: Pro-rata is "fair" to the redeeming investor but punishes remaining LPs through excessive transaction costs charged to the fund.

### 2. Liquidity-Priority: Cheap but Portfolio-Destroying

Selling only the 15 most liquid names ($320M tier) easily raises $72M at ~$100-150K market impact. But the math on what's left is ugly:

| Metric | Pre-Redemption | Post Liquidity-Only Sale |
|--------|---------------|------------------------|
| Total AUM | $600M | $528M |
| Liquid tier weight | 53% | 47% → but $248M / $528M = 47% |
| Illiquid tier weight | 17.5% | $105M / $528M = **20%** |
| Liquid-to-illiquid ratio | 3.0x | 2.4x |

The remaining portfolio tilts meaningfully toward illiquidity. Worse, the liquid names sold are likely the fund's highest-quality, most recognizable holdings. When remaining investors review the next portfolio report, they see a book that is harder to exit, more concentrated in illiquid names, and stripped of its most defensible positions. This is a **follow-on redemption accelerant**.

**Verdict**: Cheapest execution, highest probability of triggering a redemption cascade.

### 3. Risk-Priority: Intellectually Appealing, Operationally Dangerous

Cutting highest-risk positions first sounds like portfolio improvement. But high-risk positions often correlate with low liquidity. You end up force-selling illiquid names at wide spreads under time pressure — the worst possible combination. Risk-priority also ignores that some "high-risk" positions may be the fund's highest-conviction alpha generators.

**Verdict**: Conflates risk reduction with liquidity management; likely fails T+5 for the same reasons pro-rata does.

---

## Tax Implications by Approach

| Approach | Tax Efficiency | Key Consideration |
|----------|---------------|-------------------|
| Pro-rata | Poor | Forces realization of gains and losses indiscriminately; likely triggers STCG on recent winners |
| Liquidity-priority | Mixed | Liquid names often include large-cap winners with embedded gains; high STCG exposure |
| Risk-priority | Variable | May harvest losses on impaired positions but also realizes gains on volatile winners |
| **Hybrid (recommended)** | **Best** | **Deliberately harvests CyclicalMaterials $2.1M loss; defers gains on positions approaching LTCG threshold** |

**CyclicalMaterials**: $2.1M unrealized loss is a clear full-exit candidate. Harvesting this loss offsets ~$2.1M of gains realized elsewhere in the liquidation, saving the fund ~$500-700K in taxes (assuming ~25-35% blended rate for remaining investors). This is a gift — take it.

**Near-LTCG positions**: Any position within 30-60 days of crossing the 1-year holding period should be preserved if possible. The STCG-to-LTCG rate differential (~15-20 percentage points) on a meaningful gain can dwarf market impact savings.

---

## Signaling Risk and Follow-On Redemptions

This is the second-order risk that kills funds. The $72M redemption is 12% of AUM. If the post-liquidation portfolio looks impaired, remaining investors may submit follow-on redemptions at the next window. A second 10-12% redemption on a now-smaller, less-liquid book creates a vicious cycle.

**What remaining investors will scrutinize:**
- Has the liquidity profile deteriorated? (If illiquid weight rises from 17.5% to >22%, alarm bells ring)
- Were high-conviction positions gutted? (If top 10 positions were disproportionately trimmed, it signals the PM lost flexibility)
- Does the portfolio still look like the strategy they subscribed to? (Style drift from forced selling = redemption trigger)
- Are there new concentration risks? (If liquid names were sold and illiquid names untouched, single-name risk rises)

**Target**: Post-liquidation portfolio should maintain illiquid weight ≤19%, liquid-to-illiquid ratio ≥2.7x, and preserve the top 5 highest-conviction positions at ≥85% of current weight.

---

## Recommended Liquidation Plan

### Allocation Framework

| Source | $ Amount | % of $72M | Rationale |
|--------|----------|-----------|-----------|
| Highly liquid tier | $46M | 64% | Low impact (~8 bps avg), deep books, T+1-2 execution |
| Medium liquidity tier | $22M | 31% | Moderate impact (~20 bps avg), selective trimming, T+2-4 |
| Low liquidity tier | $4M | 5% | Only full exits of low-conviction names + tax harvests |

**Estimated total market impact: ~$200-300K** (vs. $800K-1.5M pro-rata)

### Specific Position Actions

#### Full Exits (complete liquidation)
| Position | Tier | Rationale | Est. Proceeds | Timeline |
|----------|------|-----------|---------------|----------|
| CyclicalMaterials | Medium/Low | $2.1M tax loss harvest; low conviction | ~$8-12M | T+1 to T+3 |
| [Low-conviction illiquid #1] | Low | Below thesis; free up illiquid capacity | ~$2-3M | T+1 to T+4 |
| [Redundant liquid position] | Liquid | Overlapping exposure with higher-conviction name | ~$5-8M | T+1 |

Full exits are preferable to partial trims when: (a) conviction is low, (b) tax loss is available, (c) position is too small to matter post-trim, or (d) the position creates redundant factor exposure.

#### Partial Trims — Liquid Tier (~$35-40M)
- Trim 15-20% across 8-10 largest liquid positions
- Execute via VWAP/TWAP algorithms over T+1 to T+2
- Participation rate: <8% of ADV — negligible market impact
- Prioritize trimming positions with embedded STCG over those near LTCG threshold

#### Partial Trims — Medium Liquidity Tier (~$12-15M)
- Trim 8-12% across 5-7 medium-liquidity names
- Execute via VWAP over T+1 to T+4, participation rate 10-15% of ADV
- Avoid names where trim would push position below minimum effective size
- Sequence: start with names that have highest ADV within the tier

#### Do Not Touch
- **SpecialtyPharma**: At 35% of ADV, even a 5% trim would take 2+ days and cost 40-80 bps. The position is ~$7M in the portfolio; selling $840K (12% pro-rata) would cost $35-65K in impact alone — a 4-8% round-trip cost. Leave it.
- Other illiquid names with high conviction and/or approaching LTCG status
- Any position where the bid-ask spread exceeds 50 bps

### Execution Timeline

| Day | Action | Cumulative Cash Raised | Risk Check |
|-----|--------|----------------------|------------|
| T+1 | Full exits of liquid low-conviction names; begin VWAP on liquid trims | ~$25M | Verify fills, check market conditions |
| T+2 | Complete liquid tier trims; begin medium-liquidity trims; CyclicalMaterials exit starts | ~$48M | If market adverse, accelerate liquid sales |
| T+3 | Continue medium-liquidity trims; complete CyclicalMaterials | ~$62M | Assess if on track; activate contingency if <$55M |
| T+4 | Complete remaining medium-liquidity trims; low-conviction illiquid exit | ~$70M | Final gap assessment |
| T+5 | Mop-up: any residual shortfall from liquid tier buffer | $72M | Settlement |

### Contingency Plan
If market dislocation occurs (e.g., broad selloff widening spreads), the liquid tier has ~$274M remaining after planned sales — ample buffer to accelerate liquid selling by an additional $5-10M at still-minimal impact. This is the insurance policy that makes the hybrid approach robust.

If a specific medium-liquidity name fails to execute (e.g., trading halt, volume collapse), redirect that allocation to liquid tier trims. Never chase illiquid names under time pressure.

---

## Post-Liquidation Portfolio Quality Check

| Metric | Pre-Redemption | Post-Liquidation (Hybrid) | Post-Liquidation (Pro-Rata) | Post-Liquidation (Liquidity-Only) |
|--------|---------------|--------------------------|----------------------------|----------------------------------|
| Total AUM | $600M | $528M | $528M | $528M |
| Liquid tier weight | 53.3% | 51.9% ($274M) | 53.3% ($281M) | 46.9% ($248M) |
| Medium tier weight | 29.2% | 28.8% ($152M) | 29.2% ($154M) | 33.0% ($174M) |
| Illiquid tier weight | 17.5% | 19.3% ($102M) | 17.5% ($92M) | 20.1% ($106M) |
| Liquid/Illiquid ratio | 3.05x | 2.69x | 3.05x | 2.34x |
| Market impact cost | — | ~$250K | ~$1.1M | ~$125K |
| Tax efficiency | — | Best (harvest $2.1M loss) | Poor | Mixed |
| Top 5 position integrity | 100% | ~90% | 88% | ~75% |

The hybrid approach keeps illiquid weight at 19.3% — modestly above pre-redemption but well below the ~20%+ threshold that would alarm sophisticated LPs. The liquid/illiquid ratio of 2.69x remains healthy. Critically, the portfolio still looks like the same strategy.

---

## Key Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Market selloff during liquidation widens spreads | Medium | Moderate — adds $50-150K cost | Liquid tier buffer; front-load execution |
| Follow-on redemption at next window | Medium | Major — could trigger liquidity spiral | Preserve portfolio quality; proactive LP communication |
| CyclicalMaterials loss reverses before exit | Low | Minor — lose tax benefit | Execute Day 1-2; loss is $2.1M, unlikely to reverse fully |
| Trading halt on key position | Low | Moderate — delays cash raise | Redirect to liquid tier; 15 liquid names provide diversification |
| Adverse selection — market reads our selling | Low-Medium | Moderate — other sellers pile on | Use algorithmic execution; spread across names and days |

---

## LP Communication Framework

Proactive communication to remaining investors should occur within 48 hours of the redemption:

1. **Acknowledge** the redemption without dramatizing it (12% is manageable, not existential)
2. **Emphasize** the fund maintained its investment strategy and liquidity profile
3. **Highlight** the tax-efficient execution (loss harvesting benefiting remaining LPs)
4. **Provide** updated liquidity metrics showing the portfolio can handle another 10-15% redemption without distress
5. **Reaffirm** conviction in remaining positions — the best names were preserved

---

## Summary Decision Framework

The optimal liquidation plan is not the cheapest (liquidity-only), not the "fairest" (pro-rata), and not the most intellectually satisfying (risk-priority). It is the one that **raises $72M within T+5 at minimal cost while leaving a portfolio that doesn't trigger the next redemption**.

The hybrid approach achieves this by: (1) drawing ~64% from liquid names where impact is negligible, (2) tactically trimming medium-liquidity names for ~31%, (3) using the remaining ~5% to fully exit low-conviction and tax-loss positions, and (4) explicitly protecting illiquid high-conviction names like SpecialtyPharma where forced selling destroys value.

Total estimated savings vs. pro-rata: **$500K-1.2M in market impact + ~$500-700K in tax efficiency = $1.0-1.9M of value preserved for remaining LPs.**

---

*This analysis is based on estimated market impact costs and assumes normal market conditions during the liquidation window. Actual execution costs may vary materially if market conditions deteriorate or if additional redemptions are received during the settlement period.*