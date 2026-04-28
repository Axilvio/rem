from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.app.db.models import Subscription, User
from bot.app.db.session import SessionLocal
from bot.app.services.config_export import ConfigExportService

router = Router()


@router.message(Command("configs"))
async def handle_configs(message: Message) -> None:
    if message.from_user is None:
        return

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if user is None:
            await message.answer("Сначала выполните /start")
            return
        subscription = await session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .where(Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )

    if subscription is None or subscription.subscription_url is None:
        await message.answer("Активная подписка не найдена. Оформите тариф командой /plans")
        return

    bundle = ConfigExportService().build_bundle(subscription.subscription_url, subscription.profile_mode)
    text = (
        "Конфиги для клиентов:\n"
        f"v2rayNG: {bundle.v2rayng}\n"
        f"Hiddify: {bundle.hiddify}\n"
        f"Nekobox: {bundle.nekobox}\n"
        f"Sing-box: {bundle.singbox}\n"
        f"Clash: {bundle.clash}"
    )
    await message.answer(text)
