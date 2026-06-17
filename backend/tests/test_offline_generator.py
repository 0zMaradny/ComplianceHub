from app.services.offline_generator import (
    generate_shared_context,
    generate_audit_plan_stage,
    generate_audit_report,
    generate_checklist,
    generate_certificate,
    generate_tnl,
    generate_certificate_text,
    generate_participation_list,
    generate_all,
    OFFLINE_GENERATORS,
    _get_clause_qa,
    _extract_client,
    _extract_standard,
    _extract_auditor,
    _extract_total_days,
    _extract_team,
    _extract_ncs,
    _extract_ofis,
    _extract_positives,
    _key_for_standard,
    STANDARD_LABEL_MAP,
)
from app.services import clause_data


SAMPLE_NOTES = """
Audit Plan for ISO 9001:2015
Client: Acme Corporation
Date: 15/06/2026
Lead Auditor: John Smith
Auditor - John Smith - 4
Scope: Quality management system
Total mandays: 6
"""

SAMPLE_MANDAY = """
Manday Calculation
Employee Count: 50
Final MD Calculation: 5.5 days
"""


class TestExtractHelpers:
    def test_extract_client(self):
        assert _extract_client('Client: Test Corp') == 'Test Corp'
        assert _extract_client('Company: Test Corp') == 'Test Corp'
        assert _extract_client('No match here') == 'Client'

    def test_extract_standard(self):
        assert 'ISO 9001:2015' in _extract_standard('ISO 9001:2015 audit')
        assert 'ISO 27001:2022' in _extract_standard('ISO 27001:2022')
        assert _extract_standard('no standard').startswith('ISO')

    def test_extract_auditor(self):
        assert _extract_auditor('Lead Auditor: Jane Doe') == 'Jane Doe'
        assert _extract_auditor('Auditor: Bob Smith') == 'Bob Smith'
        assert _extract_auditor('no match') == 'Lead Auditor'

    def test_extract_total_days(self):
        assert _extract_total_days('Total mandays: 8') == 8
        assert _extract_total_days('Total: 10') == 10
        assert _extract_total_days('No data') == 6

    def test_extract_team(self):
        team = _extract_team('John Smith - Lead Auditor - 4')
        assert len(team) == 1
        assert team[0]['name'] == 'John Smith'
        assert team[0]['role'] == 'Lead Auditor'
        assert team[0]['days'] == 4

    def test_extract_team_empty(self):
        assert _extract_team('no team data') == []


class TestKeyForStandard:
    def test_standard_key(self):
        assert _key_for_standard('ISO 9001:2015') == 'iso_9001'
        assert _key_for_standard('ISO 27001:2022') == 'iso_27001'
        assert _key_for_standard('ISO 31000:2018') == 'iso_31000'

    def test_unknown_defaults(self):
        assert _key_for_standard('ISO 99999') == 'iso_9001'

    def test_all_standards_mappable(self):
        for key, label in STANDARD_LABEL_MAP.items():
            resolved = _key_for_standard(label)
            assert resolved == key, f'{label} -> {resolved}, expected {key}'


