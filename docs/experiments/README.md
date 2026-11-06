# Experiments

Lab notebook for developing `SKILL.md`. Everything needed to rerun an
experiment is in this folder; raw outputs go to `tmp/` (gitignored).

| Folder | Holds |
| --- | --- |
| `daily/` | One log per day (`YYYY-MM-DD.md`): what ran, what broke, what changed in `SKILL.md` |
| `features/` | One note per researched feature or idea, kept up to date across days |
| `releases/` | One note per released `SKILL.md` version with its frozen score table |
| `tasks/` | Test prompts, one file per task; `@@REPO@@`, `@@OUT@@`, `@@TASK@@` are filled in by the runner |
| `fixtures/` | Input SVGs for `edit` and `animate` tasks |
| `scripts/` | Runner and acceptance check |

## Test matrix

Each iteration runs every task in `tasks/` with each model:

| Model tag | How it runs |
| --- | --- |
| `claude-opus`, `claude-sonnet`, `claude-haiku` | Claude Code subagent per model; it reads the per-task prompt files |
| `gpt-6-luna` | pi headless, `litellm-res/gpt-6-luna:medium` |
| `deepseek-v4.1-flash` | pi headless, `ollama-cloud/deepseek-v4.1-flash` |

Reference photos are public images downloaded into `tmp/refs/` (sources and
licenses listed in the daily log of the day they were added).

## Run an iteration

```bash
RUN=tmp/runs/iteration-01-skill-v0.1          # iteration number + SKILL.md version
mkdir -p $RUN
# pi models: one process per task, each capped at 9 min; reruns skip finished tasks
docs/experiments/scripts/run_pi_tasks.sh litellm-res/gpt-6-luna:medium gpt-6-luna $RUN
docs/experiments/scripts/run_pi_tasks.sh ollama-cloud/deepseek-v4.1-flash deepseek-v4.1-flash $RUN
# Claude models: fill the prompts into $RUN/<model-tag>/logs/<task>.prompt.md with the
# same sed substitution as the runner, then give one subagent per model the list.
# Acceptance check + renders + one contact sheet per task
python3 -I docs/experiments/scripts/svg_check.py $RUN --render
# Owner ranking: drag outputs best → worst; saved to $RUN/ranking.json
python3 -I docs/experiments/scripts/rank_server.py $RUN   # http://127.0.0.1:8765/
# Combined score: owner x2 + orchestrator x1 ($RUN/ranking-orchestrator.json, same format)
python3 -I docs/experiments/scripts/score_rankings.py $RUN
```

## Acceptance

Two stages:

1. **Automatic** (`svg_check.py`): valid XML, `viewBox`, unique ids, nothing
   forbidden (`script`, `foreignObject`, `image`, event attributes, external
   `href`, editor metadata). Also reports structure metrics: share of
   primitives among shapes, path command count, coordinates with more than
   two decimals, named groups, animation and reduced-motion support.
2. **Visual ranking** on the skill's four criteria (silhouette, geometry,
   prompt adherence, legibility at final size). The orchestrating agent ranks
   from the renders; the owner ranks blind on `rank_server.py`. Aesthetics
   are subjective, so both count: combined rank = (2 × owner + 1 ×
   orchestrator) / 3 (`score_rankings.py`). Tasks marked `tie` are not scored
   and flag a task that needs to be made harder.
