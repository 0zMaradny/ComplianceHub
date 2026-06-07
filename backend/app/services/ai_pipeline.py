import json

from .ai.router import generate as router_generate, extract_structured as router_extract
from . import clause_data
from ..config import ISO_STANDARDS, STANDARD_FAMILIES

SYSTEM_PROMPT = """You are an expert ISO Lead Auditor at TÜV AUSTRIA with 20+ years of experience certifying organizations across 13+ management system standards. You generate professional, legally-defensible audit documents based on rough audit notes and Manday calculation data.

CRITICAL RULES:
1. Return ONLY valid JSON. No markdown, no code fences, no extra text.
2. Never use placeholder text like "[Client Name]" or "TBD" — infer from the data or leave as empty string.
3. Every evidence/description field must be 2-3 professional sentences with specific observations and factual statements.
4. Use precise ISO audit terminology (conformant, non-conformant, observation, OFI).
5. Dates must be in DD/MM/YYYY format.
6. Numbers (days, team members) must match the Manday data exactly.
7. Your tone is professional, precise, and compliant with ISO 17021 certification standards.
8. Reference supporting standards in the standard family where relevant (e.g., ISO 27002:2022 controls for ISO 27001).
9. The document must be COMPLETE and ready to issue — no additional editing should be needed.
10. methodology field must contain approach, sampling, criteria, and methods sub-fields as described."""

SHARED_CONTEXT_PROMPT = """You are extracting shared facts from ISO audit documents. Analyze EVERY word of the audit notes and Manday data. Your extraction must be complete and accurate — these facts will be injected into all generated documents.

Extract ALL of the following fields (use null ONLY if truly absent):
- client_name: string | null
- audit_date: string | null (format: DD/MM/YYYY — use as single start date)
- standard: string | null (the ISO standard, e.g. "ISO 9001:2015")
- lead_auditor: string | null
- audit_team: list of {{name: string, role: string, days: number}} | empty list
- total_mandays: number | null
- scope_of_audit: string | null

Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return ONLY the JSON object."""


def _get_standard_key(standard_label: str) -> str:
    for k, v in ISO_STANDARDS.items():
        if v.startswith(standard_label.split(' —')[0]) or standard_label in v:
            return k
    key_map = {
        'ISO 9001': 'iso_9001', 'ISO 14001': 'iso_14001', 'ISO 45001': 'iso_45001',
        'ISO 27001': 'iso_27001', 'ISO 50001': 'iso_50001', 'ISO 20000': 'iso_20000',
        'ISO 22301': 'iso_22301', 'ISO 37301': 'iso_37301', 'ISO 42001': 'iso_42001',
        'ISO 30401': 'iso_30401', 'ISO 27701': 'iso_27701', 'ISO 31000': 'iso_31000',
        'ISO 10002': 'iso_10002',
    }
    for prefix, key in key_map.items():
        if prefix in standard_label:
            return key
    return 'iso_9001'


def _build_family_context(standards: list[str]) -> str:
    lines = []
    for s in standards:
        key = _get_standard_key(s)
        family = STANDARD_FAMILIES.get(key, {})
        if family:
            main = family.get('main', s)
            supporting = family.get('supporting', [])
            lines.append(f"Main standard: {main}")
            if supporting:
                lines.append(f"Supporting standards in this family: {', '.join(supporting)}")
        annex = clause_data.get_annex_a_data(key)
        if annex:
            flat = clause_data.flatten_clauses(annex)
            themes = list(set(t for _, t, _ in flat if any(kw in t for kw in ['Controls', 'Policy', 'Risk', 'Security', 'Physical', 'Technological', 'People'])))
            if themes:
                lines.append(f"Annex A control themes: {', '.join(themes)}")
    if lines:
        return '\n'.join(lines)
    return ''


def _build_shared_prompt(notes_text, manday_text):
    return SHARED_CONTEXT_PROMPT.format(notes_text=notes_text[:15000], manday_text=manday_text[:8000])


def extract_shared_context(api_key, notes_text, manday_text):
    prompt = _build_shared_prompt(notes_text, manday_text)
    return router_extract('extract_shared_context', prompt, api_key=api_key)


