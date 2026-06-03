from google import genai
from google.genai import types
import json
import re
import time
import random

SYSTEM_PROMPT = """You are an expert ISO Lead Auditor at TÜV AUSTRIA. You generate professional audit documents based on rough audit notes and Manday calculation data. You produce structured JSON output that can be rendered into Word documents.

Your tone is professional, precise, and compliant with ISO certification standards.

IMPORTANT: Return ONLY valid JSON. No markdown, no code fences, no extra text."""

SHARED_CONTEXT_PROMPT = """You are extracting shared facts from ISO audit documents. Analyze the audit notes and Manday calculation data below, then return a JSON object with every fact you can extract.

Return a JSON object with these fields (use null for missing):
- client_name: string | null
- client_address: string | null
- audit_start_date: string | null
- audit_end_date: string | null
- standard: string | null
- report_number: string | null
- lead_auditor: string | null
- audit_team: list of {{name: string, role: string, days: number}} | empty list
- total_mandays: number | null
- scope_of_audit: string | null
- audit_objectives: list of strings | empty list
- audit_criteria: list of strings | empty list
- certification_body: string ("TÜV AUSTRIA")
- language: string ("English")
- key_findings: list of strings (major issues mentioned) | empty list
- nonconformities_mentioned: list of {{clause: string, severity: string, description: string}} | empty list

Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return ONLY the JSON object."""

FEW_SHOT_EXAMPLE = """
Example of expected output quality:
For a note like "Clause 7.1 - Resources: The IT department has only 2 people for 500 users. Understaffed."
The evidence should read: "The organization's IT department is resourced with 2 personnel supporting approximately 500 users. During the audit, it was observed that the current staffing level may be insufficient to adequately manage the information security requirements of the organization. The department confirmed there is no current plan to increase headcount."
"""


def _build_shared_prompt(notes_text, manday_text):
    return SHARED_CONTEXT_PROMPT.format(notes_text=notes_text[:15000], manday_text=manday_text[:8000])


def _call_with_retry(client, model, prompt, config, max_retries=3):
    last_error = None
    for attempt in range(max_retries):
        try:
            gemini_client = genai.Client(api_key=client.api_key)
            resp = gemini_client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            raw = resp.text.strip()
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            return json.loads(raw)
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                delay = 2 ** attempt + random.uniform(0, 1)
                time.sleep(delay)
    return {'error': last_error, 'client_name': 'Client'}


def extract_shared_context(api_key, notes_text, manday_text, model='models/gemini-1.5-pro'):
    prompt = _build_shared_prompt(notes_text, manday_text)

    class Client:
        pass
    client = Client()
    client.api_key = api_key

    return _call_with_retry(
        client, model, prompt,
        types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type='application/json',
        ),
    )


def _build_prompt(notes_text, manday_text, standards, doc_type, shared_context=None):
    standards_str = ', '.join(standards)
    ctx_str = ''
    if shared_context:
        ctx_str = '\n== Shared Context (must use these exact values) ==\n'
        ctx_str += json.dumps(shared_context, indent=2)
        ctx_str += '\n'

    doc_specific = ''
    if doc_type == 'ISO_Checklist':
        doc_specific = FEW_SHOT_EXAMPLE

    prompts = {
        'Audit_Plan_Stage_1': f"""Based on the following data, generate a professional Stage 1 Audit Plan (readiness review).

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these fields:
- client_name: string
- audit_date: string
- standard: string
- stage: string ("Stage 1 - Readiness Review")
- audit_team: list of {{name, role, days}}
- audit_objectives: list of strings (focus on readiness, documentation review, site familiarization)
- audit_scope: string
- audit_criteria: list of strings
- daily_schedule: list of {{day: int, date: string, time: string, activity: string, auditee: string, auditor: string, clause: string}}
- confidentiality: string
- language: string
- report_date: string""",

        'Audit_Plan_Stage_2': f"""Based on the following data, generate a professional Stage 2 Audit Plan (full certification assessment).

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these fields:
- client_name: string
- audit_date: string
- standard: string
- stage: string ("Stage 2 - Certification Audit")
- audit_team: list of {{name, role, days}}
- audit_objectives: list of strings (focus on full implementation, effectiveness, compliance verification)
- audit_scope: string
- audit_criteria: list of strings
- daily_schedule: list of {{day: int, date: string, time: string, activity: string, auditee: string, auditor: string, clause: string}}
- confidentiality: string
- language: string
- report_date: string""",

        'Participation_List': f"""Based on the following data, generate an audit participation/attendance list.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these fields:
- client_name: string
- audit_date: string
- standard: string
- participants: list of {{
    name: string,
    company: string,
    department: string,
    closing_meeting: string ("Yes" / "No"),
    signature: string ("")
  }}
- notes: string""",

        'Audit_Report': f"""Based on the following data, generate a professional Audit Report.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these fields:
- client_name: string
- audit_date: string
- standard: string
- report_number: string
- scope: string
- audit_team: list of {{name, role, days}}
- findings_summary: string (2-3 professional paragraphs)
- positive_findings: list of strings
- opportunities_for_improvement: list of strings
- nonconformities: list of {{clause, severity, description, due_date}}
- conclusion: string
- report_date: string
- lead_auditor: string""",

        'ISO_Checklist': f"""Based on the following data, generate a completed ISO compliance checklist.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

{doc_specific}
Return a JSON object with these fields:
- client_name: string
- audit_date: string
- standard: string
- auditor: string
- sections: list of {{
    clause: string,
    title: string,
    requirement: string,
    status: string ("Conformant" / "Partially Conformant" / "Non-Conformant" / "Not Reviewed"),
    evidence: string (professional auditor wording, 1-3 sentences),
    notes: string,
    reference: string
  }}
- overall_assessment: string""",

        'Certificate_Text': f"""Based on the following data, generate certificate text content.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these fields:
- client_name: string
- certificate_number: string (e.g. "TUV-YYYY-NNN")
- standard: string
- audit_date: string
- scope: string
- lead_auditor: string
- certification_body: string ("TÜV AUSTRIA")
- certification_decision: string ("Certified" / "Conditional" / "Not Certified")
- issue_date: string
- expiry_date: string
- authorized_signatory: string""",
    }
    return prompts.get(doc_type, prompts['Audit_Report'])


def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None, model='models/gemini-1.5-pro'):
    prompt = _build_prompt(notes_text, manday_text, standards, doc_type, shared_context)

    class Client:
        pass
    client = Client()
    client.api_key = api_key

    result = _call_with_retry(
        client, model, prompt,
        types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            response_mime_type='application/json',
        ),
    )
    if 'error' not in result or result['error'] is None:
        return result
    return {'error': result.get('error')}
