#!/usr/bin/env python3
"""
UTAC Modular API Server

REST API for Unified Theory of Adaptive Criticality modules.
Provides programmatic access to sonification, analysis, simulation, and metadata.

Usage:
    uvicorn api.server:app --reload --port 8000

OpenAPI Docs:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import io
import base64
import numpy as np
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Import UTAC modules
try:
    from sonification.utac_sonification import (
        sonify_threshold,
        get_field_type_profile,
        FIELD_TYPES
    )
    from models.sigmoid_fit import fit_sigmoid
    from models.coupled_threshold_field import (
        CoupledThresholdField,
        simulate_coupled_dynamics
    )
except ImportError as e:
    print(f"Warning: Could not import UTAC modules: {e}")
    print("API will run with limited functionality.")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="UTAC Modular API",
    description="""
REST API for the Unified Theory of Adaptive Criticality (UTAC) modules.

## Features

- **Sonification**: Generate audio from threshold dynamics
- **Analysis**: Perform β-fits on empirical data
- **Simulation**: Run coupled threshold field simulations
- **Metadata**: Access system and field type information

## Logistic Framework

All UTAC systems follow σ(β(R-Θ)):
- **R**: Control parameter
- **Θ**: Threshold value
- **β**: Steepness (criticality measure)
- **σ**: Logistic activation

