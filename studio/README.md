# RLHF Studio

Interactive Streamlit workflow for generating DPO preference pairs
from live LLM outputs against real financial documents (SEC 10-K /
10-Q filings). This directory is the differentiated asset of
`investment-workflow-evals`: most finance-eval repos ship rubrics
only, Studio ships a full pairwise preference-pipeline end-to-end.

## What It Does (3-minute version)

1. Upload an SEC filing PDF (10-K or 10-Q).
2. Studio parses it section-aware (MD&A, Risk Factors, Financial
   Statements, etc.), filters boilerplate, and chunks it to fit the
   provider context window.
3. You pick a task prompt (e.g. "write a bull thesis for the
   fiscal-year MD&A"), a set of models / temperatures / personas, and
   a K (2-9) for how many candidate outputs to generate.
4. Studio generates K outputs in parallel, handling Anthropic, OpenAI,
   and Gemini rate limits.
5. You either (a) rank the K outputs best→worst via drag-and-drop, or
   (b) hand-edit one draft into a single chosen/rejected pair.
6. Ranked sessions expand to all K(K-1)/2 pairwise combinations, each
   emitted as one JSONL record conforming to
   [`schemas/preference_pair.json`](../schemas/preference_pair.json).

## Files

| File | Role |
|---|---|
| `app.py` | Streamlit UI. All user-facing state lives here. |
| `configs.py` | Model registry, preset bundles, and persona definitions. Provider inference keys off of SKU prefix. |
| `document.py` | Section-aware PDF parsing, boilerplate filtering, chunking. |
| `generator.py` | Multi-provider LLM call dispatch with rate-limit handling. |
| `ranker.py` | K-ranking → pairwise extraction + AI pre-screen helper. |
| `rewards.py` | GRPO-aligned reward signal (accuracy, logic, format, length, composite). |
| `storage.py` | JSONL persistence. |

## Quick Start

```bash
# From repo root
pip install -e ".[studio]"
streamlit run studio/app.py
```

## Preference-Pair Extraction Pipeline

This section documents the schema, ranker behavior, and export format.
It doubles as the dataset-card source of truth once Phase 2 ships the
preference-pair release.

### Two Entry Points, One Schema

Both the batch path (`src/extract_pairs.py`) and the interactive
Studio path (`studio/ranker.py`) emit records conforming to the
shared JSON Schema at `schemas/preference_pair.json`. The `source`
field disambiguates provenance:

| `source` value | Produced by | When |
|---|---|---|
| `scenario_anchor` | `src/extract_pairs.py` | Batch extraction from YAML scenario anchor answers (strong / acceptable / failing). |
| `studio_ranking` | `studio/ranker.py::extract_pairwise_preferences` | Interactive K-ranking over K live LLM outputs. |
| `studio_single_pair` | `studio/ranker.py` single-pair path | One draft → corrected draft → one pair. |

### Ranker → Pair Combinatorics

For a ranked list `[A, C, B, D]` (A = best, D = worst), the ranker
emits all K(K-1)/2 = 6 pairs:

```
(A>C), (A>B), (A>D), (C>B), (C>D), (B>D)
```

K=2 yields 1 pair. K=5 yields 10. K=9 (the supported cap) yields 36.
Rank margin is stored so downstream training can weight pairs by
disagreement strength.

### Schema (Full Shape)

See `schemas/preference_pair.json` for the authoritative JSON Schema.
Required top-level keys: `prompt`, `chosen`, `rejected`.

Commonly populated optional keys:

| Key | Type | Populated by |
|---|---|---|
| `timestamp` | ISO-8601 string | ranker + batch paths |
| `scenario_id` | string | `scenario_anchor` only |
| `chosen_score`, `rejected_score` | float | rewards-annotation path |
| `source` | enum | always set |
| `tags` | list[string] | error-taxonomy tags (e.g. `Hallucination`, `Math Error`) |
| `mode` | string | `single_pair` \| `ranking` |
| `ranking_metadata.session_id` | string | studio ranking |
| `ranking_metadata.total_k` | int | studio ranking |
| `ranking_metadata.chosen_rank`, `rejected_rank`, `rank_margin` | int | studio ranking |
| `ranking_metadata.chosen_config`, `rejected_config` | object | SKU + temperature + persona |
| `ranking_metadata.full_ranking` | list[string] | the full ranked labels |
| `reward_details.chosen`, `rejected` | object | GRPO-aligned reward breakdown |

### Export Format

Studio writes one JSONL record per line to a user-chosen path (default
`results/preference_pairs.jsonl`). Records append; downstream training
jobs read the file in order. Duplicate-suppression is left to the
downstream consumer — Studio deliberately does not dedupe because the
same (prompt, chosen, rejected) triple can legitimately occur across
different sessions with different ranking context.

### AI Pre-Screen

Before human ranking, Studio can optionally run an LLM pre-screen over
the K outputs using `studio/ranker.py::ai_pre_screen`. The pre-screen
assigns each output an overall quality score on 0-100 and flags
responses likely to be low-quality (default threshold ≤ 40). Pairs
extracted from sessions with pre-screen scores attached carry them
forward via `ai_judge_scores` on each pair for training weighting.

## Configuration

`configs.py` bundles two primary user-facing constructs:

- **`GenerationConfig`** — an immutable dataclass capturing the SKU,
  temperature, persona prompt, and a display label. Provider is
  inferred from SKU prefix (`claude-*` → Anthropic, `gpt-*` →
  OpenAI, `gemini-*` → Gemini).
- **Presets** — prebuilt bundles of GenerationConfigs suitable for
  common K values (e.g. "K=4 balanced frontier": Opus / Sonnet / GPT /
  Gemini at temperature 0.7).

Personas are financial-analyst viewpoints (e.g. "skeptical value PM",
"growth-at-a-reasonable-price specialist") selected to produce
legibly-different drafts at the same temperature.

## Testing

```bash
pytest tests/test_studio_smoke.py tests/test_studio_ranker.py tests/test_rewards.py -v
```

All Studio tests are structural and import-based; they do not make
live API calls.

## Known Limitations

- PDF parsing is tuned for SEC filings. Non-SEC PDFs may surface
  unfiltered boilerplate.
- Rate-limit handling uses a conservative 30k TPM assumption; users on
  higher tiers can override the delay in `ranker.py::_estimate_delay`.
- Ranker agreement metrics are not yet exposed in the UI — they are
  planned as a Phase 2 deliverable alongside the preference-pair
  dataset card.

## Licensing Note for Dataset Releases

SEC 10-K / 10-Q filings are public-domain. Any PDF parser libraries
bundled with Studio should be audited for non-permissive licensing
before a public dataset release; the Phase-2 plan calls for swapping
to EDGAR HTML ingestion if PDF licensing surfaces any third-party
rights issues. Preference pairs derived from public-domain filings
inherit public-domain status for the source text; generated model
outputs carry their respective provider licensing terms.
