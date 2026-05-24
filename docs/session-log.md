# Session log

Append-only dated notes. Use [`HANDOFF.md`](../HANDOFF.md) for the **current** snapshot between sessions.

## 2026-04-29 — Goals 7 & 8: npm CLI + dashboard usage telemetry

### What was done

**Goal 7 — `start-harness` npm CLI**
- Added `start-harness-project/cli/` — zero-runtime-dep npm package
- `bin/index.js`: Python 3.12+ guard (stdout+stderr combined), delegates to bundled `init_project.py`
- `scripts/bundle.js`: copies scaffold assets; generates blank HANDOFF.md; removes user-notes.md (prevents session state from leaking into published template)
- `cli/README.md`: install, usage, stacks table, dev instructions
- `start-harness-project/README.md`: Quick start now shows Option A (npm) + Option B (python3 direct)
- `.github/workflows/publish-cli.yml`: publishes to npmjs.com on `v*` tags using `NODE_AUTH_TOKEN` secret

**Goal 8 — Dashboard usage telemetry + UI polish**
- `lib/db.ts`: `usage_events` table, `session_start` column with migration guard, `UsageEvent` type
- `lib/types.ts`: 23-entry `MODEL_LABELS` (Claude, OpenAI, Qwen, Gemini families), `session_start` on `PipelineRun`
- `app/api/events/route.ts`: sets `session_start` on planning events; pushes full run + last 10 transitions inline in SSE (single round-trip)
- `hooks/usePipeline.ts`: merges SSE payload with explicit `merged` flag; fallback to full GET on malformed payload
- `app/api/usage/route.ts`: POST stores telemetry (fallback to most recent active run); GET returns events + totals
- `components/RunCard.tsx`: client component with click-to-expand (full title, all transitions, progress %, session start)
- `components/StatusBar.tsx`: live bar showing model, input/output tokens, session elapsed, task %
- `app/api/status-json/route.ts`: reads `STATUS.json` (`$HARNESS_STATUS_JSON` env or `<cwd>/STATUS.json`)
- `scripts/usage-event.sh`: core POST to `/api/usage`
- `scripts/claude-usage-hook.sh`: Claude Code PostToolUse hook
- `scripts/codex-usage-adapter.sh` / `opencode-usage-adapter.sh`: CLI wrappers with JSON usage parsing

**PR:** https://github.com/filipenegrao/combo-harness/pull/4 (`pr/6-dashboard-integration` → `main`)

### Decisions

- `bundle.js` generates a blank HANDOFF.md instead of copying the live one — prevents session state from shipping with the npm package
- `usePipeline.ts` fallback uses explicit `merged = false` flag (not implicit fallthrough) — QA required this for clarity
- Codex/OpenCode adapters use `export SCRIPT_DIR` before heredoc + `os.environ.get("SCRIPT_DIR")` inside Python — `sys.argv[0]` resolves to `-` in heredoc context
- `set +e` around pipe in adapters to capture `PIPESTATUS[0]` before `set -e` terminates on nonzero exit
- `STATUS.json` task %: computed in JS via reduce, not SQL — keeps DB schema simple
- SSE single round-trip: `POST /api/events` now fetches and pushes `{ run, transitions }` inline to avoid a separate client GET

### Follow-ups

- Tag `v0.1.0` to trigger npm publish: `git tag v0.1.0 && git push origin v0.1.0`
- Register `claude-usage-hook.sh` in `~/.claude/settings.json` PostToolUse hooks
- Symlink `~/.claude/hooks/usage-event.sh` → `agents-dashboard/scripts/usage-event.sh`
- Document new scripts in `agents-dashboard/README.md`

## YYYY-MM-DD — Title

### What was done

### Decisions

### Follow-ups

---

> Note: entries above this line (2026-04-29) are template/combo-harness carryover from the scaffold. They do not reflect personal-library work.

---

## 2026-05-24 — repo-001: Repository state reconciliation

### What was done

- Replaced stale `STATUS.json` (described mail-checker-ai) with a new personal-library feature tracker derived from the approved spec and implementation plan.
- Rewrote `CLAUDE.md`: accurate project description, real stack, correct repo structure, real commands.
- Rewrote `docs/architecture.md`: FastAPI layer model (config → database → models → services → routers → main), Next.js layer model (lib → components → app), DB tables, runtime flows, guardrails.
- Rewrote `docs/progress.md`: aligned with new STATUS.json feature IDs and domains.
- Rewrote `docs/design.md`: UI direction, layout mockups, typography, token guidance, component patterns, responsive strategy, PDF label notes.
- Updated `HANDOFF.md` with reconciliation results and setup gaps.
- Updated all three active-skill files (`active-orchestrator-session.md`, `active-builder-task.md`, `active-qa-review.md`) to point to personal-library project and next real feature (repo-002).
- Fixed broken references: active skill files had `docs/architecture/overview.md` (nonexistent path); corrected to `docs/architecture.md`.

### Decisions

- No application code created in this session — scope was documentation/state reconciliation only.
- `repo-001` is a reconciliation meta-feature; marked `in_progress` during session; next agent should close it to `done` when opening repo-002.
- Active skills now target `repo-002` (project scaffold + git init) as the next implementation slice.
- Old combo-harness session-log entries left intact (append-only policy); annotated with carryover note above.

### Remaining setup gaps

- No `.git/` directory exists — `git init` is repo-002's first action.
- No `api/` or `web/` directories exist yet.
- No sensors runnable until code is scaffolded and dependencies installed.

### Follow-ups

- Run repo-002: `git init`, `.gitignore`, directory scaffold, first commit.
- Then begin back-001: FastAPI pyproject.toml, config, database, main.

---

## 2026-05-24 — repo-001 correction pass (QA rejection remediation)

### What was done

QA rejected the initial reconciliation for two blocking reasons: (1) repo-001 status was inconsistent across trackers, (2) import scope from the approved spec was dropped without an ADR.

**Blocking fixes:**
- `STATUS.json`: repo-001 → `done`; added `back-011` (CSV + BibTeX import, MVP scope per spec Module 6); removed open decision about CSV import deferral
- `docs/progress.md`: marked repo-001 done; added back-011 import item under Backend — Catalog Features
- `HANDOFF.md`: clarified repo-001 is done; documented correction pass work and CI gap

**Non-blocking carryover docs corrected:**
- `docs/dashboard-integration.md`: replaced combo-harness-specific symlink instructions with a generic repo-appropriate usage guide; noted the carryover origin
- `docs/skills/README.md`: removed Gmail-triage planned skills list; updated with personal-library-appropriate candidate skills
- `.github/workflows/harness-ci.yml`: rewritten for `api/` + `web/` layout — separate backend/frontend jobs, PostgreSQL service container for tests, correct working-directory scoping; header note that jobs fail until scaffold exists

### Decisions

- Import (CSV + BibTeX) is confirmed MVP scope: spec Module 6 is explicit. No deferral, no ADR required.
- CI jobs will fail until api/ and web/ are scaffolded — expected; documented in workflow header.

### Remaining setup gaps

- No `.git/` directory; no `api/` or `web/` code. Same as previous entry — repo-002 resolves this.
- No sensors runnable. Explicitly documented; not a false pass.

### Follow-ups

- Begin repo-002: `git init`, `.gitignore`, scaffold `api/` + `web/` directories.
- back-011 import implementation happens in the same domain slice as back-010 export.
