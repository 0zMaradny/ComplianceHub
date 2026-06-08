"""Offline document content generator — produces structured JSON for all document types
without any AI API calls. Uses the clause_data module for professional, standard-specific
evidence and compliance statuses. Outputs match the unified data contracts in doc_schemas.py."""

import random
import re
from datetime import datetime, timedelta

from . import clause_data


# Seed is not fixed — different results each run


STANDARD_LABEL_MAP = {
    'iso_9001': 'ISO 9001:2015',
    'iso_14001': 'ISO 14001:2015',
    'iso_45001': 'ISO 45001:2018',
    'iso_27001': 'ISO 27001:2022',
    'iso_50001': 'ISO 50001:2018',
    'iso_20000': 'ISO 20000-1:2018',
    'iso_22301': 'ISO 22301:2019',
    'iso_37301': 'ISO 37301:2021',
    'iso_42001': 'ISO 42001:2023',
    'iso_30401': 'ISO 30401:2018',
    'iso_27701': 'ISO 27701:2025',
    'iso_31000': 'ISO 31000:2018',
    'iso_10002': 'ISO 10002:2018',
}


FAMILY_LABEL_MAP = {
    'iso_9001': 'Quality Management',
    'iso_14001': 'Environmental Management',
    'iso_45001': 'Occupational Health & Safety',
    'iso_50001': 'Energy Management',
    'iso_27001': 'Information Security Management',
    'iso_20000': 'Service Management',
    'iso_22301': 'Business Continuity Management',
    'iso_37301': 'Compliance Management',
    'iso_42001': 'Artificial Intelligence Management',
    'iso_30401': 'Knowledge Management',
    'iso_27701': 'Privacy Information Management',
    'iso_31000': 'Risk Management',
    'iso_10002': 'Complaints Handling',
}


def _key_for_standard(standard_label: str) -> str:
    for k, v in STANDARD_LABEL_MAP.items():
        if v in standard_label or k in standard_label.lower():
            return k
    for prefix, key in [('ISO 9001', 'iso_9001'), ('ISO 14001', 'iso_14001'),
                         ('ISO 45001', 'iso_45001'), ('ISO 27001', 'iso_27001'),
                         ('ISO 50001', 'iso_50001'), ('ISO 20000', 'iso_20000'),
                         ('ISO 22301', 'iso_22301'), ('ISO 37301', 'iso_37301'),
                         ('ISO 42001', 'iso_42001'), ('ISO 30401', 'iso_30401'),
                         ('ISO 27701', 'iso_27701'), ('ISO 31000', 'iso_31000'),
                         ('ISO 10002', 'iso_10002')]:
        if prefix in standard_label:
            return key
    return 'iso_9001'


def _extract_client(text: str) -> str:
    for pat in [r'Client\s*:\s*(.+)', r'Company\s*:\s*(.+)', r'(?:Firma|Kunde)\s*:\s*(.+)',
                r'Customer\s*:\s*(.+)', r'Organization\s*:\s*(.+)']:
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1).strip()
    return 'Client'


def _extract_standard(text: str) -> str:
    m = re.search(r'(ISO\s+\d+[\d:]+\d{4})', text, re.I)
    if m:
        return m.group(1)
    m = re.search(r'(ISO\s+\d+)', text, re.I)
    return (m.group(1) + ':2015') if m else 'ISO 9001:2015'


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


TODAY = datetime.now()
TODAY_STR = TODAY.strftime('%d/%m/%Y')

_CONCLUSIONS = {
    'compliant': (
        'The management system has been demonstrated to be effectively implemented and maintained. '
        'The organization shows commitment to continual improvement and conformity to all applicable requirements. '
        'Based on the audit evidence gathered, certification is recommended without conditions.'
    ),
    'conditional': (
        'The management system is generally conforming; however, certain nonconformities were identified '
        'that require corrective action before full certification can be confirmed. '
        'Certification is recommended subject to the closure of all identified nonconformities '
        'within the agreed timeframe and verification of effectiveness.'
    ),
    'not_compliant': (
        'Significant nonconformities were identified that indicate the management system '
        'has not been effectively implemented or maintained in key areas. '
        'Certification cannot be recommended at this time. A follow-up audit is required '
        'to verify implementation of corrective actions before reconsideration.'
    ),
}


