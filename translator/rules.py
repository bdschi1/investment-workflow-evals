"""Translation rules -- jargon mapping, complexity constraints."""
from __future__ import annotations

# Map institutional jargon to plain English explanations
JARGON_MAP: dict[str, str] = {
    "EV/EBITDA": (
        "a measure of how expensive a company is relative to"
        " its operating profits"
    ),
    "WACC": (
        "the minimum return investors expect to earn"
        " (weighted average cost of capital)"
    ),
    "DCF": (
        "a method that estimates what a company's future cash"
        " flows are worth today"
    ),
    "terminal value": (
        "an estimate of what the company will be worth far"
        " into the future"
    ),
    "alpha": "returns above what the overall market delivers",
    "basis points": (
        "hundredths of a percentage point (100 basis points = 1%)"
    ),
    "PEG ratio": (
        "a measure of whether a stock's price is reasonable"
        " given its growth rate"
    ),
    "free cash flow": (
        "the money a company has left after paying all its"
        " bills and investments"
    ),
    "EBITDA": (
        "operating profit before accounting adjustments"
        " (earnings before interest, taxes, depreciation,"
        " amortization)"
    ),
    "net debt": "total borrowings minus cash on hand",
    "capex": (
        "money spent on equipment, buildings, and other"
        " long-term investments"
    ),
    "margin expansion": (
        "the company is becoming more profitable on each"
        " dollar of sales"
    ),
    "multiple compression": (
        "investors are willing to pay less per dollar of earnings"
    ),
    "catalyst": (
        "an upcoming event that could move the stock price"
    ),
    "conviction": (
        "how confident the analyst is in the recommendation"
    ),
    "secular trend": (
        "a long-term shift that lasts years or decades,"
        " not a short-term cycle"
    ),
    "headwind": (
        "a factor working against the company's performance"
    ),
    "tailwind": "a factor helping the company's performance",
    "installed base": (
        "existing customers who already use the company's products"
    ),
    "TAM": (
        "total addressable market -- the maximum possible"
        " revenue opportunity"
    ),
    "ROIC": (
        "return on invested capital -- how efficiently a"
        " company uses its money"
    ),
    "gross margin": (
        "the percentage of revenue left after direct"
        " production costs"
    ),
    "operating leverage": (
        "as revenue grows, profits grow even faster because"
        " fixed costs are spread thinner"
    ),
    "price target": (
        "the analyst's estimate of what the stock should be worth"
    ),
    "stop-loss": (
        "a pre-set price at which you sell to limit losses"
    ),
    "position sizing": (
        "how much of your portfolio to allocate to this investment"
    ),
    "beta": (
        "how much a stock moves relative to the overall market"
    ),
    "downside risk": (
        "how much money you could lose in a bad scenario"
    ),
    "upside potential": (
        "how much money you could gain in a good scenario"
    ),
    "risk-adjusted return": (
        "the return you earn considering the risks taken"
    ),
    "peer group": (
        "comparable companies used for valuation benchmarks"
    ),
    "consensus estimate": (
        "the average of all analysts' predictions"
    ),
}

# Complexity rules for plain-English translation
COMPLEXITY_RULES: list[str] = [
    "Replace passive voice with active voice where possible",
    "One main idea per sentence",
    "No sentences longer than 25 words",
    "Define any financial term on first use",
    (
        "Use concrete numbers instead of relative terms"
        " (say '$5 billion' not 'significant revenue')"
    ),
    "Lead with the conclusion, then explain why",
    "Use analogies for complex concepts",
    "Avoid acronyms -- spell out or use plain English equivalent",
    (
        "Say 'the company' or use the company name instead of"
        " the ticker symbol"
    ),
    (
        "Round numbers for clarity (say 'about $95 billion'"
        " not '$94,932,000,000')"
    ),
    (
        "Use 'more expensive' / 'cheaper' instead of"
        " 'higher multiple' / 'lower multiple'"
    ),
    (
        "Frame risks as 'what could go wrong' not 'risk factors'"
    ),
]


def count_jargon(text: str) -> list[str]:
    """Find jargon terms present in text that aren't defined."""
    text_lower = text.lower()
    found = []
    for term in JARGON_MAP:
        if term.lower() in text_lower:
            # Check if the definition is also nearby (simple heuristic)
            definition = JARGON_MAP[term].lower()
            # If the first 5 words of the definition appear, it's defined
            def_words = definition.split()[:5]
            if not all(w in text_lower for w in def_words):
                found.append(term)
    return found


def replace_jargon(text: str) -> str:
    """Replace jargon terms with plain English equivalents."""
    result = text
    # Sort by length (longest first) to avoid partial replacements
    for term in sorted(JARGON_MAP.keys(), key=len, reverse=True):
        if term in result:
            replacement = f"{term} ({JARGON_MAP[term]})"
            # Only replace first occurrence
            result = result.replace(term, replacement, 1)
    return result


def estimate_reading_level(text: str) -> float:
    """Estimate Flesch-Kincaid grade level (simplified)."""
    sentences = [
        s.strip()
        for s in text.replace("!", ".").replace("?", ".").split(".")
        if s.strip()
    ]
    words = text.split()
    if not sentences or not words:
        return 0.0

    avg_sentence_length = len(words) / len(sentences)
    # Simplified syllable count: count vowel groups
    syllable_count = 0
    for word in words:
        word = word.lower().strip(".,!?;:'\"()-")
        vowels = "aeiou"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        syllable_count += max(count, 1)

    avg_syllables = syllable_count / max(len(words), 1)

    # Flesch-Kincaid Grade Level formula
    grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables - 15.59
    return max(0.0, grade)
