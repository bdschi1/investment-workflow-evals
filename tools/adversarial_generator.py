"""Adversarial variant generator — Phase 3 stub.

This module is a deliberately non-functional scaffold. Its job in
Phase 1 is to make the Phase-3 shape concrete and reviewable before
code lands, in the same spirit as the CSV + judge-agreement scaffolds
shipped earlier in this phase.

What it WILL do (Phase 3):
    Given a base scenario dict (loaded from a `scenarios/*.yaml` file)
    and a `PerturbationClass`, emit one or more variant scenarios that
    preserve surface plausibility while introducing the targeted
    analytical trap. Output variants are written under
    `evals/adversarial_variants/` with a traceability field
    `parent_scenario_id` so the base-vs-variant delta is auditable.

What it will NOT do:
    - No generation for modules 06, 08, 09-12. The Phase-3 plan
      concentrates perturbations in the more mature modules (01, 03,
      04, 05) where golden answers exist and discrimination is most
      informative.
    - No fine-tuning, no training runs. The generator emits scenarios;
      evaluation is handled by the existing harness.

See the Phase 3 section of `upgrade_plan_02_investment_workflow_evals.md`
for the full design.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class PerturbationClass(enum.StrEnum):
    """Taxonomy of adversarial perturbations.

    Each class corresponds to a well-known analytical failure mode in
    institutional investment research. The enum value is the machine-
    readable tag used in variant metadata; the docstring on each member
    is the human-readable rationale.

    This taxonomy is explicitly scoped for Phase-3 work. Additional
    classes MAY be appended (values are stable strings), but existing
    members MUST NOT be renamed or removed without bumping the
    `generator_version` in the emitted variant records.
    """

    SWAP_CYCLICAL_FOR_STRUCTURAL = "swap_cyclical_for_structural"
    """Present cyclical demand as if it were structural alpha.

    Example: an end-market tailwind driven by stimulus spending is
    reframed as a secular share-gain story. Target failure mode:
    alpha/environment confusion.
    """

    INJECT_SURVIVORSHIP_BIAS = "inject_survivorship_bias"
    """Cite a peer set that excludes delisted or restructured names.

    Target failure mode: model cites the cleaned peer set without
    flagging the survivorship issue in the comparable-analysis task.
    """

    REFRAME_BETA_AS_ALPHA = "reframe_beta_as_alpha"
    """Narratively attribute factor-driven returns to stock selection.

    Example: a long-duration growth trade during a rates rally is
    described as 'identifying compounders early'. Target failure mode:
    attribution narrative substituted for factor decomposition.
    """

    INTRODUCE_TAIL_RISK_WITH_BENIGN_SURFACE = (
        "introduce_tail_risk_with_benign_surface"
    )
    """Bury a binary regulatory / credit / legal exposure in a
    scenario that otherwise reads as routine.

    Target failure mode: model anchors on the benign surface, misses
    the tail risk, and produces a position-sizing recommendation that
    does not reflect the true payoff distribution.
    """

    OVERFIT_TO_TRAILING_MOMENTUM = "overfit_to_trailing_momentum"
    """Provide a backtest window that cherry-picks a recent regime.

    Target failure mode: model treats trailing-3y volatility as
    forward-looking risk without stress-testing the regime
    assumption.
    """

    DOLLAR_NEUTRAL_NOT_RISK_NEUTRAL = "dollar_neutral_not_risk_neutral"
    """Present a dollar-neutral pair where the two legs have very
    different volatilities / betas.

    Target failure mode: model accepts dollar-neutral framing without
    sizing on a risk-equivalent basis.
    """

    HALLUCINATED_FOOTNOTE_SOURCE = "hallucinated_footnote_source"
    """Include a plausible-looking but fabricated source attribution
    in the scenario context.

    Target failure mode: model cites the fake source in its response.
    Useful for evidence_quality stress testing.
    """


@dataclass
class VariantRequest:
    """Caller-facing request to generate one adversarial variant.

    Phase 3 will extend this with `generator_version`,
    `random_seed`, and per-class configuration payloads; the minimal
    surface here is enough to write the public API and reviewer it
    ahead of implementation.
    """

    parent_scenario_path: str
    perturbation: PerturbationClass
    variant_suffix: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def generate_variant(request: VariantRequest) -> dict[str, Any]:  # noqa: ARG001
    """Phase-3 placeholder: emit one adversarial variant scenario.

    Raises:
        NotImplementedError: always. Phase-3 implementation will load
            `request.parent_scenario_path`, apply the perturbation
            defined by `request.perturbation`, and return a scenario
            dict conforming to `schemas/scenario.yaml` with an added
            `parent_scenario_id` traceability field.

    The deliberate NotImplementedError is what makes this module safe
    to ship in Phase 1: callers fail loudly rather than silently
    generating bogus variants.
    """
    raise NotImplementedError(
        "adversarial_generator is a Phase-1 scaffold. "
        "Phase-3 work will implement generate_variant(); until then "
        "any caller wanting adversarial variants should author them "
        "by hand under evals/adversarial_variants/."
    )


__all__ = [
    "PerturbationClass",
    "VariantRequest",
    "generate_variant",
]
