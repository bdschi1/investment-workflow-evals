# Reviewer Feedback: Heritage Regional Bancorp (HRB) — Risk Assessment

## Summary Assessment

**Overall: Fail** — The report presents three metrics that collectively describe a bank under significant funding stress (145% loan-to-deposit, 45bps NIM compression, $2.1B HTM unrealized losses), then concludes with "warrants monitoring" and a Hold rating. This is a severe evidence-conclusion disconnect. The Tier 1 capital ratio of 12.3% is measured against the 6% regulatory minimum — the wrong benchmark — while the declining trend (from 14.1% a year ago) goes unmentioned.

## Dimension Scores

| Dimension | Score | Rating |
|---|---|---|
| Factual Accuracy | 14/20 | Good |
| Methodological Soundness | 5/20 | Poor |
| Logic Chain Integrity | 3/20 | Fail |
| Confidence Calibration | 5/15 | Poor |
| Completeness of Coverage | 3/10 | Poor |
| Source Reliability | 3/5 | Acceptable |
| Practical Relevance | 7/10 | Good |
| **Total** | **40/100** | **Fail** |

## Detailed Findings

### Factual Accuracy: Good

Individual data points are internally consistent and plausible: 145% loan-to-deposit (up from 138%), NIM compression from 3.10% to 2.65%, $2.1B HTM unrealized losses, Tier 1 at 12.3%, 85bps wholesale funding cost increase. The arithmetic is not the problem. The problem is what conclusions are drawn from accurate data.

### Methodological Soundness: Poor

Two methodology failures:

1. **Wrong benchmark for capital adequacy.** The report measures Tier 1 capital (12.3%) against the 6% regulatory minimum and calls it a "substantial cushion." The 6% minimum is the level at which regulators seize the bank. It is not the level at which the market, rating agencies, or counterparties become concerned. In practice, falling below 8-9% triggers rating downgrades, funding cost increases, dividend restrictions, and deposit acceleration. The actual cushion is approximately 350bps above the market concern threshold, not 630bps above the regulatory floor. This is a material misrepresentation of the bank's safety margin.

2. **Metrics treated as independent when they form a causal chain.** The report lists three concerning metrics as if they are separate observations. In reality, they are connected: deposit outflows (evidenced by 145% loan-to-deposit and rising wholesale funding costs) → if outflows accelerate, the bank may need to sell HTM securities → realizing $2.1B in losses → Tier 1 capital ratio drops significantly. The report misses the causal relationship that makes each metric more concerning in the presence of the others.

### Logic Chain Integrity: Fail

This is the critical failure. The report's own data tells a story of escalating stress:

- Loan-to-deposit at 145% (industry average: 80-90%) — the bank is lending far more than it takes in deposits, relying on expensive wholesale funding
- NIM compressed 45bps in two quarters — profitability is eroding as funding costs rise
- Wholesale funding costs up 85bps since Q1 — the bank is paying more to replace lost deposits
- $2.1B in HTM unrealized losses — hidden balance sheet damage that becomes real if the bank is forced to sell

The report lists all of this and concludes: "these metrics warrant monitoring." This is the equivalent of listing symptoms of a serious illness and recommending the patient "keep an eye on things." The conclusion dramatically understates what the evidence shows.

The Hold rating is equally disconnected. A bank with these metrics trading at 0.85x tangible book already reflects market concern. The report does not address whether the 0.85x TBV is appropriate, too low, or too high given the risk profile.

### Confidence Calibration: Poor

"Provides a substantial cushion against stress scenarios" implies the bank can withstand adverse conditions. But the report does not model any stress scenarios. What happens to Tier 1 if 50% of HTM losses are realized? What if deposits decline another 10%? The word "substantial" is used without quantification or stress testing.

"Adequate capital to weather current headwinds" is similarly unsupported. The report has just documented that headwinds are intensifying (rising loan-to-deposit, compressing NIM, increasing funding costs) and the capital ratio is presumably declining — but provides no forward trajectory.

### Completeness of Coverage: Poor

Missing elements:
- Tier 1 capital trend (14.1% → 13.2% → 12.3% — declining at ~90bps per quarter)
- Stress test: impact of partial or full HTM loss realization on capital
- Peer comparison for loan-to-deposit ratio (145% vs industry 80-90%)
- Deposit composition: how much is insured vs uninsured? (SVB relevance)
- Liquidity analysis: what is the bank's access to Federal Home Loan Bank advances or other liquidity facilities?
- Forward NIM trajectory beyond management's vague "expects stabilization"

### Source Reliability: Acceptable

Financial data appears sourced from Q3 2025 filings. Management commentary on NIM stabilization and wholesale funding costs is attributed. No external comparative data provided.

### Practical Relevance: Good

The "evidence-conclusion disconnect" is one of the most dangerous AI failure patterns in financial analysis. The model assembles accurate, concerning data, then reaches a reassuring conclusion — producing output that looks rigorous (it cited real metrics) but draws the wrong inference. This pattern is particularly high-risk because it may pass a superficial review: the data is correct, the writing is professional, and the conclusion sounds reasonable in isolation. Only a reader who connects the dots across all three metrics recognizes the severity.

The SVB parallel makes this especially important. HTM unrealized losses were widely dismissed as "not impacting reported capital" before March 2023. The AI system should be trained to recognize that accounting treatment (HTM losses not flowing through capital) does not eliminate economic risk (those losses become real when assets must be sold).

## Critical Failures

1. **Evidence-conclusion disconnect:** Three red-flag metrics → "warrants monitoring" is a severe understatement
2. **Wrong capital benchmark:** 6% regulatory minimum is seizure level, not the relevant floor
3. **Missing causal chain:** Three metrics treated as independent observations when they are causally linked

## Improvement Recommendations

- Risk assessments should require the model to state whether the evidence supports the conclusion, with an explicit "does the conclusion match the severity of the data?" check
- Capital adequacy analysis should benchmark against market-relevant thresholds (8-9%), not just regulatory minimums (6%), and include the trend line
- When multiple risk metrics are presented, the model should assess whether they are independent or causally linked — and if linked, describe the transmission mechanism
- HTM unrealized losses should trigger a mandatory "what if realized?" stress test rather than being dismissed as an accounting non-event
