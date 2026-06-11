"""Tests for Doc Refiner — versioned single-field regeneration."""

from unittest.mock import patch, MagicMock

import pytest

from app.services.doc_refiner import (
    refine_field,
    bulk_refine,
    get_field_versions,
    get_refinable_fields,
    _seed_versions,
    REFINABLE_FIELDS,
    ALL_REFINABLE,
)


class TestRefinableFields:
    """Tests for the REFINABLE_FIELDS mapping."""

    def test_audit_report_has_expected_fields(self):
        assert 'findings_summary' in REFINABLE_FIELDS['Audit_Report']
        assert 'conclusion' in REFINABLE_FIELDS['Audit_Report']
        assert 'scope' in REFINABLE_FIELDS['Audit_Report']
        assert 'methodology' in REFINABLE_FIELDS['Audit_Report']

    def test_certificate_has_conditions(self):
        assert 'conditions' in REFINABLE_FIELDS['Certificate']

    def test_all_refinable_set_includes_all_fields(self):
        for fields in REFINABLE_FIELDS.values():
            for f in fields:
                assert f in ALL_REFINABLE

    def test_unknown_doc_type_returns_empty(self):
        assert get_refinable_fields('Nonexistent_Doc') == []

    def test_get_refinable_fields_returns_list(self):
        fields = get_refinable_fields('Audit_Report')
        assert isinstance(fields, list)
        assert len(fields) > 0


class TestSeedVersions:
    """Tests for _seed_versions — initializes version history."""

    def test_seeds_all_refinable_fields(self):
        doc_info = {'_created_at': 2000000.0}
        doc_data = {
            'findings_summary': 'Test findings',
            'scope': 'Test scope',
            'conclusion': 'Test conclusion',
        }
        _seed_versions(doc_info, doc_data)

        assert '_versions' in doc_info
        # Only fields present in doc_data get seeded
        assert 'findings_summary' in doc_info['_versions']
        assert 'scope' in doc_info['_versions']
        assert 'conclusion' in doc_info['_versions']
        assert doc_info['_versions']['findings_summary'][0]['instruction'] == 'original generation'
        assert doc_info['_versions']['findings_summary'][0]['value'] == 'Test findings'

    def test_does_not_overwrite_existing_versions(self):
        doc_info = {'_versions': {'existing': [{'value': 'old'}]}}
        _seed_versions(doc_info, {'findings_summary': 'val'})
        assert doc_info['_versions'] == {'existing': [{'value': 'old'}]}

    def test_skips_empty_values(self):
        doc_info = {}
        doc_data = {'findings_summary': ''}
        _seed_versions(doc_info, doc_data)
        assert 'findings_summary' not in doc_info.get('_versions', {})


class TestRefineField:
    """Tests for refine_field — single-field regeneration."""

    def _make_job(self):
        return {
            'results': {
                'Audit_Report': {
                    '_created_at': 1000000.0,
                    '_data': {
                        'client_name': 'Acme Corp',
                        'standard': 'iso_9001',
                        'scope': 'Quality management system',
                        'findings_summary': 'Minor issues found.',
                        'conclusion': 'Conditional recommendation.',
                    },
                },
            },
        }

    def test_doc_type_not_found_returns_error(self):
        result = refine_field(self._make_job(), 'Nonexistent', 'scope', 'make better')
        assert 'error' in result
        assert 'not found' in result['error']

    def test_field_not_refinable_returns_error(self):
        result = refine_field(self._make_job(), 'Audit_Report', 'employee_count', 'fix it')
        assert 'error' in result
        assert 'not refinable' in result['error']

    def test_no_data_returns_error(self):
        job = {'results': {'Audit_Report': {'_data': None}}}
        result = refine_field(job, 'Audit_Report', 'scope', 'fix it')
        assert 'error' in result

    def test_successful_refinement(self):
        mock_router = MagicMock()
        mock_router.return_value = {'text': '{"new_value": "Improved scope statement"}'}
        job = self._make_job()

        with patch('app.services.doc_refiner.router_generate', mock_router):
            result = refine_field(job, 'Audit_Report', 'scope', 'Make it more detailed')

        assert result['field'] == 'scope'
        assert result['new_value'] == 'Improved scope statement'
        assert result['previous_value'] == 'Quality management system'
        assert 'error' not in result
        assert job['results']['Audit_Report']['_data']['scope'] == 'Improved scope statement'

    def test_refinement_stores_version(self):
        mock_router = MagicMock()
        mock_router.return_value = {'text': '{"new_value": "v2 scope"}'}
        job = self._make_job()

        with patch('app.services.doc_refiner.router_generate', mock_router):
            refine_field(job, 'Audit_Report', 'scope', 'Update scope')

        versions = job['results']['Audit_Report']['_versions']
        assert 'scope' in versions
        assert versions['scope'][-1]['value'] == 'v2 scope'
        assert versions['scope'][-1]['instruction'] == 'Update scope'

    def test_router_error_returned(self):
        mock_router = MagicMock()
        mock_router.return_value = {'error': 'All providers failed'}

        with patch('app.services.doc_refiner.router_generate', mock_router):
            result = refine_field(self._make_job(), 'Audit_Report', 'scope', 'fix')

        assert 'error' in result
        assert 'All providers failed' in result['error']

    def test_list_field_converted_to_string(self):
        mock_router = MagicMock()
        mock_router.return_value = {'text': '{"new_value": "item1\\nitem2"}'}

        job = {
            'results': {
                'ISO_Checklist': {
                    '_data': {
                        'sections': ['Clause 4', 'Clause 5'],
                        'standard': 'iso_9001',
                    },
                },
            },
        }

        with patch('app.services.doc_refiner.router_generate', mock_router):
            result = refine_field(job, 'ISO_Checklist', 'sections', 'Add Clause 6')

        assert result['new_value'] == 'item1\nitem2'
        assert 'error' not in result

    def test_exception_during_refinement(self):
        mock_router = MagicMock()
        mock_router.side_effect = ValueError('Unexpected error')

        with patch('app.services.doc_refiner.router_generate', mock_router):
            result = refine_field(self._make_job(), 'Audit_Report', 'scope', 'fix')

        assert 'error' in result
        assert 'Unexpected error' in result['error']

    def test_no_change_returns_current_value(self):
        mock_router = MagicMock()
        mock_router.return_value = {'text': '{"new_value": "Quality management system"}'}

        with patch('app.services.doc_refiner.router_generate', mock_router):
            result = refine_field(self._make_job(), 'Audit_Report', 'scope', 'keep same')

        assert result['new_value'] == 'Quality management system'
        assert 'No change needed' in result.get('info', '')


