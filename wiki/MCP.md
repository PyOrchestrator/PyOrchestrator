PyOrchestrator поставляет **MCP-сервер** (`mcp/`) для управления платформой из AI-агентов (Cursor, Claude, custom bots).

## Транспорт

| Режим | Когда использовать |
|-------|-------------------|
| **stdio** | Локальная разработка, Cursor IDE |
| **streamable-http** | Docker Compose, порт `8010` |

## Инструменты (24)

| Категория | Tools |
|-----------|-------|
| Auth | `pyorch_login`, `pyorch_whoami` |
| Scripts | `list_scripts`, `get_script`, `create_script`, `update_script_file`, `enable_script`, `disable_script`, `delete_script` |
| Runs | `run_script`, `stop_script`, `get_run`, `get_run_logs`, `list_script_runs` |
| Automation | `list_groups`, `list_schedules`, `create_schedule`, `list_webhooks`, `create_webhook` |
| Secrets | `set_script_secret`, `list_script_secrets` |
| Platform | `dashboard_stats`, `system_info`, `list_notifications` |

Resource: `pyorch://platform/overview`

## Cursor (stdio)

```json
{
  "mcpServers": {
    "pyorchestrator": {
      "command": "python3",
      "args": ["-m", "pyorchestrator_mcp"],
      "cwd": "/path/to/pyorchestrator/mcp",
      "env": {
        "PYORCH_API_URL": "http://localhost:8000",
        "PYORCH_EMAIL": "admin@pyorchestrator.local",
        "PYORCH_PASSWORD": "admin"
      }
    }
  }
}
```

## Docker (HTTP)

```bash
docker compose up -d mcp
```

URL: `http://localhost:8010/mcp`

```json
{
  "mcpServers": {
    "pyorchestrator": {
      "url": "http://localhost:8010/mcp"
    }
  }
}
```

## Переменные окружения

| Variable | Description |
|----------|-------------|
| `PYORCH_API_URL` | Backend API |
| `PYORCH_TOKEN` | JWT (optional) |
| `PYORCH_EMAIL` / `PYORCH_PASSWORD` | Auto-login |
| `MCP_TRANSPORT` | `stdio` \| `streamable-http` |
| `MCP_PORT` | HTTP port (default 8010) |

## Пример workflow агента

1. `system_info` — health check
2. `list_scripts` — найти скрипт
3. `update_script_file` — patch `main.py`
4. `run_script` → `get_run_logs` — выполнить и прочитать вывод

Подробнее: [mcp/README.md](https://github.com/Developer-RU/pyorchestrator/blob/main/mcp/README.md)
