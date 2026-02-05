"""
Grading engine for evaluating AI outputs against rubrics.

This module provides automated and semi-automated grading of AI-generated
investment analysis outputs using structured rubrics.

Usage:
    python -m tools.grading_engine grade --submission output.md --rubric evals/01_equity_thesis/rubrics/standard.yaml
"""

import argparse
import re
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class GradingResult:
    """Result of grading a submission."""
    dimension_scores: dict[str, float]
    critical_failures: list[str]
    detailed_feedback: dict[str, str]
    overall_score: float
    passed: bool


class GradingEngine:
    """
    Engine for grading AI outputs against evaluation rubrics.

    The grading engine applies structured rubrics to assess the quality
    of AI-generated investment analysis. It supports:

    - Dimension-based scoring (factual accuracy, analytical rigor, etc.)
    - Critical failure detection (hallucinations, missing risks, etc.)
    - Heuristic-based automated scoring
    - Integration with LLM-based grading (optional)
    """

    def __init__(self, rubric: dict):
        """
        Initialize with a rubric definition.

        Args:
            rubric: Dictionary containing rubric configuration with:
                - dimensions: List of scoring dimensions
                - critical_failures: List of critical failure conditions
                - pass_threshold: Minimum score to pass
        """
        self.rubric = rubric
        self.dimensions = rubric.get("dimensions", [])
        self.critical_failures = rubric.get("critical_failures", [])
        self.pass_threshold = rubric.get("pass_threshold", 70)

    def grade(
        self,
        ai_output: str,
        scenario: dict,
        use_llm: bool = False,
    ) -> tuple[dict, list, dict]:
        """
        Grade an AI output against the scenario and rubric.

        Args:
            ai_output: The AI-generated response to evaluate
            scenario: The scenario definition for context
            use_llm: Whether to use LLM-based grading (more accurate but slower)

        Returns:
            Tuple of (dimension_scores, critical_failures, detailed_feedback)
        """
        # Check for critical failures first
        critical_failures = self._check_critical_failures(ai_output, scenario)

        # Score each dimension
        dimension_scores = {}
        detailed_feedback = {}

        for dimension in self.dimensions:
            dim_id = dimension["id"]
            score, feedback = self._score_dimension(
                ai_output, scenario, dimension, use_llm
            )
            dimension_scores[dim_id] = score
            detailed_feedback[dim_id] = feedback

        return dimension_scores, critical_failures, detailed_feedback

    def _check_critical_failures(
        self,
        ai_output: str,
        scenario: dict,
    ) -> list[str]:
        """Check for critical failure conditions."""
        failures = []

        # Check for hallucinated data (mentions data that doesn't exist in scenario)
        if self._detect_hallucination(ai_output, scenario):
            failures.append("Potential hallucinated data detected")

        # Check for missing risk section
        if not self._has_risk_section(ai_output):
            failures.append("Missing or inadequate risk assessment section")

        # Check for forward-looking guarantees
        if self._has_guarantee_language(ai_output):
            failures.append("Contains forward-looking guarantees")

        # Check scenario-specific critical failures
        scenario_critical = scenario.get("evaluation_criteria", {}).get("critical_failures", [])
        for critical in scenario_critical:
            if self._check_scenario_critical_failure(ai_output, critical):
                failures.append(f"Scenario critical failure: {critical}")

        return failures

    def _detect_hallucination(self, ai_output: str, scenario: dict) -> bool:
        """
        Attempt to detect hallucinated data.

        This is a heuristic check - looks for specific patterns that
        suggest fabricated information.
        """
        # Look for very specific numbers without citation
        # Pattern: specific revenue/earnings figures not in scenario
        key_facts = scenario.get("key_facts", [])
        fact_values = []
        for fact in key_facts:
            # Extract any numbers from the facts
            numbers = re.findall(r'\$[\d,.]+[BMK]?|\d+\.?\d*%|\d{4}', fact.get("fact", ""))
            fact_values.extend(numbers)

        # Check for specific financial figures in output
        output_figures = re.findall(r'\$[\d,.]+[BMK]?', ai_output)

        # If output has many specific figures not in scenario, flag as potential hallucination
        # This is imperfect but catches obvious cases
        # Note: For portfolio construction/sizing/attribution scenarios, calculated figures are expected

        # Check if this is a calculation-heavy document type
        calculation_context_patterns = [
            r'(?i)(position|sizing|notional|volatility.adjusted|risk.contribution)',
            r'(?i)(factor.{0,20}decomposition|attribution)',
            r'(?i)(hedge|hedging).{0,20}(instrument|framework)',
            r'(?i)(terminal|dcf|valuation).{0,20}(value|framework)',
        ]
        has_calculation_context = any(
            re.search(p, ai_output) for p in calculation_context_patterns
        )

        # Skip hallucination check entirely for calculation-heavy documents
        # These legitimately produce derived figures not in the source scenario
        if has_calculation_context:
            return False

        unmatched_count = 0
        for fig in output_figures[:10]:  # Check first 10
            if not any(fig in str(fv) for fv in fact_values):
                unmatched_count += 1

        # More than 50% unmatched is suspicious
        return unmatched_count > 5

    def _has_risk_section(self, ai_output: str) -> bool:
        """Check if output has adequate risk discussion."""
        risk_patterns = [
            r"(?i)## ?risks?",
            r"(?i)### ?key risks?",
            r"(?i)risk assessment",
            r"(?i)what could go wrong",
            r"(?i)downside",
            r"(?i)what.{0,20}wrong",
            r"(?i)residual.{0,20}exposure",
            r"(?i)unhedged",
            r"(?i)factor.{0,20}drag",
            r"(?i)critical.{0,20}failure",
            r"(?i)common.{0,20}errors",
        ]

        for pattern in risk_patterns:
            if re.search(pattern, ai_output):
                # Also check that there's content after the header
                match = re.search(pattern, ai_output)
                if match:
                    after_header = ai_output[match.end():match.end() + 200]
                    # Should have at least 50 chars of risk discussion
                    if len(after_header.strip()) > 50:
                        return True

        return False

    def _has_guarantee_language(self, ai_output: str) -> bool:
        """Check for inappropriate guarantee language."""
        guarantee_patterns = [
            r"(?i)guaranteed",
            r"(?i)will definitely",
            r"(?i)certain to",
            r"(?i)cannot fail",
            r"(?i)100% chance",
            r"(?i)risk.free",
        ]

        for pattern in guarantee_patterns:
            if re.search(pattern, ai_output):
                return True

        return False

    def _check_scenario_critical_failure(
        self,
        ai_output: str,
        critical_failure: str,
    ) -> bool:
        """Check for scenario-specific critical failure."""
        # Convert description to patterns
        lower_failure = critical_failure.lower()

        if "no probability estimate" in lower_failure:
            # Check for probability language
            prob_patterns = [r'\d+%', r'probability', r'likelihood', r'chance']
            has_probability = any(re.search(p, ai_output, re.I) for p in prob_patterns)
            return not has_probability

        if "ignores binary" in lower_failure or "binary nature" in lower_failure:
            # Check for scenario analysis language indicating awareness of binary outcomes
            scenario_patterns = [
                r'if.*succeed', r'if.*fail', r'success.*scenario', r'failure.*scenario',
                r'bull.*case', r'bear.*case', r'base.*case',
                r'upside.*downside', r'asymmetric',
                r'binary', r'catalyst',
                r'probability.*success', r'probability.*fail',
                r'\d+%.*probability', r'\d+%.*chance',
            ]
            has_scenarios = any(re.search(p, ai_output, re.I) for p in scenario_patterns)
            return not has_scenarios

        return False

    def _score_dimension(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
        use_llm: bool,
    ) -> tuple[float, str]:
        """
        Score a single dimension.

        Args:
            ai_output: The AI response
            scenario: Scenario definition
            dimension: Dimension definition from rubric
            use_llm: Whether to use LLM grading

        Returns:
            Tuple of (score, feedback)
        """
        dim_id = dimension["id"]

        if use_llm:
            return self._score_with_llm(ai_output, scenario, dimension)

        # Heuristic scoring based on dimension
        if dim_id == "factual_accuracy":
            return self._score_factual_accuracy(ai_output, scenario, dimension)
        elif dim_id == "analytical_rigor":
            return self._score_analytical_rigor(ai_output, scenario, dimension)
        elif dim_id == "risk_assessment":
            return self._score_risk_assessment(ai_output, scenario, dimension)
        elif dim_id == "evidence_quality":
            return self._score_evidence_quality(ai_output, scenario, dimension)
        elif dim_id == "completeness":
            return self._score_completeness(ai_output, scenario, dimension)
        # New dimensions for DCF, Portfolio Construction, Risk Attribution
        elif dim_id == "alpha_environment":
            return self._score_alpha_environment(ai_output, scenario, dimension)
        elif dim_id == "risk_treatment":
            return self._score_risk_treatment(ai_output, scenario, dimension)
        elif dim_id == "terminal_value":
            return self._score_terminal_value(ai_output, scenario, dimension)
        elif dim_id == "risk_classification":
            return self._score_risk_classification(ai_output, scenario, dimension)
        elif dim_id == "hedging_logic":
            return self._score_hedging_logic(ai_output, scenario, dimension)
        elif dim_id == "sizing_methodology":
            return self._score_sizing_methodology(ai_output, scenario, dimension)
        elif dim_id == "attribution_discipline":
            return self._score_attribution_discipline(ai_output, scenario, dimension)
        elif dim_id == "hypothesis_testing":
            return self._score_hypothesis_testing(ai_output, scenario, dimension)
        elif dim_id == "contextual_evaluation":
            return self._score_contextual_evaluation(ai_output, scenario, dimension)
        elif dim_id == "cyclical_structural":
            return self._score_cyclical_structural(ai_output, scenario, dimension)
        elif dim_id == "risk_placement":
            return self._score_risk_placement(ai_output, scenario, dimension)
        elif dim_id == "uncertainty_judgment":
            return self._score_uncertainty_judgment(ai_output, scenario, dimension)
        else:
            # Default scoring
            return 70.0, "Default score applied"

    def _score_factual_accuracy(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score factual accuracy dimension."""
        score = 70.0  # Start with baseline
        feedback_parts = []

        # Check for citations
        citation_patterns = [
            r'10-[KQ]',
            r'Q[1-4]\s*20\d{2}',
            r'\(source:',
            r'according to',
            r'per the',
        ]
        citation_count = sum(
            len(re.findall(p, ai_output, re.I))
            for p in citation_patterns
        )

        if citation_count >= 5:
            score += 10
            feedback_parts.append("Good citation density")
        elif citation_count >= 2:
            score += 5
            feedback_parts.append("Adequate citations present")
        else:
            score -= 10
            feedback_parts.append("Insufficient citations")

        # Check for key facts from scenario
        key_facts = scenario.get("key_facts", [])
        facts_found = 0
        for fact_obj in key_facts:
            fact = fact_obj.get("fact", "")
            # Extract key terms and check if present
            if fact_obj.get("importance") == "critical":
                key_terms = fact.split()[:5]  # First 5 words
                if any(term.lower() in ai_output.lower() for term in key_terms if len(term) > 4):
                    facts_found += 1

        if facts_found >= 3:
            score += 10
            feedback_parts.append("Key facts addressed")
        elif facts_found >= 1:
            score += 5
            feedback_parts.append("Some key facts addressed")

        # Cap score
        score = min(100.0, max(0.0, score))

        return score, "; ".join(feedback_parts) if feedback_parts else "Standard factual accuracy"

    def _score_analytical_rigor(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score analytical rigor dimension."""
        score = 70.0
        feedback_parts = []

        # Check for scenario analysis
        scenario_keywords = ["bull case", "bear case", "base case", "upside", "downside", "scenario"]
        scenario_count = sum(
            1 for kw in scenario_keywords
            if kw in ai_output.lower()
        )

        if scenario_count >= 3:
            score += 15
            feedback_parts.append("Good scenario analysis present")
        elif scenario_count >= 1:
            score += 5
            feedback_parts.append("Some scenario consideration")
        else:
            score -= 10
            feedback_parts.append("Limited scenario analysis")

        # Check for assumption transparency
        assumption_keywords = ["assuming", "assumption", "we assume", "estimate", "projected"]
        assumption_count = sum(
            len(re.findall(kw, ai_output, re.I))
            for kw in assumption_keywords
        )

        if assumption_count >= 5:
            score += 10
            feedback_parts.append("Assumptions are explicit")
        elif assumption_count >= 2:
            score += 5
            feedback_parts.append("Some assumptions stated")

        # Check for logical structure
        structure_patterns = ["therefore", "thus", "because", "as a result", "consequently"]
        structure_count = sum(
            len(re.findall(p, ai_output, re.I))
            for p in structure_patterns
        )

        if structure_count >= 3:
            score += 5
            feedback_parts.append("Good logical flow")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard analytical rigor"

    def _score_risk_assessment(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score risk assessment dimension."""
        score = 60.0
        feedback_parts = []

        # Count distinct risks mentioned
        risk_section_match = re.search(r'(?i)(##.*risk|risk.*:)(.*?)(?=##|\Z)', ai_output, re.DOTALL)
        if risk_section_match:
            risk_section = risk_section_match.group(2)
            # Count bullet points or numbered items
            risk_items = len(re.findall(r'[-•\*]|\d+\.', risk_section))

            if risk_items >= 5:
                score += 20
                feedback_parts.append(f"Comprehensive risk list ({risk_items}+ risks)")
            elif risk_items >= 3:
                score += 10
                feedback_parts.append(f"Adequate risk coverage ({risk_items} risks)")
            else:
                feedback_parts.append("Limited risk identification")
        else:
            score -= 15
            feedback_parts.append("No clear risk section")

        # Check for probability/impact assessment
        prob_impact_patterns = [
            r"(?i)probability",
            r"(?i)likelihood",
            r"(?i)impact",
            r"(?i)severity",
            r"\d+%.*risk",
            r"(?i)(high|medium|low)\s*(probability|impact|risk)",
        ]

        has_assessment = any(
            re.search(p, ai_output)
            for p in prob_impact_patterns
        )

        if has_assessment:
            score += 15
            feedback_parts.append("Includes probability/impact assessment")

        # Check for mitigation discussion
        if re.search(r"(?i)mitigat|hedge|protect", ai_output):
            score += 5
            feedback_parts.append("Discusses risk mitigation")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard risk assessment"

    def _score_evidence_quality(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score evidence quality dimension."""
        score = 70.0
        feedback_parts = []

        # Check for specific source citations
        specific_source_patterns = [
            r'10-K',
            r'10-Q',
            r'8-K',
            r'earnings call',
            r'transcript',
            r'investor presentation',
            r'Bloomberg',
            r'FactSet',
        ]

        source_count = sum(
            len(re.findall(p, ai_output, re.I))
            for p in specific_source_patterns
        )

        if source_count >= 5:
            score += 15
            feedback_parts.append("Excellent source citations")
        elif source_count >= 2:
            score += 10
            feedback_parts.append("Good source references")
        else:
            score -= 5
            feedback_parts.append("Limited source citations")

        # Check for shown calculations
        calc_patterns = [r'=', r'\$\d+.*[x×\*]', r'EPS.*\$', r'P/E.*\d+']
        has_calculations = any(re.search(p, ai_output) for p in calc_patterns)

        if has_calculations:
            score += 10
            feedback_parts.append("Includes shown calculations")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard evidence quality"

    def _score_completeness(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score completeness dimension."""
        score = 60.0
        feedback_parts = []

        # Check for required sections
        required_sections = {
            "thesis": ["thesis", "investment case", "recommendation"],
            "valuation": ["valuation", "price target", "fair value"],
            "risks": ["risk", "downside", "bear case"],
            "catalyst": ["catalyst", "trigger", "timeline", "event"],
            "position": ["position", "sizing", "allocation", "portfolio"],
        }

        sections_found = []
        for section, keywords in required_sections.items():
            if any(kw in ai_output.lower() for kw in keywords):
                sections_found.append(section)

        coverage = len(sections_found) / len(required_sections)

        if coverage >= 0.9:
            score += 25
            feedback_parts.append("All major sections covered")
        elif coverage >= 0.7:
            score += 15
            feedback_parts.append("Most sections covered")
        elif coverage >= 0.5:
            score += 5
            feedback_parts.append("Some sections missing")
        else:
            score -= 15
            missing = set(required_sections.keys()) - set(sections_found)
            feedback_parts.append(f"Missing sections: {', '.join(missing)}")

        # Check for balanced presentation
        has_bull = any(kw in ai_output.lower() for kw in ["bull", "upside", "positive"])
        has_bear = any(kw in ai_output.lower() for kw in ["bear", "downside", "risk", "concern"])

        if has_bull and has_bear:
            score += 10
            feedback_parts.append("Balanced bull/bear presentation")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard completeness"

    # === DCF VALUATION DIMENSIONS ===

    def _score_alpha_environment(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score alpha vs environment separation in valuation."""
        score = 50.0
        feedback_parts = []

        # Check for explicit separation of alpha vs environment
        separation_patterns = [
            r"(?i)alpha.{0,30}(vs|versus|from|and).{0,30}environment",
            r"(?i)company.specific.{0,30}(vs|versus|from).{0,30}(market|sector|macro)",
            r"(?i)idiosyncratic.{0,30}(vs|versus|from).{0,30}(systematic|factor)",
            r"(?i)durable.{0,30}(vs|versus|from).{0,30}(cyclical|temporary)",
            r"(?i)environmental.{0,30}tailwind",
            r"(?i)structural.{0,30}(vs|versus|from).{0,30}cyclical",
        ]

        separation_count = sum(1 for p in separation_patterns if re.search(p, ai_output))
        if separation_count >= 2:
            score += 25
            feedback_parts.append("Strong alpha/environment separation")
        elif separation_count >= 1:
            score += 15
            feedback_parts.append("Some alpha/environment distinction")
        else:
            score -= 10
            feedback_parts.append("No alpha/environment separation")

        # Check for quantification of drivers
        quantification_patterns = [
            r"\d+%?\s*(of|from)\s*(growth|outperformance|return)",
            r"(?i)(contributed|drove|explained).{0,30}\d+%",
            r"(?i)\d+.{0,5}%\s*(was|came from|attributable)",
        ]

        has_quantification = any(re.search(p, ai_output) for p in quantification_patterns)
        if has_quantification:
            score += 15
            feedback_parts.append("Quantifies driver contributions")

        # Check for avoiding environmental extrapolation
        extrapolation_warning_patterns = [
            r"(?i)cannot.{0,20}extrapolate",
            r"(?i)not.{0,15}sustainable",
            r"(?i)temporary.{0,15}(tailwind|boost|benefit)",
            r"(?i)normalize",
            r"(?i)revert.{0,15}mean",
        ]

        has_extrapolation_awareness = any(re.search(p, ai_output) for p in extrapolation_warning_patterns)
        if has_extrapolation_awareness:
            score += 10
            feedback_parts.append("Warns against environmental extrapolation")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard alpha/environment analysis"

    def _score_risk_treatment(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score risk treatment in valuation."""
        score = 50.0
        feedback_parts = []

        # Check for scenario analysis
        scenario_patterns = [
            r"(?i)bull.{0,10}case",
            r"(?i)bear.{0,10}case",
            r"(?i)base.{0,10}case",
            r"(?i)scenario.{0,20}analysis",
            r"(?i)sensitivity",
            r"(?i)probability.weighted",
        ]

        scenario_count = sum(1 for p in scenario_patterns if re.search(p, ai_output))
        if scenario_count >= 3:
            score += 20
            feedback_parts.append("Comprehensive scenario analysis")
        elif scenario_count >= 2:
            score += 10
            feedback_parts.append("Includes scenario analysis")

        # Check for explicit uncertainty acknowledgment
        uncertainty_patterns = [
            r"(?i)uncertainty",
            r"(?i)not.{0,10}hedged",
            r"(?i)residual.{0,10}risk",
            r"(?i)what.{0,15}wrong",
            r"(?i)unhedged",
        ]

        uncertainty_count = sum(1 for p in uncertainty_patterns if re.search(p, ai_output))
        if uncertainty_count >= 2:
            score += 15
            feedback_parts.append("Explicit uncertainty acknowledgment")
        elif uncertainty_count >= 1:
            score += 5
            feedback_parts.append("Some uncertainty discussion")

        # Check for probability assignments
        if re.search(r"\d+%\s*(probability|chance|likelihood)", ai_output, re.I):
            score += 15
            feedback_parts.append("Probability-weighted scenarios")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard risk treatment"

    def _score_terminal_value(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score terminal value discipline in DCF."""
        score = 50.0
        feedback_parts = []

        # Check for terminal growth discussion
        terminal_patterns = [
            r"(?i)terminal.{0,15}(growth|value|rate)",
            r"(?i)perpetuity",
            r"(?i)exit.{0,10}multiple",
            r"(?i)long.term.{0,10}growth",
        ]

        has_terminal = any(re.search(p, ai_output) for p in terminal_patterns)
        if has_terminal:
            score += 15
            feedback_parts.append("Addresses terminal value")

        # Check for GDP/inflation anchoring
        gdp_patterns = [
            r"(?i)(at|near|around).{0,10}GDP",
            r"(?i)nominal.{0,10}GDP",
            r"(?i)inflation.{0,10}plus",
            r"(?i)(2|3|4)%\s*terminal",
            r"(?i)cannot.{0,20}perpetuity",
        ]

        has_gdp_anchor = any(re.search(p, ai_output) for p in gdp_patterns)
        if has_gdp_anchor:
            score += 20
            feedback_parts.append("Terminal growth anchored appropriately")
        else:
            feedback_parts.append("Terminal growth may lack grounding")

        # Check for consistency
        consistency_patterns = [
            r"(?i)consistent",
            r"(?i)reinvestment.{0,20}(rate|ratio)",
            r"(?i)ROIC.{0,20}WACC",
            r"(?i)implied.{0,15}(margin|return|growth)",
        ]

        has_consistency = any(re.search(p, ai_output) for p in consistency_patterns)
        if has_consistency:
            score += 15
            feedback_parts.append("Internal consistency checked")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard terminal value analysis"

    def _score_cyclical_structural(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score cyclical vs structural distinction."""
        score = 50.0
        feedback_parts = []

        # Check for explicit cyclical vs structural analysis
        cyclical_patterns = [
            r"(?i)cyclical.{0,20}(vs|versus|or).{0,20}structural",
            r"(?i)temporary.{0,20}(vs|versus|or).{0,20}permanent",
            r"(?i)normalize",
            r"(?i)mean.{0,10}revert",
            r"(?i)mid.cycle",
            r"(?i)through.cycle",
        ]

        cyclical_count = sum(1 for p in cyclical_patterns if re.search(p, ai_output))
        if cyclical_count >= 2:
            score += 25
            feedback_parts.append("Strong cyclical/structural analysis")
        elif cyclical_count >= 1:
            score += 10
            feedback_parts.append("Some cyclical awareness")

        # Check for normalized earnings discussion
        normalized_patterns = [
            r"(?i)normalized.{0,15}(earnings|margin|revenue)",
            r"(?i)sustainable.{0,15}(level|margin|growth)",
            r"(?i)peak.{0,15}(vs|versus|or).{0,15}trough",
        ]

        has_normalized = any(re.search(p, ai_output) for p in normalized_patterns)
        if has_normalized:
            score += 20
            feedback_parts.append("Uses normalized metrics")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard cyclical analysis"

    # === PORTFOLIO CONSTRUCTION DIMENSIONS ===

    def _score_risk_classification(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score risk classification in portfolio construction."""
        score = 50.0
        feedback_parts = []

        # Check for environmental vs idiosyncratic distinction
        env_idio_patterns = [
            r"(?i)environmental.{0,20}(vs|versus|from).{0,20}idiosyncratic",
            r"(?i)systematic.{0,20}(vs|versus|from).{0,20}specific",
            r"(?i)factor.{0,20}(vs|versus|from).{0,20}stock",
            r"(?i)market.{0,20}(vs|versus|from).{0,20}company",
            r"(?i)beta.{0,20}(vs|versus|from).{0,20}alpha",
        ]

        env_idio_count = sum(1 for p in env_idio_patterns if re.search(p, ai_output))
        if env_idio_count >= 2:
            score += 25
            feedback_parts.append("Strong env/idio classification")
        elif env_idio_count >= 1:
            score += 15
            feedback_parts.append("Some risk classification")

        # Check for multiple risk types identified
        risk_types = [
            r"(?i)beta",
            r"(?i)sector",
            r"(?i)factor",
            r"(?i)volatility",
            r"(?i)duration",
            r"(?i)liquidity",
            r"(?i)correlation",
        ]

        risk_type_count = sum(1 for p in risk_types if re.search(p, ai_output))
        if risk_type_count >= 4:
            score += 20
            feedback_parts.append("Comprehensive risk taxonomy")
        elif risk_type_count >= 2:
            score += 10
            feedback_parts.append("Multiple risks identified")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard risk classification"

    def _score_hedging_logic(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score hedging logic in portfolio construction."""
        score = 50.0
        feedback_parts = []

        # Check for hedge environmental / keep idiosyncratic logic
        hedge_logic_patterns = [
            r"(?i)hedge.{0,30}environmental",
            r"(?i)hedge.{0,30}(factor|systematic|beta)",
            r"(?i)keep.{0,20}(idiosyncratic|specific|alpha)",
            r"(?i)(don't|do not).{0,15}hedge.{0,15}(alpha|thesis)",
            r"(?i)what.{0,10}(to|not to).{0,10}hedge",
        ]

        hedge_logic_count = sum(1 for p in hedge_logic_patterns if re.search(p, ai_output))
        if hedge_logic_count >= 2:
            score += 25
            feedback_parts.append("Strong hedging logic")
        elif hedge_logic_count >= 1:
            score += 15
            feedback_parts.append("Some hedging rationale")

        # Check for specific hedge instruments
        instrument_patterns = [
            r"(?i)(SPY|XLV|XBI|XLK|QQQ)",
            r"(?i)(ETF|index).{0,15}hedge",
            r"(?i)(put|call|option)",
            r"(?i)futures",
            r"(?i)overlay",
        ]

        has_instruments = any(re.search(p, ai_output) for p in instrument_patterns)
        if has_instruments:
            score += 15
            feedback_parts.append("Specific hedge instruments")

        # Check for residual exposure acknowledgment
        residual_patterns = [
            r"(?i)residual.{0,15}exposure",
            r"(?i)unhedged.{0,15}(risk|exposure)",
            r"(?i)remain.{0,15}exposed",
            r"(?i)accept.{0,15}(as|exposure)",
        ]

        has_residual = any(re.search(p, ai_output) for p in residual_patterns)
        if has_residual:
            score += 10
            feedback_parts.append("Acknowledges residual exposure")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard hedging analysis"

    def _score_sizing_methodology(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score position sizing methodology."""
        score = 50.0
        feedback_parts = []

        # Check for risk-based (not just dollar) sizing
        risk_sizing_patterns = [
            r"(?i)volatility.{0,20}(adjusted|based|weighted)",
            r"(?i)risk.{0,20}(contribution|parity|weighted)",
            r"(?i)dollar.{0,20}(vs|versus|≠).{0,20}risk",
            r"(?i)notional.{0,20}(vs|versus|≠).{0,20}risk",
            r"(?i)equal.{0,15}(vol|risk|volatility)",
            r"(?i)size.{0,20}(on|for|by).{0,20}risk",
        ]

        risk_sizing_count = sum(1 for p in risk_sizing_patterns if re.search(p, ai_output))
        if risk_sizing_count >= 2:
            score += 25
            feedback_parts.append("Strong risk-based sizing")
        elif risk_sizing_count >= 1:
            score += 15
            feedback_parts.append("Some risk-based sizing")
        else:
            feedback_parts.append("May use notional sizing only")

        # Check for volatility calculations
        vol_patterns = [
            r"\d+%\s*(vol|volatility|σ)",
            r"(?i)(vol|volatility).{0,10}\d+%",
            r"(?i)\$[\d.]+M?.{0,10}(at|×).{0,10}\d+%",
        ]

        has_vol_calc = any(re.search(p, ai_output) for p in vol_patterns)
        if has_vol_calc:
            score += 15
            feedback_parts.append("Includes volatility calculations")

        # Check for binary/event sizing
        binary_patterns = [
            r"(?i)binary.{0,20}(risk|event|sizing)",
            r"(?i)max.{0,10}loss",
            r"(?i)event.{0,20}sizing",
            r"(?i)defined.{0,10}risk",
        ]

        has_binary = any(re.search(p, ai_output) for p in binary_patterns)
        if has_binary:
            score += 10
            feedback_parts.append("Addresses binary event sizing")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard sizing methodology"

    def _score_risk_placement(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score risk placement and budgeting."""
        score = 50.0
        feedback_parts = []

        # Check for gross/net exposure discussion
        exposure_patterns = [
            r"(?i)gross.{0,10}exposure",
            r"(?i)net.{0,10}exposure",
            r"(?i)portfolio.{0,10}(weight|allocation)",
            r"(?i)risk.{0,10}budget",
        ]

        exposure_count = sum(1 for p in exposure_patterns if re.search(p, ai_output))
        if exposure_count >= 2:
            score += 20
            feedback_parts.append("Discusses exposure management")
        elif exposure_count >= 1:
            score += 10
            feedback_parts.append("Some exposure discussion")

        # Check for risk budget or contribution
        risk_budget_patterns = [
            r"(?i)risk.{0,15}contribution",
            r"(?i)risk.{0,15}budget",
            r"(?i)\d+%\s*(of|portfolio).{0,15}(risk|vol)",
        ]

        has_risk_budget = any(re.search(p, ai_output) for p in risk_budget_patterns)
        if has_risk_budget:
            score += 15
            feedback_parts.append("Risk budgeting present")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard risk placement"

    def _score_uncertainty_judgment(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score handling of uncertainty."""
        score = 50.0
        feedback_parts = []

        # Check for explicit uncertainty handling
        uncertainty_patterns = [
            r"(?i)uncertain",
            r"(?i)unknown",
            r"(?i)range.{0,15}outcome",
            r"(?i)confidence",
            r"(?i)probability",
        ]

        uncertainty_count = sum(1 for p in uncertainty_patterns if re.search(p, ai_output))
        if uncertainty_count >= 3:
            score += 20
            feedback_parts.append("Strong uncertainty acknowledgment")
        elif uncertainty_count >= 1:
            score += 10
            feedback_parts.append("Some uncertainty discussion")

        # Check for what-if analysis
        what_if_patterns = [
            r"(?i)what.{0,10}if",
            r"(?i)what.{0,15}change.{0,15}view",
            r"(?i)revisit.{0,15}if",
            r"(?i)monitor.{0,15}for",
        ]

        has_what_if = any(re.search(p, ai_output) for p in what_if_patterns)
        if has_what_if:
            score += 15
            feedback_parts.append("Includes contingency planning")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard uncertainty handling"

    # === RISK ATTRIBUTION DIMENSIONS ===

    def _score_attribution_discipline(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score attribution discipline - factor decomposition."""
        score = 50.0
        feedback_parts = []

        # Check for factor decomposition
        factor_patterns = [
            r"(?i)factor.{0,20}(decomposition|attribution|contribution)",
            r"(?i)factor.{0,20}drag",
            r"(?i)(biotech|small.cap|growth|value|momentum).{0,20}(factor|tilt|exposure)",
            r"(?i)overweight.{0,20}×.{0,20}return",
            r"(?i)\d+%\s*(overweight|underweight).{0,20}-?\d+%",
        ]

        factor_count = sum(1 for p in factor_patterns if re.search(p, ai_output))
        if factor_count >= 3:
            score += 25
            feedback_parts.append("Strong factor decomposition")
        elif factor_count >= 1:
            score += 15
            feedback_parts.append("Some factor analysis")
        else:
            feedback_parts.append("Limited factor decomposition")

        # Check for residual alpha calculation
        residual_patterns = [
            r"(?i)residual.{0,15}alpha",
            r"(?i)after.{0,20}(factor|adjustment)",
            r"(?i)stock.selection.{0,20}(after|net|excluding)",
            r"(?i)(explained|unexplained).{0,15}by.{0,15}factor",
        ]

        has_residual = any(re.search(p, ai_output) for p in residual_patterns)
        if has_residual:
            score += 20
            feedback_parts.append("Calculates residual alpha")

        # Check for quantified calculation
        if re.search(r"\d+%.{0,15}×.{0,15}-?\d+%", ai_output):
            score += 10
            feedback_parts.append("Shows calculation methodology")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard attribution analysis"

    def _score_hypothesis_testing(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score hypothesis testing rigor."""
        score = 50.0
        feedback_parts = []

        # Check for explicit hypothesis testing
        hypothesis_patterns = [
            r"(?i)hypothesis",
            r"(?i)if.{0,20}(true|correct).{0,20}expect",
            r"(?i)falsif",
            r"(?i)(test|testing).{0,20}(belief|assumption|claim)",
            r"(?i)evidence.{0,20}(would|should).{0,20}(show|support)",
        ]

        hypothesis_count = sum(1 for p in hypothesis_patterns if re.search(p, ai_output))
        if hypothesis_count >= 2:
            score += 25
            feedback_parts.append("Strong hypothesis testing")
        elif hypothesis_count >= 1:
            score += 15
            feedback_parts.append("Some hypothesis testing")
        else:
            feedback_parts.append("Limited hypothesis testing")

        # Check for narrative skepticism
        skepticism_patterns = [
            r"(?i)(not|doesn't|does not).{0,15}support",
            r"(?i)inconsistent.{0,15}with",
            r"(?i)alternative.{0,15}explanation",
            r"(?i)(question|questioning).{0,15}(PM|narrative|belief)",
        ]

        has_skepticism = any(re.search(p, ai_output) for p in skepticism_patterns)
        if has_skepticism:
            score += 15
            feedback_parts.append("Shows appropriate skepticism")

        # Check for evidence-based conclusion
        evidence_patterns = [
            r"(?i)evidence.{0,20}(suggests|shows|indicates)",
            r"(?i)data.{0,15}(suggests|shows|indicates)",
            r"(?i)analysis.{0,15}(suggests|shows|reveals)",
        ]

        has_evidence = any(re.search(p, ai_output) for p in evidence_patterns)
        if has_evidence:
            score += 10
            feedback_parts.append("Evidence-based conclusions")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard hypothesis testing"

    def _score_contextual_evaluation(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """Score contextual evaluation - skill conditional on environment."""
        score = 50.0
        feedback_parts = []

        # Check for conditional skill assessment
        conditional_patterns = [
            r"(?i)conditional.{0,15}on.{0,15}environment",
            r"(?i)control.{0,20}for.{0,20}(factor|environment)",
            r"(?i)after.{0,20}(adjusting|controlling).{0,20}for",
            r"(?i)environment.{0,20}neutral",
            r"(?i)skill.{0,20}(given|conditional|after)",
        ]

        conditional_count = sum(1 for p in conditional_patterns if re.search(p, ai_output))
        if conditional_count >= 2:
            score += 20
            feedback_parts.append("Evaluates skill conditionally")
        elif conditional_count >= 1:
            score += 10
            feedback_parts.append("Some conditional evaluation")

        # Check for intentionality question
        intentionality_patterns = [
            r"(?i)intentional.{0,20}(vs|versus|or).{0,20}(unintentional|accidental)",
            r"(?i)was.{0,20}(intentional|deliberate|chosen)",
            r"(?i)(chosen|deliberate).{0,20}(bet|exposure|tilt)",
            r"(?i)accidental.{0,20}(accumulation|exposure)",
        ]

        has_intentionality = any(re.search(p, ai_output) for p in intentionality_patterns)
        if has_intentionality:
            score += 20
            feedback_parts.append("Addresses intentionality question")

        # Check for neutral environment skepticism
        neutral_skepticism_patterns = [
            r"(?i)(not|wasn't|was not).{0,15}neutral.{0,15}environment",
            r"(?i)silent.{0,15}(rotation|factor|regime)",
            r"(?i)environment.{0,20}(wasn't|was not|not).{0,15}neutral",
        ]

        has_neutral_skepticism = any(re.search(p, ai_output) for p in neutral_skepticism_patterns)
        if has_neutral_skepticism:
            score += 10
            feedback_parts.append("Questions neutral environment assumption")

        score = min(100.0, max(0.0, score))
        return score, "; ".join(feedback_parts) if feedback_parts else "Standard contextual evaluation"

    def _score_with_llm(
        self,
        ai_output: str,
        scenario: dict,
        dimension: dict,
    ) -> tuple[float, str]:
        """
        Score a dimension using an LLM.

        This provides more nuanced evaluation but requires API access.
        """
        # Placeholder for LLM-based scoring
        # Would integrate with Anthropic or OpenAI API
        return 75.0, "LLM scoring not yet implemented"

    def calculate_overall_score(self, dimension_scores: dict) -> float:
        """Calculate weighted overall score."""
        total = 0.0
        total_weight = 0.0

        for dimension in self.dimensions:
            dim_id = dimension["id"]
            weight = dimension.get("weight", 1.0)

            if dim_id in dimension_scores:
                total += dimension_scores[dim_id] * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return total / total_weight

    def determine_pass_fail(
        self,
        overall_score: float,
        critical_failures: list,
    ) -> bool:
        """Determine if submission passes."""
        if critical_failures:
            return False
        return overall_score >= self.pass_threshold


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Grade AI outputs against evaluation rubrics",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Grade command
    grade_parser = subparsers.add_parser("grade", help="Grade a submission")
    grade_parser.add_argument("--submission", required=True, help="Path to submission file")
    grade_parser.add_argument("--rubric", required=True, help="Path to rubric YAML")
    grade_parser.add_argument("--scenario", help="Path to scenario YAML (optional)")
    grade_parser.add_argument("--use-llm", action="store_true", help="Use LLM for grading")

    args = parser.parse_args()

    if args.command == "grade":
        # Load rubric
        with open(args.rubric) as f:
            rubric = yaml.safe_load(f)

        # Load submission
        with open(args.submission) as f:
            submission = f.read()

        # Load scenario if provided
        scenario = {}
        if args.scenario:
            with open(args.scenario) as f:
                scenario = yaml.safe_load(f)

        # Grade
        engine = GradingEngine(rubric)
        scores, failures, feedback = engine.grade(
            submission, scenario, use_llm=args.use_llm
        )

        # Output results
        overall = engine.calculate_overall_score(scores)
        passed = engine.determine_pass_fail(overall, failures)

        print(f"\n{'='*50}")
        print(f"GRADING RESULTS")
        print(f"{'='*50}")
        print(f"\nOverall Score: {overall:.1f}/100")
        print(f"Status: {'PASS' if passed else 'FAIL'}")

        print(f"\n--- Dimension Scores ---")
        for dim, score in scores.items():
            print(f"  {dim}: {score:.1f}")

        if failures:
            print(f"\n--- Critical Failures ---")
            for failure in failures:
                print(f"  - {failure}")

        print(f"\n--- Detailed Feedback ---")
        for dim, fb in feedback.items():
            print(f"  {dim}: {fb}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
