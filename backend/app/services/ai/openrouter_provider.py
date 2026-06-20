"""OpenRouter provider — routes through OpenRouter API.

Supports all free-tier and paid models via model_registry.py.
Single provider class handles all OpenRouter models by looking up
the model ID from the registry based on provider_name passed at init.
"""

import time
import json
import logging
import random
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)

from . import AIProvider
from .model_registry import ALL_MODELS
from .json_utils import extract_json


class OpenRouterProvider(AIProvider):
    def __init__(self, provider_name: str = None):
        self.provider_name = provider_name or 'openrouter'
        from app.settings import OPENROUTER_API_KEY
        self.api_key = OPENROUTER_API_KEY
        # Look up model ID from registry
        model = ALL_MODELS.get(self.provider_name)
        if model:
            self.model = model.model_id
        elif self.provider_name == 'openrouter':
            self.model = 'openrouter/free'
        else:
            self.model = 'openrouter/auto'

    def _call_with_retry(self, messages, temperature=0.3, max_tokens=4096, max_retries=2, response_format=None):
        if not self.api_key:
            return {'error': 'OPENROUTER_API_KEY not set'}

        url = 'https://openrouter.ai/api/v1/chat/completions'
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'provider': {'sort': 'price'},
        }
        if response_format:
            payload['response_format'] = response_format
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

                if response_format:
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        pass

                parsed = extract_json(text)
                if parsed is not None:
                    return parsed
                return {'text': text}

            except urllib.error.HTTPError as e:
                body = ''
                try:
                    body = e.read().decode()
                except Exception as ex:
                    logger.debug("Failed to decode HTTP error body: %s", ex)
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
        schema = {
            'type': 'json_schema',
            'json_schema': {
                'name': 'response',
                'schema': {'type': 'object'},
            },
        }
        return self._call_with_retry(messages, temperature=0.1, max_tokens=4096, response_format=schema)

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        if not self.api_key:
            yield 'OPENROUTER_API_KEY not set'
            return
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.3),
            'max_tokens': kwargs.get('max_tokens', 4096),
            'stream': True,
            'provider': {'sort': 'price'},
        }
        data = json.dumps(payload).encode()
        try:
            req = urllib.request.Request(
                'https://openrouter.ai/api/v1/chat/completions', data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'HTTP-Referer': 'https://github.com/ComplianceHub',
                    'X-Title': 'ComplianceHub',
                    'Accept': 'text/event-stream',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                buffer = ''
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    buffer += chunk.decode()
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str == '[DONE]':
                                return
                            try:
                                ev = json.loads(data_str)
                                choices = ev.get('choices', [])
                                if choices:
                                    delta = choices[0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            yield f'[Error: {str(e)}]'
