from datetime import datetime

from bot.app.utils.profile import build_profile_text


def test_build_profile_text_contains_fields() -> None:
    text = build_profile_text(
        username="alice",
        telegram_id=1,
        plan_name="3m",
        mode="bridge",
        expires_at=datetime(2026, 5, 1),
        subscription_url="https://sub.example.com/u/1",
        referral_code="abc123",
    )
    assert "Профиль" in text
    assert "Тариф: 3m" in text
    assert "Режим: bridge" in text
    assert "abc123" in text
