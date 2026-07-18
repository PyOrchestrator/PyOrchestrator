---
layout: default
title: "Architecture"
description: "PyOrchestrator service topology: FastAPI control plane, Runtime sandboxes, scheduler, PostgreSQL, Redis, MinIO, and observability stack."
---

## Concept

PyOrchestrator is a SCADA/CMS platform for creating, scheduling, running and monitoring thousands of isolated Python scripts and bots - all within a **fixed set of Docker Compose services**. User scripts do not receive separate containers; they are executed in a sandbox within a single **runtime** engine.

Design inspiration: SCADA (monitoring/control), Jenkins (CI runs), Home Assistant (automation), n8n (workflow), Airflow (scheduling), Portainer (ops UI), Node-RED (events), GitLab CI (pipelines).

---

## Service topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Docker Compose network                              │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────────────┐   │
│  │ Frontend │───▶│ Backend  │───▶│ PostgreSQL  │    │ Redis            │   │
│  │ (React)  │◀───│ (FastAPI)│◀───│             │    │ cache / pub-sub  │   │
│  └──────────┘    └────┬─────┘    └─────────────┘    └────────┬─────────┘   │
│                       │                                         │            │
│                       │ REST / WS                               │            │
│                       ▼                                         ▼            │
│              ┌────────────────┐    ┌──────────────┐    ┌──────────────┐     │
│              │ Runtime engine │◀──▶│  Scheduler   │    │    MinIO     │     │
│              │ (sandbox)      │    │ (APScheduler)│    │ files / S3   │     │
│              └────────┬───────┘    └──────────────┘    └──────────────┘     │
│                       │ metrics / logs                                     │
│                       ▼                                                    │
│         ┌─────────────────────────────────────────────┐                    │
│         │ Prometheus │ Grafana │ Loki │ Promtail      │                    │
│         └─────────────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Basic services (required)

| Service | Role | Technology |
|--------|------|------------|
| **backend** | REST API, WebSocket hub, RBAC, secrets API, OTA coordinator | FastAPI, SQLAlchemy, Redis |
| **frontend** | Dashboard, script editor, UI monitoring | React, TypeScript, Vite, Tailwind CSS |
| **runtime** | Process pool; isolated Python sandbox for each launch | Python, subprocess, venv, cgroups/rlimit |
| **scheduler** | Cron, intervals, webhooks, event chains; setting tasks at runtime | APScheduler, Redis |
| **postgres** | Metadata, runs, users, schedules, audit | PostgreSQL 16 |
| **redis** | Task queue, pub/sub, rate limits, session cache | Redis 7 |
| **minio** | Script workspaces, assets, backups, temporary files | MinIO (S3-compatible) |

### Observability (included)

| Service | Role |
|--------|------|
| **prometheus** | Collecting backend and runtime metrics |
| **grafana** | Dashboards (system and KPIs based on scripts) |
| **loki** | Log aggregation |
| **promtail** | Sending container logs to Loki |

---

## Runtime engine - sandbox model

Each script execution is an **isolated sandbox** inside the runtime container, and not a new Docker container.

```
Runtime engine (one container)
├── Supervisor (async event loop)
├── Sandbox pool manager
│   ├── Sandbox #1  script_id=42  run_id=1001
│   │   ├── subprocess (python main.py)
│   │   ├── dedicated venv (per script or run)
│   │   ├── workspace directory (bound from MinIO)
│   │   ├── environment variables + secrets
│   │   ├── rlimits: CPU, memory, open files
│   │   └── cgroup slice (if available)
│   ├── Sandbox #2  ...
│   └── Sandbox #N  (limited by max_concurrent_runs)
└── Metrics exporter (Prometheus)
```

### Insulation guarantees

| Layer | Mechanism |
|------|----------|
| Process | `subprocess` with a separate PID namespace where |
| Environment | Dictionary env to start; secrets are injected into runtime, not into code |
| File system | Workspace for script `/workspaces/{script_id}/`; without cross access |
| Dependencies | venv to a script from `requirements.txt` when enabled or imported |
| CPU | `RLIMIT_CPU`, optional cgroup `cpu.max` |
| Memory | `RLIMIT_AS`, cgroup `memory.max`, OOM kill for child process only |
| Time | Real time timeout via supervisor watchdog |
| Network | Optional egress policy (MVP: shared network; Production: network namespace) |

### Dynamic script life cycle (without restart)

1. The user saves the script in the UI → backend writes files to MinIO and a line to the database.
2. Backend publishes `script.updated` to Redis.
3. Runtime invalidates the venv cache for `script_id`.
4. The scheduler reloads the cron entries for `script_id`.
5. The next launch uses fresh code without rebuilding the container.

---

## Data streams

### Manual start

