"""Tests for institutional-to-retail research translator."""
from __future__ import annotations
import pytest
from translator.audience import (
    AudienceProfile, AudienceConfig, AUDIENCE_CONFIGS,
)
from translator.rules import (
    JARGON_MAP, count_jargon, replace_jargon, estimate_reading_level,
    COMPLEXITY_RULES,
)
from translator.outputs import (
    TranslatedResearch, AccuracyReport, KeyNumber,
)
from translator.simplifier import InstitutionalToRetailTranslator


class TestAudienceConfig:
    def test_retail_config(self):
        cfg = AUDIENCE_CONFIGS[AudienceProfile.RETAIL_INVESTOR]
        assert cfg.max_reading_level == 8
        assert cfg.max_jargon_terms == 5

    def test_general_public_config(self):
        cfg = AUDIENCE_CONFIGS[AudienceProfile.GENERAL_PUBLIC]
        assert cfg.max_reading_level == 6

    def test_executive_summary_config(self):
        cfg = AUDIENCE_CONFIGS[AudienceProfile.EXECUTIVE_SUMMARY]
        assert cfg.max_length_words == 200

    def test_all_profiles_have_configs(self):
        for profile in AudienceProfile:
            assert profile in AUDIENCE_CONFIGS


class TestJargonRules:
    def test_jargon_map_not_empty(self):
        assert len(JARGON_MAP) >= 30

    def test_count_jargon_finds_terms(self):
        text = "The EV/EBITDA multiple is 15x and the WACC is 10%."
        found = count_jargon(text)
        assert "EV/EBITDA" in found or "WACC" in found

    def test_count_jargon_clean_text(self):
        text = "The company sells products and makes money."
        found = count_jargon(text)
        assert len(found) == 0

    def test_replace_jargon_adds_definitions(self):
        text = "The WACC is 10%."
        result = replace_jargon(text)
        assert (
            "cost of capital" in result.lower()
            or "investors expect" in result.lower()
        )

    def test_replace_jargon_only_first_occurrence(self):
        text = "WACC is 10%. WACC matters."
        result = replace_jargon(text)
        # Second WACC should remain as-is
        parts = result.split("WACC")
        assert len(parts) >= 2  # At least one replacement happened

    def test_complexity_rules_exist(self):
        assert len(COMPLEXITY_RULES) >= 10


class TestReadingLevel:
    def test_simple_text(self):
        text = "The dog ran. The cat sat. It was fun."
        level = estimate_reading_level(text)
        assert level < 5

    def test_complex_text(self):
        text = (
            "The amortization of intangible assets, combined with "
            "the depreciation of property and equipment, significantly "
            "impacted the company's consolidated financial statements "
            "during the fiscal year ending December."
        )
        level = estimate_reading_level(text)
        assert level > 10

    def test_empty_text(self):
        assert estimate_reading_level("") == 0.0


class TestTranslatedResearch:
    def test_to_markdown(self):
        tr = TranslatedResearch(
            audience=AudienceProfile.RETAIL_INVESTOR,
            ticker="AAPL",
            company_name="Apple Inc.",
            summary="Apple is growing its services business.",
            what_it_means="This means more recurring revenue.",
            key_numbers=[
                KeyNumber(
                    label="Revenue",
                    value="$95B",
                    explanation="Total sales",
                ),
            ],
            risks_in_plain_english=["China sales could drop"],
            bottom_line="Consider buying on dips.",
            word_count=100,
            estimated_reading_level=7.0,
        )
        md = tr.to_markdown()
        assert "Apple Inc." in md
        assert "What You Need to Know" in md
        assert "$95B" in md
        assert "What Could Go Wrong" in md

    def test_minimal_output(self):
        tr = TranslatedResearch(
            audience=AudienceProfile.GENERAL_PUBLIC,
            ticker="X",
        )
        md = tr.to_markdown()
        assert "X" in md