def _build_checklist_sections(standard_key: str) -> list[dict]:
    clauses = clause_data.get_clause_data(standard_key)
    annex = clause_data.get_annex_a_data(standard_key)
    supporting = clause_data.get_supporting_evidence(standard_key)
    sections = []
    statuses = ['Conformant', 'Conformant', 'Conformant', 'Partially Conformant', 'Conformant']
    standard_label = STANDARD_LABEL_MAP.get(standard_key, 'ISO 9001:2015')

    if isinstance(clauses, dict) and 'sections' in clauses:
        for sid, sinfo in clauses['sections'].items():
            title = sinfo.get('title', '')
            evidence_list = sinfo.get('evidence', [])
            evidence = evidence_list[0] if evidence_list else f'Reviewed framework area: {title}. The organization demonstrates adequate implementation of this principle.'
            status = random.choice(statuses)
            sections.append({
                'clause': sid,
                'title': title,
                'requirement': title,
                'status': status,
                'evidence': evidence,
                'notes': '',
                'reference': standard_label,
            })
            sub = sinfo.get('sub_sections', {})
            for sub_id, sub_info in sub.items():
                sub_title = sub_info if isinstance(sub_info, str) else sub_info.get('title', '')
                if sub_title:
                    sub_evidence = f'Reviewed framework element: {sub_title}. The organization has incorporated this principle into its risk management approach.'
                    if isinstance(sub_info, dict):
                        ev = sub_info.get('evidence', [])
                        if ev:
                            sub_evidence = ev[0]
                    sections.append({
                        'clause': sub_id,
                        'title': sub_title,
                        'requirement': sub_title,
                        'status': random.choice(statuses),
                        'evidence': sub_evidence,
                        'notes': '',
                        'reference': standard_label,
                    })
        return sections

    flat = clause_data.flatten_clauses(clauses)
    for cid, title, depth in flat:
        if not title:
            continue
        if depth == 0 and cid in ('1', '2', '3'):
            continue
        evidence_list = clause_data.get_evidence_for_clause(clauses, cid)
        evidence = evidence_list[0] if evidence_list else f'Clause {cid} ({title}) was reviewed through documentation analysis and personnel interviews. The implemented approach is consistent with the standard requirements.'
        status = random.choice(statuses)

        supporting_refs = []
        if supporting and random.random() < 0.4:
            sup_key = random.choice(list(supporting.keys()))
            supporting_refs.append(f'{sup_key}: {supporting[sup_key]}')
        reference = standard_label
        if supporting_refs:
            reference += ' + ' + '; '.join(supporting_refs)

        sections.append({
            'clause': cid,
            'title': title,
            'requirement': f'The organization shall {title.lower()} as defined in {standard_label} Clause {cid}.',
            'status': status,
            'evidence': evidence,
            'notes': '',
            'reference': reference,
        })

    for aid, ainfo in annex.items():
        flat_a = clause_data.flatten_clauses({aid: ainfo})
        for cid, title, _ in flat_a:
            if not title:
                continue
            evidence_list = clause_data.get_evidence_for_clause(annex, cid)
            evidence = evidence_list[0] if evidence_list else f'Annex A control {cid} ({title}) was assessed. The implemented controls are commensurate with the identified risks.'
            status = random.choice(statuses)
            sections.append({
                'clause': cid,
                'title': title,
                'requirement': f'Annex A control: {title} as per {standard_label} {cid}.',
                'status': status,
                'evidence': evidence,
                'notes': '',
                'reference': f'{standard_label} Annex A',
            })

    return sections


def _generate_schedule(doc_type: str, team: list, client: str, standard_label: str, date: str) -> list[dict]:
    standard_key = _key_for_standard(standard_label)
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')
    entries = []
    auditor_names = [m.get('name', 'Lead Auditor') for m in team] or ['Lead Auditor']

    if 'Stage 1' in doc_type:
        activities = [
            (1, 'Opening meeting — introduction of audit team, confirmation of logistics and scope', 'Management', '4.1'),
            (1, 'Documentation review — system manual, documented information, policy alignment', 'Management Representative', '4.4, 5.2'),
            (1, f'Context analysis — external and internal issues, interested party requirements for {family}', 'Management Representative', '4.1, 4.2'),
            (1, 'Risk and opportunity management — assessment methodology and register review', 'Quality Manager', '6.1'),
            (1, 'Leadership interview — strategic direction, policy deployment, resource commitment', 'Operations Director', '5.1'),
            (2, 'Competence and awareness — training matrix, competence records, awareness programmes', 'HR Manager', '7.2, 7.3'),
            (2, 'Operational planning — process interaction mapping, control criteria, outsourced processes', 'Department Manager', '8.1'),
            (2, 'Internal audit programme — audit schedule, auditor competence, findings closure', 'Quality Manager', '9.2'),
            (2, 'Management review documentation — review inputs, outputs, action item tracking', 'Operations Director', '9.3'),
            (2, 'Closing meeting — preliminary findings summary, readiness recommendation', 'Management', ''),
        ]
    else:
        activities = [
            (1, 'Opening meeting — introduction of audit team, confirmation of audit plan and objectives', 'Management', '4.1'),
            (1, f'Top management interview — strategic context, policy, objectives for {family}', 'Operations Director', '5.1, 5.2'),
            (1, 'Context, interested parties, and risk review — updates since Stage 1', 'Management Representative', '4.1, 4.2'),
            (1, 'Process walkthrough — operational planning and control, process performance indicators', 'Production Supervisor', '8.1'),
            (2, 'Resource management — infrastructure, environment, monitoring and measurement resources', 'HR Manager', '7.1'),
            (2, 'Supplier and external provider management — evaluation, re-evaluation, performance monitoring', 'Procurement Manager', '8.4'),
            (2, 'Operations — detailed review of Clause 8 processes including traceability and control of nonconforming outputs', 'Department Manager', '8.5, 8.6, 8.7'),
            (2, 'Monitoring and measurement — customer satisfaction, process performance, product/service conformity', 'Quality Manager', '9.1'),
            (3, 'Internal audit review — audit reports, findings, corrective action effectiveness', 'Quality Manager', '9.2'),
            (3, 'Management review inputs and outputs — performance analysis and improvement decisions', 'Operations Director', '9.3'),
            (3, 'Nonconformity and corrective action — root cause analysis, action effectiveness verification', 'Quality Manager', '10.1'),
            (3, 'Closing meeting — findings presentation, certification recommendation', 'Management', ''),
        ]

    for i, (day, activity, auditee, clause) in enumerate(activities):
        hour = 9 + (i % 4) * 1.5
        entries.append({
            'day': day,
            'date': date,
            'time': f'{int(hour):02d}:00-{int(hour + 1.5):02d}:00',
            'activity': activity,
            'auditee': auditee,
            'auditor': auditor_names[i % len(auditor_names)],
            'clause': clause,
        })
    return entries


