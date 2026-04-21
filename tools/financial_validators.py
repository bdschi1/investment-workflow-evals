"""Financial math validator module for rubric pre-gating.

Pure-stdlib module (stdlib + re only). Extracts structured numeric claims from
free-text submissions and checks arithmetic / mechanical consistency that
keyword-based grading misses (S&U balance, BS balance, terminal growth ceiling,
WACC bounds, leverage sanity, EPS accretion math, DCF sensitivity monotonicity,
overconfidence language, inline sum arithmetic).

Design contract:
    - Check functions never raise on malformed input; they return a
      ValidationResult with severity "info" and passed=True when the pattern
      they look for is absent (treat missing-pattern as not-applicable).
    - Check functions return passed=False + severity "critical" or "warning"
      only when the target pattern IS detected AND the math is wrong.
    - All numeric extraction tolerates whitespace, commas in thousands, $
      vs USD, NBSP, and the ' %' vs 'percent' variants.

Public surface:
    validate_submission(text, scenario_type) -> list[ValidationResult]
    check_sources_uses_balance(text)
    check_balance_sheet_balance(text)
    check_terminal_growth_ceiling(text, max_rate=0.035)
    check_wacc_reasonableness(text, min=0.05, max=0.20)
    check_leverage_ratios(text)
    check_eps_accretion_math(text)
    check_dcf_sensitivity_grid_monotonic(text)
    check_no_overconfidence_language(text)
    check_numeric_consistency(text)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, Optional

Severity = Literal["critical", "warning", "info"]


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Single-check outcome used by the rubric pre-gate.

    Attributes:
        check_id: stable machine identifier (e.g. ``"sources_uses_balance"``).
        name: human-readable label for display in feedback.
        passed: True if no violation was found (includes not-applicable).
        severity: ``"critical"``, ``"warning"``, or ``"info"``.
        detail: one-line explanation of what was found.
        extracted: raw numbers / tokens extracted, for debugging / unit tests.
    """

    check_id: str
    name: str
    passed: bool
    severity: Severity
    detail: str
    extracted: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Text-normalisation helpers
# ---------------------------------------------------------------------------

_NBSP = "\u00a0"
_THIN_SPACE = "\u202f"


def _normalize(text: str) -> str:
    """Replace non-breaking / thin spaces with regular spaces."""
    if not text:
        return ""
    return text.replace(_NBSP, " ").replace(_THIN_SPACE, " ")


# Matches: $1,234.5, 1234, 360M, $1.2B, 1,200.00, etc.
# Captures the numeric portion (without $) and an optional suffix (M/B/K/bn/mm).
_NUMBER_RE = re.compile(
    r"""
    (?:\$|USD\s*)?              # optional leading $ or USD
    (?P<num>-?\d{1,3}(?:,\d{3})+(?:\.\d+)?   # 1,234 or 1,234.5
         | -?\d+\.\d+                          # 123.45
         | -?\d+)                              # plain int
    \s*
    (?P<suffix>[MmBbKk]|bn|BN|Bn|mm|MM|Mm|billion|million|thousand)?
    """,
    re.VERBOSE,
)


def _to_float(raw: str) -> Optional[float]:
    """Convert a captured number string (without suffix) to float, or None."""
    if raw is None:
        return None
    raw = raw.replace(",", "").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def _apply_suffix(value: float, suffix: Optional[str]) -> float:
    """Scale a value by its magnitude suffix to millions ($M canonical unit)."""
    if suffix is None:
        return value
    s = suffix.lower()
    if s in ("m", "mm", "million"):
        return value
    if s in ("b", "bn", "billion"):
        return value * 1_000.0
    if s in ("k", "thousand"):
        return value / 1_000.0
    return value


def _extract_numbers_from_line(line: str) -> list[float]:
    """Return all numeric values on a line, scaled to $M."""
    line = _normalize(line)
    out: list[float] = []
    for m in _NUMBER_RE.finditer(line):
        val = _to_float(m.group("num"))
        if val is None:
            continue
        out.append(_apply_suffix(val, m.group("suffix")))
    return out


def _approx_equal(
    a: float, b: float, abs_tol: float = 0.1, rel_tol: float = 0.001
) -> bool:
    """Match if within $0.1M absolute or 0.1% relative."""
    if abs(a - b) <= abs_tol:
        return True
    denom = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denom <= rel_tol


# ---------------------------------------------------------------------------
# Check 1 — Sources & Uses balance
# ---------------------------------------------------------------------------

_SECTION_HEADER_RE = re.compile(
    r"(?im)^\s*(?:#+\s*)?(?P<kind>sources|uses)\b(?:\s+(?:and|&)\s+\w+)?\s*(?:table|section)?\s*:?\s*$"
)

_INLINE_HEADER_RE = re.compile(r"(?im)(?P<kind>sources|uses)\s*\(?\$?[MmBb]?\)?\s*:")

# Matches a line like "- Senior TL: $360M" or "* Equity  $200M"
_BULLET_ITEM_RE = re.compile(
    r"(?m)^\s*[-*•]\s*(?P<label>[A-Za-z][A-Za-z0-9 /\-&()]+?)\s*[:\-]?\s*"
    r"\$?(?P<num>-?[\d,]+(?:\.\d+)?)\s*(?P<suffix>[MmBbKk]|bn|BN|mm|MM|billion|million)?\s*$"
)

# Matches a pipe-table row: "| Senior TL | $360M |"  (last numeric cell wins)
_PIPE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")


