import os
import json
import time
from typing import Any
from openai import OpenAI

from . import AIProvider

PAID_MODEL = 'mistralai/mistral-small-3.1-24b-instruct'
FREE_MODEL = 'openrouter/free'


class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.base_url = 'https://openrouter.ai/api/v1'

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=1, temperature=0.3, max_tokens=4096):
        if not self.api_key:
            return {'error': 'OPENROUTER_API_KEY not set'}
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        last_error = None

        for model in [PAID_MODEL, FREE_MODEL]:
            for attempt in range(max_retries):
                try:
                    messages = []
                    if system_prompt:
                        messages.append({'role': 'system', 'content': system_prompt})
                    messages.append({'role': 'user', 'content': prompt})
                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        extra_headers={
                            'HTTP-Referer': 'https://github.com/ComplianceHub',
                            'X-Title': 'ComplianceHub',
                        },
                    )
                    raw = resp.choices[0].message.content.strip()
                    return json.loads(raw)
                except Exception as e:
                    last_error = f'{model}: {e}'
                    if attempt < max_retries - 1:
                        time.sleep(1)
        return {'error': last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
        )

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
        )
