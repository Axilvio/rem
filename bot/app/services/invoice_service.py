from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol


class InvoiceSettings(Protocol):
    payment_provider: str


class InvoicePayload(Protocol):
    telegram_id: int
    tariff_name: str
    amount_usd: object
    currency: str


@dataclass(slots=True)
class InvoiceResult:
    provider: str
    invoice_id: str
    checkout_url: str


class InvoiceService:
    def __init__(self, settings: InvoiceSettings) -> None:
        self._settings = settings

    def create_invoice(self, request: InvoicePayload) -> InvoiceResult:
        payload = f"{request.telegram_id}:{request.tariff_name}:{request.amount_usd}:{request.currency}"
        invoice_id = hashlib.sha256(payload.encode()).hexdigest()[:16]
        provider = self._settings.payment_provider.lower()
        checkout_url = f"https://pay.example/{provider}/{invoice_id}?amount={request.amount_usd}&currency={request.currency}"
        return InvoiceResult(provider=provider, invoice_id=invoice_id, checkout_url=checkout_url)
