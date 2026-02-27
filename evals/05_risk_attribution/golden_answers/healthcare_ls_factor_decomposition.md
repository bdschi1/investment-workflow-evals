# Golden Answer: Apex Healthcare Partners - Factor Decomposition and Alpha Assessment

## Executive Summary

**Fund:** Apex Healthcare Partners (Healthcare L/S)
**Period:** Full Year 2024
**Fund Return:** +18.2%
**Benchmark (XLV):** +12.4%
**Claimed Outperformance:** ~600bps over XLV
**Estimated Residual Alpha (post factor decomposition):** Approximately -1% to +2.5%, centered near +1%
**Statistical Significance:** Not distinguishable from zero -- t-stat likely well below 2.0
**Assessment:** The majority of the fund's return is attributable to systematic factor exposures (market beta, momentum, size). The PM's narrative substantially overstates the contribution of idiosyncratic stock selection. True residual alpha appears modest and is not statistically distinguishable from zero given the available data. The claim of "market-neutral" is inconsistent with 52% net exposure.

---

## Factor Decomposition

### Step 1: Market Beta Contribution

The fund carries an average beta of 0.48 to the S&P 500 with 52% average net exposure.

- Market risk premium (MKT-RF) in 2024: +16.9%
- Market beta contribution: 0.48 x 16.9% = **+8.1%**
- Risk-free rate: +5.2%
- CAPM expected return: 8.1% + 5.2% = **+13.3%**

This single factor alone explains approximately 13.3 percentage points of the 18.2% total return. The fund's 52% net long exposure creates meaningful directional market exposure, directly contradicting the PM's characterization of the strategy as "market-neutral."

### Step 2: Multi-Factor Return Attribution

Using the fund's reported factor betas and 2024 factor returns:

| Factor | Fund Beta | Factor Return (2024) | Contribution |
|--------|-----------|---------------------|-------------|
| MKT-RF | 0.48 | +16.9% | +8.1% |
| SMB (Size) | 0.18 | +8.3% | +1.5% |
| HML (Value) | -0.12 | -2.1% | +0.3% |
| UMD (Momentum) | 0.22 | +14.1% | +3.1% |
| QMJ (Quality) | 0.15 | +6.2% | +0.9% |
| **Total Factor Contribution** | | | **+13.9%** |

Adding the risk-free rate: 13.9% + 5.2% = **+19.1% expected return from factors alone.**

### Step 3: Residual Alpha Calculation

- Fund return: +18.2%
- Factor-expected return: +19.1%
- **Point estimate of residual alpha: -0.9%**

The arithmetic decomposition suggests the fund slightly *underperformed* what its factor exposures would have predicted. However, this point estimate has substantial uncertainty due to:

- Factor beta estimation error (betas are estimated over a finite window and may not be precisely accurate)
- Interaction effects between factors
- Timing of exposure changes within the year (annual betas are averages)
- Potential omitted factors specific to healthcare (e.g., GLP-1 exposure, biotech vs pharma subsector)

A reasonable confidence range for the residual alpha is **approximately -1% to +2.5%**, reflecting the estimation uncertainty. The key takeaway is not the exact point estimate, but that it is centered near zero -- far from the PM's claimed ~600bps.

### Step 4: Decomposing the Benchmark-Relative Outperformance

The PM frames outperformance relative to XLV (+12.4%). This framing obscures the factor story:

| Component | Contribution | % of Apparent 5.8% Excess |
|-----------|-------------|--------------------------|
| Momentum exposure (0.22 x 14.1%) | +3.1% | ~53% |
| Size tilt (0.18 x 8.3%) | +1.5% | ~26% |
| Quality tilt (0.15 x 6.2%) | +0.9% | ~16% |
| Anti-value benefit (-0.12 x -2.1%) | +0.3% | ~5% |
| **Factor-driven total** | **~5.8%** | **~100%** |
| **Residual stock selection** | **~0% to +1%** | ~0-17% |

Systematic factor exposures explain approximately all of the benchmark-relative outperformance. Within healthcare, the fund's 45% biotech allocation on the long side provided a natural tailwind -- biotech (XBI +16.8%) outperformed large-cap pharma in 2024, and this subsector tilt is captured by the momentum and size factors.