class TestExtractFindings:
    def test_extract_ncs_simple(self):
        text = 'NC-Minor: Document control procedure not followed (Clause 7.5.3)\nNC-Major: Internal audit programme incomplete (Clause 9.2)'
        ncs = _extract_ncs(text)
        assert len(ncs) == 2
        assert ncs[0]['severity'] == 'Minor'
        assert ncs[0]['description'] == 'Document control procedure not followed'
        assert ncs[1]['severity'] == 'Major'
        assert ncs[1]['clause'] == '9.2'

    def test_extract_ncs_various_formats(self):
        text = 'Non-Conformity: Training records not maintained (Clause 7.2)\nFinding: No risk assessment for new process (Clause 6.1)'
        ncs = _extract_ncs(text)
        assert len(ncs) == 2
        assert ncs[0]['description'] == 'Training records not maintained'

    def test_extract_ncs_no_match(self):
        assert _extract_ncs('Everything is fine') == []

    def test_extract_ofis_simple(self):
        text = 'OFI: Consider automated monitoring (Clause 9.1)\nOpportunity for improvement: Enhance supplier evaluation (Clause 8.4)'
        ofis = _extract_ofis(text)
        assert len(ofis) == 2
        assert ofis[0]['description'] == 'Consider automated monitoring'

    def test_extract_positives_simple(self):
        text = 'Positive: Strong management commitment\nStrength: Well-documented procedures (Clause 7.5)'
        positives = _extract_positives(text)
        assert len(positives) == 2
        assert positives[0]['description'] == 'Strong management commitment'
        assert positives[1]['clause'] == '7.5'

    def test_extract_from_realistic_notes(self):
        text = """
Audit of ISO 9001:2015 at Acme Corp
Client: Acme Corporation
Lead Auditor: John Smith
Date: 15/06/2026

Findings:
1 NC-Minor: Calibration records for measuring equipment not up to date (Clause 7.1.5)
2 NC-Minor: Supplier evaluation not performed for 2 critical suppliers (Clause 8.4)
OFI: Consider implementing digital dashboard for real-time KPI monitoring (Clause 9.1)
Positive: Excellent quality culture and employee engagement
        """
        ncs = _extract_ncs(text)
        ofis = _extract_ofis(text)
        positives = _extract_positives(text)
        assert len(ncs) == 2
        assert len(ofis) == 1
        assert len(positives) == 1
        assert 'Calibration' in ncs[0]['description']
        assert 'digital dashboard' in ofis[0]['description']
        assert 'quality culture' in positives[0]['description']

    def test_findings_in_shared_context(self):
        text = """
Client: TestCorp
Date: 15/06/2026
Lead Auditor: John Smith
NC-Minor: Document control procedure not followed (Clause 7.5.3)
OFI: Enhance internal audit methodology (Clause 9.2)
Positive: Strong management commitment
        """
        ctx = generate_shared_context(text, 'Total: 4')
        assert len(ctx['extracted_ncs']) == 1
        assert len(ctx['extracted_ofis']) == 1
        assert len(ctx['extracted_positives']) == 1
        assert ctx['extracted_ncs'][0]['clause'] == '7.5.3'

    def test_no_findings_fallback(self):
        ctx = generate_shared_context('Client: Test\nDate: 01/06/2026\nLead Auditor: A', 'Total: 4')
        assert ctx['extracted_ncs'] == []
        assert ctx['extracted_ofis'] == []
        assert ctx['extracted_positives'] == []


