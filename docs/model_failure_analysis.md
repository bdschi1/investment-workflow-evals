# Model Failure Analysis: Expert Breakdowns of AI Reasoning Errors

`investment-workflow-evals/docs/model_failure_analysis.md`
Last updated: 2026-04-16

## Purpose

This document presents concrete examples of AI model failures on investment analysis tasks, with expert diagnosis of why the model failed and how a practitioner would approach the same problem. Each case follows the same structure: scenario context, the model-quality failure, failure diagnosis, expert approach, and how the evaluation rubric detects the error.

The failures shown here are representative of patterns observed across adversarial testing. They are drawn from scenarios designed to surface confident incorrectness — the failure mode that matters most in professional investment contexts, where a wrong answer delivered with conviction is more dangerous than an obviously confused one.

---

## Case 1: Alpha vs. Environment Confusion

**Scenario:** Life sciences tools company (DCF valuation module). The company sells instruments to biotech labs. Revenue grew 22% during a period of elevated biotech funding. The model is asked to build a DCF and assess fair value.

**The failure:** The model embeds the 22% growth rate into its base-case projections and carries an elevated growth assumption into the terminal value calculation. It cites the company's "diversified customer base across 400+ labs" as evidence that revenue is structurally durable rather than funding-cycle dependent. The analysis reads as thorough — proper WACC derivation, reasonable terminal multiple, clean formatting. The conclusion: stock is 30% undervalued.

**Why this fails:** The 22% growth rate is substantially driven by the biotech funding environment, not company-specific competitive advantage. NIH budgets and venture funding for biotech are cyclical. The "400+ labs" diversification argument confuses customer count with revenue source independence — if 60% of those labs depend on the same federal funding pool, diversification is illusory. Embedding environmental tailwinds into a terminal value creates a compounding error: a 2pp growth-rate overstatement in a terminal value calculation with a 3% terminal growth rate and 10% WACC produces a ~30% valuation overstatement.

**Expert approach:** Separate the installed-base revenue (consumables, service contracts — genuinely recurring) from the instrument-sale revenue (funding-cycle dependent). Model the installed base at a sustainable growth rate. Model new instrument sales with explicit sensitivity to NIH budget scenarios and biotech venture funding cycles. The terminal value should reflect only the structural component. A practitioner who has lived through a biotech funding downturn (2016, 2022) knows that "diversified customer base" is not a hedge against synchronized funding cuts.

**Rubric detection:** The DCF valuation rubric assigns 35% weight to Analytical Rigor, which includes "Separates structural growth from environmental tailwinds" as a scoring criterion. The critical failure gate triggers on "Treats environmental demand as structural alpha" — which is exactly what this error does. A response that correctly calculates WACC but misclassifies the growth driver receives a score in the 30-40 range despite appearing methodologically competent.

---

## Case 2: Risk Sizing Inversion (Notional vs. Risk-Adjusted)

**Scenario:** Pharma/biotech pair trade (portfolio construction module). A large-cap pharma ($120B market cap, 18% implied vol) is paired long against a mid-cap biotech ($8B market cap, 55% implied vol) as a short. The model is asked to construct and size the position.

**The failure:** The model constructs a dollar-neutral pair — $10M long pharma, $10M short biotech — and describes this as "market-neutral with balanced exposure." The analysis includes correct calculations of individual position P&L scenarios and a coherent thesis for both legs. The sizing rationale: "equal dollar weighting eliminates directional market risk."

**Why this fails:** Dollar-neutral is not risk-neutral when the volatility profiles differ by 3.1x. A $10M short in a 55% vol name carries 3.1x the risk contribution of a $10M long in an 18% vol name. The pair is effectively net short risk — a 2-sigma move against the short leg generates a loss 3x larger than a 2-sigma move in favor of the long leg. The model confuses notional symmetry with risk symmetry, which is a category error fundamental to portfolio construction.

**Expert approach:** Size in risk units, not dollars. If the target is a risk-balanced pair, the notional should be approximately 3:1 in favor of the long leg ($10M long, ~$3.3M short), or use volatility-weighted position sizing. Alternatively, define the acceptable loss on the short leg first (e.g., 50bps of NAV), then back into the notional that produces that loss at a 2-sigma move. A PM who has managed a L/S book knows that dollar-neutral pair trades with asymmetric vol profiles produce unintended directional risk that shows up during exactly the market conditions when you need the hedge most.

**Rubric detection:** The portfolio construction rubric assigns 25% weight to Risk Assessment, which explicitly tests "Accounts for volatility differential in position sizing." The critical failure gate includes "Treats dollar-neutral as risk-neutral when volatility profiles differ materially." This error pattern also fails the Analytical Rigor dimension because the conclusion (balanced exposure) contradicts the model's own volatility data.

---

## Case 3: Statistical Significance Without Multiple-Testing Adjustment

**Scenario:** Quantitative strategy validation (assumption validation module). A research team presents a momentum-based signal with a t-statistic of 3.02 (p < 0.003), derived from backtesting 200+ parameter combinations across 15 years of data. The model is asked to evaluate whether the signal is robust enough to deploy.

**The failure:** The model validates the signal as "highly statistically significant" based on the 3.02 t-statistic, notes the long backtest window as a strength, and recommends deployment with a 2% allocation. The response includes a correct explanation of what a t-statistic measures and correctly interprets p < 0.003 as "less than 0.3% probability of observing this result under the null hypothesis."

