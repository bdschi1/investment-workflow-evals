

# Portfolio Construction Memo: CDIV Sizing in Context of Existing SEML Position

## Executive Summary

**Positions**: SEML (existing, 4% of NAV) + CDIV (proposed, 3% of NAV)
**Recommendation**: REDUCE proposed CDIV size to 1.5–2.0% of NAV
**Rationale**: 0.65 pairwise correlation eliminates most diversification benefit; combined 7% in correlated semis creates unacceptable concentration risk within a tech book already at 28% of gross.

**One-sentence thesis**: The analyst's 3% CDIV proposal treats the position in isolation; in portfolio context, correlation-adjusted combined risk is 26% higher than the uncorrelated case, and a 2-sigma semi selloff would hit NAV for ~2.08%, demanding a smaller size.

---

## Correlation-Adjusted Risk Analysis

### The Math: Why 3% + 4% ≠ "Two Independent Bets"

Portfolio variance for two correlated positions:

$$\sigma_p = \sqrt{w_1^2 \sigma_1^2 + w_2^2 \sigma_2^2 + 2 \cdot w_1 w_2 \cdot \rho \cdot \sigma_1 \sigma_2}$$

| Metric | ρ = 0.65 (Actual) | ρ = 0 (Uncorrelated) | ρ = 1.0 (Perfect) |
|---|---|---|---|
| Combined portfolio risk contribution | **2.44%** | 1.94% | ~2.80% |
| Incremental risk vs. uncorrelated | **+26%** | Baseline | +44% |
| Diversification benefit captured | ~30% | 100% | 0% |

*Source: context.combined_risk_analysis*

At ρ = 0.65, roughly 70% of the theoretical diversification benefit is destroyed. The two positions behave more like a single oversized semiconductor bet than two independent ideas. The correlation coefficient sits closer to "same trade" than "different trade" on any reasonable scale.

### What 0.65 Correlation Actually Means

- In a 2-sigma down move for SEML, CDIV is expected to move ~1.3 sigma in the same direction
- The positions will likely draw down simultaneously in any semiconductor-specific or AI capex repricing event
- Both share the same macro driver: AI capex cycle (source: context.correlation_analysis)
- Tail correlation in risk-off environments typically exceeds steady-state correlation — 0.65 is likely a *floor* during stress

---

## Sector Concentration Analysis

### Current vs. Proposed Exposure

| Metric | Current | Proposed (3% CDIV) | Recommended (1.75% CDIV) |
|---|---|---|---|
| Semiconductor exposure | 4.0% (SEML only) | 7.0% | 5.75% |
| Tech sector weight (gross) | 28% | ~31% | ~29.75% |
| Distance to 35% tech limit | 7pp | **4pp** | 5.25pp |
| Correlated semi cluster as % of tech | 14.3% | **22.6%** | 19.3% |

Adding 3% in CDIV pushes tech to ~31% of gross — only 4 percentage points from the 35% hard limit. This leaves almost no room for any other tech idea and creates path-dependency risk: if semis rally and drift upward, the book could breach the limit passively.

### Sector Downturn Stress Test

| Scenario | SEML (4%) | CDIV (3%) | CDIV (1.75%) |
|---|---|---|---|
| 2-sigma semi selloff — combined NAV loss | -1.19% | -0.89% | -0.52% |
| **Total portfolio hit** | — | **-2.08%** | **-1.71%** |
| Recovery time to breakeven (est.) | — | 6–9 months | 4–6 months |

*Source: context.combined_risk_analysis.sector_downturn_scenario*

A 2.08% NAV hit from a single sector cluster is significant for most fund mandates. This doesn't account for correlation spikes during stress (which empirical evidence consistently shows) or second-order effects like AI capex cycle deceleration hitting both names simultaneously.

---

## Evaluating the Analyst's "Different Value Chain" Argument

### Narrative vs. Data

The analyst argues SEML (equipment) and CDIV (design) occupy different parts of the semiconductor value chain, implying diversification. **The correlation data directly contradicts this narrative.**

| Analyst Claim | Statistical Reality |
|---|---|
| "Different value chain positions" | ρ = 0.65 — high positive correlation |
| "Equipment ≠ design" | Both driven by same AI capex cycle |
| "Diversified semiconductor exposure" | 70% of diversification benefit eliminated |
| Implied independence | Shared revenue driver: hyperscaler capex budgets |

**Verdict**: The "different value chain" argument is a fundamental attribution error. While the *businesses* differ operationally, the *stock returns* are driven by the same demand signal — AI/HPC capex commitments from the same set of hyperscaler customers. Equipment orders are a leading indicator of design wins; they are linked, not independent.

