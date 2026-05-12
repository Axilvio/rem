import asyncio
import logging
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rembot.access import is_chat_member
from rembot.config import Settings
from rembot.handlers import revoke_subscription
from rembot.models import SubscriptionUser
from rembot.notify import notify_admin
from rembot.remnawave import RemnawaveClient

logger = logging.getLogger(__name__)


class MembershipSync:
    def __init__(
        self,
        bot: Bot,
        settings: Settings,
        sessionmaker: async_sessionmaker[AsyncSession],
        remnawave: RemnawaveClient,
    ) -> None:
        self._bot = bot
        self._settings = settings
        self._sessionmaker = sessionmaker
        self._remnawave = remnawave
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="membership-sync")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task:
            await self._task

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self.run_once()
            except Exception:
                logger.exception("Membership sync failed")
                await notify_admin(self._bot, self._settings, "⚠️ Ошибка фоновой проверки членства")
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._settings.membership_check_interval_seconds,
                )
            except TimeoutError:
                pass

    async def run_once(self) -> None:
        async with self._sessionmaker() as session:
            users = (
                await session.scalars(
                    select(SubscriptionUser).where(SubscriptionUser.active.is_(True))
                )
            ).all()
            for subscription in users:
                allowed = await is_chat_member(
                    self._bot,
                    self._settings.target_chat_id,
                    subscription.telegram_id,
                )
                subscription.last_membership_check_at = datetime.now(UTC)
                if allowed:
                    continue
                await revoke_subscription(
                    session=session,
                    remnawave=self._remnawave,
                    subscription=subscription,
                    reason="Пользователь больше не состоит в чате",
                )
                await notify_admin(
                    self._bot,
                    self._settings,
                    f"🗑 Подписка удалена фоновой проверкой: {subscription.telegram_id}",
                )
            await session.commit()
