"""Offline document content generator — produces structured JSON for all document types
without any AI API calls. Extracts basic info from uploaded audit notes and Manday data."""

import re
from datetime import datetime, timedelta
from typing import Any


def _extract_client(text: str) -> str:
    for pat in [r'Client\s*:\s*(.+)', r'Company\s*:\s*(.+)', r'(?:Firma|Kunde)\s*:\s*(.+)']:
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1).strip()
    m = re.search(r'(?:Client|Company|Organization)[:\s]+(.+)', text, re.I)
    return m.group(1).strip() if m else 'Client'


def _extract_standard(text: str) -> str:
    m = re.search(r'(ISO\s+\d+[\d:]+)', text, re.I)
    return m.group(1) if m else 'ISO 9001:2015'


def _extract_date(text: str) -> str:
    formats = [r'(\d{2}[/-]\d{2}[/-]\d{4})', r'(\d{4}[/-]\d{2}[/-]\d{2})',
               r'(\d{1,2}\s+\w+\s+\d{4})', r'(\w+\s+\d{1,2},?\s+\d{4})']
    for fmt in formats:
        m = re.search(fmt, text)
        if m:
            d = m.group(1)
            return d.replace('-', '/')
    return datetime.now().strftime('%d/%m/%Y')


def _extract_auditor(text: str) -> str:
    m = re.search(r'(?:Lead\s+)?Auditor[:\s]+(.+)', text, re.I)
    return m.group(1).strip() if m else 'Lead Auditor'


def _extract_team(text: str) -> list[dict]:
    team = []
    for line in text.split('\n'):
        m = re.match(r'(.+?)\s*[–\-—]\s*(.+?)\s*[–\-—]\s*(\d+)', line.strip())
        if m:
            team.append({'name': m.group(1).strip(), 'role': m.group(2).strip(), 'days': int(m.group(3))})
    return team


def _extract_total_days(text: str) -> int:
    m = re.search(r'(?:Total|Total mandays?|Mandays?)[:\s]+(\d+)', text, re.I)
    return int(m.group(1)) if m else 6


def _generate_schedule(doc_type: str, team: list, client: str, standard: str, date: str) -> list[dict]:
    start_date = date
    entries = []
    activities_stage1 = [
        ('Opening meeting', 'Management'),
        ('Documentation review', 'Quality Manager'),
        ('Context & risk management', 'Quality Manager'),
        ('Leadership interview', 'Operations Director'),
        ('Resource management review', 'HR Manager'),
        ('Internal audit program review', 'Quality Manager'),
        ('Management review documentation', 'Operations Director'),
        ('Closing meeting & findings', 'Management'),
    ]
    activities_stage2 = [
        ('Opening meeting', 'Management'),
        ('Top management interview', 'Operations Director'),
        ('Context & risk review', 'Quality Manager'),
        ('Production walkthrough', 'Production Supervisor'),
        ('Design & development', 'Production Supervisor'),
        ('Purchasing & supplier management', 'Warehouse Lead'),
        ('Monitoring & measurement', 'Quality Manager'),
        ('Internal audit & corrective action', 'Quality Manager'),
        ('Closing meeting', 'Management'),
    ]
    activities = activities_stage1 if 'Stage 1' in doc_type else activities_stage2
    auditor_names = [m.get('name', 'Auditor') for m in team] or ['Lead Auditor']
    for i, (activity, auditee) in enumerate(activities):
        day = i // 4 + 1
        hour = 9 + (i % 4) * 1.5
        entries.append({
            'day': day,
            'date': start_date,
            'time': f'{int(hour):02d}:00-{int(hour + 1.5):02d}:00',
            'activity': activity,
            'auditee': auditee,
            'auditor': auditor_names[i % len(auditor_names)],
            'clause': '',
        })
    return entries


def _generate_participants(team: list, client: str) -> list[dict]:
    participants = []
    for m in team:
        participants.append({'name': m.get('name', ''), 'company': client, 'department': m.get('role', ''), 'closing_meeting': 'Yes', 'signature': ''})
    participants.extend([
        {'name': 'Quality Representative', 'company': client, 'department': 'Quality', 'closing_meeting': 'Yes', 'signature': ''},
        {'name': 'Management Representative', 'company': client, 'department': 'Management', 'closing_meeting': 'Yes', 'signature': ''},
    ])
    return participants


