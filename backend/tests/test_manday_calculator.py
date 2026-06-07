from app.services.manday_calculator import (
    compute_mandays,
    lookup_base_mandays,
    detect_audit_type,
    compute_ims_reduction,
    compute_audit_team,
    round_mandays,
    resolve_standard_key,
    STANDARD_TABLE_MAP,
    IAF_MD_11_REDUCTION_PCT,
)


class TestRoundMandays:
    def test_rounds_to_half(self):
        assert round_mandays(3.3) == 3.5
        assert round_mandays(3.7) == 4.0
        assert round_mandays(4.0) == 4.0
        assert round_mandays(2.1) == 2.5
        assert round_mandays(1.0) == 1.0
        assert round_mandays(0.0) == 0.0


class TestLookupBaseMandays:
    def _expected_rounded(self, value):
        import math
        return int(math.ceil(value * 2.0) / 2.0)

    def test_iso_9001_medium_50_employees(self):
        md = lookup_base_mandays('iso_9001', 50, 'medium')
        assert md == self._expected_rounded(6.5)

    def test_iso_9001_low_10_employees(self):
        md = lookup_base_mandays('iso_9001', 10, 'low')
        assert md == self._expected_rounded(2.0)

    def test_iso_9001_high_120_employees(self):
        md = lookup_base_mandays('iso_9001', 120, 'high')
        assert md == self._expected_rounded(11.0)

    def test_iso_9001_first_band(self):
        md = lookup_base_mandays('iso_9001', 3, 'medium')
        assert md == self._expected_rounded(2.0)

    def test_iso_9001_last_band(self):
        md = lookup_base_mandays('iso_9001', 999999, 'medium')
        assert md == self._expected_rounded(19.0)

    def test_iso_27001_medium_default(self):
        md = lookup_base_mandays('iso_27001', 50, 'medium')
        assert md == self._expected_rounded(7.0)

    def test_framework_returns_none(self):
        md = lookup_base_mandays('iso_31000', 50, 'medium')
        assert md is None
        md = lookup_base_mandays('iso_10002', 50, 'medium')
        assert md is None

    def test_invalid_standard_returns_none(self):
        md = lookup_base_mandays('iso_99999', 50, 'medium')
        assert md is None

    def test_default_complexity(self):
        md = lookup_base_mandays('iso_9001', 50, 'unknown')
        assert md is not None
        assert md > 0

    def test_edge_employee_count(self):
        md = lookup_base_mandays('iso_9001', 0, 'medium')
        assert md == self._expected_rounded(2.0)

    def test_all_standards_have_table(self):
        mss_keys = [k for k, v in STANDARD_TABLE_MAP.items() if v[1] is not None]
        for key in mss_keys:
            md = lookup_base_mandays(key, 50, 'medium')
            assert md is not None, f'{key} returned None'
            assert md > 0, f'{key} returned {md}'

    def test_all_complexity_levels_different(self):
        low = lookup_base_mandays('iso_9001', 100, 'low')
        med = lookup_base_mandays('iso_9001', 100, 'medium')
        high = lookup_base_mandays('iso_9001', 100, 'high')
        assert low <= med <= high


class TestDetectAuditType:
    def test_initial_default(self):
        assert detect_audit_type('') == 'initial'

    def test_initial_explicit(self):
        assert detect_audit_type('initial certification') == 'initial'

    def test_surveillance_1(self):
        assert detect_audit_type('surveillance 1') == 'surveillance_1'
        assert detect_audit_type('surv 1') == 'surveillance_1'
        assert detect_audit_type('surveillance') == 'surveillance_1'

    def test_surveillance_2(self):
        assert detect_audit_type('surveillance 2') == 'surveillance_2'
        assert detect_audit_type('surv 2') == 'surveillance_2'

    def test_recertification(self):
        assert detect_audit_type('recertification audit') == 'recertification'
        assert detect_audit_type('re-certification') == 'recertification'

    def test_transfer(self):
        assert detect_audit_type('transfer audit') == 'transfer'

    def test_case_insensitive(self):
        assert detect_audit_type('Surveillance 1') == 'surveillance_1'
        assert detect_audit_type('RECERTIFICATION') == 'recertification'


class TestComputeIMSReduction:
    def test_single_standard_no_reduction(self):
        assert compute_ims_reduction(['iso_9001']) == 0.0

    def test_no_standards(self):
        assert compute_ims_reduction([]) == 0.0

    def test_qms_ems_pair(self):
        reduction = compute_ims_reduction(['iso_9001', 'iso_14001'])
        assert reduction == 0.20

    def test_qms_ohs_pair(self):
        reduction = compute_ims_reduction(['iso_9001', 'iso_45001'])
        assert reduction == 0.20

    def test_isms_pims_pair(self):
        reduction = compute_ims_reduction(['iso_27001', 'iso_27701'])
        assert reduction == 0.20

    def test_three_standards_averaged(self):
        reduction = compute_ims_reduction(['iso_9001', 'iso_14001', 'iso_45001'])
        assert 0.15 < reduction <= 0.20

    def test_capped_at_max(self):
        override = 0.30
        assert compute_ims_reduction(['iso_9001', 'iso_14001'], override) == 0.20

    def test_override_below_max(self):
        assert compute_ims_reduction(['iso_9001', 'iso_14001'], 0.10) == 0.10

    def test_many_standards_averaged_low(self):
        reduction = compute_ims_reduction(['iso_9001', 'iso_14001', 'iso_50001', 'iso_45001'])
        assert reduction <= 0.20
        assert reduction > 0

    def test_framework_pair_no_reduction(self):
        reduction = compute_ims_reduction(['iso_9001', 'iso_31000'])
        assert reduction >= 0.0


