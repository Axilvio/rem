from decimal import Decimal

from pydantic import BaseModel, Field


class TariffCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    months: int = Field(ge=1, le=24)
    price_usd: Decimal = Field(gt=Decimal("0"))
    traffic_limit_gb: int = Field(ge=0)
    device_limit: int = Field(ge=1, le=32)


class TariffToggleRequest(BaseModel):
    is_active: bool
