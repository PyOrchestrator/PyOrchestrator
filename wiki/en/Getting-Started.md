> **English** · **[Русский](ru-Getting-Started)** · [← Wiki](Home)

## Requirements

- Docker 24+ and Docker Compose v2
- 4 GB RAM (recommended 8 GB with observability stack)
- Linux or macOS (cgroups for runtime - optional)

## Installation

```bash
git clone https://github.com/PyOrchestrator/PyOrchestrator.git
cd PyOrchestrator
git checkout v0.1.13   # or the latest tag: git describe --tags --abbrev=0
cp .env.example .env
docker compose up --build
```

Current version: [**v0.1.13**](https://github.com/PyOrchestrator/PyOrchestrator/releases/tag/v0.1.13) - [release notes](https://pyorchestrator.github.io/PyOrchestrator/release-notes/).

The first launch takes a few minutes: building images, initializing PostgreSQL, MinIO, seed demo scripts.

## Login

| Field | Default |
|------|-----------------------|
| Email | `admin@pyorchestrator.local` |
| Password | `admin` |

After logging in, open **Scripts** - demo objects will be loaded (Weather, Crypto, DAP API Poster, etc.).

## First run of the script

1. Open any script → **Editor**
2. Click **Run** - live output will appear below
3. **Stop** — stop sandbox via Redis control channel

## Services and ports

| Service | Port | Destination |
|--------|------|-----------|
| frontend | 5173 | React UI (dev) |
| backend | 8000 | REST API |
| postgres | 5432 | Metadata |
| redis | 6379 | Queue jobs |
| minio | 9000 (+ 9001 with `MINIO_CONSOLE_ENABLED=true`) | S3 API / optional Console |
| grafana | 3000 | Dashboards |
| prometheus | 9090 | Metrics |
| mcp | 8010 | MCP HTTP |

Ports are configured in `.env` - see [Configuration](en-Configuration).

## Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

More details: [Deployment](en-Deployment).

## MCP for Cursor

```bash
cd mcp && pip install -e .
```

Add the config from `mcp/cursor-mcp.example.json` to Cursor Settings → MCP.

More details: [MCP](en-MCP).

## Next

- [Architecture](en-Architecture)
- [Control Plane](en-Control-Plane)
- [Security](en-Security)