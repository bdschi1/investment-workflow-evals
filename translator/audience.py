"""Audience profiles and configuration for research translation."""
from __future__ import annotations
from enum import StrEnum
from pydantic import BaseModel, Field


class AudienceProfile(StrEnum):
    RETAIL_INVESTOR = "retail_investor"
    GENERAL_PUBLIC = "general_public"
    FINANCIAL_ADVISOR = "financial_advisor"
    EXECUTIVE_SUMMARY = "executive_summary"


class AudienceConfig(BaseModel):
    """Configuration for target audience translation."""
    profile: AudienceProfile
    max_reading_level: int = Field(
        default=8, description="Flesch-Kincaid grade level target",
    )
    max_jargon_terms: int = Field(
        default=5, description="Max undefined jargon terms allowed",
    )
    max_length_words: int = Field(
        default=500, description="Target word count",
    )
    required_sections: list[str] = Field(default_factory=lambda: [
        "summary", "what_it_means", "key_numbers", "risks", "bottom_line",
    ])
    tone: str = "informative and approachable"


# Pre-built audience configs
AUDIENCE_CONFIGS = {
    AudienceProfile.RETAIL_INVESTOR: AudienceConfig(
        profile=AudienceProfile.RETAIL_INVESTOR,
        max_reading_level=8,
        max_jargon_terms=5,
        max_length_words=500,
        tone="informative and approachable, like a trusted advisor",
    ),
    AudienceProfile.GENERAL_PUBLIC: AudienceConfig(
        profile=AudienceProfile.GENERAL_PUBLIC,
        max_reading_level=6,
        max_jargon_terms=2,
        max_length_words=300,
        tone="simple and clear, like explaining to a friend",
    ),
    AudienceProfile.FINANCIAL_ADVISOR: AudienceConfig(
        profile=AudienceProfile.FINANCIAL_ADVISOR,
        max_reading_level=12,
        max_jargon_terms=15,
        max_length_words=800,
        tone="professional but accessible",
    ),
    AudienceProfile.EXECUTIVE_SUMMARY: AudienceConfig(
        profile=AudienceProfile.EXECUTIVE_SUMMARY,
        max_reading_level=10,
        max_jargon_terms=10,
        max_length_words=200,
        required_sections=["summary", "recommendation", "key_risk"],
        tone="concise and action-oriented",
    ),
}