See OpenAPI spec for full details: `/openapi.json`
    """,
    version="1.0.0",
    contact={
        "name": "Feldtheorie Project",
        "url": "https://github.com/GenesisAeon/Feldtheorie"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)


# ============================================================================
# Pydantic Models
# ============================================================================

class SonifyRequest(BaseModel):
    beta: float = Field(..., ge=0.1, le=20.0, description="Steepness parameter β")
    theta: float = Field(..., description="Threshold value Θ")
    field_type: Optional[str] = Field(
        "strongly_coupled",
        description="UTAC field type"
    )
    duration: float = Field(5.0, ge=0.1, le=60.0, description="Audio duration (s)")
    sample_rate: int = Field(44100, description="Sample rate (Hz)")
    preset: Optional[str] = Field(None, description="Optional preset name")

    @validator('field_type')
    def validate_field_type(cls, v):
        valid_types = ['weakly_coupled', 'high_dimensional', 'strongly_coupled',
                      'physically_constrained', 'meta_adaptive']
        if v not in valid_types:
            raise ValueError(f"field_type must be one of {valid_types}")
        return v

    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        if v not in [22050, 44100, 48000]:
            raise ValueError("sample_rate must be 22050, 44100, or 48000")
        return v


class SonifyResponse(BaseModel):
    audio_base64: str
    metadata: Dict[str, Any]


class AnalyzeRequest(BaseModel):
    R: List[float] = Field(..., min_items=5, description="Control parameter values")
    sigma: List[float] = Field(..., min_items=5, description="Order parameter values")
    bootstrap_iterations: int = Field(1000, ge=100, le=10000)
    null_models: List[str] = Field(
        ["linear", "exponential", "power_law"],
        description="Null models to compare"
    )

    @validator('sigma')
    def validate_sigma(cls, v):
        if any(s < 0 or s > 1 for s in v):
            raise ValueError("sigma values must be between 0 and 1")
        return v

    @validator('R', 'sigma')
    def validate_lengths_match(cls, v, values):
        if 'R' in values and len(values['R']) != len(v):
            raise ValueError("R and sigma must have same length")
        return v


class AnalyzeResponse(BaseModel):
    theta: float
    theta_ci: List[float]
    beta: float
    beta_ci: List[float]
    r_squared: float
    aic: float
    null_models: Dict[str, Dict[str, float]]
    field_type: str


class SimulateRequest(BaseModel):
    theta: float = Field(..., description="Threshold value Θ")
    beta: float = Field(..., description="Steepness parameter β")
    initial_R: float = Field(0.5, description="Initial control parameter")
    initial_psi: float = Field(0.1, description="Initial potential")
    initial_phi: float = Field(0.05, description="Initial coherence")
    duration: float = Field(10.0, ge=1.0, le=100.0, description="Simulation duration")
    dt: float = Field(0.01, ge=0.001, le=0.1, description="Time step")
    stimulus: Optional[Dict[str, float]] = Field(
        None,
        description="Stimulus parameters (base, amplitude, frequency)"
    )


class SimulateResponse(BaseModel):
    time: List[float]
    R: List[float]
    psi: List[float]
    phi: List[float]
    sigma: List[float]
    metadata: Dict[str, Any]


class SystemMetadata(BaseModel):
    id: str
    name: str
    domain: str
    parameters: Dict[str, Any]
    field_type: str
    references: List[str]
    data_sources: List[str]


class FieldTypesResponse(BaseModel):
    field_types: List[Dict[str, Any]]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return {
        "message": "UTAC Modular API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.post("/api/sonify", response_model=SonifyResponse, tags=["sonification"])
async def sonify(request: SonifyRequest):
    """
    Generate audio from threshold dynamics.

    Converts UTAC parameters (β, Θ, R-trajectory) into audio using field type
    acoustic profiles.

    **Acoustic Mapping:**
    - β → Pitch (steeper = higher frequency)
    - R-Θ → Amplitude (closer to threshold = louder)
    - σ(β(R-Θ)) → Envelope (peak at threshold crossing)
    """
    try:
        # TODO: Implement sonification using utac_sonification module
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="Sonification endpoint not yet implemented"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["analysis"])
async def analyze(request: AnalyzeRequest):
    """
    Perform β-fit on threshold data.

    Fits logistic model σ(β(R-Θ)) to empirical data and returns:
    - Best-fit parameters (β, Θ)
    - Confidence intervals (bootstrap)
    - Model comparison (ΔAIC vs null models)
    - Field type classification
    """
    try:
        # TODO: Implement analysis using sigmoid_fit module
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="Analysis endpoint not yet implemented"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/{system_id}", response_model=SystemMetadata, tags=["metadata"])
async def get_system(system_id: str):
    """
    Get system metadata.

    Returns metadata for a specific UTAC system including:
    - System name and domain
    - Fitted parameters (β, Θ, R²)
    - Field type classification
    - References and data sources
    """
    try:
        # TODO: Load system metadata from analysis/results/ or database
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="System metadata endpoint not yet implemented"
        )

    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"System '{system_id}' not found")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fieldtypes", response_model=FieldTypesResponse, tags=["metadata"])
async def get_field_types():
    """
    List all field types.

    Returns overview of all 5 UTAC field types with:
    - β-range and acoustic profile
    - Example systems
    - Characteristic dynamics
    """
    try:
        field_types = [
            {
                "name": "weakly_coupled",
                "beta_range": [2.0, 3.0],
                "description": "Gradual transitions, diffuse coupling",
                "examples": ["Ecosystem succession", "Diffusion processes"],
                "acoustic_profile": {
                    "base_frequency": 110.0,
                    "timbre": "Soft, diffuse, ambient"
                }
            },
            {
                "name": "high_dimensional",
                "beta_range": [3.0, 4.0],
                "description": "Complex, multi-scale dynamics",
                "examples": ["LLM emergence", "Neural networks", "Semantic shifts"],
                "acoustic_profile": {
                    "base_frequency": 329.63,
                    "timbre": "Ethereal, complex, layered"
                }
            },
            {
                "name": "strongly_coupled",
                "beta_range": [4.0, 5.0],
                "description": "Sharp, resonant thresholds",
                "examples": ["AMOC collapse", "Phase transitions", "QPO resonance"],
                "acoustic_profile": {
                    "base_frequency": 220.0,
                    "timbre": "Warm, resonant, clear"
                }
            },
            {
                "name": "physically_constrained",
                "beta_range": [5.0, 10.0],
                "description": "Hard physical limits",
                "examples": ["Boiling point", "Material failure", "Combustion"],
                "acoustic_profile": {
                    "base_frequency": 440.0,
                    "timbre": "Sharp, precise, metallic"
                }
            },
            {
                "name": "meta_adaptive",
                "beta_range": [10.0, 20.0],
                "description": "Extreme sensitivity, feedback loops",
                "examples": ["Urban heat islands", "Market crashes", "Cascading failures"],
                "acoustic_profile": {
                    "base_frequency": 261.63,
                    "timbre": "Morphing, adaptive, unstable"
                }
            }
        ]

        return FieldTypesResponse(field_types=field_types)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/simulate", response_model=SimulateResponse, tags=["simulation"])
async def simulate(request: SimulateRequest):
    """
    Run coupled threshold field simulation.

    Simulates coupled threshold dynamics using:
    - Membrane solver (coupled PDEs)
    - Resonant impedance ζ(R)
    - Coherence coupling φ

    Returns time series of (R, Ψ, φ, σ) for visualization.
    """
    try:
        # TODO: Implement simulation using coupled_threshold_field module
        # For now, return placeholder
        raise HTTPException(
            status_code=501,
            detail="Simulation endpoint not yet implemented"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "sonify": "not_implemented",
            "analyze": "not_implemented",
            "system": "not_implemented",
            "fieldtypes": "implemented",
            "simulate": "not_implemented"
        }
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
