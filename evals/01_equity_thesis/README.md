# Equity Thesis Evaluation Module

## Overview

This module evaluates AI-generated investment theses for long/short equity positions. It tests whether AI systems can construct sound, evidence-backed investment cases that meet institutional standards for analytical rigor, risk awareness, and actionability.

## What We're Testing

**Core capabilities**:
- Thesis clarity and specificity
- Evidence quality and citation
- Catalyst identification and timing
- Valuation support and methodology
- Risk assessment completeness
- Position sizing logic
- Regulatory compliance (balanced presentation, appropriate caveats)

**Common failure modes targeted**:
- Vague or circular reasoning ("stock is cheap because it's undervalued")
- Hallucinated financial data or company facts
- Missing or understated material risks
- Weak or unidentified catalysts
- Unreasonable valuation assumptions
- Time-period confusion (quarterly vs annual, TTM vs forward)
- Survivorship bias in historical analysis

## Evaluation Philosophy

A strong equity thesis should answer:
1. **What** is the investment case? (long/short, magnitude, time horizon)
2. **Why** is the opportunity mispriced? (what does market miss?)
3. **When** will value be realized? (catalyst and timing)
4. **What could go wrong?** (key risks and probability/impact)
5. **How much capital?** (position size given conviction and risk/reward)

The thesis must be:
- **Specific**: Directional call with expected return and time horizon
- **Logical**: Clear reasoning chain from thesis → evidence → conclusion
- **Evidence-backed**: All factual claims cited to verifiable sources
- **Risk-aware**: Material risks explicitly identified and assessed
- **Actionable**: Clear enough for someone to implement the trade

## Scenarios

### Completed Scenarios

**biotech_phase3_catalyst.yaml**
- Category: Event-driven, catalyst-focused
- Complexity: Moderate
- Key tests: Binary outcome assessment, probability estimation, risk/reward

**cyclical_trough_valuation.yaml**
- Category: Value/contrarian, cycle timing
- Complexity: High
- Key tests: Earnings normalization, peer comparison, margin mean reversion

### Planned Scenarios

- Quality compounder / moat assessment
- Activist campaign upside
- Growth deceleration / guidance cut
- Sum-of-parts / spinoff catalyst
- Turnaround story with credibility issues
- Short thesis on accounting red flags

## Rubric Structure

**Total Points**: 100

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Factual Accuracy** | 30% | Data correctness, source quality, calculation verification |
| **Analytical Rigor** | 25% | Logic flow, assumption transparency, alternative scenarios |
| **Risk Assessment** | 20% | Key risk identification, probability/impact assessment |
| **Evidence Quality** | 15% | Citation completeness, data recency, source authority |
| **Completeness** | 10% | Coverage of material factors, balanced presentation |

### Pass Thresholds

- **85+**: Production-ready (suitable for client delivery)
- **70-84**: Acceptable (needs minor review/revision)
- **50-69**: Needs work (significant gaps)
- **<50**: Fail (fundamental errors)

### Critical Failures (Automatic Fail)

- Material factual errors in financial data
- Missing material risk factors
- Incorrect calculations in valuation
- Regulatory violations (unbalanced presentation, forward guarantees)
- Hallucinated data sources

## Scoring Dimensions Detail

### 1. Factual Accuracy (30 points)

**Criteria**:
- All financial metrics cited to specific filings (e.g., "Q3'24 10-Q, page 8")
- No data older than 6 months unless historical context stated
- Calculations shown step-by-step
- Peer comparisons use consistent time periods
- Corporate actions correctly adjusted

**Scoring**:
- 27-30: All data verified, complete citations, shown calculations
- 21-26: Minor citation gaps or minor data staleness
- 15-20: Some data uncheckable or significant staleness
- 0-14: Multiple factual errors or hallucinated data

### 2. Analytical Rigor (25 points)

**Criteria**:
- Key assumptions explicitly stated
- Alternative scenarios considered (bull/base/bear)
- Clear if/then logic in thesis
- Causation vs correlation distinguished
- Counterarguments acknowledged

**Scoring**:
- 22-25: Comprehensive analysis with multiple scenarios
- 17-21: Solid base case, some scenario work
- 10-16: Basic analysis, limited scenario consideration
- 0-9: Weak logic, circular reasoning, no alternatives

### 3. Risk Assessment (20 points)

**Criteria**:
- 5+ specific risks identified
- Each risk has probability estimate
- Each risk has impact estimate
- Mix of company-specific and macro/sector risks
- Mitigation or hedging discussed

**Scoring**:
- 18-20: Comprehensive risk analysis with probability/impact
- 14-17: Most key risks identified with some assessment
- 8-13: Basic risk list, limited assessment
- 0-7: Major risks missing or cursory treatment

### 4. Evidence Quality (15 points)

**Criteria**:
- Citations to authoritative sources (filings, transcripts)
- Recent data (within 6 months)
- Shown calculations with intermediate steps
- Peer/historical comparisons for context
- Data consistency checks performed

**Scoring**:
- 14-15: Excellent sourcing with complete citations
- 11-13: Good sourcing with minor gaps
- 7-10: Acceptable sourcing but some uncheckable claims
- 0-6: Weak sourcing or unsupported assertions

### 5. Completeness (10 points)

**Criteria**:
- Covers valuation, catalysts, risks, sizing
- Balanced presentation (both bull and bear points)
- Time horizon specified
- Clear recommendation with expected return
- Monitoring plan or review triggers

**Scoring**:
- 9-10: All material factors covered, well-balanced
- 7-8: Most factors covered, reasonably balanced
- 4-6: Some gaps in coverage
- 0-3: Major omissions

## Golden Answer Structure

Each golden answer demonstrates expert-level analysis:

**Executive Summary** (3-4 sentences)
- Directional call (long/short)
- Expected return and time horizon
- Core thesis in one sentence
- Key catalyst

**Investment Thesis** (2-3 paragraphs)
- What the market is missing
- Why opportunity exists
- Supporting evidence with citations

**Valuation** (1-2 paragraphs)
- Current valuation vs historical/peers
- Target valuation methodology
- Assumptions and sensitivities

**Catalyst** (1 paragraph)
- Specific event or timeline
- Probability assessment
- Expected impact magnitude

**Key Risks** (bullet list)
- 5-7 specific risks
- Probability and impact for each
- Mitigation where applicable

**Position Sizing** (1 paragraph)
- Recommended size as % of portfolio
- Conviction level rationale
- Risk/reward justification

**Sources**
- Complete citation list

## Usage Examples

### Running Standard Evaluation
```bash
# Evaluate AI output against biotech catalyst scenario
python -m tools.eval_runner run \
  --module 01_equity_thesis \
  --scenario biotech_phase3_catalyst \
  --input examples/sample_ai_response.md
```

## Best Practices

### For Scenario Design
1. Use recent, public company situations where outcomes are known
2. Include enough context for independent verification
3. Specify data sources and cutoff dates clearly
4. Design for specific failure mode testing
5. Include both "easy" and "hard" versions

### For Rubric Application

1. Score dimensions independently before combining
2. Use anchor examples for calibration
3. Document reasoning for borderline scores
4. Flag critical failures immediately
5. Provide specific improvement feedback

---

**Module version**: 1.0  
**Last updated**: December 2024  
**Maintained by**: Brad Schonhoft, CFA