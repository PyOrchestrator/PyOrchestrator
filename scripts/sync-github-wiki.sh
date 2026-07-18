#!/usr/bin/env bash
# Publish wiki/en/ and wiki/ru/ to GitHub Wiki (https://github.com/PyOrchestrator/PyOrchestrator/wiki)
# GitHub Wiki does not support nested paths — pages are flattened to en-Page.md / ru-Page.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_REPO="${WIKI_REPO:-https://github.com/PyOrchestrator/PyOrchestrator.wiki.git}"
VERSION="v0.1.13"
CLONE_DIR="$(mktemp -d)"
trap 'rm -rf "$CLONE_DIR"' EXIT

git clone --depth 1 "$WIKI_REPO" "$CLONE_DIR"
cd "$CLONE_DIR"

rm -rf en ru

cat > Home.md <<EOF
# PyOrchestrator Wiki

**Language:** **[English](en-Home)** · [Русский](ru-Home)

Sources synced from the main repository. **Default language: English.**

**Full documentation (GitHub Pages):** https://pyorchestrator.github.io/PyOrchestrator/en/  
**Current version:** ${VERSION}

## English

| Page | Topic |
|------|-------|
| [Home](en-Home) | Overview |
| [Getting-Started](en-Getting-Started) | Quick start |
| [Architecture](en-Architecture) | Architecture |
| [Control-Plane](en-Control-Plane) | Control plane |
| [Runtime](en-Runtime) | Runtime & sandbox |
| [MCP](en-MCP) | MCP for AI agents |
| [Database-Schema](en-Database-Schema) | Database schema |
| [API-Reference](en-API-Reference) | API reference |
| [Deployment](en-Deployment) | Deployment |
| [Configuration](en-Configuration) | Configuration |
| [Security](en-Security) | Security |
| [Roadmap](en-Roadmap) | Roadmap |
| [Troubleshooting](en-Troubleshooting) | Troubleshooting |

## Русский

| Страница | Раздел |
|----------|--------|
| [Home](ru-Home) | Обзор |
| [Getting-Started](ru-Getting-Started) | Быстрый старт |
| [Architecture](ru-Architecture) | Архитектура |
| [Control-Plane](ru-Control-Plane) | Панель управления |
| [Runtime](ru-Runtime) | Runtime и sandbox |
| [MCP](ru-MCP) | MCP |
| [Database-Schema](ru-Database-Schema) | Схема данных |
| [API-Reference](ru-API-Reference) | Справочник API |
| [Deployment](ru-Deployment) | Развёртывание |
| [Configuration](ru-Configuration) | Конфигурация |
| [Security](ru-Security) | Безопасность |
| [Roadmap](ru-Roadmap) | Дорожная карта |
| [Troubleshooting](ru-Troubleshooting) | Устранение неполадок |
EOF

for f in "$ROOT/wiki/en/"*.md; do
  base="$(basename "$f" .md)"
  cp "$f" "en-${base}.md"
done

for f in "$ROOT/wiki/ru/"*.md; do
  base="$(basename "$f" .md)"
  cp "$f" "ru-${base}.md"
done

git add -A
if git diff --staged --quiet; then
  echo "Wiki already up to date."
  exit 0
fi

git commit -m "docs: sync wiki from main (${VERSION})"
git push origin HEAD
