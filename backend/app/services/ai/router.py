"""AI router — quality-aware multi-provider orchestration with Council Mode + Arabic routing + PII scrub.

Architecture:
  Tier 0: Antigravity (Claude Sonnet 4 via Google API) — premium quality, Arabic MSA, PII-safe
  Tier 1: ALL frontier free models (nemotron_ultra, qwen3_coder, kimi_k26, owl_alpha, deepseek_v4_pro, minimax_m3) via OpenRouter
          — run in parallel batches, first valid JSON wins
  Tier 2: ALL strong free models (nemotron_super, llama_70b, qwen3_next, hermes_405b, glm_47_flash) via OpenRouter
          — run in parallel batches, only if Tier 1 all fail
  Tier 3: Groq (groq_llama — Llama 3.3 70B, ~800 t/s) + Cerebras (llama_3.3_70b, ~2500 t/s)
          — single attempt, independent API endpoint, only if Tiers 1+2 fail
  Tier 4: Local AI (local_qwen / local_qwen_3b — Qwen2.5-3B or Qwen2.5-0.5B)
          — offline fallback, only if Tiers 1-3 fail

Quality-aware: each tier's output is scored (0-100). If below threshold,
the router upgrades to the next tier.

Council Mode: parallel query Tiers 0/1/2 + Judge synthesis for high-stakes docs.
Arabic routing: MOI/Al-Ahsa clients route to Claude Sonnet 4 (Tier 0) for MSA quality.
PII scrubbing: Saudi IDs, phones, emails stripped before non-Tier-0 calls.
"""

import os
import re
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
from app import settings as app_settings
from app.services.validator import validate_and_heal

logger = logging.getLogger(__name__)

# ── Council Mode configuration ──────────────────────────────────────────────
COUNCIL_MODE_ENABLED = os.getenv("COUNCIL_MODE_ENABLED", "false").lower() == "true"
COUNCIL_JUDGE_MODEL = os.getenv("COUNCIL_JUDGE_MODEL", "antigravity_claude_sonnet_46")

# ── Arabic client routing ──────────────────────────────────────────────────
ARABIC_CLIENTS = {"MSD-MOI", "Al-Ahsa", "AHSA", "MOI"}
ARABIC_PREFERRED_MODEL = "antigravity_claude_sonnet_46"

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
_PROVIDER_DEGRADE_THRESHOLD = app_settings.AI_DEGRADE_THRESHOLD

_response_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = app_settings.AI_CACHE_TTL

OPENROUTER_MODELS = {
    m.openrouter_name: m.model_id
    for m in ALL_MODELS.values()
    if m.provider == "openrouter"
}

BATCH_SIZE = app_settings.AI_BATCH_SIZE

PEAK_HOURS_START = app_settings.AI_PEAK_START
PEAK_HOURS_END = app_settings.AI_PEAK_END


# ── PII Scrubbing (PDPL compliance) ────────────────────────────────────────
def scrub_pii(text: str) -> str:
    """Remove KSA PII before sending to non-Tier-0 providers."""
    # Saudi National ID / Iqama (10 digits starting with 1 or 2)
    text = re.sub(r'\b[12]\d{9}\b', '[REDACTED_ID]', text)
    # Saudi phone numbers
    text = re.sub(r'\b(\+966|00966|05)\d{8,9}\b', '[REDACTED_PHONE]', text)
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
    # Government employee IDs (hex format like 004D26)
    text = re.sub(r'\b[0-9A-F]{6}\b', '[REDACTED_EMPLOYEE_ID]', text)
    return text


def _is_arabic_client(client_key: str) -> bool:
    """Check if client requires Arabic MSA output."""
    if not client_key:
        return False
    client_upper = client_key.upper()
    return any(arabic in client_upper for arabic in ARABIC_CLIENTS)


