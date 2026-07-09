# CLAUDE.md

Clerk is **Anika Legal's case management system & public website**. It's a monorepo with four coupled parts joined by an OpenAPI contract:

- `app/` — Django + Wagtail backend (Django REST Framework API, CMS, public site, admin)
- `frontend/` — React 18 + TypeScript + Vite SPA (the "Clerk" CMS UI)
- `intake/` — React 18 + TypeScript + Vite SPA (the public client intake form, built on SurveyJS; served at `/intake/` by the thin `app/intake` Django app)
- `openapi/` — the hand-authored OpenAPI spec that is the **source of truth** for the API; it generates the backend schema and both frontend API clients

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
2. Run `inv schema`. This bundles the spec into `app/openapi.generated.yaml`, regenerates the RTK Query client at `frontend/src/api/api.generated.ts` (intake endpoints are filtered out via `frontend/openapi-config.js`), and regenerates the intake types at `intake/src/api/types.generated.ts`.
3. **Never hand-edit the generated files** — `app/openapi.generated.yaml`, `frontend/src/api/api.generated.ts` and `intake/src/api/types.generated.ts` are build artifacts.

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

## Intake form (`intake/`)

- The public client intake form: a SurveyJS (survey-core + survey-react-ui) SPA served by the `app/intake` Django app at `/intake/` (dev Vite server on port 5174, image `clerk-intake:local`, built via `inv build --intake`).
- The question list in `src/questions/` is the source of truth; question names are the UPPER_SNAKE_CASE answer keys that `core/services/submission.py` processes - do not rename them. Flow logic (eligibility exits, saves, analytics) hooks into SurveyJS events in `src/views/FormPage.tsx` + `src/form/`.
- Commands: `npm run dev`, `npm run build`, `npm run test` (vitest - flow parity/serialization tests), `npm run lint`, `npm run format`.

## Conventions & guardrails

- **Never use en dashes or em dashes** in code, comments, commit messages, docs, or any other text. Use a normal hyphen (-) instead.
- **Branch off and PR into `develop`** (not `master`). Use conventional-commit style messages (`fix(case): ...`, `chore: ...`), matching recent history.
- **Secrets are transcrypt-encrypted** `.env` files (`env/`). Never decrypt them into plaintext, commit decrypted values, or print their contents.
- After any API change, regenerate with `inv schema` and never edit the generated files directly.
