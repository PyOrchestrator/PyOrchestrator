---
layout: default
title: "Control plane"
description: "Overview of the PyOrchestrator web UI — scripts, schedules, dashboards, secrets, backups, and system settings."
---

## Pages

| Section | Path | Description |
|--------|------|----------|
| Review | `/` | KPI, runs/load/resources charts, health |
| Scripts | `/scripts` | Object Library, Filters, Bulk Actions |
| Editor | `/scripts/:id` | Monaco, multi-file, start/stop, live logs |
| Groups | `/groups` | Organizing scripts |
| Schedules | `/schedules` | Cron/interval/webhook |
| Webhooks | `/webhooks` | Incoming HTTP Triggers |
| Alerts | `/notifications` | Alerts for runs |
| Backups | `/backups` | Creation and recovery |
| System Information | `/system` | Health, RAM/disk, services |
| MCP server | `/mcp` | MCP Documentation and Status |
| Users and groups | `/users` | RBAC (Administrator only) |
| Settings | `/settings` | Profile, topic, language |

## Roles

| Role | Opportunities |
|------|-------------|
| **Administrator** | Full access, user management |
| **Developer** | Scripts, editor, schedules |
| **Operator** | Start/Stop, View |
| **Viewer** | Read only |

## Localization

Interface: **Russian** and **English** (section **Settings** → language).

## Real-time update

Dashboard and lists support polling (live/static modes). WebSocket is used to log active run in the editor.

## Theme

Light / dark / system - switch in the sidebar header.
