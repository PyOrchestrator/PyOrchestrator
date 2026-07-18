> **English** · **[Русский](ru-MCP)** · [← Wiki](Home)

PyOrchestrator provides an **MCP server** (`mcp/`) to manage the platform of AI agents (Cursor, Claude, custom bots).

## Transport

| Mode | When to use |
|-------|-------------------|
| **stdio** | Local development, Cursor IDE |
| **streamable-http** | Docker Compose port `8010` |

## Tools (24)

| Category | Tools |
|-----------|------------|
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
      "cwd": "/path/to/PyOrchestrator/mcp",
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

## Environment variables

| Variable | Description |
|-----------|----------|
| `PYORCH_API_URL` | Backend API |
| `PYORCH_TOKEN` | JWT (optional) |
| `PYORCH_EMAIL` / `PYORCH_PASSWORD` | Autologin |
| `MCP_TRANSPORT` | `stdio` \| `streamable-http` |
| `MCP_PORT` | HTTP port (default 8010) |

## Example workflow agent

1. `system_info` - health check
2. `list_scripts` - find the script
3. `update_script_file` - change `main.py`
4. `run_script` → `get_run_logs` - execute and read the output

More details: [mcp/README.md](https://github.com/PyOrchestrator/PyOrchestrator/blob/main/mcp/README.md)