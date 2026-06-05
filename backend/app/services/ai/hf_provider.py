"""HuggingFace Inference API provider — uses HF's free hosted inference.
Requires a free HuggingFace token (sign up at huggingface.co)."""

import os
import json
import re
import time
import random
import urllib.request
import urllib.error
from typing import Any

from . import AIProvider


MODEL = os.environ.get('HF_MODEL', 'Qwen/Qwen2.5-1.5B-Instruct')
API_URL = f'https://api-inference.huggingface.co/models/{MODEL}'


def _clean_json(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    return text


class HFProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('HF_API_KEY', '')
        self.model = os.environ.get('HF_MODEL', MODEL)

    def _request(self, prompt: str, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.3) -> dict:
        key = self.api_key or os.environ.get('HF_API_KEY', '')
        if not key:
            return {'error': 'HF_API_KEY not set. Get a free token at huggingface.co/settings/tokens'}

        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'inputs': prompt,
            'parameters': {
                'max_new_tokens': max_tokens,
                'temperature': temperature,
                'return_full_text': False,
            },
            'options': {'use_cache': False, 'wait_for_model': True},
        }

        data = json.dumps(payload).encode()
        url = f'https://api-inference.huggingface.co/models/{self.model}'
        req = urllib.request.Request(
            url, data=data,
            headers={
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
            },
        )

        try:
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read().decode())
            if isinstance(result, list):
                text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                text = result.get('generated_text', '')
            else:
                return {'error': f'Unexpected response: {result}'}
            return {'text': text}
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return {'error': f'HF API HTTP {e.code}: {body[:200]}'}
        except Exception as e:
            return {'error': f'HF API error: {e}'}

    def _parse_json(self, text: str) -> dict:
        cleaned = _clean_json(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            m = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
            return {'error': 'Failed to parse JSON response', 'raw': text[:500]}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        result = self._request(prompt, system_prompt,
                               max_tokens=kwargs.get('max_tokens', 4096),
                               temperature=kwargs.get('temperature', 0.3))
        if 'error' in result:
            return result
        return self._parse_json(result.get('text', ''))

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        result = self._request(prompt, max_tokens=4096, temperature=0.1)
        if 'error' in result:
            return result
        return self._parse_json(result.get('text', ''))
