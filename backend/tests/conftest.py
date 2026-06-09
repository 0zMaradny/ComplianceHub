"""Shared test fixtures for ComplianceHub backend tests."""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_surveillance_data():
    """Reset surveillance data before each test to ensure isolation."""
    from app.services.surveillance import _reset_data
    _reset_data()
    yield
    _reset_data()


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset rate limiter between tests to prevent 429 errors."""
    import app.main as _main
    _main._rate_limit_store.clear()
    yield


@pytest.fixture
def api_client():
    """Create a fresh TestClient for each test function."""
    from app.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True, scope="session")
def _cleanup_test_data_files():
    """Clean up any test data files before the test suite starts."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'data')
    for fname in ('surveillance.json', 'surveillance_findings.json',
                  'projects.json', 'ncs.json', 'capas.json', 'evidence.json'):
        fpath = os.path.join(data_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
    yield