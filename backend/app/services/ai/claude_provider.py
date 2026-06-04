import os
import json
import time
import random
from typing import Any

from . import AIProvider


class ClaudeProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('CLAUDE_API_KEY', '')
        self.model = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=3, temperature=0.3, max_tokens=4096):
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)
        last_error = None
        for attempt in range(max_retries):
            try:
                kwargs = {
                    'model': self.model,
                    'max_tokens': max_tokens,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': temperature,
                }
                if system_prompt:
                    kwargs['system'] = system_prompt

                resp = client.messages.create(**kwargs)
                raw = resp.content[0].text.strip()

                # Attempt JSON parse — Claude may wrap in fences
                if raw.startswith('```'):
                    raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
                    if raw.endswith('```'):
                        raw = raw[:-3]
                    raw = raw.strip()

                return json.loads(raw)
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = 2 ** attempt + random.uniform(0, 1)
                    time.sleep(delay)
        return {'error': last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
        )

    def extract_structured(self, prompt: str, response_mime_type: str | None = None) -> dict[str, Any]:
        return self._call_with_retry(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
        )
