from __future__ import annotations

import hashlib
import hmac


def hmac_sha256_hex(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_hmac_sha256_hex(secret: str, payload: bytes, provided_signature: str) -> bool:
    expected = hmac_sha256_hex(secret=secret, payload=payload)
    return hmac.compare_digest(expected, provided_signature)
