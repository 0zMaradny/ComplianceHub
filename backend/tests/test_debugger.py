"""Tests for autodebugger — input/output validation, quality scoring, self-heal."""

from app.services.ai.debugger import Autodebugger


class TestValidateInput:
    def test_empty_prompt_fails(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_input('')
        assert len(errors) > 0
        assert 'empty' in errors[0].lower()

    def test_short_prompt_fails(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_input('Hi')
        assert len(errors) > 0

    def test_good_prompt_passes(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_input('Generate an audit report for ISO 9001')
        assert errors == []

    def test_short_system_prompt_fails(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_input('Good prompt', system_prompt='')
        assert len(errors) > 0


class TestValidateOutput:
    def test_missing_required_field(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_output({'client_name': ''})
        client_errors = [e for e in errors if 'client_name' in e]
        assert len(client_errors) > 0

    def test_wrong_field_type(self):
        d = Autodebugger('Audit_Plan_Stage_1')
        errors = d.validate_output({
            'client_name': 'Acme',
            'audit_date': '01/01/2025',
            'standard': 'ISO 9001',
            'stage': 'S1',
            'audit_team': 'not-a-list',
            'audit_objectives': ['obj1'],
            'audit_scope': 'full scope',
            'audit_criteria': ['criteria1'],
            'daily_schedule': [],
        })
        team_errors = [e for e in errors if 'audit_team' in e]
        assert len(team_errors) > 0

    def test_placeholder_detected(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_output({'client_name': '[Client Name]'})
        placeholder_errors = [e for e in errors if 'placeholder' in e.lower()]
        assert len(placeholder_errors) > 0

    def test_valid_output_passes(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_output({
            'client_name': 'Acme Corp',
            'audit_date': '01/01/2025',
            'standard': 'ISO 9001:2015',
            'report_number': 'TUV-AR-2025-001',
            'scope': 'Full quality management system',
            'lead_auditor': 'John Smith',
            'findings_summary': 'The audit found the system to be effective.',
            'conclusion': 'Recommended for certification.',
            'methodology': {'approach': 'A', 'sampling': 'B', 'criteria': 'C', 'methods': 'D'},
        })
        assert errors == []

    def test_error_in_result_is_reported(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_output({'error': 'Provider crashed'})
        assert len(errors) > 0

    def test_daily_schedule_missing_field(self):
        d = Autodebugger('Audit_Plan_Stage_1')
        errors = d.validate_output({
            'client_name': 'A', 'audit_date': 'd', 'standard': 's',
            'stage': 'S1', 'audit_team': [], 'audit_objectives': [],
            'audit_scope': 'x', 'audit_criteria': [],
            'daily_schedule': [{'day': 1, 'date': 'd', 'time': '9am'}],
        })
        missing = [e for e in errors if 'activity' in e.lower()]
        assert len(missing) > 0

    def test_schedule_fields_all_present_passes(self):
        d = Autodebugger('Audit_Plan_Stage_1')
        errors = d.validate_output({
            'client_name': 'A', 'audit_date': 'd', 'standard': 's',
            'stage': 'S1', 'audit_team': [], 'audit_objectives': [],
            'audit_scope': 'x', 'audit_criteria': [],
            'daily_schedule': [{'day': 1, 'date': 'd', 'time': '9am',
                                'activity': 'Opening meeting', 'auditee': 'Mgmt',
                                'auditor': 'Lead', 'clause': '4.1'}],
        })
        assert errors == []

    def test_checklist_sections_missing_fields(self):
        d = Autodebugger('ISO_Checklist')
        errors = d.validate_output({
            'client_name': 'A', 'audit_date': 'd', 'standard': 's',
            'sections': [{'clause': '4.1'}],
        })
        assert len(errors) > 0


class TestScoreQuality:
    def test_perfect_output_scores_high(self):
        d = Autodebugger('Audit_Report')
        score = d.score_quality({
            'client_name': 'Acme Corp',
            'audit_date': '01/01/2025',
            'standard': 'ISO 9001:2015',
            'report_number': 'TUV-AR-2025-001',
            'scope': 'Full quality management system review covering all processes.',
            'lead_auditor': 'John Smith',
            'findings_summary': 'The audit found the system to be effective. All processes were reviewed. Minor non-conformities were identified in document control. The management is committed to improvement.',
            'conclusion': 'Recommended for certification. The system meets all requirements. Conditions are minimal.',
            'methodology': {'approach': 'Process-based audit approach.', 'sampling': 'Statistical sampling applied.', 'criteria': 'ISO 9001:2015 requirements.', 'methods': 'Interviews, document review, observation.'},
        })
        assert score['overall'] >= 60

    def test_empty_output_scores_low(self):
        d = Autodebugger('Audit_Report')
        score = d.score_quality({})
        assert score['overall'] < 30

    def test_score_contains_expected_keys(self):
        d = Autodebugger('Audit_Report')
        score = d.score_quality({'client_name': 'A', 'audit_date': 'd',
                                  'standard': 's', 'report_number': 'n',
                                  'scope': 'x', 'lead_auditor': 'l',
                                  'findings_summary': 'y', 'conclusion': 'z',
                                  'methodology': {'approach': 'a', 'sampling': 'b',
                                                  'criteria': 'c', 'methods': 'd'}})
        for key in ('overall', 'fields', 'pass'):
            assert key in score
        for field in ('completeness', 'depth', 'integrity', 'relevance'):
            assert field in score['fields']


class TestValidateQuality:
    def test_short_field_fails(self):
        d = Autodebugger('Audit_Report')
        errors = d.validate_quality({
            'findings_summary': 'Short.',
            'conclusion': 'Bad.',
        })
        assert len(errors) > 0

    def test_few_items_fails(self):
        d = Autodebugger('Audit_Plan_Stage_1')
        errors = d.validate_quality({
            'daily_schedule': [{'activity': 'x', 'clause': '4.1'}],
        })
        items_errors = [e for e in errors if 'items' in e.lower()]
        assert len(items_errors) > 0

    def test_brief_evidence_fails_checklist(self):
        d = Autodebugger('ISO_Checklist')
        errors = d.validate_quality({
            'sections': [{'evidence': 'Ok.'}, {'evidence': 'Seen.'}, {'evidence': 'Good.'}],
        })
        assert len(errors) > 0


class TestSelfHeal:
    def test_input_validation_returns_error(self):
        d = Autodebugger('Audit_Report')
        provider_fn = lambda prompt, **kw: {}
        result = d.call_with_self_heal(provider_fn, '')
        assert 'error' in result
        assert 'empty' in result['error'].lower()

    def test_retries_on_bad_output(self):
        d = Autodebugger('Audit_Report')
        call_count = 0

        def bad_provider(prompt, **kw):
            nonlocal call_count
            call_count += 1
            return {'client_name': '', 'audit_date': 'd', 'standard': 's',
                    'report_number': 'n', 'scope': 'x', 'lead_auditor': 'l',
                    'findings_summary': 'summary', 'conclusion': 'conc',
                    'methodology': {'approach': 'a', 'sampling': 'b',
                                    'criteria': 'c', 'methods': 'd'}}

        result = d.call_with_self_heal(bad_provider, 'Generate an audit report please')
        assert '_validation_errors' in result or 'client_name' in result

    def test_audit_log_present(self):
        d = Autodebugger('Audit_Report')
        d.call_with_self_heal(lambda p, **kw: {}, 'A real prompt for testing.')
        assert len(d.audit_log) > 0

    def test_corrective_prompt_built(self):
        d = Autodebugger('Audit_Report')
        prompt = d.build_corrective_prompt('Original prompt', ['Missing field X'])
        assert 'Original prompt' in prompt
        assert 'Missing field X' in prompt
        assert 'CORRECTION' in prompt
