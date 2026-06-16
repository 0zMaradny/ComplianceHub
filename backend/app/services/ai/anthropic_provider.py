import os
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)

from . import AIProvider
from .json_utils import extract_json


class AnthropicProvider(AIProvider):
    def __init__(self, provider_name: str | None = None):
        self.provider_name = provider_name or 'claude'
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.model = 'claude-sonnet-4-20250514'
        self.base_url = 'https://api.anthropic.com/v1'

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=2, temperature=0.3, max_tokens=8192):
        if not self.api_key:
            return {'error': 'ANTHROPIC_API_KEY not set'}
        if len(self.api_key) < 100:
            return {'error': 'ANTHROPIC_API_KEY truncated or invalid (need 100+ chars)'}
        import urllib.request, urllib.error, json

        last_error = None
        for attempt in range(max_retries):
            try:
                body = {
                    'model': self.model,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'messages': [{'role': 'user', 'content': prompt}],
                }
                if system_prompt:
                    body['system'] = system_prompt

                data = json.dumps(body).encode()
                req = urllib.request.Request(
                    f'{self.base_url}/messages',
                    data=data,
                    headers={
                        'Content-Type': 'application/json',
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                    },
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode())

                if 'error' in result:
                    last_error = result['error'].get('message', str(result['error']))
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    continue

                text = ''
                for block in result.get('content', []):
                    if block.get('type') == 'text':
                        text += block.get('text', '')

                if not text:
                    return {'error': 'No text in Claude response'}

                parsed = extract_json(text)
                if parsed is not None:
                    return parsed
                return {'text': text}

            except urllib.error.HTTPError as e:
                body = ''
                try:
                    body = e.read().decode()
                except Exception:
                    pass
                last_error = f'HTTP {e.code}: {body[:200]}'
                if e.code == 429:
                    time.sleep(30)
                    continue
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        return {'error': f'Claude failed after {max_retries} retries: {last_error}'}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 8192),
        )

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
            max_tokens=4096,
        )

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        if not self.api_key:
            yield 'ANTHROPIC_API_KEY not set'
            return
        if len(self.api_key) < 100:
            yield 'ANTHROPIC_API_KEY truncated or invalid (need 100+ chars)'
            return
        import urllib.request, urllib.error, json

        body = {
            'model': self.model,
            'max_tokens': kwargs.get('max_tokens', 8192),
            'temperature': kwargs.get('temperature', 0.3),
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': True,
        }
        if system_prompt:
            body['system'] = system_prompt

        data = json.dumps(body).encode()
        try:
            req = urllib.request.Request(
                f'{self.base_url}/messages',
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'Accept': 'text/event-stream',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
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
                            try:
                                ev = json.loads(data_str)
                                if ev.get('type') == 'content_block_delta':
                                    delta = ev.get('delta', {})
                                    if delta.get('type') == 'text_delta':
                                        text = delta.get('text', '')
                                        if text:
                                            yield text
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            yield f'[Error: {str(e)}]'
