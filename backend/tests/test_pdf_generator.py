"""Unit tests for the PDF generator."""
import os, tempfile, shutil

from app.services.pdf_generator import (
    generate_pdf_file, AuditPDF, GENERATORS, safe_str,
    generate_audit_plan_stage_1, generate_audit_plan_stage_2,
    generate_participation_list, generate_audit_report,
    generate_iso_checklist, generate_certificate_text,
    generate_tnl, generate_certificate,
)


def _minimal_data(overrides=None):
    d = {
        'client_name': 'Test Corp',
        'audit_date': '01/06/2026',
        'standard': 'ISO 9001:2015',
        'lead_auditor': 'John Smith',
        'scope': 'QMS for manufacturing',
    }
    if overrides:
        d.update(overrides)
    return d


def _tmpdir():
    return tempfile.mkdtemp()


class TestAuditPDF:
    def test_pdf_creates_valid_output(self):
        pdf = AuditPDF('Test', 'ISO 9001:2015')
        pdf.add_page()
        pdf.set_font('Sans', '', 12)
        pdf.cell(0, 10, 'Hello')
        path = os.path.join(_tmpdir(), 'test.pdf')
        pdf.output(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 1000

    def test_cover_page_renders(self):
        pdf = AuditPDF('Cover Test', 'ISO 9001:2015')
        pdf.cover_page('TEST DOCUMENT', 'Client A', '01/06/2026', 'ISO 9001:2015',
                        [('Ref', 'TUV-001')])
        path = os.path.join(_tmpdir(), 'cover.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 2000

    def test_section_title_renders(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.section_title('Section 1')
        path = os.path.join(_tmpdir(), 'section.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_body_text_renders(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.body_text('This is a test paragraph with multiple sentences of content.')
        path = os.path.join(_tmpdir(), 'body.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_bullet_renders(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.bullet('Bullet point item')
        path = os.path.join(_tmpdir(), 'bullet.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_kv_row_renders(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.kv_row('Name', 'Value')
        path = os.path.join(_tmpdir(), 'kv.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_table_header_and_row_render(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.table_header([(40, 'Name'), (80, 'Role'), (30, 'Days')])
        pdf.table_row([(40, 'Alice'), (80, 'Lead Auditor'), (30, '5')])
        pdf.table_row([(40, 'Bob'), (80, 'Auditor'), (30, '3')], fill=True)
        path = os.path.join(_tmpdir(), 'table.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_status_badge_colors(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        for status in ('Conformant', 'Non-Conformant', 'Partially Conformant',
                       'Not Reviewed', 'Certified', 'Conditional', 'Not Certified'):
            pdf.status_badge(status)
            pdf.ln()
        path = os.path.join(_tmpdir(), 'badges.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000

    def test_info_block_skips_missing_keys(self):
        pdf = AuditPDF('Test')
        pdf.add_page()
        pdf.info_block({'client_name': 'ACME'}, ['client_name', 'missing_key', 'also_missing'])
        path = os.path.join(_tmpdir(), 'infoblock.pdf')
        pdf.output(path)
        assert os.path.getsize(path) > 1000


class TestGeneratorFunctions:
    def test_all_8_generators_registered(self):
        expected = [
            'Audit_Plan_Stage_1', 'Audit_Plan_Stage_2', 'Participation_List',
            'Audit_Report', 'ISO_Checklist', 'Certificate_Text', 'TNL', 'Certificate',
        ]
        for dt in expected:
            assert dt in GENERATORS, f'{dt} missing from GENERATORS'

    def test_generate_pdf_file_unknown_type(self):
        result = generate_pdf_file('UnknownType', _minimal_data(), _tmpdir())
        assert result is None

    def test_generate_pdf_file_returns_path(self):
        d = _tmpdir()
        result = generate_pdf_file('Certificate', _minimal_data(), d)
        assert result is not None
        assert os.path.exists(result)
        assert result.endswith('.pdf')
        shutil.rmtree(d, ignore_errors=True)

    def test_generate_pdf_file_filename_format(self):
        d = _tmpdir()
        result = generate_pdf_file('Certificate', _minimal_data({'client_name': 'ACME Corp'}), d)
        fname = os.path.basename(result)
        assert fname.startswith('Certificate_')
        assert 'ACME' in fname
        assert fname.endswith('.pdf')
        shutil.rmtree(d, ignore_errors=True)

    def test_generate_pdf_file_safe_name_sanitized(self):
        d = _tmpdir()
        result = generate_pdf_file('Certificate', _minimal_data({'client_name': 'ACME/Corp\\Test'}), d)
        fname = os.path.basename(result)
        assert '/' not in fname
        assert '\\' not in fname
        shutil.rmtree(d, ignore_errors=True)

    def test_generate_pdf_default_client_name(self):
        d = _tmpdir()
        result = generate_pdf_file('Certificate', {}, d)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestAuditPlanStage1:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'plan1.pdf')
        data = _minimal_data({
            'stage': 'Stage 1 - Readiness Review', 'language': 'English',
            'report_date': '15/06/2026',
            'audit_team': [{'name': 'JS', 'role': 'Lead', 'days': 3}],
            'audit_objectives': ['Verify readiness for certification'],
            'audit_criteria': ['ISO 9001:2015 clauses 4-10'],
            'daily_schedule': [{'day': 1, 'date': '01/06', 'time': '09:00',
                                'activity': 'Opening Meeting', 'auditee': 'Management',
                                'auditor': 'JS', 'clause': '4.1'}],
            'confidentiality': 'All information confidential',
        })
        result = generate_audit_plan_stage_1(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_minimal_data(self):
        d = _tmpdir()
        path = os.path.join(d, 'plan1.pdf')
        data = _minimal_data({'stage': 'Stage 1'})
        result = generate_audit_plan_stage_1(data, path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestAuditPlanStage2:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'plan2.pdf')
        data = _minimal_data({
            'stage': 'Stage 2 - Certification Audit', 'language': 'English',
            'report_date': '15/06/2026',
            'audit_team': [{'name': 'JS', 'role': 'Lead', 'days': 5}],
            'audit_objectives': ['Assess conformity'], 'audit_criteria': ['ISO 9001:2015'],
            'daily_schedule': [{'day': 1, 'date': '02/06', 'time': '09:00',
                                'activity': 'Opening', 'auditee': 'Mgmt',
                                'auditor': 'JS', 'clause': '4.1'}],
            'confidentiality': 'Confidential',
        })
        result = generate_audit_plan_stage_2(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)


class TestParticipationList:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'participants.pdf')
        data = _minimal_data({
            'participants': [
                {'name': 'Alice', 'company': 'Test Corp', 'department': 'QA',
                 'closing_meeting': 'Yes', 'signature': ''},
            ],
            'notes': 'All attendees present',
        })
        result = generate_participation_list(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_no_participants(self):
        d = _tmpdir()
        path = os.path.join(d, 'participants.pdf')
        result = generate_participation_list(_minimal_data(), path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestAuditReport:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'report.pdf')
        data = _minimal_data({
            'report_number': 'TUV-AR-2026-001', 'report_date': '15/06/2026',
            'audit_team': [{'name': 'JS', 'role': 'Lead', 'days': 5}],
            'methodology': {'approach': 'Process', 'sampling': 'ISO 19011',
                            'criteria': 'ISO 9001:2015', 'methods': 'Interviews'},
            'findings_summary': 'The QMS is effectively implemented.',
            'positive_findings': ['Strong management commitment'],
            'opportunities_for_improvement': ['Enhance risk analysis'],
            'nonconformities': [{'clause': '7.1', 'severity': 'Minor',
                                 'description': 'Resource gap found',
                                 'due_date': '01/08/2026'}],
            'conclusion': 'Recommend certification.',
        })
        result = generate_audit_report(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_no_nonconformities(self):
        d = _tmpdir()
        path = os.path.join(d, 'report.pdf')
        result = generate_audit_report(_minimal_data({
            'report_number': 'TUV-AR-2026-002', 'report_date': '15/06/2026',
            'methodology': {'approach': 'Process', 'sampling': 'ISO 19011',
                            'criteria': '', 'methods': ''},
            'findings_summary': 'All good.',
            'positive_findings': [], 'opportunities_for_improvement': [],
            'nonconformities': [], 'conclusion': 'Certify.',
        }), path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestISOChecklist:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'checklist.pdf')
        data = _minimal_data({
            'auditor': 'John Smith',
            'sections': [
                {'clause': '4.1', 'title': 'Context', 'requirement': 'Org shall determine...',
                 'status': 'Conformant', 'evidence': 'Docs reviewed', 'notes': '', 'reference': '',
                 'audit_questions': 'How are external issues identified?',
                 'evidence_to_check': 'Strategic planning docs'},
                {'clause': '4.2', 'title': 'Interested Parties', 'requirement': 'Org shall determine...',
                 'status': 'Partially Conformant', 'evidence': 'In progress', 'notes': '', 'reference': '',
                 'audit_questions': 'How are stakeholder needs monitored?',
                 'evidence_to_check': 'Stakeholder register'},
            ],
            'overall_assessment': 'Systems are compliant overall.',
        })
        result = generate_iso_checklist(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_no_sections(self):
        d = _tmpdir()
        path = os.path.join(d, 'checklist.pdf')
        result = generate_iso_checklist(_minimal_data({'auditor': 'John'}), path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestCertificateText:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'cert_text.pdf')
        data = _minimal_data({
            'certificate_number': 'TUV-2026-001',
            'certification_body': 'TUV AUSTRIA',
            'certification_decision': 'Certified',
            'issue_date': '01/06/2026',
            'expiry_date': '31/05/2029',
            'authorized_signatory': 'Jane Doe',
        })
        result = generate_certificate_text(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_conditional_decision(self):
        d = _tmpdir()
        path = os.path.join(d, 'cert_text.pdf')
        data = _minimal_data({
            'certificate_number': 'TUV-2026-002',
            'certification_body': 'TUV AUSTRIA',
            'certification_decision': 'Conditional',
            'issue_date': '01/06/2026', 'expiry_date': '31/05/2029',
            'authorized_signatory': 'Jane Doe',
        })
        result = generate_certificate_text(data, path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestTNL:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'tnl.pdf')
        data = _minimal_data({
            'entries': [
                {'tnl_number': 'TNL-001', 'clause': '7.1', 'type': 'NC',
                 'description': 'Gap found in training records',
                 'severity': 'Minor', 'auditee': 'Alice',
                 'due_date': '01/08/2026', 'status': 'Open'},
            ],
            'summary': {'total_nc': 1, 'major': 0, 'minor': 1, 'ofi': 0, 'observations': 0},
        })
        result = generate_tnl(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_empty_entries(self):
        d = _tmpdir()
        path = os.path.join(d, 'tnl.pdf')
        result = generate_tnl(_minimal_data(), path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestCertificate:
    def test_generates_valid_pdf(self):
        d = _tmpdir()
        path = os.path.join(d, 'cert.pdf')
        data = _minimal_data({
            'certificate_number': 'TUV-2026-001',
            'certification_body': 'TUV AUSTRIA',
            'certification_decision': 'Certified',
            'issue_date': '01/06/2026', 'expiry_date': '31/05/2029',
            'authorized_signatory': 'Jane Doe',
            'conditions': ['Subject to annual surveillance', 'Valid only for scope above'],
        })
        result = generate_certificate(data, path)
        assert result is not None
        assert os.path.getsize(result) > 5000
        shutil.rmtree(d, ignore_errors=True)

    def test_no_conditions(self):
        d = _tmpdir()
        path = os.path.join(d, 'cert.pdf')
        data = _minimal_data({
            'certificate_number': 'TUV-2026-002',
            'certification_body': 'TUV AUSTRIA',
            'certification_decision': 'Not Certified',
            'issue_date': '01/06/2026', 'expiry_date': '31/05/2029',
            'authorized_signatory': 'Jane Doe',
            'conditions': [],
        })
        result = generate_certificate(data, path)
        assert result is not None
        shutil.rmtree(d, ignore_errors=True)


class TestSafeStr:
    def test_none(self):
        assert safe_str(None) == ''

    def test_empty_string(self):
        assert safe_str('') == ''

    def test_zero(self):
        assert safe_str(0) == '0'

    def test_false(self):
        assert safe_str(False) == 'False'

    def test_regular_string(self):
        assert safe_str('hello') == 'hello'

    def test_number(self):
        assert safe_str(42) == '42'
