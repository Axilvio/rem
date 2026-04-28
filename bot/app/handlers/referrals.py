from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select

from bot.app.db.models import Referral, User
from bot.app.db.session import SessionLocal
from bot.app.utils.referrals_stats import calculate_bonus_days

router = Router()


@router.message(Command("referrals"))
async def handle_referrals(message: Message) -> None:
    if message.from_user is None:
        return

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if user is None:
            await message.answer("Профиль не найден. Используйте /start")
            return

        invited_count = await session.scalar(
            select(func.count(Referral.id)).where(Referral.referrer_id == user.id)
        )

    invited_total = int(invited_count or 0)
    bonus_days = calculate_bonus_days(invited_total)
    await message.answer(
        f"Реферальная статистика\nКод: {user.referral_code}\nПриглашено: {invited_total}\nПотенциальный бонус: {bonus_days} дней"
    )
