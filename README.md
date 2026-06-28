# PyOrchestrator

**SCADA/CMS platform** for creating, scheduling, running, and monitoring thousands of isolated Python scripts and bots — inside a fixed Docker Compose stack.

> One Runtime Engine. Many sandboxes. Zero per-script containers.

## Architecture

| Service | Description |
|---------|-------------|
| `backend` | FastAPI — REST, WebSocket, RBAC, secrets, backups |
| `frontend` | React + MUI + Monaco — dashboard & script editor |
| `runtime` | Python sandbox supervisor (subprocess + venv + rlimits) |
| `scheduler` | APScheduler — cron, intervals, webhooks, events |
| `postgres` | Metadata, runs, users, schedules |
| `redis` | Job queue, pub/sub, cache |
| `minio` | Script workspaces, assets, backups |
| `prometheus` + `grafana` + `loki` | Metrics & logs |

See [docs/architecture.md](docs/architecture.md) for full design.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

| URL | Service |
|-----|---------|
| http://localhost:5173 | Frontend UI |
| http://localhost:8000/docs | API (Swagger) |
| http://localhost:8000/health | Health check |
| http://localhost:3000 | Grafana (admin/admin) |
| http://localhost:9090 | Prometheus |
| http://localhost:9001 | MinIO Console |

## Project Structure

```
pyorchestrator/
├── backend/           # FastAPI application
│   └── app/
│       ├── api/v1/    # REST routers
│       ├── core/      # config, security
│       ├── models/    # SQLAlchemy ORM (MVP-1)
│       ├── schemas/   # Pydantic DTOs
│       └── services/  # business logic + UpdateProvider
├── frontend/          # React + TypeScript + Vite + MUI
├── runtime/           # Sandbox engine
│   └── engine/
│       ├── sandbox.py # isolation layer
│       └── main.py    # Redis queue consumer
├── scheduler/         # APScheduler service
├── infrastructure/  # Prometheus, Grafana, Loki configs
├── docs/
│   ├── architecture.md
│   ├── database-er.md
│   └── roadmap.md
├── docker-compose.yml
└── docker-compose.prod.yml
```

## Key Design Decisions

1. **No per-script containers** — all scripts run as isolated subprocess sandboxes inside `runtime`.
2. **Dynamic updates** — save script in UI → Redis event → runtime invalidates venv → no restart.
3. **Horizontal scale** — add `runtime` replicas sharing Redis queue (Production).
4. **Secrets vault** — encrypted per-script; injected at run time, never in code.
5. **OTA updates** — abstract `UpdateProvider`; `GitHubUpdateProvider` stub ready.

## Documentation

- [System Architecture](docs/architecture.md)
- [Database ER Diagram](docs/database-er.md)
- [MVP & Production Roadmap](docs/roadmap.md)

## Development Status

| Phase | Status |
|-------|--------|
| MVP-0 Foundation | ✅ Done |
| MVP-1 Script CRUD + Run | ✅ Done |
| MVP-2 Scheduler + Dashboard | ✅ Done |
| MVP-3 Editor + RBAC | ✅ Done |
| Production-1 Secrets + Backups | ✅ Done |
| Production-2 Scale + OTA | ✅ Stub ready |

## License

MIT
