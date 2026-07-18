---
layout: default
title: Security
description: Authentication, RBAC, secrets and recommendations for production
---

## Authentication

- **JWT** (Bearer) for REST API and WebSocket
- Passwords: bcrypt hash in PostgreSQL
- The admin account is created by default at the first start - **change immediately**

## RBAC

Built-in roles with rights codes (`scripts:read`, `scripts:write`, `scripts:run`, `schedules:write`, ...).

Check on each endpoint via `require_permission()`.

## Secrets of scripts

- AES-GCM encryption with `SECRET_MASTER_KEY`
- In the database: `ciphertext` + `nonce`
- At runtime: environment variables `SECRET_{KEY}`
- **Never** store tokens in the source code

## Internal API

Runtime and scheduler access the backend via `X-Internal-Key: INTERNAL_API_KEY`.

Don't publish internal endpoints externally.

## Sandbox insulation

- Subprocess + rlimits (not full VM isolation)
- Shared Docker network (egress is not filtered in v0.1)
- For untrusted code, consider network policies or a separate runtime pool

## Recommendations for production

1. Unique long secrets in `.env`
2. TLS for UI and API
3. Firewall: outside only 443/80
4. Regular backups of PostgreSQL + MinIO
5. Audit `audit_logs` (there is a table, UI is in the roadmap)
6. Disable demo seed or change credentials

## Report a vulnerability

See [SECURITY.md](https://github.com/PyOrchestrator/PyOrchestrator/blob/main/SECURITY.md) in the repository root.
