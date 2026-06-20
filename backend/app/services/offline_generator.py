"""Offline document content generator — produces structured JSON for all document types
without any AI API calls. Uses the clause_data module for professional, standard-specific
evidence and compliance statuses. Outputs match the unified data contracts in doc_schemas.py."""

import logging
import random
import re
from datetime import datetime, timedelta

from . import clause_data

logger = logging.getLogger(__name__)


def _deterministic_choice(options: list, seed_val: str) -> str:
    """Deterministic choice based on a seed string. Same seed always returns same result."""
    h = hash(seed_val) % len(options)
    return options[h]


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
    'iso_13485': 'ISO 13485:2016',
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
    'iso_13485': 'Medical Devices Quality Management',
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
                         ('ISO 13485', 'iso_13485'),
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


def _extract_ncs(text: str) -> list[dict]:
    ncs = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(
            r'(?:#?\d+\s*)?(?:NC|Non-Conformity|Nonconformity|Finding)\s*[-–—:]*\s*(Major|Minor)?\s*[-–—:]+\s*(.+?)(?:\s*\(?(?:Clause|Cl)\s*([\d.]+)\)?)?\s*$',
            line, re.I
        )
        if m:
            ncs.append({
                'severity': m.group(1).strip() if m.group(1) else 'Minor',
                'description': m.group(2).strip().rstrip('.'),
                'clause': m.group(3).strip() if m.group(3) else '',
            })
    return ncs


def _extract_ofis(text: str) -> list[dict]:
    ofis = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(
            r'(?:#?\d+\s*)?(?:OFI|Opportunity\s*(?:for\s+improvement)?)\s*[-–—:]+\s*(.+?)(?:\s*\(?(?:Clause|Cl)\s*([\d.]+)\)?)?\s*$',
            line, re.I
        )
        if m:
            ofis.append({
                'description': m.group(1).strip().rstrip('.'),
                'clause': m.group(2).strip() if m.group(2) else '',
            })
    return ofis


def _extract_positives(text: str) -> list[dict]:
    positives = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(
            r'(?:#?\d+\s*)?(?:Positive|Strength|Good\s*practice|Best\s*practice|Strong\s*point)\s*[-–—:]+\s*(.+?)(?:\s*\(?(?:Clause|Cl)\s*([\d.]+)\)?)?\s*$',
            line, re.I
        )
        if m:
            positives.append({
                'description': m.group(1).strip().rstrip('.'),
                'clause': m.group(2).strip() if m.group(2) else '',
            })
    return positives


def _today() -> datetime:
    """Return current date (function, not module-level constant, so it's always fresh)."""
    return datetime.now()


def _today_str() -> str:
    return _today().strftime('%d/%m/%Y')

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


