from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.config import get_settings
from bot.app.db.models import Subscription, User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()

    async def get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        user = await self._session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is not None:
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            referral_code=secrets.token_urlsafe(6),
            trial_used=False,
        )
        self._session.add(user)
        await self._session.flush()
        await self._ensure_trial_subscription(user)
        await self._session.commit()
        return user

    async def _ensure_trial_subscription(self, user: User) -> None:
        if user.trial_used:
            return
        now = datetime.now(timezone.utc)
        trial_subscription = Subscription(
            user_id=user.id,
            plan_name="trial",
            expires_at=now + timedelta(days=self._settings.trial_days),
            status="active",
            profile_mode="auto",
            subscription_url=f"{self._settings.panel_api_base_url}/sub/{user.telegram_id}",
        )
        self._session.add(trial_subscription)
        user.trial_used = True
