# HANDOFF.md — Session Memory

> Updated by the agent at the end of each session.
> This file is the context bridge between different sessions.

## Last update

- **Date:** 2026-05-24
- **Session:** backend-core repair — back-001 + back-002 + back-004
- **Branch / HEAD:** main

## Goals completed this session

### back-001: FastAPI setup — config, database, main
- Created `api/pyproject.toml` with backend package metadata and dev tooling for `ruff`, `mypy`, and `pytest`.
- Created `api/.env.example` with DB/auth/API key variables from the approved plan.
- Implemented `api/app/config.py`, `api/app/database.py`, `api/app/main.py`, and `api/app/deps.py`.
- Added `api/app/__init__.py` so `app/` is a real Python package.
- Added `api/tests/test_app.py` — minimal foundation smoke test for app import and OpenAPI generation.

### back-002: JWT auth — login endpoint and token verification
- Implemented `api/app/auth.py`: bcrypt password hashing (`hash_password`, `verify_password`) and JWT encode/decode (`create_access_token`, `verify_token`).
- Implemented `api/app/routers/auth.py`: `POST /auth/login` and `GET /auth/me`.
- Implemented `api/tests/test_auth.py`: 3 tests (login success, wrong password → 401, protected endpoint without token → 401).

### back-004: pytest async fixtures with isolated test database
- Implemented `api/tests/conftest.py`: session-scoped `test_engine`, `db_session`, `client`, and `auth_client`.
- Seeded required env vars inside `conftest.py` before importing `app.config`, so the normal `pytest` command works from `api/` without an untracked local `.env`.
- Created local PostgreSQL test database `personal_library_test` during development validation.

### Dependency/tooling decisions
- Switched from `passlib[bcrypt]` to `bcrypt` directly because `passlib v1.7.4` is incompatible with `bcrypt >=5`.
- Used `[project.optional-dependencies]` instead of `[dependency-groups]` for broader pip compatibility.
- Added setuptools package discovery config for `app*` to avoid flat-layout collision with `alembic/`.

## WIP (in-progress at handoff)

Nothing. `back-001`, `back-002`, and `back-004` are complete.

## Setup gaps / known issues

- **No tracked local `.env`** — only `api/.env.example` is versioned. Tests no longer require an untracked local `.env`; they self-seed required env vars in `conftest.py`.
- **Runtime startup still needs real config** — outside tests, importing or starting the app still requires real values for `DATABASE_URL`, `LIBRARY_USERNAME`, `LIBRARY_PASSWORD`, and `JWT_SECRET` via environment or a local `.env`.
- **PostgreSQL 18 locally** — local validation used Homebrew PostgreSQL 18.4 rather than the spec’s PostgreSQL 17. This is acceptable for development but worth noting.
- **No models yet** — `Base.metadata.create_all()` currently creates no tables because model implementation belongs to `back-003`.
- **Frontend not yet scaffolded beyond directories** — `web/` still lacks `package.json` and installed dependencies.

## Sensor results

| Sensor | Result |
|--------|--------|
| `source .venv/bin/activate && ruff check .` | All checks passed |
| `source .venv/bin/activate && mypy .` | Success: no issues found in 38 source files |
| `source .venv/bin/activate && pytest` | 4 passed, exit code 0 |

## Suggested next steps

1. **back-003**: SQLAlchemy models + initial Alembic migration — implement `book.py`, `tag.py`, `loan.py`, `label_template.py`, `alembic.ini`, `alembic/env.py`, and the initial migration.
2. Then continue with **back-005** through **back-011**.
3. **front-001** can be parallelized at any point.
