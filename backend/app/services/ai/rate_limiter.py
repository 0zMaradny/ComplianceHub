import time
import threading
from collections import defaultdict


PROVIDER_LIMITS = {
    'hf': 10,
    'gemini': 60,
    'openai': 60,
    'claude': 50,
    'local': 30,
}


class ProviderRateLimiter:
    def __init__(self):
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._window_size = 60
        self._lock = threading.Lock()

    def check(self, provider: str) -> bool:
        limit = PROVIDER_LIMITS.get(provider, 30)
        now = time.time()
        with self._lock:
            timestamps = self._windows[provider]
            cutoff = now - self._window_size
            self._windows[provider] = [t for t in timestamps if t > cutoff]
            if len(self._windows[provider]) >= limit:
                return False
            self._windows[provider].append(now)
            return True
