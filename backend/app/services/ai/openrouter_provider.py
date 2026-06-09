"""OpenRouter provider — routes through OpenRouter API.

Supports all free-tier and paid models via model_registry.py.
Single provider class handles all OpenRouter models by looking up
the model ID from the registry based on provider_name passed at init.
"""

import os
import json
import time
import random
import urllib.request
import urllib.error
from typing import Any

from . import AIProvider
from .model_registry import ALL_MODELS


class OpenRouterProvider(AIProvider):
    def __init__(self, provider_name: str = None):
        self.provider_name = provider_name or 'openrouter'
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        # Look up model ID from registry
        model = ALL_MODELS.get(self.provider_name)
        if model:
            self.model = model.model_id
        elif self.provider_name == 'openrouter':
            self.model = 'openrouter/free'
        else:
            self.model = 'openrouter/auto'

    def _call_with_retry(self, messages, temperature=0.3, max_tokens=4096, max_retries=2):
        if not self.api_key:
            return {'error': 'OPENROUTER_API_KEY not set'}

        url = 'https://openrouter.ai/api/v1/chat/completions'
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        data = json.dumps(payload).encode()
        last_error = None

        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.api_key}',
                        'HTTP-Referer': 'https://github.com/ComplianceHub',
                        'X-Title': 'ComplianceHub',
                    },
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode())

                if 'error' in result:
                    err_msg = result['error'].get('message', str(result['error']))
                    # Rate limit → wait longer
                    if 'rate' in err_msg.lower():
                        delay = 30 + random.uniform(0, 10)
                        time.sleep(delay)
                        continue
                    last_error = err_msg
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt + random.uniform(0, 1)
                        time.sleep(delay)
                    continue

                text = ''
                try:
                    text = result['choices'][0]['message']['content'].strip()
                except (KeyError, IndexError):
                    return {'error': 'No response from OpenRouter'}

                # Strip code fences
                if text.startswith('```'):
                    text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                    if text.endswith('```'):
                        text = text[:-3]
                    text = text.strip()

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {'text': text}

            except urllib.error.HTTPError as e:
                body = ''
                try:
                    body = e.read().decode()
                except Exception:
                    pass
                last_error = f'HTTP {e.code}: {body[:200]}'
                if e.code == 429:
                    delay = 30 + random.uniform(0, 10)
                    time.sleep(delay)
                    continue
                if attempt < max_retries - 1:
                    delay = 2 ** attempt + random.uniform(0, 1)
                    time.sleep(delay)
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = 2 ** attempt + random.uniform(0, 1)
                    time.sleep(delay)

        return {'error': f'OpenRouter failed after {max_retries} retries: {last_error}'}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        return self._call_with_retry(
            messages,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 4096),
        )

    def extract_structured(self, prompt: str, response_mime_type: str | None = None) -> dict[str, Any]:
        messages = [{'role': 'user', 'content': prompt}]
        return self._call_with_retry(messages, temperature=0.1, max_tokens=4096)
