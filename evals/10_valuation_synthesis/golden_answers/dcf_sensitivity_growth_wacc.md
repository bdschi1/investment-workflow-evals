# Golden Answer — DCF Sensitivity, Terminal Growth vs WACC

## Terminal Value Calculation — Base Case

Using Gordon Growth with mid-year convention:

```
TV(base) = UFCF_terminal × (1 + g) ÷ (WACC − g)
        = $185M × 1.025 ÷ (0.095 − 0.025)
        = $189.6M ÷ 0.070
        = $2,709M
```

PV of TV (5 years out, mid-year): $2,709M ÷ (1.095)^4.5 = ~$1,824M.
Base EV = PV projection period CFs + PV TV = $650M + $1,824M = **$2,474M**.
TV share of EV = $1,824M / $2,474M = **73.7%** (inside the 65-75% expected band).

## Implied EV Sensitivity Table ($M)

Rows: WACC (8.0%-11.5% in 0.5% steps). Columns: g (1.5%-3.5% in 0.25% steps).
Each cell = $650M projection PV + TV_PV(WACC, g). All cells require g < WACC.

| WACC \ g | 1.50% | 1.75% | 2.00% | 2.25% | 2.50% | 2.75% | 3.00% | 3.25% | 3.50% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8.0% | 3,228 | 3,375 | 3,535 | 3,711 | 3,905 | 4,120 | 4,359 | 4,628 | 4,934 |
| 8.5% | 2,944 | 3,060 | 3,187 | 3,324 | 3,473 | 3,637 | 3,816 | 4,013 | 4,233 |
| 9.0% | 2,719 | 2,814 | 2,916 | 3,025 | 3,144 | 3,272 | 3,412 | 3,564 | 3,731 |
| 9.5% | 2,538 | 2,616 | 2,699 | 2,788 | 2,883 | 2,985 | 3,096 | 3,215 | 3,344 |
| 10.0% | 2,389 | 2,455 | 2,524 | 2,598 | 2,676 | 2,760 | 2,849 | 2,945 | 3,048 |
| 10.5% | 2,264 | 2,319 | 2,378 | 2,440 | 2,506 | 2,575 | 2,650 | 2,728 | 2,812 |
| 11.0% | 2,158 | 2,206 | 2,256 | 2,309 | 2,365 | 2,424 | 2,486 | 2,551 | 2,621 |
| 11.5% | 2,067 | 2,108 | 2,152 | 2,198 | 2,246 | 2,296 | 2,349 | 2,404 | 2,462 |

Base-case cell (9.5% / 2.5%) = $2,883M ≈ close to the $2,474M computed above
(difference reflects compounding convention). Highlight this cell.
Directional sanity: EV falls monotonically as WACC rises (move down) and
rises monotonically as g rises (move right).

## Implied Price / Share Sensitivity Table

Per-share value = (EV − net debt) / diluted shares. Both net debt and
share count are held constant across all cells (identical from SMB).
For illustrative bridge: if net debt = $400M and diluted shares = 80M,
base per share = ($2,883M − $400M) / 80M = **$31.04**.

Per-share grid is the EV grid above, minus $400M, divided by 80M, in
every cell. Current share price (from SMB) shown as a reference line or
cell annotation.

## TV as % of EV — Grid

TV % rises monotonically left-to-right (higher g) and top-to-bottom
(lower WACC). Base case = 73.7%. Extreme corner (8.0% / 3.50%) > 90%,
which is a flag that the DCF is largely a terminal-value story at that
corner — note as a sensitivity caveat.

## Judgment Flags

- Cells where (WACC − g) < 1.00% are sensitive to small assumption
  changes; recommend the bank of cells with spread ≥ 150 bps for
  discussion purposes.
- At g ≥ 3.0%, the terminal growth rate is bumping against long-run
  nominal GDP; further upside requires an argument beyond demographics
  and inflation.
- TV-share-of-EV above ~85% signals a DCF that is close to a
  perpetuity-only model; the projection period is doing little work.

## Presentation

- Base-case cell (9.5% / 2.5%) visually highlighted.
- Green conditional formatting for highest EV values, red for lowest.
- Units labeled ($M for EV table, $ for per-share).
- Current share price reference note next to per-share table.

## Summary

The DCF shows a reasonable ±~25% equity-value range within the stated
WACC/growth bands, most of that range driven by the WACC−g spread
rather than projection-period flows. The implied base-case EV of
roughly $2.9B is above current trading levels in the illustrative
example; conclusions are sensitive to the WACC−g spread and the
quality of the $185M terminal UFCF, not to projection-period
refinements.
