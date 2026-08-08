"""Cohere provider — optional LLM fallback via Cohere's v2 chat API.

Uses a direct HTTP call (no heavy SDK dependency) to keep the platform
offline-first and dependency-light. Activated when COHERE_API_KEY is set.
"""

import os
import time
import json
import logging
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from . import AIProvider
from .json_utils import extract_json

logger = logging.getLogger(__name__)

COHERE_API_URL = "https://api.cohere.com/v2/chat"


class CohereProvider(AIProvider):
    def __init__(self, provider_name: str = "cohere"):
        self.provider_name = provider_name
        self.api_key = os.environ.get("COHERE_API_KEY", "")
        # command-a is Cohere's latest flagship; command-r-plus is a strong fallback
        self.model = os.environ.get("COHERE_MODEL", "command-a")

    def _call_with_retry(self, prompt, system_prompt=None, max_retries=2, temperature=0.3, max_tokens=4096):
        if not self.api_key:
            return {"error": "COHERE_API_KEY not set"}
        last_error = None
        for attempt in range(max_retries):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                req = Request(
                    COHERE_API_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read().decode("utf-8"))

                # Cohere v2 returns message.content as a list of {type, text}
                content = body.get("message", {}).get("content", [])
                if isinstance(content, list):
                    text = "".join(c.get("text", "") for c in content if isinstance(c, dict))
                else:
                    text = str(content)
                text = text.strip()

                parsed = extract_json(text)
                if parsed is not None:
                    return parsed
                return {"text": text}
            except (URLError, HTTPError, json.JSONDecodeError, TimeoutError) as e:
                last_error = str(e)
                logger.warning("Cohere attempt %d failed: %s", attempt + 1, last_error)
                if attempt < max_retries - 1:
                    time.sleep(1)
        return {"error": last_error}

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt,
            system_prompt,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 4096),
        )

    def extract_structured(self, prompt: str, **kwargs) -> dict[str, Any]:
        return self._call_with_retry(
            prompt,
            system_prompt="You are a precise data extractor. Return ONLY valid JSON matching the requested schema.",
            temperature=0.1,
        )

    def generate_stream(self, prompt: str, system_prompt: str | None = None, **kwargs):
        # Cohere v2 streaming requires SSE parsing; fall back to non-streaming for simplicity.
        result = self.generate(prompt, system_prompt=system_prompt, **kwargs)
        if "error" in result:
            yield result["error"]
            return
        text = result.get("text", result.get("response", str(result)))
        yield text