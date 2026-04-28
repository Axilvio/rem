from bot.app.utils.referrals_stats import calculate_bonus_days


def test_calculate_bonus_days() -> None:
    assert calculate_bonus_days(3) == 21
    assert calculate_bonus_days(-1) == 0
