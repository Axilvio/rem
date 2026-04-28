# remnawave-vpn-pro

Production-ready reference stack: Remnawave Panel + 3 Node topology + Telegram bot + FastAPI admin.

## Components
- `infra/` — production docker compose for panel and nodes
- `bot/` — aiogram + webhook + Remnawave SDK integration
- `admin/` — FastAPI + HTMX + Tailwind admin panel
- `sdk/` — typed wrappers over official SDK
- `migrations/` — Alembic migrations
- `scripts/` — install/deploy/backup/health scripts
