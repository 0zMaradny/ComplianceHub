import os
import logging
from typing import Any

from . import create_provider

logger = logging.getLogger(__name__)

# ── Task → ordered provider chain ──────────────────────────────────────────
# First entry is the primary; subsequent entries are fallbacks on failure.
# Provider names must match create_provider() keys: gemini, openai, claude, ollama.

TASK_ROUTING = {
    'extract_shared_context': ['gemini', 'openai', 'claude', 'ollama'],
    'Audit_Plan_Stage_1': ['openai', 'claude', 'gemini', 'ollama'],
    'Audit_Plan_Stage_2': ['openai', 'claude', 'gemini', 'ollama'],
    'Participation_List': ['openai', 'gemini', 'claude', 'ollama'],
    'Audit_Report': ['claude', 'openai', 'gemini', 'ollama'],
    'ISO_Checklist': ['gemini', 'openai', 'claude', 'ollama'],
    'Certificate_Text': ['claude', 'openai', 'gemini', 'ollama'],
    'Certificate': ['claude', 'openai', 'gemini', 'ollama'],
    'TNL': ['openai', 'claude', 'gemini', 'ollama'],
}


def set_api_key(provider_name: str, api_key: str):
    """Set the correct env var for the given provider."""
    env_map = {
        'gemini': 'GEMINI_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'claude': 'CLAUDE_API_KEY',
    }
    var = env_map.get(provider_name)
    if var:
        os.environ[var] = api_key


def resolve_chain(task_type: str, override_provider: str | None = None) -> list[str]:
    """Return ordered provider chain for a task type."""
    if override_provider:
        chain = [override_provider]
        fallback_str = os.environ.get('AI_FALLBACK_PROVIDERS', '').strip()
        if fallback_str:
            chain.extend(p.strip() for p in fallback_str.split(',') if p.strip())
        return chain
    return TASK_ROUTING.get(task_type, ['gemini', 'openai'])


def generate(task_type: str, prompt: str, system_prompt: str | None = None,
             api_key: str = '', override_provider: str | None = None,
             **kwargs) -> dict[str, Any]:
    """Route a generation task through the best provider chain with fallback."""
    chain = resolve_chain(task_type, override_provider)
    last_error = None
    for provider_name in chain:
        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)
            result = provider.generate(prompt, system_prompt=system_prompt, **kwargs)
            if 'error' not in result or result['error'] is None:
                return result
            last_error = result['error']
            logger.warning('Provider %s failed for %s: %s', provider_name, task_type, last_error)
        except Exception as e:
            last_error = str(e)
            logger.warning('Provider %s raised exception for %s: %s', provider_name, task_type, last_error)
    return {'error': f'All providers failed. Last error: {last_error}'}


def extract_structured(task_type: str, prompt: str,
                       api_key: str = '', override_provider: str | None = None,
                       **kwargs) -> dict[str, Any]:
    """Route a structured extraction task through the best provider chain."""
    chain = resolve_chain(task_type, override_provider)
    last_error = None
    for provider_name in chain:
        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)
            result = provider.extract_structured(prompt, **kwargs)
            if 'error' not in result or result['error'] is None:
                return result
            last_error = result['error']
            logger.warning('Provider %s failed extraction for %s: %s', provider_name, task_type, last_error)
        except Exception as e:
            last_error = str(e)
            logger.warning('Provider %s raised exception for extraction %s: %s', provider_name, task_type, last_error)
    return {'error': f'All providers failed. Last error: {last_error}'}
