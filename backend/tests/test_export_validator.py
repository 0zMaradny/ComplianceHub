"""Tests for the export validator module."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.export_validator import ExportValidator

VALID_AUDIT_REPORT = {
    'client_name': 'Test Corporation',
    'audit_date': '15/06/2026',
    'standard': 'ISO 9001:2015',
    'report_number': 'RP-2026-001',
    'scope': (
        'Quality management system for manufacturing operations at the main '
        'production facility including all processes.'
    ),
    'lead_auditor': 'John Smith',
    'findings_summary': (
        'A comprehensive audit was conducted across all applicable clauses of '
        'ISO 9001:2015. The organization demonstrated a mature quality management '
        'system with strong process controls. Audit evidence was gathered through '
        'interviews with personnel at all levels. Observation of operational processes '
        'and review of documented information confirmed the effectiveness of the system. '
        'The management review process was found to be driving continual improvement '
        'across the organization. Internal audit findings were properly addressed with '
        'corrective actions. The organization shows strong commitment to quality '
        'objectives and customer satisfaction. Leadership engagement and resource '
        'management were identified as key strengths.'
    ),
    'conclusion': (
        'The audit concluded that the quality management system is effectively '
        'implemented and maintained. The organization demonstrates conformity with '
        'ISO 9001:2015 requirements. Commitment to continual improvement and audit '
        'evidence confirms the system is achieving intended results. Certification '
        'should be maintained with observations addressed within the defined timeframe.'
    ),
    'methodology': {
        'approach': 'Process-based approach following PDCA cycle across all clauses',
        'sampling': 'Statistical sampling of records from each department',
        'criteria': 'ISO 9001:2015 requirements and organizational procedures',
        'methods': 'Interviews, document review, process observation, records analysis',
    },
    'findings': ['Finding 1: Document control', 'Finding 2: Internal audit', 'Finding 3: Management review'],
    'recommendations': ['Strengthen supplier evaluation', 'Enhance risk documentation'],
    'positive_findings': ['Leadership commitment', 'Effective corrective action', 'Employee awareness'],
    'opportunities_for_improvement': ['Digitalize quality records', 'Enhance communication'],
    'nonconformities': ['Minor NC: Document control procedure not fully followed'],
}

MINIMAL_VALID_AUDIT_REPORT = {
    'client_name': 'Test Corp',
    'audit_date': '15/06/2026',
    'standard': 'ISO 9001:2015',
    'report_number': 'RP-001',
    'scope': 'Quality management system for manufacturing facility.',
    'lead_auditor': 'John Smith',
    'findings_summary': (
        'A comprehensive audit was conducted across all applicable clauses of '
        'ISO 9001:2015. The organization demonstrated a mature quality management '
        'system with strong process controls. Audit evidence was gathered through '
        'interviews with personnel at all levels. Observation of operational processes '
        'confirmed the effectiveness of the system. The management review process was '
        'found to be driving continual improvement. Internal audit findings were '
        'properly addressed with corrective actions.'
    ),
    'conclusion': (
        'The audit concluded that the quality management system is effectively '
        'implemented and maintained. The organization demonstrates conformity with '
        'ISO 9001:2015 requirements. Certification should be maintained.'
    ),
    'methodology': {
        'approach': 'Process-based approach following PDCA cycle',
        'sampling': 'Statistical sampling of records',
        'criteria': 'ISO 9001:2015 requirements',
        'methods': 'Interviews and document review',
    },
    'findings': ['Finding 1', 'Finding 2', 'Finding 3'],
    'recommendations': ['Rec 1', 'Rec 2'],
    'positive_findings': ['PF 1', 'PF 2', 'PF 3'],
    'opportunities_for_improvement': ['OFI 1', 'OFI 2'],
    'nonconformities': ['NC 1'],
}


def test_validate_export_success():
    validator = ExportValidator('Audit_Report')
    is_valid, issues, score = validator.validate(VALID_AUDIT_REPORT)
    assert is_valid is True, f"Expected valid, got issues: {issues}"
    assert score >= 5.0, f"Score {score} below minimum 5.0"
    assert isinstance(issues, list)


def test_validate_export_success_minimal():
    validator = ExportValidator('Audit_Report')
    is_valid, issues, score = validator.validate(MINIMAL_VALID_AUDIT_REPORT)
    assert is_valid is True, f"Expected valid, got issues: {issues}"
    assert score >= 5.0


def test_validate_export_missing_required():
    validator = ExportValidator('Audit_Report')
    incomplete = {
        'client_name': 'Test Corp',
        'audit_date': '15/06/2026',
    }
    is_valid, issues, score = validator.validate(incomplete)
    assert is_valid is False or len(issues) > 0
    assert any('Missing' in i or 'required' in i.lower() for i in issues)


def test_validate_export_placeholder_detection():
    validator = ExportValidator('Audit_Report')
    output_with_placeholder = dict(MINIMAL_VALID_AUDIT_REPORT)
    output_with_placeholder['scope'] = 'Scope [TBD] placeholder still here'

    is_valid, issues, score = validator.validate(output_with_placeholder)
    assert any('Placeholder' in i for i in issues), f"Placeholder not detected: {issues}"
    assert score < 10.0


def test_validate_export_placeholder_multiple():
    validator = ExportValidator('Audit_Report')
    output = dict(MINIMAL_VALID_AUDIT_REPORT)
    output['findings_summary'] = 'Summary with [TBD] and [Company] placeholders'
    output['conclusion'] = 'Conclusion with N/A value'

    is_valid, issues, score = validator.validate(output)
    placeholder_issues = [i for i in issues if 'Placeholder' in i]
    assert len(placeholder_issues) >= 1


def test_quality_scoring():
    validator = ExportValidator('Audit_Report')
    is_valid, issues, score = validator.validate({})
    assert 0.0 <= score <= 10.0
    assert isinstance(score, float)


def test_quality_scoring_valid_output():
    validator = ExportValidator('Audit_Report')
    is_valid, issues, score = validator.validate(VALID_AUDIT_REPORT)
    assert 5.0 <= score <= 10.0


def test_quality_scoring_min_score_constant():
    assert hasattr(ExportValidator, '_score') or True
    from app.services.export_validator import EXPORT_MIN_SCORE, EXPORT_WARN_SCORE
    assert EXPORT_MIN_SCORE == 5.0
    assert EXPORT_WARN_SCORE == 7.0


def test_get_quality_report_structure():
    validator = ExportValidator('Audit_Report')
    report = validator.get_quality_report(VALID_AUDIT_REPORT, model_used='test_model')

    assert 'overall_score' in report
    assert 'structure_pass' in report
    assert 'content_depth_pass' in report
    assert 'item_counts_pass' in report
    assert 'terminology_pass' in report
    assert 'issues' in report
    assert 'recommendations' in report
    assert 'model_used' in report
    assert 'can_export' in report
    assert 'warnings' in report

    assert report['model_used'] == 'test_model'
    assert 0 <= report['overall_score'] <= 10


def test_get_quality_report_can_export():
    validator = ExportValidator('Audit_Report')
    report = validator.get_quality_report(MINIMAL_VALID_AUDIT_REPORT)
    assert report['can_export'] is True


def test_get_quality_report_recommendations():
    validator = ExportValidator('Audit_Report')
    report = validator.get_quality_report({})
    assert len(report['recommendations']) >= 1


def test_validate_with_iso_terminology_check():
    validator = ExportValidator('Audit_Report')
    output = dict(MINIMAL_VALID_AUDIT_REPORT)
    is_valid, issues, score = validator.validate(output)
    term_issues = [i for i in issues if 'ISO' in i or 'terminology' in i.lower()]
    assert len(term_issues) == 0, f"Unexpected terminology issues: {term_issues}"


def test_validate_no_iso_terms():
    validator = ExportValidator('Audit_Report')
    output = dict(MINIMAL_VALID_AUDIT_REPORT)
    output['findings_summary'] = 'A' * 350
    output['conclusion'] = 'B' * 160

    is_valid, issues, score = validator.validate(output)
    term_issues = [i for i in issues if 'ISO' in i or 'terminology' in i.lower()]
    assert any('terminology' in i.lower() for i in term_issues)
