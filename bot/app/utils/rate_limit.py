from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self._window_seconds
        queue = self._events[key]
        while queue and queue[0] < window_start:
            queue.popleft()
        if len(queue) >= self._max_requests:
            return False
        queue.append(now)
        return True
