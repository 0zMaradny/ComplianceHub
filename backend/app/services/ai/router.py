import os
import logging
from typing import Any

from . import create_provider
from .debugger import Autodebugger

logger = logging.getLogger(__name__)

# ── Task → ordered provider chain ──────────────────────────────────────────
# First entry is the primary; subsequent entries are fallbacks on failure.
# Provider names must match create_provider() keys: gemini, openai, claude, ollama.

TASK_ROUTING = {
    'extract_shared_context': ['gemini', 'openai', 'claude', 'hf', 'local'],
    'Audit_Plan_Stage_1': ['openai', 'claude', 'gemini', 'hf', 'local'],
    'Audit_Plan_Stage_2': ['openai', 'claude', 'gemini', 'hf', 'local'],
    'Participation_List': ['openai', 'gemini', 'claude', 'hf', 'local'],
    'Audit_Report': ['claude', 'openai', 'gemini', 'hf', 'local'],
    'ISO_Checklist': ['gemini', 'openai', 'claude', 'hf', 'local'],
    'Certificate_Text': ['claude', 'openai', 'gemini', 'hf', 'local'],
    'Certificate': ['claude', 'openai', 'gemini', 'hf', 'local'],
    'TNL': ['openai', 'claude', 'gemini', 'hf', 'local'],
}


def set_api_key(provider_name: str, api_key: str):
    """Set the correct env var for the given provider.
    Only sets if api_key is non-empty (avoids overwriting .env values).
    Validates api_key pattern matches the provider to avoid overwriting
    with garbage like 'hf' or 'gemini' that was meant as override."""
    env_map = {
        'gemini': 'GEMINI_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'claude': 'CLAUDE_API_KEY',
        'hf': 'HF_API_KEY',
    }
    var = env_map.get(provider_name)
    if not var or not api_key:
        return
    # Only set if key looks valid for this provider
    valid_prefixes = {
        'gemini': 'AIza',
        'openai': 'sk-',
        'claude': 'sk-ant-',
        'hf': 'hf_',
    }
    prefix = valid_prefixes.get(provider_name)
    if prefix and not api_key.startswith(prefix):
        return  # Don't overwrite env var with non-matching key
    os.environ[var] = api_key


KEY_PROVIDER_ENV = {
    'hf': 'HF_API_KEY',
}


def resolve_chain(task_type: str, override_provider: str | None = None, api_key: str = '') -> list[str]:
    """Return ordered provider chain for a task type.
    Checks both passed api_key and environment variables for available providers."""
    if override_provider:
        chain = [override_provider]
        fallback_str = os.environ.get('AI_FALLBACK_PROVIDERS', '').strip()
        if fallback_str:
            chain.extend(p.strip() for p in fallback_str.split(',') if p.strip())
        return chain

    if api_key:
        if api_key == 'hf' or api_key.startswith('hf_'):
            chain = ['hf']
        else:
            chain = list(TASK_ROUTING.get(task_type, ['gemini', 'openai']))
    else:
        chain = []

    for provider_name, env_var in KEY_PROVIDER_ENV.items():
        if os.environ.get(env_var, '').strip():
            if provider_name not in chain:
                chain.append(provider_name)

    if 'local' not in chain:
        chain.append('local')

    return chain if chain else ['local']


def _call_with_debugger(task_type: str, provider_name: str, provider_fn, prompt: str,
                        system_prompt: str | None = None, **kwargs) -> tuple[dict, list[str]]:
    """Call a provider wrapped in Autodebugger self-healing."""
    debugger = Autodebugger(task_type)
    result = debugger.call_with_self_heal(
        provider_fn, prompt, system_prompt=system_prompt, **kwargs
    )
    errors = result.pop('_validation_errors', [])
    return result, errors


def generate(task_type: str, prompt: str, system_prompt: str | None = None,
             api_key: str = '', override_provider: str | None = None,
             **kwargs) -> dict[str, Any]:
    """Route a generation task through the best provider chain with fallback
    and autodebugger self-healing on each provider."""
    chain = resolve_chain(task_type, override_provider, api_key)
    last_error = None
    for provider_name in chain:
        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)

            result, validation_errors = _call_with_debugger(
                task_type, provider_name,
                provider.generate, prompt,
                system_prompt=system_prompt, **kwargs
            )
            if 'error' not in result or result['error'] is None:
                if not validation_errors:
                    return result
                last_error = f"Validation failed after self-heal: {'; '.join(validation_errors)}"
            else:
                last_error = result['error']
            logger.warning('Provider %s failed for %s: %s', provider_name, task_type, last_error)
        except Exception as e:
            last_error = str(e)
            logger.warning('Provider %s raised exception for %s: %s', provider_name, task_type, last_error)
    return {'error': f'All providers failed. Last error: {last_error}'}


def extract_structured(task_type: str, prompt: str,
                       api_key: str = '', override_provider: str | None = None,
                       **kwargs) -> dict[str, Any]:
    """Route a structured extraction task through the best provider chain
    with autodebugger self-healing on each provider."""
    chain = resolve_chain(task_type, override_provider, api_key)
    last_error = None
    for provider_name in chain:
        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)

            result, validation_errors = _call_with_debugger(
                task_type, provider_name,
                provider.extract_structured, prompt, **kwargs
            )
            if 'error' not in result or result['error'] is None:
                if not validation_errors:
                    return result
                last_error = f"Validation failed after self-heal: {'; '.join(validation_errors)}"
            else:
                last_error = result['error']
            logger.warning('Provider %s failed extraction for %s: %s', provider_name, task_type, last_error)
        except Exception as e:
            last_error = str(e)
            logger.warning('Provider %s raised exception for extraction %s: %s', provider_name, task_type, last_error)
    return {'error': f'All providers failed. Last error: {last_error}'}
