import os
import json

from .ai import create_provider

SYSTEM_PROMPT = """You are an expert ISO Lead Auditor at TÜV AUSTRIA with 20+ years of experience. You generate professional, legally-defensible audit documents based on rough audit notes and Manday calculation data.

CRITICAL RULES:
1. Return ONLY valid JSON. No markdown, no code fences, no extra text.
2. Never use placeholder text like "[Client Name]" or "TBD" — infer from the data or leave as empty string.
3. Every evidence/description field must be 2-3 professional sentences with specific observations.
4. Use precise ISO audit terminology (conformant, non-conformant, observation, OFI).
5. Dates must be in DD/MM/YYYY format.
6. Numbers (days, team members) must match the Manday data exactly.
7. Your tone is professional, precise, and compliant with ISO 17021 certification standards."""

SHARED_CONTEXT_PROMPT = """You are extracting shared facts from ISO audit documents. Analyze EVERY word of the audit notes and Manday data. Your extraction must be complete and accurate — these facts will be injected into all generated documents.

Extract ALL of the following fields (use null ONLY if truly absent):
- client_name: string | null (look for company name, legal entity)
- client_address: string | null (look for address, location, site info)
- audit_start_date: string | null (format: DD/MM/YYYY)
- audit_end_date: string | null
- standard: string | null (the ISO standard, e.g. "ISO 9001:2015")
- report_number: string | null (any reference number mentioned)
- lead_auditor: string | null
- audit_team: list of {{name: string, role: string, days: number}} | empty list
- total_mandays: number | null
- scope_of_audit: string | null (full description of what was audited)
- audit_objectives: list of strings | empty list
- audit_criteria: list of strings | empty list
- certification_body: string (default "TÜV AUSTRIA")
- language: string (default "English")
- key_findings: list of strings (all major issues mentioned)
- nonconformities_mentioned: list of {{clause: string, severity: string (Major/Minor), description: string}} | empty list

Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return ONLY the JSON object."""

FEW_SHOT_EVIDENCE = """
EXAMPLE of good evidence writing:
Input note: "Clause 7.1 - Resources: IT dept has 2 people for 500 users. Understaffed."
Bad output: "Resources are insufficient." (too vague)
Good output: "The organization's IT department is resourced with 2 personnel supporting approximately 500 users. During the audit, it was observed that the current staffing level may be insufficient to adequately manage the information security requirements. The department confirmed there is no current plan to increase headcount, which presents a risk to sustained compliance."

Input note: "Clause 9.1 - Monitoring: Monthly reviews happen but no records kept."
Good output: "The organization conducts monthly management reviews of the quality management system; however, during the audit it was identified that records of these reviews (meeting minutes, attendance sheets, action item logs) are not consistently maintained. This was noted as an area for improvement to demonstrate effective monitoring and measurement of processes in accordance with clause 9.1.1."
"""


def _build_shared_prompt(notes_text, manday_text):
    return SHARED_CONTEXT_PROMPT.format(notes_text=notes_text[:15000], manday_text=manday_text[:8000])


def extract_shared_context(api_key, notes_text, manday_text):
    prompt = _build_shared_prompt(notes_text, manday_text)
    os.environ['GEMINI_API_KEY'] = api_key
    os.environ['OPENAI_API_KEY'] = api_key
    provider = create_provider()
    return provider.extract_structured(prompt)


