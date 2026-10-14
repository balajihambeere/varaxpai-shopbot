# src/ratelimit.py
# REQ-N-010. Book is silent on rate limiting (ENGINEERING REQUIREMENT).
# Simple fixed-window-per-minute counter, in-memory — appropriate for the
# framework's stated scale target (<100 concurrent users, single
# process); a distributed limiter (Redis, etc.) would be over-engineering
# at this scale (framework §1.5).
import time
from collections import defaultdict, deque

from src import config


class RateLimiter:
    def __init__(self, limit_per_minute: int):
        self.limit = limit_per_minute
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, client_key: str) -> bool:
        now = time.monotonic()
        window_start = now - 60
        hits = self._hits[client_key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= self.limit:
            return False
        hits.append(now)
        return True


rate_limiter = RateLimiter(config.RATE_LIMIT_PER_MINUTE)
