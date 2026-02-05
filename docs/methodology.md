# Evaluation Methodology

## Core Principles

### 1. Institutional Standards
All evaluations apply the standards expected of professional equity research analysts and portfolio managers at top-tier investment firms. AI outputs must meet the same quality bar as human-generated research that would be distributed to institutional clients or used for real portfolio decisions.

### 2. Evidence-Based Assessment
Every factual claim in AI-generated content must be:
- Verified against authoritative sources (10-K/10-Q filings, earnings transcripts, regulatory filings)
- Accompanied by clear citations
- Supported by shown calculations where applicable
- Current as of the stated date (no stale data)

### 3. Complete Reasoning Chains
Investment recommendations require explicit reasoning from thesis → evidence → conclusion:
- **Thesis**: What is the investment case? (e.g., "undervalued cyclical at earnings trough")
- **Evidence**: What data supports this? (valuation multiples, margin trends, peer comparisons)
- **Catalyst**: What will close the value gap? (demand recovery, cost reduction, management change)
- **Risk**: What could invalidate the thesis? (demand doesn't recover, competitive pressure)
- **Sizing**: How much capital should be allocated? (conviction level, risk/reward)

### 4. Adversarial Robustness
AI systems must handle edge cases and avoid common failure modes:
- Hallucinated or incorrect data
- Period mismatches (Q vs annual, TTM vs forward)
- GAAP vs non-GAAP confusion
- Survivorship bias
- Missing material risks
- Correlation vs causation errors
- Corporate action mishandling

## Evaluation Structure

Each evaluation module follows this structure:

### Scenario Definition
- Company/security context
- Market conditions and recent events
- Available data sources
- Specific task or question
- Time constraints (if applicable)

### Rubric Design
Scoring dimensions with explicit criteria:
- **Factual Accuracy** (0-25 points): Data correctness, source quality, calculation verification
- **Analytical Rigor** (0-25 points): Logic flow, assumption transparency, alternative consideration
- **Risk Assessment** (0-20 points): Key risk identification, probability/impact assessment
- **Completeness** (0-15 points): Coverage of material factors, balanced presentation
- **Actionability** (0-15 points): Clear recommendation, sizing rationale, timing consideration

Each dimension includes:
- Clear pass/fail thresholds
- Anchor examples of excellent/poor performance
- Relative weighting in overall score

### Golden Answer
Expert-level response demonstrating:
- Proper workflow and methodology
- Evidence-backed reasoning
- Risk awareness and balanced view
- Professional communication style
- Appropriate caveats and disclaimers

Golden answers serve as:
- Training targets for RLHF/DPO
- Baseline for comparison scoring
- Reference for prompt engineering
- Quality benchmark for production systems

### Adversarial Tests
Edge cases designed to surface common AI failures:
- **Data hallucination**: Scenario with limited public data where models may fabricate facts
- **Period confusion**: Mixed quarterly and annual data requiring careful normalization
- **Survivorship bias**: Historical analysis where failed companies must be included
- **Missing catalyst**: Investment case with unclear value realization mechanism
- **Hidden risk**: Material risk factor not obvious from surface-level analysis

## Scoring Methodology

### Raw Score Calculation
```
Total Score = Σ(Dimension_Score × Dimension_Weight)
Range: 0-100 points
```

### Pass Thresholds
- **Production-ready**: 85+ points (suitable for client delivery with minimal review)
- **Acceptable**: 70-84 points (requires human review and potential revision)
- **Needs work**: 50-69 points (significant issues, major revision required)
- **Fail**: <50 points (fundamental errors, not usable)

### Failure Modes Classification
Critical failures that result in automatic fail regardless of overall score:
- Material factual errors (wrong financial data, incorrect company facts)
- Regulatory violations (forward-looking guarantees, unbalanced presentation)
- Missing material risks
- Incorrect calculations in valuation or portfolio analysis
- Hallucinated data sources

## Evaluation Workflow

### 1. Setup Phase
- Load scenario definition and context
- Prepare data sources and reference materials
- Review rubric criteria and weights
- Set pass/fail thresholds

### 2. Execution Phase
- Generate AI output(s) using standardized prompts
- Collect supporting artifacts (calculations, data sources)
- Document model parameters and configuration
- Timestamp all outputs

### 3. Assessment Phase
- Verify all factual claims against sources
- Check calculations and derivations
- Evaluate reasoning chain completeness
- Score against rubric dimensions
- Flag failure modes and edge cases

### 4. Reporting Phase
- Generate structured evaluation report
- Document pass/fail status
- Highlight specific strengths and weaknesses
- Provide improvement recommendations
- Archive for training dataset

## Quality Assurance

### Rubric Validation
Before deployment, each rubric undergoes:
- Peer review by domain experts
- Calibration across multiple evaluators
- Anchor example selection
- Inter-rater reliability testing

### Golden Answer Review
Expert-level golden answers are:
- Fact-checked by independent analyst
- Reviewed for institutional quality standards
- Validated against real-world workflows
- Updated as market conditions change

### Continuous Improvement
Evaluation frameworks are living documents:
- Regular rubric refinement based on usage
- New adversarial tests as failure modes emerge
- Scenario updates as markets evolve
- Community feedback incorporation

## Use in Model Training

### RLHF / DPO Workflows
Golden answers serve as preferred outputs in preference-based training:
- Pair AI-generated output with golden answer
- Use institutional rubric to generate preference labels
- Train reward model on evaluator judgments
- Fine-tune generation model to match golden standard

### Synthetic Data Generation
Evaluation frameworks guide creation of training data:
- Scenario definitions → prompts for data generation
- Rubric criteria → quality filters for synthetic outputs
- Adversarial tests → hard negative examples
- Golden answers → demonstration examples

### Prompt Engineering
Rubrics inform system prompts and instructions:
- Scoring dimensions → explicit requirements in prompts
- Failure modes → negative examples and warnings
- Golden answers → few-shot demonstration examples
- Acceptance criteria → output format specifications

## Limitations and Caveats

### Not a Complete Assessment
These evaluations focus on analytical quality and institutional standards. They do not assess:
- Investment performance (actual returns)
- Timing accuracy (catalyst materialization)
- Market conditions (macro environment changes)
- Behavioral factors (sentiment, positioning)

### Scenario Specificity
Each evaluation is context-specific:
- Market conditions at time of creation
- Available information and data
- Regulatory environment
- Industry dynamics

Results may not generalize across different:
- Time periods (bull vs bear markets)
- Asset classes (equities vs fixed income)
- Investment styles (value vs growth vs momentum)
- Geographic regions (US vs international)

### Human Judgment Required
Automated scoring cannot fully replace:
- Nuanced risk assessment
- Judgment calls on marginal situations
- Creative or novel analytical approaches
- Contextual factors not captured in rubric

## Version Control

Evaluation frameworks are versioned to ensure reproducibility:
- Scenario definitions include creation date and context
- Rubrics note version and revision history
- Golden answers timestamped and attributed
- Scoring methodology changes documented

When markets evolve or new information emerges:
- Scenarios marked as "historical" if no longer relevant
- Updated versions created with clear change documentation
- Both versions retained for continuity
- Cross-references maintained

---

**Document version**: 1.0
**Last updated**: December 2024
**Author**: Brad Schonhoft, CFA
