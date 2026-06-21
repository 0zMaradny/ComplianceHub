import time
import json
import logging
import threading
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)

from . import AIProvider

from .json_utils import extract_json
from app.settings import ANTIGRAVITY_CLIENT_ID, ANTIGRAVITY_CLIENT_SECRET, ANTIGRAVITY_REFRESH_TOKENS

# Per-model concurrency limits (stress-tested June 2026)
# Claude + gemini-3-flash: 2 concurrent per account (429 at 3+)
# gemini-2.5-*: 15+ concurrent per account (effectively unlimited)
_MODEL_CONCURRENCY = {
    'claude-sonnet-4-6': 2,
    'claude-opus-4-6-thinking': 2,
    'gemini-3-flash': 2,
    'gemini-2.5-pro': 2,
    'gemini-2.5-flash': 20,
    'gemini-2.5-flash-thinking': 20,
}

_semaphore_lock = threading.Lock()
_semaphores: dict[tuple[str, int], threading.Semaphore] = {}


def _get_semaphore(model: str, token_idx: int) -> threading.Semaphore:
    key = (model, token_idx)
    with _semaphore_lock:
        if key not in _semaphores:
            limit = _MODEL_CONCURRENCY.get(model, 2)
            _semaphores[key] = threading.Semaphore(limit)
        return _semaphores[key]


class _RetryableError(Exception):
    def __init__(self, reason: str, cooldown: float = 86400, attempt: int = 0):
        self.reason = reason
        self.attempt = attempt
        # Exponential backoff: 30s → 300s → 3600s → 86400s max
        backoff_sequence = [30, 300, 3600, 86400]
        idx = min(attempt, len(backoff_sequence) - 1)
        self.cooldown = backoff_sequence[idx]
        super().__init__(reason)


