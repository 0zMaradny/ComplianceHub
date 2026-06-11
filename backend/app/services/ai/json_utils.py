import re
import json


def extract_json(text: str) -> dict | None:
    """Attempt to parse JSON from model output.

    Handles:
      - Markdown code fences (```json ... ```)
      - Leading/trailing non-JSON text
      - Partial JSON extraction via regex as fallback
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

    # Fallback: extract outermost {...} block
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        candidate = brace_match.group()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None
