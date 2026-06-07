import os
from unittest.mock import MagicMock
from app.services.template_manager import (
    get_template_path,
    get_checklist_is_excel,
    open_template,
    find_table_by_header,
    find_table_by_col_count,
    inject_checkbox_status,
)


class TestGetTemplatePath:
    def test_known_doc_type(self):
        path = get_template_path('Audit_Plan_Stage_1')
        assert path is not None
        assert path.endswith('.docx')

    def test_unknown_doc_type(self):
        path = get_template_path('Unknown_Doc')
        assert path is None

    def test_checklist_template_exists(self):
        path = get_template_path('ISO_Checklist', 'iso_9001')
        assert path is not None
        assert os.path.exists(path) or 'Form' in path

    def test_checklist_unknown_standard(self):
        path = get_template_path('ISO_Checklist', 'iso_99999')
        assert path is None

    def test_template_path_is_absolute(self):
        path = get_template_path('Audit_Plan_Stage_1')
        assert os.path.isabs(path)


class TestGetChecklistIsExcel:
    def test_iso_27001_is_excel(self):
        assert get_checklist_is_excel('iso_27001') is True

    def test_other_standards_not_excel(self):
        assert get_checklist_is_excel('iso_9001') is False
        assert get_checklist_is_excel('iso_14001') is False
        assert get_checklist_is_excel('iso_45001') is False


class TestOpenTemplate:
    def test_unknown_returns_none(self):
        fmt, obj = open_template('Unknown_Doc')
        assert fmt is None
        assert obj is None

    def test_docx_returns_document(self):
        fmt, obj = open_template('Audit_Plan_Stage_1')
        assert fmt == 'docx'
        assert obj is not None

    def test_xlsx_returns_path(self):
        fmt, obj = open_template('ISO_Checklist', 'iso_27001')
        assert fmt == 'xlsx'
        assert isinstance(obj, str)
        assert obj.endswith('.xlsx')


class TestFindTableByHeader:
    def test_no_matching_table(self):
        mock_doc = MagicMock()
        mock_doc.tables = []
        result = find_table_by_header(mock_doc, ['audit'])
        assert result is None

    def test_no_tables(self):
        mock_doc = MagicMock()
        mock_doc.tables = []
        result = find_table_by_col_count(mock_doc, 5)
        assert result is None


class TestInjectCheckboxStatus:
    def test_conformant(self):
        text, color = inject_checkbox_status(None, 'Conformant')
        assert '☒ Conformant' == text
        assert color is None

    def test_non_conformant(self):
        text, color = inject_checkbox_status(None, 'Non-Conformant')
        assert '☒ Non-Conformant' == text
        assert color is not None

    def test_partially_conformant(self):
        text, color = inject_checkbox_status(None, 'Partially Conformant')
        assert '☒ Partially Conformant' == text
        assert color is not None

    def test_unknown_status_uses_unchecked(self):
        text, color = inject_checkbox_status(None, 'Not Reviewed')
        assert '☐ Not Reviewed' == text
        assert color is None