def _build_prompt(notes_text, manday_text, standards, doc_type, shared_context=None):
    standards_str = ', '.join(standards)
    ctx_str = ''
    if shared_context:
        ctx_str = '\n== Shared Context (must use these exact values) ==\n'
        ctx_str += json.dumps(shared_context, indent=2)
        ctx_str += '\n'

    doc_specific = ''
    if doc_type == 'ISO_Checklist':
        doc_specific = FEW_SHOT_EVIDENCE

    prompts = {
        'Audit_Plan_Stage_1': f"""You are preparing a Stage 1 Audit Plan (readiness review) for a TÜV AUSTRIA certification audit.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Generate a detailed Audit Plan JSON. Every schedule entry must have realistic times and specific activities. The audit team members and days must exactly match the Manday data.

Return a JSON object with these fields:
- client_name: string
- audit_date: string (DD/MM/YYYY)
- standard: string (full name with year)
- stage: string ("Stage 1 - Readiness Review")
- audit_team: list of {{name, role, days}} — match Manday data exactly
- audit_objectives: list of 4-6 specific objectives covering: documentation review, site familiarization, readiness assessment, resource verification, internal audit review, management review
- audit_scope: string (2-3 sentences describing scope)
- audit_criteria: list of strings (the ISO clauses that will be assessed)
- daily_schedule: list of 8-12 entries {{day: int, date: string, time: string, activity: string, auditee: string, auditor: string, clause: string}} — realistic times like "09:00-10:30"
- confidentiality: string
- language: string
- report_date: string (30 days after audit end)""",

        'Audit_Plan_Stage_2': f"""You are preparing a Stage 2 Audit Plan (full certification assessment) for a TÜV AUSTRIA certification audit.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Generate a detailed Audit Plan JSON. Schedule must cover ALL relevant ISO clauses across the audit days. Team composition must match Manday data.

Return a JSON object with:
- client_name: string
- audit_date: string (DD/MM/YYYY)
- standard: string
- stage: string ("Stage 2 - Certification Audit")
- audit_team: list of {{name, role, days}}
- audit_objectives: list of 4-6 objectives covering: implementation verification, effectiveness evaluation, compliance confirmation, process observation, records verification, personnel interviews
- audit_scope: string
- audit_criteria: list of strings
- daily_schedule: list of 12-20 entries {{day, date, time, activity, auditee, auditor, clause}} — comprehensive, covering all shifts
- confidentiality: string
- language: string
- report_date: string""",

        'Participation_List': f"""Generate an audit Participation/Attendance List.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return JSON with:
- client_name: string
- audit_date: string
- standard: string
- participants: list of 6-15 {{name, company, department, closing_meeting: "Yes"/"No", signature: ""}}
  Include: audit team members as participants, key client personnel (management rep, department heads)
- notes: string (any additional attendance notes)""",

        'Audit_Report': f"""Generate a comprehensive Audit Report for a TÜV AUSTRIA certification audit.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

This report must be thorough and professional. Include specific findings with evidence. Nonconformities must reference exact ISO clause numbers.

Return JSON with:
- client_name: string
- audit_date: string
- standard: string
- report_number: string (format: "TUV-AR-YYYY-NNN")
- scope: string
- lead_auditor: string
- audit_team: list of {{name, role, days}}
- findings_summary: string (3-5 professional paragraphs — overall assessment, strengths, areas of concern, effectiveness evaluation)
- positive_findings: list of 3-8 strings (specific strengths observed)
- opportunities_for_improvement: list of 2-6 strings (specific OFIs with clause references)
- nonconformities: list of {{clause, severity: "Major"/"Minor", description: string, due_date: string}} — each with detailed description
- conclusion: string (2-3 paragraphs: certification recommendation, conditions if any, next surveillance date)
- report_date: string""",

        'ISO_Checklist': f"""Generate a completed ISO Compliance Checklist based on the audit evidence.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

{doc_specific}

For EACH relevant clause of the ISO standard(s), evaluate compliance based on the audit notes. Be specific and honest in assessments.

Return JSON with:
- client_name: string
- audit_date: string
- standard: string
- auditor: string
- sections: list of {{
    clause: string (e.g. "4.1", "7.1.1"),
    title: string (e.g. "Understanding the Organization"),
    requirement: string (full text of the clause requirement),
    status: string ("Conformant" / "Partially Conformant" / "Non-Conformant" / "Not Reviewed"),
    evidence: string (professional auditor wording, 2-3 specific sentences describing what was observed),
    notes: string (additional observations or context),
    reference: string (standard document reference)
  }} — include 15-30 sections covering all relevant clauses
- overall_assessment: string (2-3 paragraphs summarizing overall compliance level)""",

        'Certificate_Text': f"""Generate certificate text for a TÜV AUSTRIA certification.

ISO Standard(s): {standards_str}
{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return JSON with:
- client_name: string
- certificate_number: string (format: "TUV-YYYY-NNN")
- standard: string (full standard name with year)
- audit_date: string
- scope: string (detailed scope statement matching the audit)
- lead_auditor: string
- certification_body: string ("TÜV AUSTRIA")
- certification_decision: string ("Certified" / "Conditional" / "Not Certified")
  Base this on evidence: if major NCs → "Not Certified", if minor NCs with plan → "Conditional", if all conformant → "Certified"
- issue_date: string (DD/MM/YYYY)
- expiry_date: string (3 years from issue)
- authorized_signatory: string (use lead auditor name if not specified)""",
    }
    return prompts.get(doc_type, prompts['Audit_Report'])


def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None):
    prompt = _build_prompt(notes_text, manday_text, standards, doc_type, shared_context)
    os.environ['GEMINI_API_KEY'] = api_key
    os.environ['OPENAI_API_KEY'] = api_key
    provider = create_provider()
    result = provider.generate(prompt, system_prompt=SYSTEM_PROMPT)
    if 'error' not in result or result['error'] is None:
        return result
    return {'error': result.get('error')}
