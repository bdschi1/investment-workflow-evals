"""Unit tests for ``tools.financial_validators``.

Coverage matrix: each check gets passing / critical / warning / N/A cases
plus one end-to-end ``validate_submission`` test exercising 3+ checks.
"""

import pytest

from tools.financial_validators import (
    ValidationResult,
    check_balance_sheet_balance,
    check_dcf_sensitivity_grid_monotonic,
    check_eps_accretion_math,
    check_leverage_ratios,
    check_no_overconfidence_language,
    check_numeric_consistency,
    check_sources_uses_balance,
    check_terminal_growth_ceiling,
    check_wacc_reasonableness,
    validate_submission,
)

# --------------------------------------------------------------------------
# 1. Sources & Uses balance
# --------------------------------------------------------------------------


def test_sources_uses_bullet_format_passes():
    text = """
## Sources
- Senior TL: $360M
- Subordinated Debt: $100M
- Equity: $200M
- Total Sources: $660M

## Uses
- Purchase of Equity: $600M
- Refinance Debt: $40M
- Transaction Fees: $20M
- Total Uses: $660M
"""
    r = check_sources_uses_balance(text)
    assert isinstance(r, ValidationResult)
    assert r.passed is True
    assert r.severity == "info"
    assert r.extracted["sources_total"] == 660.0
    assert r.extracted["uses_total"] == 660.0


def test_sources_uses_bullet_format_critical_imbalance():
    text = """
## Sources
- Senior TL: $360M
- Equity: $200M
- Total Sources: $560M

## Uses
- Purchase of Equity: $600M
- Transaction Fees: $20M
- Total Uses: $620M
"""
    r = check_sources_uses_balance(text)
    assert r.passed is False
    assert r.severity == "critical"
    assert abs(r.extracted["diff"] - (-60.0)) < 1e-6


def test_sources_uses_pipe_table_format_passes():
    text = """
## Sources
| Source | $M |
|---|---|
| Senior TL | $400M |
| Mezzanine | $150M |
| Sponsor Equity | $250M |
| Total Sources | $800M |

## Uses
| Use | $M |
|---|---|
| Purchase Price | $750M |
| Fees & Expenses | $50M |
| Total Uses | $800M |
"""
    r = check_sources_uses_balance(text)
    assert r.passed is True
    assert r.extracted["sources_total"] == 800.0
    assert r.extracted["uses_total"] == 800.0


def test_sources_uses_not_applicable_when_missing():
    text = "We are analysing a DCF valuation with WACC of 9% and terminal growth of 3%."
    r = check_sources_uses_balance(text)
    assert r.passed is True
    assert r.severity == "info"
    assert "not applicable" in r.detail


def test_sources_uses_within_tolerance():
    # $660.05M vs $660.00M — within $0.1M absolute tolerance
    text = """
## Sources
- Senior TL: $400.05M
- Equity: $260M
- Total Sources: $660.05M

## Uses
- Purchase: $600M
- Fees: $60M
- Total Uses: $660M
"""
    r = check_sources_uses_balance(text)
    assert r.passed is True


# --------------------------------------------------------------------------
# 2. Balance Sheet balances
# --------------------------------------------------------------------------


def test_balance_sheet_balances_passes():
    text = """
## Pro Forma Balance Sheet
| Line Item | 2024 | 2025 |
|---|---|---|
| Cash | 100 | 120 |
| Total Assets | 1,000 | 1,100 |
| Total Liabilities | 700 | 770 |
| Total Equity | 300 | 330 |
"""
    r = check_balance_sheet_balance(text)
    assert r.passed is True
    assert r.severity == "info"


def test_balance_sheet_imbalance_critical():
    text = """
## Balance Sheet
| Line Item | 2024 | 2025 |
|---|---|---|
| Total Assets | 1,000 | 1,100 |
| Total Liabilities | 700 | 770 |
| Total Equity | 250 | 280 |
"""
    r = check_balance_sheet_balance(text)
    assert r.passed is False
    assert r.severity == "critical"
    assert len(r.extracted["mismatches"]) == 2


def test_balance_sheet_not_applicable():
    r = check_balance_sheet_balance("We analysed the DCF with a 10% WACC.")
    assert r.passed is True
    assert r.severity == "info"
    assert "not applicable" in r.detail


