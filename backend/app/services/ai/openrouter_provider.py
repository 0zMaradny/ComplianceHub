"""OpenRouter provider — uses OpenRouter API for free-tier and paid models.
Single provider class that routes to different models based on provider name.
Supports: openrouter/auto, openrouter/fusion, openai/gpt-oss-120b:free, etc."""

import os
import json
import time
import random
import urllib.request
import urllib.error
from typing import Any

from . import AIProvider

# Model mapping: provider_name -> OpenRouter model ID
MODEL_MAP = {
    'fusion': 'openrouter/fusion',
    'auto': 'openrouter/auto',
    'gpt_oss_120b': 'openai/gpt-oss-120b:free',
}


class OpenRouterProvider(AIProvider):
    def __init__(self, provider_name: str = 'fusion'):
        self.provider_name = provider_name
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.model = MODEL_MAP.get(provider_name, 'openrouter/fusion')
        self.timeout = int(os.environ.get('OPENROUTER_TIMEOUT', '120'))

    def _call_with_retry(self, messages, temperature=0.3, max_tokens=4096, max_retries=3):
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
                    },
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    result = json.loads(resp.read().decode())

                if 'error' in result:
                    last_error = result['error'].get('message', str(result['error']))
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt + random.uniform(0, 1)
                        time.sleep(delay)
                    continue

                text = ''
                try:
                    text = result['choices'][0]['message']['content'].strip()
                except (KeyError, IndexError):
                    return {'error': 'No response from OpenRouter'}

                # Try JSON parse
                if text.startswith('```'):
                    text = text.split('\n', 1)[1] if '\n' in text else text[3:]
                    if text.endswith('```'):
                        text = text[:-3]
                    text = text.strip()

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {'text': text}

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
