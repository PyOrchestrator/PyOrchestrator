# PyOrchestrator — Development Roadmap

## Phase Overview

| Phase | Target | Duration (est.) | Outcome |
|-------|--------|-----------------|---------|
| **MVP-0** | Foundation | 2 weeks | Compose up, health checks, empty UI shell |
| **MVP-1** | Script CRUD + Run | 3 weeks | Create/edit/run scripts, basic logs |
| **MVP-2** | Scheduler + Dashboard | 3 weeks | Cron, KPI cards, run history |
| **MVP-3** | Editor + Groups | 2 weeks | Monaco multi-file, groups, RBAC basic |
| **Production-1** | Hardening | 4 weeks | Secrets, notifications, backups |
| **Production-2** | Scale + OTA | 4 weeks | Multi-runtime, OTA, full RBAC |
| **Production-3** | Enterprise | ongoing | MQTT, advanced isolation, HA Postgres |

---

## MVP-0 — Foundation (Week 1–2)

### Goals
- Docker Compose stack starts with one command
- Backend connects to Postgres + Redis + MinIO
- Frontend serves login placeholder
- Runtime and Scheduler processes start and report health

### Deliverables
- [x] Project structure and architecture docs
- [ ] `docker compose up` — all services healthy
- [ ] Alembic initial migration (users, scripts, runs)
- [ ] `GET /health`, `GET /api/v1/system/info`
- [ ] Prometheus scrapes backend + runtime `/metrics`
- [ ] Grafana provisioned with system dashboard stub
- [ ] CI: lint + build images

### Exit criteria
All containers pass healthcheck; API returns 200 on `/health`.

---

## MVP-1 — Script Management & Execution (Week 3–5)

### Goals
- Full script lifecycle without system restart
- Single-file scripts run in sandbox with timeout and memory limit

### Features
| Feature | Priority |
|---------|----------|
| Create / edit / delete script | P0 |
| Enable / disable script | P0 |
| Manual run / stop | P0 |
| Stream logs (WebSocket) | P0 |
| Run history list | P0 |
| Copy script | P1 |
| Import / export (zip) | P1 |
| Basic templates (3 system templates) | P1 |

### Runtime (MVP scope)
- Subprocess + dedicated workspace directory
- `RLIMIT_CPU`, `RLIMIT_AS`, wall-clock timeout
- Per-script venv from `requirements.txt`
- Log capture stdout/stderr → Redis stream → WS

### API endpoints
```
POST   /api/v1/scripts
GET    /api/v1/scripts
GET    /api/v1/scripts/{id}
PUT    /api/v1/scripts/{id}
DELETE /api/v1/scripts/{id}
POST   /api/v1/scripts/{id}/run
POST   /api/v1/scripts/{id}/stop
GET    /api/v1/scripts/{id}/runs
GET    /api/v1/runs/{id}/logs
WS     /ws/runs/{id}
```

### Exit criteria
User creates script in UI, runs it, sees logs and success/fail status.

---

## MVP-2 — Scheduler & Monitoring (Week 6–8)

### Goals
- Cron and interval scheduling
- Dashboard with KPI cards and basic charts

### Features
| Feature | Priority |
|---------|----------|
| Cron expression schedules | P0 |
| Interval schedules | P0 |
| Max concurrent runs per script | P0 |
| Start/end date window | P1 |
| Webhook trigger (static token) | P1 |
| Dashboard KPI cards | P0 |
| CPU / memory system charts (Grafana embed) | P0 |
| Runs per day chart | P1 |
| Error count last 24h | P0 |
| Per-script status panel | P0 |

### Scheduler service
- APScheduler with Redis job store (shared state)
- Publishes to `runtime:jobs` on trigger
- Reload on `scheduler:reload` pub/sub

### Exit criteria
Script runs on cron without manual action; dashboard shows live metrics.

---

## MVP-3 — Editor, Groups & RBAC (Week 9–10)

### Goals
- Production-quality code editor
- Organize scripts into groups
- Four roles with group-scoped permissions

