#!/usr/bin/env python3
"""Combine the owner's and the orchestrator's rankings into one score table.

Usage:
    python3 -I docs/experiments/scripts/score_rankings.py RUN_DIR

Reads RUN_DIR/ranking.json (owner, from rank_server.py) and
RUN_DIR/ranking-orchestrator.json (same format). Only tasks with status
"ranked" count, and a task the owner marked "tie" is skipped entirely. Combined rank per task = (2 * owner rank + orchestrator rank) / 3;
the owner weighs double because aesthetics are subjective and the owner
grades last. Prints a Markdown table: per-task combined rank, then the mean.
"""
import json
import sys
from pathlib import Path

WEIGHTS = {"ranking.json": 2, "ranking-orchestrator.json": 1}


def load(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {task: entry["order"] for task, entry in data.items()
            if isinstance(entry, dict) and entry.get("status") == "ranked"}


def owner_ties(run_dir):
    path = run_dir / "ranking.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    return {task for task, entry in data.items() if isinstance(entry, dict) and entry.get("status") == "tie"}


def main():
    run_dir = Path(sys.argv[1])
    rankings = {name: load(run_dir / name) for name in WEIGHTS}
    # The owner grades last: a task the owner marked "tie" is not scored at all.
    tasks = sorted(set().union(*rankings.values()) - owner_ties(run_dir))
    models = sorted({m for r in rankings.values() for order in r.values() for m in order})
    combined = {m: {} for m in models}
    for task in tasks:
        for model in models:
            total = weight = 0
            for name, ranking in rankings.items():
                if task in ranking and model in ranking[task]:
                    total += WEIGHTS[name] * (ranking[task].index(model) + 1)
                    weight += WEIGHTS[name]
            if weight:
                combined[model][task] = total / weight
    print("| Model | " + " | ".join(tasks) + " | Mean |")
    print("| --- |" + " --- |" * (len(tasks) + 1))
    for model in sorted(models, key=lambda m: sum(combined[m].values()) / max(len(combined[m]), 1)):
        cells = [f"{combined[model][t]:.2f}" if t in combined[model] else "-" for t in tasks]
        mean = sum(combined[model].values()) / max(len(combined[model]), 1)
        print(f"| {model} | " + " | ".join(cells) + f" | {mean:.2f} |")


if __name__ == "__main__":
    main()
