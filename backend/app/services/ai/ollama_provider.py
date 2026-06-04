import os
import json
import re
import requests
from typing import Any

from . import AIProvider


class OllamaProvider(AIProvider):
    def __init__(self):
        self.base_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        self.model = os.environ.get('OLLAMA_MODEL', 'llama3')

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        try:
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'format': 'json',
            }
            if system_prompt:
                payload['system'] = system_prompt

            resp = requests.post(f'{self.base_url}/api/generate', json=payload, timeout=120)
            data = resp.json()
            raw = data.get('response', '{}').strip()
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            return json.loads(raw)
        except Exception as e:
            return {'error': str(e)}

    def extract_structured(self, prompt: str, response_mime_type: str | None = None) -> dict[str, Any]:
        return self.generate(prompt)