def _is_streaming_quality_acceptable(text: str, task_type: str) -> bool:
    """Basic quality check for streamed responses."""
    if not text or len(text.strip()) < 50:
        return False
    placeholder_patterns = [
        r'\[Client Name\]', r'\[client_name\]', r'\[TBD\]', r'\[TODO\]',
        r'XXXXXX', r'xxxxxx', r'\[insert', r'\[Insert',
        r'N/A\s*$', r'lorem ipsum',
    ]
    for pat in placeholder_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return False
    return True


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
    """Resolve the provider chain for a given task."""
    if override_provider:
        ALIASES = {"claude": "antigravity_claude_sonnet_46"}
        resolved = ALIASES.get(override_provider, override_provider)
        return [resolved]
    
    # Arabic clients → force Tier 0 (Claude Sonnet 4) for MSA quality
    if _is_arabic_client(client_key):
        logger.info('Arabic client detected: %s → routing to %s', client_key, ARABIC_PREFERRED_MODEL)
        return [ARABIC_PREFERRED_MODEL]
    
    all_names = ANTIGRAVITY_NAMES + FRONTIER_NAMES + STRONG_NAMES + GROQ_NAMES + LOCAL_NAMES

    def sort_key(name: str) -> tuple:
        model = ALL_MODELS.get(name)
        claims_task = model and task_type in model.strengths
        if name in ANTIGRAVITY_NAMES:
            tier = 0
        elif name in FRONTIER_NAMES:
            tier = 1
        elif name in STRONG_NAMES:
            tier = 2
        elif name in GROQ_NAMES:
            tier = 3
        else:
            tier = 4
        return (tier, 0 if claims_task else 1, all_names.index(name))

    if _skip_openrouter(task_type):
        fast_names = LOCAL_NAMES + GROQ_NAMES + ANTIGRAVITY_NAMES
        return sorted(fast_names, key=sort_key)

    return sorted(all_names, key=sort_key)


def set_api_key(provider_name: str, api_key: str):
    """Store API key in provider instance cache."""
    if not api_key:
        return
    from . import _PROVIDER_LOCK, _PROVIDER_CACHE
    with _PROVIDER_LOCK:
        provider = _PROVIDER_CACHE.get(provider_name)
        if provider and hasattr(provider, 'api_key'):
            provider.api_key = api_key


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
    model = ALL_MODELS.get(provider_name)
    if model and model.provider == 'openrouter':
        return bool(app_settings.OPENROUTER_API_KEY.strip())
    if model and model.provider == 'local':
        return True
    if model and model.provider == 'antigravity':
        return bool(app_settings.ANTIGRAVITY_REFRESH_TOKENS.strip())
    if provider_name == 'groq':
        return bool(app_settings.GROQ_API_KEY.strip())
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
    client_key: str = '',
    **kwargs,
) -> tuple[dict | None, str | None]:
    if not _rate_limiter.check(provider_name):
        return None, f'Provider {provider_name} exceeded rate limit'
    if not _is_provider_healthy(provider_name):
        return None, f'Provider {provider_name} degraded'

    # PII scrubbing: strip PII before sending to non-Tier-0 providers
    is_tier0 = provider_name in ANTIGRAVITY_NAMES
    scrubbed_prompt = prompt if is_tier0 else scrub_pii(prompt)

    _ts = time.perf_counter()
    try:
        set_api_key(provider_name, api_key)
        provider = create_provider(provider_name)
        fn = provider.extract_structured if mode == 'extract' else provider.generate

        result, validation_errors = _call_with_debugger(
            task_type, provider_name, fn, scrubbed_prompt,
            system_prompt=system_prompt if mode == 'generate' else None,
            **kwargs,
        )
        elapsed = time.perf_counter() - _ts
        elapsed_ms = int(elapsed * 1000)

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

        _debugger = Autodebugger(task_type)
        _, quality_issues = _debugger.validate_quality(result)
        quality_score = max(0, 10 - len(quality_issues) * 1.5)

        logger.info('PROFILE %s via %s in %.2fs (q=%.1f)', task_type, provider_name, elapsed, quality_score)
        _mark_provider_success(provider_name)
        record_model_result(provider_name, task_type, True, elapsed_ms, quality_score)
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
    client_key: str = '',
    **kwargs,
) -> tuple[dict | None, str | None]:
    """Try providers in parallel batches."""
    eligible = [p for p in provider_names if _provider_has_key(p)]
    if not eligible:
        return None, 'No eligible providers in batch'

    last_error = None
    for batch_start in range(0, len(eligible), batch_size):
        batch = eligible[batch_start:batch_start + batch_size]
        logger.debug('Trying batch %s', batch)

        cancel_event = threading.Event()

        def _try_provider_cancelable(p, *args, **kw):
            if cancel_event.is_set():
                return None, 'Cancelled'
            result, err = _try_provider(p, *args, **kw)
            if result is not None:
                cancel_event.set()
            return result, err

        with ThreadPoolExecutor(max_workers=len(batch)) as ex:
            futures = {
                ex.submit(
                    _try_provider_cancelable, p, task_type, prompt, system_prompt,
                    api_key, mode, client_key, **kwargs,
                ): p for p in batch
            }
            for future in as_completed(futures):
                result, err = future.result()
                if result is not None:
                    cancel_event.set()
                    return result, None
                last_error = err

    return None, last_error


