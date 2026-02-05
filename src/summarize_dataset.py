import json
from collections import Counter
from pathlib import Path

def main():
    file_path = Path(__file__).parent.parent / "results" / "final_results.jsonl"
    if not file_path.exists():
        print(f"Error: {file_path} does not exist.")
        return

    module_counts = Counter()
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            # Standardize module name extraction
            scenario_id = data.get("scenario_id", "unknown")
            module = scenario_id.split("-")[0] if "-" in scenario_id else scenario_id
            module_counts[module] += 1

    print("\n--- Dataset Summary Statistics ---")
    for mod, count in sorted(module_counts.items()):
        print(f"Module {mod:25}: {count} pair(s)")
    print("-" * 35)
    print(f"Total Unique Pairs: {sum(module_counts.values())}\n")

if __name__ == "__main__":
    main()