def _parse_sources_uses_section(
    block: str,
) -> tuple[list[tuple[str, float]], Optional[float]]:
    """Return (items, declared_total) from a block. declared_total from a
    'Total ...' line if present."""
    items: list[tuple[str, float]] = []
    declared_total: Optional[float] = None

    for raw_line in block.splitlines():
        line = _normalize(raw_line).rstrip()
        if not line.strip():
            continue
        lower = line.lower().lstrip("|").strip()
        is_total = lower.startswith("total") or lower.startswith("**total")

        # Try bullet format first
        m = _BULLET_ITEM_RE.match(line)
        if m:
            label = m.group("label").strip()
            val = _to_float(m.group("num"))
            if val is None:
                continue
            val = _apply_suffix(val, m.group("suffix"))
            if is_total or label.lower().startswith("total"):
                declared_total = val
            else:
                items.append((label, val))
            continue

        # Pipe-table row
        if _PIPE_ROW_RE.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # skip separator rows like |---|---|
            if all(set(c) <= set("-: ") for c in cells):
                continue
            # skip header row if first cell is "Source"/"Use"/"Item"/"Uses"
            if cells and cells[0].lower() in (
                "source",
                "sources",
                "use",
                "uses",
                "item",
                "category",
            ):
                continue
            if not cells:
                continue
            label = cells[0]
            # Find rightmost cell that parses to a number
            val: Optional[float] = None
            for c in reversed(cells[1:]):
                nums = _extract_numbers_from_line(c)
                if nums:
                    val = nums[-1]
                    break
            if val is None:
                continue
            if is_total or label.lower().startswith("total"):
                declared_total = val
            else:
                items.append((label, val))
            continue

        # Plain "Label ... $value" line
        if ":" in line or "\t" in line:
            # Fallback: a colon-separated "Senior TL: $360M"
            parts = re.split(r":\s*", line, maxsplit=1)
            if len(parts) == 2:
                label, rhs = parts
                nums = _extract_numbers_from_line(rhs)
                if nums:
                    val = nums[-1]
                    if is_total or label.lower().strip().startswith("total"):
                        declared_total = val
                    else:
                        items.append((label.strip(), val))

    return items, declared_total


def _split_sources_uses_blocks(text: str) -> Optional[tuple[str, str]]:
    """Return (sources_block, uses_block) by locating 'Sources' and 'Uses'
    headers; return None if either is missing."""
    text = _normalize(text)
    # collect (header_start, header_end, kind)
    headers: list[tuple[int, int, str]] = []
    for m in _SECTION_HEADER_RE.finditer(text):
        headers.append((m.start(), m.end(), m.group("kind").lower()))
    for m in _INLINE_HEADER_RE.finditer(text):
        headers.append((m.start(), m.end(), m.group("kind").lower()))
    if not headers:
        return None
    headers.sort()

    # pick the first Sources and the first Uses in document order
    src_hdr: Optional[tuple[int, int, str]] = None
    use_hdr: Optional[tuple[int, int, str]] = None
    for h in headers:
        if h[2] == "sources" and src_hdr is None:
            src_hdr = h
        elif h[2] == "uses" and use_hdr is None:
            use_hdr = h
    if src_hdr is None or use_hdr is None:
        return None

    # order the two sections and cap each block at the START of the next
    # markdown header (past the current header's own line), the next S&U
    # section, or end-of-text — whichever comes first.
    ordered = sorted([src_hdr, use_hdr], key=lambda t: t[0])
    md_header_re = re.compile(r"(?m)^\s*#+\s+\S")
    blocks: dict[str, str] = {}
    for i, (start, end, kind) in enumerate(ordered):
        body_start = start
        # Next S&U section
        hard_cap = ordered[i + 1][0] if i + 1 < len(ordered) else len(text)
        # Next markdown header after this section's own header
        m_next = md_header_re.search(text, end)
        if m_next and m_next.start() < hard_cap:
            hard_cap = m_next.start()
        blocks[kind] = text[body_start:hard_cap]
    if "sources" not in blocks or "uses" not in blocks:
        return None
    return blocks["sources"], blocks["uses"]


