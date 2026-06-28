# PyOrchestrator / SCADA CMS

SCADA/CMS control plane для изолированных Python-скриптов и ботов в Docker Compose.

**Документация (GitHub Pages):** https://developer-ru.github.io/pyorchestrator/

## Возможности

- Скрипты и боты: CRUD, Monaco multi-file editor, import/export, шаблоны
- Группы, расписания (cron/interval), вебхуки
- Runtime: subprocess sandbox + venv + rlimits, очередь Redis
- Секреты (шифрование), бэкапы, in-app notifications
- Dashboard с KPI и графиками, Prometheus/Grafana/Loki
- MCP-сервер для AI-агентов (Cursor и др.)
- RBAC: Administrator / Developer / Operator / Viewer

## Быстрый старт

```bash
git clone https://github.com/Developer-RU/pyorchestrator.git
cd pyorchestrator
cp .env.example .env
docker compose up --build
```

| Интерфейс | URL |
|-----------|-----|
| Control Plane UI | http://localhost:5173 |
| API + Swagger | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| MCP | http://localhost:8010/mcp |

Логин: `admin@pyorchestrator.local` / `admin`

## Разделы Wiki

- [Быстрый старт](Getting-Started)
- [Архитектура](Architecture)
- [Control Plane](Control-Plane)
- [Runtime](Runtime)
- [MCP](MCP)
- [Схема данных](Database-Schema)
- [API](API-Reference)
- [Развёртывание](Deployment)
- [Конфигурация](Configuration)
- [Безопасность](Security)
- [Roadmap](Roadmap)
- [Устранение неполадок](Troubleshooting)

## Архитектура

```
UI (React) ──► Backend (FastAPI) ──► PostgreSQL / MinIO
                    │                      ▲
                    ├── Redis queue ──► Runtime (sandbox)
                    └── Scheduler (APScheduler)
```

## Репозиторий

https://github.com/Developer-RU/pyorchestrator
