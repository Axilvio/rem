from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from bot.app.utils.security import verify_hmac_sha256_hex


class ProviderSettings(Protocol):
    bot_webhook_secret: str
    cryptomus_webhook_secret: str
    cryptocloud_api_key: str
    oxapay_api_key: str


@dataclass(slots=True)
class ProviderVerificationResult:
    valid: bool
    reason: str


class PaymentProviderVerifier:
    def __init__(self, settings: ProviderSettings) -> None:
        self._settings = settings

    def verify(self, provider: str, payload_raw: bytes, signature: str) -> ProviderVerificationResult:
        normalized = provider.lower().strip()
        if normalized == "cryptomus":
            secret = self._settings.cryptomus_webhook_secret or self._settings.bot_webhook_secret
            ok = verify_hmac_sha256_hex(secret, payload_raw, signature)
            return ProviderVerificationResult(valid=ok, reason="ok" if ok else "invalid cryptomus signature")

        if normalized == "cryptocloud":
            secret = self._settings.cryptocloud_api_key
            ok = bool(secret) and verify_hmac_sha256_hex(secret, payload_raw, signature)
            return ProviderVerificationResult(valid=ok, reason="ok" if ok else "invalid cryptocloud signature")

        if normalized == "oxapay":
            secret = self._settings.oxapay_api_key
            ok = bool(secret) and verify_hmac_sha256_hex(secret, payload_raw, signature)
            return ProviderVerificationResult(valid=ok, reason="ok" if ok else "invalid oxapay signature")

        return ProviderVerificationResult(valid=False, reason="unsupported provider")
