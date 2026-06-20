"""Response cache with TTL and LRU eviction.

Caches AI responses to avoid redundant API calls for identical prompts.
Thread-safe with configurable TTL and max size.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class ResponseCache:
    """Thread-safe LRU cache with TTL for AI responses."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self._cache: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def make_key(prompt: str, provider: str = "", **kwargs) -> str:
        """Create a deterministic cache key from prompt + parameters."""
        key_data = f"{provider}:{prompt}:{sorted(kwargs.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    def get(self, key: str) -> str | None:
        """Get cached value if it exists and hasn't expired."""
        with self._lock:
            if key in self._cache:
                ts, value = self._cache[key]
                if time.time() - ts < self._ttl:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return value
                del self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: str) -> None:
        """Set a cache value, evicting oldest if at capacity."""
        with self._lock:
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._cache.popitem(last=False)
            self._cache[key] = (time.time(), value)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0 to 1.0)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        """Current number of cached entries."""
        return len(self._cache)

    def stats(self) -> dict[str, Any]:
        """Cache statistics."""
        return {
            "size": self.size,
            "max_size": self._max_size,
            "ttl_seconds": self._ttl,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate, 3),
        }
