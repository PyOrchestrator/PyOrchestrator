---
layout: default
description: "Open-source SCADA/CMS to create, schedule, run, and monitor isolated Python scripts and bots in Docker Compose — with Runtime sandboxes, RBAC, and MCP for AI agents."
---

<img src="{{ '/assets/banner.png' | relative_url }}" alt="PyOrchestrator" class="banner" width="1280" height="640" loading="eager">

<div class="hero">
  <div class="hero-badges">
    <a href="https://github.com/{{ site.github_org }}/{{ site.github_repo }}/actions/workflows/ci.yml" target="_blank" rel="noopener">
      <img src="https://github.com/{{ site.github_org }}/{{ site.github_repo }}/actions/workflows/ci.yml/badge.svg" alt="CI" width="88" height="20">
    </a>
    <a href="https://github.com/{{ site.github_org }}/{{ site.github_repo }}/releases/latest" target="_blank" rel="noopener">
      <img src="https://img.shields.io/github/v/release/{{ site.github_org }}/{{ site.github_repo }}?label=release&amp;color=22d3ee" alt="Latest release" width="88" height="20">
    </a>
    <a href="https://github.com/{{ site.github_org }}/{{ site.github_repo }}/blob/main/LICENSE" target="_blank" rel="noopener">
      <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache License 2.0" width="120" height="20">
    </a>
    <a href="{{ '/en/' | relative_url }}">
      <img src="https://img.shields.io/badge/docs-GitHub%20Pages-22d3ee" alt="GitHub Pages" width="120" height="20">
    </a>
  </div>
  <p class="hero-lead">
SCADA/CMS management platform for thousands of isolated Python scripts and bots -
one Runtime Engine, many sandboxes, no separate container for the script.
  </p>
</div>

> **July 7, 2026** - [release v0.1.13](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13) published: updating backend dependencies and synchronizing documentation. Previous [v0.1.12](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.12) - script API fixes and runtime resistance to Redis.
> See [release notes]({{ '/en/release-notes/' | relative_url }}).

**PyOrchestrator** is a platform for creating, scheduling, running and monitoring Python automation in a fixed Docker Compose stack: web interface, API, scheduler, isolated runtime, observability and MCP server for AI agents.

<p class="quick-links">
<a href="{{ '/en/release-notes/' | relative_url }}">Release notes</a> ·
<a href="{{ '/en/getting-started/' | relative_url }}">Quick start</a> ·
<a href="{{ '/en/architecture/' | relative_url }}">Architecture</a> ·
<a href="{{ '/en/control-plane/' | relative_url }}">Control Panel</a> ·
  <a href="{{ '/en/mcp/' | relative_url }}">MCP</a>
</p>

## Features

| Module | Description |
|--------|----------|
| **Overview** | KPIs, combined activity charts, object inventory, and service status |
| **Scripts and bots** | CRUD, multi-file editor (Monaco), import/export, templates |
| **Groups** | Organizing scripts by category |
| **Schedules** | Cron, intervals, webhook triggers |
| **Webhooks** | External HTTP triggers |
| **Runtime** | Subprocess sandbox + venv + rlimits, Redis queue |
| **Secrets** | Encrypted storage for a script, injection at runtime |
| **Backups** | Manual and scheduled backups and restoration |
| **Alerts** | In-app notifications for run events |
| **Observability** | Prometheus, Grafana, Loki (block in UI - only if Grafana is available) |
| **MCP** | 24+ tools for Cursor and other AI agents |
| **RBAC** | Administrator / Developer / Operator / Viewer |

## Stack

| Component | Technology |
|-----------|------------|
| API | FastAPI 0.115, Uvicorn 0.49, SQLAlchemy 2.0, Alembic, asyncpg, PostgreSQL 16 |
| UI | React 18, TypeScript 5, Vite 5, Tailwind CSS 4, react-router-dom 7, Monaco, Recharts |
| Runtime | Python 3.12, subprocess, venv, psutil 7, Prometheus |
| Scheduler | APScheduler 3.10 |
| Queue/pub-sub | Redis 7 |
| Files | MinIO (S3-compatible) |
| MCP | `mcp` SDK, streamable HTTP + stdio |
| Infrastructure | Docker Compose |

## Quick start

```bash
git clone https://github.com/PyOrchestrator/PyOrchestrator.git
cd PyOrchestrator
git checkout v0.1.13
cp .env.example .env
docker compose up --build
```

| Service | URL |
|--------|-----|
| Control Panel | http://localhost:5173 |
| API + Swagger | http://localhost:8000/docs |
| Grafana | http://localhost:3000 (if `GRAFANA_ENABLED=true` and the service is running) |
| Prometheus | http://localhost:9090 |
| MinIO S3 API | http://localhost:9000 |
| MinIO Console | http://localhost:9001 (only with `MINIO_CONSOLE_ENABLED=true`) |
| MCP (HTTP) | http://localhost:8010/mcp |

**Default login:** `admin@pyorchestrator.local` / `admin` - change the password and secrets in `.env` before production.

## Repository structure

```
PyOrchestrator/
├── backend/           # FastAPI — REST, WebSocket, RBAC
├── frontend/          # React — control panel
├── runtime/           # Sandbox engine
├── scheduler/         # APScheduler service
├── mcp/               # MCP server for AI agents
├── infrastructure/    # Prometheus, Grafana, Loki
├── docs/              # Documentation (GitHub Pages)
├── wiki/              # Copy for GitHub Wiki
└── docker-compose.yml
```

## License

[Apache License 2.0](https://github.com/PyOrchestrator/PyOrchestrator/blob/main/LICENSE)