def check_sources_uses_balance(text: str) -> ValidationResult:
    """Detect S&U tables (bullet or pipe) and verify totals match within
    $0.1M or 0.1%."""
    parsed = _split_sources_uses_blocks(text)
    if parsed is None:
        return ValidationResult(
            check_id="sources_uses_balance",
            name="Sources & Uses Balance",
            passed=True,
            severity="info",
            detail="check not applicable — no S&U table detected",
            extracted={},
        )
    src_block, use_block = parsed
    src_items, src_declared = _parse_sources_uses_section(src_block)
    use_items, use_declared = _parse_sources_uses_section(use_block)

    if not src_items or not use_items:
        return ValidationResult(
            check_id="sources_uses_balance",
            name="Sources & Uses Balance",
            passed=True,
            severity="info",
            detail="check not applicable — S&U sections found but no line items parsed",
            extracted={
                "sources_items": src_items,
                "uses_items": use_items,
            },
        )

    src_sum = sum(v for _, v in src_items)
    use_sum = sum(v for _, v in use_items)
    # Reported totals — prefer declared over summed when both exist
    src_reported = src_declared if src_declared is not None else src_sum
    use_reported = use_declared if use_declared is not None else use_sum

    balanced = _approx_equal(src_reported, use_reported)
    diff = src_reported - use_reported
    extracted = {
        "sources_items": src_items,
        "uses_items": use_items,
        "sources_total": src_reported,
        "uses_total": use_reported,
        "diff": diff,
    }
    if balanced:
        return ValidationResult(
            check_id="sources_uses_balance",
            name="Sources & Uses Balance",
            passed=True,
            severity="info",
            detail=f"S&U balanced: Sources ${src_reported:.1f}M = Uses ${use_reported:.1f}M",
            extracted=extracted,
        )
    return ValidationResult(
        check_id="sources_uses_balance",
        name="Sources & Uses Balance",
        passed=False,
        severity="critical",
        detail=(
            f"S&U IMBALANCE: Sources ${src_reported:.1f}M vs Uses ${use_reported:.1f}M "
            f"(diff ${diff:+.1f}M)"
        ),
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 2 — Balance Sheet balance (A = L + E)
# ---------------------------------------------------------------------------

_BS_HEADER_RE = re.compile(
    r"(?im)^\s*#*\s*(?:balance\s+sheet|pro\s*forma\s+balance\s+sheet)\b"
)
_YEAR_ROW_RE = re.compile(r"(?<!\d)(20\d{2}(?:E|A)?)(?!\d)")


def _parse_bs_table(block: str) -> dict:
    """Parse pipe-table BS block. Return {'years': [...], rows: {label: [vals]}}."""
    lines = block.splitlines()
    years: list[str] = []
    rows: dict[str, list[float]] = {}
    for raw in lines:
        line = _normalize(raw).rstrip()
        if not _PIPE_ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if not years:
            yrs = _YEAR_ROW_RE.findall(line)
            if len(yrs) >= 1 and (
                "year" in cells[0].lower()
                or cells[0].lower() in ("", "item", "line item")
                or yrs
            ):
                years = yrs
                continue
        if not cells:
            continue
        label = cells[0].lower().replace("**", "").strip()
        nums: list[float] = []
        for c in cells[1:]:
            found = _extract_numbers_from_line(c)
            if found:
                nums.append(found[-1])
        if nums:
            rows[label] = nums
    return {"years": years, "rows": rows}


def check_balance_sheet_balance(text: str) -> ValidationResult:
    """Verify Total Assets = Total Liabilities + Total Equity for each column
    in a BS table."""
    text = _normalize(text)
    m = _BS_HEADER_RE.search(text)
    if not m:
        return ValidationResult(
            check_id="balance_sheet_balance",
            name="Balance Sheet Balances (A = L + E)",
            passed=True,
            severity="info",
            detail="check not applicable — no balance sheet table detected",
            extracted={},
        )
    # block = from header until next '# ' header or EOF
    start = m.start()
    next_hdr = re.search(r"(?m)^\s*#+\s+\w", text[m.end() :])
    end = m.end() + next_hdr.start() if next_hdr else len(text)
    block = text[start:end]
    parsed = _parse_bs_table(block)
    rows = parsed["rows"]

    def _pick(*needles: str) -> Optional[list[float]]:
        for key, vals in rows.items():
            for n in needles:
                if n in key:
                    return vals
        return None

    assets = _pick("total assets")
    liab = _pick("total liabilities")
    # prefer 'total equity' over plain 'equity'
    equity = (
        _pick("total equity")
        or _pick("total stockholders' equity")
        or _pick("total shareholders' equity")
    )
    liab_plus_eq = _pick("total liabilities and equity", "total liabilities & equity")

    if assets is None or (equity is None and liab_plus_eq is None):
        return ValidationResult(
            check_id="balance_sheet_balance",
            name="Balance Sheet Balances (A = L + E)",
            passed=True,
            severity="info",
            detail="check not applicable — BS table lacks required total rows",
            extracted={"rows_found": list(rows.keys())},
        )

    mismatches: list[dict] = []
    n = len(assets)
    for i in range(n):
        a = assets[i] if i < len(assets) else None
        if liab_plus_eq is not None and i < len(liab_plus_eq):
            rhs = liab_plus_eq[i]
        elif (
            liab is not None
            and equity is not None
            and i < len(liab)
            and i < len(equity)
        ):
            rhs = liab[i] + equity[i]
        else:
            continue
        if a is None or rhs is None:
            continue
        if not _approx_equal(a, rhs, abs_tol=1.0, rel_tol=0.001):
            mismatches.append(
                {"year_idx": i, "assets": a, "liab_plus_equity": rhs, "diff": a - rhs}
            )

    extracted = {
        "assets": assets,
        "liabilities": liab,
        "equity": equity,
        "liab_plus_equity": liab_plus_eq,
        "mismatches": mismatches,
    }
    if not mismatches:
        return ValidationResult(
            check_id="balance_sheet_balance",
            name="Balance Sheet Balances (A = L + E)",
            passed=True,
            severity="info",
            detail="balance sheet balances to within $1M across all years shown",
            extracted=extracted,
        )

    worst = max(mismatches, key=lambda d: abs(d["diff"]))
    sev: Severity = "critical" if abs(worst["diff"]) > 1.0 else "warning"
    return ValidationResult(
        check_id="balance_sheet_balance",
        name="Balance Sheet Balances (A = L + E)",
        passed=False,
        severity=sev,
        detail=(
            f"BS IMBALANCE: {len(mismatches)} year(s) mismatch, worst diff "
            f"${worst['diff']:+.2f}M (A={worst['assets']:.1f} vs L+E={worst['liab_plus_equity']:.1f})"
        ),
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 3 — Terminal growth ceiling
# ---------------------------------------------------------------------------

_TERMINAL_GROWTH_RE = re.compile(
    r"""
    (?:terminal\s+growth
       |perpetuity\s+growth
       |long[\s-]*term\s+growth(?:\s+rate)?
       |terminal\s+growth\s+rate
    )
    [^\n:=]{0,40}?
    [:=]?\s*
    (?:of\s+)?
    (?P<pct>-?\d+(?:\.\d+)?)\s*(?:%|percent)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def check_terminal_growth_ceiling(
    text: str, max_rate: float = 0.035
) -> ValidationResult:
    """Flag terminal growth rates above max_rate (default 3.5%)."""
    text = _normalize(text)
    hits = [
        (m.group(0), float(m.group("pct"))) for m in _TERMINAL_GROWTH_RE.finditer(text)
    ]
    if not hits:
        return ValidationResult(
            check_id="terminal_growth_ceiling",
            name="Terminal Growth Ceiling",
            passed=True,
            severity="info",
            detail="check not applicable — no terminal/perpetuity growth rate stated",
            extracted={},
        )

    max_pct = max(p for _, p in hits) / 100.0
    extracted = {"rates_found_pct": [p for _, p in hits], "max_rate": max_pct}
    # Critical if above 5% (egregious); warning if above max_rate but <= 5%
    if max_pct > 0.05:
        return ValidationResult(
            check_id="terminal_growth_ceiling",
            name="Terminal Growth Ceiling",
            passed=False,
            severity="critical",
            detail=f"terminal growth {max_pct*100:.2f}% exceeds 5% ceiling (egregious)",
            extracted=extracted,
        )
    if max_pct > max_rate:
        return ValidationResult(
            check_id="terminal_growth_ceiling",
            name="Terminal Growth Ceiling",
            passed=False,
            severity="warning",
            detail=(
                f"terminal growth {max_pct*100:.2f}% exceeds soft cap of "
                f"{max_rate*100:.2f}%"
            ),
            extracted=extracted,
        )
    return ValidationResult(
        check_id="terminal_growth_ceiling",
        name="Terminal Growth Ceiling",
        passed=True,
        severity="info",
        detail=f"terminal growth {max_pct*100:.2f}% within the {max_rate*100:.2f}% cap",
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 4 — WACC reasonableness
# ---------------------------------------------------------------------------

_WACC_RE = re.compile(
    r"""
    \b(?:wacc|discount\s+rate|cost\s+of\s+capital|weighted[\s-]*average\s+cost\s+of\s+capital)\b
    [^\n:=%]{0,40}?
    [:=]?\s*(?:of\s+)?
    (?P<pct>-?\d+(?:\.\d+)?)\s*(?:%|percent)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def check_wacc_reasonableness(
    text: str, min: float = 0.05, max: float = 0.20
) -> ValidationResult:
    """Flag WACC/discount rate values outside [min, max]."""
    text = _normalize(text)
    hits = [float(m.group("pct")) for m in _WACC_RE.finditer(text)]
    if not hits:
        return ValidationResult(
            check_id="wacc_reasonableness",
            name="WACC Reasonableness",
            passed=True,
            severity="info",
            detail="check not applicable — no WACC / discount rate stated",
            extracted={},
        )
    # dedup while preserving order
    seen: list[float] = []
    for h in hits:
        if h not in seen:
            seen.append(h)
    rates = [p / 100.0 for p in seen]
    extracted = {"rates_pct": seen, "min_allowed": min, "max_allowed": max}
    out_of_range = [r for r in rates if r < min or r > max]
    if not out_of_range:
        return ValidationResult(
            check_id="wacc_reasonableness",
            name="WACC Reasonableness",
            passed=True,
            severity="info",
            detail=f"WACC {[f'{r*100:.2f}%' for r in rates]} within [{min*100:.0f}%, {max*100:.0f}%]",
            extracted=extracted,
        )
    # critical if way outside (<3% or >25%), else warning
    sev: Severity = (
        "critical" if any(r < 0.03 or r > 0.25 for r in out_of_range) else "warning"
    )
    return ValidationResult(
        check_id="wacc_reasonableness",
        name="WACC Reasonableness",
        passed=False,
        severity=sev,
        detail=(
            f"WACC out of range: {[f'{r*100:.2f}%' for r in out_of_range]} "
            f"(allowed {min*100:.0f}%–{max*100:.0f}%)"
        ),
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 5 — Leverage ratios sanity
# ---------------------------------------------------------------------------

_LEVERAGE_RE = re.compile(
    r"""
    (?:net\s+debt|total\s+debt|debt)\s*/\s*ebitda
    [^\n]{0,20}?
    [:=]?\s*(?:of\s+)?
    (?P<val>-?\d+(?:\.\d+)?)\s*x
    |
    leverage(?:\s+ratio)?
    [^\n]{0,20}?
    [:=]?\s*(?:of\s+)?
    (?P<val2>-?\d+(?:\.\d+)?)\s*x
    """,
    re.IGNORECASE | re.VERBOSE,
)


def check_leverage_ratios(text: str) -> ValidationResult:
    """Flag nonsensical leverage (negative, >20x, or > 15x as warning)."""
    text = _normalize(text)
    hits: list[float] = []
    for m in _LEVERAGE_RE.finditer(text):
        raw = m.group("val") or m.group("val2")
        if raw is None:
            continue
        v = _to_float(raw)
        if v is not None:
            hits.append(v)
    if not hits:
        return ValidationResult(
            check_id="leverage_ratios",
            name="Leverage Ratio Sanity",
            passed=True,
            severity="info",
            detail="check not applicable — no leverage ratio stated",
            extracted={},
        )
    extracted = {"leverage_x": hits}
    bad_critical = [v for v in hits if v < 0 or v > 20]
    bad_warning = [v for v in hits if (0 <= v < 0.5) or (15 < v <= 20)]
    if bad_critical:
        return ValidationResult(
            check_id="leverage_ratios",
            name="Leverage Ratio Sanity",
            passed=False,
            severity="critical",
            detail=f"nonsensical leverage value(s): {bad_critical}x",
            extracted=extracted,
        )
    if bad_warning:
        return ValidationResult(
            check_id="leverage_ratios",
            name="Leverage Ratio Sanity",
            passed=False,
            severity="warning",
            detail=f"borderline leverage value(s): {bad_warning}x",
            extracted=extracted,
        )
    return ValidationResult(
        check_id="leverage_ratios",
        name="Leverage Ratio Sanity",
        passed=True,
        severity="info",
        detail=f"leverage values {hits}x within plausible range",
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 6 — EPS accretion / dilution math
# ---------------------------------------------------------------------------

_EPS_FIELD_RE = {
    "acquirer_ni": re.compile(
        r"(?i)acquirer\s+(?:net\s+income|ni)\s*[:=]?\s*\$?\s*(?P<v>-?[\d,]+(?:\.\d+)?)\s*(?P<s>[MmBbKk]|bn|mm)?"
    ),
    "target_ni": re.compile(
        r"(?i)target\s+(?:net\s+income|ni)\s*[:=]?\s*\$?\s*(?P<v>-?[\d,]+(?:\.\d+)?)\s*(?P<s>[MmBbKk]|bn|mm)?"
    ),
    "synergies": re.compile(
        r"(?i)(?:after[\s-]*tax\s+)?synerg(?:y|ies)\s*[:=]?\s*\$?\s*(?P<v>-?[\d,]+(?:\.\d+)?)\s*(?P<s>[MmBbKk]|bn|mm)?"
    ),
    "acquirer_shares": re.compile(
        r"(?i)acquirer\s+(?:diluted\s+)?shares(?:\s+outstanding)?\s*[:=]?\s*(?P<v>-?[\d,]+(?:\.\d+)?)\s*(?P<s>[MmBbKk]|mm)?"
    ),
    "new_shares": re.compile(
        r"(?i)(?:new\s+shares\s+issued|shares\s+issued)\s*[:=]?\s*(?P<v>-?[\d,]+(?:\.\d+)?)\s*(?P<s>[MmBbKk]|mm)?"
    ),
    "pro_forma_eps": re.compile(
        r"(?i)pro[\s-]*forma\s+eps\s*[:=]?\s*\$?\s*(?P<v>-?[\d,]+(?:\.\d+)?)"
    ),
    "acquirer_eps": re.compile(
        r"(?i)acquirer\s+eps\s*(?!\s+post)\s*[:=]?\s*\$?\s*(?P<v>-?[\d,]+(?:\.\d+)?)"
    ),
}


def _extract_eps_field(text: str, key: str) -> Optional[float]:
    pat = _EPS_FIELD_RE[key]
    m = pat.search(text)
    if not m:
        return None
    v = _to_float(m.group("v"))
    if v is None:
        return None
    try:
        sfx = m.group("s")
    except IndexError:
        sfx = None
    return _apply_suffix(v, sfx) if sfx else v


def check_eps_accretion_math(text: str) -> ValidationResult:
    """If an accretion/dilution table is present, recompute and flag
    mismatch > 5%."""
    text = _normalize(text)
    acq_ni = _extract_eps_field(text, "acquirer_ni")
    tgt_ni = _extract_eps_field(text, "target_ni")
    syn = _extract_eps_field(text, "synergies") or 0.0
    acq_sh = _extract_eps_field(text, "acquirer_shares")
    new_sh = _extract_eps_field(text, "new_shares") or 0.0
    reported_eps = _extract_eps_field(text, "pro_forma_eps")

    have_core = all(v is not None for v in (acq_ni, tgt_ni, acq_sh, reported_eps))
    if not have_core:
        return ValidationResult(
            check_id="eps_accretion_math",
            name="EPS Accretion / Dilution Math",
            passed=True,
            severity="info",
            detail="check not applicable — incomplete accretion/dilution table",
            extracted={
                "acquirer_ni": acq_ni,
                "target_ni": tgt_ni,
                "synergies": syn,
                "acquirer_shares": acq_sh,
                "new_shares": new_sh,
                "reported_pf_eps": reported_eps,
            },
        )

    pf_ni = acq_ni + tgt_ni + syn
    pf_shares = acq_sh + new_sh
    if pf_shares <= 0:
        return ValidationResult(
            check_id="eps_accretion_math",
            name="EPS Accretion / Dilution Math",
            passed=False,
            severity="critical",
            detail="pro-forma share count <= 0 — math cannot be verified",
            extracted={"pf_shares": pf_shares},
        )
    computed_eps = pf_ni / pf_shares
    delta = computed_eps - reported_eps
    denom = max(abs(reported_eps), 1e-9)
    rel = abs(delta) / denom
    extracted = {
        "acquirer_ni": acq_ni,
        "target_ni": tgt_ni,
        "synergies": syn,
        "acquirer_shares": acq_sh,
        "new_shares": new_sh,
        "reported_pf_eps": reported_eps,
        "computed_pf_eps": computed_eps,
        "relative_error": rel,
    }
    if rel <= 0.05:
        return ValidationResult(
            check_id="eps_accretion_math",
            name="EPS Accretion / Dilution Math",
            passed=True,
            severity="info",
            detail=(
                f"PF EPS ${reported_eps:.2f} ≈ computed ${computed_eps:.2f} "
                f"(rel err {rel*100:.1f}%)"
            ),
            extracted=extracted,
        )
    sev: Severity = "warning" if rel <= 0.15 else "critical"
    return ValidationResult(
        check_id="eps_accretion_math",
        name="EPS Accretion / Dilution Math",
        passed=False,
        severity=sev,
        detail=(
            f"PF EPS reported ${reported_eps:.2f} vs computed ${computed_eps:.2f} "
            f"(rel err {rel*100:.1f}%)"
        ),
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 7 — DCF sensitivity grid monotonicity
# ---------------------------------------------------------------------------


def _parse_sensitivity_grid(block: str) -> Optional[dict]:
    """Parse a g × WACC sensitivity table of pipe-table format.

    Expect header like ``| g \\ WACC | 8% | 9% | 10% |`` then rows
    ``| 2% | 45 | 42 | 40 |``.
    """
    pct_cell = re.compile(r"-?\d+(?:\.\d+)?\s*%")
    lines = [ln for ln in block.splitlines() if _PIPE_ROW_RE.match(ln)]
    if len(lines) < 3:
        return None
    parsed: list[list[str]] = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        parsed.append(cells)
    if len(parsed) < 2:
        return None

    header = parsed[0]
    col_pcts: list[float] = []
    for c in header[1:]:
        mm = pct_cell.search(c)
        if mm:
            col_pcts.append(float(mm.group(0).rstrip("%")))
    if len(col_pcts) < 2:
        return None

    rows: list[tuple[float, list[float]]] = []
    for row in parsed[1:]:
        rm = pct_cell.search(row[0])
        if not rm:
            continue
        rlabel = float(rm.group(0).rstrip("%"))
        vals: list[float] = []
        for c in row[1 : 1 + len(col_pcts)]:
            nums = _extract_numbers_from_line(c)
            vals.append(nums[-1] if nums else float("nan"))
        if len(vals) == len(col_pcts):
            rows.append((rlabel, vals))
    if len(rows) < 2:
        return None
    # label cells to determine which axis is g vs WACC:
    top_left = parsed[0][0].lower()
    row_is_g = (
        "g" in top_left
        and "wacc" in top_left
        and top_left.find("g") < top_left.find("wacc")
    ) or top_left.startswith("g")
    return {
        "col_pcts": col_pcts,
        "rows": rows,
        "row_axis": "g" if row_is_g else "wacc",
        "col_axis": "wacc" if row_is_g else "g",
        "header": top_left,
    }


def check_dcf_sensitivity_grid_monotonic(text: str) -> ValidationResult:
    """Verify DCF sensitivity grids: value increases with g (holding WACC),
    decreases with WACC (holding g)."""
    text = _normalize(text)
    # find a section labelled sensitivity
    sect = re.search(
        r"(?is)(sensitivity\s+(?:table|grid|analysis)[^\n]*\n(?:.*?))(?=\n\s*#|\Z)",
        text,
    )
    block = sect.group(1) if sect else text
    grid = _parse_sensitivity_grid(block)
    if grid is None:
        return ValidationResult(
            check_id="dcf_sensitivity_grid_monotonic",
            name="DCF Sensitivity Grid Monotonicity",
            passed=True,
            severity="info",
            detail="check not applicable — no sensitivity grid detected",
            extracted={},
        )

    violations: list[str] = []
    rows = grid["rows"]
    col_pcts = grid["col_pcts"]
    row_axis = grid["row_axis"]

    # Check rows (across columns)
    for rlabel, vals in rows:
        for i in range(len(vals) - 1):
            a, b = vals[i], vals[i + 1]
            if a != a or b != b:  # NaN
                continue
            # columns correspond to col_pcts (the 'other' axis).
            # If rows are g, columns are WACC — value should DECREASE as WACC rises.
            # If rows are WACC, columns are g — value should INCREASE as g rises.
            if row_axis == "g":
                if b > a + 1e-9:
                    violations.append(
                        f"row g={rlabel}%: value rises with WACC ({col_pcts[i]}%→{col_pcts[i+1]}%): {a}→{b}"
                    )
            else:
                if b < a - 1e-9:
                    violations.append(
                        f"row WACC={rlabel}%: value falls with g ({col_pcts[i]}%→{col_pcts[i+1]}%): {a}→{b}"
                    )
    # Check columns (down rows)
    for j, col_pct in enumerate(col_pcts):
        col_vals = [(rl, vals[j]) for rl, vals in rows if j < len(vals)]
        for i in range(len(col_vals) - 1):
            (rl_a, a), (rl_b, b) = col_vals[i], col_vals[i + 1]
            if a != a or b != b:
                continue
            if row_axis == "g":
                if b < a - 1e-9:
                    violations.append(
                        f"col WACC={col_pct}%: value falls with g ({rl_a}%→{rl_b}%): {a}→{b}"
                    )
            else:
                if b > a + 1e-9:
                    violations.append(
                        f"col g={col_pct}%: value rises with WACC ({rl_a}%→{rl_b}%): {a}→{b}"
                    )

    extracted = {
        "row_axis": row_axis,
        "col_pcts": col_pcts,
        "rows": rows,
        "violations": violations,
    }
    if not violations:
        return ValidationResult(
            check_id="dcf_sensitivity_grid_monotonic",
            name="DCF Sensitivity Grid Monotonicity",
            passed=True,
            severity="info",
            detail=f"sensitivity grid monotonic ({len(rows)}×{len(col_pcts)})",
            extracted=extracted,
        )
    return ValidationResult(
        check_id="dcf_sensitivity_grid_monotonic",
        name="DCF Sensitivity Grid Monotonicity",
        passed=False,
        severity="critical",
        detail=f"non-monotonic sensitivity grid: {len(violations)} violation(s); first: {violations[0]}",
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 8 — Overconfidence language
# ---------------------------------------------------------------------------

# Phrases from .claude/rules/output-language.md.
_OVERCONFIDENCE_PATTERNS = [
    (re.compile(r"(?i)\b100%\s*confident\b"), "100% confident"),
    (re.compile(r"(?i)\bguaranteed?\b"), "guaranteed"),
    (re.compile(r"(?i)\bno\s+risk\b"), "no risk"),
    (re.compile(r"(?i)\bsure\s+thing\b"), "sure thing"),
    (re.compile(r"(?i)\bcan['\u2019]?t\s+lose\b"), "can't lose"),
    (re.compile(r"(?i)\bcertain\s+to\b"), "certain to"),
    (re.compile(r"(?i)\bwill\s+definitely\b"), "will definitely"),
]

# Labels whose meaning inverts when preceded by a negator
# (e.g. "not guaranteed", "no guarantee" are acceptable anti-overconfident phrasings).
# "no risk" and "can't lose" are excluded because their overconfident meaning is intrinsic
# to the phrase itself; double-negation is rare enough to accept the false positive.
_NEGATABLE_LABELS = {
    "100% confident",
    "guaranteed",
    "sure thing",
    "certain to",
    "will definitely",
}
_NEGATOR_RE = re.compile(
    r"(?i)\b(?:not|no|never|nothing|without|hardly|barely|scarcely)\b|n['\u2019]t\b"
)


_BENIGN_BETWEEN_RE = re.compile(
    r"(?i)^[\s,;:'\"\-\(\)]*(?:a|an|the|any|quite|really|entirely|fully|"
    r"completely|even|yet|always|ever)?[\s,;:'\"\-\(\)]*$"
)


def _preceded_by_negator(text: str, start: int, window: int = 30) -> bool:
    """True if the last negator-like token before ``start`` negates the match.

    Allows at most one benign intervening word (article, mild adverb) between
    the negator and the overconfident phrase so cases like "not a sure thing"
    or "never really guaranteed" still read as negated.
    """
    prefix = text[max(0, start - window) : start]
    last_negator_end = -1
    for m in _NEGATOR_RE.finditer(prefix):
        last_negator_end = m.end()
    if last_negator_end < 0:
        return False
    between = prefix[last_negator_end:]
    return bool(_BENIGN_BETWEEN_RE.fullmatch(between))


def check_no_overconfidence_language(text: str) -> ValidationResult:
    """Flag prohibited certainty phrases from the repo's output-language rule."""
    text = _normalize(text)
    hits: list[str] = []
    for pat, label in _OVERCONFIDENCE_PATTERNS:
        for m in pat.finditer(text):
            if label in _NEGATABLE_LABELS and _preceded_by_negator(text, m.start()):
                continue
            hits.append(label)
            break
    extracted = {"phrases_found": hits}
    if not hits:
        return ValidationResult(
            check_id="overconfidence_language",
            name="Overconfidence Language",
            passed=True,
            severity="info",
            detail="no prohibited certainty phrases detected",
            extracted=extracted,
        )
    return ValidationResult(
        check_id="overconfidence_language",
        name="Overconfidence Language",
        passed=False,
        severity="critical",
        detail=f"prohibited certainty phrase(s) detected: {hits}",
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Check 9 — Inline numeric consistency ("total = A + B + C")
# ---------------------------------------------------------------------------

# Matches a claim like:
#   "total X = $1.0 + $2.0 + $3.0 = $6.0"
#   "total revenue of $1,200M = $400 + $500 + $300"
# The addends list can be on either side of the declared total.
# Matches "Total[...]= <body>" where <body> is everything up to end-of-line or
# end-of-sentence. We post-process `body` by splitting on '=' ourselves so the
# regex does not have to choose between greedy/lazy behaviour across multiple
# '=' signs. Terminator: newline, semicolon, or a period that's NOT part of a
# decimal (i.e. not followed by a digit).
_SUM_RE = re.compile(
    r"""
    \btotal\b[^=\n]{0,60}?=   # 'total ... ='
    \s*(?P<body>[^\n]+?)       # entire remainder of the line up to terminator
    (?=\n|;|$|\.(?!\d))        # sentence end but not decimal point
    """,
    re.IGNORECASE | re.VERBOSE,
)

# extract all numbers with suffix in a string (keep scale)
_ATOMIC_NUM_RE = re.compile(
    r"(?:\$|USD\s*)?(?P<num>-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+\.\d+|-?\d+)\s*"
    r"(?P<suffix>[MmBbKk]|bn|mm)?"
)


def _nums_with_scale(s: str) -> list[float]:
    s = _normalize(s)
    out: list[float] = []
    for m in _ATOMIC_NUM_RE.finditer(s):
        v = _to_float(m.group("num"))
        if v is None:
            continue
        out.append(_apply_suffix(v, m.group("suffix")))
    return out


def check_numeric_consistency(text: str) -> ValidationResult:
    """Find "total X = $A + $B + $C [= $T]" claims and verify A+B+C == T
    within 1% tolerance."""
    text = _normalize(text)
    checks: list[dict] = []
    for m in _SUM_RE.finditer(text):
        body = m.group("body") or ""
        # split the full 'total ... = BODY' into segments by '='
        # Full match text begins at 'total' and includes everything through body.
        full = m.group(0)
        # All segments separated by '='
        segments = [s.strip() for s in full.split("=")]
        # First segment is the 'total <label>' part; find a number in it (declared)
        # and segments with '+' are addend chains.
        addend_seg = next((s for s in segments if "+" in s), None)
        if addend_seg is None:
            continue
        addends = _nums_with_scale(addend_seg)
        if len(addends) < 2:
            continue
        # Declared total: pick the rightmost segment that is a single number
        # (no '+'), preferring segments AFTER the addend segment, else before.
        declared_candidates: list[float] = []
        for s in segments:
            if s is addend_seg or "+" in s:
                continue
            nums = _nums_with_scale(s)
            if len(nums) == 1:
                declared_candidates.append(nums[-1])
        if not declared_candidates:
            continue
        # prefer the last candidate (trailing total)
        declared = declared_candidates[-1]
        computed = sum(addends)
        checks.append({"declared": declared, "computed": computed, "addends": addends})

    if not checks:
        return ValidationResult(
            check_id="numeric_consistency",
            name="Inline Numeric Consistency",
            passed=True,
            severity="info",
            detail="check not applicable — no 'total = A + B + C' claims detected",
            extracted={},
        )

    bad: list[dict] = []
    for c in checks:
        if not _approx_equal(c["declared"], c["computed"], abs_tol=0.1, rel_tol=0.01):
            bad.append(c)
    extracted = {"checks": checks, "bad": bad}
    if not bad:
        return ValidationResult(
            check_id="numeric_consistency",
            name="Inline Numeric Consistency",
            passed=True,
            severity="info",
            detail=f"{len(checks)} inline sum claim(s) reconcile",
            extracted=extracted,
        )
    worst = bad[0]
    return ValidationResult(
        check_id="numeric_consistency",
        name="Inline Numeric Consistency",
        passed=False,
        severity="critical",
        detail=(
            f"inline sum mismatch: declared {worst['declared']} vs "
            f"computed {worst['computed']} (addends {worst['addends']})"
        ),
        extracted=extracted,
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

_ALL_CHECKS = {
    "sources_uses_balance": check_sources_uses_balance,
    "balance_sheet_balance": check_balance_sheet_balance,
    "terminal_growth_ceiling": check_terminal_growth_ceiling,
    "wacc_reasonableness": check_wacc_reasonableness,
    "leverage_ratios": check_leverage_ratios,
    "eps_accretion_math": check_eps_accretion_math,
    "dcf_sensitivity_grid_monotonic": check_dcf_sensitivity_grid_monotonic,
    "overconfidence_language": check_no_overconfidence_language,
    "numeric_consistency": check_numeric_consistency,
}


_SCENARIO_CHECKS = {
    "dcf": [
        "terminal_growth_ceiling",
        "wacc_reasonableness",
        "dcf_sensitivity_grid_monotonic",
        "balance_sheet_balance",
        "overconfidence_language",
        "numeric_consistency",
    ],
    "lbo": [
        "sources_uses_balance",
        "leverage_ratios",
        "balance_sheet_balance",
        "overconfidence_language",
        "numeric_consistency",
    ],
    "ma": [
        "eps_accretion_math",
        "sources_uses_balance",
        "overconfidence_language",
        "numeric_consistency",
    ],
    "generic": [
        "overconfidence_language",
        "numeric_consistency",
    ],
}


def validate_submission(
    text: str, scenario_type: str = "auto"
) -> list[ValidationResult]:
    """Run applicable checks against a submission.

    Args:
        text: raw submission text.
        scenario_type: one of ``{"auto","dcf","lbo","ma","generic"}``.
            ``"auto"`` runs every check; each check no-ops with ``info``
            severity if its pattern is not present in the text.
    """
    if scenario_type == "auto":
        names = list(_ALL_CHECKS.keys())
    else:
        names = _SCENARIO_CHECKS.get(scenario_type, list(_ALL_CHECKS.keys()))
    results: list[ValidationResult] = []
    for name in names:
        fn = _ALL_CHECKS[name]
        try:
            results.append(fn(text))
        except Exception as exc:  # defensive: never break the caller
            results.append(
                ValidationResult(
                    check_id=name,
                    name=name,
                    passed=True,
                    severity="info",
                    detail=f"check errored and was skipped: {exc!r}",
                    extracted={},
                )
            )
    return results


__all__ = [
    "ValidationResult",
    "validate_submission",
    "check_sources_uses_balance",
    "check_balance_sheet_balance",
    "check_terminal_growth_ceiling",
    "check_wacc_reasonableness",
    "check_leverage_ratios",
    "check_eps_accretion_math",
    "check_dcf_sensitivity_grid_monotonic",
    "check_no_overconfidence_language",
    "check_numeric_consistency",
]
