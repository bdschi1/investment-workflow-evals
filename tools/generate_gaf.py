"""Generate golden answer files (GAFs) using Opus informed by IRR retrieval.

Usage:
    python -m tools.generate_gaf \
        --scenario evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml \
        --output generated_gaf.md

    # Dry-run: print prompt without calling Opus
    python -m tools.generate_gaf \
        --scenario evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml \
        --dry-run

    # Compare to existing GAF
    python -m tools.generate_gaf \
        --scenario evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml \
        --compare

    # Skip IRR retrieval (use scenario context only)
    python -m tools.generate_gaf \
        --scenario evals/01_equity_thesis/scenarios/cyclical_trough_valuation.yaml \
        --no-irr
"""

from __future__ import annotations

import argparse
import sys
import textwrap
import yaml
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
_IRR_ROOT = _REPO_ROOT.parent / "investment-research-rag"
_IRR_SRC = _IRR_ROOT / "src"
_IRR_VECTORSTORE = _IRR_ROOT / "local_data" / "vectorstore"
_TEMPLATE_PATH = _REPO_ROOT / "templates" / "investment_memo_template.md"

_COLLECTIONS = ["coresources", "_default"]
_EMBEDDING_DIM = 768


# ---------------------------------------------------------------------------
# IRR retrieval
# ---------------------------------------------------------------------------

def _load_irr_retriever(collection: str):
    """Load an IRR retriever for a given collection. Returns None on failure."""
    store_path = _IRR_VECTORSTORE / collection
    if not store_path.exists():
        print(f"  [warn] Collection '{collection}' not found at {store_path}")
        return None

    # Lazy imports — only needed if IRR is available
    if str(_IRR_SRC) not in sys.path:
        sys.path.insert(0, str(_IRR_SRC))
    if str(_IRR_ROOT) not in sys.path:
        sys.path.insert(0, str(_IRR_ROOT))

    try:
        from rag.embeddings.factory import get_embedding_provider
        from rag.vectorstore.faiss_store import FAISSStore
        from rag.retrieval.retriever import Retriever
    except ImportError as e:
        print(f"  [warn] IRR imports failed: {e}")
        return None

    embedder = get_embedding_provider("ollama", model="nomic-embed-text")
    store = FAISSStore(dimension=_EMBEDDING_DIM)
    store.load(str(store_path))
    return Retriever(embedding_provider=embedder, vector_store=store)


def retrieve_context(scenario: dict, collections: list[str] | None = None) -> str:
    """Query IRR collections with scenario-derived queries. Returns formatted context."""
    if collections is None:
        collections = _COLLECTIONS

    # Build queries from scenario
    queries = _build_irr_queries(scenario)
    if not queries:
        return ""

    all_results = []
    for coll_name in collections:
        retriever = _load_irr_retriever(coll_name)
        if retriever is None:
            continue

        from rag.retrieval.schemas import RetrievalConfig
        from rag.vectorstore.schemas import MetadataFilter

        ticker = scenario.get("context", {}).get("company", {}).get("ticker")
        for query_text in queries:
            # Only filter by ticker on _default (filings), not coresources (textbooks)
            use_filter = ticker and coll_name != "coresources"
            config = RetrievalConfig(
                top_k=5,
                hybrid=False,
                min_score=0.0,
                metadata_filter=MetadataFilter(ticker=ticker) if use_filter else None,
            )
            try:
                result = retriever.retrieve(query_text, config=config)
            except Exception as e:
                print(f"    [warn] Retrieval error on '{coll_name}': {e}")
                continue
            for hit in result.results:
                all_results.append({
                    "collection": coll_name,
                    "query": query_text,
                    "score": hit.score,
                    "text": hit.text,
                    "source": getattr(hit.metadata, "source_filename", None),
                    "section": getattr(hit.metadata, "section_name", None),
                    "ticker": getattr(hit.metadata, "ticker", None),
                })

    if not all_results:
        return ""

    # Deduplicate by text content, keep highest-scoring
    seen_texts = {}
    for r in all_results:
        key = r["text"][:200]
        if key not in seen_texts or r["score"] > seen_texts[key]["score"]:
            seen_texts[key] = r
    unique = sorted(seen_texts.values(), key=lambda x: x["score"], reverse=True)[:20]

    # Format as context block
    lines = ["## Retrieved Research Context (from IRR)\n"]
    for i, r in enumerate(unique, 1):
        source_label = r["source"] or "unknown"
        section_label = f" > {r['section']}" if r.get("section") else ""
        lines.append(f"### Source {i}: {source_label}{section_label} "
                      f"[{r['collection']}] (score: {r['score']:.3f})")
        lines.append(r["text"])
        lines.append("")
    return "\n".join(lines)


