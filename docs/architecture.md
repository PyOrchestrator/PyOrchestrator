---
layout: default
title: Архитектура
description: Топология сервисов, sandbox-модель, потоки данных и безопасность
---

## Концепция

PyOrchestrator — SCADA/CMS-платформа для создания, планирования, запуска и мониторинга тысяч изолированных Python-скриптов и ботов — всё внутри **фиксированного набора сервисов Docker Compose**. Пользовательские скрипты не получают отдельные контейнеры; они выполняются в sandbox внутри единого **Runtime Engine**.

Вдохновение по дизайну: SCADA (мониторинг/управление), Jenkins (CI-запуски), Home Assistant (автоматизации), n8n (воркфлоу), Airflow (планирование), Portainer (ops UI), Node-RED (события), GitLab CI (пайплайны).

---

## Топология сервисов

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

### Основные сервисы (обязательные)

| Сервис | Роль | Технологии |
|--------|------|------------|
| **backend** | REST API, WebSocket hub, RBAC, API секретов, координатор OTA | FastAPI, SQLAlchemy, Redis |
| **frontend** | Dashboard, редактор скриптов, UI мониторинга | React, TypeScript, Vite, Tailwind CSS |
| **runtime** | Пул процессов; изолированные Python sandbox на каждый run | Python, subprocess, venv, cgroups/rlimit |
| **scheduler** | Cron, интервалы, webhooks, цепочки событий; постановка runs в runtime | APScheduler, Redis |
| **postgres** | Метаданные, runs, пользователи, расписания, аудит | PostgreSQL 16 |
| **redis** | Очередь jobs, pub/sub, rate limits, кэш сессий | Redis 7 |
| **minio** | Workspace скриптов, ассеты, бэкапы, временные файлы | MinIO (S3-compatible) |

### Observability (в комплекте)

| Сервис | Роль |
|--------|------|
| **prometheus** | Сбор метрик backend + runtime |
| **grafana** | Дашборды (система + KPI по скриптам) |
| **loki** | Агрегация логов |
| **promtail** | Отправка логов контейнеров в Loki |

---

## Runtime Engine — модель sandbox

Каждое выполнение скрипта — **изолированный sandbox** внутри контейнера Runtime Engine, а не новый Docker-контейнер.

```
Runtime Engine (один контейнер)
├── Supervisor (async event loop)
├── Sandbox Pool Manager
│   ├── Sandbox #1  script_id=42  run_id=1001
│   │   ├── subprocess (python main.py)
│   │   ├── dedicated venv (per-script или per-run)
│   │   ├── workspace dir (bind из MinIO mount)
│   │   ├── env vars + injected secrets
│   │   ├── rlimits: CPU time, memory, open files
│   │   └── cgroup slice (если доступен)
│   ├── Sandbox #2  ...
│   └── Sandbox #N  (ограничено max_concurrent_runs)
└── Metrics exporter (Prometheus)
```

### Гарантии изоляции

| Слой | Механизм |
|------|----------|
| Процесс | `subprocess` с отдельным PID namespace где поддерживается |
| Окружение | Env dict на run; секреты инъектируются в runtime, не в коде |
| Файловая система | Workspace на скрипт `/workspaces/{script_id}/`; без кросс-доступа |
| Зависимости | venv на скрипт из `requirements.txt` при enable/import |
| CPU | `RLIMIT_CPU`, опционально cgroup `cpu.max` |
| Память | `RLIMIT_AS`, cgroup `memory.max`, OOM kill только для child |
| Время | Wall-clock timeout через watchdog супервизора |
| Сеть | Опциональная политика egress (MVP: общая сеть; Production: network namespaces) |

### Динамический жизненный цикл скрипта (без рестарта)

1. Пользователь сохраняет скрипт в UI → Backend пишет файлы в MinIO + строку в БД.
2. Backend публикует `script.updated` в Redis.
3. Runtime инвалидирует venv cache для `script_id`.
4. Scheduler перезагружает cron-записи для `script_id`.
5. Следующий run использует свежий код без пересборки контейнера.

---

## Потоки данных

### Ручной запуск

```
UI → POST /api/v1/scripts/{id}/run
  → Backend проверяет RBAC, создаёт Run (queued)
  → Redis LPUSH runtime:jobs
  → Runtime забирает job, готовит sandbox, стримит логи в Redis + Loki
  → Backend WS отправляет статус в UI
  → По завершению: Run обновлён, метрики записаны, уведомления отправлены
```

