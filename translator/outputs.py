"""Output schemas for translated research."""
from __future__ import annotations
from pydantic import BaseModel, Field
from .audience import AudienceProfile


class KeyNumber(BaseModel):
    """A key financial number with plain English annotation."""
    label: str
    value: str
    explanation: str


class TranslatedResearch(BaseModel):
    """Translated research output for a target audience."""
    source_type: str = ""  # "ic_memo", "dcf_valuation", "earnings_analysis"
    audience: AudienceProfile
    ticker: str = ""
    company_name: str = ""

    # Core sections
    summary: str = ""  # 2-3 sentence overview
    what_it_means: str = ""  # Plain English thesis
    key_numbers: list[KeyNumber] = Field(default_factory=list)
    risks_in_plain_english: list[str] = Field(default_factory=list)
    bottom_line: str = ""  # Action takeaway

    # Quality metrics
    word_count: int = 0
    estimated_reading_level: float = 0.0
    jargon_terms_remaining: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render as consumer-friendly markdown."""
        lines = []
        if self.company_name:
            lines.append(
                f"# {self.company_name} ({self.ticker})"
                " -- What You Need to Know"
            )
        else:
            lines.append(f"# {self.ticker} -- What You Need to Know")
        lines.append("")

        if self.summary:
            lines.extend([self.summary, ""])

        if self.what_it_means:
            lines.extend([
                "## What This Means for You", "",
                self.what_it_means, "",
            ])

        if self.key_numbers:
            lines.extend(["## Key Numbers", ""])
            for kn in self.key_numbers:
                lines.append(
                    f"- **{kn.label}: {kn.value}** -- {kn.explanation}"
                )
            lines.append("")

        if self.risks_in_plain_english:
            lines.extend(["## What Could Go Wrong", ""])
            for risk in self.risks_in_plain_english:
                lines.append(f"- {risk}")
            lines.append("")

        if self.bottom_line:
            lines.extend(["## Bottom Line", "", self.bottom_line, ""])

        lines.extend([
            "---",
            f"*Reading level: Grade {self.estimated_reading_level:.0f}"
            f" | {self.word_count} words"
            f" | Audience:"
            f" {self.audience.value.replace('_', ' ').title()}*",
        ])

        return "\n".join(lines)


class AccuracyReport(BaseModel):
    """Report on whether key facts survived translation."""
    facts_checked: int = 0
    facts_preserved: int = 0
    accuracy_rate: float = 0.0
    missing_facts: list[str] = Field(default_factory=list)
    distorted_facts: list[str] = Field(default_factory=list)
