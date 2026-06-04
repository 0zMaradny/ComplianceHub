import os
import json
import time
import random
from typing import Any
from openai import OpenAI

from . import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o')

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=3, temperature=0.3):
        client = OpenAI(api_key=self.api_key)
        last_error = None
        for attempt in range(max_retries):
            try:
                messages = []
                if system_prompt:
                    messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': prompt})

                resp = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format={'type': 'json_object'},
                )
                raw = resp.choices[0].message.content.strip()
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
        return self._call_with_retry(prompt, temperature=0.1)