def _build_irr_queries(scenario: dict) -> list[str]:
    """Derive targeted IRR queries from scenario content."""
    queries = []
    ctx = scenario.get("context", {})

    # Handle both company and fund scenarios
    company = ctx.get("company", {})
    fund = ctx.get("fund", {})
    name = company.get("name", "") or fund.get("name", "")
    ticker = company.get("ticker", "")
    sector = company.get("sector", "") or fund.get("strategy", "")

    # Query 1: subject + situation/task summary
    situation = ctx.get("situation", "") or ctx.get("market_environment", "")
    if situation:
        queries.append(f"{name} {ticker} {situation[:200]}".strip())

    # Query 2: from task prompt
    task_prompt = scenario.get("task", {}).get("prompt", "")
    if task_prompt:
        queries.append(f"{name} {task_prompt[:200]}")

    # Query 3: key facts (critical ones)
    key_facts = scenario.get("key_facts", [])
    critical_facts = [f["fact"] for f in key_facts
                      if f.get("importance") == "critical"]
    if critical_facts:
        prefix = ticker or name
        queries.append(f"{prefix} {' '.join(critical_facts[:2])}")

    # Query 4: sector/strategy methodology
    if sector:
        queries.append(f"{sector} methodology framework analysis")

    # Query 5: academic references mentioned in data sources
    data_sources = scenario.get("data_sources", [])
    for ds in data_sources[:2]:
        ds_type = ds.get("type", "")
        desc = ds.get("description", "")
        if ds_type and desc:
            prefix = ticker or name
            queries.append(f"{prefix} {ds_type} {desc}")

    return queries[:6]


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _format_context_block(scenario: dict) -> str:
    """Format scenario context, handling both company and fund scenarios."""
    ctx = scenario.get("context", {})
    lines = []

    # Company-based scenarios
    company = ctx.get("company", {})
    if company:
        lines.append("### Subject")
        for k in ["name", "ticker", "sector", "market_cap", "description"]:
            if company.get(k):
                lines.append(f"- **{k.replace('_', ' ').title()}:** {company[k]}")

    # Fund-based scenarios (risk attribution, etc.)
    fund = ctx.get("fund", {})
    if fund:
        lines.append("### Fund")
        for k in ["name", "strategy", "aum", "inception", "benchmark", "description"]:
            if fund.get(k):
                lines.append(f"- **{k.replace('_', ' ').title()}:** {fund[k]}")

    # Performance period
    perf = ctx.get("performance_period", {})
    if perf:
        lines.append("\n### Performance Period")
        for k, v in perf.items():
            lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")

    # Fund characteristics
    chars = ctx.get("fund_characteristics", {})
    if chars:
        lines.append("\n### Fund Characteristics")
        for k, v in chars.items():
            lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")

    # Additional data (factor returns, etc.)
    addl_data = ctx.get("additional_data", {})
    if addl_data:
        lines.append("\n### Additional Data")
        for k, v in addl_data.items():
            label = k.replace("_", " ").title()
            if isinstance(v, list):
                lines.append(f"**{label}:**")
                for item in v:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- **{label}:** {v}")

    # Standard fields
    for field, label in [("situation", "Situation"), ("market_conditions", "Market Conditions"),
                         ("market_environment", "Market Environment"),
                         ("pm_claims", "PM Claims"), ("additional_context", "Additional Context")]:
        val = ctx.get(field)
        if val:
            lines.append(f"\n### {label}")
            lines.append(str(val).strip())

    lines.append(f"\n### As-of Date: {ctx.get('as_of_date', 'N/A')}")
    return "\n".join(lines)


