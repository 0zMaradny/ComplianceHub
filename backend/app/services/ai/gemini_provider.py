import os
import json
import re
import time
import random
from google import genai
from google.genai import types
from typing import Any

from . import AIProvider


class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        self.model = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

    def _get_client(self):
        key = self.api_key or os.environ.get('GEMINI_API_KEY', '')
        return genai.Client(api_key=key)

    def _call_with_retry(self, client, model, prompt, config, max_retries=3):
        last_error = None
        for attempt in range(max_retries):
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                raw = resp.text.strip()
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                return json.loads(raw)
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    delay = 2 ** attempt + random.uniform(0, 1)
                    time.sleep(delay)
        return {'error': last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        client = self._get_client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=kwargs.get('temperature', 0.3),
            response_mime_type='application/json',
        )
        return self._call_with_retry(client, self.model, prompt, config)

    def extract_structured(self, prompt: str, response_mime_type: str | None = 'application/json') -> dict[str, Any]:
        client = self._get_client()
        config = types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type=response_mime_type or 'application/json',
        )
        return self._call_with_retry(client, self.model, prompt, config)
