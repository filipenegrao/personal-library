# Agents Dashboard Integration

> **Status:** Optional. This project supports the Agents Dashboard for pipeline observability,
> but it is not required for development or deployment.

---

## Overview

The Agents Dashboard is a local real-time monitor for the Builder / QA / Orchestrator pipeline.
When running, it tracks stage transitions and agent handoffs via a browser UI.

Integration is **optional** — all hook scripts are no-ops if the dashboard is not running.

---

## Using the dashboard with this project

This project follows the standard harness pipeline convention. To use the dashboard:

1. Start the dashboard (see its own repo for setup instructions).
2. Fire events from orchestrator/builder/QA sessions using:

```bash
~/.claude/hooks/pipeline-event.sh <stage> <agent_role> [tool] [notes] [title] [model]
```

### Pipeline stages

```
idle → planning → delegated_to_builder → builder_working →
sent_to_qa → qa_reviewing → final_check → committed → done
```

### Example

```bash
~/.claude/hooks/pipeline-event.sh planning orchestrator claude-code "Scoping repo-002" "personal-library: scaffold" "claude-sonnet-4-6"
~/.claude/hooks/pipeline-event.sh delegated_to_builder orchestrator claude-code "" "repo-002" "claude-sonnet-4-6"
~/.claude/hooks/pipeline-event.sh builder_working builder claude-code "Implementing scaffold" "" "repo-002" "claude-sonnet-4-6"
~/.claude/hooks/pipeline-event.sh sent_to_qa orchestrator claude-code "" "repo-002" "claude-sonnet-4-6"
```

`git commit` and `git push` are auto-detected when the bash hook is registered.

---

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `PIPELINE_DASHBOARD_URL` | `http://localhost:3000` | Dashboard base URL |
| `PIPELINE_RUN_ID_FILE` | `<git-root>/.harness/pipeline_run_id` | Persisted current run ID |

---

## Note

The previous version of this file contained combo-harness-specific setup instructions
(symlink paths referencing `~/combo-harness/`). Those were template carryover and
have been replaced with the generic usage pattern above.