def test_balance_sheet_liab_and_equity_combined_row():
    text = """
## Balance Sheet
| Item | 2024 |
|---|---|
| Total Assets | 500 |
| Total Liabilities and Equity | 500 |
"""
    r = check_balance_sheet_balance(text)
    assert r.passed is True


# --------------------------------------------------------------------------
# 3. Terminal growth ceiling
# --------------------------------------------------------------------------


def test_terminal_growth_ok():
    r = check_terminal_growth_ceiling("Terminal growth rate: 3.0%.")
    assert r.passed is True
    assert r.extracted["max_rate"] == 0.03


def test_terminal_growth_warning_zone():
    # 4% — over the 3.5% soft cap but below the 5% critical
    r = check_terminal_growth_ceiling("Perpetuity growth of 4.0%.")
    assert r.passed is False
    assert r.severity == "warning"
    assert r.extracted["max_rate"] == 0.04


def test_terminal_growth_critical_above_five():
    r = check_terminal_growth_ceiling("We assume long-term growth rate: 6.0% forever.")
    assert r.passed is False
    assert r.severity == "critical"


def test_terminal_growth_not_applicable():
    r = check_terminal_growth_ceiling("No terminal value discussion here.")
    assert r.passed is True
    assert r.severity == "info"


# --------------------------------------------------------------------------
# 4. WACC reasonableness
# --------------------------------------------------------------------------


def test_wacc_in_range_passes():
    r = check_wacc_reasonableness("WACC of 9.5% applied in the model.")
    assert r.passed is True
    assert 9.5 in r.extracted["rates_pct"]


def test_wacc_critical_too_low():
    r = check_wacc_reasonableness("Discount rate: 2%.")
    assert r.passed is False
    assert r.severity == "critical"


def test_wacc_warning_borderline():
    # 4% — below 5% min but above 3% critical floor
    r = check_wacc_reasonableness("WACC: 4%.")
    assert r.passed is False
    assert r.severity == "warning"


def test_wacc_not_applicable():
    r = check_wacc_reasonableness("We review the LBO capital structure.")
    assert r.passed is True
    assert r.severity == "info"


# --------------------------------------------------------------------------
# 5. Leverage ratios
# --------------------------------------------------------------------------


def test_leverage_in_range():
    r = check_leverage_ratios("Pro forma net debt/EBITDA: 5.5x")
    assert r.passed is True
    assert 5.5 in r.extracted["leverage_x"]


def test_leverage_warning_borderline():
    # 17x is > 15 but <= 20 — warning
    r = check_leverage_ratios("Total debt/EBITDA of 17.0x post-close")
    assert r.passed is False
    assert r.severity == "warning"


def test_leverage_critical_nonsense():
    r = check_leverage_ratios("Leverage ratio: 25.0x")
    assert r.passed is False
    assert r.severity == "critical"


def test_leverage_not_applicable():
    r = check_leverage_ratios("We modelled revenue at $500M.")
    assert r.passed is True
    assert r.severity == "info"


# --------------------------------------------------------------------------
# 6. EPS accretion / dilution
# --------------------------------------------------------------------------


_EPS_GOOD = """
Accretion/Dilution Summary:
- Acquirer Net Income: $500M
- Target Net Income: $100M
- After-tax synergies: $50M
- Acquirer Shares: 200mm
- New Shares Issued: 30mm
- Pro Forma EPS: $2.83
"""


def test_eps_accretion_ok():
    r = check_eps_accretion_math(_EPS_GOOD)
    assert r.passed is True
    assert r.extracted["relative_error"] < 0.02


def test_eps_accretion_critical_error():
    # computed ~$2.83 but reported $4.00 → ~41% error → critical
    bad = _EPS_GOOD.replace("$2.83", "$4.00")
    r = check_eps_accretion_math(bad)
    assert r.passed is False
    assert r.severity == "critical"


def test_eps_accretion_warning_borderline():
    # computed ~$2.83; reported $3.15 → ~11% error → warning (5%-15%)
    mid = _EPS_GOOD.replace("$2.83", "$3.15")
    r = check_eps_accretion_math(mid)
    assert r.passed is False
    assert r.severity == "warning"


