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


def _build_manday_summary(manday_info: dict | None) -> str:
    if not manday_info:
        return ''
    lines = ['\n== Computed Manday Summary ==']
    if manday_info.get('audit_type'):
        lines.append(f"Audit Type: {manday_info['audit_type']}")
    if manday_info.get('total_mandays'):
        lines.append(f"Total Mandays: {manday_info['total_mandays']}")
    if manday_info.get('mandays_per_standard'):
        lines.append('Per Standard:')
        for std, days in manday_info['mandays_per_standard'].items():
            lines.append(f'  - {std}: {days} days')
    if manday_info.get('audit_team'):
        lines.append('Audit Team:')
        for m in manday_info['audit_team']:
            lines.append(f'  - {m.get("name", "?")} ({m.get("role", "?")}): {m.get("days", "?")} days')
    if manday_info.get('ims_reduction'):
        lines.append(f"IMS Reduction Applied: {manday_info['ims_reduction']}")
    if manday_info.get('employee_count'):
        lines.append(f"Employee Count: {manday_info['employee_count']}")
    if manday_info.get('site_count'):
        lines.append(f"Site Count: {manday_info['site_count']}")
    lines.append('')
    return '\n'.join(lines)


def _build_prompt(notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None, manday_info=None):
    standards_str = ', '.join(standards)
    family_context = _build_family_context(standards)
    manday_text_full = _build_manday_summary(manday_info) + '\n' + manday_text if manday_info else manday_text
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
        from ..services.client_config import get_client
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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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
{manday_text_full}

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

        'Management_Review_Minutes': f"""Generate Management Review Minutes for a TÜV AUSTRIA certification client. The review covers Clause 9.3 of the ISO standard. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with these exact fields:
- client_name: string
- review_date: string (DD/MM/YYYY)
- standard: string (full name with year)
- chairperson: string
- attendees: list of {{name, role, department}} — include 6-10 participants
- agenda_items: list of {{item, presented_by, discussion}} — 5-7 items covering: previous actions, customer feedback, audit results, process performance, NC status, risk review, resource adequacy
- decisions: list of {{decision, rationale, owner}} — 2-4 management decisions
- action_items: list of {{action, owner, due_date, status}} — 3-5 action items with realistic due dates
- review_inputs: string — 2-3 FULL PARAGRAPHS covering review inputs
- review_outputs: string — 2-3 FULL PARAGRAPHS covering resource decisions, improvement opportunities, policy changes
- next_review_date: string (12 months from review date)
- report_date: string (same as review_date)""",

        'Corrective_Action_Report': f"""Generate a Corrective Action Report (CAR) for a TÜV AUSTRIA certification audit. Covers Clause 10.1 of the ISO standard. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- car_number: string (format: "TUV-CAR-YYYY-NNN")
- standard: string
- audit_date: string (DD/MM/YYYY)
- nc_reference: string (TNL number)
- clause: string (ISO clause reference)
- severity: string ("Major" / "Minor")
- problem_description: string — detailed description of the nonconformity (2-3 sentences)
- root_cause: string — root cause analysis using 5 Whys or similar methodology (2-3 sentences)
- containment_actions: list of {{action, owner, due_date}} — 2 immediate containment actions
- corrective_actions: list of {{action, owner, due_date}} — 3 corrective actions with responsible persons
- preventive_actions: list of {{action, owner, due_date}} — 2 preventive actions to prevent recurrence
- verification_method: string — how effectiveness will be verified
- status: string ("Open" / "In Progress" / "Closed" / "Verified")
- reviewed_by: string
- closure_date: string (DD/MM/YYYY, typically 90 days from audit)""",

        'Gap_Analysis_Report': f"""Generate a Gap Analysis Report for a pre-certification assessment. Evaluates the organization's current state against ISO standard requirements. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- assessment_date: string (DD/MM/YYYY)
- standard: string
- assessor: string
- methodology: string — description of gap analysis methodology (2-3 sentences)
- sections: list of {{clause, title, requirement, status: "Conformant"/"Partially Conformant"/"Non-Conformant"/"Not Reviewed", gap_description: string (2 sentences), recommended_action: string, priority: "High"/"Medium"/"Low", target_date: string}} — include 20-40 sections covering ALL relevant clauses
- summary: {{total_clauses: int, conformant: int, partially_conformant: int, non_conformant: int, not_reviewed: int, overall_readiness: string}}
- overall_assessment: string — 2-3 FULL PARAGRAPHS with readiness recommendation""",

        'Statement_of_Applicability': f"""Generate a Statement of Applicability (SoA) for ISO 27001:2022 certification. The SoA documents which Annex A controls are applicable and the justification. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- based_on_risk_assessment: string — reference to risk assessment (1 sentence)
- controls: list of {{control_ref: string (e.g. "A.5.1"), control_title: string, applicability: "Applicable"/"Not Applicable", justification: string (2 sentences with risk context), selected_control: string, implementation_status: "Planned"/"In Progress"/"Implemented"/"Not Implemented", responsible: string}} — include ALL Annex A controls grouped by theme (A.5 Organizational: 37 controls, A.6 People: 8 controls, A.7 Physical: 14 controls, A.8 Technological: 34 controls)
- summary: {{total_controls: int, applicable: int, not_applicable: int, implemented: int, not_implemented: int}}""",

        'Business_Impact_Analysis': f"""Generate a Business Impact Analysis (BIA) for ISO 22301:2019 Business Continuity Management. Identifies critical activities, RTO/RPO/MTD, dependencies, and recovery strategies. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- assessment_date: string (DD/MM/YYYY)
- standard: string
- methodology: string — BIA methodology description (2-3 sentences)
- critical_activities: list of {{activity: string, rto: string, rpo: string, mtd: string, impact_criteria: string, dependencies: string, recovery_strategy: string, priority: string ("Critical"/"High"/"Medium"/"Low")}} — include 5-8 critical activities
- summary: {{total_activities: int, critical: int, high: int, medium: int, low: int}}
- overall_findings: string — 2-3 FULL PARAGRAPHS with BIA outcomes, key dependencies, and recommendations""",

        'Records_of_Processing_Activities': f"""Generate a Record of Processing Activities (ROPA) per ISO 27701:2025 Clause 7.6 / GDPR Article 30. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- data_controller: string — legal entity name
- data_protection_officer: string — DPO contact
- processing_activities: list of {{activity_id: string, activity_name: string, purpose: string, data_subjects: string, personal_data_categories: string, retention_period: string, cross_border_transfer: string, security_measures: string}} — include 4-6 processing activities covering HR, CRM, Marketing, Suppliers, Security, IT
- summary: {{total_activities: int, has_cross_border_transfers: string ("Yes"/"No")}}""",

        'Risk_Treatment_Plan': f"""Generate a Risk Treatment Plan for ISO 27001:2022 Clause 8.3. Documents how identified risks will be treated with selected controls and timelines. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- risk_assessment_reference: string
- risks: list of {{risk_id: string, risk_description: string, source: string, likelihood: string ("Very Low"/"Low"/"Medium"/"High"/"Very High"), impact: string ("Very Low"/"Low"/"Medium"/"High"/"Very High"), risk_level: string ("Low"/"Medium"/"High"/"Critical"), treatment_option: string ("Avoid"/"Reduce"/"Transfer"/"Accept"), treatment_details: string (2-3 sentences), selected_controls: string (Annex A references), risk_owner: string, target_date: string (DD/MM/YYYY), status: string ("Open"/"In Progress"/"Implemented"/"Closed")}} — include 6-10 risks covering technical, organizational, physical, and compliance risks
- summary: {{total_risks: int, critical: int, high: int, medium: int, low: int}}""",

        'Incident_Investigation_Report': f"""Generate an Incident Investigation Report for ISO 45001:2018 Clause 10.2. Documents incident details, root cause, corrective actions, and lessons learned. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- incident_date: string (DD/MM/YYYY)
- report_date: string (DD/MM/YYYY)
- standard: string
- incident_description: string — 3-4 sentences with date, time, location, what happened
- location: string
- incident_type: string — "Near Miss"/"First Aid"/"Medical Treatment"/"Lost Time"/"Fatality"/"Property Damage"
- severity: string — "Low"/"Medium"/"High"/"Critical"
- investigation_team: list of {{name: string, role: string}} — 3-5 team members
- root_cause: string — 2-3 paragraphs using 5 Whys or fishbone methodology
- immediate_actions: list of {{action: string, owner: string, due_date: string}} — 3-4 immediate containment actions
- corrective_actions: list of {{action: string, owner: string, due_date: string}} — 3-5 corrective actions
- lessons_learned: list of strings — 3-5 lessons
- recommendations: list of strings — 3-5 recommendations
- status: string — "Open"/"In Progress"/"Closed"
- reviewed_by: string""",

        'Internal_Audit_Program': f"""Generate an Internal Audit Program for ISO Clause 9.2 covering the annual audit schedule across the management system. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- program_year: string (e.g. "2026")
- standard: string
- audit_manager: string
- audits: list of {{audit_id: string, scope: string, audit_type: string ("Full"/"Partial"/"Follow-up"/"Special"), planned_date: string (DD/MM/YYYY), auditor: string, auditee_department: string, status: string ("Planned"/"In Progress"/"Completed"/"Cancelled"), findings_count: int}} — include 6-10 audits spread across the year covering all relevant clauses
- summary: {{total_audits: int, planned: int, in_progress: int, completed: int, cancelled: int}}""",

        'Environmental_Aspect_Register': f"""Generate an Environmental Aspect Register for ISO 14001:2015 Clause 6.1.2. Identifies environmental aspects, impacts, significance, and controls. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- methodology: string
- aspects: list of {{aspect_id: string, activity: string, aspect: string, environmental_impact: string, impact_type: string ("Positive"/"Negative"), significance: string ("Low"/"Medium"/"High"/"Critical"), control_measures: string, legal_requirement: string, evaluation: string}} — include 6-10 aspects covering operations, waste, emissions, chemicals, energy, water
- summary: {{total_aspects: int, critical: int, high: int, medium: int, low: int}}""",

        'Hazard_Identification_Register': f"""Generate a Hazard Identification and Risk Assessment Register for ISO 45001:2018 Clause 6.1.2. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- methodology: string
- hazards: list of {{hazard_id: string, activity: string, hazard: string, associated_risk: string, existing_controls: string, risk_level: string ("Low"/"Medium"/"High"/"Critical"), additional_controls: string, hierarchy_of_control: string ("Elimination"/"Substitution"/"Engineering"/"Administrative"/"PPE")}} — include 6-10 hazards covering machinery, chemicals, manual handling, electrical, fire, DSE, workplace transport
- summary: {{total_hazards: int, critical: int, high: int, medium: int, low: int}}""",

        'Energy_Review': f"""Generate an Energy Review including Energy Baseline (EnB) and Energy Performance Indicators (EnPI) for ISO 50001:2018 Clause 6.3. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- review_period: string
- methodology: string
- energy_sources: list of {{source: string, consumption: string, cost: string, trend: string ("Increasing"/"Stable"/"Decreasing"), notes: string}} — include 4-6 energy types
- significant_uses: list of {{use_id: string, equipment: string, energy_source: string, consumption: string, variables: string, enpi: string, baseline: string, current_performance: string}} — include 3-5 SEUs
- summary: {{total_energy_sources: int, total_seus: int, total_energy_cost: string}}""",

        'Compliance_Obligations_Register': f"""Generate a Compliance Obligations Register per ISO 37301:2021 / ISO 14001:2015 Clause 6.1.3. Documents all legal, regulatory, and other requirements. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- methodology: string
- obligations: list of {{obligation_id: string, obligation_type: string ("Legal"/"Regulatory"/"Contractual"/"Other"), source: string, requirement: string, applicability: string ("Full"/"Partial"/"Not Applicable"), compliance_status: string ("Compliant"/"Partially Compliant"/"Non-Compliant"/"Not Assessed"), evidence: string, due_date: string, responsible: string}} — include 6-10 obligations covering H&S, environmental, data protection, fire safety, contractual, industry standards
- summary: {{total_obligations: int, compliant: int, partially_compliant: int, non_compliant: int, not_assessed: int}}""",

        'Service_Portfolio': f"""Generate a Service Portfolio and SLA Register for ISO 20000-1:2018 Clause 7.2. Documents all services, their status, and service level agreements. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- portfolio_manager: string
- services: list of {{service_id: string, service_name: string, description: string, category: string ("Core"/"Support"/"Enabling"), status: string ("Active"/"In Development"/"Retired"/"Planned"), sla_uptime: string, sla_response_time: string, sla_resolution_time: string, service_owner: string}} — include 6-10 services covering IT support, network, applications, security, backup, cloud
- summary: {{total_services: int, active: int, in_development: int, retired: int, planned: int}}""",

        # ── ISO 20000-1 Service Management (10 new prompts) ─────────────

        'Service_Catalogue': f"""Generate a Service Catalogue for ISO 20000-1:2018 Clause 7.2. Lists all live services with features, contacts, and service hours. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- catalogue_owner: string
- catalogue_version: string
- services: list of {{service_id: string, service_name: string, description: string, service_type: string ("Business"/"Customer"/"Infrastructure"), status: string ("Live"/"Deprecated"/"Under Review"), features: string, contact: string, service_hours: string}} — include 6-10 services covering IT support, email, network, ERP, security, backup, etc.
- summary: {{total_services: int, live: int, deprecated: int, under_review: int}}""",

        'Supplier_Agreement_Register': f"""Generate a Supplier Agreement Register for ISO 20000-1:2018 Clause 8.4.2. Documents external provider agreements, performance, and renewal dates. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- register_owner: string
- agreements: list of {{agreement_id: string, supplier_name: string, service_provided: string, agreement_type: string ("Contract"/"SLA"/"Partnership"/"Letter of Agreement"), start_date: string, renewal_date: string, status: string ("Active"/"Expired"/"Under Negotiation"/"Terminated"), performance_rating: string ("Excellent"/"Satisfactory"/"Needs Improvement"), key_contacts: string}} — include 5-8 agreements
- summary: {{total_agreements: int, active: int, expired: int, under_negotiation: int, terminated: int}}""",

        'Business_Relationship_Register': f"""Generate a Business Relationship Register for ISO 20000-1:2018 Clause 8.4.3. Tracks customer accounts, satisfaction scores, complaints, and review schedules. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- relationship_manager: string
- customers: list of {{customer_id: string, customer_name: string, account_manager: string, services_used: string, satisfaction_score: string, complaints: int, last_review: string, next_review: string, status: string ("Active"/"On Hold"/"At Risk"/"Inactive")}} — include 4-6 customer accounts
- summary: {{total_customers: int, active: int, on_hold: int, at_risk: int, inactive: int, avg_satisfaction: string}}""",

        'Capacity_Management_Plan': f"""Generate a Capacity Management Plan for ISO 20000-1:2018 Clause 8.5.2. Documents infrastructure capacity, utilization, forecasts, and upgrades. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- capacity_manager: string
- review_period: string
- scope: string
- components: list of {{component_id: string, component: string, current_capacity: string, current_demand: string, utilization: string, threshold: string, forecast_demand: string, planned_upgrade: string, status: string ("Green"/"Amber"/"Red")}} — include 5-8 components covering servers, storage, network, backup, internet
- summary: {{total_components: int, green: int, amber: int, red: int}}""",

        'Change_Management_Register': f"""Generate a Change Management Register for ISO 20000-1:2018 Clause 8.6.2. Documents all changes with CAB minutes, risk/impact assessment, rollback plans. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- change_manager: string
- changes: list of {{change_id: string, title: string, description: string, change_type: string ("Standard"/"Normal"/"Emergency"), priority: string ("Low"/"Medium"/"High"/"Critical"), risk_level: string ("Low"/"Medium"/"High"), impact_assessment: string, rollback_plan: string, cab_date: string, scheduled_date: string, requestor: string, status: string ("Requested"/"Approved"/"In Progress"/"Implemented"/"Closed"/"Rolled Back")}} — include 5-8 changes
- summary: {{total_changes: int, requested: int, approved: int, in_progress: int, implemented: int, closed: int, rolled_back: int}}""",

        'Release_Deployment_Plan': f"""Generate a Release & Deployment Plan for ISO 20000-1:2018 Clause 8.6.4. Documents release schedule, deployment packages, and back-out plans. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- release_manager: string
- releases: list of {{release_id: string, release_name: string, scope: string, release_type: string ("Major"/"Minor"/"Patches"/"Emergency"), planned_date: string, deployment_window: string, rollback_procedure: string, status: string ("Planned"/"In Progress"/"Deployed"/"Rolled Back"/"Cancelled")}} — include 4-7 releases
- summary: {{total_releases: int, planned: int, in_progress: int, deployed: int, rolled_back: int, cancelled: int}}""",

        'Incident_Management_Log': f"""Generate an Incident Management Log for ISO 20000-1:2018 Clause 8.7.2. Documents major incidents, SLA breach tracking, resolution times. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- incident_manager: string
- incidents: list of {{incident_id: string, incident_summary: string, severity: string ("P1 Critical"/"P2 High"/"P3 Medium"/"P4 Low"), reported_date: string, resolved_date: string, affected_service: string, resolution: string, status: string ("New"/"In Progress"/"Resolved"/"Closed"/"Escalated")}} — include 5-8 incidents
- summary: {{total_incidents: int, critical: int, high: int, medium: int, low: int, open: int, resolved: int, avg_resolution_time: string}}""",

        'Problem_Management_Register': f"""Generate a Problem Management Register for ISO 20000-1:2018 Clause 8.7.3. Documents known errors, root cause, workarounds, and permanent fixes. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- problem_manager: string
- problems: list of {{problem_id: string, incident_refs: string, problem_summary: string, root_cause: string, workaround: string, permanent_fix: string, category: string ("Infrastructure"/"Application"/"Process"/"Security"/"Third-Party"), priority: string ("Low"/"Medium"/"High"/"Critical"), status: string ("Identified"/"Under Investigation"/"Known Error"/"Resolved"/"Closed")}} — include 4-7 problems
- summary: {{total_problems: int, critical: int, high: int, medium: int, low: int, identified: int, resolved: int}}""",

        'Service_Continuity_Plan': f"""Generate a Service Continuity Plan for ISO 20000-1:2018 Clause 8.8.2. Documents continuity of services during disruption with RTO/RPO, recovery strategies, and test results. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- plan_owner: string
- last_review_date: string
- next_review_date: string
- services: list of {{service_id: string, service_name: string, criticality: string ("Critical"/"High"/"Medium"/"Low"), rto: string, rpo: string, recovery_strategy: string, alternative_arrangements: string, last_test_date: string, test_result: string ("Pass"/"Fail"/"Partial"), status: string ("Ready"/"Needs Review"/"Remediation Required")}} — include 5-8 services
- summary: {{total_services: int, ready: int, needs_review: int, remediation: int}}""",

        'Availability_Management_Report': f"""Generate an Availability Management Report for ISO 20000-1:2018 Clause 8.8.3. Documents availability metrics, downtime analysis, MTBF, MTTR, and SLA compliance. COMPLETE output.

ISO Standard(s): {standards_str}

{ctx_str}
Audit Notes:
{notes_text}

Manday Data:
{manday_text_full}

Return JSON with:
- client_name: string
- date: string (DD/MM/YYYY)
- standard: string
- report_owner: string
- reporting_period: string
- services: list of {{service_id: string, service_name: string, target_availability: string, actual_availability: string, downtime_hours: string, number_of_outages: int, mtbf: string, mttr: string, sla_breached: string ("Yes"/"No"), notes: string}} — include 5-8 services
- summary: {{total_services: int, sla_met: int, sla_breached: int, overall_availability: string}}""",
    }
    return prompts.get(doc_type, prompts['Audit_Report'])


def generate_document(api_key, notes_text, manday_text, standards, doc_type, shared_context=None, client_key=None, manday_info=None):
    prompt = _build_prompt(notes_text, manday_text, standards, doc_type, shared_context, client_key=client_key, manday_info=manday_info)
    return router_generate(doc_type, prompt, system_prompt=SYSTEM_PROMPT, api_key=api_key, client_key=client_key)
