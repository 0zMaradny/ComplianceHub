"""Tests for the AI response cache."""
import time
import pytest
from app.services.ai.caching import ResponseCache


class TestResponseCache:
    def test_set_and_get(self):
        cache = ResponseCache(ttl_seconds=60)
        key = cache.make_key("test prompt", provider="openrouter")
        cache.set(key, "test response")
        assert cache.get(key) == "test response"

    def test_cache_miss(self):
        cache = ResponseCache(ttl_seconds=60)
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        cache = ResponseCache(ttl_seconds=1)
        key = cache.make_key("expiring prompt")
        cache.set(key, "response")
        assert cache.get(key) == "response"
        time.sleep(1.1)
        assert cache.get(key) is None

    def test_lru_eviction(self):
        cache = ResponseCache(ttl_seconds=60, max_size=2)
        k1 = cache.make_key("prompt1")
        k2 = cache.make_key("prompt2")
        k3 = cache.make_key("prompt3")
        cache.set(k1, "r1")
        cache.set(k2, "r2")
        cache.set(k3, "r3")  # Should evict k1
        assert cache.get(k1) is None
        assert cache.get(k2) == "r2"
        assert cache.get(k3) == "r3"

    def test_invalidate(self):
        cache = ResponseCache(ttl_seconds=60)
        key = cache.make_key("test")
        cache.set(key, "response")
        cache.invalidate(key)
        assert cache.get(key) is None

    def test_clear(self):
        cache = ResponseCache(ttl_seconds=60)
        for i in range(5):
            cache.set(cache.make_key(f"prompt{i}"), f"response{i}")
        cache.clear()
        assert cache.size == 0

    def test_hit_rate(self):
        cache = ResponseCache(ttl_seconds=60)
        key = cache.make_key("test")
        cache.set(key, "response")
        cache.get(key)  # hit
        cache.get("miss")  # miss
        assert cache.hit_rate == 0.5

    def test_stats(self):
        cache = ResponseCache(ttl_seconds=60, max_size=100)
        key = cache.make_key("test")
        cache.set(key, "response")
        stats = cache.stats()
        assert stats["size"] == 1
        assert stats["max_size"] == 100
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_deterministic_keys(self):
        cache = ResponseCache()
        k1 = cache.make_key("same prompt", provider="openrouter")
        k2 = cache.make_key("same prompt", provider="openrouter")
        assert k1 == k2

    def test_different_keys_for_different_params(self):
        cache = ResponseCache()
        k1 = cache.make_key("prompt", provider="openrouter")
        k2 = cache.make_key("prompt", provider="groq")
        assert k1 != k2
