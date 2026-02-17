"""Tests for investment memo schemas."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure showcase/schemas is importable
sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "showcase" / "schemas")
)
from memo_schema import (  # noqa: E402
    CatalystEvent,
    ExecutiveSummary,
    InvestmentMemo,
    InvestmentThesis,
    PositionManagement,
    Recommendation,
    RiskAssessment,
    RiskItem,
    RiskLevel,
    ValuationMetric,
)


# -------------------------------------------------------------------
# ExecutiveSummary
# -------------------------------------------------------------------


class TestExecutiveSummary:
    def test_basic(self):
        es = ExecutiveSummary(
            ticker="AAPL",
            company_name="Apple Inc.",
            recommendation=Recommendation.BUY,
            conviction=8.0,
            price_target=225.0,
        )
        assert es.ticker == "AAPL"
        assert es.conviction == 8.0

    def test_conviction_upper_bound(self):
        with pytest.raises(Exception):
            ExecutiveSummary(
                ticker="X",
                company_name="X",
                recommendation=Recommendation.HOLD,
                conviction=15.0,
            )

    def test_conviction_lower_bound(self):
        with pytest.raises(Exception):
            ExecutiveSummary(
                ticker="X",
                company_name="X",
                recommendation=Recommendation.HOLD,
                conviction=-1.0,
            )

    def test_defaults(self):
        es = ExecutiveSummary(
            ticker="MSFT",
            company_name="Microsoft Corp.",
            recommendation=Recommendation.STRONG_BUY,
            conviction=9.0,
        )
        assert es.time_horizon == "12 months"
        assert es.thesis_one_liner == ""
        assert es.price_target is None
        assert es.current_price is None


# -------------------------------------------------------------------
# InvestmentMemo — full integration
# -------------------------------------------------------------------


class TestInvestmentMemo:
    @pytest.fixture
    def sample_memo(self) -> InvestmentMemo:
        return InvestmentMemo(
            executive_summary=ExecutiveSummary(
                ticker="AAPL",
                company_name="Apple Inc.",
                recommendation=Recommendation.BUY,
                conviction=8.0,
                price_target=225.0,
                current_price=195.0,
                thesis_one_liner="Services growth inflecting higher",
            ),
            investment_thesis=InvestmentThesis(
                bull_thesis=(
                    "Apple's services revenue is accelerating "
                    "driven by installed base monetization."
                ),
                supporting_evidence=[
                    "Services grew 14% YoY",
                    "Installed base at 2.2B",
                ],
                catalyst_calendar=[
                    CatalystEvent(
                        date="Q1 2025",
                        event="Earnings",
                        expected_impact="Beat estimates",
                    ),
                ],
                key_metrics=[
                    ValuationMetric(
                        metric="P/E (fwd)",
                        current=28.5,
                        target=30.0,
                        peer_median=25.0,
                    ),
                ],
            ),
            risk_assessment=RiskAssessment(
                overall_risk_level=RiskLevel.MEDIUM,
                bear_thesis="China weakness persists",
                risks=[
                    RiskItem(
                        description="China revenue decline",
                        probability=RiskLevel.MEDIUM,
                        impact=RiskLevel.HIGH,
                        mitigation="Diversified geographic mix",
                    ),
                ],
            ),
            position_management=PositionManagement(
                entry_criteria="On pullback to $190",
                position_size_pct=3.0,
                stop_loss_pct=10.0,
                exit_triggers=[
                    "Services growth decelerates below 10%",
                ],
            ),
            sources=[
                "Apple 10-K 2024",
                "Q4 Earnings Call Transcript",
            ],
        )

    def test_memo_serializes(self, sample_memo):
        data = sample_memo.model_dump()
        assert data["executive_summary"]["ticker"] == "AAPL"

    def test_memo_roundtrip(self, sample_memo):
        data = sample_memo.model_dump()
        restored = InvestmentMemo(**data)
        assert restored.executive_summary.ticker == "AAPL"
        assert restored.executive_summary.conviction == 8.0

    def test_memo_json_roundtrip(self, sample_memo):
        json_str = sample_memo.model_dump_json()
        restored = InvestmentMemo.model_validate_json(json_str)
        assert restored.executive_summary.price_target == 225.0

    def test_to_markdown(self, sample_memo):
        md = sample_memo.to_markdown()
        assert "# AAPL" in md
        assert "Buy" in md
        assert "Services grew" in md
        assert "China revenue" in md
        assert "Sources" in md

    def test_to_markdown_has_tables(self, sample_memo):
        md = sample_memo.to_markdown()
        assert "| Date |" in md  # Catalyst table
        assert "| Risk |" in md  # Risk table
        assert "| Metric |" in md  # Key metrics table

    def test_to_markdown_has_position_mgmt(self, sample_memo):
        md = sample_memo.to_markdown()
        assert "## Position Management" in md
        assert "**Entry:**" in md
        assert "3.0% of portfolio" in md
        assert "**Stop-loss:** 10.0%" in md
        assert "**Exit trigger:**" in md

    def test_to_markdown_has_blockquote(self, sample_memo):
        md = sample_memo.to_markdown()
        assert "> Services growth inflecting higher" in md

    def test_to_markdown_has_conviction(self, sample_memo):
        md = sample_memo.to_markdown()
        assert "8.0/10" in md

    def test_minimal_memo(self):
        memo = InvestmentMemo(
            executive_summary=ExecutiveSummary(
                ticker="X",
                company_name="Test",
                recommendation=Recommendation.HOLD,
                conviction=5.0,
            ),
            investment_thesis=InvestmentThesis(
                bull_thesis="Test thesis",
            ),
            risk_assessment=RiskAssessment(
                overall_risk_level=RiskLevel.LOW,
            ),
        )
        md = memo.to_markdown()
        assert "# X" in md
        assert "Hold" in md
        assert "TBD" in md  # No price target

    def test_minimal_memo_no_position_mgmt_section(self):
        memo = InvestmentMemo(
            executive_summary=ExecutiveSummary(
                ticker="Y",
                company_name="Minimal",
                recommendation=Recommendation.SELL,
                conviction=2.0,
            ),
            investment_thesis=InvestmentThesis(
                bull_thesis="Weak thesis",
            ),
            risk_assessment=RiskAssessment(
                overall_risk_level=RiskLevel.HIGH,
            ),
        )
        md = memo.to_markdown()
        # No position management section when nothing is set
        assert "## Position Management" not in md

    def test_tail_scenarios_render(self):
        memo = InvestmentMemo(
            executive_summary=ExecutiveSummary(
                ticker="Z",
                company_name="Tail Co",
                recommendation=Recommendation.STRONG_SELL,
                conviction=2.0,
            ),
            investment_thesis=InvestmentThesis(
                bull_thesis="Minimal",
            ),
            risk_assessment=RiskAssessment(
                overall_risk_level=RiskLevel.CRITICAL,
                tail_scenarios=[
                    "Complete demand collapse",
                    "Regulatory shutdown",
                ],
            ),
        )
        md = memo.to_markdown()
        assert "**Tail Scenarios:**" in md
        assert "1. Complete demand collapse" in md
        assert "2. Regulatory shutdown" in md


# -------------------------------------------------------------------
# RiskItem
# -------------------------------------------------------------------


class TestRiskItem:
    def test_basic(self):
        r = RiskItem(
            description="FX headwinds",
            probability=RiskLevel.HIGH,
            impact=RiskLevel.MEDIUM,
        )
        assert r.probability == RiskLevel.HIGH

    def test_with_monitoring(self):
        r = RiskItem(
            description="Margin compression",
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            mitigation="Diversified revenue mix",
            monitoring_trigger="Operating margin < 20%",
        )
        assert r.monitoring_trigger == "Operating margin < 20%"


# -------------------------------------------------------------------
# CatalystEvent
# -------------------------------------------------------------------


class TestCatalystEvent:
    def test_basic(self):
        c = CatalystEvent(
            date="Q1 2025",
            event="Earnings",
            expected_impact="Positive",
        )
        assert c.probability == "medium"  # default

    def test_custom_probability(self):
        c = CatalystEvent(
            date="H2 2025",
            event="FDA approval",
            expected_impact="Major upside",
            probability="high",
        )
        assert c.probability == "high"


# -------------------------------------------------------------------
# ValuationMetric
# -------------------------------------------------------------------


class TestValuationMetric:
    def test_all_fields(self):
        v = ValuationMetric(
            metric="EV/EBITDA",
            current=15.2,
            target=18.0,
            peer_median=16.5,
        )
        assert v.current == 15.2

    def test_partial_fields(self):
        v = ValuationMetric(metric="P/E (fwd)")
        assert v.current is None
        assert v.target is None
        assert v.peer_median is None


# -------------------------------------------------------------------
# Recommendation / RiskLevel enums
# -------------------------------------------------------------------


class TestEnums:
    def test_recommendation_values(self):
        assert Recommendation.STRONG_BUY == "strong_buy"
        assert Recommendation.STRONG_SELL == "strong_sell"

    def test_risk_level_values(self):
        assert RiskLevel.LOW == "low"
        assert RiskLevel.CRITICAL == "critical"

    def test_recommendation_display(self):
        r = Recommendation.STRONG_BUY
        display = r.value.replace("_", " ").title()
        assert display == "Strong Buy"
