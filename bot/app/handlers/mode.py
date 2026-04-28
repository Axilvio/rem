from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.app.db.session import SessionLocal
from bot.app.services.subscription_mode_service import ALLOWED_MODES, SubscriptionModeService
from bot.app.utils.mode import extract_mode_argument

router = Router()


@router.message(Command("mode"))
async def handle_mode(message: Message) -> None:
    if message.from_user is None:
        return
    mode = extract_mode_argument(message.text)
    if mode is None or mode not in ALLOWED_MODES:
        await message.answer("Используйте: /mode auto|bridge|direct")
        return

    async with SessionLocal() as session:
        updated = await SubscriptionModeService(session).set_mode(message.from_user.id, mode)

    if not updated:
        await message.answer("Не удалось изменить режим. Проверьте наличие активной подписки.")
        return
    await message.answer(f"Режим маршрутизации обновлён: {mode}")
