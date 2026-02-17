# Risk Brief: {{TICKER}} -- {{COMPANY_NAME}}

*Prepared {{DATE}} | Risk Score: {{RISK_SCORE}}/10*

---

## 1. Risk Summary

| | |
|---|---|
| **Overall Risk Rating** | {{LOW / MEDIUM / HIGH / CRITICAL}} |
| **Risk Score** | {{RISK_SCORE}}/10 |
| **Key Risk Count** | {{N}} identified risks ({{CRITICAL_COUNT}} critical, {{HIGH_COUNT}} high) |
| **Recommendation** | {{AVOID / UNDERWEIGHT / HEDGE / ACTIVE SHORT / MONITOR}} |

### Assessment

[2-3 sentences summarizing the risk posture. What is the dominant risk theme? Is risk concentrated in one area or distributed across multiple dimensions? How does this compare to the sector average?]

*Example: Risk is concentrated in valuation mechanics and balance sheet leverage rather than fundamental business deterioration. The 94x trailing P/E creates a mathematical inevitability of compression that dominates all other risk factors. Sector peers carry median risk scores of 5.5/10 vs this name at 8.2/10.*

---

## 2. Risk Matrix

| # | Risk | Probability | Impact | Severity | Mitigation |
|---|------|-------------|--------|----------|------------|
| 1 | [Growth deceleration in key product line] | High | High | Critical | [Position sizing cap + quarterly growth monitoring] |
| 2 | [Multiple compression from current elevated levels] | High | High | Critical | [Stop-loss at -15% + technical level monitoring] |
| 3 | [Regulatory pricing pressure on core franchise] | Medium | High | High | [Scenario analysis + hedge with sector put spread] |
| 4 | [Balance sheet leverage limiting strategic flexibility] | Medium | Medium | Medium | [Coverage ratio monitoring + credit spread tracking] |
| 5 | [Pipeline concentration risk / binary outcomes] | Low | High | Medium | [Position sizing reflects optionality risk] |
| 6 | [FX translation headwinds on international revenue] | Medium | Low | Low | [Natural hedge through geographic diversification] |

### Severity Scoring

- **Critical** (High probability + High impact): Requires immediate position sizing action
- **High** (Medium/High in either dimension): Requires active monitoring with defined triggers
- **Medium**: Acknowledged in position sizing but not thesis-breaking
- **Low**: Background risk, monitored quarterly

---

## 3. Causal Chain Analysis

For each of the top 3 risks, map the chain of consequences through 1st, 2nd, and 3rd order effects.

### Risk 1: {{TOP_RISK_NAME}}

```
TRIGGER: [Specific observable event -- e.g., "Skyrizi quarterly growth drops below 25%"]
    |
    v
1st ORDER: [Direct, immediate consequence]
    Example: Analyst estimate revisions downward by 5-8% for FY+1
    |
    v
2nd ORDER: [Consequence of the 1st order effect]
    Example: Institutional rotation out of the name as post-patent-cliff
    growth narrative breaks; 15-20% of float turns over in 30 days
    |
    v
3rd ORDER: [Amplification / cascade / feedback loop]
    Example: Options market gamma unwinding amplifies the decline,
    triggering technical breakdown below key support and retail
    panic selling -- total drawdown 25-35% from trigger point
```

### Risk 2: {{SECOND_RISK_NAME}}

```
TRIGGER: [Specific observable event]
    |
    v
1st ORDER: [Direct consequence with magnitude]
    |
    v
2nd ORDER: [Downstream effect with transmission mechanism]
    |
    v
3rd ORDER: [Amplification or feedback loop with estimated magnitude]
```

### Risk 3: {{THIRD_RISK_NAME}}

```
TRIGGER: [Specific observable event]
    |
    v
1st ORDER: [Direct consequence with magnitude]
    |
    v
2nd ORDER: [Downstream effect with transmission mechanism]
    |
    v
3rd ORDER: [Amplification or feedback loop with estimated magnitude]
```

---

## 4. Tail Risk Scenarios

Extreme downside scenarios that are unlikely but would cause outsized losses. These inform position sizing limits and hedging strategy.

### Scenario A: {{TAIL_SCENARIO_1_NAME}}

| | |
|---|---|
| **Probability** | {{PROB_A}}% |
| **Trigger** | [What specific event or combination of events causes this scenario] |
| **Mechanism** | [How the trigger leads to outsized losses -- the causal pathway] |
| **Price Impact** | -{{DRAWDOWN_A}}% (${{TAIL_PRICE_A}}) |
| **Portfolio Impact** | -{{PORT_IMPACT_A}} bps (at current sizing) |
| **Recovery Timeline** | [How long until the position could recover, if ever] |

*Example: Simultaneous pipeline failure + Medicare pricing expansion + credit downgrade. Probability 5-10%. Stock to $120 (-45%). Recovery requires 18+ months of execution to rebuild credibility.*

### Scenario B: {{TAIL_SCENARIO_2_NAME}}