### Запуск по расписанию

```
Тик scheduler / совпадение cron
  → Проверка enabled, concurrency, окна дат
  → Тот же путь очереди, что и при ручном run
```

### Webhook / событие

```
POST /api/v1/hooks/{token}  ИЛИ  Redis event (script.completed)
  → Scheduler создаёт Run с trigger_type
  → Очередь в runtime
```

---

## Структура backend

```
backend/app/
├── api/v1/          # REST routers (scripts, runs, groups, secrets, backups, ota)
├── core/            # config, security, deps
├── models/          # SQLAlchemy ORM
├── schemas/         # Pydantic DTOs
├── services/        # бизнес-логика
│   ├── script_service.py
│   ├── run_service.py
│   ├── secret_service.py      # envelope encryption per script
│   ├── storage_service.py     # абстракция MinIO
│   ├── notification_service.py
│   ├── backup_service.py
│   └── update_service.py      # интерфейс UpdateProvider
├── ws/              # WebSocket hub (live logs, status)
└── integrations/    # email, telegram, mqtt clients
```

---

## Script SDK (инъекция в sandbox)

Скрипты получают клиентский пакет `pyorchestrator`:

```python
from pyorchestrator import Platform

platform = Platform()  # читает PYORCH_* env vars

platform.storage.upload("data/out.csv", data)
platform.secrets.get("API_TOKEN")
platform.db.query("SELECT ...")  # scoped read-only по умолчанию
platform.notify("Job done")
platform.http.get("https://...")
platform.mqtt.publish("topic", payload)
```

Секреты и токены **никогда** не в исходном коде; SDK читает из env, инъектированного runtime, и vault API.

---

## Модель безопасности

### Роли RBAC

| Роль | Возможности |
|------|-------------|
| **Administrator** | Полная конфигурация, пользователи, OTA, бэкапы |
| **Developer** | CRUD скриптов, секреты своих групп, run/stop |
| **Operator** | Run/stop/disable, просмотр логов, без редактирования кода |
| **Viewer** | Только чтение dashboard и логов |

Права ограничены **группой** (monitoring, bots, ETL, custom).

### Секреты

- Хранение зашифрованным (AES-256-GCM, ключ из `SECRET_MASTER_KEY`).
- Namespace на скрипт; расшифровка только при подготовке sandbox в Runtime.
- Аудит доступа к секретам.

---

## Раскладка файлов (MinIO)

```
pyorchestrator/
├── scripts/{script_id}/          # дерево проекта (main.py, modules/, ...)
├── runs/{run_id}/                  # артефакты run, временные выходы
├── backups/{backup_id}/            # снимки tarball
├── templates/{template_id}/        # шаблоны скриптов
└── system/                         # ассеты платформы
```

Квоты на скрипт через `storage_quota_bytes` в БД.

---

## OTA-обновления (абстрактный провайдер)

```python
class UpdateProvider(ABC):
    async def check_latest(self) -> VersionInfo: ...
    async def download(self, version: str, dest: Path) -> Path: ...
    async def verify(self, artifact: Path) -> bool: ...

class GitHubUpdateProvider(UpdateProvider):
    """Заглушка до настройки URL репозитория."""
```

Поток: check → download → backup → apply migrations → rolling restart через Compose → rollback при сбое health.

---

## Масштабирование

| Задача | Подход |
|--------|--------|
| Тысячи зарегистрированных скриптов | Индексы БД на `script_id`, `status`; в Postgres только метаданные |
| Параллельные runs | Горизонтальное масштабирование runtime (N реплик + Redis queue) в Production |
| Большой объём логов | Retention Loki; run logs также в `run_logs` (с усечением) |
| Стоимость сборки venv | Lazy build на первый run; общие слои базового образа runtime |

MVP: **1 реплика runtime**. Production: **N реплик** с общей Redis-очередью (по-прежнему без контейнера на скрипт).

---

## API (обзор)

| Область | Префикс |
|---------|---------|
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

## Стек технологий

| Слой | Выбор |
|------|-------|
| API | FastAPI + SQLAlchemy 2 + Alembic |
| БД | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Scheduler | APScheduler (отдельный сервис) |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Editor | Monaco Editor |
| Metrics | Prometheus + Grafana |
| Logs | Loki + Promtail |
| Storage | MinIO |
| Orchestration | Docker Compose |
