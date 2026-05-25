# Active Builder Task

Paste this content after harness/prompts/builder.md.
Updated by Orchestrator at the end of each completed feature.

## Task

- Feature ID: back-003
- Feature name: SQLAlchemy models and initial Alembic migration
- Domain: backend-core
- Goal: Implement the initial SQLAlchemy model layer and Alembic migration so the backend has a real schema foundation for CRUD and test fixtures.

## Mandatory scope

1. Implement `api/app/models/book.py`, `tag.py`, `loan.py`, and `label_template.py` based on the approved spec data model.
2. Add any required model exports/import wiring needed for metadata discovery.
3. Create Alembic project files needed for the initial migration path:
   - `api/alembic.ini`
   - `api/alembic/env.py`
   - initial migration under `api/alembic/versions/`
4. Ensure the SQLAlchemy metadata includes the new models for migration generation and test setup.
5. Run backend sensors from `api/`: `ruff check .`, `mypy .`, `pytest`.
6. Update `HANDOFF.md`, `STATUS.json`, and `docs/session-log.md`.

## Out of scope

1. Books/tags/loans/labels CRUD route implementation beyond schema/model foundation.
2. ISBN lookup/validation business logic.
3. Frontend scaffolding or `npm install`.
4. Export/import business logic.

## Acceptance criteria

1. The four model files match the approved data model shape closely enough for initial migration work.
2. Alembic is configured and the initial migration is present.
3. Backend sensors run and are reported: `ruff check .`, `mypy .`, `pytest` from `api/`.
4. `STATUS.json` reflects `back-003 = done` when complete.
5. `HANDOFF.md` updated.

## Constraints

1. Follow AGENTS.md.
2. Respect layer rules in docs/architecture.md.
3. No scope creep beyond schema and migration foundation.
4. No hardcoded credentials, tokens, or secrets.
