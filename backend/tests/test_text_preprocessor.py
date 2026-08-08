"""Tests for the text preprocessor module."""

import os
import sys
import importlib.util
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

_tp_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'services', 'text_preprocessor.py')
_tp_spec = importlib.util.spec_from_file_location('text_preprocessor', _tp_path)
tp = importlib.util.module_from_spec(_tp_spec)
_tp_spec.loader.exec_module(tp)

normalize_encoding = tp.normalize_encoding
_has_arabic = tp._has_arabic
remove_caveman_elements = tp.remove_caveman_elements
preprocess_text = tp.preprocess_text
preprocess_for_upload = tp.preprocess_for_upload
preprocess_for_generation = tp.preprocess_for_generation
preprocess_for_chat = tp.preprocess_for_chat
validate_and_optimize_text = tp.validate_and_optimize_text
get_compression_stats = tp.get_compression_stats
_compress_iso_codes = tp._compress_iso_codes
_compress_audit_terms = tp._compress_audit_terms


# ── normalize_encoding ────────────────────────────────────────────────────

def test_normalize_encoding_removes_bom():
    assert normalize_encoding('\ufeffHello') == 'Hello'


def test_normalize_encoding_normalizes_newlines():
    assert normalize_encoding('line1\r\nline2\rline3') == 'line1\nline2\nline3'


def test_normalize_encoding_preserves_utf8():
    assert normalize_encoding('Hello 世界') == 'Hello 世界'


# ── _has_arabic ────────────────────────────────────────────────────────────

def test_has_arabic_detects_arabic():
    assert _has_arabic('مرحبا بالعالم') is True


def test_has_arabic_no_arabic():
    assert _has_arabic('Hello world') is False


def test_has_arabic_mixed():
    assert _has_arabic('ISO 27001:2022 معيار') is True


# ── remove_caveman_elements / preprocess_text ──────────────────────────────

def test_caveman_lite_removes_filler():
    text = "So basically, we just need to really look at the audit results."
    result = preprocess_text(text, 'lite')
    assert 'basically' not in result['text']
    assert 'just' not in result['text']
    assert 'really' not in result['text']


def test_caveman_full_removes_sentence_start_so():
    text = "So we need to look at the audit results."
    result = preprocess_text(text, 'full')
    assert 'So' not in result['text']


def test_caveman_lite_keeps_articles():
    text = "The audit requires a review of the scope."
    result = preprocess_text(text, 'lite')
    assert 'The' in result['text'] or 'the' in result['text'].lower()


def test_caveman_full_removes_articles():
    text = "The audit requires a review of the scope."
    result = preprocess_text(text, 'full')
    assert 'the' not in result['text'].lower()
    assert 'a ' not in result['text']


def test_caveman_full_keeps_technical():
    text = "Actually, the ISO 27001:2022 clause A.9.2.1 must be reviewed."
    result = preprocess_text(text, 'full')
    assert 'ISO' in result['text']
    assert 'A.9.2.1' in result['text']


def test_caveman_ultra_shortens():
    text = "The application configuration database must implement authentication."
    result = preprocess_text(text, 'ultra')
    assert 'app' in result['text'] or 'config' in result['text']
    assert 'DB' in result['text'] or 'auth' in result['text']


def test_caveman_ultra_uses_arrow():
    text = "The review failed because the evidence was missing."
    result = preprocess_text(text, 'ultra')
    assert '→' in result['text']


# ── Code block preservation ────────────────────────────────────────────────

def test_preserves_fenced_code_block():
    text = "Some text.\n```python\nx = just_a_var\n```\nMore text."
    result = preprocess_text(text, 'full')
    assert '```' in result['text']
    assert 'x = just_a_var' in result['text']


# ── Arabic preservation ────────────────────────────────────────────────────

def test_preserves_arabic_text():
    arabic = "مرحبا بالعالم هذا نص عربي"
    result = preprocess_text(arabic, 'ultra')
    assert arabic in result['text']


def test_preserves_arabic_mixed_with_english():
    text = "ISO 27001 يتطلب مراجعة شاملة للنطاق."
    result = preprocess_text(text, 'full')
    # Arabic portion preserved
    assert 'يتطلب' in result['text']
    # ISO still present
    assert 'ISO' in result['text']


