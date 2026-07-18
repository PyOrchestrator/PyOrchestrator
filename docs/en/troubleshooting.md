---
layout: default
title: Troubleshooting
description: Frequent problems and diagnostics
---

## Containers do not start

```bash
docker compose ps
docker compose logs backend
docker compose logs postgres
```

Check port occupancy (`5173`, `8000`, `5432`).

## Script does not run

1. Script status - `enabled`?
2. Has the `max concurrent runs` limit been reached?
3. `docker compose logs runtime` - sandbox errors?
4. API: `GET /api/v1/runs/scripts/{id}/runs`

## Stop doesn't work

- Run must be in the status `running` or `queued`
- Check Redis: backend and runtime on the same network
- Backend logs on `POST /runs/scripts/{id}/stop`

## Frontend: recharts package not found

```bash
docker compose exec frontend npm install
docker compose restart frontend
```

## MCP does not connect

```bash
curl -s http://localhost:8010/mcp
docker compose logs mcp
```

HTTP `406` - normal (server responds).

## Grafana empty

Provisioning datasource: `infrastructure/grafana/provisioning/`

Login: `admin` / `admin` (or from `.env`).

## Reset data (dev)

```bash
docker compose down -v
docker compose up --build
```

**Will delete all PostgreSQL and MinIO data.**

## Health checks

| URL | Expected response |
|-----|-----------------|
| `http://localhost:8000/health` | `{"status":"ok"}` |
| `http://localhost:9091/health` | runtime |
| `http://localhost:9092/health` | scheduler |

## Logs

```bash
docker compose logs -f backend runtime scheduler
```

Loki: Grafana → Explore → source of Loki.
