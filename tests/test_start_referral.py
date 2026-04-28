from bot.app.utils.referral import extract_ref_code


def test_extract_ref_code() -> None:
    assert extract_ref_code('/start abc123') == 'abc123'
    assert extract_ref_code('/start') is None
    assert extract_ref_code(None) is None