def _generate_participants(team: list, client: str) -> list[dict]:
    participants = []
    for m in team:
        participants.append({'name': m.get('name', ''), 'company': client, 'department': m.get('role', ''), 'closing_meeting': 'Yes', 'signature': ''})
    participants.extend([
        {'name': 'Quality Management Representative', 'company': client, 'department': 'Quality Management', 'closing_meeting': 'Yes', 'signature': ''},
        {'name': 'Operations Director', 'company': client, 'department': 'Operations', 'closing_meeting': 'Yes', 'signature': ''},
        {'name': 'Plant Manager', 'company': client, 'department': 'Production', 'closing_meeting': 'Yes', 'signature': ''},
        {'name': 'HR Manager', 'company': client, 'department': 'Human Resources', 'closing_meeting': 'No', 'signature': ''},
    ])
    return participants


def _generate_methodology(standard_label: str) -> dict:
    return {
        'approach': (
            'The audit was conducted in accordance with ISO 19011:2018 guidelines for auditing management systems. '
            'A process-based approach was employed, following the Plan-Do-Check-Act (PDCA) cycle across all relevant '
            f'clauses of {standard_label}. The audit examined the sequence and interaction of processes, '
            'their performance indicators, and the allocation of resources to achieve planned results.'
        ),
        'sampling': (
            'Audit evidence was gathered through interviews with personnel at all relevant levels of the organization, '
            'observation of operational processes and work practices, and comprehensive review of documented information '
            'including policies, procedures, operational records, and performance reports. Sampling techniques were applied '
            'in accordance with ISO 19011:2018 guidelines, taking into account the complexity, risk profile, and '
            'significance of each process. Sample sizes were determined based on the number of employees, '
            'the diversity of activities, and the volume of records maintained.'
        ),
        'criteria': (
            f'The audit criteria consisted of the requirements of {standard_label}, the organization\'s own '
            'management system documentation (including policies, procedures, and work instructions), '
            'applicable statutory and regulatory requirements, and relevant standards referenced in the standard family. '
            'The audit team assessed conformity against these criteria using defined acceptance criteria for each clause.'
        ),
        'methods': (
            'Methods employed included: (1) document review and records analysis of policies, procedures, '
            'and operational documentation; (2) observation of operational activities and work practices '
            'at the organization\'s premises; (3) interviews with top management, process owners, '
            'and operational personnel at various levels; (4) verification of resources, infrastructure, '
            'and work environment; (5) traceability audits from records back to source documentation; '
            'and (6) verification of corrective and preventive actions from previous audits.'
        ),
    }


def generate_shared_context(notes_text: str, manday_text: str, manday_info: dict | None = None) -> dict:
    combined = notes_text + '\n' + manday_text

    if manday_info:
        total_days = manday_info.get('total_mandays', 6)
        team_list = manday_info.get('team_composition', [])
        team = [
            {'name': f'{t["role"]} #{i+1}', 'role': t['role'], 'days': t['days']}
            for i, t in enumerate(team_list)
            for _ in range(t.get('count', 1))
        ]
    else:
        team = _extract_team(combined)
        if not team and 'John' in combined:
            team = [{'name': 'John Smith', 'role': 'Lead Auditor', 'days': 4}]
        total_days = _extract_total_days(combined)

    std_label = _extract_standard(combined)
    std_key = _key_for_standard(std_label)
    client = _extract_client(combined)
    date = _extract_date(combined)
    auditor = _extract_auditor(combined)
    family = FAMILY_LABEL_MAP.get(std_key, 'Management System')

    return {
        'client_name': client,
        'audit_date': date,
        'standard': std_label,
        'standard_key': std_key,
        'lead_auditor': auditor,
        'audit_team': team,
        'total_mandays': total_days,
        'audit_scope': f'This audit covers the {family} system at {client} facilities as defined in the scope of certification.',
        'scope': f'{family} system at {client} facilities.',
        'certification_body': 'TÜV AUSTRIA',
        'language': 'English',
        'report_number': f'TUV-AR-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}',
        'certificate_number': f'TUV-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}',
    }