class _FatalError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class AntigravityProvider(AIProvider):
    def __init__(self, provider_name: str | None = None):
        self.provider_name = provider_name or 'antigravity_claude_sonnet_46'
        self.model_map = {
            'antigravity_claude_sonnet_46': 'claude-sonnet-4-6',
            'antigravity_claude_opus_46': 'claude-opus-4-6-thinking',
            'antigravity_gemini_3_flash': 'gemini-3-flash',
            'antigravity_gemini_25_flash': 'gemini-2.5-flash',
            'antigravity_gemini_25_flash_thinking': 'gemini-2.5-flash-thinking',
            'antigravity_gemini_25_pro': 'gemini-2.5-pro',
        }
        self.model = self.model_map.get(self.provider_name, 'claude-sonnet-4-6')
        self.client_id = ANTIGRAVITY_CLIENT_ID
        self.client_secret = ANTIGRAVITY_CLIENT_SECRET

        raw_tokens = [t.strip() for t in ANTIGRAVITY_REFRESH_TOKENS.split(',') if t.strip()]
        self.tokens = [{'token': t, 'exhausted_until': 0.0, 'access_token': None, 'token_expiry': 0.0} for t in raw_tokens]
        self.current_token_idx = 0

        self.base_url = 'https://cloudcode-pa.googleapis.com/v1internal:generateContent'
        self.project = 'rising-fact-p41fc'

    def _get_active_token_obj(self):
        if not self.tokens:
            return None
        for _ in range(len(self.tokens)):
            t_obj = self.tokens[self.current_token_idx]
            if time.time() > t_obj['exhausted_until']:
                return t_obj
            self.current_token_idx = (self.current_token_idx + 1) % len(self.tokens)
        return self.tokens[self.current_token_idx]

    def _ensure_token(self) -> str | None:
        t_obj = self._get_active_token_obj()
        if not t_obj:
            return None

        if time.time() < t_obj['token_expiry'] - 60 and t_obj['access_token']:
            return t_obj['access_token']

        data = json.dumps({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': t_obj['token'],
            'grant_type': 'refresh_token',
        }).encode()
        req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=data,
            headers={'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                tok = json.loads(resp.read().decode())
                t_obj['access_token'] = tok['access_token']
                t_obj['token_expiry'] = time.time() + tok.get('expires_in', 3599)
                return t_obj['access_token']
        except Exception as e:
            logger.error('Antigravity token refresh failed for a token: %s', e)
            return None

    def _call_with_retry(self, body_data: bytes, max_retries: int = 6) -> dict[str, Any]:
        last_error = None
        _429_count = 0
        for attempt in range(max_retries):
            t_obj = self._get_active_token_obj()
            if not t_obj:
                return {'error': 'No Antigravity refresh tokens configured.'}

            token_idx = self.current_token_idx
            access = self._ensure_token()
            if not access:
                t_obj['exhausted_until'] = time.time() + 300
                self.current_token_idx = (self.current_token_idx + 1) % len(self.tokens)
                continue

            sem = _get_semaphore(self.model, token_idx)
            acquired = sem.acquire(timeout=2)
            if not acquired:
                logger.warning('Antigravity semaphore timeout model=%s token=%d', self.model, token_idx)
                self.current_token_idx = (self.current_token_idx + 1) % len(self.tokens)
                last_error = {'error': f'Concurrency limit reached for {self.model}'}
                continue

            try:
                result = self._do_request(access, body_data)
                return result
            except _RetryableError as re:
                if 'Rate limited (429)' in re.reason:
                    _429_count += 1
                    re.attempt = _429_count
                logger.warning('Antigravity %s (attempt %d/%d, cooldown=%.0fs)', re.reason, attempt + 1, max_retries, re.cooldown)
                t_obj['exhausted_until'] = time.time() + re.cooldown
                self.current_token_idx = (self.current_token_idx + 1) % len(self.tokens)
                last_error = {'error': re.reason}
                continue
            except _FatalError as fe:
                return {'error': fe.reason}
            finally:
                sem.release()

        return last_error or {'error': 'Antigravity failed after retries.'}

    def _do_request(self, access: str, body_data: bytes) -> dict[str, Any]:
        req = urllib.request.Request(
            self.base_url,
            data=body_data,
            headers={
                'Authorization': f'Bearer {access}',
                'Content-Type': 'application/json',
                'User-Agent': 'antigravity/2.0 linux/arm64',
                'X-Goog-Api-Client': 'google-cloud-sdk vscode_cloudshelleditor/0.1',
                'Client-Metadata': json.dumps({
                    'ideType': 'ANTIGRAVITY', 'platform': 'LINUX', 'pluginType': 'ANTIGRAVITY',
                }),
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
            candidates = result.get('response', {}).get('candidates', [])
            if not candidates:
                raise _FatalError('No candidates in Antigravity response')
            parts = candidates[0].get('content', {}).get('parts', [])
            text = ''.join(p.get('text', '') for p in parts if 'text' in p)
            if not text:
                raise _FatalError('Empty text in Antigravity response')

            parsed = extract_json(text)
            if parsed is not None:
                return parsed
            return {'text': text}

        except urllib.error.HTTPError as e:
            body_bytes = e.read()
            try:
                detail = json.loads(body_bytes.decode())
                msg = detail.get('error', {}).get('message', str(detail)[:200])
            except Exception:
                msg = body_bytes.decode()[:200]

            if e.code == 429:
                raise _RetryableError(f'Rate limited (429): {msg}', attempt=0)
            elif e.code == 503:
                raise _RetryableError(f'No capacity (503): {msg}', cooldown=300)
            else:
                raise _FatalError(f'Antigravity HTTP {e.code}: {msg}')

        except (_RetryableError, _FatalError):
            raise
        except Exception as e:
            raise _FatalError(f'Antigravity error: {e}')

    def _call(
        self, prompt: str, system_prompt: str | None = None,
        temperature: float = 0.3, max_tokens: int = 8192,
    ) -> dict[str, Any]:
        body = {
            'project': self.project,
            'model': self.model,
            'request': {
                'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'maxOutputTokens': max_tokens,
                    'temperature': temperature,
                },
            },
            'userAgent': 'antigravity/2.0',
            'requestId': f't-{int(time.time())}',
        }
        if system_prompt:
            body['request']['systemInstruction'] = {'parts': [{'text': system_prompt}]}

        data = json.dumps(body).encode()
        retries = max(1, len(self.tokens))
        return self._call_with_retry(data, max_retries=retries)

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 8192),
        )

    def extract_structured(self, prompt: str, response_mime_type: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
            max_tokens=4096,
        )

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        result = self.generate(prompt, system_prompt, **kwargs)
        if 'error' in result:
            yield f"[Error: {result['error']}]"
            return
        text = result.get('text', '')
        if not text and isinstance(result, dict):
            text = json.dumps(result, ensure_ascii=False)
        words = text.split(' ')
        for i, word in enumerate(words):
            yield word + (' ' if i < len(words) - 1 else '')