def _build_prompt(notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None):
    standards_str = ', '.join(standards)
    family_context = _build_family_context(standards)

    ctx_str = ''
    if shared_context:
        ctx_str = '\n== Shared Context (use these exact values) ==\n'
        ctx_str += json.dumps(shared_context, indent=2)
        ctx_str += '\n'
    if family_context:
        ctx_str += '\n== Standard Family Context ==\n' + family_context + '\n'

    # ── Client context injection ──────────────────────────────────────────
    if client_key:
        from .client_config import get_client
        client = get_client(client_key)
        if client:
            lang_note = ''
            if client.language == 'ar':
                lang_note = '\nIMPORTANT: This client requires Arabic (RTL) output. Use formal Modern Standard Arabic (MSA) for all text fields. ISO clause references and Risk IDs must remain in English.'
            elif client.language == 'bidi':
                lang_note = '\nIMPORTANT: This client requires bilingual output (Arabic primary, English secondary).'

            formula_note = ''
            if client.formulas.latent_risk or client.formulas.rating_method:
                formula_note = f'\nRisk Formulas for this client:\n- Latent Risk: {client.formulas.latent_risk or "N/A"}\n- Residual Risk: {client.formulas.residual_risk or "N/A"}\n- Rating Method: {client.formulas.rating_method or "N/A"}\n- Treatment Lookup: {client.formulas.treatment_lookup or "N/A"}\nApply these formulas in all risk-related content.'

            ctx_str += f'''
== Client Context ==
Client: {client.name}
Language: {client.language} ({'Arabic/RTL' if client.visual.rtl else 'English/LTR'})
Doc Code Prefix: {client.doc_code_prefix}
Active Standards: {', '.join(client.standards)}
{lang_note}{formula_note}
'''

    prompts = {
        'Audit_Plan_Stage_1': f"""You are preparing a Stage 1 Audit Plan (readiness review) for a TÜV AUSTRIA certification audit. The output must be COMPLETE and ready to issue — no edits needed.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these exact fields:
- client_name: string
- audit_date: string (DD/MM/YYYY)
- standard: string (full name with year)
- stage: string ("Stage 1 - Readiness Review")
- audit_team: list of {{name, role, days}}
- audit_objectives: list of 5-6 specific objectives covering: documentation review, readiness assessment, resource verification, internal audit, management review
- audit_scope: string (2-3 sentences describing exactly what will be assessed)
- audit_criteria: list of 3-4 strings
- daily_schedule: list of 8-12 entries {{day: int, date: string, time: string, activity: string (specific, with ISO clause reference), auditee: string, auditor: string, clause: string}}
- confidentiality: string
- language: string
- report_date: string (30 days after audit end)""",

        'Audit_Plan_Stage_2': f"""You are preparing a Stage 2 Audit Plan (full certification assessment) for a TÜV AUSTRIA certification audit. The output must be COMPLETE and ready to issue.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return a JSON object with these exact fields:
- client_name: string
- audit_date: string (DD/MM/YYYY)
- standard: string
- stage: string ("Stage 2 - Certification Audit")
- audit_team: list of {{name, role, days}}
- audit_objectives: list of 5-6 objectives covering: implementation verification, effectiveness evaluation, compliance confirmation, process observation, personnel interviews
- audit_scope: string
- audit_criteria: list of strings
- daily_schedule: list of 12-20 entries {{day, date, time, activity, auditee, auditor, clause}} — comprehensive, covering all shifts
- confidentiality: string
- language: string
- report_date: string""",

        'Participation_List': f"""Generate an audit Participation/Attendance List for TÜV AUSTRIA. The output must be COMPLETE and ready to issue.

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
- participants: list of 8-15 {{name, company, department, closing_meeting: "Yes"/"No", signature: ""}} — include audit team members and key client personnel
- notes: string (professional attendance notes)""",

        'Audit_Report': f"""Generate a comprehensive Audit Report for a TÜV AUSTRIA certification audit. The output must be COMPLETE with full paragraph text throughout — ready to issue with NO additional editing.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return JSON with these exact fields:
- client_name: string
- audit_date: string
- standard: string
- report_number: string (format: "TUV-AR-YYYY-NNN")
- scope: string
- lead_auditor: string
- audit_team: list of {{name, role, days}}
- findings_summary: string — 3-5 FULL PARAGRAPHS covering overall assessment, key strengths, areas of concern, and system effectiveness evaluation. Each paragraph must be 3-5 complete sentences.
- positive_findings: list of 4-6 specific strengths observed, each a full sentence
- opportunities_for_improvement: list of 3-5 specific OFIs, each referencing an ISO clause
- nonconformities: list of {{clause, severity: "Major"/"Minor", description: string (detailed, 2-3 sentences), due_date: string}}
- conclusion: string — 2-3 FULL PARAGRAPHS with certification recommendation, conditions (if any), next surveillance date
- report_date: string
- methodology: {{approach: string, sampling: string, criteria: string, methods: string}} — each a full paragraph describing the audit methodology""",

        'ISO_Checklist': f"""Generate a completed ISO Compliance Checklist based on the audit evidence. Each evidence field must be 2-3 professional sentences with specific observations. The output must be COMPLETE.

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
- auditor: string
- sections: list of {{
    clause: string (e.g. "4.1"),
    title: string,
    requirement: string,
    status: string ("Conformant" / "Partially Conformant" / "Non-Conformant" / "Not Reviewed"),
    evidence: string (2-3 professional sentences),
    notes: string,
    reference: string
  }} — include 20-40 sections covering ALL relevant clauses
- overall_assessment: string (2-3 full paragraphs)""",

        'Certificate_Text': f"""Generate certificate text for a TÜV AUSTRIA certification. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return JSON with:
- client_name: string
- certificate_number: string (format: "TUV-YYYY-NNN")
- standard: string
- audit_date: string
- scope: string
- lead_auditor: string
- certification_body: string
- certification_decision: string ("Certified" / "Conditional" / "Not Certified")
- issue_date: string (DD/MM/YYYY)
- expiry_date: string (3 years from issue)
- authorized_signatory: string""",

        'TNL': f"""Generate a Test / Nonconformity Log (TNL) for audit findings. COMPLETE output.

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
- entries: list of {{
    tnl_number: string,
    clause: string,
    type: string ("NC" / "OFI" / "OBS"),
    description: string (detailed, 2-3 sentences),
    severity: string ("Major" / "Minor" / "N/A"),
    auditee: string,
    due_date: string,
    status: string ("Open" / "Closed" / "In Progress")
  }} — include 3-8 entries
- summary: {{total_nc: int, major: int, minor: int, ofi: int, observations: int}}""",

        'Certificate': f"""Generate the final Certificate document data. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text}

Return JSON with:
- client_name: string
- certificate_number: string
- standard: string
- audit_date: string
- scope: string
- lead_auditor: string
- certification_body: string
- certification_decision: string
- issue_date: string
- expiry_date: string
- authorized_signatory: string
- conditions: list of strings (condition texts if certification decision is "Conditional", empty list otherwise)""",
    }
    return prompts.get(doc_type, prompts['Audit_Report'])


def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None):
    prompt = _build_prompt(notes_text, manday_text, standards, doc_type, shared_context, client_key=client_key)
    return router_generate(doc_type, prompt, system_prompt=SYSTEM_PROMPT, api_key=api_key)
