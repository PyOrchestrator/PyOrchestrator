> **English** · **[Русский](ru-Roadmap)** · [← Wiki](Home)

## Status v0.1.13

**Latest release:** [v0.1.13](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13) (July 7, 2026)

| Phase | Status | Notes |
|-----------|--------|-----------|
| MVP-0 Foundation | ✅ | Compose, auto-migrate database, health, Prometheus/Grafana/Loki, CI |
| MVP-1 Script CRUD + Run | ✅ | CRUD, run/stop, logs WS, import/export, templates |
| MVP-2 Scheduler + Dashboard | ✅ | Cron/interval, KPI dashboard, webhooks |
| MVP-3 Editor + RBAC | ✅ | Monaco editor, JWT auth, 4 roles, groups |
| Production-1 | ✅ | Vault of secrets, notifications, backups |
| Production-2 | ✅ | OTA updates, UpdateProvider, multi-runtime compose prod, metrics |
| Production-3 | 🔜 | MQTT, HA Postgres, advanced isolation - backlog |

---

## Phase overview

| Phase | Goal | Deadline (estimate) | Result |
|------|------|--------------|-----|
| **MVP-0** | Foundation | 2 weeks | Compose up, health checks, empty UI shell |
| **MVP-1** | Script CRUD + Run | 3 weeks | Creating/editing/running scripts, basic logs |
| **MVP-2** | Scheduler + Dashboard | 3 weeks | Cron, KPI cards, history runs |
| **MVP-3** | Editor + Groups | 2 weeks | Monaco multi-file, groups, basic RBAC |
| **Production-1** | Hardening | 4 weeks | Secrets, notifications, backups |
| **Production-2** | Scale + OTA | 4 weeks | Multi-runtime, OTA, full RBAC |
| **Production-3** | Enterprise | ongoing | MQTT, advanced isolation, HA Postgres |

---

## MVP-0 – Foundation (weeks 1–2)

### Goals
- Docker Compose stack starts with one command
- Backend connects to Postgres + Redis + MinIO
- Frontend renders the login page
- Runtime and Scheduler start and report on health

### Results
- [x] Project structure and architecture documentation
- [ ] `docker compose up` — all services are healthy
- [ ] Alembic initial migration (users, scripts, runs)
- [ ] `GET /health`, `GET /api/v1/system/info`
- [ ] Prometheus scrapes backend + runtime `/metrics`
- [ ] Grafana with system dashboard template
- [ ] CI: lint + image build

### Exit criteria
All containers undergo health check; The API returns 200 on `/health`.

---

## MVP-1 - Script Management and Execution (Weeks 3-5)

### Goals
- Full script life cycle without system restart
- Single-file scripts in sandbox with timeout and memory limit

### Features
| Function | Priority |
|---------|-----------|
| Creating / editing / deleting a script | P0 |
| Enable/disable script | P0 |
| Manual run/stop | P0 |
| Stream logs (WebSocket) | P0 |
| History list runs | P0 |
| Copying the script | P1 |
| Import/export (zip) | P1 |
| Basic templates (3 system) | P1 |

### Runtime (scope MVP)
- Subprocess + dedicated workspace
- `RLIMIT_CPU`, `RLIMIT_AS`, wall-clock timeout
- venv to the script from `requirements.txt`
- Capture stdout/stderr → Redis stream → WS

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
The user creates a script in the UI, runs it, sees logs and success/fail status.

---

## MVP-2 - Scheduler and Monitoring (weeks 6–8)

### Goals
- Cron and interval schedules
- Dashboard with KPI cards and basic graphs

### Features
| Function | Priority |
|---------|-----------|
| Cron schedules | P0 |
| Interval-schedules | P0 |
| Max concurrent runs per script | P0 |
| Window start/end date | P1 |
| Webhook trigger (static token) | P1 |
| KPI dashboard cards | P0 |
| CPU/memory graphs (Grafana embed) | P0 |
| Runs per day chart | P1 |
| Errors in 24 hours | P0 |
| Script status panel | P0 |

### Service scheduler
- APScheduler with Redis job store (shared state)
- Publishing to `runtime:jobs` when triggered
- Reload by pub/sub `scheduler:reload`

### Exit criteria
The script is run via cron without manual action; dashboard shows live metrics.

---

## MVP-3 - Editor, Groups and RBAC (Weeks 9–10)

### Goals
- Production-level code editor
- Organizing scripts into groups
- Four roles with rights in the scope group

