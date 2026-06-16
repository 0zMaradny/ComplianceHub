"""Tests for Groq AI provider."""

from unittest.mock import patch, MagicMock

from app.services.ai.groq_provider import GroqProvider


class TestGroqProvider:
    def test_init_reads_env_key(self):
        with patch.dict('app.services.ai.groq_provider.os.environ',
                        {'GROQ_API_KEY': 'gsk_test_key'}):
            import importlib
            import app.services.ai.groq_provider as gp
            importlib.reload(gp)
            p = gp.GroqProvider()
            assert p.api_key == 'gsk_test_key'
            assert 'llama' in p.model

    def test_no_key_returns_error(self):
        p = GroqProvider()
        p.api_key = ''
        result = p.generate('test')
        assert 'error' in result
        assert 'not set' in result['error'].lower()

    def test_generate_calls_openai(self):
        p = GroqProvider()
        p.api_key = 'gsk_test'
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"result": "ok"}'
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        with patch('app.services.ai.groq_provider.OpenAI', return_value=mock_client):
            result = p.generate('test prompt')
            assert result == {"result": "ok"}

    def test_generate_non_json_response(self):
        p = GroqProvider()
        p.api_key = 'gsk_test'
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = 'Just text response'
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        with patch('app.services.ai.groq_provider.OpenAI', return_value=mock_client):
            result = p.generate('test prompt')
            assert result == {'text': 'Just text response'}

    def test_extract_structured_uses_low_temp(self):
        p = GroqProvider()
        p.api_key = 'gsk_test'
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"parsed": true}'
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
        with patch('app.services.ai.groq_provider.OpenAI', return_value=mock_client):
            result = p.extract_structured('extract this')
            assert result == {"parsed": True}

    def test_api_exception_returns_error(self):
        p = GroqProvider()
        p.api_key = 'gsk_test'
        with patch('app.services.ai.groq_provider.OpenAI') as mock:
            mock_instance = MagicMock()
            mock_instance.chat.completions.create.side_effect = RuntimeError('API error')
            mock.return_value = mock_instance
            result = p.generate('test')
            assert 'error' in result

    def test_generate_stream_no_key(self):
        p = GroqProvider()
        p.api_key = ''
        tokens = list(p.generate_stream('test'))
        assert 'not set' in tokens[0]
