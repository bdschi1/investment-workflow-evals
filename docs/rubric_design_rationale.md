# Rubric Design Rationale

`investment-workflow-evals/docs/rubric_design_rationale.md`
Last updated: 2026-04-16

## Purpose

This document explains the design decisions behind the evaluation rubrics in this repository — why dimensions are weighted the way they are, how critical failure gates were calibrated, what alternative structures were considered and rejected, and what trade-offs each design choice involves. The goal is to make the rubric architecture transparent and auditable, not just usable.

---

## Design Philosophy

Three principles govern every rubric in this repository:

1. **Consequences over effort.** Dimensions are weighted by the severity of getting them wrong, not by the difficulty of getting them right. Factual accuracy is weighted 30-35% not because facts are hard but because a wrong fact makes the entire analysis unusable. Completeness is weighted 10-15% because a missing section is recoverable; a wrong conclusion is not.

2. **Binary failure gates over continuous scoring.** Some errors are not "slightly wrong" — they are category errors that invalidate the analysis regardless of how well other dimensions score. A DCF that treats environmental tailwinds as structural alpha produces a wrong answer no matter how clean the WACC derivation is. Critical failure gates enforce this by capping the total score when specific errors are present.

3. **Behavioral anchors over abstract descriptions.** Each scoring level (Excellent through Fail) is defined by what the response *does*, not by adjectives like "thorough" or "adequate." This reduces inter-rater disagreement and makes automated grading more reliable. The anchor for "Excellent" in risk assessment is not "demonstrates strong risk awareness" — it is "sizes the short leg 3.1x smaller in notional to match the vol differential."

---

## Rubric 1: Equity Thesis (Module 01)

### Dimension Weights

| Dimension | Weight | Rationale |
|---|---|---|
| Factual Accuracy | 30% | Wrong facts = unusable analysis. A thesis built on incorrect revenue figures, market share data, or competitive dynamics cannot be salvaged by strong reasoning. This is the highest-consequence failure. |
| Analytical Rigor | 25% | Sound reasoning on correct facts is the core value proposition. But rigor without facts is academic, which is why it ranks second. |
| Risk Assessment | 20% | Missing risks create unhedged tail exposure. Weighted below accuracy and rigor because risk omission is detectable in review; factual errors are often not. |
| Evidence Quality | 15% | Unsourced claims are weaker but less dangerous than wrong claims. A thesis that says "management guided to 15% growth" without citing the earnings call is sloppy but potentially correct. |
| Completeness | 10% | Missing sections (e.g., no competitive analysis) degrade the thesis but do not make it wrong. An incomplete but accurate thesis is more useful than a comprehensive but inaccurate one. |

### Why Not Equal Weights?

Equal weighting (20% each) was considered and rejected. The problem: a response could score 80/100 while containing a material factual error that invalidates the conclusion. Under equal weights, strong performance on completeness and evidence quality could mask a factual accuracy failure. The current weighting ensures that a response with a material factual error cannot score above 70 (the pass threshold) unless it excels on every other dimension — which is the intended behavior.

### Critical Failure Gates

The equity thesis rubric defines four automatic-fail conditions:

1. **Material factual error (>20% misstatement).** If revenue is $1.2B and the model uses $900M, the entire thesis is built on a wrong foundation. No scoring up.
2. **Missing obvious material risk.** If a biotech thesis omits FDA approval risk, the analysis is not just incomplete — it is misleading. The distinction from "completeness" is severity: missing a competitive analysis section is a completeness gap; missing the single largest risk factor is a failure of professional judgment.
3. **Forward-looking guarantees.** Statements like "revenue will grow 20%" or "approval is certain" violate the fundamental principle that investment analysis is probabilistic. This gate exists because overconfident language in a thesis can distort downstream decisions (position sizing, hedging) in ways that create real portfolio risk.
4. **Hallucinated data sources.** Citing a 10-K filing that does not exist, referencing earnings call commentary that was never made, or inventing market share data. Fabricated evidence is worse than missing evidence because it cannot be detected without independent verification.

### Alternatives Considered