### Features
| Function | Priority |
|---------|-----------|
| Monaco editor, Python syntax | P0 |
| Multi-file project tree | P0 |
| Editor `requirements.txt` | P0 |
| Syntax checking (ast.parse) | P1 |
| Formatting (black, optional) | P2 |
| Search by project | P1 |
| CRUD groups with color/icon | P0 || Roles: Admin, Developer, Operator, Viewer | P0 |
| JWT auth + login page | P0 |

### Exit criteria
Developer edits a multi-file bot in the “bots” group; Operator can launch it, but not edit it.

---

## Production-1 - Security, Secrets and Notices (Weeks 11–14)

### Goals
- Vault of secrets, notification channels, backup/restore

### Features
| Function | Priority |
|---------|-----------|
| Secrets for the script (encryption) | P0 |
| SDK `platform.secrets.get()` | P0 |
| Email Notifications | P1 |
| Telegram notifications | P1 |
| Webhook notifications | P0 |
| In-app notifications | P0 |
| Manual backup | P0 |
| Scheduled backup | P1 |
| Restore from backup | P0 |
| Export/import full configuration | P1 |
| Audit log | P1 |
| Run on script-complete event | P1 |
| API trigger with auth | P0 |

### Exit criteria
Secrets are not visible in the code; backup restores scripts + database on a clean installation.

---

## Production-2 - Scale, OTA and advanced runtime (weeks 15–18)

### Goals
- Horizontal scaling runtime
- OTA update framework
- Detailed metrics on run

### Features
| Function | Priority |
|---------|-----------|
| Multiple runtime replicas (Redis queue) | P0 |
| Interface `UpdateProvider` | P0 |
| Stub `GitHubUpdateProvider` | P0 |
| OTA UI: check, apply, rollback | P0 |
| Auto backup before update | P0 |
| Sampling CPU/memory/threads on run | P0 |
| cgroup v2 limits (Linux) | P1 |
| Storage quotas per script | P1 |
| API temp vs persistent storage | P1 |
| MQTT client in SDK | P2 |
| UI dependency tree | P2 |

### Exit criteria
2 runtime containers process a common queue; OTA apply + rollback checked for staging.

---

## Production-3 - Enterprise and HA (ongoing)

### Backlog
- Postgres / managed DB replication
- Network namespace isolation on sandbox
- SSO (OIDC/SAML)
- Multi-tenancy
- Custom Grafana dashboard per group
- Marketplace scripts/general templates
- Git sync script sources
- Canary runs / dry-run mode
- SLA alerting

---

## Risk register

| Risk | Mitigation |
|------|-----------|
| Slow venv build for many scripts | Lazy build, venv cache, common core packages |
| Memory leak in user script | Subprocess on run + hard memory cap + kill |
| Drift scheduler | Redis distributed lock; one leader scheduler in MVP |
| Log volume | Retention Loki; paginated API; optional S3 cold storage |
| Leaked secrets | Do not return decrypted secrets via the API; access audit |

---

## Matrix MVP vs Production

| Opportunity | MVP | Production |
|------------|-----|------------|
| Script CRUD | ✅ | ✅ |
| Multi-file projects | ✅ (MVP-3) | ✅ |
| Sandbox insulation | Basic rlimits | + cgroups, optional netns |
| Cron/interval | ✅ | ✅ |
| Event/chain triggers | ❌ | ✅ |
| Webhook trigger | Basic | ✅ + rate limits |
| RBAC | ✅ (MVP-3) | ✅ + audit |
| Vault of secrets | ❌ | ✅ |
| Notifications | ❌ | ✅ |
| Backups | ❌ | ✅ |
| OTA updates | ❌ | ✅ |
| Multi-runtime | ❌ | ✅ |
| Prometheus/Grafana | Basic | Complete Dashboards |
| MQTT | ❌ | ✅ |

---

## Recommended order of sprints (first 10 weeks)

```
Sprint 1: Compose, database migrations, health, auth foundation
Sprint 2: Script CRUD API + MinIO file storage
Sprint 3: Runtime sandbox v1 + manual run + WebSocket logs
Sprint 4: Frontend script list + run panel
Sprint 5: Scheduler cron + interval
Sprint 6: Dashboard KPIs + Grafana panels
Sprint 7: Monaco editor + file tree
Sprint 8: Groups + RBAC enforcement
Sprint 9: Import/export + templates
Sprint 10: Hardening, docs, MVP v0.1.0 release
```