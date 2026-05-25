# Active QA Review

Paste this content after harness/prompts/qa.md.
Updated by Orchestrator at the end of each completed feature.

## PR under review

- Feature ID: back-003
- Feature name: SQLAlchemy models and initial Alembic migration
- Domain: backend-core

## Review objective

Validate that the initial model layer and Alembic migration match the approved spec, integrate cleanly with the backend foundation, and keep sensors green.

## Expected scope

1. `api/app/models/book.py`, `tag.py`, `loan.py`, and `label_template.py` implemented consistently with the approved spec.
2. Alembic config files and the initial migration exist and are coherent with the SQLAlchemy metadata.
3. Backend sensors executed and reported: `ruff check .`, `mypy .`, `pytest`.
4. STATUS.json updated (`back-003` done).
5. HANDOFF.md updated.

## Must not be included in this delivery

1. CRUD route/business logic beyond model and migration foundation.
2. Frontend scaffolding or npm dependency installation.
3. Export/import implementation beyond schema concerns.

## Mandatory checklist

1. Model files align with the approved spec data model and plan expectations.
2. Architecture layer names and dependency direction match `docs/architecture.md`.
3. No hardcoded credentials, tokens, or secrets.
4. Alembic is wired to the correct metadata source.
5. Sensors actually executed and results are reported accurately.
6. STATUS.json reflects real state.
7. HANDOFF.md is current.

## Required report format

1. Verdict: APPROVED | REJECTED | APPROVED WITH COMMENTS
2. Critical issues (blocking merge)
3. Non-critical issues
4. Residual risks
5. Clear next action for Builder
