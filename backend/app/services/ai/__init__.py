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

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        """Stream tokens from the provider. Yields str tokens.
        
        Default implementation returns a single token (the full response).
        Override in subclasses that support streaming.
        """
        result = self.generate(prompt, system_prompt=system_prompt, **kwargs)
        if 'error' in result:
            yield result['error']
            return
        text = result.get('text', result.get('response', str(result)))
        yield text


_PROVIDER_CACHE: dict[str, AIProvider] = {}


def create_provider(provider_name: str | None = None) -> AIProvider:
    """Factory: create AI provider by name (reads AI_PROVIDER env if None)."""
    name = (provider_name or os.environ.get('AI_PROVIDER', 'openrouter')).lower().strip()
    cached = _PROVIDER_CACHE.get(name)
    if cached is not None:
        return cached

    providers = {
        'groq': ('.groq_provider', 'GroqProvider'),
        'groq_llama': ('.groq_provider', 'GroqProvider'),
        'openrouter': ('.openrouter_provider', 'OpenRouterProvider'),
        'nemotron_ultra': ('.openrouter_provider', 'OpenRouterProvider'),
        'nemotron_super': ('.openrouter_provider', 'OpenRouterProvider'),
        'qwen3_coder': ('.openrouter_provider', 'OpenRouterProvider'),
        'gemma_31b': ('.openrouter_provider', 'OpenRouterProvider'),
        'llama_70b': ('.openrouter_provider', 'OpenRouterProvider'),
        'kimi_k26': ('.openrouter_provider', 'OpenRouterProvider'),
        'hermes_405b': ('.openrouter_provider', 'OpenRouterProvider'),
        'owl_alpha': ('.openrouter_provider', 'OpenRouterProvider'),
        'local': ('.local_provider', 'LocalProvider'),
        'local_qwen': ('.local_provider', 'LocalProvider'),
    }
    mod_path, cls_name = providers.get(name, providers['openrouter'])
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
