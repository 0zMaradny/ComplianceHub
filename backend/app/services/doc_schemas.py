"""Unified data contracts for all 8 document output types.
Both offline_generator and ai_pipeline must produce these exact shapes.
The document_generator consumes them without assumptions about missing fields."""

DOCUMENT_CONTRACTS = {

    # ── Audit Plan (shared by Stage 1 & Stage 2) ─────────────────────────
    'Audit_Plan': {
        'client_name': 'str — legal entity name',
        'audit_date': 'str DD/MM/YYYY — start date of audit',
        'standard': 'str — full standard name with year, e.g. ISO 9001:2015',
        'stage': 'str — "Stage 1 - Readiness Review" or "Stage 2 - Certification Audit"',
        'audit_team': [
            {'name': 'str', 'role': 'str', 'days': 'int'},
        ],
        'audit_objectives': ['str — 4-6 specific objectives'],
        'audit_scope': 'str — 2-3 sentence scope description',
        'audit_criteria': ['str — ISO clauses, regulatory reqs, documented procedures'],
        'daily_schedule': [
            {
                'day': 'int',
                'date': 'str DD/MM/YYYY',
                'time': 'str e.g. 09:00-10:30',
                'activity': 'str — specific audit activity',
                'auditee': 'str — person/role interviewed',
                'auditor': 'str — auditor name from team',
                'clause': 'str — ISO clause reference',
            },
        ],
        'confidentiality': 'str — confidentiality statement',
        'language': 'str e.g. English',
        'report_date': 'str DD/MM/YYYY — 30 days after audit',
    },

    # ── Participation List ──────────────────────────────────────────────
    'Participation_List': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'participants': [
            {
                'name': 'str',
                'company': 'str',
                'department': 'str',
                'closing_meeting': 'str — Yes/No',
                'signature': 'str — always empty string',
            },
        ],
        'notes': 'str — attendance notes',
    },

    # ── Audit Report ────────────────────────────────────────────────────
    'Audit_Report': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'report_number': 'str — format TUV-AR-YYYY-NNN',
        'scope': 'str',
        'lead_auditor': 'str',
        'audit_team': [
            {'name': 'str', 'role': 'str', 'days': 'int'},
        ],
        'findings_summary': 'str — 3-5 paragraphs: overall assessment, strengths, concerns, effectiveness',
        'positive_findings': ['str — 3-8 specific strengths observed'],
        'opportunities_for_improvement': ['str — 2-6 specific OFIs with clause references'],
        'nonconformities': [
            {
                'clause': 'str',
                'severity': 'str — Major/Minor',
                'description': 'str — detailed finding description',
                'due_date': 'str DD/MM/YYYY',
            },
        ],
        'conclusion': 'str — 2-3 paragraphs: recommendation, conditions, next surveillance',
        'report_date': 'str DD/MM/YYYY',
        'methodology': {
            'approach': 'str — process-based approach description',
            'sampling': 'str — sampling methodology per ISO 19011',
            'criteria': 'str — audit criteria reference',
            'methods': 'str — specific methods employed',
        },
    },

    # ── ISO Checklist ───────────────────────────────────────────────────
    'ISO_Checklist': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'auditor': 'str',
        'sections': [
            {
                'clause': 'str — e.g. 4.1',
                'title': 'str — clause title',
                'requirement': 'str — full clause requirement text',
                'status': 'str — Conformant/Partially Conformant/Non-Conformant/Not Reviewed',
                'evidence': 'str — 2-3 professional sentences with specific observations',
                'notes': 'str — additional context or observations',
                'reference': 'str — standard document reference',
            },
        ],
        'overall_assessment': 'str — 2-3 paragraphs summarizing compliance level',
    },

    # ── Certificate Text ────────────────────────────────────────────────
    'Certificate_Text': {
        'client_name': 'str',
        'certificate_number': 'str — format TUV-YYYY-NNN',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'scope': 'str',
        'lead_auditor': 'str',
        'certification_body': 'str — TÜV AUSTRIA',
        'certification_decision': 'str — Certified/Conditional/Not Certified',
        'issue_date': 'str DD/MM/YYYY',
        'expiry_date': 'str DD/MM/YYYY — 3 years from issue',
        'authorized_signatory': 'str',
    },

    # ── TNL (Test/Nonconformity Log) ────────────────────────────────────
    'TNL': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'entries': [
            {
                'tnl_number': 'str — e.g. TNL-001',
                'clause': 'str — ISO clause reference',
                'type': 'str — NC/OFI/OBS',
                'description': 'str — detailed finding description',
                'severity': 'str — Major/Minor/N/A',
                'auditee': 'str — responsible person',
                'due_date': 'str DD/MM/YYYY',
                'status': 'str — Open/Closed/In Progress',
            },
        ],
        'summary': {
            'total_nc': 'int',
            'major': 'int',
            'minor': 'int',
            'ofi': 'int',
            'observations': 'int',
        },
    },

    # ── Certificate ─────────────────────────────────────────────────────
    'Certificate': {
        'client_name': 'str',
        'certificate_number': 'str',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'scope': 'str',
        'lead_auditor': 'str',
        'certification_body': 'str — TÜV AUSTRIA',
        'certification_decision': 'str — Certified/Conditional/Not Certified',
        'issue_date': 'str DD/MM/YYYY',
        'expiry_date': 'str DD/MM/YYYY — 3 years from issue',
        'authorized_signatory': 'str',
        'conditions': ['str — conditions of certification (empty if none)'],
    },

    # ── Management Review Minutes (ISO Clause 9.3) ─────────────────────────
    'Management_Review_Minutes': {
        'client_name': 'str',
        'review_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'chairperson': 'str',
        'attendees': [
            {'name': 'str', 'role': 'str', 'department': 'str'},
        ],
        'agenda_items': [
            {'item': 'str', 'presented_by': 'str', 'discussion': 'str'},
        ],
        'decisions': [
            {'decision': 'str', 'rationale': 'str', 'owner': 'str'},
        ],
        'action_items': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str', 'status': 'str'},
        ],
        'review_inputs': 'str — 2-3 paragraphs: performance data, audit results, feedback, NC status, risk review',
        'review_outputs': 'str — 2-3 paragraphs: resource needs, improvement opportunities, policy/objective changes',
        'next_review_date': 'str DD/MM/YYYY — typically 12 months from review_date',
        'report_date': 'str DD/MM/YYYY',
    },

    # ── Corrective Action Report (ISO Clause 10.1) ────────────────────────
    'Corrective_Action_Report': {
        'client_name': 'str',
        'car_number': 'str — format TUV-CAR-YYYY-NNN',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'nc_reference': 'str — TNL reference number',
        'clause': 'str — ISO clause reference',
        'severity': 'str — Major/Minor',
        'problem_description': 'str — detailed NC description',
        'root_cause': 'str — root cause analysis (5 Whys, fishbone, etc.)',
        'containment_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'corrective_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'preventive_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'verification_method': 'str — follow-up audit, document review, on-site verification',
        'status': 'str — Open/In Progress/Closed/Verified',
        'reviewed_by': 'str',
        'closure_date': 'str DD/MM/YYYY',
    },

    # ── Gap Analysis Report (Pre-Audit Assessment) ────────────────────────
    'Gap_Analysis_Report': {
        'client_name': 'str',
        'assessment_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'assessor': 'str',
        'methodology': 'str — gap assessment methodology description',
        'sections': [
            {
                'clause': 'str — e.g. 4.1',
                'title': 'str — clause title',
                'requirement': 'str — full clause requirement text',
                'status': 'str — Conformant/Partially Conformant/Non-Conformant/Not Reviewed',
                'gap_description': 'str — description of identified gap',
                'recommended_action': 'str — action to close the gap',
                'priority': 'str — High/Medium/Low',
                'target_date': 'str DD/MM/YYYY',
            },
        ],
        'summary': {
            'total_clauses': 'int',
            'conformant': 'int',
            'partially_conformant': 'int',
            'non_conformant': 'int',
            'not_reviewed': 'int',
            'overall_readiness': 'str — percentage or readiness level',
        },
        'overall_assessment': 'str — 2-3 paragraphs summarizing gap findings and readiness recommendation',
    },

    # ── Statement of Applicability (ISO 27001 / Annex A) ──────────────────
    'Statement_of_Applicability': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'based_on_risk_assessment': 'str — reference to risk assessment report or methodology',
        'controls': [
            {
                'control_ref': 'str — e.g. A.5.1',
                'control_title': 'str — control title from Annex A',
                'applicability': 'str — Applicable/Not Applicable',
                'justification': 'str — rationale for applicability decision including risk context',
                'selected_control': 'str — control description from ISO 27002 or equivalent',
                'implementation_status': 'str — Planned/In Progress/Implemented/Not Implemented',
                'responsible': 'str — responsible person or role',
            },
        ],
        'summary': {
            'total_controls': 'int',
            'applicable': 'int',
            'not_applicable': 'int',
            'implemented': 'int',
            'not_implemented': 'int',
        },
    },
}


def build_document_data(doc_type: str, overrides: dict) -> dict:
    """Build a data dict for a document type with defaults filled in,
    merged with any overrides provided. Raises ValueError on unknown doc type."""
    contract = DOCUMENT_CONTRACTS.get(doc_type) or DOCUMENT_CONTRACTS.get({
        'Audit_Plan_Stage_1': 'Audit_Plan',
        'Audit_Plan_Stage_2': 'Audit_Plan',
    }.get(doc_type))

    if not contract:
        raise ValueError(f'Unknown document type: {doc_type}')

    result = {}
    for key, spec in contract.items():
        if key in overrides:
            result[key] = overrides[key]
        elif isinstance(spec, list) and spec:
            result[key] = []
        elif isinstance(spec, dict) and spec:
            inner = {}
            for k, v in spec.items():
                inner[k] = '' if isinstance(v, str) else ([] if isinstance(v, list) else {})
            result[key] = inner
        else:
            result[key] = ''
    result.update(overrides)
    return result
