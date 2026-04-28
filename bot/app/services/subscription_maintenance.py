from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SubscriptionMaintenanceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def deactivate_expired(self) -> int:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            text(
                "UPDATE subscriptions SET status='expired' "
                "WHERE status='active' AND expires_at IS NOT NULL AND expires_at < :now"
            ),
            {"now": now},
        )
        await self._session.commit()
        return int(result.rowcount or 0)
