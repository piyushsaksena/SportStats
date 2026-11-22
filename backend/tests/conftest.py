"""Pytest fixtures for SportStats backend test suite."""

import pytest
from fastapi.testclient import TestClient

from sportstats.api.main import app


@pytest.fixture
def client():
    """Provides a TestClient for testing FastAPI endpoints."""
    return TestClient(app)
