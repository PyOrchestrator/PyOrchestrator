**Язык:** [English](README.md) · **Русский**

# PyOrchestrator

![PyOrchestrator](docs/assets/banner.png)

[![CI](https://github.com/PyOrchestrator/PyOrchestrator/actions/workflows/ci.yml/badge.svg)](https://github.com/PyOrchestrator/PyOrchestrator/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/PyOrchestrator/PyOrchestrator?label=release&color=22d3ee)](https://github.com/PyOrchestrator/PyOrchestrator/releases/latest)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-22d3ee)](https://pyorchestrator.github.io/PyOrchestrator/ru/)

**SCADA/CMS-платформа** для создания, планирования, запуска и мониторинга тысяч изолированных Python-скриптов и ботов — в фиксированном стеке Docker Compose.

> Один Runtime Engine. Много sandbox. Без отдельного контейнера на скрипт.

**Документация:** https://pyorchestrator.github.io/PyOrchestrator/ru/ · [English](https://pyorchestrator.github.io/PyOrchestrator/en/)

## Архитектура

| Сервис | Описание |
|--------|----------|
| `backend` | FastAPI — REST, WebSocket, RBAC, секреты, бэкапы |
| `frontend` | React + Tailwind + Monaco + Recharts — панель управления |
| `runtime` | Супервизор Python sandbox (subprocess + venv + rlimits) |
| `scheduler` | APScheduler — cron, интервалы, webhooks |
| `postgres` | Метаданные, runs, пользователи, расписания |
| `redis` | Очередь задач, pub/sub, кэш |
| `minio` | Workspace скриптов, ассеты, бэкапы |
| `prometheus` + `grafana` + `loki` | Метрики и логи |
| `mcp` | MCP-сервер для AI-агентов (порт 8010) |

Полное описание: [Архитектура](https://pyorchestrator.github.io/PyOrchestrator/ru/architecture/).

### AI-агенты (MCP)

PyOrchestrator предоставляет [MCP-сервер](mcp/README.md), чтобы Cursor и другие агенты могли работать со скриптами, запусками, логами, расписаниями и секретами. Пример для Cursor: [mcp/cursor-mcp.example.json](mcp/cursor-mcp.example.json).

## Быстрый старт

```bash
git clone https://github.com/PyOrchestrator/PyOrchestrator.git
cd PyOrchestrator
git checkout v0.1.13
cp .env.example .env
docker compose up --build
```

| URL | Сервис |
|-----|--------|
| http://localhost:5173 | Панель управления |
| http://localhost:8000/docs | API (Swagger) |
| http://localhost:8000/health | Health check |
| http://localhost:3000 | Grafana (`GRAFANA_ENABLED=true`) |
| http://localhost:9090 | Prometheus |
| http://localhost:9000 | MinIO S3 API |
| http://localhost:9001 | MinIO Console (`MINIO_CONSOLE_ENABLED=true`) |
| http://localhost:8010/mcp | MCP-сервер (streamable HTTP) |

**Логин по умолчанию:** `admin@pyorchestrator.local` / `admin` — смените пароль и секреты в `.env` перед production.

**Языки интерфейса:** английский (по умолчанию) и русский — переключатель в шапке сайдбара и в Настройках.

## Структура проекта

```
PyOrchestrator/
├── backend/           # FastAPI
├── frontend/          # React + TypeScript + Vite + Tailwind
├── runtime/           # Движок sandbox
├── scheduler/         # APScheduler
├── mcp/               # MCP для AI-агентов
├── infrastructure/    # Prometheus, Grafana, Loki
├── docs/              # Документация (GitHub Pages) — en/ + ru/
├── wiki/              # Копия для GitHub Wiki — en/ + ru/
├── releases/          # Двуязычные заметки GitHub Releases
├── docker-compose.yml
└── docker-compose.prod.yml
```

## Ключевые решения

1. **Без контейнера на скрипт** — все скрипты в изолированных subprocess sandbox внутри `runtime`.
2. **Динамические обновления** — сохранение в UI → событие Redis → runtime сбрасывает venv → без рестарта.
3. **Горизонтальное масштабирование** — реплики `runtime` с общей очередью Redis (`docker-compose.prod.yml`).
4. **Vault секретов** — шифрование на скрипт; инъекция при запуске, не в коде.
5. **OTA-обновления** — абстрактный `UpdateProvider`; `GitHubUpdateProvider` готов.

## Документация

| Раздел | English | Русский |
|--------|---------|---------|
| Заметки о выпуске | [en](https://pyorchestrator.github.io/PyOrchestrator/en/release-notes/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/release-notes/) |
| Быстрый старт | [en](https://pyorchestrator.github.io/PyOrchestrator/en/getting-started/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/getting-started/) |
| Архитектура | [en](https://pyorchestrator.github.io/PyOrchestrator/en/architecture/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/architecture/) |
| Панель управления | [en](https://pyorchestrator.github.io/PyOrchestrator/en/control-plane/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/control-plane/) |
| Runtime и sandbox | [en](https://pyorchestrator.github.io/PyOrchestrator/en/runtime/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/runtime/) |
| MCP | [en](https://pyorchestrator.github.io/PyOrchestrator/en/mcp/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/mcp/) |
| API | [en](https://pyorchestrator.github.io/PyOrchestrator/en/api-reference/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/api-reference/) |
| Развёртывание | [en](https://pyorchestrator.github.io/PyOrchestrator/en/deployment/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/deployment/) |
| Конфигурация | [en](https://pyorchestrator.github.io/PyOrchestrator/en/configuration/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/configuration/) |
| Безопасность | [en](https://pyorchestrator.github.io/PyOrchestrator/en/security/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/security/) |
| Дорожная карта | [en](https://pyorchestrator.github.io/PyOrchestrator/en/roadmap/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/roadmap/) |
| Устранение неполадок | [en](https://pyorchestrator.github.io/PyOrchestrator/en/troubleshooting/) | [ru](https://pyorchestrator.github.io/PyOrchestrator/ru/troubleshooting/) |

## Статус разработки

| Этап | Статус |
|------|--------|
| MVP-0 Foundation | ✅ Готово |
| MVP-1 Script CRUD + Run | ✅ Готово |
| MVP-2 Scheduler + Dashboard | ✅ Готово |
| MVP-3 Editor + RBAC | ✅ Готово |
| Production-1 Secrets + Backups | ✅ Готово |
| Production-2 Scale + OTA | ✅ Stub готов |
| Production-3 Enterprise | 🔜 Backlog |

## Релизы

| Версия | Дата | Заметки |
|--------|------|---------|
| [v0.1.13](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13) | 2026-07-07 | Обновление backend-зависимостей, синхронизация docs |
| [v0.1.12](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.12) | 2026-07-07 | Исправления API скриптов, устойчивость runtime к Redis |
| [v0.1.11](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.11) | 2026-06-30 | Опциональные Grafana/MinIO UI, OTA |
| [v0.1.0](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.0) | 2026-06-27 | Первый публичный выпуск |

## Участие

См. [CONTRIBUTING.md](CONTRIBUTING.md) · [Русский](CONTRIBUTING.ru.md). Безопасность: [SECURITY.md](SECURITY.md) · [Русский](SECURITY.ru.md).

## Лицензия

[Apache License 2.0](LICENSE)
