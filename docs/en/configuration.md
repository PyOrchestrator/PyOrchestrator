---
layout: default
title: Configuration
description: Environment variables and service settings
---

All variables are in `.env` (see `.env.example`).

## Application

| Variable | Default | Description |
|------------|--------------|----------|
| `APP_ENV` | `development` | Environment |
| `APP_VERSION` | `0.1.13` | API version |

## Safety

| Variable | Description |
|------------|----------|
| `SECRET_MASTER_KEY` | AES key for script secrets (32+ characters) |
| `JWT_SECRET` | JWT Signature |
| `INTERNAL_API_KEY` | Auth runtime → backend internal API |
| `CORS_ORIGINS` | Allowed origins UI |

## Database

| Variable | Default |
|------------|--------------|
| `POSTGRES_DB` | `pyorchestrator` |
| `POSTGRES_USER` | `pyorch` |
| `POSTGRES_PASSWORD` | `pyorch_secret` |
| `POSTGRES_PORT` | `5432` |

## Runtime

| Variable | Default | Description |
|------------|--------------|----------|
| `MAX_CONCURRENT_SANDBOXES` | `50` | Parallel sandbox |
| `DEFAULT_MAX_MEMORY_MB` | `512` | RAM sandbox limit |
| `DEFAULT_MAX_CPU_SECONDS` | `300` | CPU time limit |
| `DEFAULT_WALL_TIMEOUT_SEC` | `3600` | Wall timeout |
| `RUNTIME_REPLICAS` | `1` | Replicas in prod |

## Frontend

| Variable | Description |
|------------|----------|
| `VITE_API_URL` | Browser backend URL |
| `VITE_WS_URL` | URL WebSocket |
| `FRONTEND_TARGET` | `development` \| `production` |

## MCP

| Variable | Default |
|------------|--------------|
| `MCP_PORT` | `8010` |
| `MCP_PYORCH_EMAIL` | email admin |
| `MCP_PYORCH_PASSWORD` | admin password |

## Script limits

In the UI when creating/editing a script:

- `max_concurrent_runs` — max. parallel runs
- `max_runtime_seconds` — max. lead time
- `max_memory_bytes` - memory limit
- `storage_quota_bytes` - storage quota

## MinIO

| Variable | Default | Description |
|------------|--------------|----------|
| `MINIO_ACCESS_KEY` | `minioadmin` | S3 access key |
| `MINIO_SECRET_KEY` | `minioadmin` | S3 secret key |
| `MINIO_BUCKET` | `pyorchestrator` | Bucket for workspaces |
| `MINIO_PORT` | `9000` | S3 API |
| `MINIO_CONSOLE_ENABLED` | `false` | MinIO Web Console (port 9001); S3 API works without it |
| `MINIO_CONSOLE_PORT` | `9001` | Console port (if enabled) |
| `MINIO_CONSOLE_PUBLIC_URL` | *(empty - `http://localhost:{MINIO_CONSOLE_PORT}`)* | Public link to console |

With `MINIO_CONSOLE_ENABLED=false`, the link to the MinIO web console does not go to `/api/v1/system/info` and is hidden on the System page.

## Grafana and observability

| Variable | Default | Description |
|------------|--------------|----------|
| `GRAFANA_PUBLIC_URL` | *(empty - the link is hidden in the UI)* | Link to Grafana in panel |
| `GRAFANA_INTERNAL_URL` | `http://grafana:3000` | URL for health-check from backend |
| `GRAFANA_ADMIN_USER` | `admin` | Login Grafana |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana password |

The **Observability** panel on the dashboard is shown only if Grafana is available: the backend checks `/api/health` against `GRAFANA_INTERNAL_URL`, and gives the link from `GRAFANA_PUBLIC_URL` (or internal URL if public is not specified).

Provisioning: `infrastructure/grafana/provisioning/`

## OTA updates

| Variable | Default | Description |
|------------|--------------|----------|
| `GITHUB_UPDATE_REPO` | `PyOrchestrator/PyOrchestrator` | Release Repository |
| `UPDATE_EXECUTOR_ENABLED` | `true` | Docker update runner |
| `UPDATE_DEPLOY_MODE` | `docker` | Deploy mode (`docker`) |
| `PYORCH_HOST_PROJECT_ROOT` | _(auto)_ | Path to the project on the host; determined automatically |

Update: **Settings → Software updates** in the control panel.
