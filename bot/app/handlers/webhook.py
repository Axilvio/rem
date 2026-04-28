from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from bot.app.config import get_settings
from bot.app.db.session import SessionLocal
from bot.app.schemas.invoice import InvoiceCreateRequest
from bot.app.schemas.payment import PaymentWebhookPayload
from bot.app.services.invoice_service import InvoiceService
from bot.app.services.payment_providers import PaymentProviderVerifier
from bot.app.services.payment_service import PaymentService
from bot.app.utils.rate_limit import SlidingWindowRateLimiter

router = APIRouter(prefix="/payments", tags=["payments"])
logger = structlog.get_logger(__name__)
settings = get_settings()
rate_limiter = SlidingWindowRateLimiter(max_requests=60, window_seconds=60)
provider_verifier = PaymentProviderVerifier(settings=settings)


@router.post("/invoice")
async def create_invoice(payload: InvoiceCreateRequest) -> dict[str, str]:
    invoice = InvoiceService(settings).create_invoice(payload)
    return {"provider": invoice.provider, "invoice_id": invoice.invoice_id, "checkout_url": invoice.checkout_url}


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    x_signature: str = Header(default="", alias="X-Signature"),
    x_provider: str = Header(default="cryptomus", alias="X-Payment-Provider"),
) -> dict[str, str]:
    client_ip = request.client.host if request.client is not None else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="rate limited")

    payload_raw = await request.body()
    verification = provider_verifier.verify(provider=x_provider, payload_raw=payload_raw, signature=x_signature)
    if not verification.valid:
        logger.warning("webhook.invalid_signature", ip=client_ip, provider=x_provider, reason=verification.reason)
        raise HTTPException(status_code=401, detail=verification.reason)

    if x_provider.lower() != settings.payment_provider.lower():
        raise HTTPException(status_code=400, detail="unsupported provider")

    try:
        payload = PaymentWebhookPayload.model_validate(json.loads(payload_raw.decode("utf-8")))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="invalid payload") from exc

    session: AsyncSession
    async with SessionLocal() as session:
        service = PaymentService(session)
        result = await service.process_webhook(
            provider=x_provider,
            signature=x_signature,
            payload_raw=payload_raw,
            payload=payload,
        )

    if not result.accepted:
        logger.warning("webhook.rejected", reason=result.reason, event_id=payload.event_id)
        raise HTTPException(status_code=400, detail=result.reason)

    logger.info("webhook.processed", event_id=payload.event_id, reason=result.reason)
    return {"status": result.reason}
