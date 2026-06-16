from app.services import clause_data


class TestWalkClauseTree:
    def test_top_level_hls(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '4')
        assert node is not None
        assert node.get('title') == 'Context of the Organization'

    def test_normal_nested_subclause(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '4.1')
        assert node is not None
        assert 'audit_questions' in node

    def test_flat_sibling_5_1_1(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '5.1.1')
        assert node is not None
        assert node.get('title') == 'General'

    def test_flat_sibling_9_1_1(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '9.1.1')
        assert node is not None
        assert node.get('title') == 'General'

    def test_annex_a_three_level(self):
        node = clause_data._walk_clause_tree(clause_data.ANNEX_A_27001, 'A.5.1')
        assert node is not None
        assert 'Information security' in node.get('title', '')

    def test_annex_a_three_level_8_23(self):
        node = clause_data._walk_clause_tree(clause_data.ANNEX_A_27001, 'A.8.23')
        assert node is not None
        assert node.get('title') == 'Web filtering'

    def test_non_existent_returns_none(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '99.99')
        assert node is None

    def test_non_existent_deep(self):
        node = clause_data._walk_clause_tree(clause_data.HLS_CORE, '5.1.99')
        assert node is None


class TestGetEvidenceForClause:
    def test_known_evidence_exists(self):
        ev = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, '4')
        assert isinstance(ev, list)

    def test_flat_sibling_returns_list(self):
        ev = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, '5.1.1')
        assert isinstance(ev, list)

    def test_non_existent_returns_empty_list(self):
        ev = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, '99.99')
        assert ev == []

    def test_annex_a_control(self):
        ev = clause_data.get_evidence_for_clause(
            clause_data.ANNEX_A_27001, 'A.8.23'
        )
        assert isinstance(ev, list)

    def test_top_level_10(self):
        ev = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, '10')
        assert isinstance(ev, list)

    def test_all_flat_siblings_resolvable(self):
        flat = clause_data.flatten_clauses(clause_data.HLS_CORE)
        for cid, _, _ in flat:
            parts = cid.split('.')
            if len(parts) < 3:
                continue
            ev = clause_data.get_evidence_for_clause(clause_data.HLS_CORE, cid)
            assert isinstance(ev, list), f'{cid}: expected list'

    def test_annex_a_enrichment_accessible(self):
        """Annex A sub-controls like A.5.1 must have audit_questions accessible."""
        node = clause_data._walk_clause_tree(clause_data.ANNEX_A_27001, 'A.5.1')
        assert node is not None
        assert 'audit_questions' in node
        assert len(node['audit_questions']) > 0

    def test_annex_a_all_controls_resolvable(self):
        """Every Annex A sub-control must be resolvable by _walk_clause_tree."""
        flat = clause_data.flatten_clauses(clause_data.ANNEX_A_27001)
        unresolved = []
        for cid, _, _ in flat:
            parts = cid.split('.')
            if len(parts) < 2:
                continue
            node = clause_data._walk_clause_tree(clause_data.ANNEX_A_27001, cid)
            if node is None:
                unresolved.append(cid)
        assert not unresolved, f'Unresolved: {unresolved}'
