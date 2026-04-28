from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.app.db.models import Subscription, User
from bot.app.db.session import SessionLocal
from bot.app.services.tariff_service import TariffService
from bot.app.utils.profile import build_profile_text

router = Router()


@router.message(Command("plans"))
async def handle_plans(message: Message) -> None:
    async with SessionLocal() as session:
        service = TariffService(session)
        await service.ensure_default_tariffs()
        tariffs = await service.list_active_tariffs()

    lines = ["Доступные тарифы:"]
    for tariff in tariffs:
        lines.append(
            f"• {tariff.name}: ${tariff.price_usd} / {tariff.months}м / {tariff.traffic_limit_gb}GB / {tariff.device_limit} devices"
        )
    lines.append("Для оплаты сразу создайте инвойс: /invoice 1m")
    await message.answer("\n".join(lines))


@router.message(Command("buy"))
async def handle_buy(message: Message) -> None:
    await message.answer(
        "Оплата: USDT TRC20 / TON / SOL. После оплаты и webhook подтверждения подписка активируется автоматически."
    )


@router.message(Command("profile"))
async def handle_profile(message: Message) -> None:
    if message.from_user is None:
        return

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
        if user is None:
            await message.answer("Профиль не найден, выполните /start")
            return

        subscription = await session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .where(Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )

    if subscription is None:
        await message.answer("Активная подписка отсутствует. Выберите тариф: /plans")
        return

    text = build_profile_text(
        username=user.username,
        telegram_id=user.telegram_id,
        plan_name=subscription.plan_name,
        mode=subscription.profile_mode,
        expires_at=subscription.expires_at,
        subscription_url=subscription.subscription_url,
        referral_code=user.referral_code,
    )
    await message.answer(text)
