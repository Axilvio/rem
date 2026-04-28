from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentWebhookPayload(BaseModel):
    event_id: str = Field(min_length=3, max_length=128)
    order_id: str = Field(min_length=2, max_length=128)
    status: str = Field(min_length=2, max_length=64)
    amount_usd: Decimal = Field(ge=Decimal("0.01"))
    currency: str = Field(default="USDT", min_length=2, max_length=16)
    telegram_id: int
    tariff_name: str = Field(default="1m", min_length=2, max_length=16)


class PaymentProcessResult(BaseModel):
    accepted: bool
    reason: str
