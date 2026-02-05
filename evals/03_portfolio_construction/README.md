# Portfolio Construction Module

This module evaluates AI-generated portfolio construction and position sizing recommendations, testing the ability to properly classify, hedge, and size risks.

## Focus Areas

- **Risk Classification** - Correctly identifying market, factor, environmental, and idiosyncratic risks
- **Hedging Logic** - Hedging environmental exposures while preserving alpha
- **Position Sizing** - Using risk-based sizing rather than notional capital
- **Tail Risk Recognition** - Identifying when backward-looking risk measures are inadequate

## Scenarios

### Pharma/Biotech Pair: Hedge the Environment, Size the Alpha
Tests ability to construct a long/short pair that isolates idiosyncratic exposure while hedging environmental risks.

**Key Challenge:** Using volatility-based sizing instead of dollar neutrality; recognizing 3x+ volatility differential between legs.

### Healthcare Services: Low Volatility, High Risk
Tests recognition that trailing volatility can mask forward-looking tail risks (policy, regulatory).

**Key Challenge:** Not relying on historical beta when asymmetric policy risk dominates; considering portfolio-level correlation of policy-exposed names.

## Common AI Failure Modes

- Confusing notional symmetry with risk neutrality
- Using trailing volatility when forward-looking risks dominate
- Ignoring volatility differentials in pair construction
- Treating diversification as immunity to correlated risks
- Over-hedging away intended alpha exposure

## Scoring Dimensions

1. **Risk Classification / Recognition** (35%)
2. **Hedging Logic / Forward-Looking Assessment** (35%)
3. **Sizing Methodology / Portfolio Context** (30%)

## Critical Failures

- Dollar-neutral sizing ignoring volatility differential
- Using historical volatility as primary risk signal for policy-exposed names
- Claiming neutrality while leaving major risks unhedged
