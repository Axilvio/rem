from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.db.models import NotificationEvent
from bot.app.utils.notification import build_expiry_event_key


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def should_send_expiry_warning(self, telegram_id: int, hours: int, expires_at_iso: str) -> bool:
        event_key = build_expiry_event_key(telegram_id=telegram_id, hours=hours, expires_at_iso=expires_at_iso)
        existing = await self._session.scalar(
            select(NotificationEvent).where(NotificationEvent.event_key == event_key)
        )
        if existing is not None:
            return False

        self._session.add(
            NotificationEvent(
                telegram_id=telegram_id,
                event_key=event_key,
                created_at=datetime.now(timezone.utc),
            )
        )
        await self._session.commit()
        return True