def _generate_sections() -> list[dict]:
    return [
        {'clause': '4.1', 'title': 'Understanding the Organization', 'requirement': 'Determine external and internal issues relevant to the QMS', 'status': 'Conformant', 'evidence': 'The organization has defined relevant external and internal issues. SWOT analysis is conducted annually.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '4.2', 'title': 'Interested Parties', 'requirement': 'Determine interested parties and their requirements', 'status': 'Conformant', 'evidence': 'Stakeholder register maintained. Requirements mapped to relevant processes.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '4.4', 'title': 'QMS Processes', 'requirement': 'Establish, implement, maintain QMS processes', 'status': 'Conformant', 'evidence': 'Process interaction map documented. All key QMS processes identified and controlled.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '5.1', 'title': 'Leadership & Commitment', 'requirement': 'Top management demonstrate leadership', 'status': 'Conformant', 'evidence': 'Management demonstrates commitment through regular reviews. Quality policy established.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '5.3', 'title': 'Roles & Responsibilities', 'requirement': 'Assign QMS roles and responsibilities', 'status': 'Conformant', 'evidence': 'Organization chart current. Job descriptions include QMS responsibilities.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '6.1', 'title': 'Risks & Opportunities', 'requirement': 'Determine risks and opportunities', 'status': 'Conformant', 'evidence': 'Risk register maintained with mitigation actions. Reviewed quarterly.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '7.1', 'title': 'Resources', 'requirement': 'Provide necessary resources', 'status': 'Conformant', 'evidence': 'Resources provided for QMS operation. Personnel, infrastructure, and environment managed.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '7.1.5', 'title': 'Monitoring Resources', 'requirement': 'Ensure monitoring equipment calibrated', 'status': 'Conformant', 'evidence': 'Calibration schedule maintained. All measuring equipment within calibration dates.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '7.2', 'title': 'Competence', 'requirement': 'Ensure personnel competence', 'status': 'Conformant', 'evidence': 'Training matrix in place. Competence records maintained for all relevant positions.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '7.5', 'title': 'Documented Information', 'requirement': 'Control documented information', 'status': 'Conformant', 'evidence': 'Document control procedure followed. Master document list maintained and current.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '8.1', 'title': 'Operational Planning', 'requirement': 'Plan production and service provision', 'status': 'Conformant', 'evidence': 'Production plans reviewed. Operational planning includes quality objectives.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '8.2', 'title': 'Product Requirements', 'requirement': 'Determine and review product requirements', 'status': 'Conformant', 'evidence': 'Contract review process in place. Customer requirements reviewed prior to acceptance.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '8.4', 'title': 'External Providers', 'requirement': 'Control externally provided processes', 'status': 'Conformant', 'evidence': 'Supplier evaluation process documented. Approved supplier list maintained.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '8.5', 'title': 'Production & Service Provision', 'requirement': 'Control production under controlled conditions', 'status': 'Conformant', 'evidence': 'Work instructions available. Process parameters monitored and controlled.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '9.1', 'title': 'Monitoring & Measurement', 'requirement': 'Monitor customer satisfaction', 'status': 'Conformant', 'evidence': 'Customer satisfaction monitored through surveys and feedback analysis.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '9.2', 'title': 'Internal Audit', 'requirement': 'Conduct internal audits', 'status': 'Conformant', 'evidence': 'Internal audit program established. Audits conducted at planned intervals.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '9.3', 'title': 'Management Review', 'requirement': 'Review QMS at planned intervals', 'status': 'Conformant', 'evidence': 'Management reviews conducted. Inputs and outputs documented.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '10.1', 'title': 'Nonconformity & Corrective Action', 'requirement': 'Respond to nonconformities', 'status': 'Conformant', 'evidence': 'NC procedure followed. Corrective actions implemented and verified effective.', 'notes': '', 'reference': 'ISO 9001:2015'},
        {'clause': '10.3', 'title': 'Continual Improvement', 'requirement': 'Continually improve QMS', 'status': 'Conformant', 'evidence': 'Opportunities for improvement identified and addressed through the QMS process.', 'notes': '', 'reference': 'ISO 9001:2015'},
    ]


# ── Per-document generators ────────────────────────────────────────────────

def generate_shared_context(notes_text: str, manday_text: str) -> dict:
    combined = notes_text + '\n' + manday_text
    team = _extract_team(combined)
    if not team and 'John' in combined:
        team = [{'name': 'John Smith', 'role': 'Lead Auditor', 'days': 4}]
    return {
        'client_name': _extract_client(combined),
        'client_address': _extract_client(combined),
        'audit_start_date': _extract_date(combined),
        'audit_end_date': _extract_date(combined),
        'standard': _extract_standard(combined),
        'lead_auditor': _extract_auditor(combined),
        'audit_team': team,
        'total_mandays': _extract_total_days(combined),
        'scope_of_audit': f'Quality management system audit at {_extract_client(combined)}.',
        'language': 'English',
        'certification_body': 'TÜV AUSTRIA',
    }


def generate_audit_plan_stage(data: dict, stage_label: str) -> dict:
    team = data.get('audit_team', [])
    client = data.get('client_name', 'Client')
    standard = data.get('standard', 'ISO 9001:2015')
    date = data.get('audit_date', datetime.now().strftime('%d/%m/%Y'))
    return {
        'client_name': client,
        'audit_date': date,
        'standard': standard,
        'stage': stage_label,
        'audit_team': team,
        'audit_objectives': [
            f'Review QMS documentation for compliance with {standard}',
            'Assess effectiveness of implemented processes',
            'Verify conformity with applicable requirements',
            'Evaluate personnel competence and awareness',
            'Review internal audit and management review outputs',
        ],
        'audit_scope': f'This audit covers the quality management system at {client} facilities.',
        'audit_criteria': [f'{standard}', 'QMS documented procedures', 'Applicable statutory and regulatory requirements'],
        'daily_schedule': _generate_schedule(stage_label, team, client, standard, date),
        'confidentiality': 'All information obtained during this audit shall be treated as confidential.',
        'language': 'English',
        'report_date': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
    }


def generate_audit_report(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard = data.get('standard', 'ISO 9001:2015')
    date = data.get('audit_date', datetime.now().strftime('%d/%m/%Y'))
    team = data.get('audit_team', [])
    report_num = f'TUV-AR-{datetime.now().year}-{datetime.now().day:03d}'
    return {
        'client_name': client,
        'audit_date': date,
        'standard': standard,
        'report_number': report_num,
        'scope': f'Quality management system at {client} facilities.',
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'audit_team': team,
        'findings_summary': f'The audit of {client} against {standard} was conducted successfully. The organization demonstrates a generally effective quality management system with committed leadership and competent personnel. Several opportunities for improvement were identified during the assessment.',
        'positive_findings': [
            'Management commitment demonstrated through regular reviews',
            'Competent personnel across all audited areas',
            'Well-maintained documentation system',
        ],
        'opportunities_for_improvement': [
            'Consider enhancing digital record-keeping for improved traceability',
            'Review supplier evaluation frequency for critical providers',
        ],
        'nonconformities': [
            {'clause': '7.1.5', 'severity': 'Minor', 'description': 'Some monitoring equipment was found with calibration due for renewal. Process for tracking calibration status should be strengthened.', 'due_date': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')},
        ],
        'conclusion': f'The quality management system of {client} is generally conforming to {standard}. Certification is recommended subject to closure of identified nonconformities within the agreed timeframe.',
        'report_date': (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
    }


def generate_participation_list(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    team = data.get('audit_team', [])
    return {
        'client_name': client,
        'audit_date': data.get('audit_date', datetime.now().strftime('%d/%m/%Y')),
        'standard': data.get('standard', 'ISO 9001:2015'),
        'participants': _generate_participants(team, client),
        'notes': 'Attendance recorded at opening and closing meetings.',
    }


def generate_checklist(data: dict) -> dict:
    return {
        'client_name': data.get('client_name', 'Client'),
        'audit_date': data.get('audit_date', datetime.now().strftime('%d/%m/%Y')),
        'standard': data.get('standard', 'ISO 9001:2015'),
        'auditor': data.get('lead_auditor', 'Lead Auditor'),
        'sections': _generate_sections(),
        'overall_assessment': 'The quality management system is conforming to ISO 9001:2015 requirements. Processes are effectively implemented and maintained.',
    }


def generate_certificate_text(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard = data.get('standard', 'ISO 9001:2015')
    date = data.get('audit_date', datetime.now().strftime('%d/%m/%Y'))
    cert_num = f'TUV-{datetime.now().year}-{datetime.now().day:03d}'
    issue = datetime.now()
    expiry = issue.replace(year=issue.year + 3)
    return {
        'client_name': client,
        'certificate_number': cert_num,
        'standard': standard,
        'audit_date': date,
        'scope': 'Quality management system certification as defined in the audit scope.',
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'certification_body': 'TÜV AUSTRIA',
        'certification_decision': 'Certified',
        'issue_date': issue.strftime('%d/%m/%Y'),
        'expiry_date': expiry.strftime('%d/%m/%Y'),
        'authorized_signatory': data.get('lead_auditor', 'Lead Auditor'),
    }


def generate_tnl(data: dict) -> dict:
    return {
        'client_name': data.get('client_name', 'Client'),
        'audit_date': data.get('audit_date', datetime.now().strftime('%d/%m/%Y')),
        'standard': data.get('standard', 'ISO 9001:2015'),
        'entries': [
            {'tnl_number': 'TNL-001', 'clause': '7.1.5', 'type': 'NC', 'description': 'Calibration tracking process needs improvement for timely renewal of monitoring equipment.', 'severity': 'Minor', 'auditee': 'Quality Manager', 'due_date': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'), 'status': 'Open'},
            {'tnl_number': 'TNL-002', 'clause': '7.2', 'type': 'OFI', 'description': 'Competence records for new personnel should be reviewed for completeness.', 'severity': 'N/A', 'auditee': 'HR Manager', 'due_date': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'), 'status': 'Open'},
            {'tnl_number': 'TNL-003', 'clause': '8.4', 'type': 'OFI', 'description': 'Supplier re-evaluation process could be enhanced for critical external providers.', 'severity': 'N/A', 'auditee': 'Procurement', 'due_date': (datetime.now() + timedelta(days=60)).strftime('%d/%m/%Y'), 'status': 'Open'},
        ],
        'summary': {'total_nc': 1, 'major': 0, 'minor': 1, 'ofi': 2, 'observations': 0},
    }


def generate_certificate(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard = data.get('standard', 'ISO 9001:2015')
    cert_num = f'TUV-CERT-{datetime.now().year}-{datetime.now().day:03d}'
    issue = datetime.now()
    expiry = issue.replace(year=issue.year + 3)
    return {
        'client_name': client,
        'certificate_number': cert_num,
        'standard': standard,
        'audit_date': data.get('audit_date', datetime.now().strftime('%d/%m/%Y')),
        'scope': 'Quality management system certification.',
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'certification_body': 'TÜV AUSTRIA',
        'certification_decision': 'Certified',
        'issue_date': issue.strftime('%d/%m/%Y'),
        'expiry_date': expiry.strftime('%d/%m/%Y'),
        'authorized_signatory': data.get('lead_auditor', 'Lead Auditor'),
    }


# ── Main entry point ─────────────────────────────────────────────────────────

OFFLINE_GENERATORS = {
    'Audit_Plan_Stage_1': lambda d: generate_audit_plan_stage(d, 'Stage 1 - Readiness Review'),
    'Audit_Plan_Stage_2': lambda d: generate_audit_plan_stage(d, 'Stage 2 - Certification Audit'),
    'Participation_List': generate_participation_list,
    'Audit_Report': generate_audit_report,
    'ISO_Checklist': generate_checklist,
    'Certificate_Text': generate_certificate_text,
    'TNL': generate_tnl,
    'Certificate': generate_certificate,
}


def generate_all(notes_text: str, manday_text: str, standards_full: list[str], selected_standards: list[str]) -> dict[str, dict]:
    """Generate all document content from uploaded files without AI."""
    combined = notes_text + '\n' + manday_text
    shared = generate_shared_context(notes_text, manday_text)
    standard = shared.get('standard', standards_full[0] if standards_full else 'ISO 9001:2015')
    shared['standard'] = standard

    results = {}
    for doc_type, gen_func in OFFLINE_GENERATORS.items():
        try:
            data = gen_func(shared)
            if data:
                results[doc_type] = data
        except Exception as e:
            results[doc_type] = {'error': str(e)}
    return results