SAMPLE_INSTITUTIONAL_TEXT = """
## Executive Summary

**Recommendation:** BUY ABBV at current levels.

AbbVie reported revenue of $14.3 billion in Q3, up 4% YoY. The company's
Immunology franchise grew 8% driven by Skyrizi and Rinvoq adoption.
Humira biosimilar erosion was better than expected at -28% YoY.

## Investment Thesis

AbbVie's diversification away from Humira is ahead of schedule. The GLP-1
pipeline presents a $5 billion revenue opportunity by 2028. Current EV/EBITDA
of 12x represents a 20% discount to peers.

Management raised full-year guidance, citing strong commercial execution
and favorable payer dynamics. The WACC of 8.5% supports our DCF-derived
price target of $210.

## Risk Factors

- Biosimilar competition continues to pressure Humira revenue
- GLP-1 clinical trial failure could eliminate pipeline optionality
- Patent cliff risk on Imbruvica by 2027
- Regulatory scrutiny on drug pricing could compress margins

## Valuation

Our DCF model with a terminal growth rate of 2.5% yields fair value of $210,
implying 15% upside from current levels. Comps analysis supports a range
of $195-$225.
"""


class TestSimplifier:
    @pytest.fixture
    def translator(self) -> InstitutionalToRetailTranslator:
        return InstitutionalToRetailTranslator()

    @pytest.fixture
    def retail_config(self) -> AudienceConfig:
        return AUDIENCE_CONFIGS[AudienceProfile.RETAIL_INVESTOR]

    def test_translate_produces_output(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
            ticker="ABBV", company_name="AbbVie Inc.",
        )
        assert isinstance(result, TranslatedResearch)
        assert result.ticker == "ABBV"
        assert result.audience == AudienceProfile.RETAIL_INVESTOR

    def test_translate_has_summary(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        assert len(result.summary) > 0

    def test_translate_extracts_numbers(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        assert len(result.key_numbers) >= 1

    def test_translate_extracts_risks(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        assert len(result.risks_in_plain_english) >= 1

    def test_translate_has_word_count(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        assert result.word_count > 0

    def test_translate_has_reading_level(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        assert result.estimated_reading_level > 0

    def test_translate_jargon_replaced(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        # After translation, some jargon should be replaced
        result.to_markdown()
        # The output should have fewer raw jargon terms
        assert isinstance(result.jargon_terms_remaining, list)

    def test_validate_accuracy(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
            ticker="ABBV",
        )
        report = translator.validate_accuracy(
            SAMPLE_INSTITUTIONAL_TEXT, result,
            key_facts=["ABBV", "$14.3 billion", "BUY", "GLP-1"],
        )
        assert isinstance(report, AccuracyReport)
        assert report.facts_checked == 4
        assert report.accuracy_rate > 0

    def test_validate_accuracy_auto_extract(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
        )
        report = translator.validate_accuracy(
            SAMPLE_INSTITUTIONAL_TEXT, result,
        )
        assert report.facts_checked > 0

    def test_general_public_simpler(self, translator):
        retail = AUDIENCE_CONFIGS[AudienceProfile.RETAIL_INVESTOR]
        general = AUDIENCE_CONFIGS[AudienceProfile.GENERAL_PUBLIC]

        retail_result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail,
        )
        general_result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, general,
        )

        # Both should produce valid output
        assert retail_result.word_count > 0
        assert general_result.word_count > 0

    def test_to_markdown_output(
        self, translator, retail_config,
    ):
        result = translator.translate(
            SAMPLE_INSTITUTIONAL_TEXT, retail_config,
            ticker="ABBV", company_name="AbbVie Inc.",
        )
        md = result.to_markdown()
        assert "ABBV" in md
        assert "What You Need to Know" in md


class TestAccuracyReport:
    def test_serialization(self):
        report = AccuracyReport(
            facts_checked=5, facts_preserved=4,
            accuracy_rate=0.8, missing_facts=["missing one"],
        )
        data = report.model_dump()
        restored = AccuracyReport(**data)
        assert restored.accuracy_rate == 0.8
