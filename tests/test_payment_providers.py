from types import SimpleNamespace

from bot.app.services.payment_providers import PaymentProviderVerifier
from bot.app.utils.security import hmac_sha256_hex


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        bot_webhook_secret="s",
        cryptomus_webhook_secret="s",
        cryptocloud_api_key="cc",
        oxapay_api_key="ox",
    )


def test_cryptomus_verify_ok() -> None:
    payload = b"abc"
    verifier = PaymentProviderVerifier(_settings())
    signature = hmac_sha256_hex("s", payload)
    result = verifier.verify("cryptomus", payload, signature)
    assert result.valid


def test_unsupported_provider() -> None:
    verifier = PaymentProviderVerifier(_settings())
    result = verifier.verify("unknown", b"abc", "x")
    assert not result.valid
