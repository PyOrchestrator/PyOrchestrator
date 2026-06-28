---
layout: default
title: Безопасность
description: Аутентификация, RBAC, секреты и рекомендации для production
---

## Аутентификация

- **JWT** (Bearer) для REST API и WebSocket
- Пароли: bcrypt hash в PostgreSQL
- Default admin создаётся при первом старте — **смените немедленно**

## RBAC

Встроенные роли с permission codes (`scripts:read`, `scripts:write`, `scripts:run`, `schedules:write`, …).

Проверка на каждом endpoint через `require_permission()`.

## Секреты скриптов

- Шифрование AES-GCM с `SECRET_MASTER_KEY`
- В БД: `ciphertext` + `nonce`
- В runtime: `SECRET_{KEY}` env vars
- **Никогда** не храните токены в исходном коде

## Internal API

Runtime и scheduler → backend через `X-Internal-Key: INTERNAL_API_KEY`.

Не публикуйте internal endpoints наружу.

## Sandbox isolation

- Subprocess + rlimits (не полная VM-изоляция)
- Shared Docker network (egress не фильтруется в v0.1)
- Для untrusted code рассмотрите network policies / отдельный runtime pool

## Рекомендации production

1. Уникальные длинные секреты в `.env`
2. TLS для UI и API
3. Firewall: только 443/80 наружу
4. Регулярные бэкапы PostgreSQL + MinIO
5. Аудит `audit_logs` (таблица есть, UI — roadmap)
6. Отключите demo seed или смените credentials

## Сообщить об уязвимости

См. [SECURITY.md](https://github.com/Developer-RU/pyorchestrator/blob/main/SECURITY.md) в корне репозитория.
