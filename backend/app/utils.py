"""Shared utility functions for the ComplianceHub backend."""

import re


def sanitize_filename(name: str) -> str:
    """Sanitize a string for safe use in file paths and ZIP entries.
    Allows only alphanumeric, underscore, hyphen, and dot. Max 120 chars."""
    return re.sub(r'[^a-zA-Z0-9._\-]', '_', name)[:120]


def validate_job_id(job_id: str) -> bool:
    """Validate that a job_id is a proper UUID hex string (32 hex chars)."""
    return bool(re.match(r'^[0-9a-f]{32}$', job_id))
