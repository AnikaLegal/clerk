# CLAUDE.md

Clerk is **Anika Legal's case management system & public website**. It's a monorepo with three coupled parts joined by an OpenAPI contract:

- `app/` — Django + Wagtail backend (Django REST Framework API, CMS, public site, admin)
- `frontend/` — React 18 + TypeScript + Vite SPA (the "Clerk" CMS UI)
- `openapi/` — the hand-authored OpenAPI spec that is the **source of truth** for the API; it generates both the backend schema and the frontend API client

Everything runs in Docker, orchestrated through `inv` (pyinvoke) tasks defined in `tasks.py`. Run `inv` commands from the project root.

## Common commands

```bash
inv dev                 # Run the app (Django + frontend) via docker compose -> http://localhost:8000
inv test                # Run the full backend pytest suite in Docker
inv test -i             # Interactive: open a shell in the test container, then `pytest -vv path/to/test.py`
inv test --path app/case/tests/...   # Run a subset
inv test -d             # Run tests under debugpy (attach with the VS Code launch profile)
inv shell               # Django shell_plus in a container
inv migrate             # makemigrations && migrate
inv reset               # Reset the local database
inv schema              # Regenerate the API contract + frontend client (see below)
inv -l                  # List all tasks
```

App URLs (via `inv dev`): website `http://localhost:8000`, Clerk CMS `/clerk`, Django admin `/admin`.

First-time setup (Docker, transcrypt, `inv build -f` / `inv build`, `inv reset`, `inv superuser you@anikalegal.com`) is in [docs/setup.md](docs/setup.md). Topic docs live in [docs/](docs/).

## API contract workflow (important)

The API is **contract-first**. To change an endpoint or schema:

1. Edit the source spec under [openapi/](openapi/) (`paths/`, `schemas/`, `responses/`).
2. Run `inv schema` (or `cd frontend && npm run schema`). This bundles the spec into `app/openapi.generated.yaml` and regenerates the RTK Query client at `frontend/src/api/api.generated.ts`.
3. **Never hand-edit the generated files** — `app/openapi.generated.yaml` and `frontend/src/api/api.generated.ts` are build artifacts.

Backend responses are validated against the contract in tests (`django-contract-tester`), so the spec and the DRF serializers/views must stay in sync.

## Backend (`app/`)

- Django 5 + Wagtail, DRF for the API. Python pinned to **3.12.5**, deps managed with **uv** (`uv.lock`, `pyproject.toml`).
- Settings split by environment in `app/clerk/settings/` (`base`, `dev`, `staging`, `prod`, `test`). Tests use `clerk.settings.test`.
- Apps (see [README.md](README.md) for the full list): `case` (the core CMS — serializers/views/urls live here), `core` (domain models), `accounts`, `emails`, `intake`, `web` (public site/blog), plus integrations: `microsoft`/`google`/`slack`/`caller`/`webhooks`/`notify`.
- Tests: pytest (`pytest-django`, `pytest-factoryboy`, factory-based). Run via `inv test` — **always run the suite before considering backend work done**. CI runs the same suite on PRs to `develop`/`master`.
- **Don't run black/isort/flake8** as a finishing step — they aren't wired into CI or a documented flow. Match the surrounding style instead.

## Frontend (`frontend/`)

- React 18 + TypeScript + Vite. State/data via Redux Toolkit + **RTK Query** (`src/api/` — `baseApi.ts` is hand-written, `api.generated.ts` is generated, `enhancedApi.ts` adds tags). Auth uses the Django CSRF cookie (`x-csrftoken`).
- **Mid-migration: prefer Mantine.** New components use `@mantine/core`; new forms use `@mantine/form` + `yup` (`mantine-form-yup-resolver`). `semantic-ui-react`, `styled-components`, and `formik` are **legacy** — don't add new code with them; migrate toward Mantine when touching that code.
- Structure: `src/pages/`, `src/features/`, `src/forms/`, `src/comps/`.
- Commands: `npm run dev`, `npm run build`, `npm run lint` (eslint), `npm run format` (prettier). The frontend also runs as a service under `inv dev`.

## Conventions & guardrails

- **Never use en dashes or em dashes** in code, comments, commit messages, docs, or any other text. Use a normal hyphen (-) instead.
- **Branch off and PR into `develop`** (not `master`). Use conventional-commit style messages (`fix(case): ...`, `chore: ...`), matching recent history.
- **Don't add `Co-Authored-By` trailers** (or any similar attribution lines) to commit messages.
- **Secrets are transcrypt-encrypted** `.env` files (`env/`). Never decrypt them into plaintext, commit decrypted values, or print their contents.
- After any API change, regenerate with `inv schema` and never edit the generated files directly.
