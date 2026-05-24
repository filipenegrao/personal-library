# Active Builder Task

Paste this content after harness/prompts/builder.md.
Updated by Orchestrator at the end of each completed feature.

## Task

- Feature ID: back-001
- Feature name: FastAPI setup — config, database, main
- Domain: backend-core
- Goal: Create the backend package metadata and base FastAPI application files so backend sensors can run and subsequent backend features have a real foundation.

## Mandatory scope

1. Create `api/pyproject.toml` with project metadata and dependencies from the approved plan.
2. Create `api/.env.example` with backend env vars for DB, auth, and optional Google Books key.
3. Implement `api/app/config.py` using `pydantic-settings`.
4. Implement `api/app/database.py` with SQLAlchemy async engine/session helpers and `Base`.
5. Implement `api/app/main.py` with a minimal FastAPI app shell suitable for later router registration.
6. Implement `api/app/deps.py` with initial dependency placeholders if needed for app startup.
7. Create the backend virtual environment and install dev dependencies needed to run sensors.
8. Update `HANDOFF.md`, `STATUS.json`, and `docs/session-log.md`.

## Out of scope

1. Alembic migration setup and model implementation (belongs to `back-003`).
2. Auth route/login logic (belongs to `back-002`).
3. Frontend scaffolding or `npm install`.
4. Book/tag/loan/label/export/import business logic.

## Acceptance criteria

1. `api/pyproject.toml` defines the backend package and dev dependencies needed for `ruff`, `mypy`, and `pytest`.
2. `api/.env.example`, `app/config.py`, `app/database.py`, `app/main.py`, and `app/deps.py` exist and are coherent with `docs/architecture.md`.
3. A backend virtual environment is created and dependencies are installed successfully.
4. Backend sensors run and are reported: `ruff check .`, `mypy .`, `pytest` from `api/`.
5. `STATUS.json` reflects `back-001 = done`.
6. `HANDOFF.md` updated.

## Constraints

1. Follow AGENTS.md.
2. Respect layer rules in docs/architecture.md.
3. No scope creep beyond backend foundation.
4. No hardcoded credentials, tokens, or secrets.
