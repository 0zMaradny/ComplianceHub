"""AI router — quality-aware multi-provider orchestration.

Architecture:
  Tier 1: AgentRouter (paid, highest quality) — if key available
  Tier 2: Frontier free models (nemotron_ultra, qwen3_coder) — best per task
  Tier 3: Strong free models (llama_70b, gpt_oss_120b, etc.) — fallback
  Tier 4: Paid (fusion, auto) — last resort
  Tier 5: Local AI — offline fallback

Quality-aware: each tier's output is validated for content quality.
If quality is insufficient, the router upgrades to the next tier.
"""

import os
import time
import json
import hashlib
import logging
import threading
from pathlib import Path
from typing import Any

from . import create_provider
from .debugger import Autodebugger
from .rate_limiter import ProviderRateLimiter
from .model_registry import ALL_MODELS, get_task_chain

logger = logging.getLogger(__name__)

# ── Model performance tracking ─────────────────────────────────────────────
_PERF_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "model_performance.json"
_PERF_LOCK = threading.Lock()
_model_perf: dict[str, dict] = {}


def _load_perf():
    global _model_perf
    if _PERF_FILE.exists():
        try:
            with open(_PERF_FILE) as f:
                _model_perf = json.load(f)
        except (json.JSONDecodeError, IOError):
            _model_perf = {}


def _save_perf():
    _PERF_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _PERF_LOCK:
        with open(_PERF_FILE, "w") as f:
            json.dump(_model_perf, f, indent=2)


def record_model_result(provider_name: str, task_type: str, success: bool,
                        response_time_ms: int, quality_score: float = 0.0):
    """Record a model invocation result for performance tracking."""
    _load_perf()
    with _PERF_LOCK:
        if provider_name not in _model_perf:
            _model_perf[provider_name] = {
                "total_uses": 0, "total_failures": 0,
                "total_quality_score": 0.0, "quality_samples": 0,
                "total_response_ms": 0, "tasks": {},
            }
        p = _model_perf[provider_name]
        p["total_uses"] += 1
        if not success:
            p["total_failures"] += 1
        if quality_score > 0:
            p["total_quality_score"] += quality_score
            p["quality_samples"] += 1
        p["total_response_ms"] += response_time_ms
        # Per-task tracking
        if task_type not in p["tasks"]:
            p["tasks"][task_type] = {"uses": 0, "failures": 0, "avg_quality": 0.0}
        p["tasks"][task_type]["uses"] += 1
        if not success:
            p["tasks"][task_type]["failures"] += 1
        if quality_score > 0:
            t = p["tasks"][task_type]
            t["avg_quality"] = (t["avg_quality"] * (t["uses"] - 1) + quality_score) / t["uses"]
    _save_perf()


def get_model_performance() -> dict:
    """Return performance data for all models."""
    _load_perf()
    result = {}
    for name, p in _model_perf.items():
        uses = p["total_uses"] or 1
        avg_quality = (p["total_quality_score"] / p["quality_samples"]) if p["quality_samples"] > 0 else 0.0
        avg_ms = p["total_response_ms"] // uses
        result[name] = {
            "total_uses": p["total_uses"],
            "total_failures": p["total_failures"],
            "failure_rate_pct": round(p["total_failures"] / uses * 100, 1),
            "avg_quality_score": round(avg_quality, 1),
            "avg_response_time_ms": avg_ms,
            "tasks": p.get("tasks", {}),
        }
    return result


def get_model_recommendation(task_type: str) -> dict:
    """Recommend the best model for a task based on historical performance."""
    _load_perf()
    candidates = []
    for name, p in _model_perf.items():
        task_data = p.get("tasks", {}).get(task_type, {})
        if task_data.get("uses", 0) >= 2:  # need minimum samples
            candidates.append({
                "name": name,
                "uses": task_data["uses"],
                "avg_quality": task_data.get("avg_quality", 0),
                "failure_rate": task_data.get("failures", 0) / task_data["uses"],
            })
    if candidates:
        # Sort by quality desc, then failure rate asc
        candidates.sort(key=lambda c: (-c["avg_quality"], c["failure_rate"]))
        return {"recommended": candidates[0]["name"], "candidates": candidates}
    # Fallback to registry chain
    chain = get_task_chain(task_type)
    return {"recommended": chain[0] if chain else "local", "candidates": []}


# Load performance data on import
_load_perf()

# ── Rate limiter (per-provider sliding window) ─────────────────────────────
_rate_limiter = ProviderRateLimiter()

