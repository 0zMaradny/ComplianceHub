"""Tests for AI pipeline — prompt building and document generation."""

from unittest.mock import patch

from app.services.ai_pipeline import (
    _get_standard_key, _build_family_context, _build_manday_summary,
    _build_shared_prompt, _build_prompt, generate_document,
)


class TestGetStandardKey:
    def test_exact_match(self):
        assert _get_standard_key('ISO 9001:2015') == 'iso_9001'

    def test_prefix_match(self):
        assert _get_standard_key('ISO 27001') == 'iso_27001'

    def test_known_prefix(self):
        assert _get_standard_key('ISO 14001:2015 — Environmental') == 'iso_14001'

    def test_unknown_returns_none(self):
        assert _get_standard_key('UNKNOWN_STANDARD') is None

    def test_45001(self):
        assert _get_standard_key('ISO 45001:2018') == 'iso_45001'

    def test_42001(self):
        assert _get_standard_key('ISO 42001') == 'iso_42001'


class TestBuildMandaySummary:
    def test_empty_info_returns_empty(self):
        assert _build_manday_summary(None) == ''
        assert _build_manday_summary({}) == ''

    def test_audit_type_included(self):
        result = _build_manday_summary({'audit_type': 'initial'})
        assert 'initial' in result

    def test_total_mandays(self):
        result = _build_manday_summary({'total_mandays': 10})
        assert '10' in result

    def test_per_standard(self):
        result = _build_manday_summary({'mandays_per_standard': {'iso_9001': 5}})
        assert 'iso_9001' in result
        assert '5' in result

    def test_audit_team(self):
        result = _build_manday_summary({
            'audit_team': [{'name': 'John', 'role': 'Lead', 'days': 3}]
        })
        assert 'John' in result
        assert 'Lead' in result
        assert '3' in result

    def test_ims_reduction(self):
        result = _build_manday_summary({'ims_reduction': '20%'})
        assert '20%' in result

    def test_full_summary(self):
        info = {
            'audit_type': 'initial',
            'total_mandays': 15,
            'mandays_per_standard': {'iso_9001': 8, 'iso_14001': 7},
            'audit_team': [{'name': 'A', 'role': 'Lead', 'days': 5}],
            'ims_reduction': '10%',
            'employee_count': 200,
            'site_count': 3,
        }
        result = _build_manday_summary(info)
        for keyword in ('initial', '15', 'iso_9001', 'iso_14001', '10%', '200', '3'):
            assert keyword in result


class TestBuildSharedPrompt:
    def test_returns_formatted_string(self):
        result = _build_shared_prompt('Notes text here', 'Manday data here')
        assert isinstance(result, str)
        assert 'Notes text here' in result
        assert 'Manday data here' in result

    def test_truncates_notes_at_15000(self):
        notes = 'x' * 20000
        result = _build_shared_prompt(notes, 'short')
        assert len(result) < 16000

    def test_truncates_manday_at_8000(self):
        manday = 'y' * 10000
        result = _build_shared_prompt('short', manday)
        assert 'y' * 8000 in result
        assert 'y' * 10000 not in result


class TestBuildFamilyContext:
    def test_returns_string(self):
        result = _build_family_context(['iso_9001'])
        assert isinstance(result, str)

    def test_unknown_standard_returns_empty(self):
        result = _build_family_context(['unknown_standard'])
        assert result == ''

    def test_empty_list_returns_empty(self):
        result = _build_family_context([])
        assert result == ''


class TestBuildPrompt:
    def test_returns_string(self):
        result = _build_prompt('notes', 'manday', ['iso_9001'], 'Audit_Report')
        assert isinstance(result, str)
        assert 'notes' in result
        assert 'manday' in result

    def test_doc_type_included(self):
        result = _build_prompt('n', 'm', ['iso_9001'], 'Audit_Report')
        assert 'Audit Report' in result or 'audit_report' in result.lower()

    def test_shared_context_injected(self):
        result = _build_prompt('n', 'm', ['iso_9001'], 'Audit_Report',
                               shared_context={'client_name': 'Acme'})
        assert 'Acme' in result

    def test_manday_info_included(self):
        result = _build_prompt('n', 'm', ['iso_9001'], 'Audit_Report',
                               manday_info={'audit_type': 'surveillance'})
        assert 'surveillance' in result


class TestGenerateDocument:
    def test_calls_router_generate(self):
        with patch('app.services.ai_pipeline.router_generate',
                   return_value={'result': 'ok'}) as mock:
            result = generate_document('api_key', 'notes', 'manday',
                                       ['iso_9001'], 'Audit_Report')
            assert result == {'result': 'ok'}
            mock.assert_called_once()

    def test_passes_correct_doc_type(self):
        with patch('app.services.ai_pipeline.router_generate',
                   return_value={}) as mock:
            generate_document('key', 'n', 'm', ['iso_9001'], 'ISO_Checklist')
            args, kwargs = mock.call_args
            assert args[0] == 'ISO_Checklist'

    def test_shared_context_forwarded(self):
        with patch('app.services.ai_pipeline.router_generate',
                   return_value={}) as mock:
            generate_document('key', 'n', 'm', ['iso_9001'], 'Audit_Report',
                              shared_context={'client_name': 'Test'})
            args, kwargs = mock.call_args
            assert kwargs.get('client_key') is None

    def test_client_key_forwarded(self):
        with patch('app.services.ai_pipeline.router_generate',
                   return_value={}) as mock:
            generate_document('key', 'n', 'm', ['iso_9001'], 'Audit_Report',
                              client_key='acme-corp')
            _, kwargs = mock.call_args
            assert kwargs.get('client_key') == 'acme-corp'
