#!/usr/bin/env bash
# Batch generate GAFs for all scenarios missing golden answers.
# Usage: ./tools/batch_generate_gaf.sh [--dry-run] [--no-irr]
#
# Requires: IRR venv with anthropic installed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IRR_PYTHON="/Users/bdsm4/code/work/bds_repos/Tier_1/investment-research-rag/.venv/bin/python"
EXTRA_ARGS="${*}"

cd "$REPO_ROOT"

# Find scenarios without matching golden answers
TOTAL=0
GENERATED=0
SKIPPED=0
FAILED=0
ERRORS=""

echo "=== Batch GAF Generation ==="
echo "Repo: $REPO_ROOT"
echo "Args: $EXTRA_ARGS"
echo ""

for scenario in evals/*/scenarios/*.yaml; do
    # Derive expected golden answer path
    module_dir="$(dirname "$(dirname "$scenario")")"
    scenario_name="$(basename "$scenario" .yaml)"
    golden_answer="$module_dir/golden_answers/$scenario_name.md"

    TOTAL=$((TOTAL + 1))

    if [ -f "$golden_answer" ]; then
        echo "[SKIP] $scenario_name (GAF exists)"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    echo ""
    echo "[GEN] $scenario_name ($scenario)"
    if "$IRR_PYTHON" -m tools.generate_gaf \
        --scenario "$scenario" \
        --no-sift \
        $EXTRA_ARGS 2>&1; then
        GENERATED=$((GENERATED + 1))
        echo "[OK]  $scenario_name"
    else
        FAILED=$((FAILED + 1))
        ERRORS="$ERRORS\n  - $scenario_name"
        echo "[FAIL] $scenario_name"
    fi

    # Brief pause to avoid API rate limits
    sleep 2
done

echo ""
echo "=== Summary ==="
echo "Total scenarios: $TOTAL"
echo "Skipped (GAF exists): $SKIPPED"
echo "Generated: $GENERATED"
echo "Failed: $FAILED"
if [ -n "$ERRORS" ]; then
    echo -e "Errors:$ERRORS"
fi
