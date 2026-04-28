from bot.app.utils.mode import extract_mode_argument


def test_extract_mode_argument() -> None:
    assert extract_mode_argument('/mode bridge') == 'bridge'
    assert extract_mode_argument('/mode') is None
    assert extract_mode_argument(None) is None
