from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.app.db.session import SessionLocal
from bot.app.services.referral_service import ReferralService
from bot.app.services.user_service import UserService
from bot.app.utils.referral import extract_ref_code

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    if message.from_user is None:
        return

    ref_code = extract_ref_code(message.text)
    async with SessionLocal() as session:
        user = await UserService(session).get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        if ref_code is not None:
            await ReferralService(session).apply_referral(user, ref_code)

    text = (
        f"Добро пожаловать, {user.username or 'пользователь'}!\n"
        "Команды:\n"
        "/plans — тарифы\n"
        "/profile — статус подписки\n"
        "/buy — инструкция по оплате\n"
        "/configs — ссылки для клиентов\n"
        "/mode — выбор маршрутизации auto|bridge|direct\n"
        "/invoice — создать инвойс по тарифу (/invoice 1m)\n"
        "/referrals — статистика по приглашениям\n"
        f"Ваш реферальный код: {user.referral_code}"
    )
    await message.answer(text)
