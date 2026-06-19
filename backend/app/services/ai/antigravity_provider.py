import os
import time
import json
import logging
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)

from . import AIProvider
from .json_utils import extract_json


class AntigravityProvider(AIProvider):
    def __init__(self, provider_name: str | None = None):
        self.provider_name = provider_name or 'antigravity_claude_sonnet_46'
        self.model_map = {
            'antigravity_claude_sonnet_46': 'claude-sonnet-4-6',
            'antigravity_claude_opus_46': 'claude-opus-4-6-thinking',
        }
        self.model = self.model_map.get(self.provider_name, 'claude-sonnet-4-6')
        self.client_id = os.environ.get('ANTIGRAVITY_CLIENT_ID', '')
        self.client_secret = os.environ.get('ANTIGRAVITY_CLIENT_SECRET', '')
        self.refresh_token = os.environ.get('ANTIGRAVITY_REFRESH', '')
        self.base_url = 'https://cloudcode-pa.googleapis.com/v1internal:generateContent'
        self.project = 'rising-fact-p41fc'
        self._access_token = None
        self._token_expiry = 0.0

    def _ensure_token(self) -> str | None:
        if time.time() < self._token_expiry - 60 and self._access_token:
            return self._access_token
        if not self.refresh_token:
            return None
        data = json.dumps({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
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
                self._access_token = tok['access_token']
                self._token_expiry = time.time() + tok.get('expires_in', 3599)
                return self._access_token
        except Exception as e:
            logger.error('Antigravity token refresh failed: %s', e)
            return None

    def _call(
        self, prompt: str, system_prompt: str | None = None,
        temperature: float = 0.3, max_tokens: int = 8192,
    ) -> dict[str, Any]:
        access = self._ensure_token()
        if not access:
            return {'error': 'ANTIGRAVITY_REFRESH not set or expired'}
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
            'userAgent': 'antigravity',
            'requestId': f't-{int(time.time())}',
        }
        if system_prompt:
            body['request']['systemInstruction'] = {'parts': [{'text': system_prompt}]}
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            self.base_url,
            data=data,
            headers={
                'Authorization': f'Bearer {access}',
                'Content-Type': 'application/json',
                'User-Agent': 'antigravity/1.15.8 linux/arm64',
                'X-Goog-Api-Client': 'google-cloud-sdk vscode_cloudshelleditor/0.1',
                'Client-Metadata': json.dumps({
                    'ideType': 'ANTIGRAVITY', 'platform': 'LINUX', 'pluginType': 'GEMINI',
                }),
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())
            candidates = result.get('response', {}).get('candidates', [])
            if not candidates:
                return {'error': 'No candidates in Antigravity response'}
            parts = candidates[0].get('content', {}).get('parts', [])
            text = ''.join(p.get('text', '') for p in parts)
            if not text:
                return {'error': 'Empty text in Antigravity response'}
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
            return {'error': f'Antigravity HTTP {e.code}: {msg}'}
        except Exception as e:
            return {'error': f'Antigravity error: {e}'}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 8192),
        )

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        return self._call(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
            max_tokens=4096,
        )

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        access = self._ensure_token()
        if not access:
            yield 'ANTIGRAVITY_REFRESH not set or expired'
            return
        body = {
            'project': self.project,
            'model': self.model,
            'request': {
                'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'maxOutputTokens': kwargs.get('max_tokens', 8192),
                    'temperature': kwargs.get('temperature', 0.3),
                },
            },
            'userAgent': 'antigravity',
            'requestId': f't-{int(time.time())}',
        }
        if system_prompt:
            body['request']['systemInstruction'] = {'parts': [{'text': system_prompt}]}
        data = json.dumps(body).encode()
        try:
            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    'Authorization': f'Bearer {access}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'antigravity/1.15.8 linux/arm64',
                    'X-Goog-Api-Client': 'google-cloud-sdk vscode_cloudshelleditor/0.1',
                    'Client-Metadata': json.dumps({
                        'ideType': 'ANTIGRAVITY', 'platform': 'LINUX', 'pluginType': 'GEMINI',
                    }),
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode())
            candidates = result.get('response', {}).get('candidates', [])
            if not candidates:
                yield '[Error: No candidates]'
                return
            parts = candidates[0].get('content', {}).get('parts', [])
            text = ''.join(p.get('text', '') for p in parts)
            if text:
                yield text
            else:
                yield '[Error: Empty response]'
        except Exception as e:
            yield f'[Error: {str(e)}]'
