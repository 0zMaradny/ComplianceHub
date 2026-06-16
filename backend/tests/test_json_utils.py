"""Tests for JSON extraction utilities."""

from app.services.ai.json_utils import extract_json


class TestExtractJson:
    def test_valid_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_empty_string(self):
        assert extract_json('') is None

    def test_whitespace_only(self):
        assert extract_json('   ') is None

    def test_markdown_fenced(self):
        result = extract_json('```json\n{"key": "val"}\n```')
        assert result == {"key": "val"}

    def test_markdown_fenced_no_lang(self):
        result = extract_json('```\n{"key": "val"}\n```')
        assert result == {"key": "val"}

    def test_leading_text(self):
        result = extract_json('Here is the result:\n{"a": 1}\nEnd.')
        assert result == {"a": 1}

    def test_trailing_text(self):
        result = extract_json('{"a": 1}\nSome trailing text')
        assert result == {"a": 1}

    def test_nested_json(self):
        result = extract_json('{"outer": {"inner": [1, 2, 3]}}')
        assert result == {"outer": {"inner": [1, 2, 3]}}

    def test_invalid_json(self):
        assert extract_json('not json at all') is None

    def test_partial_brace(self):
        assert extract_json('{invalid') is None

    def test_multiple_braces_first_is_parsed(self):
        result = extract_json('text {"first": 1} more {"second": 2}')
        assert result is not None

    def test_unicode_content(self):
        result = extract_json('{"message": "مرحبا"}')
        assert result == {"message": "مرحبا"}
