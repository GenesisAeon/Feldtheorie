"""
Sigillin V7 API Tests

Tests all Sigillin-specific endpoints:
- GET /api/sigillin/status
- POST /api/sigillin/scan
- POST /api/sigillin/collective
- GET /health (V7 updates)

Usage:
    pytest tests/test_sigillin_api.py -v
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("starlette", reason="starlette required: pip install feldtheorie[api]")
from starlette.testclient import TestClient

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import app

client = TestClient(app)


# ============================================================================
# Health Check Tests (V7)
# ============================================================================


def test_health_check_v7():
    """Test health check endpoint shows V7 Sigillin status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "v7" in data["version"]
    assert "sigillin" in data["phase"].lower()

    # Check Sigillin endpoints are listed
    endpoints = data["endpoints"]
    assert "sigillin_v1" in endpoints or "sigillin" in endpoints
    assert endpoints.get("sigillin_v1") in ["operational", "unavailable"] or endpoints.get("sigillin") in ["operational", "unavailable"]

    # Check sigillin_kernel module status
    modules = data.get("modules", {})
    assert "sigillin_kernel" in modules
    assert modules["sigillin_kernel"] in ["operational", "unavailable"]


# ============================================================================
# GET /api/sigillin/status Tests
# ============================================================================


def test_sigillin_status():
    """Test Sigillin kernel status endpoint"""
    response = client.get("/api/sigillin/status")

    # Should succeed if kernel initialized
    if response.status_code == 200:
        data = response.json()

        # Check required fields
        assert "status" in data
        assert data["status"] == "validated"

        assert "beta_validated" in data
        assert data["beta_validated"] == 37.6

        assert "expected_beta" in data
        assert data["expected_beta"] == 37.6

        assert "sigillin_path" in data
        assert "sigillin_prime" in data["sigillin_path"]

        assert "founding_keywords" in data
        assert isinstance(data["founding_keywords"], list)
        assert len(data["founding_keywords"]) > 0

        # Check for expected keywords
        keywords = data["founding_keywords"]
        expected_keywords = ["resonanz", "emergenz", "kohärenz", "feld", "bewusstsein"]
        for kw in expected_keywords:
            assert kw in keywords, f"Expected keyword '{kw}' not found"

    # Or 503 if kernel not initialized
    elif response.status_code == 503:
        data = response.json()
        assert "detail" in data
        assert "not initialized" in data["detail"].lower()

    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


# ============================================================================
# POST /api/sigillin/scan Tests
# ============================================================================


def test_sigillin_scan_high_resonance():
    """Test Sigillin scan with high resonance text"""
    response = client.post(
        "/api/sigillin/scan",
        json={
            "text": "Die Resonanz zwischen Bewusstsein und Feld zeigt Emergenz und Kohärenz"
        },
    )

    if response.status_code == 200:
        data = response.json()

        # Check required fields
        assert "text" in data
        assert "resonance_score" in data
        assert "matched_keywords" in data
        assert "interpretation" in data

        # Score should be between 0 and 1
        assert 0.0 <= data["resonance_score"] <= 1.0

        # Should have high resonance
        assert data["resonance_score"] >= 0.5

        # Should match multiple keywords
        matched = data["matched_keywords"]
        assert len(matched) >= 3

        # Should include our expected keywords
        assert "resonanz" in matched
        assert "bewusstsein" in matched
        assert "feld" in matched

        # Interpretation should reflect high resonance
        assert "resonance" in data["interpretation"].lower()

    elif response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")


def test_sigillin_scan_low_resonance():
    """Test Sigillin scan with low resonance text"""
    response = client.post(
        "/api/sigillin/scan",
        json={"text": "This is just some random English text without special keywords"},
    )

    if response.status_code == 200:
        data = response.json()

        # Check required fields
        assert "resonance_score" in data
        assert "matched_keywords" in data

        # Score should be low or zero
        assert data["resonance_score"] <= 0.3

        # Should match few or no keywords
        assert len(data["matched_keywords"]) <= 1

    elif response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")