def generate_audit_plan_stage(data: dict, stage_label: str) -> dict:
    team = data.get('audit_team', [])
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    date = data.get('audit_date', TODAY_STR)
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')

    return {
        'client_name': client,
        'audit_date': date,
        'standard': standard_label,
        'stage': stage_label,
        'audit_team': team,
        'audit_objectives': [
            f'Review documented information and system design for conformity with {standard_label} requirements',
            f'Assess the effectiveness of implemented {family} processes in achieving planned outcomes',
            'Verify conformity with applicable statutory, regulatory, and contractual requirements',
            'Evaluate personnel competence and awareness of relevant policies and procedures',
            f'Assess the organization\'s internal audit process and management review outputs for {family}',
            'Identify opportunities for improvement in the management system',
        ],
        'audit_scope': data.get('audit_scope', f'This audit covers the {family} system at {client} facilities.'),
        'audit_criteria': [
            f'{standard_label}',
            'Management system documented policies, procedures, and work instructions',
            'Applicable statutory and regulatory requirements',
            'Relevant supporting standards in the standard family',
        ],
        'daily_schedule': _generate_schedule(stage_label, team, client, standard_label, date),
        'confidentiality': 'All information obtained during this audit shall be treated as strictly confidential and used solely for the purpose of certification.',
        'language': data.get('language', 'English'),
        'report_date': (TODAY + timedelta(days=30)).strftime('%d/%m/%Y'),
    }


