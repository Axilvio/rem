from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.db.models import Subscription, User

ALLOWED_MODES = {"auto", "bridge", "direct"}


class SubscriptionModeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def set_mode(self, telegram_id: int, mode: str) -> bool:
        normalized = mode.lower().strip()
        if normalized not in ALLOWED_MODES:
            return False

        user = await self._session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            return False

        subscription = await self._session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .where(Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )
        if subscription is None:
            return False

        subscription.profile_mode = normalized
        await self._session.commit()
        return True
