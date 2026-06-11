"""Tests for AI router — quality-aware multi-provider orchestration."""

import os
import time
from unittest.mock import patch, MagicMock

import pytest

from app.services.ai.router import (
    resolve_chain, set_api_key,
    _rate_limiter, _provider_health, _response_cache,
    _is_provider_healthy, _mark_provider_success, _mark_provider_failure,
    _check_cache, _set_cache, _cache_key,
    _provider_has_key, _get_model_id,
    generate, extract_structured,
)
from app.services.ai.model_registry import (
    ALL_MODELS, FRONTIER_NAMES, STRONG_NAMES, get_tier_models,
    FIELD_MIN_LENGTHS, FIELD_MIN_ITEMS,
)


# ═══════════════════════════════════════════════════════════════════════════
# Model Registry Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestModelRegistry:
    """Test model capability registry."""

    def test_all_models_registered(self):
        expected = [
            'nemotron_ultra', 'qwen3_coder', 'kimi_k26', 'owl_alpha',
            'nemotron_super', 'llama_70b', 'qwen3_next', 'hermes_405b',
            'groq_llama', 'local_qwen',
            'fusion', 'auto',
        ]
        for name in expected:
            assert name in ALL_MODELS, f"Model '{name}' not in registry"
        removed = ['gpt_oss_120b', 'glm_45', 'gpt_oss_20b',
                    'hf', 'openai', 'claude', 'gemini', 'ollama']
        for name in removed:
            assert name not in ALL_MODELS, f"Model '{name}' should have been removed"

    def test_frontier_models_have_large_context(self):
        for m in get_tier_models('frontier_free'):
            assert m.context_length >= 200_000

    def test_frontier_models_have_strengths(self):
        for m in get_tier_models('frontier_free'):
            assert len(m.strengths) > 0

    def test_get_task_chain_starts_with_frontier(self):
        assert FRONTIER_NAMES[0] in ALL_MODELS
        assert ALL_MODELS[FRONTIER_NAMES[0]].tier == 'frontier_free'

    def test_field_min_lengths_defined(self):
        for doc_type in ('Audit_Report', 'ISO_Checklist', 'TNL',
                         'Audit_Plan_Stage_1', 'Audit_Plan_Stage_2'):
            assert doc_type in FIELD_MIN_LENGTHS

    def test_field_min_items_defined(self):
        for doc_type in ('Audit_Report', 'ISO_Checklist', 'TNL',
                         'Audit_Plan_Stage_1', 'Audit_Plan_Stage_2',
                         'Participation_List'):
            assert doc_type in FIELD_MIN_ITEMS



# ═══════════════════════════════════════════════════════════════════════════
# Router Chain Resolution Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestResolveChain:
    """Test provider chain resolution."""

    def test_default_chain_structure(self):
        chain = resolve_chain('Audit_Report')
        assert len(chain) == 10
        for name in chain:
            assert name in ALL_MODELS

    def test_chain_has_local_last(self):
        chain = resolve_chain('Audit_Report')
        assert 'groq_llama' in chain
        assert 'local_qwen' in chain
        assert chain[-1] == 'local_qwen'

    def test_all_task_types_resolved(self):
        task_types = [
            'extract_shared_context',
            'Audit_Plan_Stage_1', 'Audit_Plan_Stage_2',
            'Participation_List', 'Audit_Report',
            'ISO_Checklist', 'Certificate_Text',
            'Certificate', 'TNL',
        ]
        for task_type in task_types:
            chain = resolve_chain(task_type)
            assert len(chain) > 0, f"Empty chain for task: {task_type}"

    def test_unknown_task_gets_default_chain(self):
        chain = resolve_chain('Unknown_Task')
        assert len(chain) == 10

    def test_override_provider(self):
        chain = resolve_chain('Audit_Report', override_provider='kimi_k26')
        assert chain[0] == 'kimi_k26'


