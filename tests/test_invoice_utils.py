from bot.app.utils.invoice import extract_tariff_argument


def test_extract_tariff_argument() -> None:
    assert extract_tariff_argument('/invoice 3m') == '3m'
    assert extract_tariff_argument('/invoice') == '1m'
    assert extract_tariff_argument(None) == '1m'