| | |
|---|---|
| **Probability** | {{PROB_B}}% |
| **Trigger** | [Event or combination] |
| **Mechanism** | [Causal pathway to loss] |
| **Price Impact** | -{{DRAWDOWN_B}}% (${{TAIL_PRICE_B}}) |
| **Portfolio Impact** | -{{PORT_IMPACT_B}} bps |
| **Recovery Timeline** | [Timeline estimate] |

### Scenario C: {{TAIL_SCENARIO_3_NAME}} (Systemic)

| | |
|---|---|
| **Probability** | {{PROB_C}}% |
| **Trigger** | [Market-wide or sector-wide shock] |
| **Mechanism** | [How systemic stress specifically impacts this name more/less than peers] |
| **Price Impact** | -{{DRAWDOWN_C}}% (${{TAIL_PRICE_C}}) |
| **Portfolio Impact** | -{{PORT_IMPACT_C}} bps |
| **Correlation Note** | [Does this tail risk correlate with other portfolio positions?] |

---

## 5. Risk Monitoring Triggers

Specific data points and thresholds that signal risk is escalating. Each trigger has a defined escalation action.

| Trigger | Metric | Current | Yellow (Watch) | Orange (Act) | Red (Exit) |
|---------|--------|---------|----------------|--------------|------------|
| Growth | [Key revenue segment growth rate] | {{CURRENT_GROWTH}}% | <{{YELLOW_GROWTH}}% | <{{ORANGE_GROWTH}}% | <{{RED_GROWTH}}% |
| Margins | [Operating or EBITDA margin] | {{CURRENT_MARGIN}}% | <{{YELLOW_MARGIN}}% | <{{ORANGE_MARGIN}}% | <{{RED_MARGIN}}% |
| Leverage | [Net debt / EBITDA] | {{CURRENT_LEV}}x | >{{YELLOW_LEV}}x | >{{ORANGE_LEV}}x | >{{RED_LEV}}x |
| Valuation | [Forward P/E or EV/EBITDA] | {{CURRENT_VAL}}x | >{{YELLOW_VAL}}x | >{{ORANGE_VAL}}x | >{{RED_VAL}}x |
| Technical | [Price relative to key support] | ${{CURRENT_TECH}} | <${{YELLOW_TECH}} | <${{ORANGE_TECH}} | <${{RED_TECH}} |
| Sentiment | [Analyst revision breadth] | {{CURRENT_SENT}} | <{{YELLOW_SENT}} | <{{ORANGE_SENT}} | <{{RED_SENT}} |

### Escalation Protocol

- **Yellow**: Increase monitoring frequency to weekly; prepare contingency reduction plan
- **Orange**: Reduce position by 50%; activate hedge overlay; notify PM
- **Red**: Exit position; execute hedge; post-mortem within 5 business days

### Monitoring Frequency

| Data Point | Frequency | Source |
|------------|-----------|--------|
| Price / technicals | Daily | Market data feed |
| Earnings estimates | Weekly | Consensus tracker |
| Credit spreads | Weekly | Bloomberg / TRACE |
| Regulatory developments | As-available | News alerts, SEC filings |
| Competitive positioning | Quarterly | Earnings calls, industry reports |

---

## 6. Hedging Recommendations

### Position-Level Hedges

| Strategy | Cost | Protection Level | When to Implement |
|----------|------|-----------------|-------------------|
| [Put spread: buy ${{STRIKE_1}} put / sell ${{STRIKE_2}} put, {{EXPIRY}}] | {{COST_1}}% of notional | Protects {{PROTECTION_1}}% of downside below ${{STRIKE_1}} | Immediately / on Orange trigger |
| [Collar: sell ${{CALL_STRIKE}} call / buy ${{PUT_STRIKE}} put] | Net {{COST_2}} | Caps upside at ${{CALL_STRIKE}}, floors at ${{PUT_STRIKE}} | If conviction drops below 5/10 |
| [Pair trade: long {{HEDGE_TICKER}} as sector-neutral hedge] | Spread carry {{COST_3}}/yr | Removes sector beta, isolates idiosyncratic risk | If sector risk dominates company risk |

### Portfolio-Level Hedges

| Strategy | Purpose | Size |
|----------|---------|------|
| [Sector ETF put -- e.g., XLV puts for healthcare exposure] | Hedge sector-wide regulatory risk | {{SECTOR_HEDGE_SIZE}}% of sector exposure |
| [Duration hedge -- e.g., TLT puts if rate-sensitive] | Hedge discount rate risk for long-duration cash flows | {{RATE_HEDGE_SIZE}}% of rate-sensitive positions |
| [VIX call spread] | Tail risk protection for correlated drawdown scenarios | {{VOL_HEDGE_SIZE}}% of portfolio |

### Hedge Effectiveness Check

[1-2 sentences: Do the hedges actually protect against the identified risks? Are there gap risks where the hedge fails? What residual risk remains after hedging?]

---

*Prepared by Risk Management | Next review: {{NEXT_REVIEW_DATE}} | Not financial advice*
