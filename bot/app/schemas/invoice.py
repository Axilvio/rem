from decimal import Decimal

from pydantic import BaseModel, Field


class InvoiceCreateRequest(BaseModel):
    telegram_id: int
    tariff_name: str = Field(min_length=2, max_length=16)
    amount_usd: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(default="USDT", min_length=3, max_length=8)


class InvoiceCreateResponse(BaseModel):
    provider: str
    invoice_id: str
    checkout_url: str
