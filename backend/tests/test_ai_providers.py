"""Unit tests for AI provider classes.

Tests instantiation, key handling, and error paths without making API calls.
"""

import pytest
from app.services.ai import create_provider, AIProvider


class TestProviderInstantiation:
    def test_openrouter_is_ai_provider(self):
        p = create_provider('openrouter')
        assert isinstance(p, AIProvider)

    def test_openrouter_has_generate(self):
        p = create_provider('openrouter')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_groq_is_ai_provider(self):
        p = create_provider('groq')
        assert isinstance(p, AIProvider)

    def test_groq_has_generate(self):
        p = create_provider('groq')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_owl_alpha_is_ai_provider(self):
        p = create_provider('owl_alpha')
        assert isinstance(p, AIProvider)

    def test_owl_alpha_has_generate(self):
        p = create_provider('owl_alpha')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_local_qwen_is_ai_provider(self):
        p = create_provider('local_qwen')
        assert isinstance(p, AIProvider)

    def test_local_qwen_has_generate(self):
        p = create_provider('local_qwen')
        assert isinstance(p, AIProvider)
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_claude_is_ai_provider(self):
        p = create_provider('claude')
        assert isinstance(p, AIProvider)

    def test_claude_has_generate(self):
        p = create_provider('claude')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_local_qwen3_4b_is_ai_provider(self):
        p = create_provider('local_qwen3_4b')
        assert isinstance(p, AIProvider)

    def test_local_qwen3_4b_has_generate(self):
        p = create_provider('local_qwen3_4b')
        assert hasattr(p, 'generate')
        assert callable(p.generate)


class TestErrorPaths:
    def test_groq_no_key(self):
        from app.services.ai.groq_provider import GroqProvider
        p = GroqProvider()
        p.api_key = ''
        result = p.generate('test prompt')
        assert 'error' in result
        assert 'not set' in result['error'].lower()

    def test_openrouter_no_key(self):
        from app.services.ai.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider()
        p.api_key = ''
        result = p.generate('test prompt')
        assert 'error' in result
        assert 'not set' in result['error'].lower()

    def test_anthropic_no_key(self):
        from app.services.ai.anthropic_provider import AnthropicProvider
        p = AnthropicProvider()
        p.api_key = ''
        result = p.generate('test prompt')
        assert 'error' in result
        assert 'not set' in result['error'].lower()


class TestInitialization:
    def test_groq_reads_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv('GROQ_API_KEY', 'gsk-test-key')
            from app.services.ai.groq_provider import GroqProvider
            p = GroqProvider()
            assert p.api_key == 'gsk-test-key'
            assert p.base_url == 'https://api.groq.com/openai/v1'

    def test_openrouter_reads_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv('OPENROUTER_API_KEY', 'sk-or-test')
            from app.services.ai.openrouter_provider import OpenRouterProvider
            p = OpenRouterProvider()
            assert p.api_key == 'sk-or-test'
            assert p.model == 'openrouter/free'

    def test_anthropic_reads_env(self):
        with pytest.MonkeyPatch.context() as mp:
            mp.setenv('ANTHROPIC_API_KEY', 'sk-ant-test-key')
            from app.services.ai.anthropic_provider import AnthropicProvider
            p = AnthropicProvider()
            assert p.api_key == 'sk-ant-test-key'
            assert p.model == 'claude-sonnet-4-20250514'

    def test_anthropic_init_with_name(self):
        p = create_provider('claude')
        assert isinstance(p, AIProvider)
