#!/bin/bash
#
# Run the full Investment Workflow Evaluations pipeline
#
# Usage: ./run_all.sh
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Investment Workflow Evaluations${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Setup virtual environment if needed
if [ ! -d ".venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import yaml" 2>/dev/null; then
    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# Ensure results directory exists
mkdir -p results

echo -e "${GREEN}[1/5] Listing available modules...${NC}"
echo
python -m tools.eval_runner list
echo

echo -e "${GREEN}[2/5] Running evaluation on sample AI response...${NC}"
echo
python -m tools.eval_runner run \
    --module 01_equity_thesis \
    --scenario biotech_phase3_catalyst \
    --input examples/sample_ai_response.md \
    --output-dir results
echo

echo -e "${GREEN}[3/5] Grading golden answer with scenario context...${NC}"
echo
python -m tools.grading_engine grade \
    --submission evals/01_equity_thesis/golden_answers/biotech_phase3_catalyst.md \
    --rubric evals/01_equity_thesis/rubrics/standard.yaml \
    --scenario evals/01_equity_thesis/scenarios/biotech_phase3_catalyst.yaml
echo

echo -e "${GREEN}[4/5] Extracting RLHF preference pairs...${NC}"
echo
python -m src.extract_pairs --output results/preference_pairs.jsonl
echo

echo -e "${GREEN}[5/5] Summarizing dataset...${NC}"
echo
python -m src.summarize_dataset
echo

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Pipeline complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo "Results saved to: results/"
ls -la results/
