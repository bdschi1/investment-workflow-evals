# Risk Attribution Module

This module evaluates AI-generated risk attribution and performance analysis, testing the ability to decompose returns into factor, environmental, and idiosyncratic components.

## Focus Areas

- **Factor Decomposition** - Correctly attributing returns to systematic factors vs alpha
- **Hypothesis Testing** - Evidence-based conclusions about skill vs luck
- **Contextual Evaluation** - Evaluating performance conditional on environment
- **Intentionality Assessment** - Distinguishing deliberate exposures from accidental bets

## Status

Active -- 2 scenarios, 1 rubric, 2 golden answers.

## Scenarios

| Scenario | File | Focus |
|----------|------|-------|
| Healthcare L/S Factor Decomposition | `scenarios/healthcare_ls_factor_decomposition.yaml` | Multi-factor decomposition of a healthcare L/S fund's returns; tests whether claimed alpha survives factor adjustment |
| Factor Tilt Attribution | `scenarios/factor_tilt_attribution.yaml` | Value factor tilt vs stock selection in a long-only multi-sector fund; tests statistical significance assessment |

## Planned Scenarios

- Alpha vs Environment Attribution (macro regime conditioning)
- Capital vs Risk Concentration (position-level risk decomposition)

## Scoring Dimensions

1. **Attribution Discipline** (35%) - Factor decomposition, residual alpha calculation
2. **Hypothesis Testing** (35%) - Evidence-based conclusions, appropriate skepticism
3. **Contextual Evaluation** (30%) - Skill conditional on environment, intentionality

## Common AI Failure Modes

- Narrative attribution without factor analysis
- Declaring alpha failure without decomposition
- Ignoring environmental context in performance evaluation
- Confusing intentional positioning with accidental exposure
