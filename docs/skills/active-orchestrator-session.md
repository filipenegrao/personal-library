# Active Orchestrator Session

Paste this content at the start of a new Orchestrator conversation.
Updated by Orchestrator at the end of each completed feature.

## Session goal

Run the Builder → QA cycle for the current active feature and close the delivery
with validated commit + push.

## Read in this exact order

1. AGENTS.md
2. HANDOFF.md
3. STATUS.json
4. docs/architecture.md
5. docs/skills/active-builder-task.md
6. docs/skills/active-qa-review.md

## Active feature for this session

- Feature ID: back-001
- Feature name: FastAPI setup — config, database, main
- Domain: backend-core

## Orchestration steps

1. Trigger Builder using harness/prompts/builder.md + docs/skills/active-builder-task.md.
2. Validate implementation against architecture and scope.
3. Trigger QA using harness/prompts/qa.md + docs/skills/active-qa-review.md.
4. If QA rejects, loop corrections through Builder until approved.
5. Run backend sensors: `ruff check .`, `mypy .`, `pytest` from `api/`.
6. Ensure HANDOFF.md and STATUS.json are updated.
7. Commit with Conventional Commits.
8. Push to origin/main (once remote is set up).
9. Rotate active files for the next feature:
   - docs/skills/active-builder-task.md
   - docs/skills/active-qa-review.md
   - docs/skills/active-orchestrator-session.md

## Guardrails

1. Do not allow scope creep.
2. Do not skip QA for the active feature.
3. Do not conclude with failing sensors (or document why sensors cannot run).
4. Do not leave branch ahead/dirty after push.

## Exit criteria

1. QA verdict is approved (or approved with non-blocking notes).
2. Sensors are green (or absence documented if code not yet scaffolded).
3. Commit and push are complete.
4. Branch is synchronized (main...origin/main).
5. Next session files are pre-rotated.
