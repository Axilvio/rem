from rembot.telegram_membership import is_allowed_member_status


def test_regular_members_are_allowed() -> None:
    assert is_allowed_member_status("creator")
    assert is_allowed_member_status("administrator")
    assert is_allowed_member_status("member")


def test_restricted_member_is_allowed_only_when_still_member() -> None:
    assert is_allowed_member_status("restricted", True)
    assert not is_allowed_member_status("restricted", False)
    assert not is_allowed_member_status("restricted", None)


def test_left_and_kicked_are_denied() -> None:
    assert not is_allowed_member_status("left")
    assert not is_allowed_member_status("kicked")
    assert not is_allowed_member_status(None)
