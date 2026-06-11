"""AI Chat — 8-layer context-aware conversational assistant for audit documents."""

import json
import logging
from typing import Iterator

from .ai.router import generate as router_generate, generate_stream as router_generate_stream
from ..config import ISO_STANDARDS, OUTPUT_DOCUMENTS, DOC_LABELS

logger = logging.getLogger(__name__)

COMPRESS_PROMPT = """You are an ISO audit chat summarizer. Compress the conversation below into a single paragraph capturing key facts, decisions, and document references. Preserve specific ISO clause numbers, field names, and document types. Discard pleasantries. Max 200 words.

Conversation:
{text}

COMPACT summary:"""

SYSTEM_PROMPT = """You are an ISO audit assistant. Base answers strictly on context below. Do NOT invent facts. Use bullet points for lists, tables for comparisons. To refine a field return JSON: {"action":"refine","doc_type":"...","field":"...","new_value":"..."}. Otherwise plain text. Be direct — no pleasantries.

== CAPABILITIES ==
generate(doc_type) → structured JSON → DOCX+PDF | refine_field(job, doc_type, field, instruction) → versioned update | chat(message, job) → 8-layer context (project, docs, fields, history, standards, capabilities, client, files). Available: streaming, bulk-refine, diff-view, inline-edit."""  # noqa: E501

MAX_HISTORY_CHARS = 8000  # ~2000 tokens
KEEP_LAST_N = 2  # most recent messages preserved verbatim


def _estimate_tokens(text: str) -> int:
    return len(text) // 4


def _compress_history(history: list[str]) -> str:
    """Summarize old history when it exceeds the char limit.
    Keeps last KEEP_LAST_N messages verbatim, compresses the rest."""
    if not history:
        return "(no prior messages)"

    full_text = "\n".join(
        f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
        for i, msg in enumerate(history)
    )

    if _estimate_tokens(full_text) <= 2000:
        return full_text

    if len(history) <= KEEP_LAST_N * 2:
        recent = "\n".join(
            f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
            for i, msg in enumerate(history)
        )
        return recent

    old = history[:-KEEP_LAST_N * 2]
    recent = history[-KEEP_LAST_N * 2:]

    old_text = "\n".join(
        f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
        for i, msg in enumerate(old)
    )

    summary = ""
    try:
        compress_prompt_text = COMPRESS_PROMPT.format(text=old_text)
        result = router_generate(
            'chat_query', compress_prompt_text,
            system_prompt="You are a conversation summarizer. Output only the summary.",
        )
        if isinstance(result, dict) and 'error' not in result:
            summary = result.get('text', result.get('response', ''))
            if len(summary) > 500:
                summary = summary[:500]
    except Exception as e:
        logger.warning('History compression failed: %s', e)

    if not summary:
        summary = f"[{len(old) // 2} prior messages compressed]"

    recent_str = "\n".join(
        f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
        for i, msg in enumerate(recent)
    )

    return f"[COMPACT summary of earlier conversation]: {summary}\n\n---\n\n{recent_str}"


def _get_standard_label(standard_key: str) -> str:
    return ISO_STANDARDS.get(standard_key, standard_key)


