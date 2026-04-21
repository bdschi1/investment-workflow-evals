"""Populate self-consistency floor tables in results/judge_agreement_v1.md.

Uses the heuristic GradingEngine (no API calls) to score each available
golden-answer markdown against a per-module rubric. A second "Judge B" is
constructed by perturbing the heuristic scores with Gaussian noise
(``random.Random(seed=42).gauss(0, noise_sigma)`` and clamped to [0, 100]).

This is **not** real inter-judge agreement. It is a simulated self-consistency
floor: identical grader, identical inputs, noise-perturbed twin. Its sole
purpose is to show the metric pipeline works end-to-end and produces
sensible values for Pearson r, Spearman ρ, and weighted Cohen's κ.

Real frontier-model cross-judge agreement requires a live benchmark run
(see ``tools/benchmark_runner.py``) and is out of scope for this offline
population step.

Usage:
    python scripts/populate_judge_agreement.py

Writes (in-place) self-consistency tables to results/judge_agreement_v1.md.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import yaml

from tools.grading_engine import GradingEngine
from tools.judge_agreement import compute_full_agreement

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_MD = REPO_ROOT / "results" / "judge_agreement_v1.md"
EVALS_DIR = REPO_ROOT / "evals"

# Deterministic noise seed — matches the spec in the methodology doc.
SEED = 42
NOISE_SIGMA = 4.0  # points on the 0-100 scale


def _load_rubric(module_dir: Path) -> dict | None:
    """Load the primary rubric YAML for a module, preferring ``standard.yaml``."""
    rubrics_dir = module_dir / "rubrics"
    if not rubrics_dir.is_dir():
        return None
    candidates = sorted(rubrics_dir.glob("*.yaml"))
    if not candidates:
        return None
    # Prefer standard.yaml if present.
    preferred = [p for p in candidates if p.name == "standard.yaml"]
    rubric_path = preferred[0] if preferred else candidates[0]
    with rubric_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_scenario_for_golden(module_dir: Path, golden_path: Path) -> dict:
    """Locate the matching scenario YAML for a golden answer file.

    Goldens are named to match a scenario stem. If no match is found, an
    empty dict is returned — the heuristic grader tolerates missing scenario
    context (it just skips hallucination checks that rely on ``key_facts``).
    """
    stem = golden_path.stem
    scenarios_dir = module_dir / "scenarios"
    if not scenarios_dir.is_dir():
        return {}
    candidates = list(scenarios_dir.glob(f"{stem}.yaml")) + list(
        scenarios_dir.glob(f"{stem}.yml")
    )
    if not candidates:
        return {}
    with candidates[0].open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _score_golden(golden_path: Path, module_dir: Path) -> dict[str, float]:
    """Run the heuristic grader on a single golden answer and return dim scores.

    Rubrics whose dimensions lack an ``id`` field are skipped (returns empty
    dict) — the heuristic grader keys scoring functions off ``id``, so these
    modules cannot be heuristically graded without rubric edits that are
    out of scope for this script.
    """
    rubric = _load_rubric(module_dir)
    if rubric is None:
        return {}
    dims = rubric.get("dimensions", []) or []
    if not dims or any("id" not in d for d in dims):
        return {}
    scenario = _load_scenario_for_golden(module_dir, golden_path)
    engine = GradingEngine(rubric)
    text = golden_path.read_text(encoding="utf-8")
    try:
        dim_scores, _criticals, _feedback = engine.grade(text, scenario, use_llm=False)
    except (KeyError, TypeError, AttributeError):
        # Rubric shape not supported by the heuristic path — skip.
        return {}
    return dim_scores


def _perturb(scores: dict[str, float], rng: random.Random) -> dict[str, float]:
    """Add Gaussian noise to each score, clamped to [0, 100]."""
    return {
        k: max(0.0, min(100.0, v + rng.gauss(0.0, NOISE_SIGMA)))
        for k, v in scores.items()
    }


def _collect_pairs() -> tuple[
    list[tuple[Path, dict[str, float], dict[str, float]]],
    dict[str, list[tuple[float, float]]],
]:
    """Collect (golden_path, judge_A_scores, judge_B_scores) for every golden.

    Returns both the per-golden triples and an overall pooled list of
    (score_A, score_B) pairs across every dimension of every golden.
    """
    rng = random.Random(SEED)
    triples: list[tuple[Path, dict[str, float], dict[str, float]]] = []
    per_module: dict[str, list[tuple[float, float]]] = {}

    for module_dir in sorted(EVALS_DIR.iterdir()):
        if not module_dir.is_dir():
            continue
        goldens_dir = module_dir / "golden_answers"
        if not goldens_dir.is_dir():
            continue
        for golden in sorted(goldens_dir.glob("*.md")):
            scores_a = _score_golden(golden, module_dir)
            if not scores_a:
                continue
            scores_b = _perturb(scores_a, rng)
            triples.append((golden, scores_a, scores_b))
            mod_name = module_dir.name
            per_module.setdefault(mod_name, [])
            for dim in scores_a:
                per_module[mod_name].append((scores_a[dim], scores_b[dim]))

    return triples, per_module


def _format_number(value: float) -> str:
    if value != value:  # NaN
        return "n/a"
    return f"{value:.3f}"


def _build_tables(
    triples: list[tuple[Path, dict[str, float], dict[str, float]]],
    per_module: dict[str, list[tuple[float, float]]],
) -> str:
    """Build the markdown fragment that replaces the TBD self-consistency block."""
    if not triples:
        return (
            "### Simulated Self-Consistency Floor (seed=42)\n\n"
            "_No golden answers with loadable rubrics were found. Skipping._\n\n"
        )

    # Overall pooled pairs
    all_a: list[float] = []
    all_b: list[float] = []
    for _, a, b in triples:
        for dim in a:
            all_a.append(a[dim])
            all_b.append(b[dim])
    overall = compute_full_agreement(all_a, all_b)

    n_goldens = len(triples)
    n_pairs = len(all_a)

    lines: list[str] = []
    lines.append(
        "### Simulated Self-Consistency Floor (seed=42) — NOT real inter-judge agreement"
    )
    lines.append("")
    lines.append(
        f"Judge A is the heuristic `GradingEngine` run against {n_goldens} "
        f"golden-answer markdown files. Judge B is the same grader's output with "
        f"additive Gaussian noise (σ = {NOISE_SIGMA:.1f} points, "
        f"`random.Random({SEED})`, clamped to [0, 100]). This is a sanity floor "
        "that confirms the metric pipeline is wired end-to-end. It is **not** a "
        "real cross-model comparison — see the frontier-model section below for "
        "that."
    )
    lines.append("")
    lines.append("**Overall pooled pairs across all dimensions and modules:**")
    lines.append("")
    lines.append("| Metric | Value | Notes |")
    lines.append("|---|---|---|")
    lines.append(
        f"| Pearson r            | {_format_number(overall['pearson'])} | "
        "Linear correlation on pooled dimension scores. |"
    )
    lines.append(
        f"| Spearman ρ           | {_format_number(overall['spearman'])} | "
        "Rank correlation; robust to monotone transforms. |"
    )
    lines.append(
        f"| Cohen's κ (weighted) | {_format_number(overall['kappa_weighted'])} | "
        "Linear-weighted κ on 5 rubric bins (Fail/Poor/Acceptable/Good/Excellent). |"
    )
    lines.append(
        f"| n (pooled pairs)     | {n_pairs} | {n_goldens} goldens × dimensions per rubric. |"
    )
    lines.append("")
    lines.append(
        "**Per-module breakdown (pooled dimension scores within each module):**"
    )
    lines.append("")
    lines.append("| Module | n pairs | Pearson r | Spearman ρ | Weighted κ |")
    lines.append("|---|---:|---|---|---|")
    for mod_name in sorted(per_module):
        pairs = per_module[mod_name]
        if len(pairs) < 3:
            lines.append(f"| `{mod_name}` | {len(pairs)} | n/a | n/a | n/a (n<3) |")
            continue
        mod_a = [p[0] for p in pairs]
        mod_b = [p[1] for p in pairs]
        m = compute_full_agreement(mod_a, mod_b)
        lines.append(
            f"| `{mod_name}` | {len(pairs)} | "
            f"{_format_number(m['pearson'])} | "
            f"{_format_number(m['spearman'])} | "
            f"{_format_number(m['kappa_weighted'])} |"
        )
    lines.append("")

    # Second table: heuristic vs perturbed heuristic on goldens only (reiterates).
    lines.append(
        "### Heuristic Grader vs Perturbed Heuristic — per-golden overall scores"
    )
    lines.append("")
    lines.append(
        f"For each of the {n_goldens} goldens, we compute a weighted overall "
        "score (unweighted mean across rubric dimensions for simplicity) for "
        "both Judge A and Judge B, then compute metrics across goldens. This "
        "tests agreement at the _memo_ granularity rather than the _dimension_ "
        "granularity."
    )
    lines.append("")
    overall_a = [sum(a.values()) / len(a) for _, a, _ in triples if a]
    overall_b = [sum(b.values()) / len(b) for _, _, b in triples if b]
    per_memo = compute_full_agreement(overall_a, overall_b)
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Pearson r            | {_format_number(per_memo['pearson'])} |")
    lines.append(f"| Spearman ρ           | {_format_number(per_memo['spearman'])} |")
    lines.append(
        f"| Cohen's κ (weighted) | {_format_number(per_memo['kappa_weighted'])} |"
    )
    lines.append(f"| n (goldens)          | {n_goldens} |")
    lines.append("")

    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------
# Markdown rewriter: replaces the section between the two markers with new content.
# ----------------------------------------------------------------------

_BEGIN_MARKER = "<!-- BEGIN self-consistency floor (auto-generated) -->"
_END_MARKER = "<!-- END self-consistency floor (auto-generated) -->"


def _rewrite_results_md(tables_md: str) -> None:
    text = RESULTS_MD.read_text(encoding="utf-8")
    block = f"{_BEGIN_MARKER}\n\n{tables_md}\n{_END_MARKER}"

    if _BEGIN_MARKER in text and _END_MARKER in text:
        text = re.sub(
            rf"{re.escape(_BEGIN_MARKER)}.*?{re.escape(_END_MARKER)}",
            block,
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        # Append at end if markers are missing.
        text = text.rstrip() + "\n\n" + block + "\n"

    RESULTS_MD.write_text(text, encoding="utf-8")


def main() -> None:
    triples, per_module = _collect_pairs()
    tables_md = _build_tables(triples, per_module)
    _rewrite_results_md(tables_md)
    # Also echo the overall numbers to stdout for convenience.
    print(f"Wrote self-consistency tables to {RESULTS_MD} ({len(triples)} goldens).")


if __name__ == "__main__":
    main()
