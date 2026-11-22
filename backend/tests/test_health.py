"""Health check endpoint verification tests."""

from sportstats.api.main import api_v1_health_check, health_check


def test_root_health_endpoint():
    """Verify /health returns 200 with healthy status."""
    data = health_check()
    assert data["status"] == "healthy"
    assert data["app"] == "sportstats"
    assert "version" in data


def test_api_v1_health_endpoint():
    """Verify /api/v1/health returns 200 with api_version."""
    data = api_v1_health_check()
    assert data["status"] == "healthy"
    assert data["api_version"] == "v1"