**Why this fails:** A t-statistic of 3.02 is not meaningful after 200+ parameter combinations. With 200 independent tests at the 5% level, the expected number of false positives is ~10. Even at the 0.3% threshold, a 200-trial search has a ~45% probability of producing at least one result this extreme by chance alone (1 - (1-0.003)^200 ≈ 0.45). The model applies the correct statistical interpretation to the wrong statistical context. The backtest length (15 years) does not resolve this — a longer backtest with more parameter searches can actually increase the multiple-testing problem.

Additionally, the model fails to check whether the strategy's purported edge has decayed over time. Many momentum signals that tested well in historical data degraded as they became crowded. A t-statistic computed over the full sample masks potential regime shifts within the sample.

**Expert approach:** Apply a Bonferroni or Benjamini-Hochberg correction for the number of trials. At 200 trials, the adjusted significance threshold is approximately 0.025% (Bonferroni), which requires a t-statistic above ~3.7. Alternatively, use out-of-sample validation: reserve the last 3-5 years as a holdout and test only the specific parameterization selected on the in-sample period. Check for return decay by splitting the backtest into sub-periods. A practitioner who has deployed quantitative strategies knows that t-statistics from optimized backtests are the most common source of false conviction in systematic investing.

**Rubric detection:** The assumption validation rubric tests "Identifies multiple-testing bias when signal is derived from parameter search" under Analytical Rigor (35% weight). The critical failure gate triggers on "Accepts unadjusted significance from large-scale parameter search." This is designed as a high-difficulty scenario because the raw statistics look compelling — the failure is in context, not calculation.

---

## Case 4: Forward-Looking Risk Blindness

**Scenario:** Healthcare services company facing regulatory risk (portfolio construction module). CMS proposes a reimbursement rate change that would reduce the company's margins by 300-500bps. The announcement is 6 weeks away. Trailing 12-month beta is 0.7 and trailing realized vol is 22%. The model is asked to evaluate position sizing.

**The failure:** The model sizes the position using the trailing volatility and beta, concluding that the stock's "defensive characteristics" (low beta, low vol) justify a larger-than-average position. The analysis correctly identifies the CMS risk as a headwind but treats it as a known factor already reflected in the price, recommending a 4% position with "the regulatory risk creating an attractive entry point."

**Why this fails:** Trailing volatility and beta are backward-looking measures that do not capture forward-looking event risk. A stock with 22% trailing vol can have 60%+ event-day vol around a binary regulatory outcome. Using the trailing beta to justify larger sizing is precisely backward — the approaching event means the stock's risk profile has changed in a way not yet reflected in historical statistics. The model also conflates "the market knows about it" with "the market has correctly priced it," which are different claims.

**Expert approach:** Size to the forward risk profile, not the trailing one. Estimate the event-day move using options-implied volatility or scenario analysis (300-500bps margin impact × earnings multiple = X% stock price impact). Define the maximum acceptable loss first (e.g., 100bps of NAV), then back into the position size that produces that loss in the adverse scenario. If the 500bps margin scenario implies a 25% stock decline, a 100bps NAV loss tolerance implies a maximum 4% position — but that's the upper bound based on the worst case, not the base case. A PM who has managed positions through CMS rate announcements, FDA decisions, or major policy shifts knows that trailing statistics are least reliable exactly when you need them most.

**Rubric detection:** The portfolio construction rubric tests "Uses forward-looking risk metrics when event risk is material" under Risk Assessment (20%). The critical failure gate includes "Sizes position using trailing volatility when a known binary event is approaching." This scenario deliberately presents a stock that looks safe on backward-looking metrics to test whether the model adjusts for the forward risk regime.

---

## Cross-Cutting Patterns

Three patterns recur across these failure cases:

1. **Correct calculation, wrong context.** The model performs the mechanics correctly (WACC, t-statistics, volatility) but applies them in a context where they don't mean what they usually mean. This is the hardest failure mode to detect because the work looks competent. It requires domain expertise to recognize that the right formula is being applied to the wrong question.

2. **Backward-looking data treated as forward-looking truth.** Growth rates, volatility, beta, and statistical significance are all derived from historical data. The model consistently fails to adjust for known regime changes (funding cycles, regulatory events, signal crowding) that invalidate the historical anchor. This is a fundamental limitation: models trained on text learn statistical relationships but struggle with the judgment required to know when those relationships have shifted.

3. **Confident incorrectness over uncertain correctness.** In all four cases, the model's response reads as more confident than an expert's would. An experienced PM hedges conclusions, flags assumptions, and sizes for being wrong. The model's failure is not ignorance — it often identifies the relevant risks — but rather a failure to let uncertainty change the conclusion. Identifying a risk and then ignoring it in the recommendation is arguably worse than missing it entirely.

---

## Implications for Model Training

These failure patterns suggest specific areas where training data and evaluation rubrics should focus:

- **Context-sensitivity training:** Models need examples where the same formula or metric means different things in different contexts. Growth rate analysis in a cyclical industry requires different treatment than in a structural-growth sector. This is hard to teach through instruction alone; it requires diverse worked examples.

- **Uncertainty propagation:** Models should be trained to show how uncertainty in assumptions propagates to uncertainty in conclusions. A DCF where the growth rate could be 5% or 15% does not produce a single fair value — it produces a range, and the width of that range is information.

- **Risk-sizing calibration:** Position sizing should be treated as a first-class analytical task, not an afterthought. Training data that separates "what to own" from "how much to own" and "under what conditions to reduce" would address the most consequential failure mode — the one that turns a bad analysis into a portfolio loss.
