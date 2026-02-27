# Golden Answer: Statistical Significance Trap - Backtest Overfitting and Multiple Testing Bias

## Executive Summary

**Strategy:** Earnings Quality Momentum (EQM) systematic equity strategy
**Reported Sharpe:** 0.78 (t-stat: 3.02, p < 0.01)
**Number of Trials:** 200+ parameter combinations tested on the same 15-year sample
**Adjusted Assessment:** After correcting for multiple testing, the reported Sharpe is likely not statistically distinguishable from zero. The strategy is a probable false discovery.
**Recommendation:** Do not allocate the full $200M. Require a 12-month out-of-sample paper trading period. If live results confirm at least Sharpe 0.40 after costs, consider a $25-50M pilot allocation.

---

## Assumption Extraction

### Explicit Assumptions
1. **Sharpe ratio: 0.78** -- reported as the strategy's risk-adjusted performance
2. **T-statistic: 3.02** -- presented as strong statistical evidence (p < 0.01)
3. **Transaction costs: 10bps per side** -- assumed in backtest
4. **Backtest period: 15 years (2010-2024)** -- in-sample estimation window
5. **Monthly rebalance, 45% turnover** -- implementation parameters
6. **$200M recommended allocation** -- proposed capital commitment

### Implicit Assumptions (Not Stated, But Embedded)
7. **Single-test statistical framework** -- the t-stat of 3.02 is presented without adjustment for 200+ trials
8. **In-sample = out-of-sample** -- no holdout data was used for validation
9. **Reported parameterization is the "true" strategy** -- rather than the winner of a look-back optimization
10. **Backtest returns are achievable in live trading** -- despite the team's prior strategy underperforming by 0.35 Sharpe
11. **Transaction costs are constant and accurate at scale** -- 10bps may not hold for $200M in smaller Russell 1000 names

---

## The Multiple Testing Problem

### Why the Reported Statistics Are Overstated

The quant team tested 200+ parameter combinations over the same 15-year dataset and reported only the best result. This is the definition of data snooping. The statistical intuition:

**Expected maximum Sharpe from pure noise:** If you test N independent strategies where the true Sharpe is zero for all of them, the best-performing strategy will have an observed Sharpe of approximately:

E[SR_max] ≈ sqrt(2 × ln(N)) × (1/sqrt(T))

For N = 200, T = 15 years:
- E[SR_max] ≈ sqrt(2 × 5.3) × (1/sqrt(15)) ≈ 3.26 × 0.258 ≈ 0.84

This means that even with NO true signal in any of the 200 strategies, random chance alone would produce a best-of-200 with an observed Sharpe of approximately 0.84 -- which *exceeds* the reported 0.78.

**This is the single most important finding:** The reported Sharpe of 0.78 is fully consistent with noise. A random selection from 200+ null strategies would be expected to produce a result of similar or greater magnitude. The strategy cannot be distinguished from a false discovery based on the in-sample statistics alone.

### Only 8 of 200+ Achieved Sharpe > 0.70

The team discloses that only 8 of 200+ combinations showed Sharpe above 0.70. This is actually *consistent with* the null hypothesis (all strategies have zero true Sharpe):

Under the null, the distribution of observed Sharpes for N = 200 strategies over T = 15 years would produce:
- ~5% of strategies with Sharpe above ~0.50 by chance (approximately 10 strategies)
- ~4% with Sharpe above 0.70 (approximately 8 strategies)

The fact that exactly ~8 strategies cleared 0.70 is almost precisely what we would expect from noise. This is not evidence of signal -- it is evidence consistent with the absence of signal.

---

## Statistical Adjustments

### Bonferroni Correction

The simplest multiple-testing adjustment divides the significance level by the number of tests:

- Reported p-value: < 0.01
- Bonferroni-adjusted threshold: 0.05 / 200 = 0.00025
- Required t-stat for significance at 5% level after correction: approximately 3.7 (for ~180 monthly observations)
- Reported t-stat: 3.02

**Result:** The t-stat of 3.02 does NOT survive Bonferroni correction. The strategy would need t > 3.7 to be significant after adjusting for 200 trials.

Note: Bonferroni is conservative because it assumes all 200+ tests are independent. Many parameter variations are correlated (e.g., 6-month vs 9-month lookback windows), so the effective number of independent tests may be 50-100. Even at 50 independent tests, the required t-stat would be approximately 3.3, which the reported 3.02 still does not clear.

