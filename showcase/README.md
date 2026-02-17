# Investment Research Templates & Examples

Structured templates and worked examples for institutional-quality investment research output. These templates standardize the deliverables produced by the [multi-agent-investment-committee](https://github.com/bdschi1/multi-agent-investment-committee) pipeline and serve as golden-answer reference formats for the evaluation harness in this repo.

---

## Templates

| Template | When to Use | Audience | Typical Length |
|----------|-------------|----------|----------------|
| [Full IC Memo](templates/full_ic_memo.md) | Comprehensive investment committee presentation with bull/bear debate, macro context, and conviction tracking | Investment Committee, Portfolio Managers | 8-12 pages |
| [Equity Pitch Deck](templates/equity_pitch_deck.md) | Structured 10-slide pitch for new position proposals or quarterly reviews | IC meetings, Client presentations | 10 slides (~5-7 pages in markdown) |
| [One-Pager](templates/one_pager.md) | Quick-reference summary for active positions or screening output | Traders, Risk desk, PM daily review | 1 page |
| [Risk Brief](templates/risk_brief.md) | Standalone risk assessment for existing positions or pre-trade risk check | Risk committee, Compliance, PM | 3-5 pages |

## Worked Examples

| Example | Source | Description |
|---------|--------|-------------|
| [Life Sciences Valuation](examples/life_sciences_valuation.md) | `evals/02_dcf_valuation` golden answer | Alpha vs. environment decomposition for a life sciences tools company, demonstrating terminal value discipline and scenario-weighted valuation |

## Programmatic Schema

| File | Description |
|------|-------------|
| [memo_schema.py](schemas/memo_schema.py) | Pydantic models for all memo sections -- enables programmatic memo generation, JSON serialization, and markdown rendering |

Tests live in [`tests/test_memo_schema.py`](../tests/test_memo_schema.py).

---

## Integration with Multi-Agent Investment Committee

These templates map directly to the output schemas defined in [`multi-agent-investment-committee/agents/base.py`](https://github.com/bdschi1/multi-agent-investment-committee/blob/main/agents/base.py):

| Template Section | Source Agent | Pydantic Schema |
|------------------|-------------|-----------------|
| Executive Summary / Thesis | Portfolio Manager | `CommitteeMemo` |
| Investment Thesis / Bull Case | Sector Analyst | `BullCase` |
| Bear Case / Risk Assessment | Risk Manager | `BearCase` |
| Macro Environment | Macro Analyst | `MacroView` |
| Conviction Evolution | All agents | `ReasoningTrace` |

### Data Flow

```
multi-agent-investment-committee
    |
    |  agents produce BullCase, BearCase, MacroView, CommitteeMemo
    |
    v
showcase/schemas/memo_schema.py
    |
    |  InvestmentMemo.to_markdown() renders structured output
    |
    v
showcase/templates/*
    |
    |  Templates define the target format for each deliverable type
    |
    v
evals/*/rubrics/*
    |
    |  Eval rubrics score LLM output against these template structures
    |
    v
evals/*/golden_answers/*
        Golden answers demonstrate what "excellent" looks like
```

### RAG Pipeline Integration

When the multi-agent system uses retrieval-augmented generation (RAG) to pull in filings, transcripts, or market data, the templates define where each data source appears:

- **Sources & Data Quality** section traces every claim to its source document
- **Key Metrics** tables are populated from structured data retrieval
- **Catalyst Calendar** entries come from earnings calendar and event APIs
- **Cross-Asset Signals** are filled from macro data providers (Bloomberg, IBKR, or Yahoo Finance via the adapter layer)

---

## Usage

### As a writing guide

Open any template and fill in the placeholder sections. Each template includes example content showing the expected depth and style.

### As an eval target

Point eval rubrics at these templates to define structural requirements. The rubric can check whether LLM output includes all required sections, tables, and quantitative elements.

### As a programmatic generator

```python
from showcase.schemas.memo_schema import InvestmentMemo, ExecutiveSummary, ...

memo = InvestmentMemo(
    executive_summary=ExecutiveSummary(
        ticker="AAPL",
        company_name="Apple Inc.",
        recommendation=Recommendation.BUY,
        conviction=8.0,
        price_target=225.0,
    ),
    ...
)

# Render to markdown
print(memo.to_markdown())

# Serialize to JSON for storage or API response
print(memo.model_dump_json(indent=2))
```