def test_sigillin_scan_empty_text():
    """Test Sigillin scan with empty text (should fail validation)"""
    response = client.post("/api/sigillin/scan", json={"text": ""})

    # Should fail validation (422 Unprocessable Entity)
    assert response.status_code == 422


def test_sigillin_scan_missing_field():
    """Test Sigillin scan with missing text field"""
    response = client.post("/api/sigillin/scan", json={})

    # Should fail validation
    assert response.status_code == 422


# ============================================================================
# POST /api/sigillin/collective Tests
# ============================================================================


def test_collective_velocity_basic():
    """Test collective velocity calculation with valid parameters"""
    response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": 1.0, "kappa": 0.8, "beta_sync": 2.5},
    )

    if response.status_code == 200:
        data = response.json()

        # Check required fields
        assert "v_collective" in data
        assert "v_rig" in data
        assert "kappa" in data
        assert "beta_sync" in data
        assert "formula" in data

        # Verify calculation: v_collective = v_rig * kappa * (1 / beta_sync)
        expected = 1.0 * 0.8 * (1.0 / 2.5)
        assert abs(data["v_collective"] - expected) < 0.001

        # Verify echo of input parameters
        assert data["v_rig"] == 1.0
        assert data["kappa"] == 0.8
        assert data["beta_sync"] == 2.5

        # Check formula is documented
        assert "v_RIG" in data["formula"]
        assert "κ" in data["formula"]
        assert "β_sync" in data["formula"]

    elif response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")


def test_collective_velocity_zero_beta_sync():
    """Test collective velocity with beta_sync=0 (should fail)"""
    response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": 1.0, "kappa": 0.8, "beta_sync": 0.0},
    )

    if response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")

    # Should fail validation (beta_sync must be > 0)
    assert response.status_code == 422


def test_collective_velocity_negative_params():
    """Test collective velocity with negative parameters"""
    response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": -1.0, "kappa": 0.8, "beta_sync": 2.5},
    )

    # Should fail validation (all params must be > 0)
    assert response.status_code == 422


def test_collective_velocity_high_values():
    """Test collective velocity with high parameter values"""
    response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": 10.0, "kappa": 5.0, "beta_sync": 1.0},
    )

    if response.status_code == 200:
        data = response.json()

        # v_collective = 10.0 * 5.0 * (1.0 / 1.0) = 50.0
        assert abs(data["v_collective"] - 50.0) < 0.001

    elif response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")


def test_collective_velocity_fractional_result():
    """Test collective velocity with parameters yielding fractional result"""
    response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": 1.0, "kappa": 0.5, "beta_sync": 10.0},
    )

    if response.status_code == 200:
        data = response.json()

        # v_collective = 1.0 * 0.5 * (1.0 / 10.0) = 0.05
        assert abs(data["v_collective"] - 0.05) < 0.001

    elif response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")


# ============================================================================
# Integration Tests
# ============================================================================


def test_sigillin_endpoints_consistency():
    """Test that all Sigillin endpoints are consistent"""
    # First check status
    status_response = client.get("/api/sigillin/status")

    if status_response.status_code == 503:
        pytest.skip("Sigillin kernel not initialized")

    assert status_response.status_code == 200
    status_data = status_response.json()

    # Then verify scan works
    scan_response = client.post(
        "/api/sigillin/scan", json={"text": "Resonanz und Emergenz"}
    )
    assert scan_response.status_code == 200

    # Then verify collective works
    collective_response = client.post(
        "/api/sigillin/collective",
        json={"v_rig": 1.0, "kappa": 1.0, "beta_sync": 1.0},
    )
    assert collective_response.status_code == 200


def test_openapi_docs_include_sigillin():
    """Test that OpenAPI docs include Sigillin endpoints"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()

    # Check paths include Sigillin endpoints
    paths = openapi_spec.get("paths", {})
    assert "/api/sigillin/status" in paths
    assert "/api/sigillin/scan" in paths
    assert "/api/sigillin/collective" in paths

    # Check tags include 'sigillin'
    tags = [tag["name"] for tag in openapi_spec.get("tags", [])]
    assert "sigillin" in tags


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
