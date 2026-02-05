#!/usr/bin/env python3
"""Extract preference pairs from scenarios for RLHF training."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml

def load_scenario(path: Path) -> dict:
    """Load a scenario YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)

def format_field(field_data) -> str:
    """Helper to convert strings, lists, or dicts from YAML into a clean string."""
    if isinstance(field_data, str):
        return field_data.strip()
    if isinstance(field_data, list):
        return "\n".join([f"- {item}" for item in field_data])
    if isinstance(field_data, dict):
        return "\n".join([f"{k}: {v}" for k, v in field_data.items()])
    return str(field_data)

def build_prompt(scenario: dict) -> str:
    """Build the evaluation prompt, handling complex YAML objects."""
    parts = []
    
    # Handle the 'observed_relationship' or nested 'context'
    observed = scenario.get("observed_relationship")
    if not observed and "context" in scenario:
        pm_belief = format_field(scenario["context"].get("pm_belief", ""))
        parts.append("## PM Belief")
        parts.append(pm_belief)
    elif observed:
        parts.append("## Observed Relationship")
        parts.append(format_field(observed))

    # Handle the 'task' (which was causing the crash)
    if "task" in scenario:
        parts.append("\n## Task")
        parts.append(format_field(scenario["task"]))

    return "\n\n".join(parts)

def extract_preference_pair(scenario: dict) -> dict:
    """Extract a preference pair, handling nested anchor_answers."""
    prompt = build_prompt(scenario)
    
    # Use .get() to avoid KeyErrors and format_field to avoid AttributeErrors
    strong = scenario.get("anchor_answers", {}).get("strong", {})
    failing = scenario.get("anchor_answers", {}).get("failing", {})
    
    return {
        "scenario_id": scenario.get("id", "unknown"),
        "prompt": prompt,
        "chosen": format_field(strong.get("response", "")),
        "rejected": format_field(failing.get("response", "")),
        "chosen_score": strong.get("score", 5),
        "rejected_score": failing.get("score", 1),
    }

def get_all_scenarios(evals_dir: Path, module: str | None = None) -> list[Path]:
    """Get all scenario YAML files, optionally filtered by module."""
    if module:
        module_path = evals_dir / module / "scenarios"
        return list(module_path.glob("*.yaml"))
    return list(evals_dir.rglob("scenarios/*.yaml"))

# ... (existing imports and functions) ...

def main():
    parser = argparse.ArgumentParser(description="Extract preference pairs for RLHF")
    parser.add_argument("--module", type=str, help="Module ID")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent.parent / "results" / "results.jsonl", help="Master results file")
    
    args = parser.parse_args()
    
    evals_dir = Path(__file__).parent.parent / "evals"
    scenarios_paths = get_all_scenarios(evals_dir, args.module)
    
    pairs = []
    for path in scenarios_paths:
        scenario = load_scenario(path)
        pairs.append(extract_preference_pair(scenario))

    # CHANGE: Open in 'a' (append) mode instead of 'w'
    with open(args.output, "a") as f:
        for pair in pairs:
            f.write(json.dumps(pair) + "\n")
            
    print(f"Successfully processed {len(pairs)} scenarios.")
    print(f"Current size of {args.output}: {args.output.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()