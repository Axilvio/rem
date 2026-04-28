from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy import text
import structlog
import uvicorn

from bot.app.config import get_settings
from bot.app.db.session import SessionLocal
from bot.app.handlers import configs, invoice, mode, plans, referrals, start, webhook
from bot.app.services.notification_service import NotificationService
from bot.app.services.subscription_maintenance import SubscriptionMaintenanceService
from bot.app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


def build_webhook_app() -> FastAPI:
    app = FastAPI(title="bot-webhooks", default_response_class=ORJSONResponse)
    app.include_router(webhook.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


async def subscription_notifier() -> None:
    checkpoints = [48, 24, 6]
    while True:
        now = datetime.now(timezone.utc)
        async with SessionLocal() as session:
            rows = await session.execute(
                text(
                    "SELECT users.telegram_id, subscriptions.expires_at FROM subscriptions "
                    "JOIN users ON users.id = subscriptions.user_id WHERE subscriptions.status='active'"
                )
            )
            maintenance = SubscriptionMaintenanceService(session)
            deactivated = await maintenance.deactivate_expired()
            if deactivated:
                logger.info("subscription.deactivated", count=deactivated)
            for row in rows:
                expires_at = row.expires_at
                if expires_at is None:
                    continue
                delta_hours = int((expires_at - now).total_seconds() // 3600)
                if delta_hours in checkpoints:
                    notifier = NotificationService(session)
                    should_send = await notifier.should_send_expiry_warning(
                        telegram_id=row.telegram_id,
                        hours=delta_hours,
                        expires_at_iso=expires_at.isoformat(),
                    )
                    if should_send:
                        logger.info("subscription.expiry_warning", telegram_id=row.telegram_id, hours=delta_hours)
        await asyncio.sleep(3600)


async def run_bot() -> None:
    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(plans.router)
    dp.include_router(configs.router)
    dp.include_router(mode.router)
    dp.include_router(invoice.router)
    dp.include_router(referrals.router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main() -> None:
    configure_logging()
    webhook_server = uvicorn.Server(uvicorn.Config(build_webhook_app(), host="0.0.0.0", port=8090))
    tasks = [
        asyncio.create_task(run_bot(), name="telegram-bot"),
        asyncio.create_task(webhook_server.serve(), name="webhook-server"),
        asyncio.create_task(subscription_notifier(), name="subscription-notifier"),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        with suppress(Exception):
            task.result()
    for task in pending:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    asyncio.run(main())