# ═══════════════════════════════════════════════════════════════════════════
# Provider Key Detection Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestProviderHasKey:
    """Test _provider_has_key for all provider types."""

    def test_openrouter_key_set(self):
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'sk-or-test'}):
            assert _provider_has_key('openrouter') is True
            # All OpenRouter free models use the same key
            assert _provider_has_key('nemotron_ultra') is True
            assert _provider_has_key('qwen3_coder') is True
            assert _provider_has_key('llama_70b') is True

    def test_openrouter_key_empty(self):
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': ''}):
            assert _provider_has_key('nemotron_ultra') is False

    def test_groq_key_set(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_test123'}):
            assert _provider_has_key('groq') is True


# ═══════════════════════════════════════════════════════════════════════════
# Model ID Resolution Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestGetModelId:
    """Test _get_model_id resolves correct OpenRouter model IDs."""

    def test_nemotron_ultra(self):
        mid = _get_model_id('nemotron_ultra')
        assert 'nemotron-3-ultra' in mid

    def test_qwen3_coder(self):
        mid = _get_model_id('qwen3_coder')
        assert 'qwen3-coder' in mid

    def test_llama_70b(self):
        mid = _get_model_id('llama_70b')
        assert 'llama-3.3-70b' in mid

    def test_kimi_k26(self):
        mid = _get_model_id('kimi_k26')
        assert 'kimi-k2.6' in mid

    def test_hermes_405b(self):
        mid = _get_model_id('hermes_405b')
        assert '405b' in mid

    def test_unknown_falls_back_to_auto(self):
        mid = _get_model_id('nonexistent')
        assert mid == 'openrouter/auto'


# ═══════════════════════════════════════════════════════════════════════════
# API Key Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSetApiKey:
    """Test API key → env var mapping."""

    def test_openrouter_models_set_openrouter_key(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('nemotron_ultra', 'sk-or-test')
            assert os.environ.get('OPENROUTER_API_KEY') == 'sk-or-test'

    def test_openrouter_named_provider_sets_key(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('openrouter', 'sk-or-test')
            assert os.environ.get('OPENROUTER_API_KEY') == 'sk-or-test'

    def test_groq_key(self):
        with patch.dict(os.environ, {}, clear=True):
            set_api_key('groq', 'gsk_test')
            assert os.environ.get('GROQ_API_KEY') == 'gsk_test'

    def test_empty_key_does_nothing(self):
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'existing'}):
            set_api_key('openrouter', '')
            assert os.environ.get('OPENROUTER_API_KEY') == 'existing'


# ═══════════════════════════════════════════════════════════════════════════
# Provider Health Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestProviderHealth:
    def setup_method(self):
        _provider_health.clear()

    def test_initial_healthy(self):
        assert _is_provider_healthy('nemotron_ultra') is True

    def test_degraded_after_threshold(self):
        for _ in range(3):
            _mark_provider_failure('nemotron_ultra')
        assert _is_provider_healthy('nemotron_ultra') is False

    def test_success_resets(self):
        _mark_provider_failure('nemotron_ultra')
        _mark_provider_failure('nemotron_ultra')
        _mark_provider_success('nemotron_ultra')
        assert _is_provider_healthy('nemotron_ultra') is True


# ═══════════════════════════════════════════════════════════════════════════
# Cache Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCache:
    def setup_method(self):
        _response_cache.clear()

    def test_cache_miss(self):
        assert _check_cache('nonexistent') is None

    def test_cache_hit(self):
        _set_cache('test-key', {'result': 'ok'})
        hit = _check_cache('test-key')
        assert hit is not None
        assert hit['result'] == 'ok'

    def test_cache_expiry(self):
        _set_cache('expiring', {'data': 1})
        with patch('time.time', return_value=time.time() + 4000):
            assert _check_cache('expiring') is None

    def test_cache_key_deterministic(self):
        k1 = _cache_key('task', 'prompt')
        k2 = _cache_key('task', 'prompt')
        assert k1 == k2

    def test_cache_key_unique(self):
        k1 = _cache_key('task1', 'prompt')
        k2 = _cache_key('task2', 'prompt')
        assert k1 != k2


# ═══════════════════════════════════════════════════════════════════════════
# Rate Limiter Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRateLimiter:
    def setup_method(self):
        _rate_limiter._windows.clear()

    def test_nemotron_ultra_allowed(self):
        assert _rate_limiter.check('nemotron_ultra') is True

    def test_qwen3_coder_allowed(self):
        assert _rate_limiter.check('qwen3_coder') is True

    def test_llama_70b_allowed(self):
        assert _rate_limiter.check('llama_70b') is True

    def test_nemotron_super_allowed(self):
        assert _rate_limiter.check('nemotron_super') is True

    def test_hermes_405b_allowed(self):
        assert _rate_limiter.check('hermes_405b') is True


# ═══════════════════════════════════════════════════════════════════════════
# Generate / Extract Integration Tests (mocked)
# ═══════════════════════════════════════════════════════════════════════════

class TestGenerate:
    def test_cache_hit(self):
        with patch('app.services.ai.router._check_cache', return_value={'cached': True}):
            result = generate('test', 'prompt')
            assert result == {'cached': True}

    def test_override_provider(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_has_key', return_value=True):
                with patch('app.services.ai.router._try_provider', return_value=({'ok': True}, None)):
                    result = generate('test', 'prompt', override_provider='nemotron_ultra')
                    assert result == {'ok': True}

    def test_override_all_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_has_key', return_value=True):
                with patch('app.services.ai.router._try_provider', return_value=(None, 'failed')):
                    result = generate('test', 'prompt', override_provider='nemotron_ultra')
                    assert 'error' in result

    def test_all_tiers_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_has_key', return_value=False):
                result = generate('test', 'prompt')
                assert 'error' in result


class TestExtractStructured:
    def test_cache_hit(self):
        with patch('app.services.ai.router._check_cache', return_value={'cached': True}):
            result = extract_structured('test', 'prompt')
            assert result == {'cached': True}

    def test_override_provider(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_has_key', return_value=True):
                with patch('app.services.ai.router._try_provider', return_value=({'ok': True}, None)):
                    result = extract_structured('test', 'prompt', override_provider='nemotron_ultra')
                    assert result == {'ok': True}

    def test_all_tiers_fail(self):
        with patch('app.services.ai.router._check_cache', return_value=None):
            with patch('app.services.ai.router._provider_has_key', return_value=False):
                result = extract_structured('test', 'prompt')
                assert 'error' in result
