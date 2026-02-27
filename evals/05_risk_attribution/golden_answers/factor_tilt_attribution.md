# Golden Answer: Ridgeline Capital Equity Fund - Factor Tilt vs Stock Selection Attribution

## Executive Summary

**Fund:** Ridgeline Capital Equity Fund (Long-Only Multi-Sector)
**Period:** Full Year 2024
**Fund Return:** +26.3%
**Benchmark (SPY):** +22.1%
**Claimed Excess Return:** +420bps, attributed by PM to "bottom-up stock selection"
**Estimated Factor-Attributable Excess:** ~280-350bps (predominantly Value tilt)
**Estimated Residual Stock Selection Alpha:** ~120-140bps annualized, not statistically significant (t-stat: 1.3)
**Assessment:** Approximately two-thirds of Ridgeline's outperformance is attributable to a persistent Value factor tilt rather than idiosyncratic stock selection. The PM's narrative framing is partially misleading -- the Value exposure is likely intentional (consistent with "attractive valuations" philosophy) but labeling it as "stock selection" mischaracterizes the return source. The residual alpha is not statistically distinguishable from zero given the available track record. On a fee-adjusted basis, a passive Value ETF delivered essentially identical performance.

---

## Factor Attribution Decomposition

### Step 1: Factor-by-Factor Return Attribution

Using the fund's regression-estimated factor betas and 2024 factor returns:

| Factor | Fund Beta | t-stat | Factor Return (2024) | Contribution to Return |
|--------|-----------|--------|---------------------|----------------------|
| MKT-RF | 0.97 | 28.4 | +16.9% | +16.4% |
| SMB (Size) | 0.08 | 1.1 | +3.2% | +0.3% |
| HML (Value) | 0.35 | 3.8 | +8.1% | **+2.8%** |
| RMW (Profitability) | 0.12 | 1.4 | +4.8% | +0.6% |
| CMA (Investment) | 0.09 | 0.9 | +2.4% | +0.2% |
| UMD (Momentum) | -0.05 | -0.6 | -1.8% | +0.1% |
| Risk-free rate | | | +5.2% | +5.2% |
| **Total Factor Expected Return** | | | | **+25.6%** |
| **Regression Alpha (annualized)** | | | | **+1.4%** |

### Step 2: Excess Return Decomposition

The fund returned +26.3% versus the SPY benchmark at +22.1%, for +420bps excess return. Decomposing this:

| Component | Contribution | % of 420bps Excess |
|-----------|-------------|-------------------|
| Market beta drag (0.97 vs 1.0) | -0.5% | -12% |
| **Value tilt (0.35 x 8.1%)** | **+2.8%** | **~67%** |
| Quality tilt (0.12 x 4.8%) | +0.6% | ~14% |
| Size tilt (0.08 x 3.2%) | +0.3% | ~7% |
| Investment tilt (0.09 x 2.4%) | +0.2% | ~5% |
| Anti-momentum benefit (-0.05 x -1.8%) | +0.1% | ~2% |
| **Total factor-attributable excess** | **+3.5%** | **~83%** |
| **Residual stock selection** | **+1.2%** | **~28%** |

Note: Components sum to more than +4.2% due to estimation noise and rounding. The regression directly estimates residual alpha at +1.4% annualized.

### Step 3: The Value Factor Dominates

The single most important finding: **the Value factor (HML) alone explains approximately 2.8 percentage points of the 4.2% excess return -- roughly two-thirds.**

Key evidence for the dominance of Value:
- HML beta of 0.35 is statistically significant (t-stat: 3.8, p < 0.001)
- The tilt is persistent: HML beta ranged from 0.31 to 0.35 over 2022-2024
- The fund's portfolio characteristics confirm it: weighted P/E of 16.2x vs benchmark 21.5x, P/B of 2.8x vs 4.1x, dividend yield of 2.4% vs 1.3%
- Sector active weights are consistent with Value: overweight Financials (+4.2%), Industrials (+3.1%), Energy (+2.5%); underweight Technology (-6.8%)

This is not a transient or accidental exposure. It is a structural feature of the portfolio driven by the PM's stated philosophy of "attractive valuations."

---

## Hypothesis Testing: Is the Residual Alpha Statistically Significant?

### T-Statistic Analysis

The regression output provides an alpha t-statistic of **1.3.**