def _get_clause_qa(clause_dict, clause_id):
    node = clause_data._walk_clause_tree(clause_dict, clause_id)
    if node:
        qs = node.get('audit_questions', [])
        ev = node.get('evidence_to_check', [])
        return '\n'.join(qs) if qs else '', '\n'.join(ev) if ev else ''
    return '', ''


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
            status = _deterministic_choice(statuses, f"{standard_key}_{sid}")
            aq = '\n'.join(sinfo.get('audit_questions', [])) if isinstance(sinfo, dict) else ''
            ec = '\n'.join(sinfo.get('evidence_to_check', [])) if isinstance(sinfo, dict) else ''
            sections.append({
                'clause': sid,
                'title': title,
                'requirement': title,
                'status': status,
                'evidence': evidence,
                'audit_questions': aq,
                'evidence_to_check': ec,
                'notes': '',
                'reference': standard_label,
            })
            sub = sinfo.get('sub_sections', {})
            for sub_id, sub_info in sub.items():
                sub_title = sub_info if isinstance(sub_info, str) else sub_info.get('title', '')
                if sub_title:
                    sub_evidence = f'Reviewed framework element: {sub_title}. The organization has incorporated this principle into its risk management approach.'
                    sub_aq = ''
                    sub_ec = ''
                    if isinstance(sub_info, dict):
                        ev = sub_info.get('evidence', [])
                        if ev:
                            sub_evidence = ev[0]
                        sub_aq = '\n'.join(sub_info.get('audit_questions', []))
                        sub_ec = '\n'.join(sub_info.get('evidence_to_check', []))
                    sections.append({
                        'clause': sub_id,
                        'title': sub_title,
                        'requirement': sub_title,
                        'status': _deterministic_choice(statuses, f"{standard_key}_{sub_id}"),
                        'evidence': sub_evidence,
                        'audit_questions': sub_aq,
                        'evidence_to_check': sub_ec,
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
        aq, ec = _get_clause_qa(clauses, cid)
        status = _deterministic_choice(statuses, f"{standard_key}_{cid}")

        supporting_refs = []
        if supporting and hash(f"{standard_key}_{cid}_sup") % 10 < 4:
            sup_key = _deterministic_choice(list(supporting.keys()), f"{standard_key}_{cid}_sup_key")
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
            'audit_questions': aq,
            'evidence_to_check': ec,
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
            aq, ec = _get_clause_qa(annex, cid)
            status = _deterministic_choice(statuses, f"{standard_key}_annex_{cid}")
            sections.append({
                'clause': cid,
                'title': title,
                'requirement': f'Annex A control: {title} as per {standard_label} {cid}.',
                'status': status,
                'evidence': evidence,
                'audit_questions': aq,
                'evidence_to_check': ec,
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

    ncs = _extract_ncs(combined)
    ofis = _extract_ofis(combined)
    positives = _extract_positives(combined)

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
        'report_number': f'TUV-AR-{_today().year}-{_today().timetuple().tm_yday:03d}',
        'certificate_number': f'TUV-{_today().year}-{_today().timetuple().tm_yday:03d}',
        'extracted_ncs': ncs,
        'extracted_ofis': ofis,
        'extracted_positives': positives,
    }


def generate_audit_plan_stage(data: dict, stage_label: str) -> dict:
    team = data.get('audit_team', [])
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    date = data.get('audit_date', _today_str())
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
        'report_date': (_today() + timedelta(days=30)).strftime('%d/%m/%Y'),
    }


def generate_audit_report(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    date = data.get('audit_date', _today_str())
    team = data.get('audit_team', [])
    family = FAMILY_LABEL_MAP.get(standard_key, 'Management System')

    sections = _build_checklist_sections(standard_key)

    extracted_ncs = data.get('extracted_ncs', [])
    extracted_ofis = data.get('extracted_ofis', [])
    extracted_positives = data.get('extracted_positives', [])

    section_map = {s['clause']: s for s in sections}

    nonconformities = []
    for nc in extracted_ncs:
        clause = nc.get('clause', '')
        nonconformities.append({
            'clause': clause,
            'severity': nc.get('severity', 'Minor'),
            'description': nc['description'],
            'due_date': (_today() + timedelta(days=30)).strftime('%d/%m/%Y'),
        })
        if clause in section_map:
            section_map[clause]['status'] = 'Non-Conformant'

    if not nonconformities:
        for s in sections:
            if s['status'] == 'Non-Conformant' or (s['status'] == 'Partially Conformant' and random.random() < 0.3):
                nonconformities.append({
                    'clause': s['clause'],
                    'severity': 'Minor' if s['status'] == 'Partially Conformant' else random.choice(['Minor', 'Minor', 'Major']),
                    'description': f'{s["title"]}: {s["evidence"]}. During the audit, it was observed that the current implementation does not fully meet the requirements of {standard_label} Clause {s["clause"]}. The organization is required to implement corrective actions and demonstrate effectiveness within the agreed timeframe.',
                    'due_date': (_today() + timedelta(days=30)).strftime('%d/%m/%Y'),
                })

    ofi_descriptions = []
    for ofi in extracted_ofis:
        txt = ofi['description']
        if ofi.get('clause'):
            txt += f' (Clause {ofi["clause"]})'
        ofi_descriptions.append(txt)
        clause = ofi.get('clause', '')
        if clause in section_map and section_map[clause]['status'] != 'Non-Conformant':
            section_map[clause]['status'] = 'Partially Conformant'

    positive_descriptions = []
    for p in extracted_positives:
        txt = p['description']
        if p.get('clause'):
            txt += f' (Clause {p["clause"]})'
        positive_descriptions.append(txt)

    if not ofi_descriptions:
        ofi_descriptions = [
            'Consider enhancing the root cause analysis methodology for recurring nonconformities to prevent recurrence more effectively (Clause 10.1)',
            'Review the frequency and methodology of supplier re-evaluation, particularly for critical external providers (Clause 8.4)',
            'Strengthen the traceability of management review action items to ensure timely closure and effectiveness verification (Clause 9.3)',
            'Consider implementing a more systematic approach to capturing and sharing lessons learned across the organization (Clause 7.4)',
        ]

    if not positive_descriptions:
        positive_descriptions = [
            'Top management demonstrates active commitment through regular participation in management reviews and resource allocation for the management system',
            'Personnel across all levels display appropriate competence and awareness of their roles and responsibilities within the management system',
            'The documented information system is well-structured, with effective document control and record retention practices observed',
            'Internal audit programme is effectively implemented with competent auditors and thorough audit reports',
            'The organization has established effective processes for identifying and addressing risks and opportunities',
        ]

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

    tot_ofi = len(ofi_descriptions)
    tot_nc = len(nonconformities)

    return {
        'client_name': client,
        'audit_date': date,
        'standard': standard_label,
        'report_number': data.get('report_number', f'TUV-AR-{_today().year}-{_today().timetuple().tm_yday:03d}'),
        'scope': data.get('scope', f'{family} system at {client} facilities.'),
        'lead_auditor': data.get('lead_auditor', 'Lead Auditor'),
        'audit_team': team,
        'findings_summary': (
            f'The audit of {client} against {standard_label} was conducted over {data.get("total_mandays", 6)} audit days '
            f'by a team of {len(team)} qualified auditors. The organization demonstrates a generally effective {family} system '
            f'with committed leadership and competent personnel across the audited functions. '
            f'A total of {tot_nc} nonconformit{"y" if tot_nc == 1 else "ies"} '
            f'and {tot_ofi} opportunities for improvement were identified. '
            f'The overall level of system maturity indicates that the management system is '
            f'{ "fully" if decision == "Certified" else "partially" } capable of achieving its intended outcomes.'
        ),
        'positive_findings': positive_descriptions,
        'opportunities_for_improvement': ofi_descriptions,
        'nonconformities': nonconformities[:5],
        'conclusion': _CONCLUSIONS[conclusion_key],
        'report_date': (_today() + timedelta(days=7)).strftime('%d/%m/%Y'),
        'methodology': _generate_methodology(standard_label),
        'certification_decision': decision,
    }


def generate_participation_list(data: dict) -> dict:
    client = data.get('client_name', 'Client')
    team = data.get('audit_team', [])
    return {
        'client_name': client,
        'audit_date': data.get('audit_date', _today_str()),
        'standard': data.get('standard', 'ISO 9001:2015'),
        'participants': _generate_participants(team, client),
        'notes': (
            'Attendance was recorded at both the opening and closing meetings. '
            'All participants listed above were present for the scheduled audit activities. '
            'The audit team confirms that appropriate personnel were available for interview throughout the audit duration.'
        ),
    }


def _apply_extracted_findings_to_sections(data: dict, sections: list[dict]):
    extracted_ncs = data.get('extracted_ncs', [])
    extracted_ofis = data.get('extracted_ofis', [])
    for nc in extracted_ncs:
        clause = nc.get('clause', '')
        for s in sections:
            if s['clause'] == clause:
                s['status'] = 'Non-Conformant'
                s['notes'] = nc['description']
                break
    for ofi in extracted_ofis:
        clause = ofi.get('clause', '')
        for s in sections:
            if s['clause'] == clause and s['status'] != 'Non-Conformant':
                s['status'] = 'Partially Conformant'
                s['notes'] = ofi['description']
                break


def generate_checklist(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    standard_key = data.get('standard_key', 'iso_9001')
    sections = _build_checklist_sections(standard_key)
    _apply_extracted_findings_to_sections(data, sections)
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
        'audit_date': data.get('audit_date', _today_str()),
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
    date = data.get('audit_date', _today_str())
    cert_num = data.get('certificate_number', f'TUV-{_today().year}-{_today().timetuple().tm_yday:03d}')
    issue = _today()
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

    extracted_ncs = data.get('extracted_ncs', [])
    extracted_ofis = data.get('extracted_ofis', [])

    entries = []
    nc_count, major, minor, ofi_count = 0, 0, 0, 0

    for i, nc in enumerate(extracted_ncs):
        entries.append({
            'tnl_number': f'TNL-{i+1:03d}',
            'clause': nc.get('clause', ''),
            'type': 'NC',
            'description': nc['description'],
            'severity': nc.get('severity', 'Minor'),
            'auditee': random.choice(['Quality Manager', 'Operations Manager', 'Department Manager']),
            'due_date': (_today() + timedelta(days=30 if random.random() < 0.7 else 60)).strftime('%d/%m/%Y'),
            'status': 'Open',
        })
        nc_count += 1
        if nc.get('severity') == 'Major':
            major += 1
        else:
            minor += 1

    for i, ofi in enumerate(extracted_ofis):
        entries.append({
            'tnl_number': f'TNL-{len(entries)+1:03d}',
            'clause': ofi.get('clause', ''),
            'type': 'OFI',
            'description': ofi['description'],
            'severity': 'N/A',
            'auditee': random.choice(['Quality Manager', 'Operations Manager', 'Department Manager']),
            'due_date': (_today() + timedelta(days=60)).strftime('%d/%m/%Y'),
            'status': 'Open',
        })
        ofi_count += 1

    if not entries:
        _apply_extracted_findings_to_sections(data, sections)
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
                    'tnl_number': f'TNL-{len(entries)+1:03d}',
                    'clause': s['clause'],
                    'type': typ,
                    'description': f'{s["title"]}: {s["evidence"]}. The current implementation does not fully satisfy the requirements of {standard_label} Clause {s["clause"]}. Corrective actions shall be implemented and verified for effectiveness.',
                    'severity': severity if typ == 'NC' else 'N/A',
                    'auditee': random.choice(['Quality Manager', 'Operations Manager', 'Department Manager']),
                    'due_date': (_today() + timedelta(days=30 if random.random() < 0.7 else 60)).strftime('%d/%m/%Y'),
                    'status': 'Open',
                })

    return {
        'client_name': data.get('client_name', 'Client'),
        'audit_date': data.get('audit_date', _today_str()),
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
    cert_num = data.get('certificate_number', f'TUV-CERT-{_today().year}-{_today().timetuple().tm_yday:03d}')
    issue = _today()
    expiry = issue.replace(year=issue.year + 3)
    decision = data.get('certification_decision', 'Certified')

    return {
        'client_name': client,
        'certificate_number': cert_num,
        'standard': standard_label,
        'audit_date': data.get('audit_date', _today_str()),
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
    date = data.get('audit_date', _today_str())
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
    today_dt = datetime.strptime(review_date, '%d/%m/%Y') if '/' in review_date else _today()
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
    date = data.get('audit_date', _today_str())

    issues = generate_tnl(data)
    entries = issues.get('entries', [])
    nc_entry = entries[0] if entries else {
        'clause': '10.1',
        'severity': 'Minor',
        'tnl_number': 'TNL-001',
    }

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    severity = nc_entry.get('severity', 'Minor')
    clause = nc_entry.get('clause', '10.1')

    return {
        'client_name': client,
        'car_number': f'TUV-CAR-{_today().year}-{_today().timetuple().tm_yday:03d}',
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
    date = data.get('audit_date', _today_str())

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
    date = data.get('audit_date', _today_str())

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


def generate_business_impact_analysis(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 22301:2019')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    activities = [
        {'activity': 'Order-to-Cash Process', 'rto': '4 hours', 'rpo': '1 hour', 'mtd': '8 hours',
         'impact_criteria': 'Revenue loss of ~$50K/hour. Regulatory reporting deadlines affected. Customer contractual penalties apply after 6 hours.',
         'dependencies': 'ERP system, payment gateway, warehouse management, logistics provider, banking APIs',
         'recovery_strategy': 'Failover to secondary data center with hot-standby ERP. Manual order processing procedures available.',
         'priority': 'Critical'},
        {'activity': 'Customer Service Operations', 'rto': '2 hours', 'rpo': 'Real-time', 'mtd': '4 hours',
         'impact_criteria': 'Customer churn risk, SLA breach penalties up to $10K/day, brand reputation damage.',
         'dependencies': 'CRM system, telephony platform, knowledge base, ticketing system',
         'recovery_strategy': 'Cloud-based call routing to backup contact center. Agents can work remotely via VPN.',
         'priority': 'Critical'},
        {'activity': 'Production / Manufacturing', 'rto': '8 hours', 'rpo': '4 hours', 'mtd': '24 hours',
         'impact_criteria': 'Production loss of $20K/hour. Supply chain obligations affected. Fixed costs continue during downtime.',
         'dependencies': 'SCADA systems, MES, raw material suppliers, logistics, quality testing equipment',
         'recovery_strategy': 'Alternate production line at secondary site. Contract manufacturing agreement in place.',
         'priority': 'High'},
        {'activity': 'IT Infrastructure & Network Operations', 'rto': '2 hours', 'rpo': '30 min', 'mtd': '6 hours',
         'impact_criteria': 'All other processes depend on IT availability. Security incidents may increase during disruption.',
         'dependencies': 'Power supply, internet connectivity, cloud providers, data center facilities',
         'recovery_strategy': 'Dual data center with automatic failover. UPS and generator backup for 72 hours.',
         'priority': 'Critical'},
        {'activity': 'HR & Payroll Processing', 'rto': '48 hours', 'rpo': '24 hours', 'mtd': '96 hours',
         'impact_criteria': 'Employee dissatisfaction, regulatory fines for late payroll, labor law compliance.',
         'dependencies': 'HRIS system, payroll provider, time tracking system',
         'recovery_strategy': 'Manual payroll calculation procedures. Backup payroll service provider on retainer.',
         'priority': 'Medium'},
        {'activity': 'Procurement & Supplier Management', 'rto': '24 hours', 'rpo': '8 hours', 'mtd': '72 hours',
         'impact_criteria': 'Supply chain disruption, inability to fulfill customer orders, potential stockouts.',
         'dependencies': 'Procurement system, supplier portal, inventory management, email/communication',
         'recovery_strategy': 'Manual purchase order processing with authorized approvers. Offline supplier contact list maintained.',
         'priority': 'Medium'},
        {'activity': 'Regulatory Compliance & Reporting', 'rto': '8 hours', 'rpo': '4 hours', 'mtd': '24 hours',
         'impact_criteria': 'Regulatory fines for late filings, compliance breaches, legal liability.',
         'dependencies': 'Regulatory filing systems, legal counsel, auditors, board communication channels',
         'recovery_strategy': 'Duplicate records maintained off-site. Legal counsel retains copies of key filings.',
         'priority': 'High'},
    ]

    tiers = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for a in activities:
        p = a['priority']
        if p in tiers:
            tiers[p] += 1

    return {
        'client_name': client,
        'assessment_date': date,
        'standard': standard_label,
        'methodology': (
            f'The Business Impact Analysis was conducted using a questionnaire-based approach '
            f'across all business units of {client}. Critical activities were identified based on '
            f'financial impact, regulatory requirements, customer contractual obligations, and reputational risk. '
            f'Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and Maximum Tolerable Downtime (MTD) '
            f'were determined for each critical activity through stakeholder interviews.'
        ),
        'critical_activities': activities,
        'summary': {
            'total_activities': len(activities),
            'critical': tiers['Critical'],
            'high': tiers['High'],
            'medium': tiers['Medium'],
            'low': tiers['Low'],
        },
        'overall_findings': (
            f'The BIA assessed {len(activities)} business activities across {client}\'s operations. '
            f'Of these, {tiers["Critical"]} activities are classified as critical with maximum tolerance '
            f'for downtime measured in hours. The order-to-cash and customer service processes have the '
            f'most stringent RTO requirements at 2-4 hours. '
            f'IT infrastructure dependencies are pervasive across all critical activities, making data center '
            f'resilience and network continuity top priorities for the BCMS. '
            f'Recommendations include conducting annual BIA reviews, establishing formal RTO/RPO agreements '
            f'with all critical suppliers, and implementing automated failover for Tier 1 systems.'
        ),
    }


def generate_records_of_processing_activities(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 27701:2025')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    activities = [
        {
            'activity_id': 'ROPA-001',
            'activity_name': 'Employee HR and Payroll Data Processing',
            'purpose': 'Performance of employment contract — legal obligation (GDPR Art 6.1.b/c). Processing of special category data for social security (Art 9.2.b).',
            'data_subjects': 'Employees, contractors, interns, former employees',
            'personal_data_categories': 'Name, address, ID number, bank details, salary, performance records, medical leave data, disciplinary records, training records',
            'retention_period': 'Duration of employment + 7 years for tax/legal obligations',
            'cross_border_transfer': 'None — data processed within EU/EEA',
            'security_measures': 'Access control (RBAC), encryption at rest, pseudonymization for reporting, audit logging, HRIS security certification',
        },
        {
            'activity_id': 'ROPA-002',
            'activity_name': 'Customer Relationship Management',
            'purpose': 'Performance of contract (Art 6.1.b) — customer account management, service delivery, invoicing, support.',
            'data_subjects': 'Customers, prospects, client representatives, end users',
            'personal_data_categories': 'Name, email, phone, company, job title, billing address, payment history, communication records, support tickets',
            'retention_period': 'Duration of contract + 3 years for customer relationship management; 7 years for financial records',
            'cross_border_transfer': 'Data stored in EU data centers. Limited access from US-based support team under SCCs.',
            'security_measures': 'CRM access controls, data minimization in support portals, encryption in transit, annual access review, data masking for support staff',
        },
        {
            'activity_id': 'ROPA-003',
            'activity_name': 'Marketing and Communications',
            'purpose': 'Legitimate interest (Art 6.1.f) / Consent (Art 6.1.a) — newsletter, event invitations, targeted campaigns, analytics.',
            'data_subjects': 'Marketing prospects, newsletter subscribers, event attendees, website visitors',
            'personal_data_categories': 'Name, email, company, job title, marketing preferences, browsing behavior on company website, event attendance history',
            'retention_period': 'Until consent withdrawn or 2 years after last interaction',
            'cross_border_transfer': 'Email marketing platform based in US — Data Processing Agreement with SCCs in place.',
            'security_measures': 'Consent management platform, unsubscribe mechanism in all communications, data anonymization for analytics, regular list cleansing',
        },
        {
            'activity_id': 'ROPA-004',
            'activity_name': 'Supplier and Vendor Management',
            'purpose': 'Performance of contract (Art 6.1.b) — procurement, vendor evaluation, contract management, payment processing.',
            'data_subjects': 'Supplier contacts, vendor representatives, subcontractor personnel',
            'personal_data_categories': 'Name, business email, phone, bank account details, tax ID, contract records, performance evaluations',
            'retention_period': 'Duration of contract + 5 years for procurement records',
            'cross_border_transfer': 'None — all suppliers managed within EEA',
            'security_measures': 'Vendor portal with RBAC, encrypted storage of bank details, supplier DPAs in place, periodic vendor security reviews',
        },
        {
            'activity_id': 'ROPA-005',
            'activity_name': 'Video Surveillance and Access Control',
            'purpose': 'Legitimate interest (Art 6.1.f) — premises security, employee safety, property protection, incident investigation.',
            'data_subjects': 'Employees, visitors, contractors, general public entering premises',
            'personal_data_categories': 'CCTV footage, access badge records, visitor logs, vehicle registration data',
            'retention_period': '30 days for CCTV (90 days for incident-related footage). Access logs retained 12 months.',
            'cross_border_transfer': 'None — on-premises systems',
            'security_measures': 'Restricted access to CCTV control room, encrypted storage, retention auto-deletion, privacy masking of non-relevant areas, access control audit trail',
        },
    ]

    has_transfer = any('cross_border' in a.get('cross_border_transfer', '').lower() or 'transfer' in a.get('cross_border_transfer', '').lower() or 'US' in a.get('cross_border_transfer', '') for a in activities)

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'data_controller': f'{client} — registered address as per company registration',
        'data_protection_officer': 'DPO@client.com — Data Protection Officer appointed per GDPR Article 37',
        'processing_activities': activities,
        'summary': {
            'total_activities': len(activities),
            'has_cross_border_transfers': 'Yes' if has_transfer else 'No',
        },
    }


def generate_risk_treatment_plan(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 27001:2022')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    risks = [
        {'id': 'RISK-001', 'desc': 'Unauthorized access to customer database containing PII', 'source': 'External attacker / credential theft',
         'likelihood': 'High', 'impact': 'High', 'level': 'Critical', 'option': 'Reduce',
         'details': 'Implement MFA for all database access. Deploy database activity monitoring. Conduct quarterly access reviews.',
         'controls': 'A.8.2, A.8.15, A.8.16, A.5.15, A.5.23', 'owner': 'CISO', 'days': 45},
        {'id': 'RISK-002', 'desc': 'Ransomware attack on file servers and shared storage', 'source': 'External attacker / phishing email',
         'likelihood': 'High', 'impact': 'High', 'level': 'Critical', 'option': 'Reduce',
         'details': 'Deploy endpoint detection and response (EDR). Implement air-gapped backups with 3-2-1 strategy. Conduct phishing awareness training.',
         'controls': 'A.8.7, A.8.23, A.8.24, A.5.10, A.6.3', 'owner': 'IT Security Manager', 'days': 30},
        {'id': 'RISK-003', 'desc': 'Data exfiltration via insider threat (malicious or accidental)', 'source': 'Internal employee / contractor',
         'likelihood': 'Medium', 'impact': 'High', 'level': 'High', 'option': 'Reduce',
         'details': 'Implement DLP solution for email and web traffic. Enforce least privilege access. Monitor unusual data access patterns.',
         'controls': 'A.5.9, A.5.15, A.8.11, A.5.18, A.6.4', 'owner': 'IT Security Manager', 'days': 60},
        {'id': 'RISK-004', 'desc': 'Cloud service provider outage affecting business applications', 'source': 'External dependency / CSP failure',
         'likelihood': 'Medium', 'impact': 'Medium', 'level': 'High', 'option': 'Transfer',
         'details': 'Review cloud SLA for credits. Develop runbook for manual fallback. Test annually.',
         'controls': 'A.5.19, A.5.20, A.5.21, A.8.1', 'owner': 'Cloud Operations Lead', 'days': 90},
        {'id': 'RISK-005', 'desc': 'Loss of sensitive data during third-party integration', 'source': 'External partner / API vulnerability',
         'likelihood': 'Medium', 'impact': 'Medium', 'level': 'Medium', 'option': 'Reduce',
         'details': 'Implement API gateway with authentication and rate limiting. Conduct third-party security assessment. Encrypt data in transit.',
         'controls': 'A.5.13, A.5.19, A.8.2, A.8.20, A.5.36', 'owner': 'Integration Architect', 'days': 60},
        {'id': 'RISK-006', 'desc': 'Inadequate incident response capability delaying breach containment', 'source': 'Process deficiency',
         'likelihood': 'Low', 'impact': 'High', 'level': 'Medium', 'option': 'Reduce',
         'details': 'Develop and test Incident Response Plan. Conduct tabletop exercises quarterly. Establish 24/7 escalation contacts.',
         'controls': 'A.5.24, A.5.25, A.5.26, A.5.5', 'owner': 'CISO', 'days': 30},
        {'id': 'RISK-007', 'desc': 'Compliance violation due to missing records retention', 'source': 'Process deficiency',
         'likelihood': 'Medium', 'impact': 'Low', 'level': 'Low', 'option': 'Accept',
         'details': 'Accept residual risk. Monitor via annual compliance audits.',
         'controls': 'A.5.10, A.5.31, A.8.10', 'owner': 'Compliance Officer', 'days': 90},
    ]

    levels = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for r in risks:
        lv = r['level']
        if lv in levels:
            levels[lv] += 1

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'risk_assessment_reference': f'Information Security Risk Assessment for {client} — conducted per ISO 27005:2022 methodology',
        'risks': [
            {
                'risk_id': r['id'],
                'risk_description': r['desc'],
                'source': r['source'],
                'likelihood': r['likelihood'],
                'impact': r['impact'],
                'risk_level': r['level'],
                'treatment_option': r['option'],
                'treatment_details': r['details'],
                'selected_controls': r['controls'],
                'risk_owner': r['owner'],
                'target_date': (today_dt + timedelta(days=r['days'])).strftime('%d/%m/%Y'),
                'status': 'Open',
            }
            for r in risks
        ],
        'summary': {
            'total_risks': len(risks),
            'critical': levels['Critical'],
            'high': levels['High'],
            'medium': levels['Medium'],
            'low': levels['Low'],
        },
    }


def generate_incident_investigation_report(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 45001:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    return {
        'client_name': client,
        'incident_date': (today_dt - timedelta(days=7)).strftime('%d/%m/%Y'),
        'report_date': date,
        'standard': standard_label,
        'incident_description': (
            f'On {(today_dt - timedelta(days=7)).strftime("%d %B %Y")} at approximately 10:30 AM, an incident occurred '
            f'in the warehouse area of {client}. An employee slipped on a wet surface near the loading dock '
            f'sustaining a minor ankle injury. The employee was immediately attended to by the first aid team '
            f'and transported to the nearest medical facility for evaluation. The area was cordoned off and '
            f'secured pending investigation.'
        ),
        'location': 'Warehouse Area — Loading Dock Bay 3',
        'incident_type': 'Medical Treatment (Minor Injury)',
        'severity': 'Medium',
        'investigation_team': [
            {'name': 'Safety Manager', 'role': 'Lead Investigator'},
            {'name': 'Warehouse Supervisor', 'role': 'Site Representative'},
            {'name': 'HR Representative', 'role': 'Witness Coordinator'},
            {'name': 'Maintenance Lead', 'role': 'Technical Advisor'},
        ],
        'root_cause': (
            'Root cause analysis was conducted using the 5 Whys methodology. '
            'The immediate cause was a wet floor surface in the loading dock area. '
            'The underlying causes identified include: (1) A leaking hydraulic line on forklift #FL-07 was not '
            'reported after the morning pre-use inspection, (2) The designated spill kit near Bay 3 was found '
            'to be expired and missing absorbent materials, (3) The warehouse floor drainage system in Bay 3 '
            'was partially blocked preventing proper runoff, (4) No wet floor warning signs were available '
            'in the immediate area, and (5) The near-miss reporting system had not captured two prior '
            'incidents of minor slipping in the same area. '
            'Root cause: Inadequate preventive maintenance reporting system and insufficient spill response '
            'readiness in high-risk areas.'
        ),
        'immediate_actions': [
            {'action': 'Provide medical treatment and arrange follow-up care for affected employee', 'owner': 'HR Manager', 'due_date': date},
            {'action': 'Cordon off affected area and deploy temporary non-slip matting', 'owner': 'Warehouse Supervisor', 'due_date': date},
            {'action': 'Inspect and repair hydraulic system on forklift #FL-07', 'owner': 'Maintenance Lead', 'due_date': (today_dt + timedelta(days=1)).strftime('%d/%m/%Y')},
            {'action': 'Restock spill kit at Loading Dock Bay 3 and verify all other bay kits', 'owner': 'Safety Manager', 'due_date': (today_dt + timedelta(days=2)).strftime('%d/%m/%Y')},
        ],
        'corrective_actions': [
            {'action': 'Implement daily spill kit inspection checklist for all high-risk areas', 'owner': 'Safety Manager', 'due_date': (today_dt + timedelta(days=7)).strftime('%d/%m/%Y')},
            {'action': 'Repair drainage system in Bay 3 and inspect adjacent bays', 'owner': 'Maintenance Lead', 'due_date': (today_dt + timedelta(days=14)).strftime('%d/%m/%Y')},
            {'action': 'Install wet floor warning sign holders at all loading dock entrances', 'owner': 'Warehouse Supervisor', 'due_date': (today_dt + timedelta(days=10)).strftime('%d/%m/%Y')},
            {'action': 'Revise pre-use inspection checklist to include hydraulic system checks', 'owner': 'Maintenance Lead', 'due_date': (today_dt + timedelta(days=5)).strftime('%d/%m/%Y')},
        ],
        'lessons_learned': [
            'Pre-use inspection checklists should explicitly include hydraulic system checks for forklifts',
            'Spill kit locations must be verified monthly with documented sign-off',
            'Near-miss reporting culture needs strengthening — two prior slipping incidents were not formally reported',
            'Floor drainage maintenance should be included in the preventive maintenance schedule',
        ],
        'recommendations': [
            'Conduct refresher training on incident reporting for all warehouse staff within 30 days',
            'Implement a digital near-miss reporting tool accessible via mobile devices',
            'Review and update the spill response procedure to include clear roles and communication protocols',
            'Install anti-slip flooring in high-risk wet areas during next maintenance shutdown',
        ],
        'status': 'In Progress',
        'reviewed_by': 'Safety Manager',
    }


def generate_internal_audit_program(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 9001:2015')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()
    year = today_dt.year

    audits = [
        {'id': f'IA-{year}-001', 'scope': f'Quality Management System — all clauses of {standard_label}', 'type': 'Full',
         'planned': f'15/02/{year}', 'auditor': 'Internal Auditor A', 'dept': 'All Departments', 'status': 'Completed', 'findings': 5},
        {'id': f'IA-{year}-002', 'scope': 'Production and Service Provision — Clause 8', 'type': 'Partial',
          'planned': f'10/04/{year}', 'auditor': 'Internal Auditor B', 'dept': 'Operations', 'status': 'Completed', 'findings': 3},
        {'id': f'IA-{year}-003', 'scope': 'Procurement and Supplier Management — Clause 8.4', 'type': 'Partial',
         'planned': f'05/06/{year}', 'auditor': 'Internal Auditor A', 'dept': 'Procurement', 'status': 'In Progress', 'findings': 0},
         {'id': f'IA-{year}-004', 'scope': 'Management Review and Improvement — Clauses 9 & 10', 'type': 'Partial',
          'planned': f'12/08/{year}', 'auditor': 'Internal Auditor B', 'dept': 'Management', 'status': 'Planned', 'findings': 0},
        {'id': f'IA-{year}-005', 'scope': 'Documented Information and Records Control — Clause 7.5', 'type': 'Partial',
          'planned': f'10/10/{year}', 'auditor': 'Internal Auditor A', 'dept': 'All Departments', 'status': 'Planned', 'findings': 0},
        {'id': f'IA-{year}-006', 'scope': f'Full {standard_label} Internal Audit — Pre-Certification', 'type': 'Full',
         'planned': f'20/11/{year}', 'auditor': 'External Lead Auditor', 'dept': 'All Departments', 'status': 'Planned', 'findings': 0},
    ]

    status_counts = {'Planned': 0, 'In Progress': 0, 'Completed': 0, 'Cancelled': 0}
    for a in audits:
        s = a['status']
        if s in status_counts:
            status_counts[s] += 1

    return {
        'client_name': client,
        'program_year': str(year),
        'standard': standard_label,
        'audit_manager': 'Quality Manager',
        'audits': [
            {
                'audit_id': a['id'],
                'scope': a['scope'],
                'audit_type': a['type'],
                'planned_date': a['planned'],
                'auditor': a['auditor'],
                'auditee_department': a['dept'],
                'status': a['status'],
                'findings_count': a['findings'],
            }
            for a in audits
        ],
        'summary': {
            'total_audits': len(audits),
            'planned': status_counts['Planned'],
            'in_progress': status_counts['In Progress'],
            'completed': status_counts['Completed'],
            'cancelled': status_counts['Cancelled'],
        },
    }


def generate_environmental_aspect_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 14001:2015')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    aspects = [
        {'id': 'EAR-001', 'activity': 'Production operations — CNC machining', 'aspect': 'Emissions of metal particulates and cutting fluid mist', 'impact': 'Local air quality degradation, potential respiratory health impacts', 'type': 'Negative', 'sig': 'High',
         'controls': 'Local exhaust ventilation (LEV) system with HEPA filtration. Monthly maintenance checks. PPE requirements for operators.',
         'legal': 'Air Quality Management Regulations, Occupational Safety and Health Act, Local environmental permits', 'eval': 'High significance due to potential health impacts and regulatory requirements. LEV effectiveness verified quarterly.'},
        {'id': 'EAR-002', 'activity': 'Chemical storage — hazardous materials', 'aspect': 'Risk of chemical spill to ground/water', 'impact': 'Soil and groundwater contamination, ecological damage', 'type': 'Negative', 'sig': 'Critical',
         'controls': 'Secondary containment for all hazardous chemicals. Spill kits available. Impermeable flooring. Monthly inspection schedule.',
         'legal': 'Environmental Protection Act, Hazardous Waste Regulations, Water Resources Act', 'eval': 'Critical — potential for significant environmental damage and severe regulatory penalties. Existing controls adequate but require strict adherence.'},
        {'id': 'EAR-003', 'activity': 'Waste management — packaging waste', 'aspect': 'Generation of cardboard, plastic, and metal waste', 'impact': 'Landfill consumption, resource depletion, potential littering', 'type': 'Negative', 'sig': 'Medium',
         'controls': 'Segregation at source. Recycling contract with licensed waste carrier. Monthly waste data tracking. Reduction target: 15% year-on-year.',
         'legal': 'Waste Management Regulations, Producer Responsibility Obligations, Packaging Waste Regulations', 'eval': 'Medium — waste volumes are managed but improvement opportunities exist. Recycling rate currently 72%. Target: 85%.'},
        {'id': 'EAR-004', 'activity': 'Office operations — energy consumption', 'aspect': 'Electricity and natural gas consumption', 'impact': 'Greenhouse gas emissions, climate change contribution, resource depletion', 'type': 'Negative', 'sig': 'High',
         'controls': 'LED lighting throughout. BMS for HVAC scheduling. Motion sensors in low-traffic areas. Renewable energy tariff (40% certified).',
         'legal': 'Energy Efficiency Directive, Climate Change Act, Carbon Reporting Regulations', 'eval': 'High — significant carbon footprint. Energy reduction target: 10% over 12 months. Solar feasibility study in progress.'},
        {'id': 'EAR-005', 'activity': 'Wastewater treatment — industrial effluent', 'aspect': 'Discharge of process wastewater with potential contaminants', 'impact': 'Water pollution, aquatic ecosystem damage, regulatory non-compliance', 'type': 'Negative', 'sig': 'High',
         'controls': 'On-site pre-treatment plant. pH neutralization. Oil/water separation. Quarterly effluent testing by accredited lab.',
         'legal': 'Water Industry Act, Trade Effluent Regulations, Environmental Permitting Regulations', 'eval': 'High — discharge consent limits are strictly monitored. Compliance record: 100% over past 24 months.'},
        {'id': 'EAR-006', 'activity': 'Landscaping and grounds maintenance', 'aspect': 'Water consumption for irrigation', 'impact': 'Water resource depletion, local water scarcity impact', 'type': 'Negative', 'sig': 'Low',
         'controls': 'Drip irrigation system. Rainwater harvesting for irrigation (30% of needs). Drought-resistant planting strategy.',
         'legal': 'Water Abstraction License (if applicable), Local water conservation bylaws', 'eval': 'Low — consumption is minimal relative to operations. Rainwater harvesting reduces mains water demand.'},
    ]

    levels = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for a in aspects:
        s = a['sig']
        if s in levels:
            levels[s] += 1

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'methodology': (
            f'Environmental aspects were identified for {client} using a structured methodology covering '
            f'normal, abnormal, and emergency operating conditions. Each aspect was evaluated for '
            f'significance based on environmental impact severity, regulatory requirements, '
            f'stakeholder concerns, and business risk. Both direct and indirect aspects were considered.'
        ),
        'aspects': [
            {
                'aspect_id': a['id'], 'activity': a['activity'], 'aspect': a['aspect'],
                'environmental_impact': a['impact'], 'impact_type': a['type'],
                'significance': a['sig'], 'control_measures': a['controls'],
                'legal_requirement': a['legal'], 'evaluation': a['eval'],
            }
            for a in aspects
        ],
        'summary': {
            'total_aspects': len(aspects),
            'critical': levels['Critical'],
            'high': levels['High'],
            'medium': levels['Medium'],
            'low': levels['Low'],
        },
    }


def generate_hazard_identification_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 45001:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    hazards = [
        {'id': 'HIR-001', 'activity': 'CNC machining operations', 'hazard': 'Rotating machinery — entanglement, cutting fluid exposure, noise >85dB',
         'risk': 'Operators at risk of serious hand/arm injury from rotating parts. Noise-induced hearing loss with prolonged exposure.',
         'controls': 'Machine guarding, two-hand operation controls, emergency stop within reach. Noise monitoring quarterly. Hearing protection zone. Health surveillance for noise.',
         'level': 'High',
         'additional': 'Install light curtains on all CNC machines. Implement proximity detection systems. Upgrade to low-noise cutting tools where feasible.',
         'hoc': 'Engineering'},
        {'id': 'HIR-002', 'activity': 'Manual lifting and material handling', 'hazard': 'Manual handling of loads up to 25kg — ergonomic strain',
         'risk': 'Warehouse and production staff at risk of musculoskeletal disorders, back injuries, repetitive strain injuries.',
         'controls': 'Mechanical lifting aids (hoists, pallet jacks, forklifts). Manual handling training. Team lifting for loads >15kg. Task rotation.',
         'level': 'Medium',
         'additional': 'Conduct ergonomic assessment of all manual handling tasks. Introduce powered pallet jacks. Implement job rotation schedule.',
         'hoc': 'Administrative'},
        {'id': 'HIR-003', 'activity': 'Chemical handling — degreasing agents', 'hazard': 'Exposure to hazardous chemicals (toluene, acetone, isopropyl alcohol) — inhalation, skin contact, fire risk',
         'risk': 'Operators at risk of dermatitis, respiratory irritation, chemical burns. Fire/explosion risk from flammable solvents.',
         'controls': 'Local exhaust ventilation. Chemical-resistant gloves and aprons. Safety eyewear. Fire extinguishers in area. Flammable storage cabinet. SDS available.',
         'level': 'Critical',
         'additional': 'Replace solvent-based degreasers with aqueous alternatives. Install continuous gas monitoring. Upgrade to explosion-proof electrics.',
         'hoc': 'Elimination'},
        {'id': 'HIR-004', 'activity': 'Electrical maintenance — live panel work', 'hazard': 'Electrical shock/arc flash — working on or near live electrical equipment',
         'risk': 'Maintenance electricians at risk of fatal electrical shock, arc flash burns, and falls from shock reaction.',
         'controls': 'Permit-to-work system. Lock-out/tag-out (LOTO) procedures. Arc flash PPE. Insulated tools. Quarterly competency verification.',
         'level': 'Critical',
         'additional': 'Install remote racking devices for switchgear. Implement IR scanning program. Upgrade arc flash ratings on panels >400V.',
         'hoc': 'Engineering'},
        {'id': 'HIR-005', 'activity': 'Warehouse operations — forklift traffic', 'hazard': 'Forklift-pedestrian collision, loads falling from height, overturning',
         'risk': 'Warehouse staff and visitors at risk of crush injuries, fractures, and fatal injuries from forklift incidents.',
         'controls': 'Separated pedestrian walkways marked with yellow lines. Speed limiters on forklifts (8 km/h). Forklift pre-use checks. Operator certification. Reversing alarms.',
         'level': 'High',
         'additional': 'Install proximity sensors and auto-braking systems. Implement traffic management plan with one-way systems where feasible.',
         'hoc': 'Engineering'},
        {'id': 'HIR-006', 'activity': 'Office work — DSE', 'hazard': 'Display screen equipment — prolonged sitting, poor posture, glare',
         'risk': 'Office staff at risk of upper limb disorders, back/neck pain, eye strain, headaches.',
         'controls': 'Adjustable chairs and desks. Anti-glare screens. DSE self-assessment. Eye test vouchers every 2 years. Break reminder software.',
         'level': 'Low',
         'additional': 'Introduce sit-stand desks. Implement micro-break prompts at 55-min intervals. Conduct annual DSE workstation audits.',
         'hoc': 'Administrative'},
    ]

    levels = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for h in hazards:
        lv = h['level']
        if lv in levels:
            levels[lv] += 1

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'methodology': (
            f'Hazard identification was conducted for {client} using a systematic approach covering all '
            f'work areas, activities, and personnel. Risk assessment methodology follows the hierarchy of '
            f'control: elimination, substitution, engineering controls, administrative controls, and PPE. '
            f'Both routine and non-routine activities were included.'
        ),
        'hazards': [
            {
                'hazard_id': h['id'], 'activity': h['activity'], 'hazard': h['hazard'],
                'associated_risk': h['risk'], 'existing_controls': h['controls'],
                'risk_level': h['level'], 'additional_controls': h['additional'],
                'hierarchy_of_control': h['hoc'],
            }
            for h in hazards
        ],
        'summary': {
            'total_hazards': len(hazards),
            'critical': levels['Critical'],
            'high': levels['High'],
            'medium': levels['Medium'],
            'low': levels['Low'],
        },
    }


def generate_energy_review(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 50001:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    sources = [
        {'source': 'Grid Electricity', 'consumption': '2,450,000 kWh', 'cost': '$318,500', 'trend': 'Stable',
         'notes': '40% from certified renewable sources. Peak demand: 420 kW. Power factor: 0.95.'},
        {'source': 'Natural Gas', 'consumption': '850,000 kWh (30,000 therms)', 'cost': '$42,500', 'trend': 'Decreasing',
         'notes': 'Used for space heating and process drying. Boiler efficiency: 88%. Annual service maintained.'},
        {'source': 'Diesel (Generator Backup)', 'consumption': '2,500 liters', 'cost': '$5,250', 'trend': 'Stable',
         'notes': 'Emergency backup only. Monthly test runs (30 min). Annual fuel quality check.'},
        {'source': 'Solar PV (On-site Generation)', 'consumption': '85,000 kWh generated', 'cost': '-$12,750 (savings)', 'trend': 'Stable',
         'notes': '120 kWp rooftop installation. Feed-in tariff: $0.08/kWh. Generation metered separately.'},
        {'source': 'Propane (Forklift Fleet)', 'consumption': '8,500 kg', 'cost': '$14,875', 'trend': 'Increasing',
         'notes': 'Fleet of 12 propane forklifts. Transition to electric under evaluation. Charging infrastructure cost: $45K estimated.'},
    ]

    seus = [
        {'id': 'SEU-001', 'equipment': 'HVAC System — Main Production Hall', 'source': 'Electricity + Natural Gas',
         'consumption': '680,000 kWh/yr electricity + 420,000 kWh/yr gas', 'variables': 'Outside air temperature, production hours, occupancy levels',
         'enpi': 'kWh/m²/HDD (normalized) — target: 85. Current: 92',
         'baseline': '2025 average: 95 kWh/m²/HDD (12-month rolling)',
         'current': '3% above baseline — damper maintenance overdue. Adjust schedule for non-production days.'},
        {'id': 'SEU-002', 'equipment': 'Compressed Air System', 'source': 'Electricity',
         'consumption': '320,000 kWh/yr (13% of total electricity)', 'variables': 'Production volume, number of shifts, leakage rate',
         'enpi': 'kWh/m³ compressed air — target: 0.12. Current: 0.15',
         'baseline': '2025 average: 0.16 kWh/m³',
         'current': '6% improvement vs baseline. Leak detection program ongoing — 12% leakage rate identified.'},
        {'id': 'SEU-003', 'equipment': 'CNC Machining Center (5 units)', 'source': 'Electricity',
         'consumption': '410,000 kWh/yr', 'variables': 'Production batch size, material type, spindle utilization',
         'enpi': 'kWh/part produced — target: 4.5. Current: 5.2',
         'baseline': '2025 average: 5.8 kWh/part',
         'current': '10% improvement vs baseline achieved through programming optimization. Additional 5% target through spindle speed optimization.'},
        {'id': 'SEU-004', 'equipment': 'Process Drying Oven', 'source': 'Natural Gas',
         'consumption': '280,000 kWh/yr gas', 'variables': 'Production throughput, moisture content of input material, ambient conditions',
         'enpi': 'kWh/kg material dried — target: 0.35. Current: 0.42',
         'baseline': '2025 average: 0.44 kWh/kg',
         'current': '5% from target. Heat recovery feasibility study recommended — estimated 15% reduction potential.'},
    ]

    total_cost = '$368,375'

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'review_period': 'January 2026 – December 2026',
        'methodology': (
            f'The energy review for {client} was conducted following ISO 50006 guidelines. '
            f'Energy consumption data was collected from utility bills, submetering systems, and equipment-level monitoring. '
            f'Significant Energy Uses (SEUs) were identified based on consumption magnitude and improvement potential. '
            f'Energy Baselines (EnB) were established using 2025 as the reference year. '
            f'Energy Performance Indicators (EnPI) were defined for each SEU with appropriate normalizing factors.'
        ),
        'energy_sources': [
            {'source': s['source'], 'consumption': s['consumption'], 'cost': s['cost'], 'trend': s['trend'], 'notes': s['notes']}
            for s in sources
        ],
        'significant_uses': [
            {
                'use_id': seu['id'], 'equipment': seu['equipment'], 'energy_source': seu['source'],
                'consumption': seu['consumption'], 'variables': seu['variables'], 'enpi': seu['enpi'],
                'baseline': seu['baseline'], 'current_performance': seu['current'],
            }
            for seu in seus
        ],
        'summary': {
            'total_energy_sources': len(sources),
            'total_seus': len(seus),
            'total_energy_cost': total_cost,
        },
    }


def generate_compliance_obligations_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 37301:2021')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    obligations = [
        {'id': 'COR-001', 'type': 'Legal', 'source': 'Occupational Safety and Health Act (OSHA)', 'req': 'Employer shall provide a workplace free from recognized hazards. Maintain injury/illness records. Display OSHA poster.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'Safety program documentation available. OSHA 300 logs maintained. Posters displayed in all common areas. Annual training records on file.',
         'due': 'Ongoing', 'resp': 'Safety Manager'},
        {'id': 'COR-002', 'type': 'Legal', 'source': 'Environmental Protection Act — Waste Management', 'req': 'Duty of care for waste. Complete waste transfer notes. Register as waste carrier if transporting own waste.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'Waste transfer notes maintained for all waste streams. Licensed waste carrier contract in place. Waste hierarchy applied.',
         'due': 'Ongoing', 'resp': 'Environmental Manager'},
        {'id': 'COR-003', 'type': 'Regulatory', 'source': 'ISO 14001:2015 Clause 6.1.3', 'req': 'Determine compliance obligations related to environmental aspects. Maintain register of obligations.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'Compliance obligations register maintained and updated quarterly. Legal register reviewed by external counsel annually.',
         'due': 'Ongoing', 'resp': 'Quality Manager'},
        {'id': 'COR-004', 'type': 'Regulatory', 'source': 'ISO 45001:2018 Clause 6.1.3', 'req': 'Determine legal requirements and other requirements related to OH&S management system.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'OH&S legal register maintained. Requirements communicated to relevant personnel. Updates tracked through subscription service.',
         'due': 'Ongoing', 'resp': 'Safety Manager'},
        {'id': 'COR-005', 'type': 'Legal', 'source': 'General Data Protection Regulation (GDPR)', 'req': 'Process personal data lawfully, fairly, and transparently. Maintain ROPA. Report breaches within 72 hours.',
         'app': 'Partial', 'status': 'Partially Compliant', 'evidence': 'ROPA documented. Privacy notices updated. Breach notification procedure in draft. DPO appointed. Consent records need improvement.',
         'due': '30/09/2026', 'resp': 'Data Protection Officer'},
        {'id': 'COR-006', 'type': 'Contractual', 'source': 'Customer contracts — confidentiality clauses', 'req': 'Maintain confidentiality of customer proprietary information. Limit access to need-to-know basis. Implement appropriate security measures.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'NDAs in place with all employees. Data classification policy implemented. Access controls audited quarterly. No breaches reported.',
         'due': 'Ongoing', 'resp': 'Legal Counsel'},
        {'id': 'COR-007', 'type': 'Regulatory', 'source': 'ISO 50001:2018 Clause 6.3', 'req': 'Conduct energy review. Establish EnB and EnPI. Update at defined intervals.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'Energy review completed per ISO 50006. EnB established for 2025. EnPI tracking in place. Review scheduled for next management review.',
         'due': 'Ongoing', 'resp': 'Energy Manager'},
        {'id': 'COR-008', 'type': 'Legal', 'source': 'Fire Safety Regulations', 'req': 'Conduct fire risk assessment. Maintain fire detection and suppression systems. Fire drill records. Emergency evacuation plans.',
         'app': 'Full', 'status': 'Compliant', 'evidence': 'Fire risk assessment completed and reviewed annually. Fire wardens trained. Drills conducted quarterly. Systems tested weekly.',
         'due': 'Ongoing', 'resp': 'Facilities Manager'},
    ]

    counts = {'Compliant': 0, 'Partially Compliant': 0, 'Non-Compliant': 0, 'Not Assessed': 0}
    for o in obligations:
        s = o['status']
        if s in counts:
            counts[s] += 1

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'methodology': (
            f'Compliance obligations for {client} were identified through review of applicable legislation, '
            f'regulatory requirements, industry standards, contractual commitments, and other requirements '
            f'to which the organization subscribes. The register is reviewed quarterly and updated '
            f'when new obligations arise or existing obligations change.'
        ),
        'obligations': [
            {
                'obligation_id': o['id'], 'obligation_type': o['type'], 'source': o['source'],
                'requirement': o['req'], 'applicability': o['app'],
                'compliance_status': o['status'], 'evidence': o['evidence'],
                'due_date': o['due'], 'responsible': o['resp'],
            }
            for o in obligations
        ],
        'summary': {
            'total_obligations': len(obligations),
            'compliant': counts['Compliant'],
            'partially_compliant': counts['Partially Compliant'],
            'non_compliant': counts['Non-Compliant'],
            'not_assessed': counts['Not Assessed'],
        },
    }


