"""
API Tests for UTAC Modular API

Tests all 5 endpoints:
- POST /api/sonify
- POST /api/analyze
- GET /api/system/{system_id}
- GET /api/fieldtypes
- POST /api/simulate

Usage:
    pytest tests/test_api.py -v
"""

import pytest
import json
import base64
from starlette.testclient import TestClient
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.server import app

client = TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "UTAC" in data["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["phase"] == "2"
    assert data["progress"] == "60%"

    # Check all endpoints are implemented
    endpoints = data["endpoints"]
    assert endpoints["sonify"] == "implemented"
    assert endpoints["analyze"] == "implemented"
    assert endpoints["system"] == "implemented"
    assert endpoints["fieldtypes"] == "implemented"
    assert endpoints["simulate"] == "implemented"


# ============================================================================
# GET /api/fieldtypes Tests
# ============================================================================

def test_get_fieldtypes():
    """Test field types endpoint"""
    response = client.get("/api/fieldtypes")
    assert response.status_code == 200
    data = response.json()

    assert "field_types" in data
    field_types = data["field_types"]
    assert len(field_types) == 5

    # Check field type names
    names = [ft["name"] for ft in field_types]
    assert "weakly_coupled" in names
    assert "high_dimensional" in names
    assert "strongly_coupled" in names
    assert "physically_constrained" in names
    assert "meta_adaptive" in names

    # Check structure of first field type
    ft = field_types[0]
    assert "name" in ft
    assert "beta_range" in ft
    assert "description" in ft
    assert "examples" in ft
    assert "acoustic_profile" in ft


# ============================================================================
# POST /api/sonify Tests
# ============================================================================

def test_sonify_basic():
    """Test sonification endpoint with basic parameters"""
    response = client.post(
        "/api/sonify",
        json={
            "beta": 4.2,
            "theta": 50.0,
            "duration": 1.0,  # Short for test
            "sample_rate": 22050  # Lower for faster test
        }
    )
    assert response.status_code == 200
    data = response.json()

    assert "audio_base64" in data
    assert "metadata" in data

    # Check metadata
    metadata = data["metadata"]
    assert metadata["beta"] == 4.2
    assert metadata["theta"] == 50.0
    assert metadata["duration"] == 1.0
    assert metadata["sample_rate"] == 22050
    assert "field_type" in metadata
    assert "base_frequency_hz" in metadata


def test_sonify_field_type():
    """Test sonification with explicit field type"""
    response = client.post(
        "/api/sonify",
        json={
            "beta": 4.5,
            "theta": 100.0,
            "field_type": "strongly_coupled",
            "duration": 0.5,
            "sample_rate": 22050
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["field_type"] == "strongly_coupled"


def test_sonify_invalid_beta():
    """Test sonification with invalid beta (out of range)"""
    response = client.post(
        "/api/sonify",
        json={
            "beta": 25.0,  # > 20.0 max
            "theta": 50.0
        }
    )
    assert response.status_code == 422  # Validation error


def test_sonify_invalid_field_type():
    """Test sonification with invalid field type"""
    response = client.post(
        "/api/sonify",
        json={
            "beta": 4.0,
            "theta": 50.0,
            "field_type": "invalid_type"
        }
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# POST /api/analyze Tests
# ============================================================================

def test_analyze_basic():
    """Test analysis endpoint with basic logistic data"""
    # Generate simple logistic data
    R = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sigma = [0.01, 0.02, 0.05, 0.12, 0.35, 0.68, 0.88, 0.95, 0.98, 0.99]

    response = client.post(
        "/api/analyze",
        json={
            "R": R,
            "sigma": sigma,
            "bootstrap_iterations": 100  # Low for test speed
        }
    )
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "theta" in data
    assert "theta_ci" in data
    assert "beta" in data
    assert "beta_ci" in data
    assert "r_squared" in data
    assert "aic" in data
    assert "null_models" in data
    assert "field_type" in data

    # Check ranges
    assert 0.0 <= data["theta"] <= 1.0
    assert 0.1 <= data["beta"] <= 20.0
    assert 0.0 <= data["r_squared"] <= 1.0

    # Check null models
    null_models = data["null_models"]
    assert "linear" in null_models
    assert "exponential" in null_models


def test_analyze_mismatched_arrays():
    """Test analysis with mismatched array lengths"""
    response = client.post(
        "/api/analyze",
        json={
            "R": [0.1, 0.2, 0.3],
            "sigma": [0.01, 0.02]  # Different length
        }
    )
    assert response.status_code == 422  # Validation error


def test_analyze_sigma_out_of_range():
    """Test analysis with sigma values outside [0,1]"""
    response = client.post(
        "/api/analyze",
        json={
            "R": [0.1, 0.2, 0.3, 0.4, 0.5],
            "sigma": [0.1, 0.2, 1.5, 0.4, 0.5]  # 1.5 > 1.0
        }
    )
    assert response.status_code == 422  # Validation error


def test_analyze_too_few_points():
    """Test analysis with too few data points"""
    response = client.post(
        "/api/analyze",
        json={
            "R": [0.1, 0.2],
            "sigma": [0.1, 0.2]  # < 5 points
        }
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# GET /api/system/{system_id} Tests
# ============================================================================

def test_get_system_amazon():
    """Test getting Amazon system metadata"""
    response = client.get("/api/system/amazon")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "amazon"
    assert "name" in data
    assert "domain" in data
    assert "parameters" in data
    assert "field_type" in data
    assert "references" in data
    assert "data_sources" in data

    # Check parameters
    params = data["parameters"]
    assert "beta" in params
    assert "beta_ci" in params
    assert "theta" in params
    assert "theta_ci" in params
    assert "r_squared" in params


def test_get_system_not_found():
    """Test getting non-existent system"""
    response = client.get("/api/system/nonexistent_system_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_system_adaptive_theta():
    """Test getting adaptive_theta system"""
    response = client.get("/api/system/adaptive_theta")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "adaptive_theta"


# ============================================================================
# POST /api/simulate Tests
# ============================================================================

def test_simulate_basic():
    """Test simulation endpoint with basic parameters"""
    response = client.post(
        "/api/simulate",
        json={
            "theta": 0.66,
            "beta": 4.8,
            "initial_R": 0.5,
            "initial_psi": 0.1,
            "initial_phi": 0.05,
            "duration": 1.0,  # Short for test
            "dt": 0.1  # Large step for test speed
        }
    )
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "time" in data
    assert "R" in data
    assert "psi" in data
    assert "phi" in data
    assert "sigma" in data
    assert "metadata" in data

    # Check array lengths match
    n_steps = len(data["time"])
    assert len(data["R"]) == n_steps
    assert len(data["psi"]) == n_steps
    assert len(data["phi"]) == n_steps
    assert len(data["sigma"]) == n_steps

    # Check metadata
    metadata = data["metadata"]
    assert metadata["theta"] == 0.66
    assert metadata["beta"] == 4.8
    assert metadata["dt"] == 0.1


def test_simulate_with_stimulus():
    """Test simulation with custom stimulus"""
    response = client.post(
        "/api/simulate",
        json={
            "theta": 0.5,
            "beta": 4.0,
            "duration": 1.0,
            "dt": 0.1,
            "stimulus": {
                "base": 0.2,
                "amplitude": 0.3,
                "frequency": 1.0
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "time" in data
    assert len(data["time"]) > 0


def test_simulate_invalid_duration():
    """Test simulation with invalid duration"""
    response = client.post(
        "/api/simulate",
        json={
            "theta": 0.5,
            "beta": 4.0,
            "duration": 150.0  # > 100.0 max
        }
    )
    assert response.status_code == 422  # Validation error


def test_simulate_invalid_dt():
    """Test simulation with invalid dt"""
    response = client.post(
        "/api/simulate",
        json={
            "theta": 0.5,
            "beta": 4.0,
            "dt": 0.2  # > 0.1 max
        }
    )
    assert response.status_code == 422  # Validation error


# ============================================================================
# Integration Tests
# ============================================================================

def test_analyze_then_sonify():
    """Test workflow: analyze data, then sonify result"""
    # Step 1: Analyze
    R = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sigma = [0.01, 0.02, 0.05, 0.12, 0.35, 0.68, 0.88, 0.95, 0.98, 0.99]

    analyze_response = client.post(
        "/api/analyze",
        json={"R": R, "sigma": sigma}
    )
    assert analyze_response.status_code == 200
    analyze_data = analyze_response.json()

    # Step 2: Sonify with fitted parameters
    sonify_response = client.post(
        "/api/sonify",
        json={
            "beta": analyze_data["beta"],
            "theta": analyze_data["theta"] * 50,  # Scale theta
            "duration": 0.5,
            "sample_rate": 22050
        }
    )
    assert sonify_response.status_code == 200
    sonify_data = sonify_response.json()
    assert "audio_base64" in sonify_data


def test_get_system_then_simulate():
    """Test workflow: get system metadata, then simulate"""
    # Step 1: Get system
    system_response = client.get("/api/system/amazon")
    assert system_response.status_code == 200
    system_data = system_response.json()

    # Step 2: Simulate with system parameters
    params = system_data["parameters"]
    simulate_response = client.post(
        "/api/simulate",
        json={
            "theta": params["theta"],
            "beta": params["beta"],
            "duration": 1.0,
            "dt": 0.1
        }
    )
    assert simulate_response.status_code == 200
    simulate_data = simulate_response.json()
    assert len(simulate_data["time"]) > 0


# ============================================================================
# Performance Tests
# ============================================================================

def test_sonify_performance():
    """Test that sonification completes in reasonable time"""
    import time
    start = time.time()

    response = client.post(
        "/api/sonify",
        json={
            "beta": 4.0,
            "theta": 50.0,
            "duration": 1.0,
            "sample_rate": 22050
        }
    )

    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 5.0  # Should complete in < 5 seconds


def test_analyze_performance():
    """Test that analysis completes in reasonable time"""
    import time

    R = [i * 0.1 for i in range(11)]
    sigma = [1 / (1 + 10 * (0.5 - r) ** 4) for r in R]

    start = time.time()
    response = client.post(
        "/api/analyze",
        json={
            "R": R,
            "sigma": sigma,
            "bootstrap_iterations": 100
        }
    )

    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 3.0  # Should complete in < 3 seconds


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