| Metric | Value | Assessment |
|--------|-------|-----------|
| Alpha (annualized) | +1.4% | Positive but modest |
| Alpha t-statistic | 1.3 | Below 2.0 significance threshold |
| Implied p-value | ~0.20 | Not significant at 5% or 10% |
| Interpretation | ~20% probability of observing this alpha if true alpha is zero | Cannot reject the null hypothesis |

**Conclusion:** The residual alpha is not statistically distinguishable from zero at conventional significance levels. This does not prove the PM lacks stock selection skill -- it means the data is insufficient to conclude that skill exists. A 20% p-value means there is roughly a one-in-five chance of seeing this result even if the PM has zero true alpha.

### Deflated Sharpe Ratio Assessment

Per Bailey and Lopez de Prado (2014), the minimum track record length for a Sharpe ratio to be reliably distinguishable from zero increases as the Sharpe decreases and as non-normality increases.

For the factor-adjusted residual:
- Residual alpha: ~1.4% annualized
- Residual volatility: approximately tracking error x sqrt(1 - R²) ≈ 4.8% x sqrt(0.06) ≈ 1.2%
- Residual Sharpe: 1.4% / 1.2% ≈ 1.17

This in-sample residual Sharpe is upward biased (selected for review because the fund outperformed). Adjusting for selection bias and non-normality, the DSR framework suggests 8-15+ years of monthly data would be needed to conclude the alpha is real at the 5% level. With only 5 years of history, the evidence is inconclusive.

### Cyclical Performance Pattern

The fund's track record is consistent with factor-driven, not alpha-driven, returns:

| Year | Fund Excess Return | Value Factor (HML) | Pattern Match |
|------|-------------------|--------------------|--------------|
| 2022 | +310bps | Positive (Value > Growth) | Yes -- outperformed when Value was up |
| 2023 | -220bps | Negative (Growth > Value) | Yes -- underperformed when Value was down |
| 2024 | +420bps | +8.1% (strong Value year) | Yes -- outperformed in strong Value year |

The fund outperforms in Value-favorable years and underperforms in Growth-favorable years. Three data points are too few for a rigorous test, but the pattern is consistent with the factor attribution: the fund's relative performance is driven primarily by the Value factor cycle, not by stock selection that would persist across environments.

---

## Evaluation of PM's Narrative

### Claim: "Disciplined bottom-up stock selection" drove 420bps outperformance

**Assessment: Substantially misleading, though not entirely inaccurate.**

The quantitative evidence:

| Return Source | Contribution | Characterization |
|---------------|-------------|-----------------|
| Value factor tilt | +2.8% (~67%) | Systematic factor exposure, not stock selection |
| Other factor tilts (Quality, Size, etc.) | +0.7% (~17%) | Systematic factor exposure |
| Market beta drag | -0.5% (-12%) | Below-benchmark beta |
| Residual stock selection | +1.2% (~28%) | Potentially alpha, but not statistically significant |

The PM attributes the entire +420bps to stock selection. The data shows approximately two-thirds to three-quarters is factor exposure. The remaining residual is positive but small and statistically indistinguishable from noise.

### Is the Value Tilt "Intentional"?

This is an important nuance:

1. **The Value tilt is almost certainly intentional.** The PM's philosophy emphasizes "attractive valuations" and "durable competitive advantages." The portfolio's characteristics (low P/E, low P/B, high dividend yield) and sector tilts (overweight value sectors, underweight growth) all confirm a deliberately value-oriented approach. The tilt has been persistent across three years of data.

2. **However, the PM may not frame it as factor exposure.** Many fundamental managers genuinely believe they are doing bottom-up stock selection when their valuation discipline systematically tilts them toward the Value factor. This is a well-documented phenomenon (Frazzini et al., "Deactivating Active Share"). The PM's self-concept ("stock picker") and the quantitative reality ("Value factor harvester with a modest stock selection overlay") can coexist.

3. **The distinction matters for fee negotiations and allocation decisions.** An intentional Value tilt is a legitimate strategy, but it is replicable at much lower cost through passive Value products. If 67% of the return is factor-driven, the fee should reflect the narrow scope of genuine active management.

---

## Fee-Adjusted Comparison to Passive Alternatives

### Ridgeline vs Passive Value (VLUE)

| Metric | Ridgeline | VLUE (Passive Value) | Difference |
|--------|-----------|---------------------|-----------|
| Gross return | +26.3% | +25.8% | +50bps |
| Management fee | 75bps | 15bps | +60bps |
| **Net return** | **+25.6%** | **+25.7%** | **-10bps** |

