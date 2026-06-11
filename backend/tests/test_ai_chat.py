"""Tests for AI Chat — 8-layer context builder and chat endpoint."""

from unittest.mock import patch, MagicMock

import pytest

from app.services.ai_chat import build_chat_context, chat_with_ai


# ── Sample job data ──────────────────────────────────────────────────────
SAMPLE_JOB = {
    'standards': ['iso_9001', 'iso_14001'],
    'client_key': 'acme-corp',
    'results': {
        'Audit_Report': {
            'path': '/tmp/report.docx',
            '_created_at': 1000000.0,
            '_data': {
                'client_name': 'Acme Corp',
                'scope': 'Quality and environmental management systems',
                'findings_summary': 'Three minor non-conformities identified',
                'conclusion': 'Recommended for certification',
                'methodology': 'On-site audit over 3 days',
            },
        },
        'ISO_Checklist': {
            'path': '/tmp/checklist.docx',
            '_data': {
                'sections': ['Clause 4', 'Clause 5'],
                'overall_assessment': 'Generally conformant',
            },
        },
        'Certificate': {
            'error': 'Generation failed',
        },
    },
    'notes_summary': 'Opening meeting at 9am. Document review complete.',
    'manday_summary': 'Total mandays: 5. Audit team: 2.',
}


class TestBuildChatContext:
    """Tests for build_chat_context — assembles 8-layer context string."""

    def test_returns_string(self):
        result = build_chat_context(SAMPLE_JOB)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_project_info_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== PROJECT INFO ===' in result
        assert 'Acme Corp' in result
        assert 'iso_9001' in result

    def test_contains_document_status_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== GENERATED DOCUMENTS ===' in result
        assert 'Audit Report' in result
        assert '✅ generated' in result
        assert '❌ failed' in result

    def test_contains_per_doc_fields_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== PER-DOCUMENT FIELDS ===' in result
        assert 'findings_summary' in result
        assert 'Three minor non-conformities' in result

    def test_contains_iso_standards_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== ISO STANDARDS ===' in result
        assert 'iso_9001' in result
        assert 'iso_14001' in result

    def test_contains_system_capabilities_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== SYSTEM CAPABILITIES ===' in result
        assert 'Generate audit documents' in result

    def test_contains_chat_history_placeholder(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== CHAT HISTORY ===' in result
        assert '{chat_history}' in result

    def test_contains_client_config_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== CLIENT CONFIG ===' in result
        assert 'acme-corp' in result

    def test_contains_uploaded_files_layer(self):
        result = build_chat_context(SAMPLE_JOB)
        assert '=== UPLOADED FILES ===' in result
        assert 'Opening meeting' in result
        assert '5' in result

    def test_empty_job_does_not_crash(self):
        result = build_chat_context({})
        assert isinstance(result, str)
        assert '=== PROJECT INFO ===' in result

    def test_no_results_does_not_crash(self):
        result = build_chat_context({'standards': ['iso_9001']})
        assert isinstance(result, str)
        assert '❌ failed' not in result

    def test_no_notes_omits_uploaded_files_layer(self):
        job = {'standards': [], 'client_key': '', 'results': {}}
        result = build_chat_context(job)
        assert '=== UPLOADED FILES ===' not in result

    def test_field_value_truncated_at_300_chars(self):
        long_field = 'x' * 500
        job = {
            'standards': [],
            'client_key': '',
            'results': {
                'Audit_Report': {
                    'path': '/tmp/r.docx',
                    '_data': {'findings_summary': long_field},
                },
            },
        }
        result = build_chat_context(job)
        assert 'x' * 300 in result
        assert 'x' * 500 not in result


class TestChatWithAi:
    """Tests for chat_with_ai — sends messages through the router."""

    def test_success_returns_response(self):
        with patch('app.services.ai_chat.router_generate', return_value={'text': 'This is the AI response.'}):
            result = chat_with_ai('Hello', '=== CHAT HISTORY ===\n{chat_history}')

        assert result['error'] is False
        assert result['response'] == 'This is the AI response.'

    def test_error_from_router_returned(self):
        with patch('app.services.ai_chat.router_generate', return_value={'error': 'Rate limited'}):
            result = chat_with_ai('Hello', 'context')

        assert result['error'] is True
        assert 'Rate limited' in result['response']

    def test_router_exception_returns_error(self):
        with patch('app.services.ai_chat.router_generate', side_effect=RuntimeError('Connection failed')):
            result = chat_with_ai('Hello', 'context')

        assert result['error'] is True
        assert 'Connection failed' in result['response']

    def test_history_injected_into_context(self):
        mock_router = MagicMock(return_value={'text': 'ok'})
        with patch('app.services.ai_chat.router_generate', mock_router):
            chat_with_ai('Hi', '=== CHAT HISTORY ===\n{chat_history}', history=['Hello', 'Response'])

        prompt = mock_router.call_args[0][1]
        assert 'User: Hello' in prompt
        assert 'Assistant: Response' in prompt

    def test_history_keeps_all_when_under_token_limit(self):
        mock_router = MagicMock(return_value={'text': 'ok'})
        with patch('app.services.ai_chat.router_generate', mock_router):
            long_history = ['m1', 'r1', 'm2', 'r2', 'm3', 'r3', 'm4', 'r4']
            chat_with_ai('Hi', '{chat_history}', history=long_history)

        prompt = mock_router.call_args[0][1]
        assert 'm1' in prompt
        assert 'm4' in prompt

    def test_compress_history_triggers_over_limit(self):
        from app.services.ai_chat import _compress_history
        huge_history = ['Hello how are you'] + ['x' * 4000] * 10
        with patch('app.services.ai_chat.router_generate') as mock_compress:
            mock_compress.return_value = {'text': 'summary of earlier chat'}
            result = _compress_history(huge_history)
        assert 'COMPACT' in result
        assert 'summary of earlier chat' in result

    def test_no_history_says_no_prior_messages(self):
        mock_router = MagicMock(return_value={'text': 'ok'})
        with patch('app.services.ai_chat.router_generate', mock_router):
            chat_with_ai('Hi', '{chat_history}')

        prompt = mock_router.call_args[0][1]
        assert 'no prior messages' in prompt