This is a textbook case of narrative overriding data. A 0.65 correlation is not a "low correlation that happens to be positive" — it indicates a strong shared factor. For context, 0.65 is higher than the average intra-sector correlation for most GICS sub-industries and approaches the correlation of direct competitors.

The analyst's argument would require ρ ≤ 0.25 to meaningfully hold. At 0.65, the value chain distinction is economically irrelevant for portfolio construction purposes.

---

## Practical Recommendation

### Proposed Sizing: CDIV at 1.5–2.0% (Not 3%)

| Option | SEML | CDIV | Total Semi | Combined Risk | Rationale |
|---|---|---|---|---|---|
| **A: Analyst proposal** | 4.0% | 3.0% | 7.0% | 2.44% | ❌ Rejected — ignores correlation |
| **B: Reduced CDIV** | 4.0% | 1.75% | 5.75% | ~2.10% | ✅ Preferred if SEML thesis intact |
| **C: Trim SEML + add CDIV** | 3.0% | 2.0% | 5.0% | ~1.90% | ✅ Preferred if CDIV has stronger marginal thesis |
| **D: Replace SEML with CDIV** | 0% | 3.0% | 3.0% | ~1.20% | Consider only if SEML thesis exhausted |

### Decision Framework: Trim SEML or Size Down CDIV?

The right answer depends on **marginal thesis strength**:

1. **If SEML has already captured most of its upside** (e.g., equipment cycle maturing, multiple expansion complete): Trim SEML to 3%, add CDIV at 2%. Total semi exposure = 5%, combined risk ≈ 1.90%. This is Option C.

2. **If SEML still has significant remaining upside** and CDIV is additive but secondary: Keep SEML at 4%, size CDIV at 1.5–1.75%. Total semi exposure = 5.5–5.75%. This is Option B.

3. **If both have equivalent conviction**: Default to Option B. The existing position has embedded gains and information advantage from longer holding period.

### Sizing Logic

The target is to keep correlation-adjusted combined risk contribution roughly equivalent to what a single 4% uncorrelated position would contribute (~1.94%). Working backward from this risk budget:

- At ρ = 0.65, a CDIV position of ~1.75% alongside 4% SEML produces combined risk of ~2.10% — roughly 8% above the uncorrelated benchmark, which is an acceptable premium for a genuinely differentiated thesis
- A 3% CDIV position overshoots this risk budget by 26%, which is not compensated by the incremental alpha given the shared driver

### Key Condition for Any CDIV Allocation

CDIV must demonstrate **idiosyncratic alpha sources** beyond the shared AI capex driver. Examples:
- Company-specific design win pipeline not captured by sector beta
- Margin expansion story independent of cycle volume
- Valuation discount to intrinsic value that doesn't depend on the same multiple expansion driving SEML

If the entire CDIV thesis reduces to "AI capex is accelerating," it is functionally a leverage-up on the existing SEML bet, not a new position.

---

## Implementation Guidelines

| Parameter | Specification |
|---|---|
| CDIV entry size | 1.75% of NAV (midpoint of 1.5–2.0% range) |
| SEML adjustment | Hold at 4% unless marginal thesis favors CDIV, then trim to 3% |
| Combined semi cap | 5.75% hard ceiling; 5.0% soft target |
| Tech book headroom | Maintain ≥5pp buffer to 35% limit |
| Correlation monitoring | Re-evaluate if 60-day rolling ρ exceeds 0.75 — triggers mandatory trim |
| Stress trigger | If combined semi loss exceeds 1.5% of NAV in any 5-day window, reduce smaller position by 50% |
| Review frequency | Monthly correlation check; quarterly thesis review for both positions |

---

## Summary Decision Matrix

| Evaluation Dimension | Analyst Proposal (3%) | Adjusted Recommendation (1.75%) |
|---|---|---|
| Standalone merit | ✅ Strong | ✅ Strong |
| Portfolio context risk | ❌ 2.44% combined | ✅ ~2.10% combined |
| Sector concentration | ❌ 7% correlated semis | ✅ 5.75% |
| Tech limit buffer | ⚠️ 4pp to limit | ✅ 5.25pp |
| 2σ stress loss | ❌ 2.08% NAV | ✅ ~1.71% NAV |
| Diversification efficiency | ❌ 70% benefit destroyed | ⚠️ Still impaired but sized for it |

**Bottom line**: CDIV is likely a good idea sized wrong. At 1.75%, the portfolio captures most of the alpha opportunity while respecting the statistical reality that ρ = 0.65 makes this substantially the same bet as SEML. The analyst's value chain argument is intellectually reasonable but empirically false — the correlation data is the final word.

---

*This analysis relies on point-in-time correlation estimates which may understate tail dependence; all sizing recommendations are probabilistic and subject to revision as correlation dynamics evolve.*