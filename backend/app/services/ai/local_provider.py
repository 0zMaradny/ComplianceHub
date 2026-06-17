import json
import logging
import os
import time
import urllib.request
import urllib.error
from typing import Any

from . import AIProvider
from .json_utils import extract_json

logger = logging.getLogger(__name__)

LOCAL_BASE = os.environ.get('LOCAL_AI_BASE', 'http://localhost:8080')
LOCAL_TIMEOUT = int(os.environ.get('LOCAL_AI_TIMEOUT', '120'))
MAX_RETRIES = int(os.environ.get('LOCAL_AI_MAX_RETRIES', '2'))


class LocalProvider(AIProvider):
    """Provider for local llama-server (qwen-0.5b / qwen-3b) at localhost:8080."""

    def _call(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        body = json.dumps({
            'messages': messages,
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 8192),
            'stream': False,
        }).encode()

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(
                    f'{LOCAL_BASE}/v1/chat/completions',
                    data=body,
                    headers={'Content-Type': 'application/json'},
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=LOCAL_TIMEOUT) as resp:
                    data = json.loads(resp.read().decode())
                text = data['choices'][0]['message']['content']

                parsed = extract_json(text)
                if parsed is not None:
                    return parsed
                return {'text': text}

            except urllib.error.HTTPError as e:
                last_error = f'HTTP {e.code}'
                if attempt < MAX_RETRIES - 1:
                    time.sleep(1)
            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(1)

        logger.warning('Local provider failed after %d retries: %s', MAX_RETRIES, last_error)
        return {'error': last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call(prompt, system_prompt=system_prompt, **kwargs)

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        return self._call(prompt, system_prompt='Return ONLY valid JSON. Do NOT wrap in markdown code fences.', **kwargs)

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        """Non-streaming fallback — local server may not support SSE."""
        result = self._call(prompt, system_prompt=system_prompt, **kwargs)
        if 'error' in result:
            yield f'[Error: {result["error"]}]'
            return
        yield result.get('text', json.dumps(result))
