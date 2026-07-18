> **English** · **[Русский](ru-Deployment)** · [← Wiki](Home)

## Development (default)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: Vite dev server with hot reload (`FRONTEND_TARGET=development`)
- Backend: volume mount `./backend/app`
- All ports are published on localhost

## Production

```bash
cp .env.example .env
# edit secrets and passwords
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

`docker-compose.prod.yml`:

- Frontend - static assembly via nginx
- Runtime — `RUNTIME_REPLICAS` (default 2)
- Postgres/Redis - internal network only
- Prometheus/Grafana - bind `127.0.0.1`

## Production checklist

- [ ] Change `SECRET_MASTER_KEY`, `JWT_SECRET`, `INTERNAL_API_KEY`
- [ ] Change `POSTGRES_PASSWORD`, `MINIO_*`, `GRAFANA_ADMIN_PASSWORD`
- [ ] Change the password of the admin user
- [ ] Configure `CORS_ORIGINS` to the real UI domain
- [ ] TLS termination (nginx/traefik before frontend + API)
- [ ] Schedule backups in the UI
- [ ] Restrict access to observability ports

## Update

### OTA from control panel (recommended)

1. **Settings → Software updates → Check**
2. **Update** - download the release from GitHub, rebuild the Compose stack

### Manual update

```bash
git fetch --tags
git checkout v0.1.13
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Resources

| Profile | CPU | RAM | Disk |
|---------|-----|-----|------|
| Minimal | 2 | 4 GB | 20 GB |
| Featured | 4 | 8 GB | 50 GB |
| Loaded (50+ parallel sandbox) | 8+ | 16 GB | 100 GB |

## Publishing to GitHub Organization

1. Create org `pyorchestrator` (or your name)
2. Update `docs/_config.yml`: `url`, `baseurl`, `github_org`, `github_repo`
3. Settings → Pages → Source: **GitHub Actions**
4. Push to `main` - workflow `pages.yml` will publish documentation