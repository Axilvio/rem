# Remnawave Telegram Access Bot

Production-ready Telegram bot for Remnawave 2.7.x. The bot issues one unlimited subscription per Telegram account only if the user is a member of the configured group. If the user leaves the group, the Remnawave user is deleted and the local record is marked as revoked.

## What it does

- Long polling Telegram bot based on aiogram 3.
- Checks membership in a single configured Telegram group before issuing access.
- Creates/reuses a Remnawave user with:
  - username `tg_<telegram_id>`;
  - unlimited traffic: `trafficLimitBytes = 0`;
  - no reset strategy: `NO_RESET`;
  - HWID/device limit: `2`;
  - all current internal squads from Remnawave;
  - long expiration date so the subscription is effectively valid while the user remains in the group.
- Builds a short subscription-page URL from `REMNAWAVE_SUB_BASE_URL` and Remnawave `shortUuid`.
- Stores Telegram ↔ Remnawave mapping in SQL database.
- Revokes access on Telegram `chat_member` leave/kick events and by periodic background reconciliation.
- Sends admin notifications for issuance, revocation, access denial and background errors.

## Requirements

- Python 3.12 or 3.13.
- Telegram bot token from BotFather.
- The bot must be added to the target group and must be able to read membership changes. For reliable leave/kick events, make it an admin in the group.
- Remnawave API token with permissions for users and internal squads.
- PostgreSQL is recommended for production. SQLite works for a small single-process deployment.

## Configuration

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your-telegram-bot-token
TARGET_CHAT_ID=-1001234567890
ADMIN_CHAT_ID=123456789

REMNAWAVE_BASE_URL=https://panel.diler.tech
REMNAWAVE_TOKEN=your-remnawave-api-token
REMNAWAVE_SUB_BASE_URL=https://sub.diler.tech

DATABASE_URL=postgresql+asyncpg://rembot:password@127.0.0.1:5432/rembot
MEMBERSHIP_CHECK_INTERVAL_SECONDS=1800
```

`TARGET_CHAT_ID` must be the group/supergroup id. If you do not know it, temporarily log incoming updates or use a Telegram helper bot to get the id.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
rembot
```

## Docker image without compose

```bash
docker build -t rembot .
docker run --env-file .env --restart unless-stopped rembot
```

## Operational notes

- Do not commit `.env`; it contains the Telegram bot token and Remnawave API token.
- If Remnawave already contains `tg_<telegram_id>`, the bot reuses the existing user and stores its current subscription URL.
- The bot fetches all internal squads at issuance time. If you add a new squad later, existing users will not be automatically updated until they are recreated or updated manually.
- Telegram membership events are not the only revocation mechanism: the background job checks all active local users every `MEMBERSHIP_CHECK_INTERVAL_SECONDS` seconds.
