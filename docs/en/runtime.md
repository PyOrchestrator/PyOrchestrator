---
layout: default
title: "Runtime & sandbox"
description: "How PyOrchestrator isolates Python scripts: subprocess sandboxes, venv, rlimits, Redis queue, and live logs."
---

## Principle

User scripts **do not receive a separate Docker container**. All runs are executed as **isolated subprocess** inside the `runtime` service.

```
Runtime Engine
├── Redis BLPOP runtime:jobs
├── SandboxPool (semaphore max_concurrent)
│   └── One sandbox per run
│       ├── venv (per workspace)
│       ├── subprocess python entrypoint
│       ├── RLIMIT_CPU / RLIMIT_AS
│       └── wall-clock timeout
└── POST /internal/runs/* → backend
```

## Run lifecycle

1. **Queue** - backend creates `Run` (status `queued`), puts job in Redis
2. **Start** - runtime picks up the job, calls `/internal/runs/start`
3. **Execution** - sandbox runs `entrypoint` with secrets in env (`SECRET_*`)
4. **Logs** - stdout/stderr → WebSocket + PostgreSQL
5. **Completion** — exit code, duration → `/internal/runs/complete`
6. **Stop** - UI publishes `stop` to `run:{id}:control`, SIGTERM process

## Isolation

| Layer | Mechanism |
|------|----------|
| Process | `subprocess.Popen` |
| FS | `/workspaces/{script_id}/{run_id}/` |
| Dependencies | `pip install -r requirements.txt` to local venv |
| CPU/Memory | `resource.setrlimit` |
| Time | `asyncio.wait_for` wall timeout |
| Secrets | Encryption at rest, injection at run |

## Scaling

`docker compose -f docker-compose.prod.yml` - several replicas of `runtime`, a common Redis queue.

## Hot code reload

Saving the script in the UI → Redis `script:updated` → runtime invalidates the venv cache → next run with new code **without restarting the containers**.
