import time
import threading
from collections import defaultdict


PROVIDER_LIMITS = {
    'antigravity_claude_sonnet_46': 30,
    'antigravity_claude_opus_46': 30,
    'antigravity_gemini_3_flash': 30,
    'antigravity_gemini_25_flash': 60,
    'antigravity_gemini_25_flash_thinking': 60,
    'antigravity_gemini_25_pro': 30,
    'groq': 30,
    'groq_llama': 30,
    'openrouter': 30,

    'nemotron_ultra': 20,
    'nemotron_super': 20,
    'qwen3_coder': 20,
    'gemma_31b': 20,
    'llama_70b': 20,
    'kimi_k26': 20,
    'hermes_405b': 20,
    'owl_alpha': 20,
    'local': 5,
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
