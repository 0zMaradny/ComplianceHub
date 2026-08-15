import time
import threading
from collections import defaultdict


PROVIDER_LIMITS = {
    'premium_claude': 30,
    'groq': 30,
    'groq_llama': 30,
    'groq_scout': 30,
    'openrouter': 30,

    'nemotron_ultra': 20,
    'nemotron_super': 20,
    'qwen3_coder': 20,
    'qwen3_next': 20,
    'kimi_k3': 20,
    'hermes_405b': 20,
    'owl_alpha': 20,
    'glm_52': 20,
    'minimax_m3': 20,
    'qwen38_max_preview': 20,
    'deepseek_v4_flash': 20,
    'llama_4_scout': 20,
    'glm_5_turbo': 20,
    'longcat_2': 20,
    'local': 5,
    'local_qwen3_4b': 5,
    'local_qwen_3b': 5,
    'local_qwen': 5,
}


class ProviderRateLimiter:
    """Thread-safe sliding window rate limiter.

    NOTE: This is per-process. For multi-worker gunicorn deployments,
    each worker has its own counter. For strict global rate limiting,
    use a shared backend (Redis, memcached, or file-based lock).
    For single-worker deployments (default), this is sufficient.
    """
    def __init__(self):
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._window_size = 60
        self._lock = threading.Lock()

    def check(self, provider: str) -> bool:
        limit = PROVIDER_LIMITS.get(provider, 20)
        now = time.time()
        with self._lock:
            timestamps = self._windows[provider]
            cutoff = now - self._window_size
            self._windows[provider] = [t for t in timestamps if t > cutoff]
            if len(self._windows[provider]) >= limit:
                return False
            self._windows[provider].append(now)
            return True
