"""Tests for standardized AI error responses."""
import pytest
from app.services.ai.errors import AIError, from_exception, from_http_error, ensure_error_dict, RETRYABLE_CODES, NON_RETRYABLE_CODES


class TestAIError:
    def test_to_dict(self):
        err = AIError(code="RATE_LIMIT", message="Too many requests", provider="openrouter", retryable=True)
        d = err.to_dict()
        assert d["error"] == "Too many requests"
        assert d["code"] == "RATE_LIMIT"
        assert d["provider"] == "openrouter"

    def test_to_dict_with_details(self):
        err = AIError(code="AUTH", message="Invalid key", provider="groq", details={"key_prefix": "gsk_"})
        d = err.to_dict()
        assert d["details"]["key_prefix"] == "gsk_"

    def test_str_representation(self):
        err = AIError(code="TIMEOUT", message="Connection timeout", provider="local")
        assert "[TIMEOUT]" in str(err)
        assert "local" in str(err)


class TestFromException:
    def test_rate_limit_detection(self):
        err = from_exception(Exception("Rate limit exceeded (429)"), "openrouter")
        assert err.code == "RATE_LIMIT"
        assert err.retryable is True

    def test_auth_detection(self):
        err = from_exception(Exception("Authentication failed: 401 Unauthorized"), "groq")
        assert err.code == "AUTH"
        assert err.retryable is False

    def test_timeout_detection(self):
        err = from_exception(Exception("Connection timed out"), "local")
        assert err.code == "TIMEOUT"

    def test_server_error_detection(self):
        err = from_exception(Exception("Internal server error 500"), "openrouter")
        assert err.code == "SERVER_ERROR"

    def test_generic_error(self):
        err = from_exception(ValueError("Something went wrong"), "unknown")
        assert err.code == "GENERATION"

    def test_long_message_truncated(self):
        err = from_exception(Exception("x" * 1000), "test")
        assert len(err.message) <= 500


class TestFromHTTPError:
    def test_401(self):
        err = from_http_error(401, "Unauthorized", "openrouter")
        assert err.code == "AUTH"
        assert err.retryable is False

    def test_429(self):
        err = from_http_error(429, "Rate limited", "groq")
        assert err.code == "RATE_LIMIT"
        assert err.retryable is True

    def test_500(self):
        err = from_http_error(500, "Internal error", "local")
        assert err.code == "SERVER_ERROR"

    def test_unknown_status(self):
        err = from_http_error(418, "I'm a teapot", "test")
        assert err.code == "SERVER_ERROR"


class TestEnsureErrorDict:
    def test_standardize_existing_error(self):
        result = {"error": "Something failed"}
        standardized = ensure_error_dict(result, "test")
        assert "code" in standardized
        assert "provider" in standardized

    def test_passthrough_success(self):
        result = {"text": "success"}
        assert ensure_error_dict(result, "test") == result

    def test_wrap_unknown_format(self):
        result = 42
        standardized = ensure_error_dict(result, "test")
        assert "error" in standardized
        assert standardized["code"] == "UNKNOWN"
