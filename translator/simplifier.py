"""Heuristic research simplifier -- no LLM required."""
from __future__ import annotations
import logging
import re
from .base import BaseTranslator
from .audience import AudienceConfig, AudienceProfile
from .outputs import TranslatedResearch, AccuracyReport, KeyNumber
from .rules import (
    count_jargon, replace_jargon, estimate_reading_level,
)

logger = logging.getLogger(__name__)


class InstitutionalToRetailTranslator(BaseTranslator):
    """Translate institutional research to retail-friendly format.

    Uses heuristic rules (jargon replacement, sentence simplification,
    structure extraction) -- no LLM API calls required.
    """

    def translate(
        self,
        institutional_text: str,
        audience: AudienceConfig,
        ticker: str = "",
        company_name: str = "",
    ) -> TranslatedResearch:
        """Translate institutional text for target audience."""
        # Extract key components
        summary = self._extract_summary(institutional_text, audience)
        what_it_means = self._extract_thesis(
            institutional_text, audience,
        )
        key_numbers = self._extract_key_numbers(institutional_text)
        risks = self._extract_risks(institutional_text, audience)
        bottom_line = self._extract_bottom_line(
            institutional_text, audience,
        )

        # Apply jargon replacement based on audience
        if audience.profile in (
            AudienceProfile.RETAIL_INVESTOR,
            AudienceProfile.GENERAL_PUBLIC,
        ):
            summary = replace_jargon(summary)
            what_it_means = replace_jargon(what_it_means)
            risks = [replace_jargon(r) for r in risks]
            bottom_line = replace_jargon(bottom_line)

        # Build output
        full_text = " ".join([summary, what_it_means, bottom_line])
        full_text += " ".join(risks)

        return TranslatedResearch(
            source_type="institutional_research",
            audience=audience.profile,
            ticker=ticker,
            company_name=company_name,
            summary=summary,
            what_it_means=what_it_means,
            key_numbers=key_numbers[:5],  # Max 5 key numbers
            risks_in_plain_english=risks[:5],  # Max 5 risks
            bottom_line=bottom_line,
            word_count=len(full_text.split()),
            estimated_reading_level=estimate_reading_level(full_text),
            jargon_terms_remaining=count_jargon(full_text),
        )

    def validate_accuracy(
        self,
        original: str,
        translated: TranslatedResearch,
        key_facts: list[str] | None = None,
    ) -> AccuracyReport:
        """Check that key facts from original survive in translation."""
        if key_facts is None:
            key_facts = self._auto_extract_facts(original)

        translated_text = (
            f"{translated.summary} {translated.what_it_means} "
            f"{translated.bottom_line} "
            + " ".join(translated.risks_in_plain_english)
            + " ".join(kn.value for kn in translated.key_numbers)
        ).lower()

        preserved = 0
        missing = []
        for fact in key_facts:
            # Check if the core content of the fact appears
            fact_words = set(fact.lower().split())
            # A fact is "preserved" if >50% of its words appear
            matches = sum(1 for w in fact_words if w in translated_text)
            if matches / max(len(fact_words), 1) > 0.5:
                preserved += 1
            else:
                missing.append(fact)

        total = len(key_facts) or 1
        return AccuracyReport(
            facts_checked=len(key_facts),
            facts_preserved=preserved,
            accuracy_rate=preserved / total,
            missing_facts=missing,
        )

    # ------------------------------------------------------------------
    # Private extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_summary(
        text: str, audience: AudienceConfig,
    ) -> str:
        """Extract or generate a summary from the first paragraphs."""
        # Look for executive summary section
        patterns = [
            r"(?i)executive\s+summary[:\n]+(.*?)(?:\n\n|\n---)",
            r"(?i)summary[:\n]+(.*?)(?:\n\n|\n---)",
            r"(?i)recommendation[:\s]+(.*?)(?:\n\n|\n---)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Truncate to ~3 sentences
                sentences = re.split(r'[.!?]+', summary)
                sentences = [
                    s.strip() for s in sentences if s.strip()
                ]
                return ". ".join(sentences[:3]) + "."

        # Fallback: use first 2-3 sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [
            s.strip() for s in sentences if len(s.strip()) > 20
        ]
        return ". ".join(sentences[:3]) + "." if sentences else ""

    @staticmethod
    def _extract_thesis(
        text: str, audience: AudienceConfig,
    ) -> str:
        """Extract the investment thesis."""
        patterns = [
            r"(?i)(?:investment\s+)?thesis[:\n]+(.*?)"
            r"(?:\n\n|\n##|\n---)",
            r"(?i)bull\s+case[:\n]+(.*?)(?:\n\n|\n##|\n---)",
            r"(?i)core\s+insight[:\n]+(.*?)(?:\n\n|\n##|\n---)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                thesis = match.group(1).strip()
                sentences = re.split(r'[.!?]+', thesis)
                sentences = [
                    s.strip() for s in sentences if s.strip()
                ]
                return ". ".join(sentences[:3]) + "."
        return ""

    @staticmethod
    def _extract_key_numbers(text: str) -> list[KeyNumber]:
        """Extract key financial numbers from the text."""
        numbers = []

        # Look for revenue
        rev_match = re.search(
            r'(?i)revenue[^.]*?(\$[\d,.]+\s*'
            r'(?:billion|million|B|M))',
            text,
        )
        if rev_match:
            numbers.append(KeyNumber(
                label="Revenue",
                value=rev_match.group(1),
                explanation="Total sales for the period",
            ))

        # Look for growth rate
        growth_match = re.search(
            r'(?i)(?:grew|growth|growing)[^.]*?([\d.]+%)',
            text,
        )
        if growth_match:
            numbers.append(KeyNumber(
                label="Growth Rate",
                value=growth_match.group(1),
                explanation="How fast the company is growing",
            ))

        # Look for price target
        pt_match = re.search(
            r'(?i)(?:price\s+target|fair\s+value|target\s+price)'
            r'[^.]*?(\$[\d,.]+)',
            text,
        )
        if pt_match:
            numbers.append(KeyNumber(
                label="Price Target",
                value=pt_match.group(1),
                explanation=(
                    "What the analyst thinks the stock"
                    " should be worth"
                ),
            ))

        # Look for margin
        margin_match = re.search(
            r'(?i)(?:margin|profitability)[^.]*?([\d.]+%)',
            text,
        )
        if margin_match:
            numbers.append(KeyNumber(
                label="Profit Margin",
                value=margin_match.group(1),
                explanation=(
                    "How much profit the company keeps from"
                    " each dollar of sales"
                ),
            ))

        # Look for P/E or valuation multiple
        pe_match = re.search(r'(?i)P/?E[^.]*?([\d.]+)x', text)
        if pe_match:
            numbers.append(KeyNumber(
                label="P/E Ratio",
                value=f"{pe_match.group(1)}x",
                explanation=(
                    "How much investors pay per dollar of"
                    " earnings (lower may be cheaper)"
                ),
            ))

        return numbers

    @staticmethod
    def _extract_risks(
        text: str, audience: AudienceConfig,
    ) -> list[str]:
        """Extract risk factors and simplify them."""
        risks = []

        # Look for risk section
        risk_match = re.search(
            r'(?i)(?:risk|bear\s+case|what\s+could\s+go\s+wrong)'
            r'[:\s\n]+(.*?)(?:\n##|\n---|\Z)',
            text,
            re.DOTALL,
        )
        if risk_match:
            risk_text = risk_match.group(1)
            # Extract bullet points or numbered items
            items = re.findall(
                r'[-\u2022*]\s*(.+?)(?:\n|$)', risk_text,
            )
            if not items:
                # Try numbered items
                items = re.findall(
                    r'\d+\.\s*(.+?)(?:\n|$)', risk_text,
                )
            if not items:
                # Try sentences
                items = [
                    s.strip()
                    for s in re.split(r'[.!?]+', risk_text)
                    if len(s.strip()) > 20
                ]
            risks = items[:5]

        return risks

    @staticmethod
    def _extract_bottom_line(
        text: str, audience: AudienceConfig,
    ) -> str:
        """Extract or generate bottom line recommendation."""
        patterns = [
            r'(?i)(?:bottom\s+line|conclusion|recommendation)'
            r'[:\n]+(.*?)(?:\n\n|\n##|\n---|\Z)',
            r'(?i)(?:we\s+recommend|our\s+view|overall)'
            r'[^.]*\.(.*?\.)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                bl = match.group(1).strip()
                sentences = re.split(r'[.!?]+', bl)
                sentences = [
                    s.strip() for s in sentences if s.strip()
                ]
                return ". ".join(sentences[:2]) + "."
        return ""

    @staticmethod
    def _auto_extract_facts(text: str) -> list[str]:
        """Auto-extract key facts for accuracy validation."""
        facts = []

        # Extract ticker mentions
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', text)
        if ticker_match:
            facts.append(f"ticker {ticker_match.group(1)}")

        # Extract dollar amounts
        for match in re.finditer(
            r'\$[\d,.]+\s*(?:billion|million|B|M)?', text,
        ):
            facts.append(match.group(0))

        # Extract percentages
        for match in re.finditer(r'[\d.]+%', text):
            facts.append(match.group(0))

        # Extract recommendation direction
        for word in [
            "buy", "sell", "hold", "overweight", "underweight",
            "bullish", "bearish",
        ]:
            if word in text.lower():
                facts.append(f"direction: {word}")
                break

        return facts[:10]  # Cap at 10 facts
