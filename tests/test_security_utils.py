from bot.app.utils.security import hmac_sha256_hex, verify_hmac_sha256_hex


def test_hmac_roundtrip() -> None:
    payload = b'{"hello":"world"}'
    signature = hmac_sha256_hex("secret", payload)
    assert verify_hmac_sha256_hex("secret", payload, signature)


def test_hmac_invalid() -> None:
    payload = b"abc"
    assert not verify_hmac_sha256_hex("secret", payload, "wrong")
