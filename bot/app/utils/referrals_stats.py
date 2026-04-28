def calculate_bonus_days(invited_total: int, bonus_per_referral: int = 7) -> int:
    if invited_total < 0:
        return 0
    return invited_total * bonus_per_referral