# ── ISO code compression ──────────────────────────────────────────────────

def test_compress_iso_codes():
    text = "ISO 27001:2022 clause A.9.2.1 and ISO 9001:2015"
    result = _compress_iso_codes(text)
    assert 'ISO27k' in result
    assert 'ISO9k' in result
    assert 'cl.' in result


def test_compress_audit_terms():
    text = "Statement of Applicability and non-conformity found"
    result = _compress_audit_terms(text)
    assert 'SoA' in result
    assert 'NC' in result


# ── Token savings verification ─────────────────────────────────────────────

def test_chat_message_savings():
    """Chat message with filler should save at least 20% tokens."""
    msg = "Sure! I'd be happy to help you with that. So basically, we just need to look at the audit notes and then I think we should generate the SoA document based on those findings."
    result = preprocess_for_chat(msg, 'full')
    assert result['savings_pct'] >= 20


def test_audit_text_savings():
    """Audit document text should save at least 20% tokens."""
    text = """So what I'm thinking is, we probably need to look at the audit notes for ISO 27001 clause A.9.2.1, which is about access control, and then I think we should generate the Statement of Applicability document based on those findings. Also, the client would like to review the non-conformities before finalizing the audit report."""
    result = preprocess_text(text, 'ultra')
    assert result['savings_pct'] >= 20


def test_arabic_savings_zero():
    """Arabic text should not be compressed (0% savings)."""
    msg = "مرحبا، أود مراجعة تقرير التدقيق"
    result = preprocess_for_chat(msg, 'ultra')
    assert result['savings_pct'] == 0
    assert result.get('arabic') is True


# ── Entry-point integration tests ─────────────────────────────────────────

def test_preprocess_for_upload_text():
    content = b"Actually, the audit just needs a simple review of the scope."
    result = preprocess_for_upload(content, 'notes.txt', 'full')
    assert 'the' not in result['text'].lower()
    assert result['savings_pct'] > 0


def test_preprocess_for_upload_binary():
    """DOCX binary should not be processed at upload stage."""
    content = b'PK\x03\x04fake_docx_content'
    result = preprocess_for_upload(content, 'notes.docx', 'full')
    assert result['text'] == ''  # Handled downstream


def test_preprocess_for_generation():
    notes = "Basically, we need to review the ISO 27001:2022 audit."
    manday = "The client requires 10 mandays of effort."
    result = preprocess_for_generation(notes, manday, 'full')
    assert result['notes_savings_pct'] > 0
    assert result['manday_savings_pct'] > 0
    assert 'ISO27k' in result['notes_text']


def test_preprocess_for_generation_empty():
    result = preprocess_for_generation('', '', 'full')
    assert result['notes_text'] == ''
    assert result['manday_text'] == ''


def test_preprocess_for_chat_no_message():
    result = preprocess_for_chat('', 'full')
    assert result['message'] == ''
    assert result['savings_pct'] == 0


# ── Validation ─────────────────────────────────────────────────────────────

def test_validate_empty_text():
    result = validate_and_optimize_text('')
    assert result['valid'] is False
    assert len(result['warnings']) > 0


def test_validate_short_text():
    result = validate_and_optimize_text('Hi', min_chars=10)
    assert result['valid'] is False


def test_validate_truncation():
    text = 'A' * 50000
    result = validate_and_optimize_text(text, max_chars=100)
    assert result['truncated'] is True
    assert len(result['text']) == 100


def test_validate_good_text():
    result = validate_and_optimize_text('Good audit notes text here.')
    assert result['valid'] is True
    assert len(result['warnings']) == 0


# ── Compression stats ──────────────────────────────────────────────────────

def test_get_compression_stats():
    original = "The quick brown fox jumps over the lazy dog."
    processed = "quick brown fox jumps over lazy dog."
    stats = get_compression_stats(original, processed)
    assert stats['original_chars'] > stats['processed_chars']
    assert stats['savings_pct'] > 0


def test_get_compression_stats_empty():
    stats = get_compression_stats('', '')
    assert stats['savings_pct'] == 0
