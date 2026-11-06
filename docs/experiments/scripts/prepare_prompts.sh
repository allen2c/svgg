#!/usr/bin/env bash
# Fill the task prompts for a model that is driven by hand (e.g. a Claude subagent).
# Usage: prepare_prompts.sh <run-dir> <model-tag> [task ...]
# Writes <run-dir>/<model-tag>/logs/<task>.prompt.md and prints their paths.
set -eu
run_dir=$(cd "$1" && pwd); tag=$2; shift 2
repo=$(cd "$(dirname "$0")/../../.." && pwd)
tasks=("$@"); [ ${#tasks[@]} -eq 0 ] && tasks=($(cd "$repo/docs/experiments/tasks" && ls *.md | sed 's/\.md$//'))
out="$run_dir/$tag"; mkdir -p "$out/logs"
for task in "${tasks[@]}"; do
  sed -e "s#@@REPO@@#$repo#g" -e "s#@@OUT@@#$out#g" -e "s#@@TASK@@#$task#g" \
    "$repo/docs/experiments/tasks/$task.md" > "$out/logs/$task.prompt.md"
  echo "$out/logs/$task.prompt.md"
done
