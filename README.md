**Language:** **English** · [Русский](README.ru.md)

# PyOrchestrator

![PyOrchestrator](docs/assets/banner.png)

[![CI](https://github.com/PyOrchestrator/PyOrchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/PyOrchestrator/PyOrchestrator/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/PyOrchestrator/PyOrchestrator?label=release&color=22d3ee)](https://github.com/PyOrchestrator/PyOrchestrator/releases/latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-22d3ee)](https://pyorchestrator.github.io/PyOrchestrator/en/)

**SCADA/CMS platform** for creating, scheduling, running, and monitoring thousands of isolated Python scripts and bots — inside a fixed Docker Compose stack.

> One Runtime Engine. Many sandboxes. Zero per-script containers.

**Documentation:** https://pyorchestrator.github.io/PyOrchestrator/en/ · [Русский](https://pyorchestrator.github.io/PyOrchestrator/ru/)

## Architecture

| Service | Description |
|---------|-------------|
| `backend` | FastAPI — REST, WebSocket, RBAC, secrets, backups |
| `frontend` | React + Tailwind + Monaco + Recharts — control plane UI |
| `runtime` | Python sandbox supervisor (subprocess + venv + rlimits) |
| `scheduler` | APScheduler — cron, intervals, webhooks |
| `postgres` | Metadata, runs, users, schedules |
| `redis` | Job queue, pub/sub, cache |
| `minio` | Script workspaces, assets, backups |
| `prometheus` + `grafana` + `loki` | Metrics & logs |
| `mcp` | MCP server for AI agents (port 8010) |

See [Architecture](https://pyorchestrator.github.io/PyOrchestrator/en/architecture/) for full design.

### AI agents (MCP)

PyOrchestrator exposes an [MCP server](mcp/README.md) so Cursor and other agents can list scripts, run jobs, read logs, manage schedules and secrets. See [mcp/cursor-mcp.example.json](mcp/cursor-mcp.example.json) for Cursor setup.

## Quick Start

```bash
git clone https://github.com/PyOrchestrator/PyOrchestrator.git
cd PyOrchestrator
git checkout v0.1.13
cp .env.example .env
docker compose up --build
```

| URL | Service |
|-----|---------|
| http://localhost:5173 | Control Plane UI |
| http://localhost:8000/docs | API (Swagger) |
| http://localhost:8000/health | Health check |
| http://localhost:3000 | Grafana (`GRAFANA_ENABLED=true`) |
| http://localhost:9090 | Prometheus |
| http://localhost:9000 | MinIO S3 API |
| http://localhost:9001 | MinIO Console (`MINIO_CONSOLE_ENABLED=true`) |
| http://localhost:8010/mcp | MCP server (streamable HTTP) |

**Default login:** `admin@pyorchestrator.local` / `admin` — change password and `.env` secrets before production.

**UI languages:** English (default) and Russian — switcher in the sidebar header and Settings.

## Project Structure

```
PyOrchestrator/
├── backend/           # FastAPI application
│   └── app/
│       ├── api/v1/    # REST routers
│       ├── core/      # config, security
│       ├── models/    # SQLAlchemy ORM
│       ├── schemas/   # Pydantic DTOs
│       └── services/  # business logic + UpdateProvider
├── frontend/          # React + TypeScript + Vite + Tailwind
├── runtime/           # Sandbox engine
│   └── engine/
│       ├── sandbox.py # isolation layer
│       └── main.py    # Redis queue consumer
├── scheduler/         # APScheduler service
├── mcp/               # MCP server for AI agents
├── infrastructure/    # Prometheus, Grafana, Loki configs
├── docs/              # Documentation (GitHub Pages / Jekyll) — en/ + ru/
├── wiki/              # Copy for GitHub Wiki — en/ + ru/
├── releases/          # Bilingual GitHub Release notes
├── docker-compose.yml
└── docker-compose.prod.yml
```

## Key Design Decisions

1. **No per-script containers** — all scripts run as isolated subprocess sandboxes inside `runtime`.
2. **Dynamic updates** — save script in UI → Redis event → runtime invalidates venv → no restart.
3. **Horizontal scale** — add `runtime` replicas sharing Redis queue (`docker-compose.prod.yml`).
4. **Secrets vault** — encrypted per-script; injected at run time, never in code.
5. **OTA updates** — abstract `UpdateProvider`; `GitHubUpdateProvider` stub ready.

## Documentation

| Topic | English | Русский |
|-------|---------|---------|
| Release notes | [en](https://pyorchestrator.github.io/PyOrchestrator/en/release-notes/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/release-notes/) |
| Quick start | [en](https://pyorchestrator.github.io/PyOrchestrator/en/getting-started/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/getting-started/) |
| Architecture | [en](https://pyorchestrator.github.io/PyOrchestrator/en/architecture/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/architecture/) |
| Control Plane UI | [en](https://pyorchestrator.github.io/PyOrchestrator/en/control-plane/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/control-plane/) |
| Runtime & sandbox | [en](https://pyorchestrator.github.io/PyOrchestrator/en/runtime/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/runtime/) |
| MCP for AI agents | [en](https://pyorchestrator.github.io/PyOrchestrator/en/mcp/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/mcp/) |
| API reference | [en](https://pyorchestrator.github.io/PyOrchestrator/en/api-reference/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/api-reference/) |
| Deployment | [en](https://pyorchestrator.github.io/PyOrchestrator/en/deployment/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/deployment/) |
| Configuration | [en](https://pyorchestrator.github.io/PyOrchestrator/en/configuration/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/configuration/) |
| Security | [en](https://pyorchestrator.github.io/PyOrchestrator/en/security/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/security/) |
| Roadmap | [en](https://pyorchestrator.github.io/PyOrchestrator/en/roadmap/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/roadmap/) |
| Troubleshooting | [en](https://pyorchestrator.github.io/PyOrchestrator/en/troubleshooting/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/troubleshooting/) |

## Development Status

| Phase | Status |
|-------|--------|
| MVP-0 Foundation | ✅ Done |
| MVP-1 Script CRUD + Run | ✅ Done |
| MVP-2 Scheduler + Dashboard | ✅ Done |
| MVP-3 Editor + RBAC | ✅ Done |
| Production-1 Secrets + Backups | ✅ Done |
| Production-2 Scale + OTA | ✅ Stub ready |
| Production-3 Enterprise | 🔜 Backlog |

## Releases

| Version | Date | Notes |
|---------|------|-------|
| [v0.1.13](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13) | 2026-07-07 | Backend dependency updates, docs sync |
| [v0.1.12](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.12) | 2026-07-07 | Script API fixes, runtime Redis resilience |
| [v0.1.11](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.11) | 2026-06-30 | Optional Grafana/MinIO UI, OTA |
| [v0.1.0](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.0) | 2026-06-27 | First public release |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) · [Русский](CONTRIBUTING.ru.md). Security issues: [SECURITY.md](SECURITY.md) · [Русский](SECURITY.ru.md).

## License

[Apache License 2.0](LICENSE)