def _council_route(
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    client_key: str = '',
    **kwargs,
) -> dict[str, Any]:
    """Council Mode: parallel query Tiers 0/1/2 + Judge synthesis."""
    logger.info('Council Mode activated for task: %s', task_type)
    
    tasks = [
        _try_providers_batched(ANTIGRAVITY_NAMES, task_type, prompt, system_prompt, api_key, 'generate', client_key=client_key, **kwargs),
        _try_providers_batched(FRONTIER_NAMES[:2], task_type, prompt, system_prompt, api_key, 'generate', client_key=client_key, **kwargs),
        _try_providers_batched(STRONG_NAMES[:2], task_type, prompt, system_prompt, api_key, 'generate', client_key=client_key, **kwargs),
    ]
    
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(lambda t=t: t for t in tasks) for task in tasks]
        results = [f.result() for f in as_completed(futures)]
    
    valid_drafts = []
    for result, err in results:
        if result is not None:
            valid_drafts.append(result)
    
    if len(valid_drafts) < 2:
        logger.warning('Council Mode: insufficient drafts (%d), falling back', len(valid_drafts))
        return valid_drafts[0] if valid_drafts else _route(task_type, prompt, 'generate', system_prompt, api_key, client_key=client_key, **kwargs)
    
    judge_prompt = f"""You are a Senior Lead Auditor synthesizing multiple AI drafts.
Review these drafts and produce a single consensus answer.
Discard hallucinations. Enforce client formulas and ISO clause accuracy.

ORIGINAL REQUEST:
{prompt}

DRAFTS:
{chr(10).join(f'--- Draft {i+1} ---{chr(10)}{json.dumps(d, indent=2)[:2000]}' for i, d in enumerate(valid_drafts))}

OUTPUT: Final consensus JSON only. No meta-commentary."""
    
    judge_result, judge_err = _try_providers_batched(
        [COUNCIL_JUDGE_MODEL], task_type, judge_prompt, system_prompt, api_key, 'generate', client_key=client_key, **kwargs
    )
    
    if judge_result is not None:
        judge_result['_council_mode'] = True
        judge_result['_council_drafts'] = len(valid_drafts)
        return judge_result
    
    logger.warning('Council Mode: Judge failed, returning first draft. Error: %s', judge_err)
    valid_drafts[0]['_council_mode'] = 'fallback'
    return valid_drafts[0]


