"""Tests for the bilingual text constants module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.bilingual import (
    CONFIDENTIALITY,
    COVER_LABELS,
    HEADINGS,
    METHODOLOGY,
    SECTION_HEADERS,
    TABLE_HEADERS,
    t,
)

EXPECTED_HEADING_KEYS = [
    'audit_objectives',
    'audit_scope',
    'audit_criteria',
    'audit_team',
    'daily_schedule',
    'confidentiality',
    'language_report',
    'general_info',
    'executive_summary',
    'key_strengths',
    'audit_methodology',
    'approach',
    'sampling',
    'criteria',
    'methods',
    'detailed_findings',
    'positive_findings',
    'ofi',
    'nonconformities',
    'conclusion',
    'checklist_results',
    'overall_assessment',
    'certificate_details',
    'attendance_record',
    'nc_observation_log',
    'summary',
    'notes',
    'table_of_contents',
]


def test_all_english_keys_exist():
    for key in EXPECTED_HEADING_KEYS:
        assert key in HEADINGS['en'], f"Missing EN heading: {key}"
        val = HEADINGS['en'][key]
        assert isinstance(val, str) and len(val) > 0


def test_all_arabic_keys_exist():
    for key in EXPECTED_HEADING_KEYS:
        assert key in HEADINGS['ar'], f"Missing AR heading: {key}"
        val = HEADINGS['ar'][key]
        assert isinstance(val, str) and len(val) > 0


def test_bilingual_heading_keys_match():
    assert set(HEADINGS['en'].keys()) == set(HEADINGS['ar'].keys())


def test_cover_labels_keys():
    for lang in ('en', 'ar'):
        labels = COVER_LABELS[lang]
        assert 'client' in labels, f"Missing 'client' in {lang}"
        assert 'standard' in labels, f"Missing 'standard' in {lang}"
        assert 'date' in labels, f"Missing 'date' in {lang}"
        assert 'lead_auditor' in labels, f"Missing 'lead_auditor' in {lang}"
        assert 'confidential' in labels
        assert 'scope' in labels
        assert 'certification_body' in labels


def test_cover_labels_translation():
    assert COVER_LABELS['en']['client'] == 'Client'
    assert COVER_LABELS['ar']['client'] == 'العميل'
    assert COVER_LABELS['en']['standard'] == 'Standard'
    assert COVER_LABELS['ar']['standard'] == 'المواصفة'
    assert COVER_LABELS['en']['lead_auditor'] == 'Lead Auditor'
    assert COVER_LABELS['ar']['lead_auditor'] == 'المراجع الرئيسي'


def test_table_headers_completeness():
    en_keys = set(TABLE_HEADERS['en'].keys())
    ar_keys = set(TABLE_HEADERS['ar'].keys())
    assert en_keys == ar_keys, f"Key mismatch: EN={en_keys - ar_keys}, AR={ar_keys - en_keys}"

    for key in en_keys:
        en_headers = TABLE_HEADERS['en'][key]
        ar_headers = TABLE_HEADERS['ar'][key]
        assert len(en_headers) == len(ar_headers), (
            f"Header count mismatch for '{key}': "
            f"EN={len(en_headers)}, AR={len(ar_headers)}"
        )
        assert all(isinstance(h, str) and h for h in en_headers)
        assert all(isinstance(h, str) and h for h in ar_headers)


def test_table_headers_known_keys():
    known = {'tnl', 'audit_team', 'daily_schedule', 'participants', 'nc_table', 'certificate_fields'}
    for lang in ('en', 'ar'):
        for key in known:
            assert key in TABLE_HEADERS[lang], f"Missing TABLE_HEADERS['{lang}']['{key}']"


def test_methodology_content():
    for lang in ('en', 'ar'):
        methodology = METHODOLOGY[lang]
        assert 'approach' in methodology
        assert 'sampling' in methodology
        assert 'criteria' in methodology
        assert 'methods' in methodology

        for key in ('approach', 'sampling', 'criteria', 'methods'):
            val = methodology[key]
            assert isinstance(val, str), f"{lang}.{key} should be a string"
            assert len(val) > 50, f"{lang}.{key} is too short ({len(val)} chars)"
        assert '{standard}' in methodology['approach'], f"{lang}.approach missing '{{standard}}' placeholder"
        assert '{standard}' in methodology['criteria'], f"{lang}.criteria missing '{{standard}}' placeholder"


def test_confidentiality_present():
    assert 'en' in CONFIDENTIALITY
    assert 'ar' in CONFIDENTIALITY
    assert len(CONFIDENTIALITY['en']) > 20
    assert len(CONFIDENTIALITY['ar']) > 20


def test_section_headers_present():
    expected = {'checklist_qa', 'checklist_findings', 'checklist_qa_ar', 'checklist_findings_ar'}
    assert expected.issubset(SECTION_HEADERS.keys())


def test_t_helper():
    result_en = t('audit_objectives', 'en')
    assert result_en == '1. Audit Objectives'

    result_ar = t('audit_objectives', 'ar')
    assert result_ar == '1. أهداف المراجعة'


def test_t_helper_custom_category():
    result = t('client', 'en', 'COVER_LABELS')
    assert result == 'Client'

    result_ar = t('client', 'ar', 'COVER_LABELS')
    assert result_ar == 'العميل'


def test_t_helper_fallback():
    result = t('nonexistent_key', 'en')
    assert result == 'nonexistent_key'

    result_ar = t('nonexistent_key', 'ar')
    assert result_ar == 'nonexistent_key'
