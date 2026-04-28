from types import SimpleNamespace

from bot.app.services.invoice_service import InvoiceService


def test_invoice_generation_is_deterministic() -> None:
    settings = SimpleNamespace(payment_provider="cryptomus")
    service = InvoiceService(settings)
    req = SimpleNamespace(telegram_id=1, tariff_name="1m", amount_usd="8.00", currency="USDT")
    first = service.create_invoice(req)
    second = service.create_invoice(req)
    assert first.invoice_id == second.invoice_id
    assert first.checkout_url.startswith("https://pay.example/cryptomus/")