### Features
| Feature | Priority |
|---------|----------|
| Monaco editor, Python syntax | P0 |
| Multi-file project tree | P0 |
| `requirements.txt` editor | P0 |
| Syntax check (ast.parse) | P1 |
| Format (black, optional) | P2 |
| Project search | P1 |
| Groups CRUD with color/icon | P0 |
| Roles: Admin, Developer, Operator, Viewer | P0 |
| JWT auth + login page | P0 |

### Exit criteria
Developer role edits multi-file bot in group "bots", Operator can run but not edit.

---

## Production-1 — Security, Secrets & Notifications (Week 11–14)

### Goals
- Secrets vault, notification channels, backup/restore

### Features
| Feature | Priority |
|---------|----------|
| Per-script secrets (encrypted) | P0 |
| SDK `platform.secrets.get()` | P0 |
| Email notifications | P1 |
| Telegram notifications | P1 |
| Webhook notifications | P0 |
| In-app notifications | P0 |
| Manual backup | P0 |
| Scheduled backup | P1 |
| Restore from backup | P0 |
| Export/import full config | P1 |
| Audit log | P1 |
| Run on script-complete event | P1 |
| API trigger with auth | P0 |

### Exit criteria
Secrets not visible in code; backup restores scripts + DB on clean install.

---

## Production-2 — Scale, OTA & Advanced Runtime (Week 15–18)

### Goals
- Horizontal runtime scaling
- OTA update framework
- Rich per-run metrics

### Features
| Feature | Priority |
|---------|----------|
| Multiple runtime replicas (Redis queue) | P0 |
| `UpdateProvider` interface | P0 |
| `GitHubUpdateProvider` stub | P0 |
| OTA UI: check, apply, rollback | P0 |
| Pre-update automatic backup | P0 |
| Per-run CPU/memory/thread sampling | P0 |
| cgroup v2 limits (Linux) | P1 |
| Storage quotas per script | P1 |
| Temp vs persistent storage API | P1 |
| MQTT client in SDK | P2 |
| Dependency tree display in UI | P2 |

### Exit criteria
2 runtime containers drain shared queue; OTA apply + rollback tested on staging.

---

## Production-3 — Enterprise & HA (ongoing)

### Features (backlog)
- Postgres replication / managed DB option
- Network namespace isolation per sandbox
- SSO (OIDC/SAML)
- Multi-tenancy
- Custom Grafana dashboards per group
- Script marketplace / shared templates
- Git sync for script sources
- Canary runs / dry-run mode
- SLA alerting

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Venv build slow for many scripts | Lazy build, venv cache, shared base packages |
| Memory leak in user script | Per-run subprocess + hard memory cap + kill |
| Scheduler drift | Redis distributed lock; single leader scheduler in MVP |
| Log volume | Loki retention; paginated API; optional S3 cold storage |
| Secret leakage | Never return decrypted secrets via API; audit access |

---

## MVP vs Production Feature Matrix

| Capability | MVP | Production |
|------------|-----|------------|
| Script CRUD | ✅ | ✅ |
| Multi-file projects | ✅ (MVP-3) | ✅ |
| Sandbox isolation | Basic rlimits | + cgroups, optional netns |
| Cron / interval | ✅ | ✅ |
| Event / chain triggers | ❌ | ✅ |
| Webhook trigger | Basic | ✅ + rate limits |
| RBAC | ✅ (MVP-3) | ✅ + audit |
| Secrets vault | ❌ | ✅ |
| Notifications | ❌ | ✅ |
| Backups | ❌ | ✅ |
| OTA updates | ❌ | ✅ |
| Multi-runtime | ❌ | ✅ |
| Prometheus/Grafana | Basic | Full dashboards |
| MQTT | ❌ | ✅ |

---

## Suggested Sprint Order (first 10 weeks)

```
Sprint 1: Compose, DB migrations, health, auth skeleton
Sprint 2: Script CRUD API + MinIO file storage
Sprint 3: Runtime sandbox v1 + manual run + logs WS
Sprint 4: Frontend script list + run panel
Sprint 5: Scheduler cron + interval
Sprint 6: Dashboard KPI + Grafana panels
Sprint 7: Monaco editor + file tree
Sprint 8: Groups + RBAC enforcement
Sprint 9: Import/export + templates
Sprint 10: Hardening, docs, MVP release tag v0.1.0
```
