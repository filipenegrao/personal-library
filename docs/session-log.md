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

---

## 2026-05-24 — repo-002: Project scaffold

### What was done

- Created root `.gitignore` with Python patterns (`__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `dist/`, `.env`), Node patterns (`node_modules/`, `.next/`, `.env.local`), logs (`*.log`), and macOS artifacts (`.DS_Store`).
- Scaffolded `api/` directory tree:
  - `api/app/{models,schemas,routers,services}/` with `__init__.py` files in each subpackage
  - `api/alembic/versions/`
  - `api/tests/`
  - 33 placeholder `.py` files matching the approved plan's file structure (main.py, config.py, database.py, auth.py, deps.py, 4 model files, 4 schema files, 6 router files, 5 service files, 9 test files), plus 3 empty `__init__.py` files — 36 `.py` files total
- Scaffolded `web/` directory tree:
  - `web/src/{app,components,lib}/`
  - Route directories: `login/`, `catalog/[id]/`, `books/new/`, `loans/`, `labels/`
- No application logic added — all placeholder files are empty (0 bytes).
- Git was already initialized before this slice (root commit on `main` from repo-001 reconciliation).
- Updated `STATUS.json`: repo-002 → `done`, foundation domain → `done`, release_phase → `scaffold-complete`.
- Updated `docs/progress.md`: repo-002 checkbox checked.
- Rewrote `HANDOFF.md` with current session snapshot.

### Decisions

- Placeholder files kept empty per task constraint ("no application logic"). The `__init__.py` files are also empty — no imports or `__all__` lists needed at scaffold stage.
- Web route directories created as bare directories only — no `page.tsx` or `layout.tsx` files. Those belong in front-001 and subsequent frontend features.

### Remaining setup gaps

- No sensors runnable: no `pyproject.toml`, no `package.json`, no venv, no node_modules.
- CI workflow (`.github/workflows/harness-ci.yml`) will fail until project config files and dependencies are installed.

### Follow-ups

- **back-001**: FastAPI setup — pyproject.toml, .env.example, config, database, main, deps.
- **front-001**: Next.js 15 scaffold — create-next-app, Tailwind v4, shadcn/ui, auth middleware.

---

## 2026-05-24 — back-001: FastAPI setup (config, database, main)

### What was done

- Created `api/pyproject.toml` with all backend production and dev dependencies.
  - Used `[project.optional-dependencies]` instead of `[dependency-groups]` for pip compatibility (pip 24.0).
  - Added `[tool.setuptools.packages.find]` with `include = ["app*"]` to avoid flat-layout collision with `alembic/`.
  - Configured `[tool.pytest.ini_options]` (`asyncio_mode = "auto"`), `[tool.ruff]` (line-length 100), `[tool.mypy]` (ignore_missing_imports, explicit_package_bases).
- Created `api/.env.example` — 8 env vars matching the approved plan.
- Implemented `api/app/config.py` — `Settings` class via pydantic-settings, reads from `.env`.
- Implemented `api/app/database.py` — `Base` (DeclarativeBase), `make_engine()`, `make_session_factory()`.
- Implemented `api/app/main.py` — FastAPI app shell with async lifespan (engine/session factory setup/teardown), CORS middleware (allow localhost:3000), router registration for all 6 route groups.
- Implemented `api/app/deps.py` — `get_db` (async session from request state) and `get_current_user` (Bearer token validation via auth.verify_token).
- Added structural stubs required for clean imports:
  - `api/app/auth.py`: `verify_token()` raises `NotImplementedError` (back-002 replaces this).
  - All 6 router files (`auth.py`, `books.py`, `tags.py`, `loans.py`, `labels.py`, `export.py`): minimal `router = APIRouter()`.
- Created Python 3.12 virtual environment in `api/.venv/`. All dependencies installed successfully via `pip install -e ".[dev]"`.
- Sorted out a `mypy` false positive on `Settings()` (env file not visible to type checker) with `# type: ignore[call-arg]`.

### Decisions

- Router stubs added during back-001 rather than later: without them, `main.py` import would fail at static analysis (ruff/mypy). These stubs contain no business logic — just `from fastapi import APIRouter` + `router = APIRouter()`.
- `deps.py` imports `verify_token` from `auth.py` (using the stub) rather than deferring auth wiring. This keeps the layer dependency chain correct (deps → auth) and avoids later refactoring.
- `[[tool.mypy] explicit_package_bases = true` added to fix the "found twice" error caused by `alembic/` and `app/` sharing the same directory root.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 36 source files |
| `pytest` | 0 tests collected — **exit code 5** (not green) |

### Remaining setup gaps

- No `.env` file — `.env.example` must be copied and filled with real PostgreSQL credentials.
- PostgreSQL not running locally — server startup blocked until DB is available (back-003).
- `pytest` exits with code 5 (0 tests collected) — each backend feature will populate its respective test file.
- Frontend not yet scaffolded (front-001).

### Follow-ups

- **back-002**: JWT auth — implement auth.py fully, auth router, test_auth.py.
- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-004**: pytest fixtures with isolated test database.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-24 — back-001 QA correction pass

### What was done

QA rejected the initial back-001 for one blocking reason: `pytest` exited with code 5 (0 tests collected), but the repo state claimed sensors were green. Also noted a docs-accuracy issue: HANDOFF misstated the first startup blocker.

**Blocking fix:**
- Created `api/tests/test_app.py` — minimal foundation smoke test that sets required env vars, imports the FastAPI app, and verifies title and OpenAPI schema generation.
- `pytest` now exits 0 with 1 test passed.

**Docs correction:**
- Corrected `HANDOFF.md` startup blocker order: `app/config.py` instantiates `Settings()` at module import time, which requires `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, `JWT_SECRET`. Without these, any import of the app module fails before reaching DB or lifespan logic.
- Corrected `docs/session-log.md` back-001 entry: sensor table now shows "exit code 5 (not green)" instead of the misleadingly neutral "0 tests collected".
- Updated `STATUS.json`: `tests: true`, notes include the QA correction pass.
- Removed stale "pytest collects 0 tests" gap from HANDOFF.md setup issues.

### Decisions

- The smoke test uses `os.environ.setdefault` to satisfy `pydantic-settings` required fields at import time. This is a minimal, legitimate test pattern — no DB needed, no HTTP client needed.
- Kept `back-001` status as `done` — the blocker was a missing test, not a broken implementation. The foundation code was correct; only the sensor reporting was wrong.
- The startup blocker correction in HANDOFF now correctly identifies `Settings()` at import time as the first failure mode.

### Sensor results (post-correction)

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found |
| `pytest` | 1 passed, exit code 0 |

### Follow-ups

- **back-002**: JWT auth — implement auth.py fully, auth router, test_auth.py.
- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-004**: pytest fixtures with isolated test database.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-24 — back-001 QA correction pass #2 (import fix)

### What was done

QA reran `pytest` and the smoke test failed: `ModuleNotFoundError: No module named 'app'`. The `api/app/` directory had no `__init__.py`, so `app` was only discoverable via the editable install link (`pip install -e .`). Without it, the test's `from app.main import app` failed.

**Fix:**
- Created `api/app/__init__.py` (empty) — makes `app` a proper Python package discoverable from the `api/` directory regardless of editable install state.
- Reran all three sensors: `ruff check .` (pass), `mypy .` (pass, 38 source files), `pytest` (1 passed, exit 0).

### Decisions

- `__init__.py` kept empty — no imports or `__all__` needed. It exists purely to declare `app/` as a Python package. This is the minimal, idiomatic fix.
- The editable install still works correctly alongside the `__init__.py`.
- `docs/progress.md` did not need changes — back-001 remained marked done.

### Sensor results (post fix)

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 38 source files |
| `pytest` | 1 passed, exit code 0 |

### Follow-ups

- **back-002**: JWT auth — implement auth.py fully, auth router, test_auth.py.
- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-004**: pytest fixtures with isolated test database.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-24 — backend-core repair: pytest bootstrap + tracker correction

### What was done

- Fixed `pytest` startup for the normal repo workflow by seeding required env vars at the top of `api/tests/conftest.py` before importing `app.config`.
- Repaired malformed `STATUS.json` so the canonical tracker is valid JSON again.
- Corrected tracker and handoff truthfulness around backend sensor execution and local env-file usage.
- Kept the combined backend-core delivery coherent: `back-001`, `back-002`, and `back-004` are the implemented features in the live tree.

### Decisions

- Tests no longer depend on an untracked local `api/.env` file. The required test-only env vars are seeded in `conftest.py`.
- Runtime app startup outside tests still requires real env vars or a local `.env`; only the test bootstrap was made self-contained.
- No additional scope was introduced beyond making the actual `pytest` command pass and repairing the broken docs/state.

### Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 38 source files |
| `source .venv/bin/activate && pytest` | 4 passed, exit code 0 |

### Follow-ups

- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-005**: ISBN EAN-13 validation and normalization.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-24 — back-001 QA correction pass #3 (pytest console script path)

### What was done

QA found that `pytest` (the console script) still failed while `python -m pytest` passed. The console script does not add CWD to `sys.path`, so `app` was not importable.

**Root cause:** Python adds the CWD to `sys.path[0]` when invoked as `python -m pytest`, but the `pytest` console script does not. With `pip install -e .`, an editable link made `app` discoverable for `python -m pytest` but not for the bare `pytest` command.

**Fix:**
- Added `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `api/pyproject.toml` — tells pytest to add the `api/` directory to the Python path for all invocation methods.

### Sensor results (post fix)

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 38 source files |
| `pytest` | 1 passed, exit code 0 |

### Follow-ups

- **back-002**: JWT auth — implement auth.py fully, auth router, test_auth.py.
- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-004**: pytest fixtures with isolated test database.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-24 — back-002 + back-004: JWT auth + test fixtures

### What was done

**back-002 — JWT auth:**
- Implemented `api/app/auth.py` with bcrypt password hashing (`hash_password`, `verify_password`) and JWT encode/decode (`create_access_token`, `verify_token`).
- Implemented `api/app/routers/auth.py` with `POST /auth/login` (validates credentials from env, returns JWT) and `GET /auth/me` (protected test endpoint using `get_current_user` dependency).
- Implemented `api/tests/test_auth.py` with 3 tests (login success, wrong password → 401, protected endpoint without token → 401).

**back-004 — test fixtures:**
- Implemented `api/tests/conftest.py`: `test_engine` (session-scoped, drop/create schema), `db_session` (per-test rollback), `client` (ASGITransport ASGI client with DB override), `auth_client` (pre-authenticated via login).
- Created `personal_library_test` database on local PostgreSQL 18.4 (Homebrew).
- Created `api/.env` with local dev config (gitignored).

### Decisions

- **Switched from passlib to bcrypt**: `passlib v1.7.4` is incompatible with `bcrypt >=5.0`. The `detect_wrap_bug` routine in passlib's bcrypt backend sends a 256+ byte test password, but bcrypt 5+ enforces a 72-byte limit. Using `bcrypt.hashpw`/`bcrypt.checkpw` directly is simpler and avoids the compatibility issue.
- **Added `GET /auth/me` test endpoint**: The plan expected `test_protected_endpoint_without_token` to hit `/books/` for a 403, but no routes have auth dependencies yet. Added a minimal `/auth/me` endpoint that uses `get_current_user` so the token verification can be tested.
- **PostgreSQL 18 vs 17**: Local Homebrew install provides PostgreSQL 18.4 instead of the spec's target 17. SQLAlchemy + asyncpg work with both versions.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 38 source files |
| `pytest` | 4 passed (test_app + 3 auth tests), exit 0 |

### Follow-ups

- **back-003**: SQLAlchemy models + initial Alembic migration.
- **back-005**: ISBN EAN-13 validation and normalization.
- **back-006**: ISBN lookup — Open Library + Google Books.
- **back-007**: Books CRUD with ISBN lookup endpoint.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-25 — back-003: SQLAlchemy models and initial Alembic migration

### What was done

**Models (SQLAlchemy 2 typed ORM):**
- Implemented `api/app/models/book.py` — `Book` model with UUID PK, isbn_13 (indexed), isbn_10, title, subtitle, authors (JSONB with default `[]`), publisher, published_year, language, pages, cover_url, dewey_code, notes, created_at (tz-aware, default UTC now). Relationships: `book_tags` (cascade delete-orphan), `loans`.
- Implemented `api/app/models/tag.py` — `Tag` (UUID PK, unique name, color default `#6366f1`) and `BookTag` (composite PK: book_id + tag_id, FKs to books and tags). Bi-directional relationships.
- Implemented `api/app/models/loan.py` — `Loan` (UUID PK, book_id FK, borrower_name, loaned_at tz-aware default UTC now, due_date nullable, returned_at nullable, notes). Relationship back to Book.
- Implemented `api/app/models/label_template.py` — `LabelTemplate` (UUID PK, name, width_mm default 50.0, height_mm default 30.0, font_size default 8, show_dewey/show_title/show_barcode defaults True, created_at tz-aware).
- Implemented `api/app/models/__init__.py` — exports all 5 models; importing `app.models` registers every table on `Base.metadata`.

**Alembic:**
- Created `api/alembic.ini` — valid config, blank `sqlalchemy.url` (runtime from `settings`).
- Created `api/alembic/env.py` — loads `settings.database_url`, sets `target_metadata = Base.metadata`, imports `app.models` for autogenerate, supports offline and async online migrations.
- Created `api/alembic/versions/0001_initial_schema.py` — concrete migration with `upgrade()` (creates all 5 tables, PKs, FKs, unique constraint on tags.name, index on books.isbn_13) and `downgrade()` (drops all tables in reverse dependency order).

**Supporting fix:**
- Added `bcrypt>=4.0` to `api/pyproject.toml` dependencies — was installed but missing from the dependency list since back-002.

### Decisions

- Used `from __future__ import annotations` + `TYPE_CHECKING` imports to resolve cross-model forward references (Book ↔ BookTag, Book ↔ Loan) without introducing circular imports at runtime.
- Used `sqlalchemy.dialects.postgresql.UUID(as_uuid=True)` for all UUID columns — PostgreSQL-native type with Python `uuid.UUID` mapping.
- Authors field uses `JSON` type with `default=list` in the ORM and `server_default='[]'::jsonb` in the migration — ensures empty array default at both Python and DB levels.
- Migration uses `server_default=sa.text("now()")` for timestamp columns — delegates default to PostgreSQL's `now()` function, consistent with the ORM's `default=lambda: datetime.now(timezone.utc)`.
- Label template defaults (50.0, 30.0, 8, True) are set as ORM Python defaults AND migration server defaults for consistency.
- `alembic.ini` leaves `sqlalchemy.url` blank — runtime URL comes from `settings.database_url` in `env.py`.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 4 passed, exit code 0 |

### Follow-ups

- **back-005**: ISBN EAN-13 validation and normalization.
- **back-006**: ISBN lookup — Open Library + Google Books fallback.
- **back-007**: Books CRUD with ISBN lookup endpoint (will also add model-level integration tests).
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-25 — back-003 corrective pass (QA)

### What was done

Three QA findings addressed:

1. **Type annotation fix**: `authors: Mapped[list]` → `Mapped[list[str]]` in `api/app/models/book.py`. The untyped `list` was too permissive for a column that stores author name strings.

2. **JSONB alignment**: Switched `authors` column from generic `sqlalchemy.JSON` to `sqlalchemy.dialects.postgresql.JSONB` in both the Book model and `0001_initial_schema.py`. The architecture doc explicitly states `authors (jsonb)`. Since no production DB exists, the initial migration was amended directly.

3. **Delete policy documented and made explicit**:
   - `book_tags.book_id → books.id`: Added `ondelete="CASCADE"` to both model FK and migration FK. This aligns DB-level behavior with the existing ORM `cascade="all, delete-orphan"` on `Book.book_tags`. Deleting a book now correctly cascades to delete its tag associations at both levels.
   - `book_tags.tag_id → tags.id`: Added `ondelete="RESTRICT"` — was previously implicit (NO ACTION). Prevents deleting a tag that is still associated with books.
   - `loans.book_id → books.id`: Left as implicit RESTRICT (no `ondelete` clause). This is an **open decision** for `back-008` — should deleting a book preserve its loan history, cascade-delete it, or set it to NULL? Currently, PostgreSQL will reject a book delete if loans reference it.

### Decisions

- Amending `0001_initial_schema.py` directly is safe because no production database has been deployed with this migration. The repo is pre-first-real-deploy.
- `ondelete="CASCADE"` on `book_tags.book_id` mirrors the ORM cascade and is defensive: if someone bypasses the ORM (raw SQL delete), the DB still enforces the expected behavior.
- `ondelete="RESTRICT"` on `book_tags.tag_id` is a defensive guard: deleting a tag should not silently destroy book associations. This is the safe default for a catalog app.
- `loans.book_id` delete policy is deferred to `back-008` because the product spec doesn't define whether loan history should survive book deletion. Both RESTRICT (protect history) and CASCADE (clean removal) are reasonable; the implementer must reconcile with the catalog workflow.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 4 passed, exit code 0 |

### Follow-ups

- **back-008**: Tags and loans CRUD — must resolve `loans.book_id` FK delete policy.
- **back-005**: ISBN EAN-13 validation and normalization.

---

## 2026-05-25 — back-005: ISBN EAN-13 validation and normalization

### What was done

- Implemented `api/app/services/isbn_validate.py`:
  - `normalize_isbn(raw: str) -> str | None` — strips spaces and hyphens via regex, returns digits-only ISBN for valid 10 or 13 digit shapes, `None` for invalid input.
  - `validate_isbn13(isbn: str) -> bool` — standard EAN-13 checksum: alternating weights 1/3 on first 12 digits, check digit mod 10.
- Implemented `api/tests/test_isbn_validate.py` — 6 unit tests:
  1. valid ISBN-13 (`9780306406157` → True)
  2. wrong checksum (`9780306406150` → False)
  3. too short (`978030640615` → False)
  4. normalize with hyphens (`978-0-306-40615-7` → `9780306406157`)
  5. normalize with spaces (`978 0 306 40615 7` → `9780306406157`)
  6. invalid input (`not-an-isbn` → None)

### Decisions

- Used the straightforward implementation from the plan — `re.sub` for stripping, weighted sum for checksum.
- `normalize_isbn` accepts both 10 and 13 digit lengths because downstream flows (back-006 ISBN lookup, back-007 CRUD) may receive either input format. The function delegates format-specific validation to `validate_isbn13`.
- No external dependencies beyond stdlib `re`.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 10 passed (4 existing + 6 new), exit code 0 |

### Follow-ups

- **back-006**: ISBN lookup — Open Library + Google Books fallback.
- **back-007**: Books CRUD with ISBN lookup endpoint.
- **back-008**: Tags and loans CRUD — must resolve `loans.book_id` FK delete policy.

---

## 2026-05-25 — back-005 corrective pass (QA)

### What was done

QA rejected `back-005` for a bug in `normalize_isbn()`:

- The line `digits[:12].isdigit()` only checked the first 12 characters of the normalized string. For a 13-character input like `"978030640615X"`, the slice `[:12]` was all digits, so the check passed and the function returned the non-digit string `"978030640615X"` instead of `None`.

**Fix:**

- Changed `digits[:12].isdigit()` → `digits.isdigit()` — validates the entire normalized string.
- Added regression test `test_normalize_isbn_nondigit_last_char` asserting `normalize_isbn("978030640615X") is None`.

**Design note:** ISBN-10 values ending in `X` (a valid checksum digit in ISBN-10) are intentionally rejected by `normalize_isbn`. This function's contract is digits-only normalization; ISBN-10 `X` handling is not in scope for this slice.

### Decisions

- Used the minimal fix: replace the partial digit slice with a full `isdigit()` call. The length check already guards against empty strings, so `isdigit()` on the full string is safe.
- Did not broaden `normalize_isbn` to accept ISBN-10 trailing `X` — that would change the contract and expand scope.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 11 passed (7 ISBN tests), exit code 0 |

### Follow-ups

- **back-006**: ISBN lookup — Open Library + Google Books fallback.
- **back-007**: Books CRUD with ISBN lookup endpoint.
- **back-008**: Tags and loans CRUD — must resolve `loans.book_id` FK delete policy.

---

## 2026-05-25 — back-006: ISBN lookup — Open Library + Google Books fallback

### What was done

- Implemented `api/app/services/isbn_lookup.py`:
  - `BookData` dataclass — 10 fields (title, authors, publisher, published_year, pages, language, cover_url, isbn_13, isbn_10, dewey_code).
  - `lookup_isbn(isbn: str) -> BookData | None` — tries Open Library first, falls back to Google Books on miss.
  - `_try_open_library(isbn: str) -> BookData | None` — queries `https://openlibrary.org/api/books` with `bibkeys=ISBN:{isbn}`, `format=json`, `jscmd=data`. Parses `title`, `authors[].name`, first publisher, year from `publish_date` (regex), `number_of_pages`, cover URL (medium or small). Returns `None` if request fails or ISBN key absent.
  - `_try_google_books(isbn: str) -> BookData | None` — queries `https://www.googleapis.com/books/v1/volumes` with `q=isbn:{isbn}`. Includes `key` param only if `settings.google_books_api_key` is non-empty. Parses first item from `items[0].volumeInfo`: title, authors, publisher, year from `publishedDate` (first 4 digits), page count, language, cover thumbnail, ISBN_13/ISBN_10 from `industryIdentifiers`. Returns `None` if request fails, `totalItems` is falsey, or no items.
  - Broad `except Exception` returns `None` for transient errors — keeps the MVP lookup non-fatal.
- Implemented `api/tests/test_isbn_lookup.py` — 3 async `respx`-mocked tests:
  1. Open Library success: mock returns full book data, asserts title/authors/publisher parsed.
  2. Google Books fallback: Open Library returns `{}`, Google Books returns one item with `totalItems: 1`, asserts title parsed.
  3. Both fail: Open Library returns `{}`, Google Books returns `totalItems: 0`, asserts `None`.

### Decisions

- Used `httpx.AsyncClient(timeout=10)` — 10-second timeout prevents hanging on slow APIs.
- Google Books API key is optional and conditionally included — no hard dependency on a real key. Without it, requests still work but may hit default rate limits.
- ISBN normalization is NOT performed in the lookup service — the caller (router in back-007) is responsible for normalizing/validating the ISBN before calling `lookup_isbn`. This keeps services decoupled.
- Used `re.search(r"\d{4}", ...)` for year extraction from both APIs — handles varied date formats (`"2005"`, `"Jan 2005"`, `"2005-01-01"`).

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 14 passed, exit code 0 |

### Follow-ups

- **back-007**: Books CRUD with ISBN lookup endpoint — will wire `lookup_isbn` into the `GET /books/lookup/{isbn}` endpoint.
- **back-008**: Tags and loans CRUD — must resolve `loans.book_id` FK delete policy.

---

## 2026-05-25 — back-007: Books CRUD with ISBN lookup endpoint

### What was done

**Schemas** (`api/app/schemas/book.py`):
- `TagOut` — id, name, color with `from_attributes=True`.
- `BookCreate` — all book fields + `tag_ids` for tag association during creation.
- `BookUpdate` — same shape as BookCreate but all fields optional, `tag_ids` defaults to `None` (meaning "don't change tags").
- `BookOut` — all persisted fields + `created_at` + `tags: list[TagOut]`.

**Router** (`api/app/routers/books.py`):
- `GET /books/lookup/{isbn}` — normalizes ISBN via `normalize_isbn`, validates EAN-13 checksum, calls `lookup_isbn`. Returns 422 for invalid ISBN, 404 if not found. Fills `isbn_13` from the validated input if the service result omits it (Open Library doesn't populate `isbn_13`/`isbn_10`).
- `POST /books/` — creates a book and optionally attaches tags via `BookTag` join table. Returns 201.
- `GET /books/` — lists books with optional `search` (ilike on title/subtitle), `language` (exact match), `tag_id` (exists in book_tags) filters. Ordered by `created_at` desc.
- `GET /books/{book_id}` — fetches single book with tags via `selectinload`, or 404.
- `PATCH /books/{book_id}` — partial update via `model_dump(exclude_unset=True)`. When `tag_ids` is explicitly provided (not `None`), deletes existing `BookTag` rows and inserts new ones.
- `DELETE /books/{book_id}` — deletes and returns 204.
- Helpers: `_book_to_out` (maps ORM Book + nested BookTag.tag to BookOut), `_get_book_or_404` (loads with joined tags), `_sync_tags` (bulk inserts BookTag rows).

**Tests** (`api/tests/test_books.py`):
- 9 ORM-level tests using `db_session`: create, list (ordered desc), get, get 404, update, delete + verify 404, create with tags, filter by tag, search.
- 3 HTTP-level lookup tests using `auth_client` + `unittest.mock.patch` to mock `lookup_isbn`: invalid ISBN → 422, success → 200 with `isbn_13` filled from input, not found → 404.

### Infrastructure fix

**Event loop mismatch** — session-scoped `test_engine` in pytest-asyncio 1.3.0 + asyncpg causes `RuntimeError: Task got Future attached to a different loop`. The asyncpg connection pool creates connections in one event loop, but function-scoped tests run in different loops.

**Fix:** Changed `test_engine` from `scope="session"` to function-scoped. Each test gets its own engine, connection pool, and fresh schema (drop_all + create_all per test). Slightly slower but avoids the event loop issue entirely.

### Decisions

- Lookup endpoint fills missing `isbn_13` from validated input at the router boundary — avoids modifying `back-006` service layer. Open Library's API returns no ISBN identifiers; Google Books does. The router ensures callers always get a stable `isbn_13` field.
- Search on `Book.title.ilike` and `Book.subtitle.ilike` only — does not search `authors` JSONB column due to complexity of text casting on JSONB. This is adequate for MVP and can be extended later.
- Tag sync on PATCH uses delete-all + re-insert strategy — simpler than computing diffs, correct for small cardinality.
- `db_session.commit()` in tests needs data to persist within the same engine scope. With function-scoped engine, each test has its own schema, so data naturally resets between tests.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 26 passed, exit code 0 |

### Follow-ups

- **back-008**: Tags and loans CRUD — must resolve `loans.book_id` FK delete policy.
- **back-009**: Label templates and PDF generation.
- **back-010**: BibTeX and CSV export.

---

## 2026-05-25 — back-008: Tags and loans CRUD

### What was done

**Tag schemas** (`api/app/schemas/tag.py`):
- `TagCreate` — name (required), color (default `#6366f1`).
- `TagUpdate` — name and color, both optional, for partial updates.
- `TagOut` — id, name, color with `from_attributes=True`.

**Loan schemas** (`api/app/schemas/loan.py`):
- `LoanCreate` — book_id, borrower_name, due_date (optional), notes (optional).
- `LoanReturn` — returned_at (optional, defaults to UTC now in the endpoint).
- `LoanOut` — id, book_id, borrower_name, loaned_at, due_date, returned_at, notes with `from_attributes=True`.

**Tags router** (`api/app/routers/tags.py`):
- `POST /tags/` — create tag (201).
- `GET /tags/` — list tags ordered by name.
- `PATCH /tags/{tag_id}` — partial update (name/color), 404 on missing.
- `DELETE /tags/{tag_id}` — delete tag (204). If the tag is in use (has associated BookTag rows), catches the DB `IntegrityError` from the `ON DELETE RESTRICT` FK and returns 409 Conflict.

**Loans router** (`api/app/routers/loans.py`):
- `POST /loans/` — create loan. Validates `book_id` exists before writing (404 if not found). Returns 201.
- `GET /loans/` — list loans ordered by `loaned_at` desc. Supports `open_only=true` filter (excludes returned loans).
- `POST /loans/{loan_id}/return` — mark loan as returned. Sets `returned_at` to provided datetime or current UTC. 404 on missing loan.

**Model fix** — Tag.book_tags relationship:
- Added `passive_deletes=True` to `Tag.book_tags` relationship. Without it, SQLAlchemy's ORM tried to blank-out the `book_tags.tag_id` column (which is part of the composite PK) when deleting a Tag. `passive_deletes=True` tells the ORM to let the DB handle the FK constraint, so the `ON DELETE RESTRICT` raises an `IntegrityError` that the router catches and converts to 409.

**Tests**:
- `api/tests/test_tags.py` — 6 HTTP tests: create tag (201 + verify fields), list tags (ordered by name), update tag (partial), delete tag (verify absent from list), 404 on missing tag (via PATCH), 409 on delete of in-use tag.
- `api/tests/test_loans.py` — 6 HTTP tests: create loan, create loan with nonexistent book → 404, return loan, return nonexistent loan → 404, list loans, open_only filter excludes returned loans.

### `loans.book_id` delete policy — resolved

**Decision: kept as implicit RESTRICT** (no `ondelete` clause on FK). PostgreSQL's `NO ACTION` means deleting a book with active loans will fail. This preserves loan history and prevents accidental deletion of books with loan records. The open decision in STATUS.json is now closed.

### Decisions

- Used `passive_deletes=True` on `Tag.book_tags` instead of checking tag usage with a pre-delete query. The DB-level constraint already exists, and catching the `IntegrityError` is simpler, atomic, and avoids a race condition.
- Loan `book_id` existence is validated with a `SELECT Book.id` before insert rather than relying on FK violation. This gives a clear 404 "Book not found" instead of a generic 500 on FK error.
- `returned_at` defaults to `datetime.now(timezone.utc)` in the endpoint, not in the schema default — keeps the schema clean and the behavior explicit in the router.
- No `GET /tags/{tag_id}` endpoint — not required by the plan. Single-tag lookup can be done via the list endpoint if needed.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 38 passed, exit code 0 |

### Follow-ups

- **back-009**: Label templates and PDF generation (reportlab).
- **back-010**: BibTeX and CSV export.
- **back-011**: CSV and BibTeX import.

---

## 2026-05-26 — back-009: Label templates and PDF generation

### What was done

**Schemas** (`api/app/schemas/label_template.py`):
- `LabelTemplateCreate` — name (required), width_mm (50.0), height_mm (30.0), font_size (8), show_dewey/show_title/show_barcode (True).
- `LabelTemplateOut` — all fields + id, created_at with `from_attributes=True`.
- `LabelGenerateRequest` — book_ids (list[uuid.UUID]), template_id (uuid.UUID).

**PDF service** (`api/app/services/pdf_labels.py`):
- `generate_labels_pdf(books, template) -> bytes` — ReportLab Canvas, page size from template dimensions (mm), Code128 barcode from `book.isbn_13`, optional dewey/title/barcode sections, one label per page, raw bytes output.

**Router** (`api/app/routers/labels.py`):
- `POST /labels/templates/` (201), `GET /labels/templates/`, `DELETE /labels/templates/{id}` (204), `POST /labels/generate` (200, `application/pdf`).
- Auth required on all endpoints.
- 404 on missing template or no books found.

**Tests** (`api/tests/test_labels.py`):
- 8 HTTP tests: create template (verify all defaults), list templates, delete + verify absent, template not found → 404, generate PDF (Content-Type, non-trivial length), template not found → 404 on generate, empty book_ids → 404, bogus book_ids → 404.

### Decisions

- Used single `from reportlab.lib.units import mm` instead of dual import from both `units` and `pagesizes` — ruff flagged the redefinition.
- `show_barcode` gracefully handles missing `isbn_13` (book without ISBN) and barcode rendering exceptions — no PDF generation failure on missing data.
- PDF generation is synchronous (ReportLab is CPU-bound). Post-MVP thread-pool offloading noted in HANDOFF.md.
- Followed existing router patterns from `tags.py` — helper `_get_template_or_404`, same dependency injection, same commit/refresh/validate flow.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 46 passed, exit code 0 |

### Follow-ups

- **back-010**: BibTeX and CSV export.
- **back-011**: CSV and BibTeX import.
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-28 — back-010: BibTeX and CSV export

### What was done

**CSV service** (`api/app/services/csv_io.py`):
- `generate_csv(books: list[Book]) -> str` — 14-column CSV via `csv.writer` + `io.StringIO`. Authors joined with `"; "`. Empty list produces headers-only CSV.

**BibTeX service** (`api/app/services/bibtex_io.py`):
- `generate_bibtex(books: list[Book]) -> str` — uses `bibtexparser` 1.4 API (`BibDatabase` + `dumps`). Cite key: first author surname + year, UUID fallback. Deduplication with incrementing suffix. Fields: title (+ subtitle), author, publisher, year, isbn, language, note.

**Export router** (`api/app/routers/export.py`):
- `GET /export/csv` — auth required, `text/csv`, `Content-Disposition: attachment`, orders by title.
- `GET /export/bibtex` — auth required, `application/x-bibtex`, `Content-Disposition: attachment`, orders by title.

**Tests** (`api/tests/test_export.py`):
- 6 HTTP tests: CSV with books, CSV empty, BibTeX with books, BibTeX empty, auth required for both endpoints.

### Decisions

- Used `bibtexparser` 1.x API (`BibDatabase` + `dumps`) as it's the installed version (1.4.4). The 2.x API is async/`Library`-based but not available in this version.
- Cite key format uses first author's surname + year. Deduplication appends an incrementing number when keys collide.
- BibTeX media type `application/x-bibtex` instead of `text/plain` — more specific for download identification.
- CSV authors joined with `"; "` — semicolons as inner delimiter, matching the CSV spec where commas separate columns.
- No tags in export — tags are associations, not standard BibTeX/CSV book fields.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 40 source files |
| `pytest` | 52 passed (46 existing + 6 new), exit code 0 |

### QA and Security

- QA verdict: APPROVED. Minor reservation: generated BibTeX cite keys can still collide if a natural key equals a suffixed duplicate key.
- Security verdict: ADVISORY. Non-blocking follow-ups: CSV formula-injection sanitization before multi-user/shared exports, `Cache-Control: private, no-store` on export responses, and unbounded/synchronous export behavior if catalog size grows.

### Follow-ups

- **back-011**: CSV and BibTeX import (counterpart to this export feature).
- **front-001**: Next.js scaffold (can run in parallel).

---

## 2026-05-28 — Harness CLI loop hardening

### What was done

- Updated `harness/prompts/scripts/agent-loop.py` to use the existing prompt files directly from `harness/prompts/` instead of a missing `templates/` directory.
- Added default config fallback plus `harness/prompts/agent-harness.config.example.json` with `opencode` backend Builder and `copilot` QA/Security examples.
- Added `--diff-path` so QA/Security prompts can be scoped to the active slice instead of the full dirty worktree.
- Added command placeholders `{root}`, `{prompt_file}`, and `{prompt}` for CLI integration.
- Made Builder/QA/Security nonzero exits stop the loop instead of continuing to later gates.
- Updated `harness/prompts/README.md` with active-file inventory, future-orchestrator instructions, correct repo-relative usage, and scoped-diff example.
- Removed unused duplicate prompt variants: `harness/prompts/builder 2.md`, `harness/prompts/orchestrator 2.md`, and `harness/prompts/qa 2.md`.
- Removed generated `harness/prompts/scripts/__pycache__/` bytecode.
- Updated `.gitignore` to ignore `.harness/` generated runs and local `harness/prompts/agent-harness.config.json`.

### Verification

| Check | Result |
|-------|--------|
| `python3 -m py_compile harness/prompts/scripts/agent-loop.py` | passed |
| `python3 -m json.tool harness/prompts/agent-harness.config.example.json` | passed |
| `harness/prompts/scripts/agent-loop.sh --help` | passed |
| manual smoke run (`--mode manual --builder backend --diff-path ...`) | generated prompts and final report |
| `git check-ignore -v .harness/runs/20260528-134153/final-report.md` | `.harness/` ignore rule confirmed |

### Notes

- The harness still does not commit or push.
- Full automation depends on local `opencode`/`copilot` permissions and may still need command approval in Codex.

---

## 2026-05-28 — back-011: CSV and BibTeX import

### What was done

**CSV import/export service** (`api/app/services/csv_io.py`):
- Added `parse_csv(content)` using `csv.DictReader`, with blank-row skipping and missing/empty-header validation.
- Added `map_csv_row_to_book_data(row)` to map export-style CSV rows back to book fields, including semicolon-separated authors and optional integer fields.
- Added `https`-only scheme filtering for imported `cover_url`.
- Added ISBN-10/ISBN-13 shape normalization for CSV imports; invalid or oversized ISBN values are dropped before persistence.
- Hardened `generate_csv()` against spreadsheet formula injection by prefixing formula-like cells with `'`.

**BibTeX import/export service** (`api/app/services/bibtex_io.py`):
- Added `parse_bibtex(content)` using `bibtexparser.loads()` and filtering to `@book` entries.
- Added `map_bibtex_entry_to_book_data(entry)` to map author/year/isbn/publisher/language/note into book fields.
- Added normalization for valid hyphenated/space-separated ISBN values; invalid values are dropped before persistence.

**Import API**:
- Added `api/app/schemas/import_result.py` with `ImportResult`.
- Added `api/app/routers/import_.py` with authenticated `POST /import/csv` and `POST /import/bibtex` multipart upload endpoints.
- Added stream-read 1 MB upload cap and 5,000-record cap with 413 responses.
- Registered the import router in `api/app/main.py`.

**Export hardening** (`api/app/routers/export.py`):
- Added `Cache-Control: private, no-store` to CSV and BibTeX export responses.

**Tests**:
- Added `api/tests/test_import.py` with 21 HTTP tests for CSV/BibTeX import success, empty files, empty-header rejection, auth, extension validation, missing titles, malformed/extra-column behavior, oversized upload rejection, too-many-rows rejection, non-UTF-8 rejection, `cover_url` https-only filtering, invalid ISBN handling, hyphenated ISBN-13 normalization, and BibTeX article filtering.
- Extended `api/tests/test_export.py` with formula sanitization and cache-header coverage.

### Sensor results

| Sensor | Result |
|--------|--------|
| `ruff check .` | All checks passed |
| `mypy .` | Success: no issues found in 43 source files |
| `pytest` | 74 passed, 1 existing warning, exit code 0 |

### Gate results

| Gate | Result |
|------|--------|
| QA | APPROVED after scoped rerun |
| Security | CLEAN after actionable advisories were fixed |

### Follow-ups

- Next product slice after acceptance: `front-001` Next.js scaffold.

## 2026-05-28 — front-001: Next.js 15 scaffold (Next.js 16.2.6 installed)

### What was done

**Next.js scaffold** (`web/`):
- Scaffolded with `create-next-app` (App Router, TypeScript, Tailwind v4). Installed version is **Next.js 16.2.6** (latest at time of install), not 15.
- Moved `app/` into `src/app/` per project structure spec; updated `tsconfig.json` `paths` to `"@/*": ["./src/*"]`.
- Installed and initialized **shadcn/ui** (v4.8.2) with Tailwind v4 support — created `src/components/ui/button.tsx` and `src/lib/utils.ts`.
- Installed **@zxing/browser** for ISBN scanning.
- Added **ESLint** (v9 flat config via `eslint-config-next` which exports a native flat config array) and `lint` script.

**Breaking changes in Next.js 16** (noted in `web/AGENTS.md`):
- `middleware.ts` is deprecated and renamed to **`proxy.ts`**. The exported function must be named `proxy`, not `middleware`.
- `next lint` CLI command is removed. Lint script uses `eslint src` directly.

**Files created:**
- `src/proxy.ts` — auth guard (redirects unauthenticated → `/login`; redirects authenticated from `/login` → `/catalog`).
- `src/lib/api.ts` — typed `apiFetch<T>` wrapper against `NEXT_PUBLIC_API_URL`, with `ApiError` class.
- `src/lib/auth.ts` — server functions for `login` (POSTs `/auth/login`, sets httpOnly JWT cookie, redirects to `/catalog`), `logout` (deletes cookie, redirects to `/login`), `getToken` (reads cookie value).
- `src/app/login/page.tsx` — placeholder login page.
- `src/app/catalog/page.tsx` — placeholder catalog page.
- `web/.env.local.example` — documents `NEXT_PUBLIC_API_URL`.
- `web/eslint.config.mjs` — ESLint flat config using `eslint-config-next`.

### Sensor results

| Sensor | Result |
|--------|--------|
| `npm run lint` | Passed (0 warnings, 0 errors) |
| `npm run build` | Passed — 4 routes built (/, /_not-found, /catalog, /login) + Proxy (Middleware) |

### Gate results

| Gate | Result |
|------|--------|
| QA | APPROVED_WITH_RESERVATIONS — no blockers; 3 items deferred to front-002: (1) extract shared API_URL to lib/config.ts, (2) use apiFetch in auth.ts login instead of raw fetch, (3) replace NEXT_PUBLIC_API_URL in auth.ts with server-only env var |
| Security | ADVISORY — postcss CVE in next@16.2.6 (build-time only, no viable fix); NEXT_PUBLIC_ in server context; ?from= redirect param must be validated as relative path in front-002 to prevent open-redirect |

### Follow-ups

- `front-002`: Login page UI (form, POST to `/auth/login` via `login` server action). Address all QA/Security advisories in this slice.

## 2026-05-28 — front-002: Login page UI

### What was done

- Created `web/src/lib/config.ts` — shared `API_URL` constant from `process.env.API_URL` (server-only, no NEXT_PUBLIC_ prefix)
- Refactored `web/src/lib/api.ts` — imports `API_URL` from `./config` instead of inline constant
- Refactored `web/src/lib/auth.ts` — imports `API_URL` from `./config`; `login()` now uses `apiFetch` from `api.ts` instead of raw `fetch`; removed `redirect('/catalog')` from `login()` (client handles navigation)
- Updated `web/.env.local.example` — renamed `NEXT_PUBLIC_API_URL` to `API_URL`
- Fixed open-redirect in `web/src/proxy.ts` — validates `?from=` param is a safe relative path (starts with `/`, not `//`)
- Added `web/src/components/ui/input.tsx` and `web/src/components/ui/label.tsx` (shadcn-style, no new packages)
- Implemented `web/src/app/login/page.tsx` — client component with username+password form, inline error display, `router.push('/catalog')` on success

### Sensor results

| Sensor | Result |
|--------|--------|
| `npm run lint` | Passed (0 warnings, 0 errors) |
| `npm run build` | Passed — routes: /, /_not-found, /catalog, /login + Proxy |

### Gate results

| Gate | Result |
|------|--------|
| QA | APPROVED_WITH_RESERVATIONS — no blockers; deferred to front-003: wire ?from= redirect, add server-only to config.ts, fix aria-invalid scope, add frontend test runner |
| Security | ADVISORY — postcss CVE carry-forward; config.ts server-only guard needed |

### Follow-ups

- `front-003`: Book catalog page. Address deferred items: ?from= redirect, server-only import, aria-invalid fix, frontend test runner.
