"""AI router — quality-aware multi-provider orchestration.

Architecture:
  Tier 1: ALL frontier free models (nemotron_ultra, qwen3_coder, kimi_k26, owl_alpha) via OpenRouter
          — run in parallel batches, first valid JSON wins
  Tier 2: ALL strong free models (nemotron_super, llama_70b, qwen3_next, hermes_405b) via OpenRouter
          — run in parallel batches, only if Tier 1 all fail
  Tier 3: Groq (groq_llama — Llama 3.3 70B, ~800 t/s)
          — single attempt, independent API endpoint, only if Tiers 1+2 fail
   Tier 4: Local AI (local_qwen / local_qwen_3b — Qwen2.5-3B or Qwen2.5-0.5B)
           — offline fallback, only if Tiers 1-3 fail

Quality-aware: each tier's output is scored (0-100). If below threshold,
the router upgrades to the next tier.
"""

import os
import time
import json
import hashlib
import logging
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from . import create_provider
from .debugger import Autodebugger
from .rate_limiter import ProviderRateLimiter
from .model_registry import ANTIGRAVITY_NAMES, FRONTIER_NAMES, STRONG_NAMES, GROQ_NAMES, LOCAL_NAMES, ALL_MODELS, TASK_PRIORITY

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
        if task_data.get("uses", 0) >= 2:
            candidates.append({
                "name": name,
                "uses": task_data["uses"],
                "avg_quality": task_data.get("avg_quality", 0),
                "failure_rate": task_data.get("failures", 0) / task_data["uses"],
            })
    if candidates:
        candidates.sort(key=lambda c: (-c["avg_quality"], c["failure_rate"]))
        return {"recommended": candidates[0]["name"], "candidates": candidates}
    chain = FRONTIER_NAMES + STRONG_NAMES + GROQ_NAMES + LOCAL_NAMES
    return {"recommended": chain[0] if chain else "local", "candidates": []}


_load_perf()

# ── Rate limiter (per-provider sliding window) ─────────────────────────────
_rate_limiter = ProviderRateLimiter()

_provider_health: dict[str, int] = {}
_PROVIDER_DEGRADE_THRESHOLD = int(os.environ.get('AI_DEGRADE_THRESHOLD', '3'))

_response_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = int(os.environ.get('AI_CACHE_TTL', '3600'))

OPENROUTER_MODELS = {
    m.openrouter_name: m.model_id
    for m in ALL_MODELS.values()
    if m.provider == "openrouter"
}

BATCH_SIZE = int(os.environ.get('AI_BATCH_SIZE', '2'))

PEAK_HOURS_START = int(os.environ.get('AI_PEAK_START', '12'))
PEAK_HOURS_END = int(os.environ.get('AI_PEAK_END', '18'))


def _is_openrouter_peak_hours() -> bool:
    """Weekdays 12:00-18:00 UTC — OpenRouter congestion hours."""
    now = time.gmtime()
    return now.tm_wday < 5 and PEAK_HOURS_START <= now.tm_hour < PEAK_HOURS_END


def _skip_openrouter(task_type: str) -> bool:
    """Skip OpenRouter tiers during peak hours for low-priority tasks."""
    return _is_openrouter_peak_hours() and TASK_PRIORITY.get(task_type, 'high') == 'low'


def resolve_chain(
    task_type: str,
    override_provider: str | None = None,
    api_key: str = '',
    client_key: str = '',
) -> list[str]:
    if override_provider:
        return [override_provider]
    return ANTIGRAVITY_NAMES + FRONTIER_NAMES + STRONG_NAMES + GROQ_NAMES + LOCAL_NAMES


def set_api_key(provider_name: str, api_key: str):
    if not api_key:
        return
    model = ALL_MODELS.get(provider_name)
    if model and model.provider == 'openrouter':
        os.environ['OPENROUTER_API_KEY'] = api_key
    elif provider_name == 'openrouter':
        os.environ['OPENROUTER_API_KEY'] = api_key
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
    model = ALL_MODELS.get(provider_name)
    if model:
        return model.model_id
    return OPENROUTER_MODELS.get(provider_name, 'openrouter/auto')


def _provider_has_key(provider_name: str) -> bool:
    env_map = {
        'groq': 'GROQ_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY',
    }
    model = ALL_MODELS.get(provider_name)
    if model and model.provider == 'openrouter':
        return bool(os.environ.get('OPENROUTER_API_KEY', '').strip())
    if model and model.provider == 'local':
        return True  # local server doesn't need an API key
    if model and model.provider == 'antigravity':
        return bool(os.environ.get('ANTIGRAVITY_REFRESH', '').strip())
    env = env_map.get(provider_name)
    if env:
        return bool(os.environ.get(env, '').strip())
    return False


def _call_with_debugger(
    task_type: str,
    provider_name: str,
    provider_fn,
    prompt: str,
    system_prompt: str | None = None,
    **kwargs,
) -> tuple[dict, list[str]]:
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


