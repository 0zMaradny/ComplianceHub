import os
import json
import re
import time
from typing import Any

from huggingface_hub import InferenceClient

from . import AIProvider


_COOLDOWN_AFTER: dict[int, int] = {
    402: 60,
    429: 60,
    503: 120,
}


def _clean_json(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text)
    return text


class HFProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get('HF_API_KEY', '')
        self.model = os.environ.get('HF_MODEL', 'meta-llama/Meta-Llama-3-8B-Instruct')
        self._cooldown_until: float = 0.0
        self._consecutive_fails: int = 0
        self._last_request_time: float = 0.0

    def _in_cooldown(self) -> str | None:
        remaining = self._cooldown_until - time.time()
        if remaining > 0:
            return f'HF provider in cooldown for {remaining:.0f}s ({self._consecutive_fails} consecutive fails)'
        return None

    def _parse_status_code(self, msg: str) -> int | None:
        m = re.search(r'\b(40[23]|503)\b', msg)
        if m:
            return int(m.group())
        return None

    def _apply_cooldown(self, status_code: int | None):
        delay = _COOLDOWN_AFTER.get(status_code, 60)
        self._cooldown_until = time.time() + delay
        self._consecutive_fails += 1

    def _request(self, prompt: str, system_prompt: str | None = None, max_tokens: int = 4096, temperature: float = 0.3) -> dict:
        cooldown_msg = self._in_cooldown()
        if cooldown_msg:
            return {'error': cooldown_msg}

        key = self.api_key or os.environ.get('HF_API_KEY', '')
        if not key:
            return {'error': 'HF_API_KEY not set. Get a free token at huggingface.co/settings/tokens'}

        gap = 0.8 - (time.time() - self._last_request_time)
        if gap > 0:
            time.sleep(gap)

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
            self._last_request_time = time.time()
            self._consecutive_fails = 0
            self._cooldown_until = 0.0
            text = resp.choices[0].message.content
            return {'text': text}

        except Exception as e:
            self._last_request_time = time.time()
            msg = str(e)
            status_code = self._parse_status_code(msg)
            self._apply_cooldown(status_code)

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
