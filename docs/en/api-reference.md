---
layout: default
title: "API reference"
description: "REST API endpoints for PyOrchestrator: authentication, scripts, runs, schedules, webhooks, secrets, and system health."
---

Base URL: `http://localhost:8000/api/v1`

Online documentation: **http://localhost:8000/docs** (Swagger UI)

## Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{"email": "admin@pyorchestrator.local", "password": "admin"}
```

Answer: `{ "access_token": "...", "token_type": "bearer" }`

Next in the headings: `Authorization: Bearer <token>`

## Scripts

| Method | Path | Description |
|-------|------|----------|
| GET | `/scripts` | List of scripts |
| POST | `/scripts` | Create |
| GET | `/scripts/{id}` | Get |
| PATCH | `/scripts/{id}` | Update |
| DELETE | `/scripts/{id}` | Delete |
| GET | `/scripts/{id}/files` | List of files |
| PUT | `/scripts/{id}/files/{path}` | Save file |

## Runs

| Method | Path | Description |
|-------|------|----------|
| POST | `/runs/scripts/{id}/run` | Queue |
| POST | `/runs/scripts/{id}/stop` | Stop running/queued |
| GET | `/runs/scripts/{id}/runs` | History |
| GET | `/runs/{run_id}` | run status |
| GET | `/runs/{run_id}/logs` | Logs |

## Schedules and webhooks

| Method | Path | Description |
|-------|------|----------|
| GET/POST | `/schedules` | List/create |
| PATCH/DELETE | `/schedules/{id}` | Change/delete |
| GET/POST | `/webhooks` | List/create |
| POST | `/hooks/{token}` | Public call webhook |

## System

| Method | Path | Description |
|-------|------|----------|
| GET | `/system/info` | System Information |
| GET | `/mcp/info` | MCP server status |
| GET | `/dashboard/stats` | KPI dashboard |
| GET | `/dashboard/timeseries` | Time series for graphs |

## WebSocket

```
ws://localhost:8000/ws/runs/{run_id}
```

Real-time log stream (JWT in connection or cookie - depends on deployment).

## Metrics

Prometheus: `http://localhost:8000/metrics` (backend), runtime `:9093`