### Deflated Sharpe Ratio (Lopez de Prado, 2014)

The DSR adjusts for:
- Number of trials (N = 200+)
- Non-normality of returns (skewness, kurtosis)
- Sample length (T = 180 months)
- Correlation among trials

The DSR p-value for SR = 0.78 given N = 200 trials is estimated at approximately 0.40-0.60, far above any conventional significance threshold. In plain language: there is roughly a 40-60% probability of observing this Sharpe or better from the best of 200 null strategies.

**The DSR-adjusted Sharpe -- the "true" signal strength after accounting for the search -- is likely in the range of 0.00-0.30.** This is economically insignificant for a strategy requiring dedicated capital, infrastructure, and risk budget.

### Harvey, Liu, and Zhu (2016)

HLZ argue that the conventional t > 2.0 threshold is inadequate in finance because the field has tested thousands of factors. Their minimum threshold is t > 3.0, but this applies to the broader literature over decades. For a single team testing 200+ variants on one dataset, the effective threshold is t > 3.5-4.0.

The reported t-stat of 3.02 falls below even the HLZ field-level minimum once the team-specific trial count is considered.

---

## Statistical Significance vs Economic Significance

### Transaction Costs

The backtest assumes 10bps per side. This is optimistic:

| Component | Backtest Assumption | Realistic Estimate | Gap |
|-----------|--------------------|--------------------|-----|
| Commission | ~2bps | ~2bps | Minimal |
| Spread crossing | ~3bps | ~5-8bps (smaller R1000 names) | 2-5bps |
| Market impact | ~5bps | ~10-20bps (at $200M scale) | 5-15bps |
| **Total per side** | **10bps** | **17-30bps** | **7-20bps** |

At 45% turnover (90% effective for long-short):
- Backtest cost: 90% × 20bps = 18bps annual
- Realistic cost: 90% × 34-60bps = 31-54bps annual
- **Additional drag: 13-36bps, reducing Sharpe by 0.10-0.30**

### Backtest-to-Live Decay

The team's own prior strategy provides the most relevant base rate:
- Prior strategy: Backtest Sharpe exceeded live Sharpe by 0.35 since 2022 launch
- McLean and Pontiff (2016): Publication of a factor reduces returns by ~50% out-of-sample
- Expected decay for a heavily optimized in-sample strategy: 0.30-0.50 Sharpe points

### Estimated Live Performance

| Component | Sharpe Impact |
|-----------|--------------|
| Reported backtest Sharpe | 0.78 |
| Multiple-testing adjustment | -0.30 to -0.50 |
| Transaction cost adjustment | -0.10 to -0.30 |
| Backtest-to-live decay (team base rate) | -0.15 to -0.35 |
| **Estimated live Sharpe** | **-0.17 to +0.23** |

The wide range reflects genuine uncertainty, but the center of gravity is near zero. The most likely outcome is that the strategy generates approximately zero risk-adjusted returns after accounting for data snooping, realistic costs, and implementation friction.

### The "Best Period" Problem

The strategy's strongest performance came during 2020-2021, a period of extreme factor dispersion and momentum tailwinds. This period is unlikely to repeat in kind. Strategies that look best in unusual environments often mean-revert -- or worse -- when conditions normalize. A responsible evaluation should re-run the backtest excluding 2020-2021 to see if the signal survives in "normal" markets.

---

## Red Flags

### 1. Structural: Best-of-200 Without Adjustment (Critical)

This is a methodology flaw, not an aggressive assumption. Reporting the best of 200+ backtests without statistical adjustment is functionally equivalent to p-hacking. The framing of the result ("t-stat of 3.02, significant at the 1% level") without disclosing the adjustment creates a misleading impression of evidence quality.

### 2. Structural: No Out-of-Sample Validation (Critical)

The entire 15-year sample was used for both parameter search and performance reporting. This makes it impossible to distinguish signal from noise using only the reported results. Any credible systematic strategy should reserve at least 30% of the data for out-of-sample testing, or use walk-forward validation.

### 3. Inconsistency: Prior Strategy Underperformance (Important)

The team's previous strategy has underperformed its backtest Sharpe by 0.35 points since its 2022 launch. This is not a one-off disappointment -- it is a revealed base rate for this team's backtest-to-live translation. The same process that produced the prior overfitting is being used again with more degrees of freedom (200+ parameter combinations).

