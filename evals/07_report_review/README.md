# Module 07: AI Report Review

Evaluates the ability to critically review AI-generated equity research reports and produce structured feedback. Unlike Modules 01-06 which test *generating* investment analysis, this module tests *reviewing* it — identifying errors, gaps, and overconfidence in AI output.

Each scenario contains a flawed AI-generated research excerpt. The task is to produce structured reviewer feedback across seven quality dimensions, flagging specific issues with evidence.

## Scenarios

| ID | Sector | Embedded Error Types |
|---|---|---|
| `saas_rule_of_40` | SaaS | Metric mischaracterization, convention mismatch, revenue type ambiguity |
| `cybersecurity_comp_table` | Cybersecurity | Metric switching in comp table, timeframe mismatch, implied equivalence |
| `medtech_tam_analysis` | Med-Tech | Arithmetic-as-analysis, stale source, static share assumption |
| `saas_scenario_analysis` | SaaS | Narrow scenario range, no drivers, unquantified confidence claims |
| `semiconductor_valuation` | Semiconductors | Circular self-comparison, missing compression context, no peer reference |
| `regional_bank_risk` | Banking | Evidence-conclusion disconnect, regulatory minimum misuse, no trend data |

## Rubric Dimensions

| Dimension | Weight |
|---|---|
| Factual Accuracy | 20% |
| Methodological Soundness | 20% |
| Logic Chain Integrity | 20% |
| Confidence Calibration | 15% |
| Completeness of Coverage | 10% |
| Source Reliability | 5% |
| Practical Relevance | 10% |

Pass threshold: 70/100. Excellence: 85/100.

## Relationship to Other Modules

- **Module 01 (Equity Thesis)** tests generating theses; Module 07 tests reviewing them
- **Module 02 (DCF Valuation)** covers valuation generation; Module 07 covers auditing valuation claims
- **Module 04 (Assumption Validation)** tests validating assumptions in isolation; Module 07 tests finding assumption failures embedded in complete reports

## Use Case

This module maps to the workflow of reviewing AI-generated equity research for accuracy, rigor, and practical investment utility — calibrating and improving autonomous research systems to operate at institutional standards.
