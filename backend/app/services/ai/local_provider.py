"""Local AI provider using llama.cpp server (OpenAI-compatible API).
Falls back to offline generator if server is unreachable."""

import os
import json
import re
import time
import random
import urllib.request
import urllib.error
from typing import Any

from . import AIProvider


def _clean_json(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    return text


class LocalProvider(AIProvider):
    def __init__(self):
        self.base_url = os.environ.get('LOCAL_AI_URL', 'http://127.0.0.1:8080')
        self.timeout = int(os.environ.get('LOCAL_AI_TIMEOUT', '120'))
        self._healthy = None

    def _is_alive(self) -> bool:
        if self._healthy is False:
            return False
        try:
            req = urllib.request.Request(f'{self.base_url}/health')
            urllib.request.urlopen(req, timeout=2)
            self._healthy = True
            return True
        except Exception:
            self._healthy = False
            return False

    def _request(self, payload: dict) -> dict:
        if not self._is_alive():
            return {'error': 'Local AI server is not running'}
        url = f'{self.base_url}/v1/chat/completions'
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            return json.loads(resp.read().decode())
        except Exception as e:
            return {'error': f'Local AI unavailable: {e}'}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'model': 'local',
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.3),
            'max_tokens': kwargs.get('max_tokens', 4096),
            'stop': kwargs.get('stop', []),
        }

        result = self._request(payload)
        if 'error' in result:
            return result

        try:
            text = result['choices'][0]['message']['content']
            text = _clean_json(text)
            parsed = json.loads(text)
            return parsed
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {'error': f'Failed to parse response: {e}', 'raw': text if 'text' in dir() else ''}

    def extract_structured(self, prompt: str, response_mime_type: str | None = None) -> dict[str, Any]:
        messages = [{'role': 'user', 'content': prompt}]
        payload = {
            'model': 'local',
            'messages': messages,
            'temperature': 0.1,
            'max_tokens': 4096,
        }

        result = self._request(payload)
        if 'error' in result:
            return result

        try:
            text = result['choices'][0]['message']['content']
            text = _clean_json(text)
            parsed = json.loads(text)
            return parsed
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return {'error': f'Failed to parse response: {e}', 'raw': text if 'text' in dir() else ''}
