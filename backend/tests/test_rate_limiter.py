"""Tests for provider rate limiter."""

import time
from app.services.ai.rate_limiter import ProviderRateLimiter


class TestProviderRateLimiter:
    def setup_method(self):
        self.limiter = ProviderRateLimiter()
        self.limiter._windows.clear()

    def test_initial_check_allowed(self):
        assert self.limiter.check('groq') is True

    def test_under_limit_allowed(self):
        for _ in range(5):
            assert self.limiter.check('local_qwen') is True

    def test_unknown_provider_gets_default_limit(self):
        for _ in range(20):
            assert self.limiter.check('unknown_provider') is True
        assert self.limiter.check('unknown_provider') is False

    def test_groq_limit_30(self):
        for _ in range(30):
            assert self.limiter.check('groq') is True
        assert self.limiter.check('groq') is False

    def test_local_limit_5(self):
        for _ in range(5):
            assert self.limiter.check('local') is True
        assert self.limiter.check('local') is False

    def test_openrouter_limit_30(self):
        for _ in range(30):
            assert self.limiter.check('openrouter') is True
        assert self.limiter.check('openrouter') is False

    def test_windows_cleared_after_time(self):
        self.limiter.check('groq')
        self.limiter._windows['groq'] = [time.time() - 120]
        assert self.limiter.check('groq') is True

    def test_thread_safety(self):
        import threading
        errors = []

        def hammer():
            try:
                for _ in range(10):
                    self.limiter.check('groq')
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=hammer) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0
