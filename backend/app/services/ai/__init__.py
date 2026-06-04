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


def create_provider(provider_name: str | None = None) -> AIProvider:
    """Factory: create AI provider by name (reads AI_PROVIDER env if None)."""
    name = (provider_name or os.environ.get('AI_PROVIDER', 'gemini')).lower().strip()

    if name == 'openai':
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif name == 'ollama':
        from .ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        from .gemini_provider import GeminiProvider
        return GeminiProvider()
