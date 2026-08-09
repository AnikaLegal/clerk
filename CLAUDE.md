# CLAUDE.md

Clerk is **Anika Legal's case management system & public website**. It's a monorepo with three coupled parts joined by an OpenAPI contract:

- `app/` - Django + Wagtail backend (Django REST Framework API, CMS, public site, admin)
- `frontend/` - React 18 + TypeScript + Vite SPA (the "Clerk" CMS UI)
- `openapi/` - the hand-authored OpenAPI spec that is the **source of truth** for the API; it generates both the backend schema and the frontend API client

Everything runs in Docker, orchestrated through `just` recipes in the root `justfile`. `just` ships in the app dev venv, so activate it (`source app/.venv/bin/activate`) or call `app/.venv/bin/just` directly, and run `just` from the project root.

## Common commands

```bash
just dev                 # Run the app (Django + frontend) via docker compose -> http://localhost:8000
just test                # Run the full backend pytest suite in Docker
just test -i             # Interactive: open a shell in the test container, then `pytest -vv path/to/test.py`
just test app/case/tests/...   # Run a subset (positional path; a leading app/ is stripped)
just test -d             # Run tests under debugpy (attach with the VS Code launch profile)
just shell               # Django shell_plus in a container
just migrate             # makemigrations && migrate
just reset               # Reset the local database
just schema              # Regenerate the API contract + frontend client (see below)
just                     # List all recipes (also `just --list`; `just help <recipe>` for usage)
```

App URLs (via `just dev`): website `http://localhost:8000`, Clerk CMS `/clerk`, Django admin `/admin`.

First-time setup (Docker, transcrypt, `uv --directory app sync` + venv activation, `just build`, `just reset`, `just superuser you@anikalegal.org.au`) is in [docs/setup.md](docs/setup.md). Topic docs live in [docs/](docs/).

## API contract workflow (important)

The API is **contract-first**. To change an endpoint or schema:

1. Edit the source spec under [openapi/](openapi/) (`paths/`, `schemas/`, `responses/`).
2. Run `just schema` (or `cd frontend && npm run schema`). This bundles the spec into `app/openapi.generated.yaml` and regenerates the RTK Query client at `frontend/src/api/api.generated.ts`.
3. **Never hand-edit the generated files** - `app/openapi.generated.yaml` and `frontend/src/api/api.generated.ts` are build artifacts.

Backend responses are validated against the contract in tests (`django-contract-tester`), so the spec and the DRF serializers/views must stay in sync.

## Backend (`app/`)

- Django 5 + Wagtail, DRF for the API. Python pinned to **3.12.5**, deps managed with **uv** (`uv.lock`, `pyproject.toml`).
- Settings split by environment in `app/clerk/settings/` (`base`, `dev`, `staging`, `prod`, `test`). Tests use `clerk.settings.test`.
- Apps (see [README.md](README.md) for the full list): `case` (the core CMS - serializers/views/urls live here), `core` (domain models), `accounts`, `emails`, `intake`, `web` (public site/blog), plus integrations: `microsoft`/`google`/`slack`/`caller`/`webhooks`/`notify`.
- Tests: pytest (`pytest-django`, `pytest-factoryboy`, factory-based). Run via `just test` - **always run the suite before considering backend work done**. CI runs the same suite on pushes to `develop`/`master` and on PRs into them.
- **Don't run black/isort/flake8** as a finishing step - they aren't wired into CI or a documented flow. Match the surrounding style instead.

## Frontend (`frontend/`)

- React 18 + TypeScript + Vite. State/data via Redux Toolkit + **RTK Query** (`src/api/` - `baseApi.ts` is hand-written, `api.generated.ts` is generated, `enhancedApi.ts` adds tags). Auth uses the Django CSRF cookie (`x-csrftoken`).
- **Mid-migration: prefer Mantine.** New components use `@mantine/core`; new forms use `@mantine/form` + `yup` (`mantine-form-yup-resolver`). `semantic-ui-react`, `styled-components`, and `formik` are **legacy** - don't add new code with them; migrate toward Mantine when touching that code.
- Structure: `src/pages/`, `src/features/`, `src/forms/`, `src/comps/`.
- Commands: `npm run dev`, `npm run build`, `npm run lint` (eslint), `npm run format` (prettier). The frontend also runs as a service under `just dev`.

## Conventions & guardrails

- **Never use en dashes or em dashes** in code, comments, commit messages, docs, or any other text. Use a normal hyphen (-) instead.
- **Number every list in a reply** - tasks, findings, options, next steps - so the user can refer to an item by its number. Number across the whole reply rather than restarting per section.
- **Branch off `develop`** (not `master`). Use conventional-commit style messages (`fix(case): ...`, `chore: ...`), matching recent history.
- **Don't assume a pull request is required.** The PR-based flow in [docs/setup.md](docs/setup.md#contributing) is written for volunteers and outside contributors; core tech team members commit to `develop` directly. Follow whichever the user is using, and ask if it isn't clear.
- **Don't add `Co-Authored-By` trailers** (or any similar attribution lines) to commit messages.
- **Don't include test output results in commit messages** (e.g. "Checks green: intake tsc/lint/86 tests").
- **Don't assume the git repository state** - the user may have made changes manually or in another session. Check the actual state (`git status`, `git log`, etc.) before reporting it.
- **Secrets are transcrypt-encrypted** `.env` files (`env/`). Never decrypt them into plaintext, commit decrypted values, or print their contents.
- After any API change, regenerate with `just schema` and never edit the generated files directly.