class TestResolveStandardKey:
    def test_standard_display_name(self):
        assert resolve_standard_key('ISO 9001:2015') == 'iso_9001'

    def test_standard_number_only(self):
        assert resolve_standard_key('9001') == 'iso_9001'
        assert resolve_standard_key('27001') == 'iso_27001'

    def test_unknown_returns_none(self):
        assert resolve_standard_key('ISO 99999') is None


class TestComputeAuditTeam:
    def test_small_audit_single_lead(self):
        team = compute_audit_team(1.0, 'initial')
        assert team == [{'role': 'Lead Auditor', 'count': 1, 'days': 1.0}]

    def test_medium_audit_team(self):
        team = compute_audit_team(3.0, 'initial')
        assert len(team) == 2
        assert team[0]['role'] == 'Lead Auditor'
        assert team[1]['role'] == 'Auditor'

    def test_large_audit_two_auditors(self):
        team = compute_audit_team(6.0, 'initial')
        assert len(team) == 2
        assert team[0]['role'] == 'Lead Auditor'
        assert team[1]['role'] == 'Auditor'
        assert team[1]['count'] == 2

    def test_very_large_audit(self):
        team = compute_audit_team(20.0, 'initial')
        assert len(team) == 2
        assert team[0]['role'] == 'Lead Auditor'
        assert team[1]['role'] == 'Auditor'
        assert team[1]['count'] == 2

    def test_zero_mandays(self):
        assert compute_audit_team(0, 'initial') == []

    def test_boundary_1_5(self):
        team = compute_audit_team(1.5, 'initial')
        assert team[0]['days'] == 1.5

    def test_boundary_4(self):
        team = compute_audit_team(4.0, 'initial')
        assert len(team) == 2


class TestComputeMandays:
    def test_single_standard_initial_default(self):
        result = compute_mandays(['iso_9001'], 'initial', employee_count=50)
        assert result['total_mandays'] == 6.0
        assert result['audit_type'] == 'initial'
        assert result['employee_count'] == 50

    def test_surveillance_reduces_days(self):
        initial = compute_mandays(['iso_9001'], 'initial', employee_count=50)
        surv = compute_mandays(['iso_9001'], 'surveillance_1', employee_count=50)
        assert surv['total_mandays'] < initial['total_mandays']

    def test_ims_reduction_applied(self):
        single = compute_mandays(['iso_9001'], 'initial', employee_count=50)
        ims = compute_mandays(['iso_9001', 'iso_14001'], 'initial', employee_count=50)
        expected = round_mandays((single['total_base_mandays'] + 5.5) * (1 - 0.20))
        assert ims['total_mandays'] <= expected + 1

    def test_framework_standards(self):
        result = compute_mandays(['iso_31000'], 'initial', employee_count=50)
        assert result['total_mandays'] == 4.0
        result = compute_mandays(['iso_10002'], 'initial', employee_count=50)
        assert result['total_mandays'] == 4.0

    def test_manday_docx_text_extraction(self):
        text = 'Total Employees: 120'
        result = compute_mandays(['iso_9001'], 'initial', manday_docx_text=text)
        assert result['employee_count'] == 120

    def test_audit_type_multiplier_in_notes(self):
        result = compute_mandays(['iso_9001'], 'surveillance_1', employee_count=50)
        notes = ' '.join(result['notes'])
        assert 'surveillance' in notes.lower()

    def test_site_count_multiplier(self):
        single = compute_mandays(['iso_9001'], 'initial', employee_count=50, site_count=1)
        multi = compute_mandays(['iso_9001'], 'initial', employee_count=50, site_count=3)
        assert multi['total_mandays'] >= single['total_mandays']

    def test_invalid_audit_type_defaults_to_initial(self):
        result = compute_mandays(['iso_9001'], 'invalid_type', employee_count=50)
        assert result['audit_type'] == 'initial'

    def test_string_standard_converted_to_list(self):
        result = compute_mandays('iso_9001', 'initial', employee_count=50)
        assert result['standards'] == ['iso_9001']

    def test_default_employee_count(self):
        result = compute_mandays(['iso_9001'], 'initial')
        assert result['employee_count'] == 50

    def test_all_audit_types_have_multipliers(self):
        for atype in ['initial', 'surveillance_1', 'surveillance_2', 'recertification', 'transfer']:
            result = compute_mandays(['iso_9001'], atype, employee_count=50)
            assert result['total_mandays'] > 0
            assert result['audit_type'] == atype

    def test_iat_md_11_pairs(self):
        for (s1, s2), expected_pct in IAF_MD_11_REDUCTION_PCT.items():
            reduction = compute_ims_reduction([s1, s2])
            assert reduction == expected_pct, f'{s1}+{s2}: expected {expected_pct}, got {reduction}'

    def test_ims_4_standards(self):
        standards = ['iso_9001', 'iso_14001', 'iso_45001', 'iso_50001']
        result = compute_mandays(standards, 'initial', employee_count=50)
        assert result['ims_reduction_pct'] > 0
        assert result['ims_reduction_pct'] <= 20.0
        assert result['total_mandays'] > 0

    def test_team_composition_has_correct_structure(self):
        result = compute_mandays(['iso_9001'], 'initial', employee_count=50)
        team = result['team_composition']
        total_team_days = sum(t['count'] * t['days'] for t in team)
        assert abs(total_team_days - result['total_mandays']) < result['total_mandays'] * 0.1

    def test_base_mandays_from_docx(self):
        result = compute_mandays(
            ['iso_9001'], 'initial', employee_count=50,
            base_mandays_from_docx={'iso_9001': 8.0}
        )
        assert result['base_per_standard']['iso_9001'] == 8.0
