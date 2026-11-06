#!/usr/bin/env bash
# Run every task prompt in docs/experiments/tasks with one pi headless model.
# Usage: run_pi_tasks.sh <pi-model> <model-tag> <run-dir> [task ...]
# Idempotent: a task whose <run-dir>/<model-tag>/<task>.svg exists is skipped.
# Each task is one pi process capped at 9 minutes (exit 124 or 142 = timed out; re-run resumes).
set -u
model=$1; tag=$2; run_dir=$(cd "$3" && pwd); shift 3
repo=$(cd "$(dirname "$0")/../../.." && pwd)
tasks=("$@"); [ ${#tasks[@]} -eq 0 ] && tasks=($(cd "$repo/docs/experiments/tasks" && ls *.md | sed 's/\.md$//'))
# macOS has no timeout(1); fall back to gtimeout or a perl alarm wrapper.
if command -v timeout >/dev/null; then cap() { timeout "$@"; }
elif command -v gtimeout >/dev/null; then cap() { gtimeout "$@"; }
else cap() { local s=${1%m}; shift; perl -e 'alarm shift; exec @ARGV' $((s*60)) "$@"; }; fi
out="$run_dir/$tag"; mkdir -p "$out/logs" "$out/sessions"
for task in "${tasks[@]}"; do
  [ -s "$out/$task.svg" ] && { echo "skip $tag/$task"; continue; }
  sed -e "s#@@REPO@@#$repo#g" -e "s#@@OUT@@#$out#g" -e "s#@@TASK@@#$task#g" \
    "$repo/docs/experiments/tasks/$task.md" > "$out/logs/$task.prompt.md"
  start=$(date +%s)
  (cd "$out" && cap 9m pi -p --mode json --model "$model" -ne -ns --offline \
     --session-dir "$out/sessions" --session-id "$task" @"$out/logs/$task.prompt.md" \
     </dev/null >> "$out/logs/$task.events.jsonl" 2>> "$out/logs/$task.stderr")
  code=$?
  echo "$(date '+%H:%M:%S') $tag/$task exit=$code seconds=$(( $(date +%s) - start )) svg=$([ -s "$out/$task.svg" ] && echo yes || echo no)"
done
