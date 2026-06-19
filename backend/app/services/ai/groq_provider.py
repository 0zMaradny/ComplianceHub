import time
from typing import Any
from openai import OpenAI

from . import AIProvider
from .json_utils import extract_json
from app.settings import GROQ_API_KEY


class GroqProvider(AIProvider):
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = 'llama-3.3-70b-versatile'
        self.base_url = 'https://api.groq.com/openai/v1'

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=2, temperature=0.3, max_tokens=4096, response_format=None):
        if not self.api_key:
            return {'error': 'GROQ_API_KEY not set'}
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        last_error = None
        for attempt in range(max_retries):
            try:
                messages = []
                if system_prompt:
                    messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': prompt})
                kwargs = dict(model=self.model, messages=messages, max_tokens=max_tokens, temperature=temperature)
                if response_format:
                    kwargs['response_format'] = response_format
                resp = client.chat.completions.create(**kwargs)
                raw = resp.choices[0].message.content.strip()
                if response_format:
                    import json
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        pass
                parsed = extract_json(raw)
                if parsed is not None:
                    return parsed
                return {'text': raw}
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(1)
        return {'error': last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt, system_prompt,
            temperature=kwargs.get('temperature', 0.3),
        )

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        schema = {
            'type': 'json_schema',
            'json_schema': {
                'name': 'response',
                'schema': {'type': 'object'},
            },
        }
        return self._call_with_retry(
            prompt,
            system_prompt='You are a precise data extractor. Return ONLY valid JSON matching the requested schema.',
            temperature=0.1,
            response_format=schema,
        )

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        if not self.api_key:
            yield 'GROQ_API_KEY not set'
            return
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.3),
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            yield f'[Error: {str(e)}]'