---

## Hypothesis Testing: Skill vs Luck

### Statistical Significance of Residual Alpha

The residual alpha estimate of approximately -1% to +2.5% needs to be tested for statistical significance.

**Information Ratio Analysis:**
- Reported IR: 0.95 (relative to XLV benchmark)
- However, this IR conflates factor returns with alpha -- it measures *total* excess return, not factor-adjusted excess
- After factor adjustment, the residual IR is likely 0.1-0.3
- For a single year: t-stat = IR x sqrt(T) ≈ 0.2 x sqrt(1) = 0.2
- A t-stat of 0.2 is far below the 2.0 threshold for conventional significance (p > 0.40)

**Minimum Track Record Length:**
Per Bailey and Lopez de Prado's Deflated Sharpe Ratio framework, a Sharpe ratio of 1.42 (which includes factor returns) would require approximately 5-7 years to be statistically distinguishable from zero at the 5% level, accounting for non-normality and potential multiple testing. A factor-adjusted Sharpe of approximately 0.1-0.3 would require 40+ years to reach statistical significance.

**Conclusion:** A single year of data is wholly insufficient to distinguish skill from luck. Even with the PM's full 10-year track record, it would be difficult to make a statistically rigorous alpha claim if the factor-adjusted alpha is as small as this decomposition suggests. We should not conclude the PM lacks skill -- but we also cannot conclude they have it.

### Pattern Analysis

Available data points suggest factor-driven returns:
- **2024:** Fund +18.2% in a strong momentum and small-cap year -- outperformed XLV
- **2023:** Fund +8.1% vs SPY +26.3% -- significant underperformance in a growth/mega-cap dominated year

This pattern is consistent with a fund whose returns are driven by momentum, size, and anti-mega-cap factor exposures rather than idiosyncratic stock selection. A longer time series would be needed to test this pattern more rigorously.

---

## Intentionality Assessment

### Stated Strategy vs Actual Exposures

| PM Claim | Reality | Assessment |
|----------|---------|-----------|
| "Market-neutral" | 52% net long, 0.48 beta to SPY | **Misleading** -- this is a directional long-biased fund |
| "Bottom-up stock selection" | Significant MKT, UMD, SMB betas | **Partially misleading** -- factor tilts drive most returns |
| "Clinical trial expertise" | Long book 45% biotech | **Plausible** -- consistent with biotech overweight |
| "Short book alpha" | Shorts rose 6.4% in sector up 12.4% | **Supportive** -- some evidence of short-side value-add |

The PM's marketing narrative emphasizes alpha and stock selection. The quantitative evidence points to a fund primarily harvesting systematic factor premia (market, momentum, size) with a healthcare sector overlay. This does not prove the PM lacks skill entirely, but the primary return driver appears to be factor exposure, not idiosyncratic alpha.

### Short Book Evaluation

The short book merits separate analysis. In a year where the healthcare sector (XLV) returned +12.4%, the short book lost only 6.4%. This implies approximately 6 percentage points of positive contribution from short selection relative to a naive short-healthcare position.