def test_eps_accretion_not_applicable():
    r = check_eps_accretion_math("This LBO analysis has no EPS accretion work.")
    assert r.passed is True
    assert r.severity == "info"


# --------------------------------------------------------------------------
# 7. DCF sensitivity grid monotonicity
# --------------------------------------------------------------------------

_SENS_GOOD = """
## Sensitivity Table

| g \\ WACC | 8% | 9% | 10% |
|---|---|---|---|
| 2% | 48 | 42 | 38 |
| 3% | 52 | 45 | 40 |
| 4% | 58 | 50 | 44 |
"""


def test_sensitivity_grid_monotonic():
    r = check_dcf_sensitivity_grid_monotonic(_SENS_GOOD)
    assert r.passed is True
    assert r.severity == "info"


def test_sensitivity_grid_non_monotonic_row():
    bad = """
## Sensitivity Table

| g \\ WACC | 8% | 9% | 10% |
|---|---|---|---|
| 2% | 48 | 60 | 38 |
| 3% | 52 | 45 | 40 |
"""
    r = check_dcf_sensitivity_grid_monotonic(bad)
    assert r.passed is False
    assert r.severity == "critical"
    assert len(r.extracted["violations"]) >= 1


def test_sensitivity_grid_non_monotonic_column():
    # column should increase as g rises (column axis here is WACC so holding WACC
    # constant, moving down rows (g rises) should INCREASE value).
    bad = """
## Sensitivity Table

| g \\ WACC | 8% | 9% |
|---|---|---|
| 2% | 50 | 45 |
| 3% | 40 | 35 |
"""
    r = check_dcf_sensitivity_grid_monotonic(bad)
    assert r.passed is False
    assert r.severity == "critical"


def test_sensitivity_grid_not_applicable():
    r = check_dcf_sensitivity_grid_monotonic("No sensitivity grid in this memo.")
    assert r.passed is True
    assert r.severity == "info"


# --------------------------------------------------------------------------
# 8. Overconfidence language
# --------------------------------------------------------------------------


def test_overconfidence_clean():
    r = check_no_overconfidence_language(
        "This investment has risks but risk-adjusted returns look attractive."
    )
    assert r.passed is True
    assert r.severity == "info"
    assert r.extracted["phrases_found"] == []


def test_overconfidence_guaranteed():
    r = check_no_overconfidence_language(
        "This position is guaranteed to return 20% annually."
    )
    assert r.passed is False
    assert r.severity == "critical"
    assert "guaranteed" in r.extracted["phrases_found"]


def test_overconfidence_multiple_phrases():
    r = check_no_overconfidence_language(
        "Sure thing — certain to outperform with no risk of loss."
    )
    assert r.passed is False
    assert r.severity == "critical"
    assert "sure thing" in r.extracted["phrases_found"]
    assert "certain to" in r.extracted["phrases_found"]
    assert "no risk" in r.extracted["phrases_found"]


def test_overconfidence_will_definitely():
    r = check_no_overconfidence_language(
        "The stock will definitely double within two years."
    )
    assert r.passed is False
    assert r.severity == "critical"
    assert "will definitely" in r.extracted["phrases_found"]


@pytest.mark.parametrize(
    "text",
    [
        "returns are not guaranteed under this strategy.",
        "There is no guarantee the deal closes on time.",
        "management is never certain to deliver on guidance.",
        "Nothing guaranteed about regulatory outcome.",
        "We are not 100% confident in the synergy estimate.",
        "This outcome isn't guaranteed given macro risk.",
        "It's not a sure thing — scenario-dependent.",
        "Without guaranteed offtake, project IRR drops below hurdle.",
    ],
)
def test_overconfidence_accepts_negated_phrases(text):
    """Phrases preceded by a negator should not trip the overconfidence check."""
    r = check_no_overconfidence_language(text)
    assert (
        r.passed is True
    ), f"Expected pass for negated phrase; got hits={r.extracted['phrases_found']}"
    assert r.extracted["phrases_found"] == []


def test_overconfidence_still_catches_unnegated_after_negated():
    """Negator earlier in the sentence shouldn't shield a later bare overconfident phrase."""
    r = check_no_overconfidence_language(
        "The deal is not guaranteed, but management says it is guaranteed to close."
    )
    assert r.passed is False
    assert "guaranteed" in r.extracted["phrases_found"]


