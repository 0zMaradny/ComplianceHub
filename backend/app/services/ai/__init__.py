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
    }
    mod_path, cls_name = providers.get(name, providers['gemini'])
    import importlib
    mod = importlib.import_module(mod_path, __package__)
    cls = getattr(mod, cls_name)
    inst = cls()
    _PROVIDER_CACHE[name] = inst
    return inst
