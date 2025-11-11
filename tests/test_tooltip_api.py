"""
Tests for UTAC Tooltip System API

v2-feat-ext-001: Tooltip System
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import app

client = TestClient(app)


# ============================================================================
# Health & Status Tests
# ============================================================================

def test_health_check():
    """Test health endpoint returns correct status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "tooltip" in data["endpoints"]
    assert data["endpoints"]["tooltip"] == "implemented ✨ NEW!"


# ============================================================================
# Tooltip API Tests
# ============================================================================

def test_get_all_tooltip_data():
    """Test GET /api/tooltip returns list of tooltip data"""
    response = client.get("/api/tooltip")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure of first item
    first = data[0]
    assert "preset_id" in first
    assert "label" in first
    assert "domain" in first
    assert "beta" in first
    assert "field_type" in first


def test_get_tooltip_data_specific_preset():
    """Test GET /api/tooltip/{preset_id} for specific preset"""
    # Test with a known preset (adjust if needed)
    response = client.get("/api/tooltip/llm_resonance")
    assert response.status_code == 200
    data = response.json()
    assert data["preset_id"] == "llm_resonance"
    assert "beta" in data
    assert "field_type" in data
    assert "crep" in data


def test_get_tooltip_data_nonexistent_preset():
    """Test GET /api/tooltip/{preset_id} with nonexistent preset"""
    response = client.get("/api/tooltip/nonexistent_preset_xyz")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# Field Type Classification Tests
# ============================================================================

def test_field_type_weakly_coupled():
    """Test field type classification for weakly coupled (β < 2.5)"""
    from api.server import classify_field_type
    result = classify_field_type(2.0)
    assert result.type == "weakly_coupled"
    assert result.beta_range == [0.0, 2.5]
    assert result.color == "#a8dadc"


def test_field_type_high_dimensional():
    """Test field type classification for high-dimensional (2.5 ≤ β < 4.0)"""
    from api.server import classify_field_type
    result = classify_field_type(3.5)
    assert result.type == "high_dimensional"
    assert result.beta_range == [2.5, 4.0]
    assert result.color == "#457b9d"


def test_field_type_strongly_coupled():
    """Test field type classification for strongly coupled (4.0 ≤ β < 5.5)"""
    from api.server import classify_field_type
    result = classify_field_type(4.5)
    assert result.type == "strongly_coupled"
    assert result.beta_range == [4.0, 5.5]
    assert result.color == "#1d3557"


def test_field_type_physically_constrained():
    """Test field type classification for physically constrained (5.5 ≤ β < 10.0)"""
    from api.server import classify_field_type
    result = classify_field_type(7.0)
    assert result.type == "physically_constrained"
    assert result.beta_range == [5.5, 10.0]
    assert result.color == "#e63946"


def test_field_type_meta_adaptive():
    """Test field type classification for meta-adaptive (β ≥ 10.0)"""
    from api.server import classify_field_type
    result = classify_field_type(16.3)  # Urban heat β
    assert result.type == "meta_adaptive"
    assert result.beta_range == [10.0, 1000.0]
    assert result.color == "#f77f00"


def test_field_type_none_input():
    """Test field type classification with None input (should default)"""
    from api.server import classify_field_type
    result = classify_field_type(None)
    assert result.type == "high_dimensional"  # Default


# ============================================================================
# CREP Score Tests
# ============================================================================

def test_crep_scores_computation():
    """Test CREP scores are computed correctly"""
    from api.server import compute_crep_scores
    crep = compute_crep_scores(
        r2=0.95,
        delta_aic=150.0,
        impedance_mean=1.5,
        beta=4.5
    )
    assert crep is not None
    assert 0 <= crep.coherence <= 1
    assert 0 <= crep.resilience <= 1
    assert 0 <= crep.empathy <= 1
    assert 0 <= crep.propagation <= 1
    # Coherence should be close to R²
    assert abs(crep.coherence - 0.95) < 0.01


def test_crep_scores_null_inputs():
    """Test CREP scores return None with null inputs"""
    from api.server import compute_crep_scores
    crep = compute_crep_scores(
        r2=None,
        delta_aic=150.0,
        impedance_mean=1.5,
        beta=4.5
    )
    assert crep is None


# ============================================================================
# Data Structure Tests
# ============================================================================

def test_tooltip_data_structure():
    """Test tooltip data has required fields"""
    response = client.get("/api/tooltip")
    data = response.json()
    for item in data:
        # Required fields
        assert "preset_id" in item
        assert "label" in item
        assert "domain" in item
        assert "impedance_closed" in item
        assert "impedance_open" in item
        assert "impedance_mean" in item


def test_field_type_info_structure():
    """Test field_type has correct structure"""
    response = client.get("/api/tooltip")
    data = response.json()
    for item in data:
        if item.get("field_type"):
            ft = item["field_type"]
            assert "type" in ft
            assert "description" in ft
            assert "beta_range" in ft
            assert "color" in ft
            assert len(ft["beta_range"]) == 2
            assert ft["color"].startswith("#")


# ============================================================================
# Integration Tests
# ============================================================================

def test_tooltip_data_matches_field_type_beta():
    """Test that field_type classification matches beta value"""
    response = client.get("/api/tooltip")
    data = response.json()

    for item in data:
        if item.get("beta") is not None and item.get("field_type"):
            beta = item["beta"]
            ft = item["field_type"]
            beta_min, beta_max = ft["beta_range"]

            # Beta should be within field type range
            # (Allow small tolerance for boundary cases)
            assert beta_min <= beta <= beta_max + 0.1, \
                f"{item['preset_id']}: β={beta} not in {ft['type']} range [{beta_min}, {beta_max}]"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
