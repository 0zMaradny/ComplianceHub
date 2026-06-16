"""Tests for local AI provider."""

from unittest.mock import patch

from app.services.ai.local_provider import LocalProvider


class TestLocalProviderInit:
    def test_default_base_url(self):
        p = LocalProvider()
        assert p._call is not None

    def test_reads_env_vars(self):
        with patch.dict('app.services.ai.local_provider.os.environ',
                        {'LOCAL_AI_BASE': 'http://custom:9090',
                         'LOCAL_AI_TIMEOUT': '30'}):
            import importlib
            import app.services.ai.local_provider as lp
            importlib.reload(lp)
            assert lp.LOCAL_BASE == 'http://custom:9090'
            assert lp.LOCAL_TIMEOUT == 30


class TestLocalProviderCall:
    def test_server_unreachable_returns_error(self):
        p = LocalProvider()
        with patch('urllib.request.urlopen') as mock:
            mock.side_effect = ConnectionRefusedError('Connection refused')
            result = p._call('test prompt')
            assert 'error' in result

    def test_generate_delegates_to_call(self):
        p = LocalProvider()
        with patch.object(p, '_call', return_value={'text': 'ok'}):
            result = p.generate('test')
            assert result == {'text': 'ok'}

    def test_extract_structured_delegates_to_call(self):
        p = LocalProvider()
        with patch.object(p, '_call', return_value={'parsed': True}):
            result = p.extract_structured('test')
            assert result == {'parsed': True}

    def test_generate_stream_includes_error(self):
        p = LocalProvider()
        with patch.object(p, '_call', return_value={'error': 'Server down'}):
            tokens = list(p.generate_stream('test'))
            assert len(tokens) > 0
            assert 'Error' in tokens[0]
