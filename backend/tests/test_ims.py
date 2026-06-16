"""Tests for IMS Multi-Standard Support."""

from app.services.ims import (
    get_ims_mapping, get_integrated_clause_list, get_shared_docs,
    get_unique_requirements, generate_ims_gap_analysis,
)


class TestGetImsMapping:
    def test_known_pair_45001_14001(self):
        mapping = get_ims_mapping(['iso_45001', 'iso_14001'])
        assert mapping is not None
        assert mapping['name'] == 'IMS-OHS-ENV'
        assert 'clauses' in mapping

    def test_reversed_order(self):
        mapping = get_ims_mapping(['iso_14001', 'iso_45001'])
        assert mapping is not None
        assert mapping['name'] == 'IMS-OHS-ENV'

    def test_sorted_order(self):
        mapping = get_ims_mapping(['iso_14001', 'iso_9001'])
        assert mapping is not None
        assert mapping['name'] == 'IMS-Q-ENV'

    def test_unknown_pair_returns_none(self):
        mapping = get_ims_mapping(['iso_9001', 'iso_27001'])
        assert mapping is None

    def test_single_standard_returns_none(self):
        mapping = get_ims_mapping(['iso_9001'])
        assert mapping is None


class TestGetIntegratedClauseList:
    def test_known_pair_returns_clauses(self):
        clauses = get_integrated_clause_list(['iso_45001', 'iso_14001'])
        assert len(clauses) > 0
        assert all('clause' in c for c in clauses)
        assert all('title' in c for c in clauses)

    def test_contains_hls_clause_4_1(self):
        clauses = get_integrated_clause_list(['iso_45001', 'iso_14001'])
        clause_ids = [c['clause'] for c in clauses]
        assert '4.1' in clause_ids

    def test_unknown_pair_returns_empty(self):
        clauses = get_integrated_clause_list(['iso_9001', 'iso_27001'])
        assert clauses == []

    def test_clauses_sorted(self):
        clauses = get_integrated_clause_list(['iso_45001', 'iso_14001'])
        ids = [c['clause'] for c in clauses]
        expected = sorted(ids, key=lambda c: tuple(int(p) for p in c.split('.')))
        assert ids == expected

    def test_each_clause_has_mapping_field(self):
        clauses = get_integrated_clause_list(['iso_45001', 'iso_14001'])
        for c in clauses:
            assert 'mapping' in c


class TestGetSharedDocs:
    def test_known_pair_returns_shared_docs(self):
        docs = get_shared_docs(['iso_45001', 'iso_14001'])
        assert len(docs) > 0
        assert all('document' in d for d in docs)
        assert all('clause' in d for d in docs)

    def test_unknown_pair_returns_empty(self):
        docs = get_shared_docs(['iso_9001', 'iso_27001'])
        assert docs == []

    def test_shared_docs_have_standards_list(self):
        docs = get_shared_docs(['iso_45001', 'iso_14001'])
        for d in docs:
            assert 'standards' in d
            assert len(d['standards']) == 2


class TestGetUniqueRequirements:
    def test_known_pair_returns_dict(self):
        unique = get_unique_requirements(['iso_45001', 'iso_14001'])
        assert isinstance(unique, dict)
        for std in ['iso_45001', 'iso_14001']:
            assert std in unique
            assert isinstance(unique[std], list)

    def test_unknown_pair_returns_empty(self):
        unique = get_unique_requirements(['iso_9001', 'iso_27001'])
        assert unique == {}

    def test_unique_items_have_required_fields(self):
        unique = get_unique_requirements(['iso_45001', 'iso_14001'])
        for std, items in unique.items():
            for item in items:
                assert 'clause' in item
                assert 'title' in item
                assert 'note' in item


class TestGenerateImsGapAnalysis:
    def test_all_conformant(self):
        data = {'4.1': {'status': 'conformant', 'evidence': 'Docs reviewed'},
                '4.2': {'status': 'conformant', 'evidence': 'Stakeholder identified'}}
        result = generate_ims_gap_analysis(['iso_45001', 'iso_14001'], data)
        assert result['conformant'] >= 2
        assert result['nc'] == 0

    def test_mixed_statuses(self):
        data = {'4.1': {'status': 'conformant'},
                '4.2': {'status': 'nc'}}
        result = generate_ims_gap_analysis(['iso_45001', 'iso_14001'], data)
        assert result['conformant'] >= 1
        assert result['nc'] >= 1

    def test_all_not_reviewed(self):
        result = generate_ims_gap_analysis(['iso_45001', 'iso_14001'], {})
        assert result['not_reviewed'] > 0
        assert result['compliance_score'] == 0

    def test_unknown_pair_returns_fallback(self):
        result = generate_ims_gap_analysis(['iso_9001', 'iso_27001'], {})
        assert result['standards'] == ['iso_9001', 'iso_27001']
        assert result['readiness'] is not None

    def result_contains_all_keys(self):
        result = generate_ims_gap_analysis(['iso_45001', 'iso_14001'],
                                           {'4.1': {'status': 'conformant'}})
        for key in ('standards', 'ims_name', 'total_clauses', 'conformant',
                    'compliance_score', 'clauses', 'shared_docs',
                    'unique_requirements', 'readiness'):
            assert key in result
