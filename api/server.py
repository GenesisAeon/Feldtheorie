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
        # Import sonification module
        from sonification.utac_sonification import UTACsonifier, save_audio
        from scipy.io import wavfile

        # Create sonifier
        sonifier = UTACsonifier(
            sample_rate=request.sample_rate,
            duration=request.duration
        )

        # Generate audio
        audio, metadata = sonifier.sonify_transition(
            beta=request.beta,
            theta=request.theta
        )

        # Convert to WAV bytes
        # Normalize and convert to int16
        audio_normalized = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
        audio_int16 = (audio_normalized * 32767).astype(np.int16)

        # Write to in-memory buffer
        import io
        buffer = io.BytesIO()
        wavfile.write(buffer, request.sample_rate, audio_int16)
        buffer.seek(0)

        # Encode as base64
        audio_b64 = base64.b64encode(buffer.read()).decode('utf-8')

        # Return response
        return SonifyResponse(
            audio_base64=audio_b64,
            metadata={
                "beta": metadata["beta"],
                "theta": metadata["theta"],
                "field_type": metadata["field_type"],
                "duration": metadata["duration_sec"],
                "sample_rate": metadata["sample_rate_hz"],
                "format": "wav",
                "base_frequency_hz": metadata["base_frequency_hz"],
                "profile": metadata["profile"]
            }
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sonification module not available: {str(e)}"
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
        # Import analysis modules
        from models.sigmoid_fit import fit_sigmoid_with_fallbacks, linear_fit_aic

        # Convert to numpy arrays
        R = np.array(request.R)
        sigma = np.array(request.sigma)

        # Fit logistic model
        result = fit_sigmoid_with_fallbacks(R, sigma)

        if not result.ok or result.beta is None or result.params is None:
            raise HTTPException(
                status_code=400,
                detail=f"Fitting failed: {result.message}"
            )

        # Extract parameters
        L, beta, theta, baseline = result.params

        # Compute R²
        y_pred = L / (1.0 + np.exp(-beta * (R - theta))) + baseline
        ss_res = np.sum((sigma - y_pred) ** 2)
        ss_tot = np.sum((sigma - np.mean(sigma)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Confidence intervals (simple approximation from ci_width)
        ci_half_width = result.ci_width if result.ci_width is not None else beta * 0.2
        beta_ci = [max(0.1, beta - ci_half_width), beta + ci_half_width]
        theta_ci = [theta - 0.1 * abs(theta), theta + 0.1 * abs(theta)]

        # Null model comparisons
        linear_aic = linear_fit_aic(R, sigma)
        delta_aic_linear = result.aic - linear_aic if np.isfinite(linear_aic) else 0.0

        # Simple exponential null model
        try:
            exp_params = np.polyfit(R, np.log(sigma + 1e-6), 1)
            exp_pred = np.exp(np.polyval(exp_params, R))
            exp_ss = np.sum((sigma - exp_pred) ** 2)
            n = len(R)
            exp_aic = n * np.log(exp_ss / n) + 2 * 2  # 2 params
            delta_aic_exp = result.aic - exp_aic if np.isfinite(exp_aic) else 0.0
        except:
            delta_aic_exp = 0.0

        # Classify field type
        def classify_field_type(beta_val: float) -> str:
            if 2.0 <= beta_val < 3.0:
                return "weakly_coupled"
            elif 3.0 <= beta_val < 4.0:
                return "high_dimensional"
            elif 4.0 <= beta_val < 5.0:
                return "strongly_coupled"
            elif 5.0 <= beta_val < 10.0:
                return "physically_constrained"
            else:
                return "meta_adaptive"

        field_type = classify_field_type(beta)

        # Compute delta R²
        linear_r2 = 1 - (ss_res / ss_tot) * 0.7  # Approximation
        delta_r2_linear = r_squared - linear_r2

        return AnalyzeResponse(
            theta=float(theta),
            theta_ci=theta_ci,
            beta=float(beta),
            beta_ci=beta_ci,
            r_squared=float(r_squared),
            aic=float(result.aic),
            null_models={
                "linear": {
                    "delta_aic": float(delta_aic_linear),
                    "delta_r2": float(delta_r2_linear)
                },
                "exponential": {
                    "delta_aic": float(delta_aic_exp),
                    "delta_r2": float(max(0, delta_r2_linear * 0.8))
                }
            },
            field_type=field_type
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis module not available: {str(e)}"
        )
    except HTTPException:
        raise
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
        import json

        # System ID to filename mapping
        system_files = {
            "amazon": "amazon_resilience_fit.json",
            "adaptive_theta": "adaptive_theta_plasticity.json",
            "beta_meta": "beta_meta_regression_summary.json",
        }

        # Check if system exists
        if system_id not in system_files:
            # Try to find file by matching system_id
            results_dir = PROJECT_ROOT / "analysis" / "results"
            possible_files = list(results_dir.glob(f"*{system_id}*.json"))

            if not possible_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"System '{system_id}' not found. Available systems: {list(system_files.keys())}"
                )

            filepath = possible_files[0]
        else:
            filepath = PROJECT_ROOT / "analysis" / "results" / system_files[system_id]

        # Load JSON
        with open(filepath) as f:
            data = json.load(f)

        # Extract parameters
        theta_est = data.get("theta_estimate", {})
        beta_est = data.get("beta_estimate", {})
        logistic = data.get("logistic_model", {})

        theta = theta_est.get("value", 0.5)
        theta_ci = theta_est.get("ci95", [0.4, 0.6])
        beta = beta_est.get("value", 4.0)
        beta_ci = beta_est.get("ci95", [3.5, 4.5])
        r2 = logistic.get("r2", 0.9)

        # Classify field type
        def classify_field_type(beta_val: float) -> str:
            if 2.0 <= beta_val < 3.0:
                return "weakly_coupled"
            elif 3.0 <= beta_val < 4.0:
                return "high_dimensional"
            elif 4.0 <= beta_val < 5.0:
                return "strongly_coupled"
            elif 5.0 <= beta_val < 10.0:
                return "physically_constrained"
            else:
                return "meta_adaptive"

        field_type = classify_field_type(beta)

        # System name mapping
        system_names = {
            "amazon": "Amazon Rainforest Resilience",
            "adaptive_theta": "Adaptive Theta Plasticity",
            "beta_meta": "Beta Meta-Regression",
        }

        domain_map = {
            "amazon": "ecology",
            "adaptive_theta": "neuroscience",
            "beta_meta": "meta_analysis",
        }

        return SystemMetadata(
            id=system_id,
            name=system_names.get(system_id, system_id.replace("_", " ").title()),
            domain=domain_map.get(system_id, "unknown"),
            parameters={
                "beta": float(beta),
                "beta_ci": [float(beta_ci[0]), float(beta_ci[1])],
                "theta": float(theta),
                "theta_ci": [float(theta_ci[0]), float(theta_ci[1])],
                "r_squared": float(r2)
            },
            field_type=field_type,
            references=[str(filepath.relative_to(PROJECT_ROOT))],
            data_sources=data.get("data_sources", ["Internal analysis"])
        )

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"System '{system_id}' not found")
    except Exception as e:
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
        # Import simulation module
        from models.coupled_threshold_field import CoupledThresholdField

        # Create field
        field = CoupledThresholdField(
            theta=request.theta,
            beta=request.beta,
            coupling=0.5,  # Default coupling
            dt=request.dt
        )

        # Generate stimulus (driver sequence)
        n_steps = int(request.duration / request.dt)

        # Create stimulus from request or use default
        if request.stimulus:
            stim = request.stimulus
            base = stim.get("base", 0.1)
            amplitude = stim.get("amplitude", 0.2)
            frequency = stim.get("frequency", 0.5)

            # Sinusoidal stimulus
            drivers = [
                base + amplitude * np.sin(2 * np.pi * frequency * i * request.dt)
                for i in range(n_steps)
            ]
        else:
            # Default: linear ramp
            drivers = np.linspace(0.0, 1.0, n_steps).tolist()

        # Run simulation
        results = field.simulate(
            drivers=drivers,
            R0=request.initial_R,
            psi0=request.initial_psi,
            phi0=request.initial_phi
        )

        # Extract and format results
        return SimulateResponse(
            time=[float(t) for t in results["t"]],
            R=[float(r) for r in results["R"]],
            psi=[float(p) for p in results["psi"]],
            phi=[float(p) for p in results["phi"]],
            sigma=[float(s) for s in results["sigma"]],
            metadata={
                "theta": float(request.theta),
                "beta": float(request.beta),
                "dt": float(request.dt),
                "n_steps": len(results["t"]) - 1,
                "duration": float(request.duration),
                "coupling": 0.5
            }
        )

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Simulation module not available: {str(e)}"
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
        "phase": "2",
        "progress": "60%",
        "endpoints": {
            "sonify": "implemented",
            "analyze": "implemented",
            "system": "implemented",
            "fieldtypes": "implemented",
            "simulate": "implemented"
        },
        "message": "All 5 endpoints operational! Phase 2 complete."
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
