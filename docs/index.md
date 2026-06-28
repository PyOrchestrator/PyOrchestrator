---
layout: default
---

<div class="hero">
  <span class="hero-badge">v0.1.0 · Docker Compose · MIT</span>
  <p class="hero-lead">
    SCADA/CMS control plane для тысяч изолированных Python-скриптов и ботов —
    один Runtime Engine, множество sandbox, без отдельного контейнера на скрипт.
  </p>
</div>

**PyOrchestrator** — платформа для создания, планирования, запуска и мониторинга Python-автоматизации в фиксированном стеке Docker Compose: веб-интерфейс, API, планировщик, изолированный runtime, observability и MCP-сервер для AI-агентов.

<p class="quick-links">
  <a href="{{ '/getting-started/' | relative_url }}">Быстрый старт</a> ·
  <a href="{{ '/architecture/' | relative_url }}">Архитектура</a> ·
  <a href="{{ '/control-plane/' | relative_url }}">Control Plane</a> ·
  <a href="{{ '/mcp/' | relative_url }}">MCP</a>
</p>

## Возможности

| Модуль | Описание |
|--------|----------|
| **Обзор (Dashboard)** | KPI, объединённые графики активности, состав объектов, health |
| **Скрипты и боты** | CRUD, multi-file editor (Monaco), import/export, шаблоны |
| **Группы** | Организация скриптов по категориям |
| **Расписания** | Cron, interval, webhook-триггеры |
| **Вебхуки** | Внешние HTTP-триггеры |
| **Runtime** | Subprocess sandbox + venv + rlimits, очередь Redis |
| **Секреты** | Шифрованное хранилище per-script, инъекция в runtime |
| **Бэкапы** | Ручные и по расписанию, restore |
| **Оповещения** | In-app notifications по событиям runs |
| **Observability** | Prometheus, Grafana, Loki |
| **MCP** | 24+ tools для Cursor и других AI-агентов |
| **RBAC** | Administrator / Developer / Operator / Viewer |

## Стек

| Компонент | Технология |
|-----------|------------|
| API | FastAPI 0.115, SQLAlchemy 2, asyncpg, PostgreSQL 16 |
| UI | React 18, TypeScript, Vite 5, Tailwind CSS 4, Monaco, Recharts |
| Runtime | Python 3.12, subprocess, venv, psutil, Prometheus |
| Scheduler | APScheduler 3.10 |
| Очередь / pub-sub | Redis 7 |
| Файлы | MinIO (S3-compatible) |
| MCP | `mcp` SDK, streamable HTTP + stdio |
| Инфраструктура | Docker Compose |

## Быстрый старт

```bash
git clone https://github.com/Developer-RU/pyorchestrator.git
cd pyorchestrator
cp .env.example .env
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| Control Plane UI | http://localhost:5173 |
| API + Swagger | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| MinIO Console | http://localhost:9001 |
| MCP (HTTP) | http://localhost:8010/mcp |

**Логин по умолчанию:** `admin@pyorchestrator.local` / `admin` — смените пароль и секреты в `.env` перед production.

## Структура репозитория

```
pyorchestrator/
├── backend/           # FastAPI — REST, WebSocket, RBAC
├── frontend/          # React control plane
├── runtime/           # Sandbox engine
├── scheduler/         # APScheduler service
├── mcp/               # MCP server для AI-агентов
├── infrastructure/    # Prometheus, Grafana, Loki
├── docs/              # Документация (GitHub Pages)
├── wiki/              # Копия для GitHub Wiki
└── docker-compose.yml
```

## Лицензия

[MIT License](https://github.com/Developer-RU/pyorchestrator/blob/main/LICENSE)
