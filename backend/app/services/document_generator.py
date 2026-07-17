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

def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None, manday_info=None):
    prompt = build_prompt(notes_text, manday_text, standards, doc_type, shared_context, client_key=client_key, manday_info=manday_info)
    
    # Primary Generation Loop (Existing Quality Logic)
    for attempt in range(AI_QUALITY_MAX_RETRIES + 1):
        result = router_generate(doc_type, prompt, system_prompt=SYSTEM_PROMPT, api_key=api_key, client_key=client_key)
        
        if 'error' in result:
            return result
            
        # Existing Quality Score Check
        score_data = result.get('_score', {})
        quality_score = score_data.get('overall', 0) if isinstance(score_data, dict) else 0
        
        if quality_score >= AI_QUALITY_THRESHOLD:
            # NEW: Run 10-Gate Validator before returning
            content = result.get('content', '')
            validated_content, validation_result = await validate_and_heal(content, prompt, client_key or "UNKNOWN", doc_type)
            result['content'] = validated_content
            result['validator_gates'] = validation_result
            return result

        # Retry Logic for Low Quality Score
        logger.warning('Quality score %.1f below threshold (attempt %d)', quality_score, attempt + 1)
        if attempt < AI_QUALITY_MAX_RETRIES:
            prompt = f"{prompt}\n\n[QUALITY FEEDBACK]\n- Score was {quality_score}/100. Improve clause accuracy and evidence detail."

    result['_quality_retries'] = AI_QUALITY_MAX_RETRIES + 1
    return result
