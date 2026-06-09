import time
import threading
from collections import defaultdict


PROVIDER_LIMITS = {
    # Legacy providers
    'hf': 10,
    'gemini': 60,
    'openai': 60,
    'claude': 50,
    'ollama': 30,
    'groq': 30,
    'openrouter': 30,
    'agentrouter': 60,
    # Local
    'local': 30,
    # OpenRouter models (shared rate limit pool)
    'fusion': 20,
    'auto': 20,
    'nemotron_ultra': 20,
    'nemotron_super': 20,
    'qwen3_coder': 20,
    'gemma_31b': 20,
    'llama_70b': 20,
    'gpt_oss_120b': 20,
    'kimi_k26': 20,
}


class ProviderRateLimiter:
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
