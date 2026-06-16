"""Tests for the file parser module."""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.file_parser import (
    extract_audit_notes,
    extract_manday_data,
    parse_docx,
    parse_txt,
)


def test_parse_txt_success():
    content = "First paragraph\nSecond paragraph\nThird paragraph"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        path = f.name
    try:
        result = parse_txt(path)
        assert result['filename'] == os.path.basename(path)
        assert result['text'] == content
        assert result['paragraphs'] == ['First paragraph', 'Second paragraph', 'Third paragraph']
        assert result['tables'] == []
    finally:
        os.unlink(path)


def test_parse_txt_strips_empty_lines():
    content = "Line 1\n\n\nLine 2\n  \nLine 3"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        path = f.name
    try:
        result = parse_txt(path)
        assert result['paragraphs'] == ['Line 1', 'Line 2', 'Line 3']
    finally:
        os.unlink(path)


@patch('app.services.file_parser.Document')
def test_parse_docx_success(mock_document_cls):
    mock_doc = MagicMock()
    mock_doc.paragraphs = [
        MagicMock(text='Section 1: Introduction'),
        MagicMock(text=''),
        MagicMock(text='Section 2: Scope'),
        MagicMock(text='Section 3: Methodology'),
    ]
    mock_doc.tables = []
    mock_document_cls.return_value = mock_doc

    result = parse_docx('/fake/path/report.docx')

    assert result['filename'] == 'report.docx'
    assert result['paragraphs'] == [
        'Section 1: Introduction',
        'Section 2: Scope',
        'Section 3: Methodology',
    ]
    assert 'Section 1: Introduction' in result['text']
    assert 'Section 2: Scope' in result['text']
    assert result['tables'] == []


@patch('app.services.file_parser.Document')
def test_parse_docx_with_tables(mock_document_cls):
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text='Report data')]

    mock_table = MagicMock()
    mock_table.rows = [
        MagicMock(cells=[MagicMock(text='Name'), MagicMock(text='Value')]),
        MagicMock(cells=[MagicMock(text='Total'), MagicMock(text='42')]),
    ]
    mock_doc.tables = [mock_table]
    mock_document_cls.return_value = mock_doc

    result = parse_docx('/fake/path/data.docx')

    assert len(result['tables']) == 1
    assert result['tables'][0] == [['Name', 'Value'], ['Total', '42']]


@patch('app.services.file_parser.parse_docx')
def test_extract_manday_data_basic(mock_parse_docx):
    mock_parse_docx.return_value = {
        'filename': 'manday.docx',
        'paragraphs': [
            'Client: Acme Corp',
            'Address: 123 Main St',
            'Audit Date: 15/06/2026',
            '5 Manday',
            'Standard: ISO 9001:2015',
            'Auditor: John Doe',
        ],
        'text': (
            'Client: Acme Corp\n'
            'Address: 123 Main St\n'
            'Audit Date: 15/06/2026\n'
            '5 Manday\n'
            'Standard: ISO 9001:2015\n'
            'Auditor: John Doe'
        ),
        'tables': [],
    }

    result = extract_manday_data('/fake/manday.docx')

    extracted = result['extracted']
    assert extracted['client_name'] == 'Acme Corp'
    assert extracted['client_address'] == '123 Main St'
    assert extracted['audit_date'] == '15/06/2026'
    assert extracted['mandays'] == '5'
    assert extracted['standard'] == 'ISO 9001:2015'
    assert extracted['experts'] == ['John Doe']


@patch('app.services.file_parser.parse_docx')
def test_extract_manday_data_empty(mock_parse_docx):
    mock_parse_docx.return_value = {
        'filename': 'empty.docx',
        'paragraphs': [],
        'text': '',
        'tables': [],
    }

    result = extract_manday_data('/fake/empty.docx')

    assert result['extracted'] == {}


@patch('app.services.file_parser.parse_docx')
def test_extract_audit_notes_docx(mock_parse_docx):
    mock_parse_docx.return_value = {
        'filename': 'notes.docx',
        'paragraphs': ['Audit observation 1', 'Audit observation 2'],
        'text': 'Audit observation 1\nAudit observation 2',
        'tables': [],
    }

    result = extract_audit_notes('/fake/notes.docx')

    assert result['filename'] == 'notes.docx'
    assert result['paragraphs'] == ['Audit observation 1', 'Audit observation 2']
    mock_parse_docx.assert_called_once_with('/fake/notes.docx')


def test_extract_audit_notes_txt():
    content = 'Audit note line 1\nAudit note line 2'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        path = f.name
    try:
        result = extract_audit_notes(path)
        assert result['filename'] == os.path.basename(path)
        assert result['paragraphs'] == ['Audit note line 1', 'Audit note line 2']
    finally:
        os.unlink(path)


def test_parse_docx_handles_missing_file():
    with patch('app.services.file_parser.Document') as mock:
        mock.side_effect = FileNotFoundError('No such file')
        result = parse_docx('/nonexistent/path.docx')
        assert 'error' in result


def test_extract_manday_data_no_file():
    with patch('app.services.file_parser.parse_docx') as mock:
        mock.side_effect = FileNotFoundError('No file')
        result = extract_manday_data('/fake/missing.docx')
        assert 'error' in result


def test_extract_manday_data_any_path():
    mock_result = {
        'filename': 'manday.docx',
        'paragraphs': ['Audit: 5 days', 'Standard: ISO 14001'],
        'text': 'Audit: 5 days\nStandard: ISO 14001',
        'tables': [],
    }
    with patch('app.services.file_parser.parse_docx', return_value=mock_result):
        output = extract_manday_data('/fake/test.docx')
        assert output['extracted'] is not None


def test_extract_audit_notes_unknown_ext():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as f:
        f.write('test content')
        path = f.name
    try:
        result = extract_audit_notes(path)
        assert result['text'] == ''
    finally:
        os.unlink(path)