class TestGetFieldVersions:
    """Tests for get_field_versions — version history retrieval."""

    def _make_job(self):
        return {
            'results': {
                'Audit_Report': {
                    '_created_at': 1000000.0,
                    '_data': {
                        'client_name': 'Acme Corp',
                        'standard': 'iso_9001',
                        'scope': 'Quality management system',
                    },
                },
            },
        }

    def test_returns_versions_for_field(self):
        job = {
            'results': {
                'Audit_Report': {
                    '_versions': {
                        'scope': [
                            {'value': 'v1', 'timestamp': 1.0, 'instruction': 'original'},
                            {'value': 'v2', 'timestamp': 2.0, 'instruction': 'refined'},
                        ],
                    },
                },
            },
        }
        versions = get_field_versions(job, 'Audit_Report', 'scope')
        assert len(versions) == 2
        assert versions[0]['value'] == 'v1'
        assert versions[1]['instruction'] == 'refined'

    def test_no_versions_returns_empty_list(self):
        versions = get_field_versions(self._make_job(), 'Audit_Report', 'scope')
        assert versions == []

    def test_doc_not_found_returns_empty_list(self):
        versions = get_field_versions(self._make_job(), 'Nonexistent', 'scope')
        assert versions == []

    def test_field_not_found_returns_empty_list(self):
        job = {
            'results': {
                'Audit_Report': {
                    '_versions': {'conclusion': [{'value': 'ok'}]},
                },
            },
        }
        versions = get_field_versions(job, 'Audit_Report', 'scope')
        assert versions == []


class TestBulkRefine:
    def test_bulk_refine_no_refinable_fields(self):
        from app.services.doc_refiner import bulk_refine
        result = bulk_refine({'results': {}}, 'Unknown_Doc', 'improve')
        assert result['error'] == 'No refinable fields for Unknown_Doc'
        assert result['total'] == 0

    def test_bulk_refine_refines_all_fields(self, monkeypatch):
        from app.services.doc_refiner import bulk_refine
        def mock_generate(*a, **kw):
            return {'text': '{"new_value": "Improved content"}'}
        monkeypatch.setattr('app.services.doc_refiner.router_generate', mock_generate)
        doc_data = {
            'standard': 'iso_9001', 'client_name': 'TestCo',
            'findings_summary': 'Old findings', 'conclusion': 'Old conclusion',
            'scope': 'Old scope', 'methodology': 'Old methods',
        }
        job_data = {
            'results': {
                'Audit_Report': {'_data': doc_data},
            },
        }
        result = bulk_refine(job_data, 'Audit_Report', 'improve everything')
        assert result['total'] == 4
        assert result['succeeded'] == 4
        assert result['failed'] == 0
        assert len(result['results']) == 4
