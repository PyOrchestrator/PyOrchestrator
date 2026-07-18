**Language:** **English** · [Русский](SECURITY.ru.md)

# Security Policy

## Supported versions

| Version | Support |
|---------|---------|
| 0.1.x   | ✅ Active |

## Reporting a vulnerability

**Do not open a public Issue** for security vulnerabilities.

Email **security@pyorchestrator.org** (or create a private GitHub Security Advisory).

Include:

- Description and impact
- Steps to reproduce
- PyOrchestrator version / commit hash
- Suggested fix (if any)

We aim to respond within **72 hours** and ship patches for critical issues in a reasonable timeframe.

## Production recommendations

- Change the admin password and all secrets in `.env` (`SECRET_KEY`, `SECRET_MASTER_KEY`, `INTERNAL_API_KEY`)
- Do not expose PostgreSQL, Redis, or MinIO ports publicly
- Use TLS for UI and API
- Restrict network egress for runtime when running untrusted scripts
- Keep base Docker images up to date
