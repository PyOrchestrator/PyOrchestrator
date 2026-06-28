# PyOrchestrator — System Architecture

## Vision

PyOrchestrator is a SCADA/CMS platform for creating, scheduling, running, and monitoring thousands of isolated Python scripts and bots — all inside a **fixed set of Docker Compose services**. User scripts never get their own containers; they run in sandboxes inside a single **Runtime Engine**.

Design influences: SCADA (monitoring/control), Jenkins (CI runs), Home Assistant (automations), n8n (workflows), Airflow (scheduling), Portainer (ops UI), Node-RED (event flows), GitLab CI (pipelines).

---

## Service Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Docker Compose Network                          │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────────────┐   │
│  │ Frontend │───▶│ Backend  │───▶│ PostgreSQL  │    │ Redis            │   │
│  │ (React)  │◀───│ (FastAPI)│◀───│             │    │ cache / pubsub   │   │
│  └──────────┘    └────┬─────┘    └─────────────┘    └────────┬─────────┘   │
│                       │                                         │            │
│                       │ REST / WS                               │            │
│                       ▼                                         ▼            │
│              ┌────────────────┐    ┌──────────────┐    ┌──────────────┐     │
│              │ Runtime Engine │◀──▶│  Scheduler   │    │    MinIO     │     │
│              │ (sandboxes)    │    │ (APScheduler)│    │ file storage │     │
│              └────────┬───────┘    └──────────────┘    └──────────────┘     │
│                       │ metrics / logs                                     │
│                       ▼                                                    │
│         ┌─────────────────────────────────────────────┐                    │
│         │ Prometheus │ Grafana │ Loki │ Promtail      │                    │
│         └─────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core services (required)

| Service | Role | Tech |
|---------|------|------|
| **backend** | REST API, WebSocket hub, RBAC, secrets vault API, OTA coordinator | FastAPI, SQLAlchemy, Redis |
| **frontend** | Dashboard, script editor, monitoring UI | React, TypeScript, Vite, MUI |
| **runtime** | Single process pool; spawns isolated Python sandboxes per script run | Python, subprocess, venv, cgroups/rlimit |
| **scheduler** | Cron, intervals, webhooks, event chains; dispatches runs to runtime | APScheduler, Redis |
| **postgres** | Metadata, runs, users, schedules, audit | PostgreSQL 16 |
| **redis** | Job queue, pub/sub events, rate limits, session cache | Redis 7 |
| **minio** | Script workspaces, assets, backups, temp files | MinIO (S3-compatible) |

### Observability (bundled)

| Service | Role |
|---------|------|
| **prometheus** | Scrapes backend + runtime metrics |
| **grafana** | Dashboards (system + per-script KPIs) |
| **loki** | Log aggregation |
| **promtail** | Ships container logs to Loki |

---

## Runtime Engine — Sandbox Model

Each script execution is an **isolated sandbox** inside the Runtime Engine container — not a new Docker container.

```
Runtime Engine (single container)
├── Supervisor (async event loop)
├── Sandbox Pool Manager
│   ├── Sandbox #1  script_id=42  run_id=1001
│   │   ├── subprocess (python main.py)
│   │   ├── dedicated venv (per-script or per-run)
│   │   ├── workspace dir (bind from MinIO mount)
│   │   ├── env vars + injected secrets
│   │   ├── rlimits: CPU time, memory, open files
│   │   └── cgroup slice (when available)
│   ├── Sandbox #2  ...
│   └── Sandbox #N  (bounded by max_concurrent_runs)
└── Metrics exporter (Prometheus)
```

### Isolation guarantees

| Layer | Mechanism |
|-------|-----------|
| Process | `subprocess` with separate PID namespace where supported |
| Environment | Per-run env dict; secrets injected at runtime, never in code |
| Filesystem | Per-script workspace under `/workspaces/{script_id}/`; no cross-script paths |
| Dependencies | Per-script venv built from `requirements.txt` on enable/import |
| CPU | `RLIMIT_CPU`, optional cgroup `cpu.max` |
| Memory | `RLIMIT_AS`, cgroup `memory.max`, OOM kill scoped to child |
| Time | Wall-clock timeout via supervisor watchdog |
| Network | Optional egress policy (MVP: shared network; Production: network namespaces) |

### Dynamic script lifecycle (no restart)

1. User saves script via UI → Backend writes files to MinIO + DB row.
2. Backend publishes `script.updated` on Redis.
3. Runtime invalidates venv cache for that script_id.
4. Scheduler reloads cron entries for that script_id.
5. Next run uses fresh code without container rebuild.

---

## Data Flow

### Manual run

```
UI → POST /api/v1/scripts/{id}/run
  → Backend validates RBAC, creates Run record (queued)
  → Redis LPUSH runtime:jobs
  → Runtime pops job, prepares sandbox, streams logs to Redis + Loki
  → Backend WS pushes status to UI
  → On exit: Run updated, metrics recorded, notifications fired
```

