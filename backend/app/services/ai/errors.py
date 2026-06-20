"""Standardized AI provider error responses.

All providers return errors in a consistent format for easier debugging
and unified error handling in the router.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AIError:
    """Standardized error from an AI provider call."""

    code: str  # e.g., 'RATE_LIMIT', 'AUTH', 'TIMEOUT', 'GENERATION', 'CONNECTION'
    message: str  # Human-readable error message
    provider: str  # Which provider failed
    retryable: bool = True  # Can we retry with another provider?
    details: dict[str, Any] = field(default_factory=dict)  # Provider-specific details

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API responses."""
        d: dict[str, Any] = {"error": self.message, "code": self.code, "provider": self.provider}
        if self.details:
            d["details"] = self.details
        return d

    def __str__(self) -> str:
        return f"[{self.code}] {self.provider}: {self.message}"


# Error code classification
RETRYABLE_CODES = {"RATE_LIMIT", "TIMEOUT", "CONNECTION", "SERVER_ERROR"}
NON_RETRYABLE_CODES = {"AUTH", "INVALID_REQUEST", "CONTENT_POLICY", "MODEL_NOT_FOUND"}


def classify_error(code: str) -> AIError:
    """Create an AIError with appropriate retryable flag based on code."""
    retryable = code in RETRYABLE_CODES
    return AIError(code=code, message=f"Error: {code}", provider="unknown", retryable=retryable)


def from_exception(exc: Exception, provider: str) -> AIError:
    """Create an AIError from an exception."""
    msg = str(exc)
    code = "GENERATION"

    # Classify common error types
    if "rate limit" in msg.lower() or "429" in msg:
        code = "RATE_LIMIT"
    elif "timeout" in msg.lower():
        code = "TIMEOUT"
    elif "auth" in msg.lower() or "401" in msg or "403" in msg:
        code = "AUTH"
    elif "connection" in msg.lower():
        code = "CONNECTION"
    elif "500" in msg or "502" in msg or "503" in msg:
        code = "SERVER_ERROR"

    return AIError(
        code=code,
        message=msg[:500],  # Truncate long messages
        provider=provider,
        retryable=code in RETRYABLE_CODES,
        details={"exception_type": type(exc).__name__},
    )


def from_http_error(status_code: int, body: str, provider: str) -> AIError:
    """Create an AIError from an HTTP error response."""
    code_map = {
        401: "AUTH",
        403: "AUTH",
        429: "RATE_LIMIT",
        500: "SERVER_ERROR",
        502: "SERVER_ERROR",
        503: "SERVER_ERROR",
        504: "TIMEOUT",
    }
    code = code_map.get(status_code, "SERVER_ERROR")
    return AIError(
        code=code,
        message=f"HTTP {status_code}: {body[:300]}",
        provider=provider,
        retryable=code in RETRYABLE_CODES,
        details={"http_status": status_code},
    )


def ensure_error_dict(result: dict[str, Any], provider: str) -> dict[str, Any]:
    """Ensure a result dict has standardized error format.

    If the result already has an 'error' key, standardize it.
    If it has 'text', wrap it in the standard format.
    """
    if "error" in result:
        if "code" not in result:
            result["code"] = "GENERATION"
        if "provider" not in result:
            result["provider"] = provider
        return result
    if "text" in result:
        return result  # Success case — no error
    # Unknown format — wrap it
    return {"error": str(result), "code": "UNKNOWN", "provider": provider}
