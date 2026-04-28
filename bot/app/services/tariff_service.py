from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.db.models import Tariff


class TariffService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ensure_default_tariffs(self) -> None:
        existing = await self._session.scalar(select(Tariff.id).limit(1))
        if existing is not None:
            return
        defaults = [
            Tariff(name="1m", months=1, price_usd=Decimal("8.00"), traffic_limit_gb=300, device_limit=3),
            Tariff(name="3m", months=3, price_usd=Decimal("21.00"), traffic_limit_gb=1000, device_limit=5),
            Tariff(name="6m", months=6, price_usd=Decimal("39.00"), traffic_limit_gb=3000, device_limit=8),
            Tariff(name="12m", months=12, price_usd=Decimal("69.00"), traffic_limit_gb=8000, device_limit=10),
        ]
        self._session.add_all(defaults)
        await self._session.commit()

    async def list_active_tariffs(self) -> list[Tariff]:
        rows = await self._session.scalars(select(Tariff).where(Tariff.is_active.is_(True)).order_by(Tariff.months))
        return list(rows)