### 4. Signal: "Academic Support" Conflated with Parameterization Validation (Moderate)

The team cites Sloan (1996) and Dechow et al. (2010) to support the earnings quality signal. The academic evidence for accruals predicting returns is legitimate. However, academic support for the *concept* does not validate the specific *implementation* -- the particular combination of lookback window, skip period, weighting scheme, and quality metric that produced a 0.78 Sharpe from 200+ alternatives. Many academically supported signals exist and yet fail to deliver after optimization and implementation.

### 5. Signal: Optimistic Transaction Cost Assumptions (Moderate)

The 10bps-per-side assumption is at the low end of what a $200M book would realistically experience in the smaller names within the Russell 1000. Realistic costs of 17-30bps per side would materially erode returns.

---

## Recommended Adjustments

| Assumption | Quant Team | Recommended | Justification |
|-----------|-----------|-------------|---------------|
| T-stat significance | 3.02, p < 0.01 | Not significant after adjustment | 200+ trials require t > 3.7 (Bonferroni) |
| Sharpe ratio | 0.78 | 0.00-0.30 (adjusted) | DSR correction for N = 200+ |
| Transaction costs | 10bps per side | 17-30bps per side | Market impact at $200M scale |
| Out-of-sample validation | None | Required before allocation | Standard practice for systematic strategies |
| Allocation | $200M immediately | $0 until validated; $25-50M pilot after | Conditional on live evidence |

---

## Decision Framework

### Do Not Allocate $200M on In-Sample Backtest

The evidence does not support a full allocation:
- Statistics do not survive multiple-testing correction
- No out-of-sample validation
- Team's own prior strategy demonstrates the overfitting problem
- Realistic transaction costs further erode the already-questionable signal

### Conditional Allocation Path

| Phase | Duration | Capital | Advancement Criteria |
|-------|----------|---------|---------------------|
| Out-of-sample paper trading | 12 months | $0 | Signal direction matches; Sharpe > 0.20 |
| Pilot allocation | 6-12 months | $25-50M | Live Sharpe > 0.30 after all costs |
| Scale-up | 12+ months post-pilot | $100-150M | Consistent alpha; live SR > 0.40 |
| Full allocation | After 2+ years live | $200M | Sustained evidence of durability |

### Process Improvements to Require

1. **Pre-register the parameter search space** before running backtests. Define the number and range of combinations in advance.
2. **Apply DSR or Bonferroni correction** to all reported statistics. This should be a team standard, not a request from the PM.
3. **Hold out at least 30% of data** for genuine out-of-sample testing, or use walk-forward validation.
4. **Report all tested variants**, not just the best. A table showing the full distribution of Sharpe ratios across all 200+ trials would be far more informative than a single cherry-picked result.
5. **Stress-test transaction costs** at 2x and 3x the assumed level. If the strategy only works at 10bps, it does not work.
6. **Explain the prior strategy's underperformance.** What went wrong, and what has changed in the process to prevent a recurrence?

---

## Summary: Key Principles

1. **A t-stat of 3.02 from the best of 200+ trials is not significant.** The expected maximum t-stat from 200 null strategies is approximately 3.3, meaning the reported result is consistent with pure noise.

2. **The Deflated Sharpe Ratio likely reduces the "true" Sharpe to near zero.** After adjusting for the number of trials, the evidence for a genuine signal is weak.

3. **Statistical significance is not economic significance.** Even if a modest signal exists, transaction costs, market impact, and backtest-to-live decay may eliminate economic value.

4. **The team's own track record is the most informative prior.** A 0.35 Sharpe decay on their previous strategy suggests systematic overfitting, not bad luck.

5. **The correct response is conditional, not binary.** The underlying signal concepts (earnings quality, momentum) have academic merit. But the specific parameterization is unvalidated. Require out-of-sample evidence before committing capital.

6. **Demand process changes.** Pre-registration, multiple-testing adjustment, held-out data, and full disclosure of the parameter search are standard practices. Their absence here is a red flag about the team's quantitative rigor.

---

**Author:** Expert Analyst
**Date:** February 2026
**Methodology:** Multiple testing adjustment (Bonferroni, Deflated Sharpe Ratio), backtest-to-live decay estimation, conditional allocation framework
