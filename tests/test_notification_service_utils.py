from bot.app.utils.notification import build_expiry_event_key


def test_build_expiry_event_key() -> None:
    key = build_expiry_event_key(telegram_id=10, hours=24, expires_at_iso="2026-05-01T00:00:00+00:00")
    assert key == "expiry:10:24:2026-05-01T00:00:00+00:00"
