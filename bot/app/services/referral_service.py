from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.db.models import Referral, User


class ReferralService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def apply_referral(self, new_user: User, ref_code: str) -> bool:
        referrer = await self._session.scalar(select(User).where(User.referral_code == ref_code))
        if referrer is None or referrer.id == new_user.id:
            return False

        existing = await self._session.scalar(select(Referral).where(Referral.invited_telegram_id == new_user.telegram_id))
        if existing is not None:
            return False

        new_user.referred_by_user_id = referrer.id
        self._session.add(Referral(referrer_id=referrer.id, invited_telegram_id=new_user.telegram_id, bonus_days=7))
        await self._session.commit()
        return True
