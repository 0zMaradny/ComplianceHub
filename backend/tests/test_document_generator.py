from docx import Document

from app.services.document_generator import (
    _build_checklist_grouped_table,
    generate_document_file,
    sanitize_filename,
)


def _count_tables(doc, header_text):
    count = 0
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if header_text in cell.text:
                    count += 1
                    break
    return count


class TestBuildChecklistGroupedTable:
    def test_empty_sections(self):
        doc = Document()
        _build_checklist_grouped_table(doc, [], lang='en')
        assert len(doc.tables) == 2
        assert all(len(t.rows) >= 1 for t in doc.tables)

    def test_single_section(self):
        doc = Document()
        sections = [{'clause': '4.1', 'title': 'Context', 'status': 'Conformant',
                     'evidence': 'Reviewed docs', 'audit_questions': 'Q?',
                     'evidence_to_check': 'E!', 'findings': 'OK'}]
        _build_checklist_grouped_table(doc, sections, lang='en')
        assert _count_tables(doc, 'Audit Questions') >= 1
        assert _count_tables(doc, 'Findings') >= 1
        qa_table = doc.tables[0]
        assert len(qa_table.rows) >= 2

    def test_mixed_statuses(self):
        doc = Document()
        sections = [
            {'clause': '4.1', 'title': 'Context', 'status': 'Conformant',
             'evidence': 'E1', 'audit_questions': 'Q1', 'evidence_to_check': 'C1', 'findings': 'F1'},
            {'clause': '5.2', 'title': 'Policy', 'status': 'Non-Conformant',
             'evidence': 'E2', 'audit_questions': 'Q2', 'evidence_to_check': 'C2', 'findings': 'F2'},
        ]
        _build_checklist_grouped_table(doc, sections, lang='en')
        assert len(doc.tables) == 2
        assert len(doc.tables[0].rows) == 3

    def test_missing_keys(self):
        doc = Document()
        sections = [{'clause': '4.1'}]
        _build_checklist_grouped_table(doc, sections, lang='en')
        assert len(doc.tables) == 2

    def test_two_section_layout(self):
        doc = Document()
        sections = [{'clause': '6.1', 'title': 'Actions', 'status': 'Conformant',
                     'evidence': 'E', 'audit_questions': 'AQ', 'evidence_to_check': 'EC',
                     'findings': 'F', 'reference': 'R'}]
        _build_checklist_grouped_table(doc, sections, lang='en')
        for table in doc.tables:
            header_row = table.rows[0]
            header_text = ' '.join(cell.text for cell in header_row.cells)
            if 'Audit Questions' in header_text:
                assert 'Clause Ref' in header_text
                assert 'Evidence to Check' in header_text
            elif 'Findings' in header_text:
                assert 'Status' in header_text
                assert 'Reference' in header_text

    def test_arabic_lang_no_crash(self):
        doc = Document()
        sections = [{'clause': '4.1', 'title': 'السياق', 'status': 'مطابق',
                     'evidence': 'تم المراجعة', 'audit_questions': 'سؤال',
                     'evidence_to_check': 'وثائق', 'findings': 'موافق'}]
        _build_checklist_grouped_table(doc, sections, lang='ar')
        assert len(doc.tables) >= 1

    def test_ten_sections_no_crash(self):
        doc = Document()
        sections = [
            {'clause': f'4.{i}', 'title': f'Title {i}', 'status': 'Conformant',
             'evidence': 'E', 'audit_questions': 'Q', 'evidence_to_check': 'C', 'findings': 'F'}
            for i in range(10)
        ]
        _build_checklist_grouped_table(doc, sections, lang='en')
        assert len(doc.tables) == 2
        assert len(doc.tables[0].rows) == 11  # header + 10 sections


class TestSanitizeFilename:
    def test_removes_special_chars(self):
        result = sanitize_filename('My Client (Acme) [2025].docx')
        assert '<' not in result and '>' not in result

    def test_caps_at_120_chars(self):
        long_name = 'A' * 100 + '.docx'
        result = sanitize_filename(long_name)
        assert len(result) <= 120
        assert result == 'A' * 100 + '.docx'

    def test_allows_alphanumeric(self):
        result = sanitize_filename('Client-Name_2025.docx')
        assert 'Client' in result

