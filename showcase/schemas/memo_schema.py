"""Pydantic schemas for investment research memo sections.

These schemas enable programmatic memo generation, JSON serialization,
and markdown rendering. They map to the template structures in
showcase/templates/ and the agent output schemas in
multi-agent-investment-committee/agents/base.py.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


# -------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------

class Recommendation(StrEnum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# -------------------------------------------------------------------
# Component models
# -------------------------------------------------------------------

class CatalystEvent(BaseModel):
    """A single catalyst event on the 12-month timeline."""

    date: str
    event: str
    expected_impact: str
    probability: str = "medium"


class RiskItem(BaseModel):
    """A single risk with probability, impact, and mitigation."""

    description: str
    probability: RiskLevel
    impact: RiskLevel
    mitigation: str = ""
    monitoring_trigger: str = ""


class ValuationMetric(BaseModel):
    """A single valuation metric with current, target, and peer values."""

    metric: str
    current: float | None = None
    target: float | None = None
    peer_median: float | None = None


# -------------------------------------------------------------------
# Memo sections
# -------------------------------------------------------------------

class ExecutiveSummary(BaseModel):
    """Header and thesis summary for the memo."""

    ticker: str
    company_name: str
    recommendation: Recommendation
    conviction: float = Field(ge=0, le=10)
    price_target: float | None = None
    current_price: float | None = None
    time_horizon: str = "12 months"
    thesis_one_liner: str = ""


class InvestmentThesis(BaseModel):
    """Bull case thesis with supporting evidence and catalysts."""

    bull_thesis: str
    supporting_evidence: list[str] = Field(default_factory=list)
    catalyst_calendar: list[CatalystEvent] = Field(
        default_factory=list,
    )
    key_metrics: list[ValuationMetric] = Field(
        default_factory=list,
    )


class RiskAssessment(BaseModel):
    """Bear case with risk matrix and tail scenarios."""

    overall_risk_level: RiskLevel
    bear_thesis: str = ""
    risks: list[RiskItem] = Field(default_factory=list)
    tail_scenarios: list[str] = Field(default_factory=list)
    worst_case_price: float | None = None


class PositionManagement(BaseModel):
    """Entry, sizing, stop-loss, and exit criteria."""

    entry_criteria: str = ""
    position_size_pct: float | None = None
    stop_loss_pct: float | None = None
    exit_triggers: list[str] = Field(default_factory=list)


# -------------------------------------------------------------------
# Complete memo
# -------------------------------------------------------------------

class InvestmentMemo(BaseModel):
    """Complete investment memo combining all sections."""

    executive_summary: ExecutiveSummary
    investment_thesis: InvestmentThesis
    risk_assessment: RiskAssessment
    position_management: PositionManagement = Field(
        default_factory=PositionManagement,
    )
    sources: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the memo as a markdown string."""
        es = self.executive_summary
        rec_display = (
            es.recommendation.value.replace("_", " ").title()
        )
        pt_display = f"${es.price_target}" if es.price_target else "TBD"

        lines = [
            f"# {es.ticker} — {es.company_name}",
            "",
            (
                f"**Recommendation:** {rec_display} "
                f"| **Conviction:** {es.conviction}/10 "
                f"| **Price Target:** {pt_display}"
            ),
            "",
        ]

        if es.thesis_one_liner:
            lines.extend([f"> {es.thesis_one_liner}", ""])

        # Investment thesis
        lines.extend([
            "## Investment Thesis",
            "",
            self.investment_thesis.bull_thesis,
            "",
        ])
        if self.investment_thesis.supporting_evidence:
            lines.append("**Supporting Evidence:**")
            for i, ev in enumerate(
                self.investment_thesis.supporting_evidence, 1
            ):
                lines.append(f"{i}. {ev}")
            lines.append("")

        # Catalyst calendar
        if self.investment_thesis.catalyst_calendar:
            lines.extend([
                "## Catalyst Calendar",
                "",
                "| Date | Event | Impact | Probability |",
                "|------|-------|--------|------------|",
            ])
            for c in self.investment_thesis.catalyst_calendar:
                lines.append(
                    f"| {c.date} | {c.event} "
                    f"| {c.expected_impact} "
                    f"| {c.probability} |"
                )
            lines.append("")

        # Key metrics
        if self.investment_thesis.key_metrics:
            lines.extend([
                "## Key Metrics",
                "",
                "| Metric | Current | Target | Peer Median |",
                "|--------|---------|--------|-------------|",
            ])
            for m in self.investment_thesis.key_metrics:
                cur = m.current if m.current is not None else ""
                tgt = m.target if m.target is not None else ""
                peer = m.peer_median if m.peer_median is not None else ""
                lines.append(
                    f"| {m.metric} | {cur} | {tgt} | {peer} |"
                )
            lines.append("")

        # Risk assessment
        ra = self.risk_assessment
        lines.extend([
            (
                "## Risk Assessment "
                f"(Overall: {ra.overall_risk_level.value.title()})"
            ),
            "",
        ])
        if ra.bear_thesis:
            lines.extend([
                f"**Bear Thesis:** {ra.bear_thesis}",
                "",
            ])
        if ra.risks:
            lines.extend([
                "| Risk | Probability | Impact | Mitigation |",
                "|------|------------|--------|------------|",
            ])
            for r in ra.risks:
                lines.append(
                    f"| {r.description} "
                    f"| {r.probability.value} "
                    f"| {r.impact.value} "
                    f"| {r.mitigation} |"
                )
            lines.append("")

        if ra.tail_scenarios:
            lines.append("**Tail Scenarios:**")
            for i, s in enumerate(ra.tail_scenarios, 1):
                lines.append(f"{i}. {s}")
            lines.append("")

        # Position management
        pm = self.position_management
        if pm.entry_criteria or pm.position_size_pct is not None:
            lines.extend(["## Position Management", ""])
            if pm.entry_criteria:
                lines.append(f"- **Entry:** {pm.entry_criteria}")
            if pm.position_size_pct is not None:
                lines.append(
                    f"- **Size:** {pm.position_size_pct}% of portfolio"
                )
            if pm.stop_loss_pct is not None:
                lines.append(
                    f"- **Stop-loss:** {pm.stop_loss_pct}%"
                )
            for trigger in pm.exit_triggers:
                lines.append(f"- **Exit trigger:** {trigger}")
            lines.append("")

        # Sources
        if self.sources:
            lines.append("## Sources")
            for i, s in enumerate(self.sources, 1):
                lines.append(f"{i}. {s}")

        return "\n".join(lines)