On a fee-adjusted basis, the passive Value ETF delivered essentially identical performance in 2024. The fund's 75bps fee consumed all of the modest alpha advantage and then some. The allocator paid 5x the fee for effectively the same return.

### Multi-Year Fee Perspective

Over a 5-year horizon, the cumulative fee differential compounds:
- Annual fee gap: 60bps (75bps - 15bps)
- 5-year cumulative drag: approximately 300bps
- The fund needs to generate at least 60bps of annual residual alpha just to *break even* with the passive alternative after fees

Given that the estimated residual alpha is ~120-140bps pre-fee (and not statistically significant), the net-of-fee alpha is approximately 60-80bps -- a thin and uncertain margin. Over multiple years, the compound effect of the fee gap is likely to erode most or all of the residual alpha advantage.

---

## Recommendations for the Allocator

### What We Can Say

1. **Approximately two-thirds of the 2024 excess return is attributable to the Value factor tilt.** This is arithmetic, not judgment. HML beta of 0.35 times HML return of +8.1% equals +2.8%, which is ~67% of the +4.2% excess.

2. **The residual alpha (~1.2-1.4%) is not statistically significant.** The t-stat of 1.3 does not clear conventional significance thresholds. We cannot conclude the PM has stock selection skill based on available evidence.

3. **The PM's narrative is partially misleading.** Attributing 420bps entirely to stock selection understates the role of systematic factor exposure and overstates the skill component.

4. **The fee structure is difficult to justify on quantitative evidence alone.** A passive Value ETF delivered comparable net returns at one-fifth the cost.

### What We Cannot Say

1. **We cannot conclude the PM has no skill.** The residual alpha is positive, and 5 years of data is insufficient for a definitive determination. Absence of evidence is not evidence of absence.

2. **We cannot rule out value-add beyond standard factors.** Industry knowledge, risk management, drawdown mitigation, and qualitative judgment are real skills that may not appear in a factor regression.

3. **We cannot extrapolate one year's decomposition.** If Value reverses sharply, the fund may underperform -- but the stock selection component, if genuine, would persist.

### Specific Actions

1. **Request multi-year factor-adjusted attribution from the PM.** If the fund consistently generates 100-150bps of residual alpha after factor adjustment across multiple years, that becomes a more meaningful signal even if not yet statistically significant.

2. **Evaluate portfolio-level factor exposure.** If the allocator already has Value exposure elsewhere (directly or through other active managers), Ridgeline adds unintended factor concentration. Understanding the total Value allocation is essential before maintaining this position.

3. **Negotiate fees.** If 60-70% of returns are factor-replicable, the fee should reflect the narrower scope of genuine active management. Options:
   - Reduce base fee to 40-50bps
   - Implement a fulcrum fee tied to factor-adjusted (not benchmark-relative) alpha
   - Negotiate a fee reduction in exchange for a longer lock-up commitment

4. **Set clear expectations.** The fund will likely underperform meaningfully in Growth-dominated markets. The allocator should budget for this and evaluate whether the factor cyclicality is compatible with the total portfolio.

5. **Do not make a binary hire/fire decision.** The evidence suggests a fund that is primarily a Value factor vehicle with a modest potential stock selection overlay. Whether that justifies the fees depends on the allocator's alternatives, portfolio context, and tolerance for factor cyclicality.

---

## Sources

1. Paleologo, G. (2021). *Advanced Portfolio Management.* Wiley. Chapters on performance attribution and factor decomposition.
2. Bailey, D. & Lopez de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management,* 40(5).
3. Frazzini, A., Friedman, J., & Pomorski, L. (2015). "Deactivating Active Share." AQR Working Paper.
4. Fama, E. & French, K. (2015). "A Five-Factor Asset Pricing Model." *Journal of Financial Economics,* 116(1).
5. Kenneth French Data Library -- Fama-French five-factor plus momentum returns, 2024.
6. Ridgeline Capital Equity Fund Year-End Report, January 15, 2025.
8. Bloomberg market data: SPY, VLUE, sector returns as of December 31, 2024.

---

## Disclaimers

This analysis is for educational purposes and does not constitute investment advice. Factor decomposition involves estimation uncertainty, and all conclusions are probabilistic rather than definitive. Regression-based factor betas are estimated with error and may not be stable over time. Single-year attribution is inherently noisy and should not be the sole basis for allocation decisions. All investments involve risk, including potential loss of principal.

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Multi-factor return decomposition (Fama-French five-factor + momentum), Deflated Sharpe Ratio assessment, fee-adjusted passive comparison
