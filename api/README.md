# 🌐 UTAC Modular API

REST API for the Unified Theory of Adaptive Criticality (UTAC) modules.

**Version:** 1.0.0
**Status:** 🟡 IN DEVELOPMENT (Phase 1 Complete)

---

## 📋 Overview

This API provides programmatic access to UTAC's core capabilities:

- **🎵 Sonification**: Generate audio from threshold dynamics
- **📊 Analysis**: Perform β-fits on empirical data
- **🔬 Simulation**: Run coupled threshold field simulations
- **📚 Metadata**: Access system and field type information

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
cd /home/user/Feldtheorie
pip install -r api/requirements.txt

# Run server
uvicorn api.server:app --reload --port 8000
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

## 📡 Endpoints

### 1. **POST /api/sonify** - Generate Audio

Convert UTAC parameters into audio.

**Request:**
```json
{
  "beta": 4.2,
  "theta": 50.0,
  "field_type": "strongly_coupled",
  "duration": 5.0,
  "sample_rate": 44100
}
```

**Response:** WAV audio (binary) or JSON metadata

**Status:** ✅ **IMPLEMENTED** (Phase 2)

---

### 2. **POST /api/analyze** - Perform β-Fit

Fit logistic model to empirical data.

**Request:**
```json
{
  "R": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
  "sigma": [0.01, 0.02, 0.05, 0.12, 0.35, 0.68, 0.88, 0.95, 0.98, 0.99],
  "bootstrap_iterations": 1000
}
```

**Response:**
```json
{
  "theta": 0.45,
  "theta_ci": [0.42, 0.48],
  "beta": 4.5,
  "beta_ci": [4.2, 4.8],
  "r_squared": 0.98,
  "aic": -245.6,
  "null_models": {
    "linear": {"delta_aic": 120.4, "delta_r2": 0.15}
  },
  "field_type": "strongly_coupled"
}
```

**Status:** ✅ **IMPLEMENTED** (Phase 2)

---

### 3. **GET /api/system/{system_id}** - System Metadata

Get metadata for a specific UTAC system.

**Example:**
```bash
GET /api/system/amoc
```

**Response:**
```json
{
  "id": "amoc",
  "name": "Atlantic Meridional Overturning Circulation",
  "domain": "climate",
  "parameters": {
    "beta": 4.2,
    "beta_ci": [3.9, 4.5],
    "theta": 50.0,
    "r_squared": 0.95
  },
  "field_type": "strongly_coupled",
  "references": ["analysis/results/amoc_transport_fit.json"],
  "data_sources": ["RAPID Array 26°N"]
}
```

**Status:** ✅ **IMPLEMENTED** (Phase 2)

---

### 4. **GET /api/fieldtypes** - List Field Types

Get overview of all 5 UTAC field types.

**Response:**
```json
{
  "field_types": [
    {
      "name": "weakly_coupled",
      "beta_range": [2.0, 3.0],
      "description": "Gradual transitions, diffuse coupling",
      "examples": ["Ecosystem succession"],
      "acoustic_profile": {
        "base_frequency": 110.0,
        "timbre": "Soft, diffuse"
      }
    },
    ...
  ]
}
```

**Status:** ✅ **IMPLEMENTED**

---

### 5. **POST /api/simulate** - Run Simulation

Simulate coupled threshold dynamics.

**Request:**
```json
{
  "theta": 0.66,
  "beta": 4.8,
  "initial_R": 0.5,
  "initial_psi": 0.1,
  "initial_phi": 0.05,
  "duration": 10.0,
  "dt": 0.01
}
```

**Response:**
```json
{
  "time": [0.0, 0.01, 0.02, ...],
  "R": [0.5, 0.51, 0.52, ...],
  "psi": [0.1, 0.11, 0.12, ...],
  "phi": [0.05, 0.06, 0.07, ...],
  "sigma": [0.3, 0.35, 0.4, ...],
  "metadata": {
    "theta": 0.66,
    "beta": 4.8,
    "dt": 0.01,
    "n_steps": 1000
  }
}
```

**Status:** ✅ **IMPLEMENTED** (Phase 2)

---

## 🧪 Testing

```bash
# Run API tests
pytest tests/test_api.py -v

# Test with curl
curl http://localhost:8000/api/fieldtypes

# Test with Python
import requests
response = requests.get("http://localhost:8000/api/fieldtypes")
print(response.json())
```

---

## 📚 Logistic Framework

All UTAC systems follow the logistic activation function:

```
σ(β(R-Θ))
```

Where:
- **R**: Control parameter (0-1 or system-specific)
- **Θ (Theta)**: Threshold value
- **β (Beta)**: Steepness parameter (criticality measure)
- **σ**: Logistic function (0-1)

### Field Types

UTAC classifies systems into 5 field types based on β:

1. **Weakly Coupled** (β ≈ 2-3): Gradual transitions
2. **High-Dimensional** (β ≈ 3-4): Complex dynamics
3. **Strongly Coupled** (β ≈ 4-5): Sharp thresholds
4. **Physically Constrained** (β ≈ 5-10): Hard limits
5. **Meta-Adaptive** (β > 10): Extreme sensitivity

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t utac-api .

# Run container
docker run -p 8000:8000 utac-api

# With docker-compose
docker-compose up -d
```

**Status:** 🔴 Not Implemented (Phase 4)

---

## 📊 Development Status

**Phase 1: Foundation** (✅ COMPLETED)
- [x] OpenAPI 3.0 Spec (`openapi.yaml`)
- [x] FastAPI Server Skeleton (`server.py`)
- [x] Requirements (`requirements.txt`)
- [x] Initial README

**Phase 2: Core Endpoints** (✅ COMPLETED - R: 0.25 → 0.60)
- [x] POST /api/sonify ✅
- [x] POST /api/analyze ✅
- [x] GET /api/system/:id ✅
- [x] GET /api/fieldtypes ✅
- [x] POST /api/simulate ✅

**Phase 3: Docs & Tests** (🔴 PENDING)
- [ ] Comprehensive README
- [ ] API Tests (`tests/test_api.py`)
- [ ] Usage Examples (`examples/`)

**Phase 4: Docker & Polish** (🔴 PENDING)
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] Production deployment guide

---

## 🤝 Contributing

This API is part of the Feldtheorie project. See main repo README for contribution guidelines.

---

## 📜 License

MIT License - see LICENSE file in main repository.

---

## 🔗 References

- **OpenAPI Spec**: `api/openapi.yaml`
- **Main Project**: https://github.com/GenesisAeon/Feldtheorie
- **UTAC Framework**: `docs/utac_theoretical_framework.md`
- **Sonification**: `sonification/README.md`

---

**Version:** 1.0.0 (Phase 1 Complete)
**Last Updated:** 2025-11-11
**Maintained by:** Claude Code + Johann Römer

*"σ(β(R-Θ)) now speaks HTTP!"* 🌐✨
