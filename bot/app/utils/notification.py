def build_expiry_event_key(telegram_id: int, hours: int, expires_at_iso: str) -> str:
    return f"expiry:{telegram_id}:{hours}:{expires_at_iso}"
