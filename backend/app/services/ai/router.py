import os
import time
import hashlib
import logging
from typing import Any

from . import create_provider
from .debugger import Autodebugger
from .rate_limiter import ProviderRateLimiter

logger = logging.getLogger(__name__)

# ── Rate limiter (per-provider sliding window) ─────────────────────────────
_rate_limiter = ProviderRateLimiter()

# ── Provider health tracking (skip after 3 consecutive fails) ──────────────
_provider_health: dict[str, int] = {}
_PROVIDER_DEGRADE_THRESHOLD = 3

# ── Response cache (md5 hash, 1h TTL) ──────────────────────────────────────
_response_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 3600


# ── Task → ordered provider chain ──────────────────────────────────────────
# First entry is the primary; subsequent entries are fallbacks on failure.
# Provider names must match create_provider() keys: gemini, openai, claude, ollama.

TASK_ROUTING = {
    'extract_shared_context': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'Audit_Plan_Stage_1': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'Audit_Plan_Stage_2': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'Participation_List': ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    'Audit_Report': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'ISO_Checklist': ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    'Certificate_Text': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'Certificate': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
    'TNL': ['fusion', 'openai', 'gpt_oss_120b', 'local'],
}

# ── Client-Specific Provider Overrides ──────────────────────────────────────
# Override the default chain for specific client + doc_type combinations.
# Key: (client_key, doc_type) -> provider chain

