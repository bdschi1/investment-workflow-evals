# Golden Answer — Accretion/Dilution, [COMPANY] / HealthServ Analytics

This golden describes the deliverable in the form the rubric grades,
using illustrative figures where SMB placeholders are not resolved.
An actual Excel submission would replace `[X]` with SMB-provided
values; the structure and mechanics below are what must be present.

## 1. Transaction Summary

| Item | Value |
|---|---|
| Target | HealthServ Analytics (private) |
| EV offered | $700M |
| EV / LTM EBITDA | 10.0x ($70M EBITDA) |
| EV / LTM Revenue | 2.0x ($350M revenue) |
| Implied target net income | $42M |
| Target growth | 15% p.a. |
| Intangible amortization | $35M / yr over 10 yrs |
| New-debt rate | 5.5% pre-tax |
| Foregone-interest-on-cash | 4.5% pre-tax |
| Tax rate | [COMPANY] effective rate |

## 2. Pro Forma EPS — All Four Financing Scenarios, Year 1

Formula for each scenario:

```
Pro-forma EPS = (Acquirer NI + Target NI
                 - (cash_used x 4.5%) x (1 - t)
                 - (new_debt x 5.5%) x (1 - t)
                 - $35M x (1 - t)
                 + Synergies_after_tax_phase1)
                / (Acquirer_shares + new_shares_from_stock)
```

Where:
- cash_used = $700M x cash_pct
- new_debt = $700M x new_debt_pct
- new_shares_from_stock = ($700M x stock_pct) / [COMPANY] share price
- Year-1 synergies_after_tax = (0.25 x $25M + 0.00 x $15M) x (1 - t)
  = $6.25M pre-tax, after-tax using acquirer's t

| Scenario | Cash% | Stock% | Debt% | Year-1 EPS vs standalone |
|---|---:|---:|---:|---|
| 100% Cash | 100 | 0 | 0 | Dilutive — foregone interest is the drag; no share dilution offset |
| 50/50 Cash/Stock | 50 | 50 | 0 | Mildly dilutive Year 1 — share count rises but interest drag halves |
| 50/50 Cash/Debt | 50 | 0 | 50 | Neutral-to-dilutive Year 1 — interest expense partially offset by lower foregone interest |
| 1/3 Each | 33 | 34 | 33 | Dilutive Year 1 (balanced drag) |

All scenarios show the deal moving toward accretion in Year 2-3 as
synergies phase in and amortization remains fixed.

## 3. Sensitivity Matrix — Offer Price x Financing Mix

Rows = offer price $600M, $650M, $700M, $750M, $800M ($50M steps).
Columns = each of the 4 financing scenarios. Cells = Year-1
accretion/(dilution) % vs standalone EPS. Directional correctness
required:
- Lower offer price → more accretive (less EV funded)
- Higher stock pct → less interest drag, more share dilution
- Higher debt pct → more interest drag, no share dilution

## 4. Synergy Breakeven per Scenario

For each financing mix, solve for the pre-tax run-rate cost +
revenue synergies at which Year-3 pro forma EPS = standalone EPS.

```
Breakeven_synergies = (foregone_interest_AT + new_debt_interest_AT
                       + intangible_amort_AT
                       - target_NI_AT
                       + dilution_from_new_shares)
                      / (1 - t)
```

Breakeven is highest for 100%-cash (largest interest-income drag) and
lowest for 50/50 cash/stock. Report all four as single-number pre-tax
thresholds.

## 5. 3-Year Pro Forma Walk

| Year | Cost synergy phase | Revenue synergy phase | Notes |
|---|---:|---:|---|
| 1 | 25% | 0% | Deal most dilutive; synergies essentially absent |
| 2 | 75% | 33% | Crossover into accretion likely for debt & stock mixes |
| 3 | 100% | 67% | Solidly accretive across all 4 scenarios at base assumptions |

Target growth of 15% lifts target NI from $42M (Y1) to ~$48M (Y2) to
~$55M (Y3), further aiding accretion.

## Formatting

- Accretive cells rendered green; dilutive in red with parentheses.
- Distinguish assumed inputs (blue font) from calculated values (black).
- Summary page with all 4 scenarios side by side, Year 1/2/3 rows.

## Commentary

The analysis shows the transaction is sensitive to financing mix far
more than to synergy realization — the interest-income drag from cash
use and the $35M annual amortization set a meaningful Year-1 hurdle.
Accretion in Years 2 and 3 relies on (a) synergy phase-in roughly as
planned and (b) target growth of 15% holding. Synergies are an
assumption rather than a result, and the analysis should not be read
as a forecast of realized EPS.
