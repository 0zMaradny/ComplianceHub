import os
from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        pass

    @abstractmethod
    def extract_structured(self, prompt: str, response_mime_type: str | None = None) -> dict[str, Any]:
        pass


_PROVIDER_CACHE: dict[str, AIProvider] = {}


def create_provider(provider_name: str | None = None) -> AIProvider:
    """Factory: create AI provider by name (reads AI_PROVIDER env if None)."""
    name = (provider_name or os.environ.get('AI_PROVIDER', 'gemini')).lower().strip()
    cached = _PROVIDER_CACHE.get(name)
    if cached is not None:
        return cached

    providers = {
        'gemini': ('.gemini_provider', 'GeminiProvider'),
        'openai': ('.openai_provider', 'OpenAIProvider'),
        'claude': ('.claude_provider', 'ClaudeProvider'),
        'hf': ('.hf_provider', 'HFProvider'),
        'local': ('.local_provider', 'LocalProvider'),
        'agentrouter': ('.agentrouter_provider', 'AgentRouterProvider'),
        'groq': ('.groq_provider', 'GroqProvider'),
        'ollama': ('.ollama_provider', 'OllamaProvider'),
        # OpenRouter models — all route through openrouter_provider.py
        'openrouter': ('.openrouter_provider', 'OpenRouterProvider'),
        'fusion': ('.openrouter_provider', 'OpenRouterProvider'),
        'auto': ('.openrouter_provider', 'OpenRouterProvider'),
        'nemotron_ultra': ('.openrouter_provider', 'OpenRouterProvider'),
        'nemotron_super': ('.openrouter_provider', 'OpenRouterProvider'),
        'qwen3_coder': ('.openrouter_provider', 'OpenRouterProvider'),
        'qwen3_next': ('.openrouter_provider', 'OpenRouterProvider'),
        'llama_70b': ('.openrouter_provider', 'OpenRouterProvider'),
        'gpt_oss_120b': ('.openrouter_provider', 'OpenRouterProvider'),
        'gpt_oss_20b': ('.openrouter_provider', 'OpenRouterProvider'),
        'kimi_k26': ('.openrouter_provider', 'OpenRouterProvider'),
        'glm_45': ('.openrouter_provider', 'OpenRouterProvider'),
        'hermes_405b': ('.openrouter_provider', 'OpenRouterProvider'),
    }
    mod_path, cls_name = providers.get(name, providers['gemini'])
    import importlib
    mod = importlib.import_module(mod_path, __package__)
    cls = getattr(mod, cls_name)
    # OpenRouter provider needs the provider_name to select the right model
    if cls_name == 'OpenRouterProvider':
        inst = cls(provider_name=name)
    else:
        inst = cls()
    _PROVIDER_CACHE[name] = inst
    return inst
