def extract_ref_code(text: str | None) -> str | None:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    candidate = parts[1].strip()
    return candidate if candidate else None
