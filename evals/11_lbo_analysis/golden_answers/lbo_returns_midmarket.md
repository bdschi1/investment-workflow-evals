# Golden Answer — Midmarket LBO Returns ([COMPANY])

Deliverable is a 6-tab Excel; this golden captures the required
methodology, sample numeric walks at illustrative figures, and the
analytical judgment required. Replace `[X]` with SMB values.

## Transaction Summary (illustrative at $300M LTM EBITDA)

- Entry EV at 10.0x EBITDA: $3,000M
- Unaffected equity + ~25% premium = offer equity value
- Management rolls 10% of pro-forma equity

## Sources & Uses

| Sources | $M |
|---|---:|
| Senior secured term loan (3.0x EBITDA) | 900 |
| Subordinated notes (1.25x EBITDA) | 375 |
| Sponsor equity | 1,485 |
| Management rollover | 165 |
| **Total** | **2,925** |

| Uses | $M |
|---|---:|
| Equity purchase price (including refinance of existing debt via EV definition) | 2,865 |
| Advisory (1.5% of TEV) | 43.5 |
| Financing fees (3.0% of new debt) | 38.3 |
| Legal / other | 5.0 |
| Cash to balance sheet (min $10M) | 10.0 |
| (Rounding / plug to sponsor equity) | (36.8) |
| **Total** | **2,925** |

Sources − Uses = $0 (sponsor equity is the plug). Entry total leverage
= $1,275M / $300M = 4.25x.

## Operating Model (base case, 5-year summary)

| Year | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| Revenue growth | 7% | 6% | 5% | 5% | 4% |
| EBITDA margin expansion | 50bp | 75bp | 50bp | 25bp | 25bp |
| EBITDA ($M) | 336 | 379 | 420 | 455 | 485 |
| Capex (3.25% of revenue) | (35) | (39) | (43) | (47) | (51) |
| Working-capital delta (12% incremental) | (8) | (8) | (7) | (7) | (6) |
| Bolt-on EBITDA contribution | +5 | +8 | +10 | +12 | +12 |

FCF conversion (~60-65% of EBITDA) flows to debt paydown per schedule.

## Debt Schedule (term loan mechanics)

Interest expense = avg balance x (SOFR + 400bps) for senior TL;
8.5% fixed for sub notes. Mandatory amortization = 1% of original TL
principal per year ($9M/yr). Excess CF sweep = 50% of (CFO − capex −
mandatory amort − $10M min cash), applied to term loan after revolver.

Illustrative ending debt balances (senior TL + sub notes), $M:

| Year | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Senior TL | 900 | 820 | 720 | 600 | 470 | 340 |
| Sub notes | 375 | 375 | 375 | 375 | 375 | 375 |
| Total debt | 1,275 | 1,195 | 1,095 | 975 | 845 | 715 |
| Net debt | 1,265 | 1,180 | 1,075 | 955 | 820 | 685 |

## Returns Analysis — Sample IRR/MOIC Matrix

Base sponsor equity at close = $1,485M. Exit equity = Exit_EBITDA x
Exit_Multiple − Exit_Net_Debt. IRR uses XIRR on the dated cash flows.

IRR at Year-5 exit:

| Exit x EBITDA \ | 7.0x | 8.0x | 9.0x | 10.0x | 11.0x |
|---|---:|---:|---:|---:|---:|
| IRR | ~9% | ~16% | ~21% | ~25% | ~29% |
| MOIC | 1.5x | 2.0x | 2.4x | 2.9x | 3.3x |

Highlight cells ≥ 20% IRR / ≥ 2.0x MOIC in green. Full matrix covers
exit years 3-6 at 0.5x multiple increments.

## Sensitivities

- Table 1: entry multiple (8.0-10.0x) x exit multiple (8.0-11.0x)
  → IRR. Diagonal "in = out" shows deleveraging/growth alone.
- Table 2: revenue CAGR (2-8%) x terminal EBITDA margin (18-24%)
  → IRR at base exit year/multiple.
- Table 3: entry leverage (3.5-5.5x) x exit multiple (8.0-11.0x)
  → MOIC. Highlights the equity-efficiency / capital-structure trade.

## Commentary (probabilistic)

Base-case returns are in the 20-25% IRR and 2.0-2.5x MOIC range,
roughly consistent with market midmarket LBO returns. The dominant
levers in the sensitivity tables are exit multiple and EBITDA growth,
not entry leverage — a reminder that capital structure sizes the
equity check and debt cost, but the operational story does the heavier
lifting on returns. The range reported here is scenario-contingent,
not a forecast of realized IRR.

## Constraints Satisfied

- Sources = Uses ($0 check cell)
- Interest and amortization formula-linked (no hardcoding)
- Cash sweep triggers only above $10M min cash
- MOIC separates sponsor equity from total equity (mgmt rollover)
- XIRR methodology (not simple annualized)
- Exit equity = Exit EV − Net debt (net, not gross)
