def extract_mode_argument(text: str | None) -> str | None:
    if text is None:
        return None
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    arg = parts[1].strip().lower()
    return arg or None
