from datetime import datetime


def build_profile_text(
    username: str | None,
    telegram_id: int,
    plan_name: str,
    mode: str,
    expires_at: datetime | None,
    subscription_url: str | None,
    referral_code: str,
) -> str:
    return (
        f"Профиль @{username or telegram_id}\n"
        f"Тариф: {plan_name}\n"
        f"Режим: {mode}\n"
        f"Действует до: {expires_at}\n"
        f"Ссылка: {subscription_url}\n"
        f"Реферальный код: {referral_code}"
    )
