"""Unit tests for AI provider classes.

Tests instantiation, key handling, and error paths without making API calls.
"""

import pytest
import os
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

    def test_antigravity_claude_sonnet_46_is_provider(self):
        p = create_provider('antigravity_claude_sonnet_46')
        assert isinstance(p, AIProvider)

    def test_antigravity_claude_sonnet_46_has_generate(self):
        p = create_provider('antigravity_claude_sonnet_46')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_antigravity_claude_opus_46_is_provider(self):
        p = create_provider('antigravity_claude_opus_46')
        assert isinstance(p, AIProvider)

    def test_antigravity_claude_opus_46_has_generate(self):
        p = create_provider('antigravity_claude_opus_46')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_antigravity_gemini_3_flash_is_provider(self):
        p = create_provider('antigravity_gemini_3_flash')
        assert isinstance(p, AIProvider)

    def test_antigravity_gemini_3_flash_has_generate(self):
        p = create_provider('antigravity_gemini_3_flash')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_antigravity_gemini_25_flash_is_provider(self):
        p = create_provider('antigravity_gemini_25_flash')
        assert isinstance(p, AIProvider)

    def test_antigravity_gemini_25_flash_has_generate(self):
        p = create_provider('antigravity_gemini_25_flash')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_antigravity_gemini_25_flash_thinking_is_provider(self):
        p = create_provider('antigravity_gemini_25_flash_thinking')
        assert isinstance(p, AIProvider)

    def test_antigravity_gemini_25_flash_thinking_has_generate(self):
        p = create_provider('antigravity_gemini_25_flash_thinking')
        assert hasattr(p, 'generate')
        assert callable(p.generate)

    def test_antigravity_gemini_25_pro_is_provider(self):
        p = create_provider('antigravity_gemini_25_pro')
        assert isinstance(p, AIProvider)

    def test_antigravity_gemini_25_pro_has_generate(self):
        p = create_provider('antigravity_gemini_25_pro')
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

    def test_antigravity_no_tokens(self):
        from app.services.ai.antigravity_provider import AntigravityProvider
        p = AntigravityProvider(provider_name='antigravity_claude_sonnet_46')
        # Empty the tokens list to simulate no config
        p.tokens = []
        result = p.generate('test prompt')
        assert 'error' in result
        assert 'No Antigravity refresh tokens configured' in result['error']


class TestInitialization:
    def test_groq_reads_env(self):
        # Test that provider can be instantiated - actual env reading happens in settings
        from app.services.ai.groq_provider import GroqProvider
        p = GroqProvider()
        assert isinstance(p, AIProvider)
        assert p.model == 'llama-3.3-70b-versatile'
        assert p.base_url == 'https://api.groq.com/openai/v1'

    def test_openrouter_reads_env(self):
        from app.services.ai.openrouter_provider import OpenRouterProvider
        p = OpenRouterProvider()
        assert isinstance(p, AIProvider)
        assert p.model in ('openrouter/free', 'openrouter/auto') or 'nemotron' in p.model or 'qwen' in p.model

    def test_antigravity_init_with_name(self):
        p = create_provider('antigravity_claude_sonnet_46')
        assert isinstance(p, AIProvider)
        assert hasattr(p, 'model_map')
        assert 'antigravity_claude_sonnet_46' in p.model_map