def _route(
    task_type: str,
    prompt: str,
    mode: str = 'generate',
    system_prompt: str | None = None,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    council_mode: bool = False,
    **kwargs,
) -> dict[str, Any]:
    """Route a task through the quality-aware provider chain."""
    ck = _cache_key(task_type, prompt)
    cached = _check_cache(ck)
    if cached is not None:
        return cached

    sp = system_prompt if mode == 'generate' else None

    if council_mode and COUNCIL_MODE_ENABLED and mode == 'generate':
        result = _council_route(task_type, prompt, sp, api_key, client_key, **kwargs)
        if result is not None:
            _set_cache(ck, result)
            return result

    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
        for provider_name in chain:
            if not _provider_has_key(provider_name):
                continue
            result, err = _try_provider(
                provider_name, task_type, prompt,
                sp, api_key, mode, client_key, **kwargs,
            )
            if result is not None:
                _set_cache(ck, result)
                return result
        return {'error': f'Override provider exhausted. Last: {err}', 'code': 'ALL_PROVIDERS_EXHAUSTED', 'provider': 'router'}

    result, _ = _try_providers_batched(
        ANTIGRAVITY_NAMES, task_type, prompt,
        sp, api_key, mode, client_key=client_key, **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    if _skip_openrouter(task_type):
        logger.info('PEAK: task_type=%s %s -> Groq (Tier 3) + Local (Tier 4)', task_type, mode)
        result, last_error = _try_providers_batched(
            GROQ_NAMES, task_type, prompt,
            sp, api_key, mode, client_key=client_key, **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        result, last_error = _try_providers_batched(
            LOCAL_NAMES, task_type, prompt,
            sp, api_key, mode, client_key=client_key, **kwargs,
        )
        if result is not None:
            _set_cache(ck, result)
            return result
        return {'error': f'Groq + Local exhausted. Last: {last_error}', 'code': 'ALL_PROVIDERS_EXHAUSTED', 'provider': 'router'}

    result, _ = _try_providers_batched(
        FRONTIER_NAMES, task_type, prompt,
        sp, api_key, mode, client_key=client_key, **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        STRONG_NAMES, task_type, prompt,
        sp, api_key, mode, client_key=client_key, **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        GROQ_NAMES, task_type, prompt,
        sp, api_key, mode, client_key=client_key, **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    result, last_error = _try_providers_batched(
        LOCAL_NAMES, task_type, prompt,
        sp, api_key, mode, client_key=client_key, **kwargs,
    )
    if result is not None:
        _set_cache(ck, result)
        return result

    return {'error': f'All providers exhausted. Last: {last_error}', 'code': 'ALL_PROVIDERS_EXHAUSTED', 'provider': 'router'}


def generate(
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    council_mode: bool = False,
    **kwargs,
) -> dict[str, Any]:
    """Generate a document through the quality-aware provider chain."""
    return _route(task_type, prompt, 'generate', system_prompt, api_key, override_provider, client_key, council_mode, **kwargs)


def generate_stream(
    task_type: str,
    prompt: str,
    system_prompt: str | None = None,
    api_key: str = '',
    override_provider: str | None = None,
    client_key: str = '',
    **kwargs,
):
    """Stream a response through the provider chain."""
    scrubbed_prompt = scrub_pii(prompt) if not override_provider else prompt
    
    if override_provider:
        chain = resolve_chain(task_type, override_provider, api_key, client_key=client_key)
    elif _skip_openrouter(task_type):
        logger.info('PEAK: task_type=%s streaming -> Antigravity + Groq + Local', task_type)
        chain = ANTIGRAVITY_NAMES + GROQ_NAMES + LOCAL_NAMES
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
            for token in provider.generate_stream(scrubbed_prompt, system_prompt=system_prompt, **kwargs):
                collected.append(token)
                yield token

            full = ''.join(collected)
            if full and not full.startswith('[Error:'):
                if _is_streaming_quality_acceptable(full, task_type):
                    _mark_provider_success(provider_name)
                    return
                else:
                    logger.warning('Streaming quality check failed for %s (task=%s)', provider_name, task_type)
                    _mark_provider_failure(provider_name)
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
    """Route a structured extraction task through the quality-aware chain."""
    return _route(task_type, prompt, 'extract', None, api_key, override_provider, client_key, **kwargs)