def build_prompt(scenario: dict, irr_context: str, template: str) -> str:
    """Construct the Opus prompt from scenario + IRR context + template."""
    task = scenario.get("task", {})
    eval_criteria = scenario.get("evaluation_criteria", {})

    # Format context block (handles company, fund, or mixed scenarios)
    context_block = _format_context_block(scenario)

    # Format key facts
    key_facts_text = ""
    for f in scenario.get("key_facts", []):
        importance = f.get("importance", "supporting")
        key_facts_text += f"- [{importance.upper()}] {f['fact']} (source: {f.get('source', 'N/A')})\n"

    # Format data sources
    data_sources_text = ""
    for ds in scenario.get("data_sources", []):
        data_sources_text += f"\n### {ds.get('type', 'Unknown')} — {ds.get('description', '')}\n"
        data_sources_text += f"Date: {ds.get('date', 'N/A')}\n"
        for dp in ds.get("key_data_points", []):
            data_sources_text += f"- {dp}\n"

    # Format evaluation criteria
    criteria_text = ""
    for dim in eval_criteria.get("dimensions", []):
        criteria_text += f"\n**{dim['name']}** (weight: {dim.get('weight', 0):.0%})\n"
        for c in dim.get("criteria", []):
            criteria_text += f"  - {c}\n"

    # Format pitfalls
    pitfalls_text = ""
    for p in scenario.get("pitfalls", []):
        pitfalls_text += f"- AVOID: {p['description']} (type: {p.get('failure_type', 'N/A')})\n"

    # Format critical failures
    critical_failures = eval_criteria.get("critical_failures", [])
    critical_text = ""
    for cf in critical_failures:
        critical_text += f"- CRITICAL FAIL: {cf}\n"

    # Format constraints
    constraints = task.get("constraints", [])
    constraints_text = "\n".join(f"- {c}" for c in constraints)

    prompt = f"""You are a senior PM writing a golden answer file (GAF) — an institutional-quality reference response for an investment evaluation scenario. This GAF serves as a training target and grading baseline.

## CRITICAL: Conciseness Rules

**Target length: 150–220 lines of markdown.** This is a hard constraint.

Write like a PM writing for other PMs — punchy, opinionated, data-dense. Every sentence must earn its place.
- Lead with the conclusion, not the setup
- Use tables for quantitative data instead of prose
- No filler paragraphs, no "it is important to note that..."
- No restating what the scenario already says
- No meta-commentary about the analysis process
- Combine related points rather than listing them separately
- One disclaimer line at the end, not a full paragraph
- Adapt the template structure to the scenario type — skip sections that don't apply, add sections that do

## Requirements

1. Hit every evaluation dimension listed below
2. Avoid every pitfall and critical failure condition
3. Use probabilistic language — never express certainty about outcomes
4. Cite specific sources from the data provided
5. Internally consistent financial data throughout
6. Complete reasoning chains (thesis → evidence → conclusion) but stated efficiently

---

## Scenario: {scenario.get('title', 'Unknown')}

{context_block}

---

## Analysis Task
{task.get('prompt', 'N/A')}

**Output Type:** {task.get('expected_output_type', 'investment_thesis')}
**Time Horizon:** {task.get('time_horizon', 'N/A')}

### Constraints
{constraints_text}

---

## Available Data Sources
{data_sources_text}

## Key Facts (your analysis must address these)
{key_facts_text}

---

## Evaluation Criteria (graded on these dimensions)
{criteria_text}

## Critical Failure Conditions (any = automatic fail)
{critical_text}

## Pitfalls to Avoid
{pitfalls_text}

---

{irr_context if irr_context else ""}

## Output Template (adapt to scenario type — skip irrelevant sections)

{template}

---

Write the complete golden answer now. Markdown only, no preamble."""

    return prompt


# ---------------------------------------------------------------------------
# Opus generation
# ---------------------------------------------------------------------------

def _ensure_api_key():
    """Load ANTHROPIC_API_KEY from ~/.zshrc if not already in env."""
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    zshrc = Path.home() / ".zshrc"
    if zshrc.exists():
        for line in zshrc.read_text().splitlines():
            line = line.strip()
            if line.startswith("export ANTHROPIC_API_KEY="):
                val = line.split("=", 1)[1].strip().strip("'\"")
                os.environ["ANTHROPIC_API_KEY"] = val
                return
    raise RuntimeError("ANTHROPIC_API_KEY not found in env or ~/.zshrc")


def call_opus(prompt: str) -> str:
    """Call Claude Opus via Anthropic SDK. Returns the generated text."""
    import anthropic

    _ensure_api_key()
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return next((b.text for b in response.content if b.type == "text"), "")


