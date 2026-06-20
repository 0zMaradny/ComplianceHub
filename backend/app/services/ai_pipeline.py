import logging

from .ai.router import generate as router_generate, extract_structured as router_extract
from app.settings import AI_QUALITY_THRESHOLD, AI_QUALITY_MAX_RETRIES
from .ai.prompts import build_prompt

_build_prompt = build_prompt  # alias for backward compatibility

logger = logging.getLogger(__name__)

QUALITY_THRESHOLD = AI_QUALITY_THRESHOLD
QUALITY_MAX_RETRIES = AI_QUALITY_MAX_RETRIES

SYSTEM_PROMPT = """=== ROLE ===
Act as Senior Lead Auditor at UKAS-accredited Certification Body (TÜV AUSTRIA). You are Track A — The Judge. Your priority is non-conformity precision over general advice. You identify findings ONLY — never offer solutions or implementation advice.

=== TASK ===
Generate complete, ready-to-issue ISO certification audit documents from the provided audit notes, manday data, and ISO clause structure. Each document must be independently usable by a certification body. Return ONLY valid JSON.

=== RULES ===
- Clause-by-clause output format: Clause | Compliance Status | Evidence Required | NC Severity
- Use formal certification body English — precise, objective, evidence-based
- Plain English — short, concrete, specific words. No leverage · no utilize · no synergies
- Every evidence/description field = 2-3 professional sentences with specific observations
- ISO terminology: conformant, non-conformant, partially conformant, OFI, not reviewed
- Dates in DD/MM/YYYY format. Numbers must match provided Manday data exactly
- Never use placeholders ([Client Name], TBD, etc.). Every field must be populated
- Never offer solutions or implementation advice — identify and describe only
- Document must be complete and ready to issue as-is

=== PUSH ===
Ship it like a real TÜV client deliverable. Think before answering (maximum reasoning)."""

SHARED_CONTEXT_PROMPT = """Extract shared facts from ISO audit docs. Return ONLY JSON.

Fields:
- client_name: string | null
- audit_date: string | null (DD/MM/YYYY)
- standard: string | null (e.g. "ISO 9001:2015")
- lead_auditor: string | null
- audit_team: list of {{name, role, days}} | []
- total_mandays: number | null
- scope_of_audit: string | null

Audit Notes:
{notes_text}

Manday Data:
{manday_text}"""


def _build_shared_prompt(notes_text, manday_text):
    return SHARED_CONTEXT_PROMPT.format(notes_text=notes_text[:15000], manday_text=manday_text[:8000])


def extract_shared_context(api_key, notes_text, manday_text):
    prompt = _build_shared_prompt(notes_text, manday_text)
    return router_extract('extract_shared_context', prompt, api_key=api_key)


def _inject_quality_feedback(prompt: str, quality_issues: list[str]) -> str:
    """Inject quality feedback into the prompt for regeneration."""
    feedback = "\n\n=== QUALITY FEEDBACK FROM PREVIOUS ATTEMPT ===\nThe previous output had these issues. Fix them:\n"
    for issue in quality_issues:
        feedback += f"- {issue}\n"
    feedback += "\nRegenerate with all issues resolved. No new issues should be introduced."
    return prompt + feedback


def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None, manday_info=None):
    prompt = build_prompt(notes_text, manday_text, standards, doc_type, shared_context, client_key=client_key, manday_info=manday_info)

    for attempt in range(QUALITY_MAX_RETRIES + 1):
        result = router_generate(doc_type, prompt, system_prompt=SYSTEM_PROMPT, api_key=api_key, client_key=client_key)

        if 'error' in result:
            return result

        # _score is a dict {'overall': int, 'fields': dict, 'pass': bool} from Autodebugger
        score_data = result.get('_score', {})
        quality_score = score_data.get('overall', 0) if isinstance(score_data, dict) else 0
        if quality_score >= QUALITY_THRESHOLD:
            return result

        logger.warning(
            'Quality score %.1f below threshold %.1f for %s (attempt %d/%d)',
            quality_score, QUALITY_THRESHOLD, doc_type,
            attempt + 1, QUALITY_MAX_RETRIES + 1
        )

        if attempt < QUALITY_MAX_RETRIES:
            # Include specific quality errors from the debugger for targeted retry
            quality_errors = result.get('_quality_errors', [])
            feedback = [f"Quality score was {quality_score}/100 (threshold: {QUALITY_THRESHOLD}/100)"]
            if quality_errors:
                feedback.extend(quality_errors[:5])  # Top 5 specific errors
            else:
                feedback.append("Improve clause accuracy, evidence detail, and format compliance")
            prompt = _inject_quality_feedback(prompt, feedback)

    result['_quality_retries'] = QUALITY_MAX_RETRIES + 1
    result['_quality_passed'] = False
    return result
