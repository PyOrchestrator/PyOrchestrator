> **English** · **[Русский](ru-Home)** · [← Wiki](Home)

<div class="hero">
  <span class="hero-badge">v0.1.13 Docker Compose Apache 2.0</span>
  <p class="hero-lead">
    SCADA/CMS management platform for thousands of isolated Python scripts and bots -
    one Runtime Engine, many sandboxes, no separate container for the script.
  </p>
</div>

**PyOrchestrator** is a platform for creating, scheduling, running and monitoring Python automation in a fixed Docker Compose stack: web interface, API, scheduler, isolated runtime, observability and MCP server for AI agents.

<p class="quick-links">
  <a href="en-Getting-Started">Quick start</a> ·
  <a href="en-Architecture">Architecture</a> ·
  <a href="en-Control-Plane">Control panel</a> ·
  <a href="en-MCP">MCP</a>
</p>

## Features

| Module | Description |
|--------|----------|
| **Review** | KPI, integrated activity graphs, composition of objects, state of services |
| **Scripts and bots** | CRUD, multi-file editor (Monaco), import/export, templates |
| **Groups** | Organizing scripts by category |
| **Schedules** | Cron, intervals, webhook triggers |
| **Webhooks** | External HTTP triggers |
| **Runtime** | Subprocess sandbox + venv + rlimits, Redis queue |
| **Secrets** | Encrypted storage for a script, injection at runtime |
| **Backups** | Manual and scheduled recovery |
| **Alerts** | In-app notifications for running events |
| **Observability** | Prometheus, Grafana, Loki (block in UI - only if Grafana is available) |
| **MCP** | 24+ tools for Cursor and other AI agents |
| **RBAC** | Administrator / Developer / Operator / Viewer |

## Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI 0.115, Uvicorn 0.49, SQLAlchemy 2.0, Alembic, asyncpg, PostgreSQL 16 |
| UI | React 18, TypeScript 5, Vite 5, Tailwind CSS 4, react-router-dom 7, Monaco, Recharts |
| Runtime | Python 3.12, subprocess, venv, psutil 7, Prometheus |
| Scheduler | APScheduler 3.10 |
| Queue/pub-sub | Redis 7 |
| Files | MinIO (S3-compatible) |
| MCP | `mcp` SDK, streamable HTTP + stdio |
| Infrastructure | Docker Compose |

## Quick start

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
| Grafana | http://localhost:3000 (if `GRAFANA_ENABLED=true`) |
| Prometheus | http://localhost:9090 |
| MinIO S3 API | http://localhost:9000 |
| MinIO Console | http://localhost:9001 (with `MINIO_CONSOLE_ENABLED=true`) |
| MCP (HTTP) | http://localhost:8010/mcp |

**Default login:** `admin@pyorchestrator.local` / `admin` - change the password and secrets in `.env` before production.

## Repository structure

```
PyOrchestrator/
├── backend/           # FastAPI — REST, WebSocket, RBAC
├── frontend/          # React — control panel
├── runtime/           # Sandbox engine
├── scheduler/         # APScheduler service
├── mcp/               # MCP server for AI agents
├── infrastructure/    # Prometheus, Grafana, Loki
├── docs/              # Documentation (GitHub Pages)
├── wiki/              # Copy for GitHub Wiki
└── docker-compose.yml
```

## License

[Apache License 2.0](https://github.com/PyOrchestrator/PyOrchestrator/blob/main/LICENSE)