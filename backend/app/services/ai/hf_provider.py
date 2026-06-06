"""HuggingFace Inference API provider — uses HF's hosted inference.
Requires a free HF token AND Inference Providers enabled at
https://huggingface.co/settings/inference-providers"""

import os
import json
import re
from typing import Any

from huggingface_hub import InferenceClient

from . import AIProvider


def _clean_json(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    return text


class HFProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('HF_API_KEY', '')
        self.model = os.environ.get('HF_MODEL', 'meta-llama/Meta-Llama-3-8B-Instruct')

    def _request(self, prompt: str, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.3) -> dict:
        key = self.api_key or os.environ.get('HF_API_KEY', '')
        if not key:
            return {'error': 'HF_API_KEY not set. Get a free token at huggingface.co/settings/tokens'}

        try:
            client = InferenceClient(token=key)
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            resp = client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = resp.choices[0].message.content
            return {'text': text}

        except Exception as e:
            msg = str(e)
            if 'model_not_supported' in msg or 'not supported by any provider' in msg:
                return {'error': (
                    f'Model "{self.model}" is not available on your HF account. '
                    'Enable Inference Providers at '
                    'https://huggingface.co/settings/inference-providers, '
                    'then try a supported model.'
                )}
            return {'error': f'HF API error: {msg[:200]}'}

    def _parse_json(self, text: str) -> dict:
        cleaned = _clean_json(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
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