# ── Provider health tracking (skip after 3 consecutive fails) ──────────────
_provider_health: dict[str, int] = {}
_PROVIDER_DEGRADE_THRESHOLD = 3

# ── Response cache (md5 hash, 1h TTL) ──────────────────────────────────────
_response_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 3600

# ── OpenRouter model mapping ───────────────────────────────────────────────
OPENROUTER_MODELS = {
    m.openrouter_name: m.model_id
    for m in ALL_MODELS.values()
    if m.provider == "openrouter"
}


def resolve_chain(
    task_type: str,
    override_provider: str | None = None,
    api_key: str = '',
    client_key: str = '',
) -> list[str]:
    """Return ordered provider chain for a task type.

    Uses model_registry.get_task_chain() which picks the best model per tier.
    Always ends with 'local' as final fallback.
    """
    if override_provider:
        chain = [override_provider]
        fallback_str = os.environ.get('AI_FALLBACK_PROVIDERS', '').strip()
        if fallback_str:
            chain.extend(p.strip() for p in fallback_str.split(',') if p.strip())
        if 'local' not in chain:
            chain.append('local')
        return chain

    return get_task_chain(task_type)


def set_api_key(provider_name: str, api_key: str):
    """Set the correct env var for the given provider."""
    if not api_key:
        return
    model = ALL_MODELS.get(provider_name)
    if model and model.provider == 'openrouter':
        os.environ['OPENROUTER_API_KEY'] = api_key
    elif provider_name in ('openrouter', 'openai'):
        # Generic openrouter name or openai → set OpenRouter key
        os.environ['OPENROUTER_API_KEY'] = api_key
        if provider_name == 'openai':
            os.environ['OPENAI_API_KEY'] = api_key
    # Also handle legacy provider names
    elif provider_name == 'agentrouter':
        os.environ['AGENTROUTER_API_KEY'] = api_key
    elif provider_name == 'groq':
        os.environ['GROQ_API_KEY'] = api_key


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


def _get_model_id(provider_name: str) -> str:
    """Get the OpenRouter model ID for a provider name."""
    model = ALL_MODELS.get(provider_name)
    if model:
        return model.model_id
    # Fallback for providers not in registry
    return OPENROUTER_MODELS.get(provider_name, 'openrouter/auto')


def _provider_has_key(provider_name: str) -> bool:
    """Check if the API key for a provider is available."""
    env_map = {
        'agentrouter': 'AGENTROUTER_API_KEY',
        'groq': 'GROQ_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY',
        'hf': 'HF_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'gemini': 'GEMINI_API_KEY',
        'claude': 'CLAUDE_API_KEY',
    }
    # All OpenRouter free models use OPENROUTER_API_KEY
    model = ALL_MODELS.get(provider_name)
    if model and model.provider == 'openrouter':
        return bool(os.environ.get('OPENROUTER_API_KEY', '').strip())
    env = env_map.get(provider_name)
    if env:
        return bool(os.environ.get(env, '').strip())
    # Local doesn't need a key
    return provider_name == 'local'


def _call_with_debugger(
    task_type: str,
    provider_name: str,
    provider_fn,
    prompt: str,
    system_prompt: str | None = None,
    **kwargs,
) -> tuple[dict, list[str]]:
    """Call a provider wrapped in Autodebugger self-healing.

    Returns (result, errors) where errors may include:
    - '_validation_errors': structure validation failures
    - '_quality_errors': content quality failures (triggers model upgrade)
    """
    debugger = Autodebugger(task_type)
    result = debugger.call_with_self_heal(
        provider_fn, prompt, system_prompt=system_prompt, **kwargs
    )
    validation_errors = result.pop('_validation_errors', [])
    return result, validation_errors


