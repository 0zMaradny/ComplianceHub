"""Doc Refiner — versioned single-field regeneration for generated audit documents."""

import logging
import time

from .ai.router import generate as router_generate
from .ai_pipeline import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

REFINABLE_FIELDS = {
    'Audit_Report': ['findings_summary', 'conclusion', 'scope', 'methodology'],
    'ISO_Checklist': ['sections', 'overall_assessment'],
    'Certificate_Text': ['scope', 'certification_decision'],
    'Certificate': ['scope', 'certification_decision', 'conditions'],
    'TNL': ['summary'],
    'Audit_Plan_Stage_1': ['audit_scope', 'audit_objectives', 'audit_criteria'],
    'Audit_Plan_Stage_2': ['audit_scope', 'audit_objectives', 'audit_criteria'],
    'Participation_List': ['notes'],
}

ALL_REFINABLE = set()
for fields in REFINABLE_FIELDS.values():
    ALL_REFINABLE.update(fields)


def _seed_versions(doc_info: dict, doc_data: dict) -> None:
    """Initialize version history for all refinable fields if not present."""
    if '_versions' in doc_info:
        return
    doc_info['_versions'] = {}
    for field in ALL_REFINABLE:
        val = doc_data.get(field)
        if val is not None and val != '':
            doc_info['_versions'][field] = [
                {'value': val, 'timestamp': doc_info.get('_created_at', time.time()), 'instruction': 'original generation'}
            ]


def refine_field(
    job_data: dict,
    doc_type: str,
    field: str,
    instruction: str,
    api_key: str = '',
) -> dict:
    """Regenerate a single field in a generated document.

    Returns {'field': field, 'new_value': str, 'previous_value': str | None, 'error': str | None}
    """
    results = job_data.get('results') or {}
    doc_info = results.get(doc_type)

    if not doc_info or not isinstance(doc_info, dict):
        return {'field': field, 'error': f'Document {doc_type} not found in job'}

    doc_data = doc_info.get('_data')
    if not doc_data:
        return {'field': field, 'error': f'Data for {doc_type} not found in job'}

    if field not in REFINABLE_FIELDS.get(doc_type, []):
        return {'field': field, 'error': f'Field {field} is not refinable for {doc_type}'}

    _seed_versions(doc_info, doc_data)

    current_value = doc_data.get(field, '')
    if isinstance(current_value, list):
        current_value = '\n'.join(str(item) for item in current_value)
    elif isinstance(current_value, dict):
        import json
        current_value = json.dumps(current_value, indent=2, ensure_ascii=False)

    context = {
        'standard': doc_data.get('standard', ''),
        'client_name': doc_data.get('client_name', ''),
        'audit_date': doc_data.get('audit_date', ''),
        'doc_type': doc_type,
        'field': field,
    }
    context_str = '\n'.join(f'{k}: {v}' for k, v in context.items() if v)

    refine_prompt = f"""== FIELD REFINEMENT ==
Refine field '{field}' in {doc_type} for {context_str}
Current: {(current_value or '(empty)')[:200]}
Instruction: {instruction}

== FLOW ==
This refinement: new value → stored in _versions[{field}] with instruction + timestamp → preview shows latest version. Versions preserved for rollback.

Return ONLY {{"new_value": "..."}}. Preserve audit tone. Keep ISO clause references accurate. Do NOT change other fields or add extra keys."""

    try:
        result = router_generate(
            doc_type,
            refine_prompt,
            system_prompt=SYSTEM_PROMPT,
            api_key=api_key,
        )

        if isinstance(result, dict) and 'error' in result:
            return {'field': field, 'error': result['error']}

        raw = result.get('text', result.get('response', ''))
        import json as _json
        try:
            parsed = _json.loads(raw)
            new_value = parsed.get('new_value', raw)
        except (_json.JSONDecodeError, TypeError):
            new_value = raw.strip()

        if not new_value or new_value == current_value:
            return {'field': field, 'new_value': current_value, 'info': 'No change needed'}

        # Update doc_data with new value
        old_val = doc_data.get(field)
        doc_data[field] = new_value

        # Store version
        tim = time.time()
        versions = doc_info['_versions']
        if field not in versions:
            versions[field] = []
        versions[field].append({
            'value': new_value,
            'timestamp': tim,
            'instruction': instruction,
        })

        return {
            'field': field,
            'new_value': new_value,
            'previous_value': old_val,
        }

    except Exception as e:
        logger.exception("Field refinement failed")
        return {'field': field, 'error': str(e)}


def get_field_versions(job_data: dict, doc_type: str, field: str) -> list:
    """Return version history for a field."""
    results = job_data.get('results') or {}
    doc_info = results.get(doc_type)
    if not doc_info or not isinstance(doc_info, dict):
        return []
    versions = doc_info.get('_versions', {})
    return versions.get(field, [])


def bulk_refine(
    job_data: dict,
    doc_type: str,
    instruction: str,
    api_key: str = '',
) -> dict:
    """Refine all refinable fields for a doc type with the same instruction.

    Returns {'results': [{field, new_value, error}, ...], 'total': int, 'succeeded': int, 'failed': int}
    """
    fields = REFINABLE_FIELDS.get(doc_type, [])
    if not fields:
        return {'results': [], 'total': 0, 'succeeded': 0, 'failed': 0, 'error': f'No refinable fields for {doc_type}'}

    results = []
    succeeded = 0
    failed = 0
    for field in fields:
        r = refine_field(job_data, doc_type, field, instruction, api_key=api_key)
        results.append(r)
        if 'error' in r and r['error']:
            failed += 1
        else:
            succeeded += 1

    return {'results': results, 'total': len(fields), 'succeeded': succeeded, 'failed': failed}


def get_refinable_fields(doc_type: str) -> list[str]:
    """Return list of refinable fields for a document type."""
    return REFINABLE_FIELDS.get(doc_type, [])
