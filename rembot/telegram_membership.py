ALLOWED_MEMBER_STATUSES: set[str] = {"creator", "administrator", "member"}


def is_allowed_member_status(status: str | None, is_member: bool | None = None) -> bool:
    if status in ALLOWED_MEMBER_STATUSES:
        return True
    if status == "restricted":
        return bool(is_member)
    return False
