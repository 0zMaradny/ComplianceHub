import logging
from .ai.router import generate as router_generate
from app.settings import AI_QUALITY_THRESHOLD, AI_QUALITY_MAX_RETRIES
from .ai.prompts import build_prompt
from .validator import validate_output  # NEW IMPORT

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """=== ROLE ===
Act as Senior Lead Auditor at UKAS-accredited Certification Body (TÜV AUSTRIA).
=== RULES ===
- No placeholders ([Client Name], TBD).
- No solutions in Track A outputs.
- Show don't tell (no meta-commentary).
"""

async def validate_and_heal(content: str, prompt: str, client_id: str, doc_type: str, max_retries: int = 2) -> tuple:
    """Run 10-gate validator. Auto-heal if gates fail."""
    validation = await validate_output(
        content=content,
        active_client=client_id,
        task_type=doc_type,
        high_stakes=(doc_type in ["soa", "audit_report"]),
        router_fn=router_generate,
    )

    if not validation["passed"] and max_retries > 0:
        heal_prompt = f"{prompt}\n\n[VALIDATOR FAILED — CORRECT THESE ISSUES]\n"
        for issue in validation['issues']:
            heal_prompt += f"- {issue}\n"
        heal_prompt += "\nRegenerate fixing ALL issues above."
        
        result = router_generate(doc_type, heal_prompt, system_prompt=SYSTEM_PROMPT)
        if 'error' not in result:
            return await validate_and_heal(result.get('content', ''), heal_prompt, client_id, doc_type, max_retries - 1)
    
    return content, validation

import json
from app.services.validator import validate_and_heal

async def generate_document(api_key, notes_text, manday_text, standards, doc_type, 
                           shared_context=None, client_key=None, manday_info=None):
    """Generate document with Autodebugger + 10-gate validator."""
    prompt = build_prompt(notes_text, manday_text, standards, doc_type, 
                         shared_context, client_key=client_key, manday_info=manday_info)

    # ─── Phase 1: Autodebugger Quality Loop (existing) ───────────────
    for attempt in range(QUALITY_MAX_RETRIES + 1):
        result = router_generate(doc_type, prompt, system_prompt=SYSTEM_PROMPT, 
                                 api_key=api_key, client_key=client_key)

        if 'error' in result:
            return result

        score_data = result.get('_score', {})
        quality_score = score_data.get('overall', 0) if isinstance(score_data, dict) else 0
        
        if quality_score >= QUALITY_THRESHOLD:
            break

        logger.warning(
            'Quality score %.1f below threshold %.1f for %s (attempt %d/%d)',
            quality_score, QUALITY_THRESHOLD, doc_type,
            attempt + 1, QUALITY_MAX_RETRIES + 1
        )

        if attempt < QUALITY_MAX_RETRIES:
            quality_errors = result.get('_quality_errors', [])
            feedback = [f"Quality score was {quality_score}/100 (threshold: {QUALITY_THRESHOLD}/100)"]
            if quality_errors:
                feedback.extend(quality_errors[:5])
            else:
                feedback.append("Improve clause accuracy, evidence detail, and format compliance")
            prompt = _inject_quality_feedback(prompt, feedback)

    # ─── Phase 2: 10-Gate Validator (NEW) ────────────────────────────
    content = result.get('content', '')
    if not content:
        content = str(result)

    validated_content, validation_result = await validate_and_heal(
        content=content,
        prompt=prompt,
        client_key=client_key,
        doc_type=doc_type,
        api_key=api_key,
        max_retries=2,
    )

    # ─── Return with validator metadata ──────────────────────────────
    result['content'] = validated_content
    result['_validator_passed'] = validation_result["passed"]
    result['_validator_issues'] = validation_result["issues"]
    result['_validator_gates'] = validation_result["gates_run"]

    if not validation_result["passed"]:
        result['_validator_warnings'] = validation_result["issues"]
        logger.warning(
            'Validator failed after retries for %s: %s',
            doc_type, validation_result["issues"][:3]
        )

    return result