### Scheduled run

```
Scheduler tick / cron match
  → Checks script enabled, concurrency policy, date window
  → Same queue path as manual run
```

### Webhook / event trigger

```
POST /api/v1/hooks/{token}  OR  Redis event (script.completed)
  → Scheduler creates Run with trigger_type
  → Queue to runtime
```

---

## Backend Module Layout

```
backend/app/
├── api/v1/          # REST routers (scripts, runs, groups, secrets, backups, ota)
├── core/            # config, security, deps
├── models/          # SQLAlchemy ORM
├── schemas/         # Pydantic DTOs
├── services/        # business logic
│   ├── script_service.py
│   ├── run_service.py
│   ├── secret_service.py      # envelope encryption per script
│   ├── storage_service.py     # MinIO abstraction
│   ├── notification_service.py
│   ├── backup_service.py
│   └── update_service.py      # UpdateProvider interface
├── ws/              # WebSocket hub (live logs, status)
└── integrations/    # email, telegram, mqtt clients
```

---

## Script SDK (injected into sandboxes)

Scripts receive a `pyorchestrator` client package:

```python
from pyorchestrator import Platform

platform = Platform()  # reads PYORCH_* env vars

platform.storage.upload("data/out.csv", data)
platform.secrets.get("API_TOKEN")
platform.db.query("SELECT ...")  # scoped read-only by default
platform.notify("Job done")
platform.http.get("https://...")
platform.mqtt.publish("topic", payload)
```

Secrets and tokens are **never** in source code; SDK reads from runtime-injected env + vault API.

---

## Security Model

### RBAC roles

| Role | Capabilities |
|------|--------------|
| **Administrator** | Full system config, users, OTA, backups |
| **Developer** | CRUD scripts, secrets for owned groups, run/stop |
| **Operator** | Run/stop/disable, view logs, no code edit |
| **Viewer** | Read-only dashboard and logs |

Permissions are scoped per **group** (monitoring, bots, ETL, custom).

### Secrets

- Stored encrypted at rest (AES-256-GCM, key from `SECRET_MASTER_KEY`).
- Per-script namespace; decryption only when Runtime prepares sandbox.
- Audit log on secret access.

---

## File Storage Layout (MinIO)

```
pyorchestrator/
├── scripts/{script_id}/          # project tree (main.py, modules/, ...)
├── runs/{run_id}/                # run artifacts, temp outputs
├── backups/{backup_id}/          # tarball snapshots
├── templates/{template_id}/    # script templates
└── system/                       # platform assets
```

Quotas enforced per script via `storage_quota_bytes` in DB.

---

## OTA Updates (abstract provider)

```python
class UpdateProvider(ABC):
    async def check_latest(self) -> VersionInfo: ...
    async def download(self, version: str, dest: Path) -> Path: ...
    async def verify(self, artifact: Path) -> bool: ...

class GitHubUpdateProvider(UpdateProvider):
    """Placeholder until repo URL is configured."""
```

Flow: check → download → backup → apply migrations → rolling restart via Compose → rollback on health failure.

---

## Scalability Notes

| Concern | Approach |
|---------|----------|
| Thousands of registered scripts | DB indexes on `script_id`, `status`; metadata only in Postgres |
| Concurrent runs | Runtime horizontal scaling (multiple runtime replicas + Redis queue) in Production |
| Large log volume | Loki retention policies; run logs also in `run_logs` table (truncated) |
| Venv build cost | Lazy build on first run; shared base image layers in runtime container |

MVP: **1 runtime replica**. Production: **N runtime replicas** sharing Redis job queue (still no per-script containers).

---

## API Surface (high level)

| Area | Prefix |
|------|--------|
| Auth / users | `/api/v1/auth`, `/api/v1/users` |
| Scripts & files | `/api/v1/scripts`, `/api/v1/scripts/{id}/files` |
| Runs & logs | `/api/v1/runs`, `/api/v1/scripts/{id}/runs` |
| Schedules | `/api/v1/schedules` |
| Groups | `/api/v1/groups` |
| Secrets | `/api/v1/scripts/{id}/secrets` |
| Notifications | `/api/v1/notifications` |
| Webhooks | `/api/v1/hooks/{token}` |
| Backups | `/api/v1/backups` |
| OTA | `/api/v1/system/updates` |
| Metrics | `/metrics` (Prometheus) |
| WebSocket | `/ws` |

---

## Technology Stack Summary

| Layer | Choice |
|-------|--------|
| API | FastAPI + SQLAlchemy 2 + Alembic |
| DB | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Scheduler | APScheduler (dedicated service) |
| Frontend | React 18 + TypeScript + Vite + MUI |
| Editor | Monaco Editor |
| Metrics | Prometheus + Grafana |
| Logs | Loki + Promtail |
| Storage | MinIO |
| Orchestration | Docker Compose |
