"""Tests for the client configuration module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.client_config import (
    CLIENTS,
    ClientConfig,
    RiskFormulas,
    VisualIdentity,
    get_client,
    get_client_by_doc_code,
    get_doc_code,
    list_clients,
    validate_client_data,
)

EXPECTED_CLIENTS = {'msd_moi', 'uacc', 'sagco', 'al_ahsa'}


def test_get_client_config_msd_moi():
    client = get_client('msd_moi')
    assert client is not None
    assert client.key == 'msd_moi'
    assert client.language == 'ar'
    assert client.doc_code_prefix == 'MSD-MOI-GRC-'
    assert 'iso_22301' in client.standards
    assert 'iso_31000' in client.standards

    assert client.visual.rtl is True
    assert client.visual.primary_header == '#004D26'
    assert client.visual.accent == '#C8A96E'
    assert client.visual.data_row_alt == '#E8F5E9'

    assert client.formulas.latent_risk == 'S = O × Q'
    assert client.formulas.residual_risk == 'V = S × (1 − U/4)'
    assert client.formulas.rating_method == 'VLOOKUP Treatment Plan'
    assert client.formulas.treatment_lookup == 'VLOOKUP by Risk ID'


def test_get_client_config_uacc():
    client = get_client('uacc')
    assert client is not None
    assert client.key == 'uacc'
    assert client.language == 'en'
    assert client.doc_code_prefix == 'UACC-EnMS-'
    assert client.standards == ['iso_50001']
    assert client.name == 'UACC (Umm Alqura Cement Company — Taif Plant)'
    assert client.name_ar == 'شركة أسمنت أم القرى — مصنع الطائف'

    assert client.visual.rtl is False
    assert client.visual.primary_header == '#003D7A'
    assert client.visual.accent == '#C00000'

    assert client.formulas.latent_risk == ''
    assert client.formulas.residual_risk == ''
    assert client.formulas.rating_method == 'L × S'
    assert client.formulas.treatment_lookup == 'Nested IF Risk Level'


def test_get_client_sagco():
    client = get_client('sagco')
    assert client is not None
    assert client.doc_code_prefix == 'SAGCO-'
    assert 'iso_45001' in client.standards
    assert 'iso_14001' in client.standards


def test_get_client_al_ahsa():
    client = get_client('al_ahsa')
    assert client is not None
    assert client.language == 'ar'
    assert client.standards == ['iso_27001']
    assert client.visual.rtl is True


def test_resolve_client_known():
    client = get_client('msd_moi')
    assert isinstance(client, ClientConfig)
    assert client.language == 'ar'
    assert client.visual.rtl is True

    client = get_client('uacc')
    assert isinstance(client, ClientConfig)
    assert client.language == 'en'
    assert client.visual.rtl is False


def test_resolve_client_default():
    client = get_client('nonexistent_unknown')
    assert client is None


def test_list_clients():
    result = list_clients()
    assert isinstance(result, list)
    keys = {c['key'] for c in result}
    assert keys == EXPECTED_CLIENTS

    for entry in result:
        assert 'name' in entry
        assert 'name_ar' in entry
        assert 'doc_code_prefix' in entry
        assert 'language' in entry
        assert 'standards' in entry
        assert 'description' in entry


def test_get_doc_code_known_client():
    code = get_doc_code('msd_moi', 'RR', 1)
    assert code == 'MSD-MOI-GRC-RR-001'

    code = get_doc_code('uacc', 'BIA', 5)
    assert code == 'UACC-EnMS-BIA-005'

    code = get_doc_code('sagco', 'RA', 12)
    assert code == 'SAGCO-RA-012'

    code = get_doc_code('al_ahsa', 'ISMS', 3)
    assert code == 'ALAHSA-ISMS-ISMS-003'


def test_get_doc_code_unknown_client():
    code = get_doc_code('nonexistent', 'RR', 1)
    assert code == 'UNKNOWN-RR-001'


def test_get_client_by_doc_code():
    client = get_client_by_doc_code('MSD-MOI-GRC-RR-001')
    assert client is not None
    assert client.key == 'msd_moi'

    client = get_client_by_doc_code('UACC-EnMS-BIA-005')
    assert client is not None
    assert client.key == 'uacc'

    client = get_client_by_doc_code('SAGCO-RA-012')
    assert client is not None
    assert client.key == 'sagco'

    client = get_client_by_doc_code('ALAHSA-ISMS-ISMS-003')
    assert client is not None
    assert client.key == 'al_ahsa'


def test_get_client_by_doc_code_not_found():
    client = get_client_by_doc_code('UNKNOWN-PREFIX-001')
    assert client is None


def test_validate_client_data_success():
    errors = validate_client_data('msd_moi', {
        'doc_code': 'MSD-MOI-GRC-RR-001',
        'standard': 'ISO 22301',
    })
    assert errors == []

    errors = validate_client_data('uacc', {
        'doc_code': 'UACC-EnMS-BIA-001',
        'standard': 'ISO 50001:2018',
    })
    assert errors == []


def test_validate_client_data_wrong_prefix():
    errors = validate_client_data('msd_moi', {
        'doc_code': 'UACC-EnMS-RR-001',
    })
    assert len(errors) == 1
    assert 'doc code' in errors[0].lower()
    assert 'MSD-MOI-GRC-' in errors[0]


def test_validate_client_data_wrong_standard():
    errors = validate_client_data('msd_moi', {
        'doc_code': 'MSD-MOI-GRC-RR-001',
        'standard': 'ISO 27001',
    })
    assert len(errors) == 1
    assert 'standard' in errors[0].lower()
    assert 'iso_22301' in errors[0] or 'iso_31000' in errors[0]


def test_validate_client_data_unknown_client():
    errors = validate_client_data('nonexistent', {})
    assert len(errors) == 1
    assert 'unknown client' in errors[0].lower()


def test_formula_templates():
    for client_key in ('msd_moi', 'uacc', 'sagco', 'al_ahsa'):
        client = get_client(client_key)
        formulas = client.formulas
        if formulas.latent_risk:
            assert isinstance(formulas.latent_risk, str)
        if formulas.residual_risk:
            assert isinstance(formulas.residual_risk, str)
        if formulas.rating_method:
            assert isinstance(formulas.rating_method, str)
            assert formulas.rating_method != 'TBD' or client_key == 'sagco'
        if formulas.treatment_lookup:
            assert isinstance(formulas.treatment_lookup, str)


def test_formula_templates_msd_moi():
    client = get_client('msd_moi')
    assert 'S' in client.formulas.latent_risk
    assert 'O' in client.formulas.latent_risk
    assert 'Q' in client.formulas.latent_risk
    assert 'V' in client.formulas.residual_risk
    assert 'S' in client.formulas.residual_risk
    assert 'U' in client.formulas.residual_risk


def test_formula_templates_uacc():
    client = get_client('uacc')
    assert client.formulas.rating_method == 'L × S'
    assert 'L' in client.formulas.rating_method
    assert 'S' in client.formulas.rating_method


def test_visual_defaults():
    default = VisualIdentity()
    assert default.primary_header == '#003D7A'
    assert default.accent == '#C00000'
    assert default.secondary == '#1A3D7A'
    assert default.data_row_alt == '#F2F2F2'
    assert default.layout == 'A4'
    assert default.rtl is False


def test_risk_formulas_defaults():
    default = RiskFormulas()
    assert default.latent_risk == ''
    assert default.residual_risk == ''
    assert default.rating_method == ''
    assert default.treatment_lookup == ''


def test_all_clients_have_required_attrs():
    for key, client in CLIENTS.items():
        assert isinstance(client.key, str) and client.key
        assert isinstance(client.name, str) and client.name
        assert isinstance(client.doc_code_prefix, str)
        assert client.language in ('en', 'ar', 'bidi')
        assert isinstance(client.standards, list)
        assert all(isinstance(s, str) for s in client.standards)
        assert isinstance(client.formulas, RiskFormulas)
        assert isinstance(client.visual, VisualIdentity)


def test_all_clients_have_doc_code_prefix():
    for key, client in CLIENTS.items():
        assert client.doc_code_prefix, f"Client {key} missing doc_code_prefix"