```
UI → POST /api/v1/scripts/{id}/run
  → Backend validates RBAC and creates a Run (queued)
  → Redis LPUSH runtime:jobs
  → Runtime retrieves the job, prepares the sandbox, and streams logs to Redis + Loki
  → Backend sends the status to the UI over WebSocket
  → On completion: Run is updated, metrics recorded, and notifications sent
```

### Scheduled launch

```
Scheduler tick / cron match
  → Check enabled state, concurrency limit, and date window
  → Same queue path as a manual launch
```

### Webhook or event

```
POST /api/v1/hooks/{token}  OR  Redis event (script.completed)
  → Scheduler creates a Run with trigger_type
  → Enqueue for runtime
```

---

## Backend structure

```
backend/app/
├── api/v1/          # REST routers (scripts, runs, groups, secrets, backups, ota)
├── core/            # configuration, security, dependencies
├── models/          # SQLAlchemy ORM
├── schemas/         # Pydantic DTO
├── services/        # business logic
│   ├── script_service.py
│   ├── run_service.py
│   ├── secret_service.py      # per-script envelope encryption
│   ├── storage_service.py     # MinIO abstraction
│   ├── notification_service.py
│   ├── backup_service.py
│   └── update_service.py      # UpdateProvider interface
├── ws/              # WebSocket hub (live logs, status)
└── integrations/    # email, Telegram, and MQTT clients
```

---

## SDK scripts (injection into sandbox)

The scripts receive the `pyorchestrator` client package:

```python
from pyorchestrator import Platform

platform = Platform()  # reads PYORCH_* environment variables

platform.storage.upload("data/out.csv", data)
platform.secrets.get("API_TOKEN")
platform.db.query("SELECT ...")  # read-only in the default scope
platform.notify("Task completed")
platform.http.get("https://...")
platform.mqtt.publish("topic", payload)
```

Secrets and tokens are **never** stored in the source code; The SDK reads the env injected by the runtime and the vault API.

---

## Security model

### RBAC Roles

| Role | Opportunities |
|------|-------------|
| **Administrator** | Full configuration, users, OTA, backups |
| **Developer** | CRUD scripts, secrets of their groups, starting and stopping |
| **Operator** | Start/stop/shutdown, view logs, without editing code |
| **Viewer** | Reading only dashboard and logs |

Rights are limited to **group** (monitoring, bots, ETL, custom).

### Secrets

- Encrypted storage (AES-256-GCM, key from `SECRET_MASTER_KEY`).
- Namespace for the script; decryption only when preparing sandbox at runtime.
- Audit of access to secrets.

---

## File layout (MinIO)

```
PyOrchestrator/
├── scripts/{script_id}/          # project tree (main.py, modules/, ...)
├── runs/{run_id}/                # run artifacts and temporary outputs
├── backups/{backup_id}/          # tarball snapshots
├── templates/{template_id}/      # script templates
└── system/                       # platform assets
```

Script quotas are set by the `storage_quota_bytes` field in the database.

---

## OTA updates (abstract provider)

```python
class UpdateProvider(ABC):
    async def check_latest(self) -> VersionInfo: ...
    async def download(self, version: str, dest: Path) -> Path: ...
    async def verify(self, artifact: Path) -> bool: ...

class GitHubUpdateProvider(UpdateProvider):
    """Stub until the repository URL is configured."""
```

Flow: check → download → backup → migrations → rolling restart via Compose → rollback if health fails.

---

## Scaling

| Problem | Approach |
|--------|--------|
| Thousands of registered scripts | DB indexes on `script_id`, `status`; in Postgres only metadata |
| Parallel launches | Horizontal scaling runtime (N replicas + Redis queue) in Production |
| Large volume of logs | Retention in Loki; startup logs also in `run_logs` (truncated) |
| venv build cost | Lazy build for the first launch; common layers of the runtime base image |

MVP: **1 runtime replica**. Production: **N replicas** with a shared Redis queue (still without a container per script).

---

## API (overview)

| Region | Prefix |
|---------|---------|
| Authentication and users | `/api/v1/auth`, `/api/v1/users` |
| Scripts and files | `/api/v1/scripts`, `/api/v1/scripts/{id}/files` |
| Launches and logs | `/api/v1/runs`, `/api/v1/scripts/{id}/runs` |
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

## Technology stack

| Layer | Choice |
|------|-------|
| API | FastAPI + SQLAlchemy 2 + Alembic 1.18 + Uvicorn 0.49 |
| Database | PostgreSQL 16 |
| Cache and queue | Redis 7 |
| Planner | APScheduler (separate service) |
| Frontend | React 18 + TypeScript 5 + Vite 5 + Tailwind CSS 4 + react-router-dom 7 |
| Editor | Monaco Editor |
| Metrics | Prometheus + Grafana |
| Logs | Loki + Promtail |
| Storage | MinIO |
| Orchestration | Docker Compose |
