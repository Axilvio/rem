from bot.app.utils.subscription import months_to_days


def test_months_to_days_minimum() -> None:
    assert months_to_days(0) == 30


def test_months_to_days_scaling() -> None:
    assert months_to_days(3) == 90
