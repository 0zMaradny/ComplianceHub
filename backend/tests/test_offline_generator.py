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
    _extract_client,
    _extract_standard,
    _extract_auditor,
    _extract_total_days,
    _extract_team,
    _key_for_standard,
    STANDARD_LABEL_MAP,
)


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
    def test_generate_all_creates_8_docs(self):
        results = generate_all(SAMPLE_NOTES, SAMPLE_MANDAY, ['ISO 9001:2015'], ['iso_9001'])
        assert len(results) == 12
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
        assert len(results) == 12
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
            assert len(results) == 12
            errors = [k for k, v in results.items() if 'error' in v]
            assert not errors, f'{std_key} errors: {errors}'