def _try_provider(
    provider_name: str,
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    mode: str = 'generate',
    **kwargs,
) -> tuple[dict | None, str | None]:
    """Try a single provider with full quality-aware validation.

    Returns (result, None) on success, or (None, error_message) on failure.
    On quality failure, returns (result, quality_error) with result containing
    '_quality_errors' for the caller to handle.
    """
    if not _rate_limiter.check(provider_name):
        return None, f'Provider {provider_name} exceeded rate limit'
    if not _is_provider_healthy(provider_name):
        return None, f'Provider {provider_name} degraded'

    _ts = time.perf_counter()
    try:
        set_api_key(provider_name, api_key)
        provider = create_provider(provider_name)
        fn = provider.extract_structured if mode == 'extract' else provider.generate

        result, validation_errors = _call_with_debugger(
            task_type, provider_name, fn, prompt,
            system_prompt=system_prompt if mode == 'generate' else None,
            **kwargs,
        )
        elapsed = time.perf_counter() - _ts

        elapsed_ms = int((time.perf_counter() - _ts) * 1000)

        if 'error' in result and result['error'] is not None:
            logger.warning('Provider %s failed %s in %.2fs: %s',
                           provider_name, task_type, elapsed, result['error'])
            _mark_provider_failure(provider_name)
            record_model_result(provider_name, task_type, False, elapsed_ms)
            return None, result['error']

        # Check quality errors — triggers MODEL UPGRADE
        quality_errors = result.pop('_quality_errors', [])
        if quality_errors:
            logger.warning('Provider %s quality-failed %s in %.2fs: %s',
                           provider_name, task_type, elapsed, quality_errors[:2])
            _mark_provider_failure(provider_name)
            record_model_result(provider_name, task_type, False, elapsed_ms, quality_score=3.0)
            return None, f'Quality insufficient: {"; ".join(str(e) for e in quality_errors[:2])}'

        if validation_errors:
            logger.warning('Provider %s validation-failed %s in %.2fs',
                           provider_name, task_type, elapsed)
            _mark_provider_failure(provider_name)
            record_model_result(provider_name, task_type, False, elapsed_ms)
            return None, f"Validation failed: {'; '.join(validation_errors)}"

        # Success — compute quality score for tracking
        _debugger = Autodebugger(task_type)
        _, quality_issues = _debugger.validate_quality(result)
        quality_score = max(0, 10 - len(quality_issues) * 1.5)  # rough score

        logger.info('PROFILE %s via %s in %.2fs (q=%.1f)', task_type, provider_name, elapsed, quality_score)
        _mark_provider_success(provider_name)
        record_model_result(provider_name, task_type, True, elapsed_ms, quality_score)
        # Attach metadata to result for upstream use
        result['_model_used'] = provider_name
        result['_quality_score'] = round(quality_score, 1)
        result['_response_time_ms'] = elapsed_ms
        return result, None

    except Exception as e:
        elapsed_ms = int((time.perf_counter() - _ts) * 1000)
        logger.warning('Provider %s exception %s in %.2fs: %s',
                       provider_name, task_type, elapsed, e)
        _mark_provider_failure(provider_name)
        record_model_result(provider_name, task_type, False, elapsed_ms)
        return None, str(e)


def generate(
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    **kwargs,
) -> dict[str, Any]:
    """Generate a document through the quality-aware provider chain.

    Strategy:
    1. If override_provider: use that chain
    2. If AgentRouter key available: try it first (paid, highest quality)
    3. Try best frontier free model for this task
    4. If quality fails → try next free model in chain
    5. Last resort: openrouter/auto (paid) → local
    """
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    # Build provider chain
    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    else:
        chain: list[str] = []
        # Tier 1: AgentRouter (if available)
        if _provider_has_key('agentrouter'):
            chain.append('agentrouter')
        # Tiers 2-4: model registry chain (frontier → strong → basic → paid)
        chain.extend(get_task_chain(task_type))
        # Deduplicate while preserving order
        seen: set[str] = set()
        deduped: list[str] = []
        for p in chain:
            if p not in seen:
                deduped.append(p)
                seen.add(p)
        chain = deduped

    last_error = None
    for provider_name in chain:
        if not _provider_has_key(provider_name):
            continue

        result, err = _try_provider(
            provider_name, task_type, prompt,
            system_prompt, api_key, 'generate', **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        last_error = err

    return {'error': f'All providers exhausted. Last: {last_error}'}


def extract_structured(
    task_type: str,
    prompt: str,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    **kwargs,
) -> dict[str, Any]:
    """Route a structured extraction task through the quality-aware chain."""
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    else:
        chain = []
        if _provider_has_key('agentrouter'):
            chain.append('agentrouter')
        chain.extend(get_task_chain(task_type))
        seen: set[str] = set()
        deduped: list[str] = []
        for p in chain:
            if p not in seen:
                deduped.append(p)
                seen.add(p)
        chain = deduped

    last_error = None
    for provider_name in chain:
        if not _provider_has_key(provider_name):
            continue

        result, err = _try_provider(
            provider_name, task_type, prompt,
            None, api_key, 'extract', **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        last_error = err

    return {'error': f'All providers exhausted. Last: {last_error}'}
