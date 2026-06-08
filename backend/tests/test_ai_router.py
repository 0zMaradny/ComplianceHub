import os
import time
import pytest
from unittest.mock import patch, MagicMock

from app.services.ai.router import (
    _provider_available,
    _cache_key, _check_cache, _set_cache,
    _is_provider_healthy, _mark_provider_success, _mark_provider_failure,
    set_api_key,
    _try_provider, _try_parallel,
    FREE_PARALLEL_PROVIDERS,
    generate, extract_structured,
)


class TestProviderAvailable:
    def test_agentrouter_key_set(self):
        with patch.dict(os.environ, {'AGENTROUTER_API_KEY': 'sk-test123'}):
            assert _provider_available('agentrouter') is True

    def test_agentrouter_key_empty(self):
        with patch.dict(os.environ, {'AGENTROUTER_API_KEY': ''}):
            assert _provider_available('agentrouter') is False

    def test_agentrouter_key_missing(self):
        with patch.dict(os.environ, clear=True):
            assert _provider_available('agentrouter') is False

    def test_groq_key_set(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_test123'}):
            assert _provider_available('groq') is True

    def test_groq_key_empty(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}):
            assert _provider_available('groq') is False

    def test_openrouter_key_set(self):
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'sk-or-test'}):
            assert _provider_available('openrouter') is True

    def test_hf_key_set(self):
        with patch.dict(os.environ, {'HF_API_KEY': 'hf_test'}):
            assert _provider_available('hf') is True

    def test_local_always_available(self):
        assert _provider_available('local') is True

    def test_unknown_provider_available(self):
        assert _provider_available('nonexistent') is True


class TestCache:
    def test_cache_key_consistency(self):
        k1 = _cache_key('doc', 'hello world')
        k2 = _cache_key('doc', 'hello world')
        assert k1 == k2
        assert len(k1) == 32

    def test_cache_key_different_task(self):
        k1 = _cache_key('doc_a', 'hello')
        k2 = _cache_key('doc_b', 'hello')
        assert k1 != k2

    def test_set_and_get(self):
        key = _cache_key('test', 'cache me')
        result = {'data': 'cached'}
        _set_cache(key, result)
        cached = _check_cache(key)
        assert cached == result

    def test_cache_miss(self):
        result = _check_cache('nonexistent')
        assert result is None

    def test_cache_expiry(self):
        key = _cache_key('test', 'expire_me')
        _set_cache(key, {'data': 'fresh'})
        with patch('time.time', return_value=time.time() + 7200):
            cached = _check_cache(key)
            assert cached is None

    def test_cache_miss_after_delete(self):
        key = _cache_key('test', 'delete_me')
        _set_cache(key, {'data': 'temp'})
        _check_cache(key)
        _check_cache(key)


class TestHealthTracking:
    def test_initial_healthy(self):
        assert _is_provider_healthy('test_provider') is True

    def test_mark_failure_degrades(self):
        _mark_provider_failure('degrading')
        assert _is_provider_healthy('degrading') is True
        _mark_provider_failure('degrading')
        assert _is_provider_healthy('degrading') is True

    def test_three_fails_degrades(self):
        for _ in range(4):
            _mark_provider_failure('failing')
        assert _is_provider_healthy('failing') is False

    def test_success_resets(self):
        for _ in range(4):
            _mark_provider_failure('recovering')
        _mark_provider_success('recovering')
        assert _is_provider_healthy('recovering') is True


