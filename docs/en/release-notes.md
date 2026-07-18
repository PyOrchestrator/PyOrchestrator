---
layout: default
title: "Release notes"
description: "PyOrchestrator release history with highlights, fixes, and upgrade notes for each version."
---

## v0.1.13 - updating backend dependencies and synchronizing documentation

**Date:** July 7, 2026
**Tag:** [`v0.1.13`](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13)

### Changed

- **Backend:** uvicorn 0.49.0, alembic 1.18.5, python-jose 3.5.0, psutil 7.2.2
- **Runtime:** psutil 7.2.2 (in runtime image)
- Documentation, wiki, CHANGELOG and README are updated to the current stack

---

## v0.1.12 - API script fixes and runtime stability

**Date:** July 7, 2026
**Tag:** [`v0.1.12`](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.12)

### Corrected

- **Script code update:** `PUT /scripts/{id}` with the `code` field now updates the entrypoint file (as when created)
- **Deleting a script:** Correctly clearing notifications before deleting launches - no FK errors
- **Runtime:** reconnecting to Redis after a connection failure; Log publishing is resistant to temporary failures

### Changed

- **Backend:** SQLAlchemy 2.0.51, Pydantic 2.13.4, pydantic-settings 2.14.2, redis 8.0.1, python-multipart 0.0.32
- **Frontend:** react-router-dom 7.18.1, @tailwindcss/vite 4.3.2
- **CI:** actions/checkout v7

---

## v0.1.11 - optional observability and MinIO Console

**Date:** June 30, 2026
**Tag:** [`v0.1.11`](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.11)

### New

- **Observability** block on the dashboard - only if Grafana is enabled (`GRAFANA_ENABLED`) and responds to health-check
- **MinIO Console** optional: by default only S3 API (`MINIO_CONSOLE_ENABLED=false`)

### Changed

- **System** page: Bucket cards and MinIO status at full width when console is disabled
- Documentation and wiki updated for OTA and new environment variables

### OTA (since v0.1.5)

Full updates via **Settings → Software Updates** with GitHub Releases, Docker runner and rollback.

---

## v0.1.0 - first public release

**Date:** June 27, 2026
**Tag:** [`v0.1.0`](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.0) · Apache 2.0

The first stable release of the PyOrchestrator platform is a SCADA/CMS for managing thousands of isolated Python scripts and bots in a fixed Docker Compose stack.

### What's included in the release

| Region | Contents |
|---------|------------|
| **Control plane** | FastAPI API, React UI, JWT + RBAC (4 roles), groups, i18n (ru/en) |
| **Scripts** | CRUD, multi-file Monaco editor, import/export, templates, demo objects |
| **Execution** | Runtime sandbox (subprocess + venv + rlimits), Redis queue, WebSocket live logs |
| **Planning** | APScheduler: cron, intervals, webhook triggers |
| **Data** | PostgreSQL 16, MinIO (S3), encrypted vault of secrets per script |
| **Operations** | Manual and scheduled backups, in-app notifications, health/metrics |
| **Observability** | Prometheus, Grafana, Loki |
| **AI agents** | MCP server (24+ tools), HTTP + stdio |
| **Documentation** | GitHub Pages in Russian, wiki copy in repository |
| **CI** | Backend/frontend build, Docker Compose build |

### Quick start

```bash
git clone https://github.com/PyOrchestrator/PyOrchestrator.git
cd PyOrchestrator
git checkout v0.1.13
cp .env.example .env
docker compose up --build
```

| Service | URL |
|--------|-----|
| Control Panel | http://localhost:5173 |
| API + Swagger | http://localhost:8000/docs |
| MCP | http://localhost:8010/mcp |

**Default login:** `admin@pyorchestrator.local` / `admin` - change the password and secrets in `.env` before production.

---

Full list of changes: [CHANGELOG.md](https://github.com/PyOrchestrator/PyOrchestrator/blob/main/CHANGELOG.md)