**Three-tier rubric (Strong / Acceptable / Fail):** Simpler to apply but too coarse. The difference between a 75 and a 90 matters — the former needs revision, the latter does not. Three tiers cannot express this distinction.

**Seven dimensions instead of five:** Adding "Originality" and "Actionability" was considered. Rejected because originality is subjective (what counts as a novel insight depends on the reader's prior knowledge) and actionability is context-dependent (a thesis can be analytically excellent but not actionable if the stock is illiquid). Both dimensions would have introduced inter-rater disagreement without improving the rubric's ability to detect the failures that matter.

---

## Rubric 2: Portfolio Construction (Module 03)

### Dimension Weights

| Dimension | Weight | Rationale |
|---|---|---|
| Analytical Rigor | 35% | Portfolio construction is primarily a reasoning task. The "right answer" depends entirely on the quality of the analytical framework. A position size derived from sound reasoning is defensible even if the outcome is bad; a position size derived from poor reasoning is indefensible even if the outcome is good. |
| Risk Assessment | 25% | Higher than in the equity thesis rubric because portfolio construction IS risk management. A thesis can be useful without a risk section; a position-sizing recommendation without risk assessment is malpractice. |
| Factual Accuracy | 20% | Lower than in thesis rubric because portfolio construction scenarios typically provide the relevant data (volatility, correlation, NAV) — the task is not to find facts but to reason about them. Factual errors are less likely and less consequential here. |
| Completeness | 10% | Same rationale as thesis rubric. |
| Evidence Quality | 10% | Lower because the evidence base is defined by the scenario. The task is reasoning about given evidence, not sourcing new evidence. |

### Why Analytical Rigor Is 35% Here but 25% in Equity Thesis

The equity thesis module tests whether the model can identify the right facts AND reason about them. Portfolio construction provides the facts and tests reasoning in isolation. When reasoning is the primary task, reasoning quality should dominate the score. This is not a universal principle — it is a design choice that reflects what each module is designed to measure.

### Critical Failure Gates

1. **Dollar-neutral treated as risk-neutral.** The single most common portfolio construction error. If two positions have materially different volatility profiles and the response treats equal dollar weighting as "balanced," the analysis has a category error that cannot be fixed by better writing.
2. **Trailing volatility used for forward event risk.** When a known binary event (FDA decision, earnings, regulatory ruling) is approaching, trailing statistics understate forward risk. Sizing to trailing vol in this context is not conservative — it is mispriced risk.
3. **Missing correlation analysis in multi-position sizing.** Two 3% positions in correlated names are not two independent 3% bets — they are a 6% bet on the same factor. Missing this is a portfolio-level risk failure.

### Why Three Gates Instead of One

A single gate ("any material analytical error") was tested and produced too many false positives. Raters disagreed on what constituted "material." The three specific gates are designed to be unambiguous: either the response treats dollar-neutral as risk-neutral or it does not. Binary conditions eliminate the subjectivity that a general "material error" gate introduces.

---

## Rubric 3: Risk Attribution (Module 05)

### Dimension Weights

| Dimension | Weight | Rationale |
|---|---|---|
| Analytical Rigor | 30% | Same principle as portfolio construction — risk attribution is a reasoning task. |
| Factual Accuracy | 25% | Higher than portfolio construction because risk attribution requires correctly reading and interpreting quantitative data (factor loadings, return decomposition, correlation matrices). Misreading a Barra decomposition is a factual error with analytical consequences. |
| Risk Assessment | 20% | Recursive: the task IS risk assessment, so this dimension tests whether the risk assessment is itself well-assessed. Does the response identify the limitations of the attribution framework? Does it distinguish between realized and forward-looking risk? |
| Evidence Quality | 15% | Risk attribution requires showing work — arithmetic, decomposition steps, factor-by-factor analysis. "The portfolio has factor exposure" without showing which factors, how much exposure, and what the P&L impact would be is an evidence failure. |
| Completeness | 10% | Same rationale throughout. |

### Critical Failure Gates

1. **Factor return attributed to stock selection.** If a Barra decomposition shows 5% of 6% excess return is factor exposure and the response credits the PM with "strong stock picking," the analysis has failed at its core task. This is the risk attribution equivalent of the alpha/environment confusion in the thesis module.
2. **Arithmetic presented without showing steps.** "The portfolio's true alpha is approximately 1%" without showing: total return, factor contributions by factor, residual calculation. Risk attribution that states conclusions without traceable arithmetic is not auditable and therefore not useful.

### Why This Rubric Has Only Two Gates

Risk attribution scenarios are narrower in scope than equity thesis or portfolio construction. The failure modes are more concentrated — the primary error is misattributing returns, and the secondary error is not showing work. Additional gates were considered (e.g., "fails to discuss factor regime dependency") but were reclassified as scoring criteria rather than gates because they affect quality, not validity.

---

## Cross-Rubric Design Patterns

### Weight Allocation Follows Task Type

| Task Type | Highest Weight | Rationale |
|---|---|---|
| Information-gathering (thesis, research) | Factual Accuracy (30-35%) | Getting the facts right is the foundation |
| Reasoning-intensive (portfolio, risk) | Analytical Rigor (30-35%) | Facts are given; reasoning is the test |
| Quantitative (attribution, DCF) | Factual Accuracy + Evidence (40% combined) | Numbers must be right AND shown |

This pattern was discovered empirically during calibration, not designed in advance. Early rubric versions used the same weights across all modules. Calibration exercises revealed that raters consistently disagreed on scores for reasoning-heavy tasks when factual accuracy was weighted too high — the "right facts, wrong conclusion" responses were being scored too generously. Adjusting weights by task type resolved the disagreement.

### Critical Failure Gates Are Derived From Real Investment Losses

Every critical failure gate corresponds to an error pattern that has caused real capital losses in professional investment management:

- **Alpha/environment confusion** — PMs who confused a rising tide with stock-picking skill and maintained positions through the cycle turn, producing large drawdowns.
- **Notional vs. risk-adjusted sizing** — Pair trades that were "dollar neutral" but risk-directional, producing outsized losses on the short leg during a squeeze.
- **Trailing vol for forward events** — Positions sized to trailing volatility that experienced 3-5x the expected move on a binary event, breaching risk limits.
- **Factor misattribution** — Allocators who increased capital to PMs with "alpha" that was actually factor exposure, then experienced correlated drawdowns across multiple allocations.

These gates are not theoretical — they encode the specific judgment failures that separate experienced practitioners from models that pattern-match on surface-level analytical competence.

### Scoring Anchor Calibration

Each rubric's scoring anchors were calibrated through the following process:

1. **Draft anchors** — Written based on practitioner experience of what "excellent" vs. "acceptable" vs. "failing" analysis looks like in practice.
2. **Test against golden answers** — Golden answers (expert-written reference responses) are scored against the rubric. A golden answer that scores below 85 indicates a rubric calibration problem, not a golden answer problem.
3. **Test against adversarial examples** — Adversarial responses ("sounds smart but is wrong") are scored. An adversarial example that scores above 50 indicates the rubric is not detecting the intended failure.
4. **Adjust thresholds** — Pass threshold (70) and excellence threshold (85) are set so that: a response with one non-critical weakness passes, a response with the core analytical insight scores 85+, and a response with a critical failure does not pass regardless of other dimensions.

This calibration loop is iterative. Changes to scenarios or golden answers trigger re-calibration of the associated rubric.

---

## Limitations

- **Inter-rater reliability is not formally measured.** The rubrics are designed for reliability (behavioral anchors, binary gates), but Cohen's kappa or similar metrics have not been computed across multiple raters. This is a gap that limits confidence in the rubric's consistency when applied by different evaluators.
- **Sample size constraints.** Rubrics are calibrated against 3-6 golden answers and adversarial examples per module. Larger calibration sets would increase confidence that scoring thresholds are correctly placed.
- **Domain scope.** All rubrics are designed for equity-oriented investment analysis. Extension to fixed income, derivatives, or macro analysis would require new dimensions and re-calibration.
