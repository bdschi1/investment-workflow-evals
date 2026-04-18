---
name: Propose a new evaluation scenario
about: Submit a new scenario for an existing module, or sketch a scenario for a module that needs more coverage
title: "[scenario] <module_id> — <short description>"
labels: ["scenario"]
assignees: []
---

<!--
Scenario proposals should be focused on analytical failure modes the
existing suite does not already cover. If the scenario looks like a
restatement of an existing one, include a short justification of what
new failure mode it targets. A scenario that produces identical
rankings across frontier models (no discrimination) is not useful.

Please use probabilistic language throughout — e.g. "often fails",
"tends to", "in the tested sample". Avoid "guaranteed", "always",
"100%", "cannot fail" constructions.
-->

## Module

<!-- e.g. 01_equity_thesis, 09_ma_analysis. Must match an existing module id. -->

## Scenario stem (filename)

<!-- snake_case. Example: competitor_read_through_pre_earnings -->

## Rubric tags

<!-- Which existing rubric dimensions does this scenario primarily exercise?
Pick from (module-dependent): factual_accuracy, analytical_rigor,
risk_assessment, evidence_quality, completeness, alpha_vs_environment,
attribution_discipline, hypothesis_testing, contextual_evaluation, etc.
Check the module's rubric file for the authoritative list. -->

- [ ] Tag 1: …
- [ ] Tag 2: …
- [ ] Tag 3 (optional): …

## Expected critical-failure class

<!-- If the rubric has critical_failures conditions (treating cyclical
demand as structural alpha, embedding unhedged risks into terminal
value, hallucinated data, etc.), which one does this scenario stress
test? State "none" if the scenario is focused on weighted-dimension
scoring only. -->

## Golden-answer sketch

<!-- 3-10 bullets outlining what a strong expert response would cover.
Not a full golden answer — enough that a reviewer can tell whether the
scenario admits a discriminating rubric. Include any load-bearing
numerical assumptions (e.g. dilution bands, terminal-value bounds)
that the golden answer would need to reference. -->

- …
- …
- …

## Adversarial "sounds smart but is wrong" response sketch

<!-- Optional but strongly preferred. 3-6 bullets of an AI-plausible
response that would trip the critical-failure condition above. If the
module rubric has a critical_failures section, make clear which one
this fires. -->

- …
- …

## Source / inspiration

<!-- Link to SEC filing, research note, known blowup, or market
episode that motivates the scenario. Bundled PDFs are off-limits
without a licensing check. EDGAR HTML links are fine. -->

## Checklist

- [ ] Scenario stem is snake_case and does not already exist under
      `evals/<module_id>/scenarios/`.
- [ ] Module id matches an existing directory. (If the module does
      not exist yet, open a separate "new module" issue first.)
- [ ] Rubric tags reference dimension ids that exist in the module's
      rubric YAML.
- [ ] No client-facing, confidential, or third-party-copyrighted
      material is reproduced verbatim.
- [ ] Probabilistic framing used throughout (no "guaranteed" /
      "always" / "100%" language).
