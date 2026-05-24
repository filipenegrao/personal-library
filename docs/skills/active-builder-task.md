# Active Builder Task

Paste this content after harness/prompts/builder.md.
Updated by Orchestrator at the end of each completed feature.

## Task

- Feature ID: repo-002
- Feature name: Project scaffold and git init
- Domain: foundation
- Goal: Create the initial project structure, .gitignore, and first git commit so the codebase is ready for backend and frontend implementation.

## Mandatory scope

1. Create root `.gitignore` covering Python, Node, and common macOS artifacts (per approved plan Task 1, Step 1).
2. Create `api/` directory structure: `app/{models,schemas,routers,services}/`, `alembic/versions/`, `tests/`. Touch all `__init__.py` and placeholder `.py` files.
3. Create `web/` directory structure: `src/{app,components,lib}/` and route subdirectories.
4. Run `git init` and commit `.gitignore` as the first commit.
5. Update `HANDOFF.md` and `STATUS.json` (mark repo-001 as done, repo-002 as done).

## Out of scope

1. Installing Python packages or creating a virtual environment.
2. Installing npm packages or running `npm install`.
3. Writing any application logic in the placeholder files — empty files only.
4. Configuring CI/CD or GitHub Actions.

## Acceptance criteria

1. `.gitignore` covers `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `.env`, `node_modules/`, `.next/`, `.env.local`, `.DS_Store`.
2. All directories from the approved plan file structure exist.
3. `git init` complete; first commit includes only `.gitignore`.
4. STATUS.json reflects repo-001 = done, repo-002 = done.
5. HANDOFF.md updated.

## Constraints

1. Follow AGENTS.md.
2. Respect layer rules in docs/architecture.md.
3. No scope creep — placeholder files only, no logic.
4. No hardcoded credentials, tokens, or secrets.