CLIENT_ROUTING = {
    # MSD-MOI: Arabic BCM content — GPT-OSS handles structured output well
    ('msd_moi', 'Audit_Report'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    ('msd_moi', 'Certificate_Text'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    ('msd_moi', 'TNL'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    # UACC: English EnMS — Fusion for technical content
    ('uacc', 'ISO_Checklist'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    ('uacc', 'Audit_Plan_Stage_1'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    # SAGCO: IMS dual-standard — Fusion for complex integrated content
    ('sagco', 'Audit_Report'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    ('sagco', 'Certificate_Text'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    # Al-Ahsa: Arabic ISMS — Fusion for Arabic ISMS content
    ('al_ahsa', 'Audit_Report'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
    ('al_ahsa', 'Certificate_Text'): ['fusion', 'gpt_oss_120b', 'openai', 'local'],
}


def set_api_key(provider_name: str, api_key: str):
    """Set the correct env var for the given provider.
    Only sets if api_key is non-empty."""
    env_map = {
        'openai': 'OPENAI_API_KEY',
    }
    var = env_map.get(provider_name)
    if not var or not api_key:
        return
    os.environ[var] = api_key


KEY_PROVIDER_ENV = {
    # Only OpenRouter key is required for the free-tier providers
    # (fusion, auto, gpt_oss_120b all route through OpenRouter)
}


def resolve_chain(task_type: str, override_provider: str | None = None, api_key: str = '', client_key: str = '') -> list[str]:
    """Return ordered provider chain for a task type.
    Uses client-specific routing when available."""
    if override_provider:
        chain = [override_provider]
        fallback_str = os.environ.get('AI_FALLBACK_PROVIDERS', '').strip()
        if fallback_str:
            chain.extend(p.strip() for p in fallback_str.split(',') if p.strip())
        return chain

    # ── Client-specific routing ─────────────────────────────────────────
    if client_key:
        client_chain = CLIENT_ROUTING.get((client_key, task_type))
        if client_chain:
            return list(client_chain)

    # ── Standard routing ────────────────────────────────────────────────
    chain = list(TASK_ROUTING.get(task_type, ['fusion', 'gpt_oss_120b', 'local']))

    # If OpenAI key is available, use it; otherwise filter to OpenRouter-based providers
    if not os.environ.get('OPENAI_API_KEY', '').strip():
        # No OpenAI key — use OpenRouter free models + local
        chain = [p for p in chain if p in ('fusion', 'gpt_oss_120b', 'auto', 'local')]
    else:
        chain = [p for p in chain if p in ('fusion', 'openai', 'gpt_oss_120b', 'auto', 'local')]

    if 'local' not in chain:
        chain.append('local')

    return chain if chain else ['local']


def _cache_key(task_type: str, prompt: str) -> str:
    raw = f'{task_type}:{prompt}'
    return hashlib.md5(raw.encode()).hexdigest()


def _check_cache(key: str) -> dict | None:
    entry = _response_cache.get(key)
    if entry and (time.time() - entry[0]) < _CACHE_TTL:
        logger.debug('Cache hit for %s', key[:12])
        return entry[1]
    if entry:
        del _response_cache[key]
    return None


def _set_cache(key: str, result: dict):
    _response_cache[key] = (time.time(), result)


def _is_provider_healthy(provider_name: str) -> bool:
    return _provider_health.get(provider_name, 0) < _PROVIDER_DEGRADE_THRESHOLD


def _mark_provider_success(provider_name: str):
    _provider_health[provider_name] = 0


def _mark_provider_failure(provider_name: str):
    _provider_health[provider_name] = _provider_health.get(provider_name, 0) + 1


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
             client_key: str = '', **kwargs) -> dict[str, Any]:
    # Check cache first
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    last_error = None
    for provider_name in chain:
        # Rate limit check
        if not _rate_limiter.check(provider_name):
            logger.warning('Provider %s rate-limited, skipping', provider_name)
            last_error = f'Provider {provider_name} exceeded rate limit'
            continue

        # Health check
        if not _is_provider_healthy(provider_name):
            logger.warning('Provider %s degraded (skipping, %d consecutive fails)',
                          provider_name, _provider_health.get(provider_name, 0))
            last_error = f'Provider {provider_name} degraded'
            continue

        _ts = time.perf_counter()
        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)

            result, validation_errors = _call_with_debugger(
                task_type, provider_name,
                provider.generate, prompt,
                system_prompt=system_prompt, **kwargs
            )
            elapsed = time.perf_counter() - _ts
            if 'error' not in result or result['error'] is None:
                if not validation_errors:
                    logger.info('PROFILE router %s via %s in %.2fs', task_type, provider_name, elapsed)
                    _mark_provider_success(provider_name)
                    _set_cache(ck, result)
                    return result
                last_error = f"Validation failed after self-heal: {'; '.join(validation_errors)}"
            else:
                last_error = result['error']
            logger.warning('Provider %s failed for %s after %.2fs: %s', provider_name, task_type, elapsed, last_error)
            _mark_provider_failure(provider_name)
        except Exception as e:
            elapsed = time.perf_counter() - _ts
            last_error = str(e)
            logger.warning('Provider %s raised exception for %s after %.2fs: %s', provider_name, task_type, elapsed, last_error)
            _mark_provider_failure(provider_name)
    return {'error': f'All providers failed. Last error: {last_error}'}


def extract_structured(task_type: str, prompt: str,
                       api_key: str = '', override_provider: str | None = None,
                       client_key: str = '', **kwargs) -> dict[str, Any]:
    """Route a structured extraction task through the best provider chain
    with autodebugger self-healing on each provider."""
    # Check cache first
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    last_error = None
    for provider_name in chain:
        # Rate limit check
        if not _rate_limiter.check(provider_name):
            logger.warning('Provider %s rate-limited, skipping extraction', provider_name)
            last_error = f'Provider {provider_name} exceeded rate limit'
            continue

        # Health check
        if not _is_provider_healthy(provider_name):
            logger.warning('Provider %s degraded (skipping extraction, %d consecutive fails)',
                          provider_name, _provider_health.get(provider_name, 0))
            last_error = f'Provider {provider_name} degraded'
            continue

        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)

            result, validation_errors = _call_with_debugger(
                task_type, provider_name,
                provider.extract_structured, prompt, **kwargs
            )
            if 'error' not in result or result['error'] is None:
                if not validation_errors:
                    _mark_provider_success(provider_name)
                    _set_cache(ck, result)
                    return result
                last_error = f"Validation failed after self-heal: {'; '.join(validation_errors)}"
            else:
                last_error = result['error']
            logger.warning('Provider %s failed extraction for %s: %s', provider_name, task_type, last_error)
            _mark_provider_failure(provider_name)
        except Exception as e:
            last_error = str(e)
            logger.warning('Provider %s raised exception for extraction %s: %s', provider_name, task_type, last_error)
            _mark_provider_failure(provider_name)
    return {'error': f'All providers failed. Last error: {last_error}'}