# ---------------------------------------------------------------------------
# SIFT screening
# ---------------------------------------------------------------------------

def run_sift(filepath: Path) -> bool:
    """Run SIFT/AAH screening on the generated file. Returns True if passed."""
    import subprocess

    sift_dir = Path("/Users/bdsm4/code/tools/acs")
    if not sift_dir.exists():
        print("  [warn] SIFT not found at /Users/bdsm4/code/tools/acs — skipping screening")
        return True

    venv_python = sift_dir / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print("  [warn] SIFT venv not found — skipping screening")
        return True

    try:
        result = subprocess.run(
            [str(venv_python), "-m", "sift", "screen-file", str(filepath),
             "--output", "table"],
            capture_output=True,
            text=True,
            cwd=str(sift_dir),
            timeout=120,
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"  [SIFT FAILED] {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  [warn] SIFT error: {e}")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate golden answer files using Opus + IRR retrieval"
    )
    parser.add_argument("--scenario", required=True, help="Path to scenario YAML")
    parser.add_argument("--output", help="Output path for generated GAF (default: auto)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt, don't call Opus")
    parser.add_argument("--no-irr", action="store_true", help="Skip IRR retrieval")
    parser.add_argument("--compare", action="store_true", help="Show diff vs existing GAF")
    parser.add_argument("--no-sift", action="store_true", help="Skip SIFT screening")
    parser.add_argument("--collections", nargs="+", default=None,
                        help="IRR collections to query (default: coresources _default)")
    args = parser.parse_args()

    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        # Try relative to repo root
        scenario_path = _REPO_ROOT / args.scenario
    if not scenario_path.exists():
        print(f"Error: scenario not found: {args.scenario}")
        sys.exit(1)

    # Load scenario
    print(f"Loading scenario: {scenario_path.name}")
    with open(scenario_path) as f:
        scenario = yaml.safe_load(f)

    # Load template
    template = ""
    if _TEMPLATE_PATH.exists():
        template = _TEMPLATE_PATH.read_text()
    else:
        print("  [warn] Template not found, using minimal structure")
        template = "Use standard investment memo structure."

    # IRR retrieval
    irr_context = ""
    if not args.no_irr:
        print("Querying IRR collections...")
        irr_context = retrieve_context(scenario, collections=args.collections)
        if irr_context:
            n_chunks = irr_context.count("### Source")
            print(f"  Retrieved {n_chunks} unique chunks from IRR")
        else:
            print("  No IRR results — proceeding with scenario context only")

    # Build prompt
    prompt = build_prompt(scenario, irr_context, template)
    print(f"Prompt: {len(prompt):,} chars")

    if args.dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN — Full prompt:")
        print("=" * 80)
        print(prompt)
        return

    # Generate
    print("Calling Opus...")
    generated = call_opus(prompt)
    print(f"Generated: {len(generated):,} chars, ~{len(generated.splitlines())} lines")

    # Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        # Auto: put in generated_gaf/ next to golden_answers/
        scenario_id = scenario.get("id", scenario_path.stem)
        module_dir = scenario_path.parent.parent
        gen_dir = module_dir / "generated_gaf"
        gen_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = gen_dir / f"{scenario_id}_{timestamp}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(generated)
    print(f"Saved: {out_path}")

    # SIFT screening
    if not args.no_sift:
        print("Running SIFT screening...")
        passed = run_sift(out_path)
        if not passed:
            print("  ** SIFT flagged issues — review before using as GAF **")

    # Compare to existing
    if args.compare:
        existing_dir = scenario_path.parent.parent / "golden_answers"
        scenario_id = scenario.get("id", scenario_path.stem)
        existing_path = existing_dir / f"{scenario_id}.md"
        if existing_path.exists():
            print(f"\nExisting GAF: {existing_path}")
            print(f"  Lines: {len(existing_path.read_text().splitlines())}")
            print(f"  Chars: {len(existing_path.read_text()):,}")
            print(f"\nGenerated GAF: {out_path}")
            print(f"  Lines: {len(generated.splitlines())}")
            print(f"  Chars: {len(generated):,}")
            print(f"\nTo diff: diff {existing_path} {out_path}")
        else:
            print(f"\n  No existing GAF found at {existing_path}")


if __name__ == "__main__":
    main()