def build_chat_context(job_data: dict) -> str:
    """Build an 8-layer context string from a job's progress_store entry."""
    layers = []

    results = job_data.get('results') or {}
    standards_raw = job_data.get('standards') or []
    client_key = job_data.get('client_key', '')

    # Layer 1: Project info
    client_name = 'N/A'
    for dt, info in results.items():
        if isinstance(info, dict) and info.get('_data'):
            data = info['_data']
            if data.get('client_name'):
                client_name = data['client_name']
                break
    layers.append(f"=== PROJECT INFO ===\nClient: {client_name}\nStandards: {', '.join(standards_raw)}\nClient Key: {client_key or 'none'}")

    # Layer 2: Document results overview
    doc_statuses = []
    for dt in OUTPUT_DOCUMENTS:
        info = results.get(dt, {})
        if isinstance(info, dict):
            status = '✅ generated' if info.get('path') else ('❌ failed' if 'error' in info else '⏳ pending')
            doc_statuses.append(f"  {DOC_LABELS.get(dt, dt)} ({dt}): {status}")
    layers.append("=== GENERATED DOCUMENTS ===\n" + "\n".join(doc_statuses))

    # Layer 3: Per-doc field data
    doc_fields = []
    for dt in OUTPUT_DOCUMENTS:
        info = results.get(dt, {})
        if isinstance(info, dict) and info.get('_data'):
            data = info['_data']
            field_summary_parts = []
            for key in ('scope', 'findings_summary', 'conclusion', 'overall_assessment',
                        'certification_decision', 'methodology', 'audit_scope',
                        'audit_objectives', 'audit_criteria', 'recommendations',
                        'positive_findings', 'opportunities_for_improvement'):
                val = data.get(key)
                if val:
                    if isinstance(val, str):
                        field_summary_parts.append(f"    {key}: {val[:300]}")
                    elif isinstance(val, list):
                        field_summary_parts.append(f"    {key}: {len(val)} items")
                    elif isinstance(val, dict):
                        field_summary_parts.append(f"    {key}: {json.dumps(val, ensure_ascii=False)[:200]}")
            doc_fields.append(f"  [{DOC_LABELS.get(dt, dt)}]\n" + "\n".join(field_summary_parts))
    layers.append("=== PER-DOCUMENT FIELDS ===\n" + "\n".join(doc_fields))

    # Layer 4: ISO knowledge
    standards_info = []
    for s in standards_raw:
        label = _get_standard_label(s)
        standards_info.append(f"  {s}: {label}")
    layers.append("=== ISO STANDARDS ===\n" + "\n".join(standards_info))

    # Layer 5: System capabilities
    layers.append("""=== SYSTEM CAPABILITIES ===
- Generate audit documents (Audit Plan, Audit Report, ISO Checklist, Certificate, TNL, etc.)
- Refine individual fields in generated documents (rewrite findings, conclusions, scope)
- Answer questions about generated document content
- Provide ISO standard clause references and audit terminology explanations
- To refine a field: specify the document type, field name, and desired change""")

    # Layer 6: Chat history placeholder — injected by chat_with_ai
    layers.append("=== CHAT HISTORY ===\n{chat_history}")

    # Layer 7: Client config
    layers.append(f"=== CLIENT CONFIG ===\nClient Key: {client_key or 'none'}")

    # Layer 8: Uploaded files summary
    notes_summary = job_data.get('notes_summary', '')
    manday_summary = job_data.get('manday_summary', '')
    if notes_summary or manday_summary:
        layers.append(f"=== UPLOADED FILES ===\nAudit Notes: {notes_summary[:500]}\nManday Data: {manday_summary[:500]}")

    return "\n\n".join(layers)


def chat_with_ai(message: str, context: str, history: list | None = None) -> dict:
    """Send a chat message to the AI and return the response."""
    if history is None:
        history = []

    history_str = _compress_history(history)
    context_with_history = context.replace("{chat_history}", history_str)

    prompt = f"""{context_with_history}

=== USER MESSAGE ===
{message}"""

    try:
        result = router_generate(
            'chat_query', prompt,
            system_prompt=SYSTEM_PROMPT,
        )

        if isinstance(result, dict) and 'error' in result:
            return {'response': f'AI service error: {result["error"]}', 'error': True}

        text = result.get('text', result.get('response', str(result)))
        return {'response': text, 'error': False}

    except Exception as e:
        logger.exception("Chat AI call failed")
        return {'response': f'Chat service error: {str(e)}', 'error': True}


def chat_stream(message: str, context: str, history: list | None = None) -> Iterator[str]:
    """Stream a chat response token by token. Yields str tokens."""
    if history is None:
        history = []

    history_str = _compress_history(history)
    context_with_history = context.replace("{chat_history}", history_str)

    prompt = f"""{context_with_history}

=== USER MESSAGE ===
{message}"""

    try:
        yield from router_generate_stream(
            'chat_query', prompt,
            system_prompt=SYSTEM_PROMPT,
        )
    except Exception as e:
        logger.exception("Chat stream failed")
        yield f'[Error: {str(e)}]'
