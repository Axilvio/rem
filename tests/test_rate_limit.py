from bot.app.utils.rate_limit import SlidingWindowRateLimiter


def test_rate_limit_blocks_after_threshold() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=30)
    assert limiter.allow("1.1.1.1")
    assert limiter.allow("1.1.1.1")
    assert not limiter.allow("1.1.1.1")
