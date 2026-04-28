from decimal import Decimal

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.app.config import get_settings
from bot.app.db.models import Tariff
from bot.app.db.session import SessionLocal
from bot.app.schemas.invoice import InvoiceCreateRequest
from bot.app.services.invoice_service import InvoiceService

router = Router()


from bot.app.utils.invoice import extract_tariff_argument


@router.message(Command("invoice"))
async def handle_invoice(message: Message) -> None:
    if message.from_user is None:
        return

    tariff_name = extract_tariff_argument(message.text)
    async with SessionLocal() as session:
        tariff = await session.scalar(select(Tariff).where(Tariff.name == tariff_name, Tariff.is_active.is_(True)))

    if tariff is None:
        await message.answer("Тариф не найден. Используйте /plans")
        return

    payload = InvoiceCreateRequest(
        telegram_id=message.from_user.id,
        tariff_name=tariff.name,
        amount_usd=Decimal(tariff.price_usd),
        currency="USDT",
    )
    invoice = InvoiceService(get_settings()).create_invoice(payload)
    await message.answer(
        f"Инвойс создан:\nID: {invoice.invoice_id}\nПровайдер: {invoice.provider}\nСсылка: {invoice.checkout_url}"
    )
