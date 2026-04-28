from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.app.config import get_settings
from bot.app.db.models import Payment, PaymentWebhookEvent, Subscription, Tariff, User
from bot.app.schemas.payment import PaymentProcessResult, PaymentWebhookPayload
from bot.app.utils.subscription import months_to_days

SUCCESS_STATUSES = {"paid", "paid_over", "confirm", "success"}



class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()

    async def process_webhook(
        self,
        provider: str,
        signature: str,
        payload_raw: bytes,
        payload: PaymentWebhookPayload,
    ) -> PaymentProcessResult:
        payload_hash = hashlib.sha256(payload_raw).hexdigest()
        event = PaymentWebhookEvent(
            provider=provider,
            event_id=payload.event_id,
            signature=signature,
            payload_hash=payload_hash,
        )
        self._session.add(event)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            return PaymentProcessResult(accepted=True, reason="duplicate event")

        user = await self._session.scalar(select(User).where(User.telegram_id == payload.telegram_id))
        if user is None:
            return PaymentProcessResult(accepted=False, reason="user not found")

        tariff = await self._session.scalar(select(Tariff).where(Tariff.name == payload.tariff_name))
        if tariff is None:
            tariff = Tariff(name="1m", months=1, price_usd=payload.amount_usd, traffic_limit_gb=300, device_limit=3)
            self._session.add(tariff)
            await self._session.flush()

        payment = Payment(
            user_id=user.id,
            provider=provider,
            external_id=payload.order_id,
            tariff_id=tariff.id,
            amount_usd=payload.amount_usd,
            currency=payload.currency,
            status=payload.status,
            raw_payload=payload.model_dump(mode="json"),
        )
        self._session.add(payment)

        if payload.status.lower() in SUCCESS_STATUSES:
            await self._activate_or_extend_subscription(user, tariff)

        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            return PaymentProcessResult(accepted=True, reason="duplicate order")
        return PaymentProcessResult(accepted=True, reason="processed")

    async def _activate_or_extend_subscription(self, user: User, tariff: Tariff) -> None:
        now = datetime.now(timezone.utc)
        active_subscription = await self._session.scalar(
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .where(Subscription.status == "active")
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )

        extend_days = months_to_days(tariff.months)
        if active_subscription is None:
            new_sub = Subscription(
                user_id=user.id,
                plan_name=tariff.name,
                status="active",
                profile_mode="auto",
                expires_at=now + timedelta(days=extend_days),
                subscription_url=f"{self._settings.panel_api_base_url}/sub/{user.telegram_id}",
            )
            self._session.add(new_sub)
            return

        base = active_subscription.expires_at if active_subscription.expires_at and active_subscription.expires_at > now else now
        active_subscription.expires_at = base + timedelta(days=extend_days)
