def extract_tariff_argument(text: str | None) -> str:
    if not text:
        return "1m"
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return "1m"
    return parts[1].strip() or "1m"