def _try_providers_batched(
    provider_names: list[str],
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    mode: str = 'generate',
    batch_size: int = BATCH_SIZE,
    **kwargs,
) -> tuple[dict | None, str | None]:
    """Try providers in parallel batches.

    Runs up to `batch_size` providers concurrently via ThreadPoolExecutor.
    On first successful result, cancels remaining futures and returns.
    If all in a batch fail, moves to the next batch.
    """
    eligible = [p for p in provider_names if _provider_has_key(p)]
    if not eligible:
        return None, 'No eligible providers in batch'

    last_error = None
    for batch_start in range(0, len(eligible), batch_size):
        batch = eligible[batch_start:batch_start + batch_size]
        logger.debug('Trying batch %s', batch)

        with ThreadPoolExecutor(max_workers=len(batch)) as ex:
            futures = {
                ex.submit(
                    _try_provider, p, task_type, prompt, system_prompt,
                    api_key, mode, **kwargs,
                ): p for p in batch
            }
            for future in as_completed(futures):
                result, err = future.result()
                if result is not None:
                    for f in futures:
                        f.cancel()
                    return result, None
                last_error = err

    return None, last_error


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
      1. Cache check
      2. Tier 1: ALL frontier free models in parallel batches
      3. Tier 2: ALL strong free models in parallel batches (if Tier 1 fails)
      4. Tier 3: Groq (if Tiers 1+2 fail)
      5. Tier 4: Local AI (qwen-3b or qwen-0.5b) (if Tiers 1-3 fail)
      6. Return error if all exhausted
    """
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
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
        return {'error': f'Override provider exhausted. Last: {err}'}

    result, _ = _try_providers_batched(
        ANTIGRAVITY_NAMES, task_type, prompt,
        system_prompt, api_key, 'generate', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    if _skip_openrouter(task_type):
        logger.info('PEAK: task_type=%s -> direct to Groq (Tier 3)', task_type)
        result, last_error = _try_providers_batched(
            GROQ_NAMES, task_type, prompt,
            system_prompt, api_key, 'generate', **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        return {'error': f'Groq exhausted. Last: {last_error}'}

    result, _ = _try_providers_batched(
        FRONTIER_NAMES, task_type, prompt,
        system_prompt, api_key, 'generate', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        STRONG_NAMES, task_type, prompt,
        system_prompt, api_key, 'generate', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        GROQ_NAMES, task_type, prompt,
        system_prompt, api_key, 'generate', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        LOCAL_NAMES, task_type, prompt,
        system_prompt, api_key, 'generate', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    return {'error': f'All providers exhausted. Last: {last_error}'}


def generate_stream(
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    **kwargs,
):
    """Stream a response through the provider chain.

    Tries providers sequentially (not in parallel, since streaming
    requires a single active connection). Falls through tiers:
    frontier → strong → groq → error.
    """
    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    elif _skip_openrouter(task_type):
        logger.info('PEAK: task_type=%s streaming -> direct to Groq (Tier 3)', task_type)
        chain = GROQ_NAMES[:]
    else:
        chain = ANTIGRAVITY_NAMES + FRONTIER_NAMES + STRONG_NAMES + GROQ_NAMES + LOCAL_NAMES

    for provider_name in chain:
        if not _provider_has_key(provider_name):
            continue
        if not _rate_limiter.check(provider_name):
            continue
        if not _is_provider_healthy(provider_name):
            continue

        try:
            set_api_key(provider_name, api_key)
            provider = create_provider(provider_name)

            collected = []
            for token in provider.generate_stream(prompt, system_prompt=system_prompt, **kwargs):
                collected.append(token)
                yield token

            full = ''.join(collected)
            if full and not full.startswith('[Error:'):
                _mark_provider_success(provider_name)
                return
            else:
                _mark_provider_failure(provider_name)
        except Exception as e:
            _mark_provider_failure(provider_name)
            yield f'[Error: {str(e)}]'
            return

    yield '[Error: All providers exhausted for streaming]'


def extract_structured(
    task_type: str,
    prompt: str,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    **kwargs,
) -> dict[str, Any]:
    """Route a structured extraction task through the quality-aware chain.

    Strategy:
      1. Cache check
      2. Tier 1: ALL frontier free models in parallel batches
      3. Tier 2: ALL strong free models in parallel batches (if Tier 1 fails)
      4. Tier 3: Groq (if Tiers 1+2 fail)
      5. Tier 4: Local AI (qwen-3b or qwen-0.5b) (if Tiers 1-3 fail)
    """
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
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
        return {'error': f'Override provider exhausted. Last: {err}'}

    result, _ = _try_providers_batched(
        ANTIGRAVITY_NAMES, task_type, prompt,
        None, api_key, 'extract', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    if _skip_openrouter(task_type):
        logger.info('PEAK: task_type=%s extract -> direct to Groq (Tier 3)', task_type)
        result, last_error = _try_providers_batched(
            GROQ_NAMES, task_type, prompt,
            None, api_key, 'extract', **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        return {'error': f'Groq exhausted. Last: {last_error}'}

    result, _ = _try_providers_batched(
        FRONTIER_NAMES, task_type, prompt,
        None, api_key, 'extract', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        STRONG_NAMES, task_type, prompt,
        None, api_key, 'extract', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        GROQ_NAMES, task_type, prompt,
        None, api_key, 'extract', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        LOCAL_NAMES, task_type, prompt,
        None, api_key, 'extract', **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    return {'error': f'All providers exhausted. Last: {last_error}'}