# --------------------------------------------------------------------------
# 9. Inline numeric consistency
# --------------------------------------------------------------------------


def test_numeric_consistency_good_forward():
    r = check_numeric_consistency("Total revenue = $400M + $500M + $300M = $1,200M.")
    assert r.passed is True
    assert r.severity == "info"


def test_numeric_consistency_bad_forward():
    r = check_numeric_consistency("Total equity = $100 + $200 + $300 = $650.")
    assert r.passed is False
    assert r.severity == "critical"
    assert r.extracted["bad"][0]["declared"] == 650.0
    assert r.extracted["bad"][0]["computed"] == 600.0


def test_numeric_consistency_bad_reverse_order():
    r = check_numeric_consistency("Total sources of $7.0B = $1.0B + $2.0B + $3.0B.")
    assert r.passed is False
    assert r.severity == "critical"


def test_numeric_consistency_not_applicable():
    r = check_numeric_consistency("No inline arithmetic in this prose.")
    assert r.passed is True
    assert r.severity == "info"


def test_numeric_consistency_commas_and_units():
    # "$1,234M + $2,000M + $3,000M = $6,234M"
    r = check_numeric_consistency("Total = $1,234M + $2,000M + $3,000M = $6,234M.")
    assert r.passed is True


# --------------------------------------------------------------------------
# End-to-end: validate_submission exercising multiple checks
# --------------------------------------------------------------------------


_LBO_MEMO = """
# LBO: Project Snowflake Dividend Recap Feasibility

## Thesis
We believe the sponsor can pull a modest dividend recap, but returns are not guaranteed.

## Sources
- Senior TL (5.0x): $500M
- Senior Notes: $200M
- Equity Rollover: $100M
- Total Sources: $800M

## Uses
- Repay Existing Debt: $600M
- Dividend to Sponsor: $150M
- Transaction Fees: $50M
- Total Uses: $800M

## Capital Structure
Post-transaction total debt/EBITDA: 6.5x. Interest coverage compresses to 2.1x.

## Balance Sheet Snapshot
| Line Item | 2024 | 2025 |
|---|---|---|
| Total Assets | 1,500 | 1,600 |
| Total Liabilities | 1,200 | 1,250 |
| Total Equity | 300 | 350 |

## Note on Arithmetic
Total fee pool = $20M + $15M + $15M = $50M.
"""


def test_validate_submission_end_to_end_lbo():
    results = validate_submission(_LBO_MEMO, scenario_type="auto")
    by_id = {r.check_id: r for r in results}

    # 1) S&U should balance
    assert by_id["sources_uses_balance"].passed is True
    assert by_id["sources_uses_balance"].extracted["sources_total"] == 800.0

    # 2) BS should balance in 2024 but 2025 has A=1,600 vs L+E=1,600 => balances
    assert by_id["balance_sheet_balance"].passed is True

    # 3) leverage 6.5x is fine
    assert by_id["leverage_ratios"].passed is True

    # 4) overconfidence check clean — "not guaranteed" is a negated (acceptable) phrasing.
    assert by_id["overconfidence_language"].passed is True

    # 5) inline arithmetic check passes (20 + 15 + 15 = 50)
    assert by_id["numeric_consistency"].passed is True

    # 6) at least 3 checks produced a result
    assert len(results) >= 3


def test_validate_submission_scenario_type_lbo_runs_subset():
    results = validate_submission(_LBO_MEMO, scenario_type="lbo")
    ids = {r.check_id for r in results}
    assert "sources_uses_balance" in ids
    assert "leverage_ratios" in ids
    assert "overconfidence_language" in ids
    # EPS accretion (M&A-specific) should NOT be in the LBO subset
    assert "eps_accretion_math" not in ids


def test_validate_submission_returns_info_for_missing_patterns():
    text = "This is a minimal qualitative memo with no tables or numbers."
    results = validate_submission(text, scenario_type="auto")
    # Every result should be passed=True / info / 'not applicable' or clean
    assert all(r.passed for r in results)
    # At least one check explicitly said "not applicable"
    assert any("not applicable" in r.detail for r in results)
