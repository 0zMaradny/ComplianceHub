import re
import json


def extract_json(text: str) -> dict | None:
    """Attempt to parse JSON from model output.

    Handles:
      - Markdown code fences (```json ... ```)
      - Leading/trailing non-JSON text
      - Multiple brace-delimited blocks (picks the first valid JSON)
    """
    text = text.strip()
    if not text:
        return None

    # Strip markdown code fences
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?\s*```$', '', text)
        text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: scan for first complete {...} block,
    # respecting string-escaped braces
    depth = 0
    start = -1
    in_str = False
    escaped = False
    for i, ch in enumerate(text):
        if in_str:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = -1

    return None