class TestSetApiKey:
    def test_agentrouter_valid(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('agentrouter', 'sk-valid123')
            assert os.environ.get('AGENTROUTER_API_KEY') == 'sk-valid123'

    def test_agentrouter_invalid_prefix(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('agentrouter', 'invalid_prefix')
            assert 'AGENTROUTER_API_KEY' not in os.environ

    def test_groq_valid(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('groq', 'gsk_valid456')
            assert os.environ.get('GROQ_API_KEY') == 'gsk_valid456'

    def test_groq_invalid_prefix(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('groq', 'invalid_prefix')
            assert 'GROQ_API_KEY' not in os.environ

    def test_openrouter_valid(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('openrouter', 'sk-or-v1-test789')
            assert os.environ.get('OPENROUTER_API_KEY') == 'sk-or-v1-test789'

    def test_openrouter_invalid_prefix(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('openrouter', 'bad_prefix')
            assert 'OPENROUTER_API_KEY' not in os.environ

    def test_empty_api_key_does_nothing(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('agentrouter', '')
            assert 'AGENTROUTER_API_KEY' not in os.environ

    def test_unknown_provider_does_nothing(self):
        set_api_key('unknown', 'some_key')
        for k in os.environ:
            assert k not in ('UNKNOWN_API_KEY',)


class TestTryProvider:
    def test_provider_rate_limited(self):
        with patch('app.services.ai.router._rate_limiter') as mock_rl:
            mock_rl.check.return_value = False
            result, err = _try_provider('groq', 'test', 'prompt')
            assert result is None
            assert 'rate limit' in err.lower()

    def test_provider_degraded(self):
        _mark_provider_failure('degraded_provider')
        _mark_provider_failure('degraded_provider')
        _mark_provider_failure('degraded_provider')
        _mark_provider_failure('degraded_provider')
        with patch('app.services.ai.router._rate_limiter') as mock_rl:
            mock_rl.check.return_value = True
            result, err = _try_provider('degraded_provider', 'test', 'prompt')
            assert result is None
            assert 'degraded' in err.lower()

    def test_provider_raises_exception(self):
        with patch('app.services.ai.router.create_provider') as mock_cp:
            mock_cp.side_effect = RuntimeError('mock failure')
            with patch('app.services.ai.router._rate_limiter') as mock_rl:
                mock_rl.check.return_value = True
                result, err = _try_provider('groq', 'test', 'prompt')
                assert result is None
                assert err is not None


class TestTryParallel:
    def test_no_available_providers(self):
        with patch('app.services.ai.router._provider_available', return_value=False):
            result, err = _try_parallel(['groq', 'openrouter'], 'test', 'prompt')
            assert result is None
            assert 'No parallel providers' in err

    def test_all_providers_fail(self):
        with patch('app.services.ai.router._provider_available', return_value=True):
            with patch('app.services.ai.router._try_provider', return_value=(None, 'fail')):
                result, err = _try_parallel(['groq'], 'test', 'prompt')
                assert result is None
                assert 'All parallel' in err


class TestGenerate:
    def test_cache_hit(self):
        with patch('app.services.ai.router._check_cache') as mock_cc:
            mock_cc.return_value = {'cached': True}
            result = generate('test', 'prompt')
            assert result == {'cached': True}

    def test_override_provider_sequential(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._try_provider', return_value=({'ok': True}, None)):
                result = generate('test', 'prompt', override_provider='groq')
                assert result == {'ok': True}

    def test_override_provider_all_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._try_provider', return_value=(None, 'failed')):
                result = generate('test', 'prompt', override_provider='groq')
                assert 'error' in result

    def test_tier1_agentrouter_success(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_available', return_value=True):
                with patch('app.services.ai.router._try_provider', return_value=({'ok': 'ar'}, None)):
                    result = generate('test', 'prompt')
                    assert result == {'ok': 'ar'}

    def test_falls_through_to_local(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_available', return_value=False):
                with patch('app.services.ai.router._try_parallel', return_value=(None, 'fail')):
                    with patch('app.services.ai.router._try_provider', return_value=({'ok': 'local'}, None)):
                        result = generate('test', 'prompt')
                        assert result == {'ok': 'local'}

    def test_all_tiers_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_available', return_value=False):
                with patch('app.services.ai.router._try_parallel', return_value=(None, 'fail')):
                    with patch('app.services.ai.router._try_provider', return_value=(None, 'fail')):
                        result = generate('test', 'prompt')
                        assert result == {'error': 'All providers failed.'}


class TestExtractStructured:
    def test_cache_hit(self):
        with patch('app.services.ai.router._check_cache') as mock_cc:
            mock_cc.return_value = {'cached': True}
            result = extract_structured('test', 'prompt')
            assert result == {'cached': True}

    def test_override_provider(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._try_provider', return_value=({'ok': True}, None)):
                result = extract_structured('test', 'prompt', override_provider='groq')
                assert result == {'ok': True}

    def test_all_tiers_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_available', return_value=False):
                with patch('app.services.ai.router._try_parallel', return_value=(None, 'fail')):
                    with patch('app.services.ai.router._try_provider', return_value=(None, 'fail')):
                        result = extract_structured('test', 'prompt')
                        assert result == {'error': 'All providers failed.'}
