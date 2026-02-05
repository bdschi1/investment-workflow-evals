# Golden Answer: Pharma/Biotech Pair Trade Construction

## Executive Summary

**Trade:** Long MegaPharma (MEGA) / Short Catalyst Biotech (CATB)

**Core Insight:** This is a stock-specific pair, but the two legs have vastly different risk profiles. Equal dollar sizing would leave the portfolio short ~3x more risk than intended. Proper construction requires volatility-adjusted sizing and explicit environmental hedging.

---

## Risk Classification

### Step 1: Identify All Risk Types

| Risk Type | MEGA (Long) | CATB (Short) | Net Exposure |
|-----------|-------------|--------------|--------------|
| **Market (beta)** | 0.7 | 1.8 | Short 1.1 turns of beta |
| **Sector (healthcare)** | High | High | Roughly flat |
| **Factor: Biotech vs Pharma** | Negative | Positive | Short biotech factor |
| **Factor: Duration/rates** | Low (cash generative) | High (cash burning) | Short duration |
| **Idiosyncratic: Valuation** | Undervalued (thesis) | Overvalued (thesis) | Intended exposure |
| **Idiosyncratic: Pipeline** | Diversified | Binary Phase 3 | Intended exposure |

### Step 2: Classify as Environmental vs Idiosyncratic

**Environmental (NOT part of thesis):**
- Beta differential (0.7 vs 1.8)
- Biotech vs pharma factor
- Duration/rate sensitivity
- Sector-wide moves

**Idiosyncratic (IS the thesis):**
- MEGA undervaluation vs sum-of-parts
- MEGA pipeline optionality
- CATB probability of success overpriced
- CATB management credibility issues

---

## Sizing Methodology

### The Problem with Dollar-Neutral Sizing

If we size $10M long MEGA / $10M short CATB:

| Position | Capital | Volatility | Vol Contribution |
|----------|---------|------------|------------------|
| MEGA long | $10M | 18% | $1.8M at 1σ |
| CATB short | $10M | 55% | $5.5M at 1σ |
| **Ratio** | 1:1 | **3.1:1** | |

The short leg contributes **3x more risk** than the long leg. This is not a balanced pair—it's a disguised short biotech bet.

### Volatility-Adjusted Sizing

To equalize risk contribution:

| Target | Calculation | Position Size |
|--------|-------------|---------------|
| Equal vol contribution | Match at $2.5M vol each | |
| MEGA position | $2.5M / 18% | **$13.9M long** |
| CATB position | $2.5M / 55% | **$4.5M short** |

**Ratio: 3.1:1 in dollar terms to achieve 1:1 in risk terms**

### Binary Risk Adjustment

CATB has a Phase 3 readout in 60 days. This is not normally distributed volatility—it's binary:
- Success: stock +40-60%
- Failure: stock -50-70%

Implied volatility around the event is likely 80%+, not 55% trailing. For the event window:

| Adjustment | Rationale |
|------------|-----------|
| Reduce short notional further | Or use options to cap loss |
| Consider put spread instead of short stock | Defined risk on binary |
| Size for max loss, not volatility | ~$4.5M × 70% = $3.2M max loss |

---

## Hedging Framework

### What to Hedge (Environmental)

| Exposure | Hedge Instrument | Rationale |
|----------|------------------|-----------|
| Beta differential | Long SPY or XLV vs short position | Net long 1.1 turns |
| Biotech factor | Long XBI overlay | Pair is structurally short biotech |
| Duration/rates | Consider if significant | Cash-burner short in rising rate environment |

### What NOT to Hedge (Idiosyncratic = Alpha)

| Exposure | Why Keep It |
|----------|-------------|
| MEGA valuation gap | This is the thesis |
| CATB probability mispricing | This is the thesis |
| CATB management issues | Stock-specific, intentional |

### Suggested Hedge Implementation

**Option 1: Beta Adjustment**
- Short additional $3-4M of XLV against the pair
- Brings beta closer to neutral

**Option 2: Accept Sector Exposure**
- If comfortable with healthcare overweight
- Document as intentional sector bet

**Option 3: Hybrid**
- Hedge beta, accept biotech factor exposure
- Reduces market correlation, keeps sector view

---

## Residual Exposure After Hedging

| Risk | Status | Acceptable? |
|------|--------|-------------|
| Market beta | Hedged to ~neutral | ✓ |
| Healthcare sector | Flat (both legs) | ✓ |
| Biotech vs pharma | Short ~$4M notional | Discuss with PM |
| MEGA idiosyncratic | Long | ✓ Intended |
| CATB idiosyncratic | Short | ✓ Intended |

**Explicit residual:** Short biotech factor (~$4M notional). This is the main unhedged environmental exposure. Either:
1. Accept as part of thesis (biotech expensive broadly)
2. Hedge with XBI call or long futures

---

## Position Sizing Summary

| Component | Notional | Risk Contribution |
|-----------|----------|-------------------|
| MEGA long | $13.9M | ~$2.5M at 1σ |
| CATB short | $4.5M | ~$2.5M at 1σ |
| Beta hedge (XLV short) | $3.5M | Reduces beta to neutral |
| **Gross exposure** | $21.9M | |
| **Net exposure** | $5.9M long | |

### As Percent of $500M Portfolio

| Metric | Value |
|--------|-------|
| Gross capital | 4.4% |
| Net capital | 1.2% |
| Risk contribution | ~1.0% of portfolio vol |

---

## Monitoring Framework

### Pre-Event (Before Phase 3)
- Monitor biotech factor exposure
- Track CATB IV for event sizing
- Watch for thesis-changing news on either leg

### At Event
- CATB readout will dominate short-term P&L
- Success: cover portion, reassess thesis
- Failure: take profit, reduce position

### Post-Event
- Re-evaluate pair dynamics
- CATB volatility will collapse post-binary
- May need to resize or restructure

---

## What Could Go Wrong

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| CATB Phase 3 success | Short leg +50%, ~$2.3M loss | Sized for this; long leg provides partial offset |
| Biotech rally | Short biotech factor hurts | Could hedge with XBI calls |
| MEGA disappoints | Long leg down | Diversified pharma, limited single-point risk |
| Correlation spike | Pair moves together | Both healthcare; diversification limited |

---

## Summary: Key Construction Principles

1. **Size on risk, not dollars** → 3.1:1 notional ratio
2. **Hedge environmental, keep idiosyncratic** → Beta hedge, no pipeline hedge
3. **Respect binary events** → Size for max loss, not trailing vol
4. **Document residuals** → Short biotech factor is explicit, accepted exposure
5. **Avoid false neutrality** → Dollar-neutral ≠ risk-neutral

---

**Author:** Expert Analyst
**Date:** December 2024
**Methodology:** Volatility-adjusted sizing with explicit environmental hedging