def generate_audit_report(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    date = data.get('audit_date', TODAY_STR)
    team = data.get('audit_team', [])
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')

    sections = _build_checklist_sections(standard_key)

    nonconformities = []
    for s in sections:
        if s['status'] == 'Non-Conformant' or (s['status'] == 'Partially Conformant' and random.random() < 0.3):
            nonconformities.append({
                'clause': s['clause'],
                'severity': 'Minor' if s['status'] == 'Partially Conformant' else random.choice(['Minor', 'Minor', 'Major']),
                'description': (
                    f'{s["title"]}: {s["evidence"]} '
                    f'During the audit, it was observed that the current implementation does not fully meet the '
                    f'requirements of {standard_label} Clause {s["clause"]}. '
                    'The organization is required to implement corrective actions and demonstrate effectiveness within the agreed timeframe.'
                ),
                'due_date': (TODAY + timedelta(days=30)).strftime('%d/%m/%Y'),
            })

    has_major = any(nc['severity'] == 'Major' for nc in nonconformities)
    has_any_nc = len(nonconformities) > 0

    if has_major:
        conclusion_key = 'not_compliant'
        decision = 'Not Certified'
    elif has_any_nc:
        conclusion_key = 'conditional'
        decision = 'Conditional'
    else:
        conclusion_key = 'compliant'
        decision = 'Certified'

    return {
        'client_name': client,
        'audit_date': date,
        'standard': standard_label,
        'report_number': data.get('report_number', f'TUV-AR-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}'),
        'scope': data.get('scope', f'{family} system at {client} facilities.'),
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'audit_team': team,
        'findings_summary': (
            f'The audit of {client} against {standard_label} was conducted over {data.get("total_mandays", 6)} audit days '
            f'by a team of {len(team)} qualified auditors. The organization demonstrates a generally effective {family} system '
            f'with committed leadership and competent personnel across the audited functions. '
            f'A total of {len(nonconformities)} nonconformit{"y" if len(nonconformities) == 1 else "ies"} '
            f'and {len(nonconformities) + random.randint(1, 3)} opportunities for improvement were identified. '
            f'The overall level of system maturity indicates that the management system is '
            f'{ "fully" if decision == "Certified" else "partially" } capable of achieving its intended outcomes. '
            f'Key strengths include management commitment, competent personnel, and a well-structured documentation system. '
            f'Areas requiring attention include the effectiveness of corrective action processes and the robustness of '
            f'performance monitoring in certain operational areas.'
        ),
        'positive_findings': [
            'Top management demonstrates active commitment through regular participation in management reviews and resource allocation for the management system',
            'Personnel across all levels display appropriate competence and awareness of their roles and responsibilities within the management system',
            'The documented information system is well-structured, with effective document control and record retention practices observed',
            'Internal audit programme is effectively implemented with competent auditors and thorough audit reports',
            'The organization has established effective processes for identifying and addressing risks and opportunities',
        ],
        'opportunities_for_improvement': [
            'Consider enhancing the root cause analysis methodology for recurring nonconformities to prevent recurrence more effectively (Clause 10.1)',
            'Review the frequency and methodology of supplier re-evaluation, particularly for critical external providers (Clause 8.4)',
            'Strengthen the traceability of management review action items to ensure timely closure and effectiveness verification (Clause 9.3)',
            'Consider implementing a more systematic approach to capturing and sharing lessons learned across the organization (Clause 7.4)',
        ],
        'nonconformities': nonconformities[:5],
        'conclusion': _CONCLUSIONS[conclusion_key],
        'report_date': (TODAY + timedelta(days=7)).strftime('%d/%m/%Y'),
        'methodology': _generate_methodology(standard_label),
        'certification_decision': decision,
    }


def generate_participation_list(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    team = data.get('audit_team', [])
    return {
        'client_name': client,
        'audit_date': data.get('audit_date', TODAY_STR),
        'standard': data.get('standard', 'ISO 9001:2015'),
        'participants': _generate_participants(team, client),
        'notes': (
            'Attendance was recorded at both the opening and closing meetings. '
            'All participants listed above were present for the scheduled audit activities. '
            'The audit team confirms that appropriate personnel were available for interview throughout the audit duration.'
        ),
    }


def generate_checklist(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    sections = _build_checklist_sections(standard_key)
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')

    compliant_count = sum(1 for s in sections if s['status'] == 'Conformant')
    total = len(sections) if sections else 1
    percent = int(compliant_count / total * 100)
    pc_count = sum(1 for s in sections if s['status'] == 'Partially Conformant')
    nc_count = sum(1 for s in sections if s['status'] == 'Non-Conformant')

    if percent >= 90:
        quality = 'fully mature'
    elif percent >= 70:
        quality = 'substantially implemented'
    else:
        quality = 'partially implemented'

    return {
        'client_name': data.get('client_name', 'Client'),
        'audit_date': data.get('audit_date', TODAY_STR),
        'standard': standard_label,
        'auditor': data.get('lead_auditor', 'Lead Auditor'),
        'sections': sections,
        'overall_assessment': (
            f'The {family} system at {data.get("client_name", "the organization")} demonstrates approximately {percent}% '
            f'conformity with {standard_label} requirements across {total} audited clauses. '
            f'The system is assessed as {quality}, with {compliant_count} clauses conformant, '
            f'{pc_count} partially conformant, and {nc_count} non-conformant. '
            f'The organization\'s management demonstrates commitment to the system, and the foundational processes '
            f'are effectively established. Key areas for improvement include addressing the identified nonconformities '
            f'and partially conformant clauses through targeted corrective actions and systematic root cause analysis. '
            f'Overall, the management system provides a sound framework for achieving the organization\'s objectives '
            f'and meeting applicable requirements.'
        ),
    }


def generate_certificate_text(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    date = data.get('audit_date', TODAY_STR)
    cert_num = data.get('certificate_number', f'TUV-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}')
    issue = TODAY
    expiry = issue.replace(year=issue.year + 3)

    return {
        'client_name': client,
        'certificate_number': cert_num,
        'standard': standard_label,
        'audit_date': date,
        'scope': data.get('scope', f'Management system certification for {standard_label} as defined in the audit scope statement.'),
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'certification_body': 'TÜV AUSTRIA',
        'certification_decision': data.get('certification_decision', 'Certified'),
        'issue_date': issue.strftime('%d/%m/%Y'),
        'expiry_date': expiry.strftime('%d/%m/%Y'),
        'authorized_signatory': data.get('lead_auditor', 'Lead Auditor'),
    }


def generate_tnl(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    sections = _build_checklist_sections(standard_key)

    entries = []
    nc_count, major, minor, ofi_count = 0, 0, 0, 0

    for i, s in enumerate(sections):
        if len(entries) >= 5:
            break
        if s['status'] in ('Non-Conformant', 'Partially Conformant'):
            typ = 'NC' if s['status'] == 'Non-Conformant' else random.choice(['NC', 'OFI'])
            severity = 'Minor'
            if typ == 'NC':
                nc_count += 1
                severity = random.choice(['Minor', 'Minor', 'Major'])
                if severity == 'Major':
                    major += 1
                else:
                    minor += 1
            else:
                ofi_count += 1

            entries.append({
                'tnl_number': f'TNL-{i+1:03d}',
                'clause': s['clause'],
                'type': typ,
                'description': (
                    f'{s["title"]}: {s["evidence"]} '
                    f'The current implementation does not fully satisfy the requirements of {standard_label} Clause {s["clause"]}. '
                    f'Corrective actions shall be implemented and verified for effectiveness.'
                ),
                'severity': severity if typ == 'NC' else 'N/A',
                'auditee': random.choice(['Quality Manager', 'Operations Manager', 'Department Manager']),
                'due_date': (TODAY + timedelta(days=30 if random.random() < 0.7 else 60)).strftime('%d/%m/%Y'),
                'status': 'Open',
            })

    return {
        'client_name': data.get('client_name', 'Client'),
        'audit_date': data.get('audit_date', TODAY_STR),
        'standard': standard_label,
        'entries': entries,
        'summary': {
            'total_nc': nc_count,
            'major': major,
            'minor': minor,
            'ofi': ofi_count,
            'observations': 0,
        },
    }


def generate_certificate(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    cert_num = data.get('certificate_number', f'TUV-CERT-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}')
    issue = TODAY
    expiry = issue.replace(year=issue.year + 3)
    decision = data.get('certification_decision', 'Certified')

    return {
        'client_name': client,
        'certificate_number': cert_num,
        'standard': standard_label,
        'audit_date': data.get('audit_date', TODAY_STR),
        'scope': data.get('scope', 'Management system certification as defined in the audit scope statement.'),
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'certification_body': 'TÜV AUSTRIA',
        'certification_decision': decision,
        'issue_date': issue.strftime('%d/%m/%Y'),
        'expiry_date': expiry.strftime('%d/%m/%Y'),
        'authorized_signatory': data.get('lead_auditor', 'Lead Auditor'),
        'conditions': (
            ['Closure of all identified nonconformities within 60 days and verification of corrective action effectiveness by the audit team.']
            if decision == 'Conditional'
            else []
        ),
    }


def generate_management_review_minutes(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', TODAY_STR)
    team = data.get('audit_team', [])
    lead = data.get('lead_auditor', 'Lead Auditor')

    attendees = []
    for m in team:
        attendees.append({'name': m.get('name', ''), 'role': m.get('role', ''), 'department': m.get('role', '')})
    attendees += [
        {'name': 'Quality Management Representative', 'role': 'QMR', 'department': 'Quality Management'},
        {'name': 'Operations Director', 'role': 'Director', 'department': 'Operations'},
    ]

    review_date = date
    today_dt = datetime.strptime(review_date, '%d/%m/%Y') if '/' in review_date else TODAY
    next_review = (today_dt.replace(year=today_dt.year + 1)).strftime('%d/%m/%Y')

    return {
        'client_name': client,
        'review_date': review_date,
        'standard': standard_label,
        'chairperson': lead,
        'attendees': attendees,
        'agenda_items': [
            {'item': 'Review of previous management review action items and status', 'presented_by': 'Quality Manager', 'discussion': 'Reviewed status of all open action items from previous management review. Majority are closed with verified effectiveness.'},
            {'item': f'Customer feedback and satisfaction analysis for {family}', 'presented_by': 'Operations Director', 'discussion': 'Customer satisfaction index remains stable at 87%. Key feedback themes include response time and service quality. No systemic issues identified.'},
            {'item': f'Audit results — internal and external audits for {standard_label}', 'presented_by': 'Quality Manager', 'discussion': 'Internal audit completed with 3 minor NCs and 5 OFIs. External audit readiness assessed as adequate. All audit findings are being addressed through the corrective action process.'},
            {'item': 'Process performance and product/service conformity', 'presented_by': 'Department Managers', 'discussion': 'Overall process performance KPIs are within targets. Nonconforming output rate reduced by 12% compared to previous period.'},
            {'item': f'Status of nonconformities and corrective actions for {standard_label}', 'presented_by': 'Quality Manager', 'discussion': 'All open NCs have corrective action plans. Trend analysis shows reduction in repeat NCs, indicating effective root cause analysis.'},
            {'item': f'Risk and opportunity review for {family}', 'presented_by': 'Operations Director', 'discussion': 'Risk register reviewed and updated. One new risk identified related to supply chain. Mitigation plan developed and assigned.'},
            {'item': 'Resource adequacy and infrastructure planning', 'presented_by': 'HR Manager', 'discussion': 'Resource requirements assessed for upcoming period. Training budget approved. Infrastructure upgrades planned for Q3.'},
        ],
        'decisions': [
            {'decision': 'Continue with current quality policy and objectives — no changes required', 'rationale': 'Current policy remains appropriate for organizational context and strategic direction', 'owner': 'CEO'},
            {'decision': 'Approve CAPEX for monitoring equipment upgrade', 'rationale': 'Existing equipment approaching end of calibration validity. Upgrade will improve measurement accuracy.', 'owner': 'Operations Director'},
            {'decision': 'Conduct additional supplier audit for top 3 critical suppliers', 'rationale': 'Supply chain risk identified. On-site audit will verify supplier capability and quality system effectiveness.', 'owner': 'Quality Manager'},
        ],
        'action_items': [
            {'action': 'Complete CAPEX approval and initiate equipment procurement', 'owner': 'Operations Director', 'due_date': (today_dt + timedelta(days=30)).strftime('%d/%m/%Y'), 'status': 'Open'},
            {'action': 'Schedule and conduct supplier audits for top 3 critical suppliers', 'owner': 'Quality Manager', 'due_date': (today_dt + timedelta(days=60)).strftime('%d/%m/%Y'), 'status': 'Open'},
            {'action': 'Update risk register with new supply chain risk and mitigation plan', 'owner': 'Risk Manager', 'due_date': (today_dt + timedelta(days=14)).strftime('%d/%m/%Y'), 'status': 'Open'},
            {'action': 'Distribute updated quality policy to all departments with acknowledgement', 'owner': 'HR Manager', 'due_date': (today_dt + timedelta(days=21)).strftime('%d/%m/%Y'), 'status': 'In Progress'},
            {'action': 'Update training plan to include new equipment operation training', 'owner': 'HR Manager', 'due_date': (today_dt + timedelta(days=45)).strftime('%d/%m/%Y'), 'status': 'Open'},
        ],
        'review_inputs': (
            f'The management review considered comprehensive inputs across all relevant {family} processes. '
            f'Customer satisfaction data indicates stable performance with an index of 87%. '
            f'Audit results from the most recent internal audit identified 3 minor nonconformities and 5 opportunities for improvement, '
            f'all of which are being addressed through established corrective action processes. '
            f'Process performance metrics show that key process indicators are meeting their defined targets, '
            f'with nonconforming output reduced by 12% compared to the previous review period. '
            f'The status of nonconformities and corrective actions indicates effective handling of identified issues, '
            f'with trend analysis showing a reduction in repeat nonconformities. '
            f'Risk and opportunity management remains effective with regular review and updating of the risk register.'
        ),
        'review_outputs': (
            'Based on the review of inputs, the management system is assessed as effective and achieving its intended outcomes. '
            'The following decisions and actions have been established: approval of CAPEX for monitoring equipment upgrade, '
            'supplier audits for critical external providers, and continuation of the current quality policy and objectives. '
            'Resource needs have been identified and will be addressed through the approved budget allocation. '
            'Opportunities for improvement include enhancing the root cause analysis methodology and strengthening supplier evaluation processes. '
            'The management system continues to be appropriate, adequate, and effective for the organization\'s context and strategic direction.'
        ),
        'next_review_date': next_review,
        'report_date': review_date,
    }


def generate_corrective_action_report(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', TODAY_STR)

    issues = generate_tnl(data)
    entries = issues.get('entries', [])
    nc_entry = entries[0] if entries else {
        'clause': '10.1',
        'severity': 'Minor',
        'tnl_number': 'TNL-001',
    }

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else TODAY

    severity = nc_entry.get('severity', 'Minor')
    clause = nc_entry.get('clause', '10.1')

    return {
        'client_name': client,
        'car_number': f'TUV-CAR-{TODAY.year}-{TODAY.timetuple().tm_yday:03d}',
        'standard': standard_label,
        'audit_date': date,
        'nc_reference': nc_entry.get('tnl_number', 'TNL-001'),
        'clause': clause,
        'severity': severity,
        'problem_description': (
            f'During the audit conducted on {date} at {client}, a nonconformity was identified '
            f'against {standard_label} Clause {clause}. '
            f'The organization has not fully implemented the requirements of this clause, '
            f'as evidenced by incomplete documentation and insufficient evidence of process effectiveness. '
            f'This finding was communicated to management during the closing meeting.'
        ),
        'root_cause': (
            'Root cause analysis was conducted using the 5 Whys methodology. '
            'The primary root cause was identified as inadequate training and awareness of personnel '
            'regarding the specific requirements of this clause. '
            'Secondary contributing factors include insufficient supervisory oversight '
            'and lack of clear documented procedures. '
            'No systemic issues were identified that would indicate a broader management system failure.'
        ),
        'containment_actions': [
            {'action': 'Immediate containment: Implement short-term controls to address the identified gap and prevent recurrence before the next operation cycle', 'owner': 'Quality Manager', 'due_date': (today_dt + timedelta(days=7)).strftime('%d/%m/%Y')},
            {'action': 'Notify all relevant personnel of the finding and required immediate actions', 'owner': 'Department Manager', 'due_date': (today_dt + timedelta(days=2)).strftime('%d/%m/%Y')},
        ],
        'corrective_actions': [
            {'action': 'Revise and update documented procedures for Clause ' + clause + ' to ensure full alignment with standard requirements', 'owner': 'Quality Manager', 'due_date': (today_dt + timedelta(days=30)).strftime('%d/%m/%Y')},
            {'action': 'Conduct targeted training for all affected personnel on the revised procedures', 'owner': 'HR Manager', 'due_date': (today_dt + timedelta(days=45)).strftime('%d/%m/%Y')},
            {'action': 'Implement monitoring mechanism to verify ongoing compliance with the updated procedures', 'owner': 'Quality Manager', 'due_date': (today_dt + timedelta(days=60)).strftime('%d/%m/%Y')},
        ],
        'preventive_actions': [
            {'action': 'Review training programme to ensure all relevant clauses are adequately covered in initial and refresher training', 'owner': 'HR Manager', 'due_date': (today_dt + timedelta(days=60)).strftime('%d/%m/%Y')},
            {'action': 'Include verification of this clause in the next scheduled internal audit to confirm effectiveness of implemented actions', 'owner': 'Internal Audit Manager', 'due_date': (today_dt + timedelta(days=90)).strftime('%d/%m/%Y')},
        ],
        'verification_method': 'Follow-up on-site verification during next surveillance audit. Review of updated documentation, training records, and process performance data.',
        'status': 'Open',
        'reviewed_by': data.get('lead_auditor', 'Lead Auditor'),
        'closure_date': (today_dt + timedelta(days=90)).strftime('%d/%m/%Y'),
    }


def generate_gap_analysis_report(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', TODAY_STR)

    sections = clause_data.get_gap_checklist_data(standard_key)

    total = len(sections)
    c_count = sum(1 for s in sections if s['status'] == 'Conformant')
    pc_count = sum(1 for s in sections if s['status'] == 'Partially Conformant')
    nc_count = sum(1 for s in sections if s['status'] == 'Non-Conformant')
    nr_count = sum(1 for s in sections if s['status'] == 'Not Reviewed')

    if total > 0:
        readiness_pct = int((c_count + pc_count * 0.5) / total * 100)
    else:
        readiness_pct = 0

    overall = (
        f'The gap analysis of {client} against {standard_label} assessed {total} clauses and requirements. '
        f'Of these, {c_count} are conformant, {pc_count} are partially conformant, '
        f'{nc_count} are non-conformant, and {nr_count} were not reviewed. '
        f'The overall readiness level is estimated at {readiness_pct}%. '
        f'The organization has established foundational management system elements including documented policies, '
        f'defined responsibilities, and basic operational controls. '
        f'Key areas requiring attention include fully implementing the requirements for identified partially conformant '
        f'and non-conformant clauses, developing documented procedures where gaps exist, '
        f'and ensuring that evidence of implementation is maintained. '
        f'A structured action plan with assigned responsibilities and target dates should be developed '
        f'to address the identified gaps prior to the Stage 1 certification audit.'
    )

    return {
        'client_name': client,
        'assessment_date': date,
        'standard': standard_label,
        'assessor': data.get('lead_auditor', 'Lead Auditor'),
        'methodology': (
            'The gap analysis was conducted through review of available documentation, '
            'interviews with key personnel, and assessment of current practices against the requirements '
            f'of {standard_label}. Each clause was evaluated for conformance and assigned a status '
            'based on the level of implementation and evidence available. '
            'Recommendations are provided for addressing identified gaps.'
        ),
        'sections': sections,
        'summary': {
            'total_clauses': total,
            'conformant': c_count,
            'partially_conformant': pc_count,
            'non_conformant': nc_count,
            'not_reviewed': nr_count,
            'overall_readiness': f'{readiness_pct}%',
        },
        'overall_assessment': overall,
    }


def generate_statement_of_applicability(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', TODAY_STR)

    annex = clause_data.get_annex_a_data(standard_key)
    controls_list = []

    if annex and isinstance(annex, dict):
        for theme_key, theme_val in annex.items():
            if isinstance(theme_val, dict):
                for ctrl_key, ctrl_val in theme_val.items():
                    if ctrl_key == 'title':
                        continue
                    if isinstance(ctrl_val, dict):
                        ctrl_title = ctrl_val.get('title', ctrl_key)
                    else:
                        ctrl_title = str(ctrl_val)
                    applicable = random.choice(['Applicable', 'Applicable', 'Applicable', 'Not Applicable'])
                    justification = (
                        f'Based on the information security risk assessment and the organization\'s context, '
                        f'this control is {applicable.lower()} for the scope of the ISMS. '
                        f'The risk treatment plan identifies this control as '
                        f'{"necessary" if applicable == "Applicable" else "not required"} '
                        f'to address identified risks to an acceptable level.'
                    )
                    impl_status = random.choice(['Implemented', 'Implemented', 'In Progress', 'Planned', 'Not Implemented'])
                    controls_list.append({
                        'control_ref': ctrl_key,
                        'control_title': ctrl_title,
                        'applicability': applicable,
                        'justification': justification,
                        'selected_control': ctrl_title,
                        'implementation_status': impl_status,
                        'responsible': 'Information Security Manager',
                    })

    total = len(controls_list)
    applicable = sum(1 for c in controls_list if c['applicability'] == 'Applicable')
    na = total - applicable
    implemented = sum(1 for c in controls_list if c['implementation_status'] == 'Implemented')
    not_implemented = sum(1 for c in controls_list if c['implementation_status'] in ('Not Implemented', 'Planned'))

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'based_on_risk_assessment': f'Information security risk assessment conducted as part of the ISMS implementation for {standard_label}. Risk assessment methodology follows ISO 27005:2022 guidelines.',
        'controls': controls_list,
        'summary': {
            'total_controls': total,
            'applicable': applicable,
            'not_applicable': na,
            'implemented': implemented,
            'not_implemented': not_implemented,
        },
    }


OFFLINE_GENERATORS = {
    'Audit_Plan_Stage_1': lambda d: generate_audit_plan_stage(d, 'Stage 1 - Readiness Review'),
    'Audit_Plan_Stage_2': lambda d: generate_audit_plan_stage(d, 'Stage 2 - Certification Audit'),
    'Participation_List': generate_participation_list,
    'Audit_Report': generate_audit_report,
    'ISO_Checklist': generate_checklist,
    'Certificate_Text': generate_certificate_text,
    'TNL': generate_tnl,
    'Certificate': generate_certificate,
    'Management_Review_Minutes': generate_management_review_minutes,
    'Corrective_Action_Report': generate_corrective_action_report,
    'Gap_Analysis_Report': generate_gap_analysis_report,
    'Statement_of_Applicability': generate_statement_of_applicability,
}


def generate_all(notes_text: str, manday_text: str, standards_full: list[str], selected_standards: list[str], manday_info: dict | None = None) -> dict[str, dict]:
    shared = generate_shared_context(notes_text, manday_text, manday_info)
    standard_label = shared.get('standard', standards_full[0] if standards_full else 'ISO 9001:2015')
    shared['standard'] = standard_label

    results = {}
    for doc_type, gen_func in OFFLINE_GENERATORS.items():
        try:
            data = gen_func(shared)
            if data:
                results[doc_type] = data
        except Exception as e:
            results[doc_type] = {'error': str(e)}
    return results