def generate_service_portfolio(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    services = [
        {'id': 'SVC-001', 'name': 'IT Help Desk & End-User Support', 'desc': 'First-line IT support for all employees. Incident logging, triage, and resolution. Hardware and software support for workstations.',
         'cat': 'Core', 'status': 'Active',
         'uptime': '99.5%', 'response': '30 minutes (Priority 1), 4 hours (Priority 2)', 'resolution': '4 hours (P1), 24 hours (P2), 5 days (P3)',
         'owner': 'IT Support Manager'},
        {'id': 'SVC-002', 'name': 'Network Infrastructure Services', 'desc': 'Corporate LAN/WAN connectivity, VPN access, WiFi, firewall management, network monitoring and capacity management.',
         'cat': 'Core', 'status': 'Active',
         'uptime': '99.9% (backbone), 99.5% (user-facing)', 'response': '15 minutes for network outages', 'resolution': '2 hours for critical outages, 8 hours for standard issues',
         'owner': 'Network Manager'},
        {'id': 'SVC-003', 'name': 'Business Application Hosting', 'desc': 'Hosting and maintenance of ERP, CRM, HRIS, and other business-critical applications. Database administration and patch management.',
         'cat': 'Core', 'status': 'Active',
         'uptime': '99.7%', 'response': '15 minutes (application down), 1 hour (performance degradation)', 'resolution': '2 hours (critical), 8 hours (major), 48 hours (minor)',
         'owner': 'Applications Manager'},
        {'id': 'SVC-004', 'name': 'Cloud Migration Service', 'desc': 'Assessment, planning, and execution of workload migration to cloud. Hybrid cloud architecture management.',
         'cat': 'Enabling', 'status': 'In Development',
         'uptime': 'N/A (in development)', 'response': 'N/A', 'resolution': 'N/A',
         'owner': 'Cloud Architect'},
        {'id': 'SVC-005', 'name': 'Data Backup & Disaster Recovery', 'desc': 'Automated backup of servers, databases, and critical data. Off-site replication. DR testing and business continuity support.',
         'cat': 'Support', 'status': 'Active',
         'uptime': 'Guaranteed 99.9% backup success rate', 'response': 'Immediate for backup failures (automated alerting)', 'resolution': '4 hours for restore requests (non-DR), 1 hour for DR activation',
         'owner': 'Infrastructure Manager'},
        {'id': 'SVC-006', 'name': 'Cybersecurity Operations', 'desc': 'Security monitoring, threat detection and response, vulnerability management, endpoint protection, SIEM operations.',
         'cat': 'Core', 'status': 'Active',
         'uptime': '24/7 monitoring coverage', 'response': '10 minutes (critical security incident), 1 hour (high severity)', 'resolution': '1 hour (contain critical), 4 hours (contain high), 24 hours (remediate)',
         'owner': 'CISO'},
        {'id': 'SVC-007', 'name': 'Software Development Platform', 'desc': 'CI/CD pipeline, source control, test automation, dev/staging/prod environments. Developer tooling and access management.',
         'cat': 'Enabling', 'status': 'Active',
         'uptime': '99.5% pipeline availability', 'response': '30 minutes (pipeline down), 2 hours (tool issues)', 'resolution': '2 hours (critical), 24 hours (non-critical)',
         'owner': 'DevOps Lead'},
        {'id': 'SVC-008', 'name': 'Managed Print Services', 'desc': 'Printer fleet management, print server administration, consumables replenishment, print cost tracking.',
         'cat': 'Support', 'status': 'Planned',
         'uptime': 'Target: 98%', 'response': 'Target: 4 hours for printer faults', 'resolution': 'Target: 24 hours',
         'owner': 'Facilities Manager'},
    ]

    statuses = {'Active': 0, 'In Development': 0, 'Retired': 0, 'Planned': 0}
    for s in services:
        st = s['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client,
        'date': date,
        'standard': standard_label,
        'portfolio_manager': 'IT Service Delivery Manager',
        'services': [
            {
                'service_id': s['id'], 'service_name': s['name'], 'description': s['desc'],
                'category': s['cat'], 'status': s['status'],
                'sla_uptime': s['uptime'], 'sla_response_time': s['response'],
                'sla_resolution_time': s['resolution'], 'service_owner': s['owner'],
            }
            for s in services
        ],
        'summary': {
            'total_services': len(services),
            'active': statuses['Active'],
            'in_development': statuses['In Development'],
            'retired': statuses['Retired'],
            'planned': statuses['Planned'],
        },
    }


# ── ISO 20000-1 Service Management Generators ─────────────────────────────

def generate_service_catalogue(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    services = [
        {'id': 'CAT-001', 'name': 'IT Help Desk', 'desc': 'Single point of contact for all IT incidents and service requests. Provides first-line support, triage, and escalation management.', 'type': 'Customer', 'status': 'Live', 'features': '24/7 ticket submission, self-service portal, knowledge base, SLA-based prioritisation, real-time status tracking', 'contact': 'IT Support Manager', 'hours': '24x7'},
        {'id': 'CAT-002', 'name': 'Corporate Email & Collaboration', 'desc': 'Enterprise email, calendaring, instant messaging, and video conferencing services for all employees.', 'type': 'Business', 'status': 'Live', 'features': '50GB mailbox, shared calendars, Teams/Slack integration, mobile sync, encryption in transit/at rest', 'contact': 'IT Support Manager', 'hours': '24x7'},
        {'id': 'CAT-003', 'name': 'Network Connectivity', 'desc': 'Corporate LAN, WAN, VPN, and WiFi services connecting all sites and remote workers.', 'type': 'Infrastructure', 'status': 'Live', 'features': 'Site-to-site VPN, SD-WAN, guest WiFi, traffic shaping, network monitoring, DDoS protection', 'contact': 'Network Manager', 'hours': '24x7'},
        {'id': 'CAT-004', 'name': 'ERP System Hosting', 'desc': 'Hosting, administration, and support for the enterprise resource planning system.', 'type': 'Business', 'status': 'Live', 'features': '99.7% uptime SLA, daily backups, patch management, user administration, custom report development', 'contact': 'Applications Manager', 'hours': 'Business Hours (08:00-18:00)'},
        {'id': 'CAT-005', 'name': 'Cybersecurity Monitoring', 'desc': 'Security operations monitoring, threat detection, vulnerability management, and incident response.', 'type': 'Infrastructure', 'status': 'Live', 'features': '24/7 SOC, SIEM platform, endpoint protection, phishing simulation, vulnerability scanning, threat intelligence feeds', 'contact': 'CISO', 'hours': '24x7'},
        {'id': 'CAT-006', 'name': 'Cloud Backup & Disaster Recovery', 'desc': 'Automated backup of critical systems and data with off-site replication and DR orchestration.', 'type': 'Infrastructure', 'status': 'Live', 'features': 'Automated daily backups, 30-day retention, off-site replication, DR runbook testing, RTO 4 hrs / RPO 1 hr', 'contact': 'Infrastructure Manager', 'hours': '24x7'},
        {'id': 'CAT-007', 'name': 'Legacy System Migration Service', 'desc': 'Assessment, planning, and execution of workload migration from legacy systems to modern platforms.', 'type': 'Customer', 'status': 'Under Review', 'features': 'Application discovery, dependency mapping, migration planning, cutover management, post-migration validation', 'contact': 'Cloud Architect', 'hours': 'Business Hours'},
        {'id': 'CAT-008', 'name': 'Managed Print Services', 'desc': 'Printer fleet management, print server administration, consumables replenishment, cost tracking.', 'type': 'Customer', 'status': 'Deprecated', 'features': 'Centralized print management, follow-me printing, print quota enforcement, automatic toner replenishment', 'contact': 'Facilities Manager', 'hours': 'Business Hours'},
    ]

    statuses = {'Live': 0, 'Deprecated': 0, 'Under Review': 0}
    for s in services:
        st = s['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'catalogue_owner': 'IT Service Delivery Manager',
        'catalogue_version': '2.1 — March 2026',
        'services': [
            {'service_id': s['id'], 'service_name': s['name'], 'description': s['desc'],
             'service_type': s['type'], 'status': s['status'], 'features': s['features'],
             'contact': s['contact'], 'service_hours': s['hours']}
            for s in services
        ],
        'summary': {
            'total_services': len(services),
            'live': statuses['Live'],
            'deprecated': statuses['Deprecated'],
            'under_review': statuses['Under Review'],
        },
    }


def generate_supplier_agreement_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()
    agreements = [
        {'id': 'SAR-001', 'supplier': 'CloudServe Technologies', 'service': 'Cloud infrastructure hosting — IaaS and PaaS services for production systems', 'type': 'SLA', 'start': (today_dt - timedelta(days=180)).strftime('%d/%m/%Y'), 'renewal': (today_dt + timedelta(days=545)).strftime('%d/%m/%Y'), 'status': 'Active', 'rating': 'Satisfactory', 'contacts': 'CloudServe Account Manager + CloudOps Lead'},
        {'id': 'SAR-002', 'supplier': 'SecureNet Ltd', 'service': 'Managed firewall, intrusion detection, and DDoS protection services', 'type': 'Contract', 'start': (today_dt - timedelta(days=365)).strftime('%d/%m/%Y'), 'renewal': (today_dt + timedelta(days=730)).strftime('%d/%m/%Y'), 'status': 'Active', 'rating': 'Excellent', 'contacts': 'SecureNet support portal + CISO'},
        {'id': 'SAR-003', 'supplier': 'DataGuard Backup', 'service': 'Off-site backup storage, DR replication, and recovery testing', 'type': 'SLA', 'start': (today_dt - timedelta(days=90)).strftime('%d/%m/%Y'), 'renewal': (today_dt + timedelta(days=275)).strftime('%d/%m/%Y'), 'status': 'Active', 'rating': 'Satisfactory', 'contacts': 'DataGuard Support + Infrastructure Manager'},
        {'id': 'SAR-004', 'supplier': 'TelecomCorp', 'service': 'WAN connectivity, MPLS links, and internet leased lines', 'type': 'Contract', 'start': (today_dt - timedelta(days=730)).strftime('%d/%m/%Y'), 'renewal': (today_dt - timedelta(days=30)).strftime('%d/%m/%Y'), 'status': 'Under Negotiation', 'rating': 'Needs Improvement', 'contacts': 'TelecomCorp Account Manager + Network Manager'},
        {'id': 'SAR-005', 'supplier': 'SoftwareLicence Pro', 'service': 'Enterprise software licensing — Microsoft, Oracle, Adobe', 'type': 'Partnership', 'start': (today_dt - timedelta(days=365)).strftime('%d/%m/%Y'), 'renewal': (today_dt + timedelta(days=700)).strftime('%d/%m/%Y'), 'status': 'Active', 'rating': 'Excellent', 'contacts': 'Licensing portal + Procurement Manager'},
        {'id': 'SAR-006', 'supplier': 'HelpDesk Pro', 'service': 'ITSM platform — incident, problem, change management system', 'type': 'SLA', 'start': (today_dt - timedelta(days=180)).strftime('%d/%m/%Y'), 'renewal': (today_dt + timedelta(days=185)).strftime('%d/%m/%Y'), 'status': 'Terminated', 'rating': 'Needs Improvement', 'contacts': 'N/A — contract terminated. Migration to in-house solution completed.'},
    ]

    statuses = {'Active': 0, 'Expired': 0, 'Under Negotiation': 0, 'Terminated': 0}
    for a in agreements:
        st = a['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'register_owner': 'Procurement Manager',
        'agreements': [
            {'agreement_id': a['id'], 'supplier_name': a['supplier'], 'service_provided': a['service'],
             'agreement_type': a['type'], 'start_date': a['start'], 'renewal_date': a['renewal'],
             'status': a['status'], 'performance_rating': a['rating'], 'key_contacts': a['contacts']}
            for a in agreements
        ],
        'summary': {
            'total_agreements': len(agreements),
            'active': statuses['Active'],
            'expired': statuses['Expired'],
            'under_negotiation': statuses['Under Negotiation'],
            'terminated': statuses['Terminated'],
        },
    }


def generate_business_relationship_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    customers = [
        {'id': 'BRR-001', 'name': 'Manufacturing Division — HQ', 'mgr': 'Account Director A', 'svcs': 'IT Help Desk, Email, Network, ERP, Backup, Cybersecurity', 'sat': '9.2/10', 'complaints': 1, 'last': (today_dt - timedelta(days=45)).strftime('%d/%m/%Y'), 'next': (today_dt + timedelta(days=320)).strftime('%d/%m/%Y'), 'status': 'Active'},
        {'id': 'BRR-002', 'name': 'R&D Lab Facility', 'mgr': 'Account Director A', 'svcs': 'Network, Cloud Backup, Cybersecurity Monitoring', 'sat': '8.8/10', 'complaints': 0, 'last': (today_dt - timedelta(days=90)).strftime('%d/%m/%Y'), 'next': (today_dt + timedelta(days=275)).strftime('%d/%m/%Y'), 'status': 'Active'},
        {'id': 'BRR-003', 'name': 'Regional Warehouse — North', 'mgr': 'Account Director B', 'svcs': 'IT Help Desk, Network, Managed Print', 'sat': '6.5/10', 'complaints': 3, 'last': (today_dt - timedelta(days=30)).strftime('%d/%m/%Y'), 'next': (today_dt + timedelta(days=60)).strftime('%d/%m/%Y'), 'status': 'At Risk'},
        {'id': 'BRR-004', 'name': 'Sales Office — West', 'mgr': 'Account Director B', 'svcs': 'Email, VPN, VoIP', 'sat': '7.8/10', 'complaints': 1, 'last': (today_dt - timedelta(days=120)).strftime('%d/%m/%Y'), 'next': (today_dt + timedelta(days=245)).strftime('%d/%m/%Y'), 'status': 'Active'},
        {'id': 'BRR-005', 'name': 'Remote Workers Cohort', 'mgr': 'IT Support Manager', 'svcs': 'VPN, Email, Collaboration Tools, Endpoint Security', 'sat': '8.0/10', 'complaints': 2, 'last': (today_dt - timedelta(days=60)).strftime('%d/%m/%Y'), 'next': (today_dt + timedelta(days=305)).strftime('%d/%m/%Y'), 'status': 'Active'},
    ]

    statuses = {'Active': 0, 'On Hold': 0, 'At Risk': 0, 'Inactive': 0}
    score_sum = 0
    for c in customers:
        st = c['status']
        if st in statuses:
            statuses[st] += 1
        sat_str = c['sat'].split('/')[0]
        score_sum += float(sat_str)

    avg_sat = f'{score_sum / len(customers):.1f}/10'

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'relationship_manager': 'Head of Service Delivery',
        'customers': [
            {'customer_id': c['id'], 'customer_name': c['name'], 'account_manager': c['mgr'],
             'services_used': c['svcs'], 'satisfaction_score': c['sat'], 'complaints': c['complaints'],
             'last_review': c['last'], 'next_review': c['next'], 'status': c['status']}
            for c in customers
        ],
        'summary': {
            'total_customers': len(customers),
            'active': statuses['Active'],
            'on_hold': statuses['On Hold'],
            'at_risk': statuses['At Risk'],
            'inactive': statuses['Inactive'],
            'avg_satisfaction': avg_sat,
        },
    }


def generate_capacity_management_plan(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    components = [
        {'id': 'CMP-001', 'comp': 'Primary Application Servers (Cluster-A)', 'cur': '16 vCPU, 64 GB RAM, 2 TB SSD', 'demand': 'avg 55% CPU, 62% RAM, 40% storage', 'util': '55%', 'thresh': '80%', 'forecast': 'Expected 15% growth over 12 months', 'upgrade': 'Add 2 nodes in Q3 2026. Estimated cost: $45K', 'status': 'Green'},
        {'id': 'CMP-002', 'comp': 'Database Servers (SQL Cluster)', 'cur': '32 vCPU, 128 GB RAM, 4 TB NVMe', 'demand': 'avg 68% CPU, 74% RAM, 55% storage', 'util': '74%', 'thresh': '80%', 'forecast': 'Expected 20% growth from new ERP modules', 'upgrade': 'Add 64 GB RAM in Q2 2026. Evaluate storage expansion.', 'status': 'Amber'},
        {'id': 'CMP-003', 'comp': 'SAN Storage Array', 'cur': '120 TB raw (96 TB usable)', 'demand': '78 TB used (81% utilization)', 'util': '81%', 'thresh': '80%', 'forecast': 'Growth ~2 TB/month', 'upgrade': 'URGENT: Add 40 TB shelf ordered. Expected delivery: 2 weeks.', 'status': 'Red'},
        {'id': 'CMP-004', 'comp': 'Network Backbone (10 Gbps)', 'cur': '10 Gbps core, 1 Gbps access', 'demand': 'Peak 6.2 Gbps (62%), avg 3.8 Gbps (38%)', 'util': '62%', 'thresh': '75%', 'forecast': 'Expected 25% growth with new site connection', 'upgrade': 'Plan core upgrade to 25 Gbps in Q4 2026.', 'status': 'Green'},
        {'id': 'CMP-005', 'comp': 'Internet Bandwidth (500 Mbps)', 'cur': '500 Mbps symmetrical', 'demand': 'Peak 420 Mbps (84%), avg 280 Mbps (56%)', 'util': '84%', 'thresh': '80%', 'forecast': 'WAN optimization being deployed', 'upgrade': 'Upgrade to 1 Gbps planned. Supplier quote received: $1,200/month.', 'status': 'Red'},
        {'id': 'CMP-006', 'comp': 'Backup Storage', 'cur': '200 TB raw capacity', 'demand': '165 TB used (82.5%)', 'util': '83%', 'thresh': '85%', 'forecast': 'Growth ~3 TB/month', 'upgrade': 'Deduplication appliance upgrade in progress. Expected completion: 1 month.', 'status': 'Amber'},
    ]

    counts = {'Green': 0, 'Amber': 0, 'Red': 0}
    for c in components:
        st = c['status']
        if st in counts:
            counts[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'capacity_manager': 'Infrastructure Manager',
        'review_period': 'Monthly — next review: 15th of each month',
        'scope': 'All IT infrastructure components supporting ISO 20000-1:2018 scope. Includes servers, storage, network, backup, and internet connectivity.',
        'components': [
            {'component_id': c['id'], 'component': c['comp'], 'current_capacity': c['cur'],
             'current_demand': c['demand'], 'utilization': c['util'], 'threshold': c['thresh'],
             'forecast_demand': c['forecast'], 'planned_upgrade': c['upgrade'], 'status': c['status']}
            for c in components
        ],
        'summary': {
            'total_components': len(components),
            'green': counts['Green'],
            'amber': counts['Amber'],
            'red': counts['Red'],
        },
    }


def generate_change_management_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    changes = [
        {'id': 'CHG-001', 'title': 'ERP System Upgrade v4.2 to v5.0', 'desc': 'Major version upgrade of ERP including database schema changes, new UI, and API updates. Requires full regression testing.', 'type': 'Normal', 'priority': 'High', 'risk': 'High', 'impact': 'ERP unavailable for 8 hours during cutover. All business units affected.', 'rollback': 'Full database restore from pre-upgrade backup. Revert application binaries. Estimated rollback time: 4 hours.', 'cab': (today_dt - timedelta(days=14)).strftime('%d/%m/%Y'), 'sched': (today_dt + timedelta(days=30)).strftime('%d/%m/%Y'), 'req': 'IT Applications Manager', 'status': 'Approved'},
        {'id': 'CHG-002', 'title': 'Firewall Rule Update — New Office Location', 'desc': 'Add firewall rules for new branch office. Open ports for VPN, file sharing, and business applications.', 'type': 'Standard', 'priority': 'Medium', 'risk': 'Low', 'impact': 'No impact. Pre-approved change type following standard template.', 'rollback': 'Remove added rules. Revert to previous config. Time: 30 minutes.', 'cab': 'N/A — Standard change', 'sched': (today_dt - timedelta(days=5)).strftime('%d/%m/%Y'), 'req': 'Network Engineer', 'status': 'Implemented'},
        {'id': 'CHG-003', 'title': 'Emergency Security Patch — Critical CVE', 'desc': 'Apply out-of-band security patch for critical vulnerability in web server software (CVE-2026-1234).', 'type': 'Emergency', 'priority': 'Critical', 'risk': 'Medium', 'impact': 'Brief service interruption during patch application. Estimated downtime: 15 minutes.', 'rollback': 'Restore pre-patch snapshot. Time: 10 minutes.', 'cab': 'Emergency CAB convened', 'sched': (today_dt - timedelta(days=2)).strftime('%d/%m/%Y'), 'req': 'Security Operations Lead', 'status': 'Implemented'},
        {'id': 'CHG-004', 'title': 'SAN Storage Expansion', 'desc': 'Add 40 TB storage shelf to primary SAN. Requires scheduled downtime for storage controller firmware update.', 'type': 'Normal', 'priority': 'High', 'risk': 'Medium', 'impact': 'Storage performance may be degraded during firmware update. Expected window: 2 hours.', 'rollback': 'Keep old shelf online. Revert firmware if incompatibility detected.', 'cab': (today_dt - timedelta(days=7)).strftime('%d/%m/%Y'), 'sched': (today_dt + timedelta(days=14)).strftime('%d/%m/%Y'), 'req': 'Infrastructure Manager', 'status': 'Approved'},
        {'id': 'CHG-005', 'title': 'Desktop Image Update — Windows 11', 'desc': 'Deploy updated Windows 11 desktop image including latest security patches and application versions.', 'type': 'Normal', 'priority': 'Medium', 'risk': 'Low', 'impact': 'User impact managed via phased rollout. Pilot group: 50 users, then full rollout.', 'rollback': 'Restore previous image version via SCCM. Time: 2 hours per site.', 'cab': (today_dt - timedelta(days=21)).strftime('%d/%m/%Y'), 'sched': (today_dt + timedelta(days=7)).strftime('%d/%m/%Y'), 'req': 'Desktop Support Lead', 'status': 'Approved'},
        {'id': 'CHG-006', 'title': 'Power Supply Replacement — UPS Battery', 'desc': 'Replace end-of-life UPS battery units in main data center. Requires scheduled power-down of non-critical systems.', 'type': 'Normal', 'priority': 'Low', 'risk': 'Low', 'impact': 'Non-critical systems powered down for 1 hour. Critical systems on redundant UPS.', 'rollback': 'Keep old batteries until new ones verified. Contingency generator on standby.', 'cab': 'N/A — CAB approved via email', 'sched': (today_dt + timedelta(days=45)).strftime('%d/%m/%Y'), 'req': 'Facilities Manager', 'status': 'Requested'},
    ]

    statuses = {'Requested': 0, 'Approved': 0, 'In Progress': 0, 'Implemented': 0, 'Closed': 0, 'Rolled Back': 0}
    for c in changes:
        st = c['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'change_manager': 'IT Change Manager',
        'changes': [
            {'change_id': c['id'], 'title': c['title'], 'description': c['desc'],
             'change_type': c['type'], 'priority': c['priority'], 'risk_level': c['risk'],
             'impact_assessment': c['impact'], 'rollback_plan': c['rollback'],
             'cab_date': c['cab'], 'scheduled_date': c['sched'], 'requestor': c['req'],
             'status': c['status']}
            for c in changes
        ],
        'summary': {
            'total_changes': len(changes),
            'requested': statuses['Requested'],
            'approved': statuses['Approved'],
            'in_progress': statuses['In Progress'],
            'implemented': statuses['Implemented'],
            'closed': statuses['Closed'],
            'rolled_back': statuses['Rolled Back'],
        },
    }


def generate_release_deployment_plan(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    releases = [
        {'id': 'REL-001', 'name': 'ERP v5.0 Major Release', 'scope': 'Complete ERP system upgrade including database migration, new UI framework, API v2, and reporting engine overhaul.', 'type': 'Major', 'planned': (today_dt + timedelta(days=30)).strftime('%d/%m/%Y'), 'window': '22:00 Saturday – 06:00 Sunday', 'rollback': 'Database restore + application binary rollback. Validated in DR test environment. Estimated: 4 hours.', 'status': 'Planned'},
        {'id': 'REL-002', 'name': 'Security Patch Bundle — April 2026', 'scope': 'Monthly security patches for Windows servers, Linux servers, network devices, and endpoints.', 'type': 'Patches', 'planned': (today_dt + timedelta(days=7)).strftime('%d/%m/%Y'), 'window': '20:00–00:00 Friday', 'rollback': 'WSUS rollback via group policy. Time: 1 hour.', 'status': 'Planned'},
        {'id': 'REL-003', 'name': 'VPN Gateway Upgrade', 'scope': 'Replace VPN gateway hardware. New appliance supports 2x throughput and modern encryption standards.', 'type': 'Minor', 'planned': (today_dt - timedelta(days=45)).strftime('%d/%m/%Y'), 'window': '22:00–02:00', 'rollback': 'Fail back to old gateway. Config already exported. Time: 30 min.', 'status': 'Deployed'},
        {'id': 'REL-004', 'name': 'Emergency TLS 1.2 Deprecation', 'scope': 'Emergency release to disable TLS 1.0/1.1 on all public-facing services. Required by compliance deadline.', 'type': 'Emergency', 'planned': (today_dt - timedelta(days=10)).strftime('%d/%m/%Y'), 'window': 'Immediate — rolling deployment across server groups', 'rollback': 'Re-enable TLS 1.1 via registry/config push. Time: 15 minutes per server group.', 'status': 'Deployed'},
        {'id': 'REL-005', 'name': 'Desktop Image v2026.1', 'scope': 'Updated Windows 11 desktop image with new application versions, security baseline, and driver updates.', 'type': 'Minor', 'planned': (today_dt + timedelta(days=14)).strftime('%d/%m/%Y'), 'window': 'Deploy via SCCM during business hours. Pilot: 50 users. Phased over 2 weeks.', 'rollback': 'Re-publish previous image version. Force reinstall on affected machines.', 'status': 'In Progress'},
        {'id': 'REL-006', 'name': 'SAN Firmware Update v7.2', 'scope': 'Critical firmware update for SAN controllers. Fixes known IO latency issue and security vulnerability.', 'type': 'Patches', 'planned': (today_dt + timedelta(days=21)).strftime('%d/%m/%Y'), 'window': '09:00–11:00 Sunday (maintenance window)', 'rollback': 'Boot from secondary controller with old firmware. Time: 15 minutes.', 'status': 'Planned'},
    ]

    statuses = {'Planned': 0, 'In Progress': 0, 'Deployed': 0, 'Rolled Back': 0, 'Cancelled': 0}
    for r in releases:
        st = r['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'release_manager': 'IT Release Manager',
        'releases': [
            {'release_id': r['id'], 'release_name': r['name'], 'scope': r['scope'],
             'release_type': r['type'], 'planned_date': r['planned'], 'deployment_window': r['window'],
             'rollback_procedure': r['rollback'], 'status': r['status']}
            for r in releases
        ],
        'summary': {
            'total_releases': len(releases),
            'planned': statuses['Planned'],
            'in_progress': statuses['In Progress'],
            'deployed': statuses['Deployed'],
            'rolled_back': statuses['Rolled Back'],
            'cancelled': statuses['Cancelled'],
        },
    }


def generate_incident_management_log(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    def fmt_dt(d):
        return d.strftime('%d/%m/%Y %H:%M')

    incidents = [
        {'id': 'INC-001', 'summary': 'ERP system unresponsive — all users unable to access finance and procurement modules', 'sev': 'P1 Critical', 'reported': fmt_dt(today_dt - timedelta(hours=4)), 'resolved': 'Open', 'svc': 'ERP System Hosting', 'res': 'Root cause identified as database lock contention. Rollback of bulk data import in progress.', 'status': 'In Progress'},
        {'id': 'INC-002', 'summary': 'Email delivery delay — messages queued for 30+ minutes', 'sev': 'P2 High', 'reported': fmt_dt(today_dt - timedelta(days=1, hours=3)), 'resolved': fmt_dt(today_dt - timedelta(days=1)), 'svc': 'Corporate Email', 'res': 'Mail queue cleared. Anti-spam filter rule corrected. Service restored within 45 minutes.', 'status': 'Resolved'},
        {'id': 'INC-003', 'summary': 'VPN service intermittently dropping connections', 'sev': 'P2 High', 'reported': fmt_dt(today_dt - timedelta(days=2)), 'resolved': fmt_dt(today_dt - timedelta(days=1, hours=12)), 'svc': 'Network Connectivity', 'res': 'VPN concentrator license limit reached. Additional licenses installed. Connection limit increased.', 'status': 'Resolved'},
        {'id': 'INC-004', 'summary': 'Single user unable to access file shares — permission error', 'sev': 'P4 Low', 'reported': fmt_dt(today_dt - timedelta(hours=2)), 'resolved': 'Open', 'svc': 'IT Help Desk', 'res': 'Assigned to IT Support Technician. Password reset and group membership refresh in progress.', 'status': 'New'},
        {'id': 'INC-005', 'summary': 'Backup job failed — SAN snapshot timeout', 'sev': 'P3 Medium', 'reported': fmt_dt(today_dt - timedelta(days=1)), 'resolved': fmt_dt(today_dt - timedelta(hours=6)), 'svc': 'Cloud Backup & DR', 'res': 'SAN controller firmware timeout issue. Backup window extended. Job re-ran successfully.', 'status': 'Closed'},
        {'id': 'INC-006', 'summary': 'Suspicious login attempts detected on admin portal', 'sev': 'P1 Critical', 'reported': fmt_dt(today_dt - timedelta(days=3)), 'resolved': fmt_dt(today_dt - timedelta(days=2, hours=18)), 'svc': 'Cybersecurity Monitoring', 'res': 'Source IP blocked. Credential reset for affected accounts. Investigation ongoing for data exfiltration.', 'status': 'Escalated'},
    ]

    sev_counts = {'P1 Critical': 0, 'P2 High': 0, 'P3 Medium': 0, 'P4 Low': 0}
    status_counts = {'New': 0, 'In Progress': 0, 'Resolved': 0, 'Closed': 0, 'Escalated': 0}
    resolved_times = []

    for inc in incidents:
        sv = inc['sev']
        if sv in sev_counts:
            sev_counts[sv] += 1
        st = inc['status']
        if st in status_counts:
            status_counts[st] += 1
        if inc['resolved'] != 'Open':
            try:
                r = datetime.strptime(inc['resolved'], '%d/%m/%Y %H:%M')
                rp = datetime.strptime(inc['reported'], '%d/%m/%Y %H:%M')
                resolved_times.append((r - rp).total_seconds() / 3600)
            except Exception as e:
                logger.warning("Failed to parse dates for incident %s: %s", inc.get('id'), e)

    avg_res = f'{sum(resolved_times) / len(resolved_times):.1f} hrs' if resolved_times else 'N/A'

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'incident_manager': 'IT Service Desk Manager',
        'incidents': [
            {'incident_id': i['id'], 'incident_summary': i['summary'], 'severity': i['sev'],
             'reported_date': i['reported'], 'resolved_date': i['resolved'],
             'affected_service': i['svc'], 'resolution': i['res'], 'status': i['status']}
            for i in incidents
        ],
        'summary': {
            'total_incidents': len(incidents),
            'critical': sev_counts['P1 Critical'],
            'high': sev_counts['P2 High'],
            'medium': sev_counts['P3 Medium'],
            'low': sev_counts['P4 Low'],
            'open': status_counts['New'] + status_counts['In Progress'],
            'resolved': status_counts['Resolved'] + status_counts['Closed'],
            'avg_resolution_time': avg_res,
        },
    }


def generate_problem_management_register(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    problems = [
        {'id': 'PRB-001', 'inc_refs': 'INC-001, INC-009', 'summary': 'ERP database lock contention causing intermittent system unavailability during peak batch processing windows', 'rc': 'Inadequate indexing on key transaction tables combined with inefficient query patterns in the new procurement module. Root cause confirmed via SQL Profiler analysis.', 'wa': 'Manual kill of blocking sessions. Schedule batch jobs outside peak hours as temporary measure.', 'fix': 'Query optimization patch for procurement module. Index rebuild on top 10 contended tables. Deployment planned with ERP v5.0 upgrade.', 'cat': 'Application', 'pri': 'Critical', 'status': 'Under Investigation'},
        {'id': 'PRB-002', 'inc_refs': 'INC-006, INC-012, INC-018', 'summary': 'Repeated brute-force login attempts targeting administrative interfaces', 'rc': 'Public-facing admin portals without IP rate limiting. Credential stuffing attack using previously compromised credentials from third-party data breaches.', 'wa': 'IP-based rate limiting implemented. Geo-blocking for non-operational regions.', 'fix': 'Deploy WAF with bot detection. Implement CAPTCHA on login pages. Enforce hardware MFA for all admin accounts.', 'cat': 'Security', 'pri': 'Critical', 'status': 'Known Error'},
        {'id': 'PRB-003', 'inc_refs': 'INC-003', 'summary': 'VPN concentrator reaching license limit during peak remote working hours', 'rc': 'Underestimated concurrent connection requirements. License pool was sized for 60% of workforce; actual remote usage is 85%.', 'wa': 'Temporary license addition (10 extra slots) while permanent solution is implemented.', 'fix': 'Upgrade VPN concentrator to higher-capacity model. Transition to cloud-based ZTNA solution for long-term scalability.', 'cat': 'Infrastructure', 'pri': 'High', 'status': 'Resolved'},
        {'id': 'PRB-004', 'inc_refs': 'INC-005', 'summary': 'SAN snapshot timeout causing backup job failures', 'rc': 'SAN controller firmware version has a known timeout issue when snapshot sizes exceed 500 GB. No workaround in current firmware.', 'wa': 'Split large volume backups into multiple smaller jobs. Extend backup window by 2 hours.', 'fix': 'SAN firmware upgrade to v7.2 (scheduled). Addresses timeout issue and improves snapshot performance by 40%.', 'cat': 'Infrastructure', 'pri': 'High', 'status': 'Known Error'},
        {'id': 'PRB-005', 'inc_refs': 'INC-015', 'summary': 'Print server memory leak causing weekly service restarts', 'rc': 'Legacy printer driver has known memory leak in spooler service. Vendor confirmed issue — no fix available for current driver version.', 'wa': 'Weekly scheduled restart of print spooler service. Script deployed to automate restart during low-usage periods.', 'fix': 'Replace affected printers with models supporting modern driver architecture. Migration plan approved.', 'cat': 'Process', 'pri': 'Medium', 'status': 'Known Error'},
        {'id': 'PRB-006', 'inc_refs': 'INC-020', 'summary': 'Intermittent WiFi disconnections on mobile devices in Building B', 'rc': 'AP density insufficient in high-occupancy areas. Channel overlap detected on 2.4 GHz band. Roaming settings suboptimal for mixed-vendor client devices.', 'wa': 'Reduce AP broadcast power to force client distribution. Enable band steering to 5 GHz.', 'fix': 'Add 4 additional APs in Building B conference areas. Site survey completed. Procurement in progress.', 'cat': 'Infrastructure', 'pri': 'Medium', 'status': 'Under Investigation'},
    ]

    pri_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    status_counts = {'Identified': 0, 'Under Investigation': 0, 'Known Error': 0, 'Resolved': 0, 'Closed': 0}
    for p in problems:
        pr = p['pri']
        if pr in pri_counts:
            pri_counts[pr] += 1
        st = p['status']
        if st in status_counts:
            status_counts[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'problem_manager': 'Problem Management Lead',
        'problems': [
            {'problem_id': p['id'], 'incident_refs': p['inc_refs'], 'problem_summary': p['summary'],
             'root_cause': p['rc'], 'workaround': p['wa'], 'permanent_fix': p['fix'],
             'category': p['cat'], 'priority': p['pri'], 'status': p['status']}
            for p in problems
        ],
        'summary': {
            'total_problems': len(problems),
            'critical': pri_counts['Critical'],
            'high': pri_counts['High'],
            'medium': pri_counts['Medium'],
            'low': pri_counts['Low'],
            'identified': status_counts['Identified'] + status_counts['Under Investigation'],
            'resolved': status_counts['Resolved'] + status_counts['Closed'],
        },
    }


def generate_service_continuity_plan(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    today_dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else _today()

    services = [
        {'id': 'SCP-001', 'name': 'Corporate Email & Collaboration', 'crit': 'Critical', 'rto': '2 hours', 'rpo': '15 minutes', 'strat': 'Active-active geographically redundant email servers. Automatic failover between data centers.', 'alt': 'Webmail access via secondary ISP. Mobile access via ActiveSync. Emergency comms via Teams mobile app.', 'test': (today_dt - timedelta(days=30)).strftime('%d/%m/%Y'), 'result': 'Pass', 'status': 'Ready'},
        {'id': 'SCP-002', 'name': 'ERP System', 'crit': 'Critical', 'rto': '4 hours', 'rpo': '1 hour', 'strat': 'Active-passive cluster with database replication. Manual failover to DR site. Validated quarterly.', 'alt': 'Manual order processing forms (paper-based). Offline Excel invoicing. Batch upload when system restored.', 'test': (today_dt - timedelta(days=60)).strftime('%d/%m/%Y'), 'result': 'Pass', 'status': 'Ready'},
        {'id': 'SCP-003', 'name': 'Network Infrastructure', 'crit': 'Critical', 'rto': '1 hour', 'rpo': 'N/A', 'strat': 'Redundant network paths. SD-WAN with automatic failover. LTE backup at key sites.', 'alt': '4G/5G failover via cellular routers. VPN concentrator at DR site. Pre-configured backup routers.', 'test': (today_dt - timedelta(days=90)).strftime('%d/%m/%Y'), 'result': 'Partial', 'status': 'Needs Review'},
        {'id': 'SCP-004', 'name': 'Data Backup & Recovery', 'crit': 'Critical', 'rto': '4 hours (restore)', 'rpo': '1 hour (backup frequency)', 'strat': 'Automated daily backups with off-site replication to geographically separate data center. Weekly DR test.', 'alt': 'Tape backups stored in fireproof safe (last resort). Restore times: 24 hours for full system.', 'test': (today_dt - timedelta(days=7)).strftime('%d/%m/%Y'), 'result': 'Pass', 'status': 'Ready'},
        {'id': 'SCP-005', 'name': 'IT Help Desk', 'crit': 'High', 'rto': '4 hours', 'rpo': 'N/A', 'strat': 'Cloud-based ITSM platform (no on-prem dependency). Agents can work remotely via VPN. Phone system auto-reroutes.', 'alt': 'Manual ticket logging via Excel. Emergency phone tree for critical issues. SMS-based status updates.', 'test': (today_dt - timedelta(days=45)).strftime('%d/%m/%Y'), 'result': 'Fail', 'status': 'Remediation Required'},
        {'id': 'SCP-006', 'name': 'Cybersecurity Operations', 'crit': 'Critical', 'rto': '30 minutes', 'rpo': 'Real-time', 'strat': '24/7 SOC with geographically distributed teams. SIEM platform with hot-hot architecture. Threat intel feeds from multiple sources.', 'alt': 'Manual log review procedures (reduced capability). Emergency contacts activated via phone tree.', 'test': (today_dt - timedelta(days=14)).strftime('%d/%m/%Y'), 'result': 'Pass', 'status': 'Ready'},
    ]

    statuses = {'Ready': 0, 'Needs Review': 0, 'Remediation Required': 0}
    for s in services:
        st = s['status']
        if st in statuses:
            statuses[st] += 1

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'plan_owner': 'IT Continuity Manager',
        'last_review_date': (today_dt - timedelta(days=30)).strftime('%d/%m/%Y'),
        'next_review_date': (today_dt + timedelta(days=335)).strftime('%d/%m/%Y'),
        'services': [
            {'service_id': s['id'], 'service_name': s['name'], 'criticality': s['crit'],
             'rto': s['rto'], 'rpo': s['rpo'], 'recovery_strategy': s['strat'],
             'alternative_arrangements': s['alt'], 'last_test_date': s['test'],
             'test_result': s['result'], 'status': s['status']}
            for s in services
        ],
        'summary': {
            'total_services': len(services),
            'ready': statuses['Ready'],
            'needs_review': statuses['Needs Review'],
            'remediation': statuses['Remediation Required'],
        },
    }


def generate_availability_management_report(data: dict) -> dict:
    standard_label = data.get('standard', 'ISO 20000-1:2018')
    client = data.get('client_name', 'Client')
    date = data.get('audit_date', _today_str())

    services = [
        {'id': 'AMR-001', 'name': 'Corporate Email & Collaboration', 'target': '99.9%', 'actual': '99.95%', 'downtime': '0.44 hours', 'outages': 1, 'mtbf': '720 hours', 'mttr': '0.44 hours', 'breach': 'No', 'notes': 'Single brief outage due to database maintenance. Exceeded target.'},
        {'id': 'AMR-002', 'name': 'ERP System', 'target': '99.7%', 'actual': '99.65%', 'downtime': '3.07 hours', 'outages': 2, 'mtbf': '360 hours', 'mttr': '1.53 hours', 'breach': 'Yes', 'notes': 'Two incidents: database lock contention (2.5 hrs) and scheduled patch overrun (0.57 hrs). SLA breached by 0.05% points.'},
        {'id': 'AMR-003', 'name': 'Network Infrastructure (Core)', 'target': '99.95%', 'actual': '99.98%', 'downtime': '0.18 hours', 'outages': 0, 'mtbf': 'N/A', 'mttr': 'N/A', 'breach': 'No', 'notes': 'No core network outages. Single BGP flap caused minor latency spike. Within SLA.'},
        {'id': 'AMR-004', 'name': 'Internet Connectivity', 'target': '99.8%', 'actual': '99.75%', 'downtime': '2.19 hours', 'outages': 3, 'mtbf': '240 hours', 'mttr': '0.73 hours', 'breach': 'Yes', 'notes': 'ISP-side routing issue caused 2 major outages. Secondary link activated. SLA credit claimed.'},
        {'id': 'AMR-005', 'name': 'IT Help Desk — Phone Service', 'target': '99.5%', 'actual': '99.8%', 'downtime': '1.75 hours', 'outages': 1, 'mtbf': 'N/A', 'mttr': '1.75 hours', 'breach': 'No', 'notes': 'VoIP provider maintenance. Call auto-routed to mobile backup within SLA.'},
        {'id': 'AMR-006', 'name': 'Cloud Backup Service', 'target': '99.9%', 'actual': '99.5%', 'downtime': '4.38 hours', 'outages': 2, 'mtbf': '360 hours', 'mttr': '2.19 hours', 'breach': 'Yes', 'notes': 'SAN snapshot timeout (3 hrs) and backup window overrun (1.38 hrs). Storage team engaged.'},
    ]

    met = sum(1 for s in services if s['breach'] == 'No')
    breached = sum(1 for s in services if s['breach'] == 'Yes')

    actual_vals = [float(s['actual'].rstrip('%')) for s in services]
    overall = f'{sum(actual_vals) / len(actual_vals):.2f}%'

    return {
        'client_name': client, 'date': date, 'standard': standard_label,
        'report_owner': 'Service Assurance Manager',
        'reporting_period': 'March 2026 (monthly)',
        'services': [
            {'service_id': s['id'], 'service_name': s['name'],
             'target_availability': s['target'], 'actual_availability': s['actual'],
             'downtime_hours': s['downtime'], 'number_of_outages': s['outages'],
             'mtbf': s['mtbf'], 'mttr': s['mttr'], 'sla_breached': s['breach'], 'notes': s['notes']}
            for s in services
        ],
        'summary': {
            'total_services': len(services),
            'sla_met': met,
            'sla_breached': breached,
            'overall_availability': overall,
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
    'Business_Impact_Analysis': generate_business_impact_analysis,
    'Records_of_Processing_Activities': generate_records_of_processing_activities,
    'Risk_Treatment_Plan': generate_risk_treatment_plan,
    'Incident_Investigation_Report': generate_incident_investigation_report,
    'Internal_Audit_Program': generate_internal_audit_program,
    'Environmental_Aspect_Register': generate_environmental_aspect_register,
    'Hazard_Identification_Register': generate_hazard_identification_register,
    'Energy_Review': generate_energy_review,
    'Compliance_Obligations_Register': generate_compliance_obligations_register,
    'Service_Portfolio': generate_service_portfolio,

    # ── ISO 20000-1 Service Management (10 new) ────────────────
    'Service_Catalogue': generate_service_catalogue,
    'Supplier_Agreement_Register': generate_supplier_agreement_register,
    'Business_Relationship_Register': generate_business_relationship_register,
    'Capacity_Management_Plan': generate_capacity_management_plan,
    'Change_Management_Register': generate_change_management_register,
    'Release_Deployment_Plan': generate_release_deployment_plan,
    'Incident_Management_Log': generate_incident_management_log,
    'Problem_Management_Register': generate_problem_management_register,
    'Service_Continuity_Plan': generate_service_continuity_plan,
    'Availability_Management_Report': generate_availability_management_report,
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