However, caveats apply:
- The short book was 40% pharma and 30% services -- subsector allocation within healthcare may explain some of the short-side outperformance rather than stock-level selection
- Large-cap pharma (the short book's largest tilt) may have underperformed biotech within healthcare, providing a structural tailwind
- A single year of short-side data cannot confirm persistent skill

The short book is the most encouraging aspect of the fund's performance. Further decomposition across multiple years would be needed to assess whether this is skill or a favorable subsector positioning that happened to work in 2024.

---

## Contextual Evaluation

### Market Environment

The 2024 environment was mixed for this fund's profile:

| Factor | Effect on Fund | Assessment |
|--------|---------------|-----------|
| Momentum +14.1% | Strong tailwind (0.22 UMD beta) | Favorable |
| Small-cap +8.3% | Moderate tailwind (0.18 SMB beta) | Favorable |
| Quality +6.2% | Modest tailwind (0.15 QMJ beta) | Slightly favorable |
| Healthcare vs SPY: -9.7% | Headwind for healthcare specialist | Unfavorable |
| Biotech (XBI +16.8%) vs broad healthcare | Tailwind for biotech-heavy long book | Favorable |

On balance, the factor environment was favorable for this fund's factor profile, but the sector headwind (healthcare underperforming SPY by ~10%) was real. A fair assessment notes that the PM navigated the healthcare-specific environment adequately, but absolute returns were substantially boosted by non-healthcare systematic factors.

### Fee-Adjusted Returns

| Component | Value |
|-----------|-------|
| Gross return | +18.2% |
| Management fee | -1.5% |
| Performance fee (est. 20% above hurdle) | -2.5% to -3.0% |
| **Net return to investor** | **~13% to 14%** |

A simple long-only healthcare ETF (XLV) returned +12.4% at approximately 10bps in fees. The fee-adjusted spread between the fund and a passive healthcare allocation is approximately 100-150bps -- a thin margin that may not justify the fee structure, complexity, and illiquidity of a hedge fund allocation.

### Comparison to Factor Replication

A hypothetical factor-tilted healthcare portfolio (long biotech-overweight, momentum-screened, small-cap-tilted healthcare names) could likely have been constructed at 30-50bps in fees and may have delivered 14-17% returns given the factor environment. This approach would have captured most of the fund's non-alpha returns at a fraction of the cost.

---

## Key Risks in the Attribution

1. **Factor beta estimation error:** Betas estimated from limited history may not be stable; true factor contributions could differ by 1-2 percentage points
2. **Omitted factors:** Industry-specific factors (GLP-1 exposure, patent cliff avoidance, clinical trial catalysts) are not captured by standard Fama-French models and may explain some of the residual
3. **Non-linear exposures:** If the fund uses options or has convex payoff structures, linear factor models will misattribute returns
4. **Timing of exposures:** Annual average betas may mask meaningful intra-year shifts in positioning
5. **Survivorship bias:** We are evaluating this fund because it outperformed -- the sample is selected on the outcome

---

## Conclusions

1. **The PM's claimed ~600bps of alpha over XLV is substantially overstated.** Multi-factor decomposition suggests systematic factor exposures (market beta, momentum, size) explain substantially all of the return. Residual idiosyncratic alpha likely falls in the range of -1% to +2.5%, centered near zero.

2. **The "market-neutral" characterization is inconsistent with 52% net exposure.** The fund carries meaningful directional market risk, which drove the largest single component of returns (~8.1% from market beta alone).

3. **Statistical evidence for skill is insufficient.** A single year of modestly positive (or possibly negative) residual alpha cannot support a skill determination. The residual alpha t-statistic is likely well below conventional significance thresholds.

4. **The short book shows some encouraging signals** but requires further decomposition across multiple years to separate stock selection from subsector allocation effects.

5. **The fee structure is difficult to justify** on 2024 evidence alone, given that most returns appear replicable through passive factor exposure at much lower cost.

6. **Recommendation for allocator:** Request multi-year factor-adjusted performance attribution from the PM. Evaluate whether short book alpha persists. Consider whether the factor exposures (momentum, size, market beta) are intentional and aligned with the allocator's portfolio. Do not make a hire/fire decision based on a single year's decomposition.

---

## Sources

1. Paleologo, G. (2021). *Advanced Portfolio Management.* Wiley. Chapters on factor attribution and alpha decomposition.
2. Frazzini, A., Friedman, J., & Pomorski, L. (2015). "Deactivating Active Share." AQR Working Paper.
3. Bailey, D. & Lopez de Prado, M. (2014). "The Deflated Sharpe Ratio." *Journal of Portfolio Management.*
4. Kenneth French Data Library -- Fama-French factor returns, 2024.
5. Apex Healthcare Partners Year-End Fact Sheet, January 15, 2025.
6. Bloomberg market data: SPY, XLV, XBI returns as of December 31, 2024.

---

## Disclaimers

This analysis is for educational purposes and does not constitute investment advice. Factor decomposition involves estimation uncertainty, and the conclusions drawn here are probabilistic rather than definitive. Single-year attribution is inherently noisy and should be supplemented with longer-horizon analysis before making allocation decisions. All investments involve risk, including potential loss of principal.

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Multi-factor return decomposition (Fama-French + momentum + quality) with residual alpha estimation and hypothesis testing