class TestGenerateSharedContext:
    def test_basic_context(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        assert ctx['client_name'] == 'Acme Corporation'
        assert 'John Smith' in ctx.get('lead_auditor', '')
        assert ctx['standard_key'] == 'iso_9001'

    def test_context_with_manday_info(self):
        manday_info = {
            'total_mandays': 8.0,
            'team_composition': [
                {'role': 'Lead Auditor', 'count': 1, 'days': 4.0},
                {'role': 'Auditor', 'count': 2, 'days': 2.0},
            ],
        }
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY, manday_info)
        assert ctx['total_mandays'] == 8.0
        assert len(ctx['audit_team']) == 3

    def test_context_empty_text(self):
        ctx = generate_shared_context('', '')
        assert ctx['client_name'] == 'Client'
        assert ctx['standard_key'] == 'iso_9001'

    def test_context_has_all_keys(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        required = ['client_name', 'audit_date', 'standard', 'standard_key',
                     'lead_auditor', 'audit_team', 'total_mandays']
        for key in required:
            assert key in ctx, f'Missing key: {key}'


class TestGenerateFunctions:
    def test_all_generators_exist(self):
        expected = ['Audit_Plan_Stage_1', 'Audit_Plan_Stage_2', 'Participation_List',
                     'Audit_Report', 'ISO_Checklist', 'Certificate_Text', 'TNL', 'Certificate']
        for doc_type in expected:
            assert doc_type in OFFLINE_GENERATORS, f'Missing generator: {doc_type}'

    def test_generate_audit_plan_stage(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        plan = generate_audit_plan_stage(ctx, 'Stage 1 - Readiness Review')
        assert plan['client_name'] == 'Acme Corporation'
        assert 'schedule' in str(list(plan.keys())) or 'daily_schedule' in plan
        assert len(plan['audit_objectives']) > 0

    def test_generate_audit_report(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        report = generate_audit_report(ctx)
        assert report['client_name'] == 'Acme Corporation'
        assert 'findings_summary' in report
        assert 'nonconformities' in report
        assert 'conclusion' in report

    def test_generate_checklist(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        checklist = generate_checklist(ctx)
        assert 'sections' in checklist
        assert len(checklist['sections']) > 0
        first = checklist['sections'][0]
        assert 'clause' in first
        assert 'status' in first
        assert 'evidence' in first
        assert 'audit_questions' in first
        assert 'evidence_to_check' in first

    def test_checklist_enriched_fields_populated(self):
        for std_key in ('iso_9001', 'iso_27001', 'iso_14001'):
            ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
            ctx['standard_key'] = std_key
            ctx['standard'] = STANDARD_LABEL_MAP.get(std_key, 'ISO 9001:2015')
            checklist = generate_checklist(ctx)
            enriched = [s for s in checklist['sections'] if s.get('audit_questions') and s.get('evidence_to_check')]
            assert len(enriched) > 0, f'{std_key}: no enriched sections found'

    def test_flat_sibling_clause_qa_resolved(self):
        """Verify flat-sibling clause IDs like 5.1.1 (sibling of 5.1 in clause 5)
        are correctly resolved by _get_clause_qa."""
        flat = clause_data.flatten_clauses(clause_data.HLS_CORE)
        for cid, title, depth in flat:
            parts = cid.split('.')
            if len(parts) < 3:
                continue
            qs, ev = _get_clause_qa(clause_data.HLS_CORE, cid)
            assert qs or ev, f'{cid} ("{title}"): unresolved by _get_clause_qa'

    def test_flat_sibling_evidence_resolved(self):
        """Verify flat-sibling clause IDs are found by get_evidence_for_clause."""
        flat = clause_data.flatten_clauses(clause_data.HLS_CORE)
        for cid, title, depth in flat:
            parts = cid.split('.')
            if len(parts) < 3:
                continue
            result = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, cid)
            assert isinstance(result, list), f'{cid}: expected list, got {type(result)}'

    def test_generate_certificate(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        cert = generate_certificate(ctx)
        assert cert['client_name'] == 'Acme Corporation'
        assert cert['certification_decision'] in ('Certified', 'Conditional', 'Not Certified')
        assert 'issue_date' in cert
        assert 'expiry_date' in cert

    def test_generate_tnl(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        tnl = generate_tnl(ctx)
        assert tnl is not None

    def test_generate_certificate_text(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        ct = generate_certificate_text(ctx)
        assert ct is not None

    def test_generate_participation_list(self):
        ctx = generate_shared_context(SAMPLE_NOTES, SAMPLE_MANDAY)
        pl = generate_participation_list(ctx)
        assert pl is not None


class TestGenerateAll:
    def test_generate_all_creates_all_docs(self):
        results = generate_all(SAMPLE_NOTES, SAMPLE_MANDAY, ['ISO 9001:2015'], ['iso_9001'])
        assert len(results) == 32
        assert 'Audit_Plan_Stage_1' in results
        assert 'Audit_Plan_Stage_2' in results
        assert 'Audit_Report' in results
        assert 'ISO_Checklist' in results
        assert 'Certificate' in results

    def test_generate_all_with_manday_info(self):
        manday_info = {'total_mandays': 8.0, 'team_composition': [
            {'role': 'Lead Auditor', 'count': 1, 'days': 4.0},
        ]}
        results = generate_all(SAMPLE_NOTES, SAMPLE_MANDAY, ['ISO 9001:2015'], ['iso_9001'], manday_info)
        assert len(results) == 32
        for doc_type, doc_data in results.items():
            if 'error' in doc_data:
                continue
            if 'total_mandays' in doc_data:
                assert doc_data['total_mandays'] is not None

    def test_generate_all_no_errors(self):
        results = generate_all(SAMPLE_NOTES, SAMPLE_MANDAY, ['ISO 9001:2015'], ['iso_9001'])
        errors = [k for k, v in results.items() if 'error' in v]
        assert not errors, f'Errors: {errors}'

    def test_generate_all_all_standards(self):
        for std_key, std_label in STANDARD_LABEL_MAP.items():
            results = generate_all(SAMPLE_NOTES, SAMPLE_MANDAY, [std_label], [std_key])
            assert len(results) == 32
            errors = [k for k, v in results.items() if 'error' in v]
            assert not errors, f'{std_key} errors: {errors}'
