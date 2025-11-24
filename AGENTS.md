# Repository Guidelines

## Project Structure & Module Organization
The Django project lives in `base/` (settings, root urls, ASGI/WSGI entrypoints). Feature code sits in `home/`, with domain models in `models.py`, view logic in `views.py`, forms/filters/serializers in their respective files, and custom services in `services.py`. UI assets stay under `home/templates/` and `home/static/`, while sample datasets such as `data.json` and environment defaults in `.env` assist local experiments. Tests and fixtures are under `home/tests/`, mirroring the app's modules; add new modules alongside their tests in this tree.

## Build, Test, and Development Commands
- `make runserver` (or `uv run ./manage.py runserver 5000`) loads the dev server with browser reload helpers.
- `make shell` starts a Django shell with project settings preloaded.
- `make makemigrations && make migrate` generates and applies schema changes; never edit migration files manually.
- `make test` runs `pytest --reuse-db`, which shortens repeated runs by reusing the SQLite/Postgres schema.
Use `uv run` directly if Make is unavailable.

## Coding Style & Naming Conventions
Target Python 3.13, 4-space indentation, and descriptive snake_case for modules, functions, and test names. Class names should stay in PascalCase and model Meta options declare verbose names when surfaced in admin. Prefer Django QuerySet APIs and keep view logic thin by delegating to `services.py`. Template files should pass `djlint --profile=django`, and HTML IDs/classes follow kebab-case to align with the current templates.

## Testing Guidelines
Write pytest-style tests in `home/tests/tests.py` or module-specific files, grouping related scenarios in classes prefixed with `Test`. Name functions `test_<feature>_<expectation>`. Reuse fixtures from `home/tests/fixtures/`; store any JSON fixtures beside them. Run `make test` before pushing and ensure added features have regression coverage (aim to keep current failure count at zero and avoid lowering coverage, even though no numeric gate exists).

## Commit & Pull Request Guidelines
The repository history is empty, so adopt Conventional Commits (`feat:`, `fix:`, `docs:`) for clarity. Each PR should include: a succinct summary, reproduction or verification steps (`make test`, screenshots for UI), linked issue IDs (e.g., `CRM-42`), and notes on migrations or env changes. Keep branches focused on one logical change set and mention any follow-up work explicitly.

## Configuration & Security Tips
All secrets stay in `.env`; never commit real API keys. Use `python-dotenv` locally or export variables before invoking `make`. Align DB URLs via `dj-database-url`, and enable `DEBUG=0` plus `ALLOWED_HOSTS` when staging deployments. Static files go through WhiteNoise, so run `python manage.py collectstatic` when preparing production bundles.
