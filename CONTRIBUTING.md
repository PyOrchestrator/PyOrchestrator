**Language:** **English** · [Русский](CONTRIBUTING.ru.md)

# Contributing

Thanks for your interest in PyOrchestrator.

## Bug reports

Open an [Issue](https://github.com/PyOrchestrator/PyOrchestrator/issues) with:

- Steps to reproduce
- Expected vs actual behavior
- Version (`APP_VERSION` from `.env` or `GET /health`)
- `docker compose ps` output and relevant logs (`docker compose logs <service>`)

## Pull requests

1. Fork the repository and create a branch from `main`
2. Follow existing code style (Python: async FastAPI; frontend: React + TypeScript + Tailwind)
3. Do not commit `.env`, secrets, `node_modules`, or `__pycache__`
4. Update `docs/en/` and `docs/ru/` (and `wiki/` if needed) when behavior or configuration changes
5. Ensure CI passes (backend compile, frontend build, `docker compose build`)
6. Describe the changes in the PR

## Documentation

Docs are a Jekyll site under `docs/`:

- Pages live in `docs/en/` (primary) and `docs/ru/` (secondary)
- Navigation: `docs/_data/nav.yml`
- UI strings: `docs/_data/ui.yml`
- Language switcher in the sidebar / mobile header
- Styles: `docs/assets/css/style.css`

After push to `main`, GitHub Actions publishes Pages: https://pyorchestrator.github.io/PyOrchestrator/en/

GitHub Wiki sources: `wiki/en/` and `wiki/ru/` — publish with `./scripts/sync-github-wiki.sh`.

## Local development

```bash
cp .env.example .env
docker compose up --build

# Frontend hot-reload (optional, outside Docker)
cd frontend && npm install && npm run dev

# Backend (optional)
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

Docs locally:

```bash
cd docs && bundle install && bundle exec jekyll serve
```

## Questions

See the [documentation](https://pyorchestrator.github.io/PyOrchestrator/en/) or open an Issue.
