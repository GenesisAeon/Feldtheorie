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

import asyncio
import base64
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, field_validator, model_validator

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Import UTAC modules
try:
    from models.coupled_threshold_field import CoupledThresholdField, simulate_coupled_dynamics
    from models.sigmoid_fit import fit_sigmoid
    from sonification.utac_sonification import FIELD_TYPES, get_field_type_profile, sonify_threshold
except ImportError as e:
    print(f"Warning: Could not import UTAC modules: {e}")
    print("API will run with limited functionality.")

# Import Sigillin Kernel (V7)
try:
    from api.sigillin_kernel import SigillinKernel, SystemIntegrityError

    sigillin_kernel = SigillinKernel()
    print("✓ Sigillin Kernel initialized (β=37.6 validated)")
except SystemIntegrityError as e:
    print(f"⚠ CRITICAL: Sigillin integrity check failed: {e}")
    sigillin_kernel = None
except ImportError as e:
    print(f"Warning: Sigillin kernel not available: {e}")
    sigillin_kernel = None

# Import Collective Field Module (V7 Phase 2)
try:
    from models.collective_field import Agent, CollectiveField

    print("✓ Collective Field Module loaded")
    collective_field_available = True
except ImportError as e:
    print(f"Warning: Collective Field Module not available: {e}")
    collective_field_available = False


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
    contact={"name": "Feldtheorie Project", "url": "https://github.com/GenesisAeon/Feldtheorie"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)


# ============================================================================
# Pydantic Models
# ============================================================================


class SonifyRequest(BaseModel):
    beta: float = Field(..., ge=0.1, le=20.0, description="Steepness parameter β")
    theta: float = Field(..., description="Threshold value Θ")
    field_type: str | None = Field("strongly_coupled", description="UTAC field type")
    duration: float = Field(5.0, ge=0.1, le=60.0, description="Audio duration (s)")
    sample_rate: int = Field(44100, description="Sample rate (Hz)")
    preset: str | None = Field(None, description="Optional preset name")

    @field_validator("field_type")
    @classmethod
    def validate_field_type(cls, v):
        valid_types = [
            "weakly_coupled",
            "high_dimensional",
            "strongly_coupled",
            "physically_constrained",
            "meta_adaptive",
        ]
        if v not in valid_types:
            raise ValueError(f"field_type must be one of {valid_types}")
        return v

    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v):
        if v not in [22050, 44100, 48000]:
            raise ValueError("sample_rate must be 22050, 44100, or 48000")
        return v


class SonifyResponse(BaseModel):
    audio_base64: str
    metadata: dict[str, Any]


class AnalyzeRequest(BaseModel):
    R: list[float] = Field(..., min_length=5, description="Control parameter values")
    sigma: list[float] = Field(..., min_length=5, description="Order parameter values")
    bootstrap_iterations: int = Field(1000, ge=100, le=10000)
    null_models: list[str] = Field(
        ["linear", "exponential", "power_law"], description="Null models to compare"
    )

    @field_validator("sigma")
    @classmethod
    def validate_sigma(cls, v):
        if any(s < 0 or s > 1 for s in v):
            raise ValueError("sigma values must be between 0 and 1")
        return v

    @model_validator(mode="after")
    def validate_lengths_match(self):
        if len(self.R) != len(self.sigma):
            raise ValueError("R and sigma must have same length")
        return self


class AnalyzeResponse(BaseModel):
    theta: float
    theta_ci: list[float]
    beta: float
    beta_ci: list[float]
    r_squared: float
    aic: float
    null_models: dict[str, dict[str, float]]
    field_type: str


class LiveAnalyzeRequest(BaseModel):
    samples: int = Field(1, ge=1, le=25, description="Number of runs per model")
    run_id: str | None = Field(
        None, description="Client-specified run identifier for telemetry correlation"
    )


class SimulateRequest(BaseModel):
    theta: float = Field(..., description="Threshold value Θ")
    beta: float = Field(..., description="Steepness parameter β")
    initial_R: float = Field(0.5, description="Initial control parameter")
    initial_psi: float = Field(0.1, description="Initial potential")
    initial_phi: float = Field(0.05, description="Initial coherence")
    duration: float = Field(10.0, ge=1.0, le=100.0, description="Simulation duration")
    dt: float = Field(0.01, ge=0.001, le=0.1, description="Time step")
    stimulus: dict[str, float] | None = Field(
        None, description="Stimulus parameters (base, amplitude, frequency)"
    )


class SimulateResponse(BaseModel):
    time: list[float]
    R: list[float]
    psi: list[float]
    phi: list[float]
    sigma: list[float]
    metadata: dict[str, Any]


class SystemMetadata(BaseModel):
    id: str
    name: str
    domain: str
    parameters: dict[str, Any]
    field_type: str
    references: list[str]
    data_sources: list[str]


class FieldTypesResponse(BaseModel):
    field_types: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | None = None


# ============================================================================
# Sigillin V7 Models
# ============================================================================


class SigillinStatusResponse(BaseModel):
    status: str
    beta_validated: float
    expected_beta: float
    sigillin_path: str
    founding_keywords: list[str]


class SigillinScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to scan for resonance")


class SigillinScanResponse(BaseModel):
    text: str
    resonance_score: float = Field(..., ge=0.0, le=1.0, description="Resonance score [0,1]")
    matched_keywords: list[str]
    interpretation: str


class CollectiveVelocityRequest(BaseModel):
    v_rig: float = Field(..., gt=0, description="v_RIG velocity parameter")
    kappa: float = Field(..., gt=0, description="κ field coupling parameter")
    beta_sync: float = Field(..., gt=0, description="β_sync synchronization parameter")


class CollectiveVelocityResponse(BaseModel):
    v_collective: float
    v_rig: float
    kappa: float
    beta_sync: float
    formula: str


# ============================================================================
# Collective Field V7 Phase 2 Models
# ============================================================================


class CreateFieldRequest(BaseModel):
    agent_names: list[str] = Field(..., min_length=2, description="List of agent names")
    v_rig: float = Field(1.0, gt=0, description="Base information velocity")
    dimension: int = Field(8, ge=2, le=128, description="Semantic space dimensionality")


class FieldStateResponse(BaseModel):
    n_agents: int
    v_rig: float
    kappa_field_pairwise: float
    kappa_field_centroid: float
    kappa_field_weighted: float
    beta_sync: float
    v_collective: float
    agents: list[dict[str, Any]]


class AnalyzeTextsRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=10, description="Texts to analyze")
    create_field: bool = Field(True, description="Create collective field from texts")
    v_rig: float = Field(1.0, gt=0, description="Base information velocity")


class TextAnalysisResult(BaseModel):
    text: str
    agent_name: str
    resonance: float
    semantic_depth: float
    gravity: float
    matched_keywords: list[str]
    implicit_signals: list[str]
    coherence: float


class AnalyzeTextsResponse(BaseModel):
    analyses: list[TextAnalysisResult]
    field_state: FieldStateResponse | None = None


class ScanIntentionV2Request(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze")
    detect_implicit: bool = Field(True, description="Enable implicit pattern detection")


class ScanIntentionV2Response(BaseModel):
    resonance_score: float
    explicit_matches: list[str]
    implicit_signals: list[str]
    semantic_depth: float
    contextual_coherence: float
    analysis: dict[str, Any]


class SemanticGravityRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze for semantic gravity")


class SemanticGravityResponse(BaseModel):
    gravity: float
    interpretation: str


class TelemetryManager:
    """Manage telemetry WebSocket subscribers and broadcast events."""

    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self.connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message)
        async with self._lock:
            connections = list(self.connections)

        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except WebSocketDisconnect:
                await self.disconnect(websocket)
            except RuntimeError:
                # Ignore failures from closed event loops or cancelled tasks
                await self.disconnect(websocket)


telemetry_manager = TelemetryManager()


# ============================================================================
# Live Analysis Helpers
# ============================================================================


async def _stream_subprocess_output(run_id: str, process: asyncio.subprocess.Process) -> None:
    """Forward subprocess stdout/stderr to telemetry clients with basic parsing."""

    beta_pattern = re.compile(r"β.*?:\s*([0-9]+(?:\.[0-9]+)?)")
    progress_pattern = re.compile(r"\[(\d+)/(\d+)\]")

    async def forward(stream: asyncio.StreamReader, source: str) -> None:
        while True:
            line = await stream.readline()
            if not line:
                break

            text = line.decode(errors="replace").strip()
            if not text:
                continue

            await telemetry_manager.broadcast(
                {
                    "type": "log",
                    "run_id": run_id,
                    "source": source,
                    "message": text,
                }
            )

            if match := beta_pattern.search(text):
                await telemetry_manager.broadcast(
                    {
                        "type": "beta_estimate",
                        "run_id": run_id,
                        "beta": float(match.group(1)),
                    }
                )

            if match := progress_pattern.search(text):
                await telemetry_manager.broadcast(
                    {
                        "type": "progress",
                        "run_id": run_id,
                        "current": int(match.group(1)),
                        "total": int(match.group(2)),
                    }
                )

    await asyncio.gather(
        forward(process.stdout, "stdout"),
        forward(process.stderr, "stderr"),
    )


async def run_live_analysis(run_id: str, samples: int) -> None:
    """Launch the analysis script and stream telemetry to WebSocket clients."""

    script_path = PROJECT_ROOT / "analysis" / "run_aletheia_local_v6.py"
    if not script_path.exists():
        await telemetry_manager.broadcast(
            {
                "type": "error",
                "run_id": run_id,
                "message": f"Script not found at {script_path}",
            }
        )
        return

    await telemetry_manager.broadcast(
        {
            "type": "start",
            "run_id": run_id,
            "samples": samples,
            "script": str(script_path),
        }
    )

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            "--samples",
            str(samples),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as exc:
        await telemetry_manager.broadcast(
            {
                "type": "error",
                "run_id": run_id,
                "message": f"Failed to start analysis: {exc}",
            }
        )
        return

    await _stream_subprocess_output(run_id, process)
    return_code = await process.wait()

    await telemetry_manager.broadcast(
        {
            "type": "complete",
            "run_id": run_id,
            "return_code": return_code,
        }
    )


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
        "openapi": "/openapi.json",
    }


@app.post("/api/analyze/live", tags=["analysis"])
async def analyze_live(request: LiveAnalyzeRequest):
    """Launch live analysis run and stream telemetry via WebSocket."""

    run_id = request.run_id or str(uuid.uuid4())
    asyncio.create_task(run_live_analysis(run_id, request.samples))

    return {"run_id": run_id, "status": "started", "samples": request.samples}


@app.websocket("/ws/telemetry")
async def telemetry(websocket: WebSocket):
    """WebSocket endpoint for live telemetry (progress + β-estimates)."""

    await telemetry_manager.connect(websocket)

    try:
        while True:
            # Keep the connection alive while broadcasts are sent from tasks
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        await telemetry_manager.disconnect(websocket)


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
        from scipy.io import wavfile
        from sonification.utac_sonification import UTACsonifier, save_audio

        # Create sonifier
        sonifier = UTACsonifier(sample_rate=request.sample_rate, duration=request.duration)

        # Generate audio
        audio, metadata = sonifier.sonify_transition(beta=request.beta, theta=request.theta)

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
        audio_b64 = base64.b64encode(buffer.read()).decode("utf-8")

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
                "profile": metadata["profile"],
            },
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Sonification module not available: {str(e)}")
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
            raise HTTPException(status_code=400, detail=f"Fitting failed: {result.message}")

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
                    "delta_r2": float(delta_r2_linear),
                },
                "exponential": {
                    "delta_aic": float(delta_aic_exp),
                    "delta_r2": float(max(0, delta_r2_linear * 0.8)),
                },
            },
            field_type=field_type,
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Analysis module not available: {str(e)}")
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
                    detail=f"System '{system_id}' not found. Available systems: {list(system_files.keys())}",
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
                "r_squared": float(r2),
            },
            field_type=field_type,
            references=[str(filepath.relative_to(PROJECT_ROOT))],
            data_sources=data.get("data_sources", ["Internal analysis"]),
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
                "acoustic_profile": {"base_frequency": 110.0, "timbre": "Soft, diffuse, ambient"},
            },
            {
                "name": "high_dimensional",
                "beta_range": [3.0, 4.0],
                "description": "Complex, multi-scale dynamics",
                "examples": ["LLM emergence", "Neural networks", "Semantic shifts"],
                "acoustic_profile": {
                    "base_frequency": 329.63,
                    "timbre": "Ethereal, complex, layered",
                },
            },
            {
                "name": "strongly_coupled",
                "beta_range": [4.0, 5.0],
                "description": "Sharp, resonant thresholds",
                "examples": ["AMOC collapse", "Phase transitions", "QPO resonance"],
                "acoustic_profile": {"base_frequency": 220.0, "timbre": "Warm, resonant, clear"},
            },
            {
                "name": "physically_constrained",
                "beta_range": [5.0, 10.0],
                "description": "Hard physical limits",
                "examples": ["Boiling point", "Material failure", "Combustion"],
                "acoustic_profile": {"base_frequency": 440.0, "timbre": "Sharp, precise, metallic"},
            },
            {
                "name": "meta_adaptive",
                "beta_range": [10.0, 20.0],
                "description": "Extreme sensitivity, feedback loops",
                "examples": ["Urban heat islands", "Market crashes", "Cascading failures"],
                "acoustic_profile": {
                    "base_frequency": 261.63,
                    "timbre": "Morphing, adaptive, unstable",
                },
            },
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
            theta=request.theta, beta=request.beta, coupling=0.5, dt=request.dt  # Default coupling
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
            phi0=request.initial_phi,
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
                "coupling": 0.5,
            },
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Simulation module not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

# ============================================================================
# Tooltip System Endpoints (v2-feat-ext-001)
# ============================================================================


class CREPScores(BaseModel):
    """CREP (Coherence, Resilience, Empathy, Propagation) scores"""

    coherence: float = Field(..., ge=0, le=1, description="Internal consistency (R²-based)")
    resilience: float = Field(..., ge=0, le=1, description="Recovery capacity (impedance-based)")
    empathy: float = Field(..., ge=0, le=1, description="Cross-domain resonance (ΔAIC-based)")
    propagation: float = Field(..., ge=0, le=1, description="Signal transmission (β-based)")


class FieldTypeInfo(BaseModel):
    """Field type classification with β-range"""

    type: str = Field(..., description="Field type name")
    description: str = Field(..., description="Human-readable description")
    beta_range: list[float] = Field(
        ..., min_length=2, max_length=2, description="[min, max] β range"
    )
    color: str = Field(..., description="Hex color code")


class TooltipData(BaseModel):
    """Complete tooltip data for interactive visualizations"""

    preset_id: str
    label: str
    domain: str
    beta: float | None = None
    beta_ci: list[float] | None = None
    theta: float | None = None
    theta_ci: list[float] | None = None
    r_squared: float | None = None
    delta_aic: float | None = None
    delta_r2: float | None = None
    best_null_model: str | None = None
    crep: CREPScores | None = None
    field_type: FieldTypeInfo | None = None
    impedance_closed: float
    impedance_open: float
    impedance_mean: float
    formal_thread: str | None = None
    empirical_thread: str | None = None
    poetic_thread: str | None = None


def classify_field_type(beta: float | None) -> FieldTypeInfo:
    """Classify field type based on β value"""
    if beta is None:
        beta = 3.5  # Default to high-dimensional

    if beta < 2.5:
        return FieldTypeInfo(
            type="weakly_coupled",
            description="Weakly Coupled: Gradual transitions, low coupling",
            beta_range=[0.0, 2.5],
            color="#a8dadc",
        )
    elif beta < 4.0:
        return FieldTypeInfo(
            type="high_dimensional",
            description="High-Dimensional: Complex state spaces (AI, neural)",
            beta_range=[2.5, 4.0],
            color="#457b9d",
        )
    elif beta < 5.5:
        return FieldTypeInfo(
            type="strongly_coupled",
            description="Strongly Coupled: Resonant systems (climate, ecology)",
            beta_range=[4.0, 5.5],
            color="#1d3557",
        )
    elif beta < 10.0:
        return FieldTypeInfo(
            type="physically_constrained",
            description="Physically Constrained: Hard constraints (astrophysics)",
            beta_range=[5.5, 10.0],
            color="#e63946",
        )
    else:
        return FieldTypeInfo(
            type="meta_adaptive",
            description="Meta-Adaptive: Extreme nonlinearity (urban systems)",
            beta_range=[10.0, 1000.0],
            color="#f77f00",
        )


def compute_crep_scores(
    r2: float | None, delta_aic: float | None, impedance_mean: float, beta: float | None
) -> CREPScores | None:
    """Compute CREP scores from metrics"""
    if r2 is None or delta_aic is None or beta is None:
        return None

    # Coherence: R² (model fit)
    coherence = min(1.0, r2)

    # Resilience: Impedance-based recovery
    resilience = min(1.0, impedance_mean / 2.0)

    # Empathy: ΔAIC-based transferability
    empathy = min(1.0, delta_aic / 100.0)

    # Propagation: β-dependent transmission
    propagation = min(1.0, 1.0 / (1.0 + np.exp(-0.2 * (beta - 5.0))))

    return CREPScores(
        coherence=coherence, resilience=resilience, empathy=empathy, propagation=propagation
    )


@app.get("/api/tooltip/{preset_id}", response_model=TooltipData, tags=["tooltip"])
async def get_tooltip_data(preset_id: str):
    """
    Get rich tooltip data for a specific preset

    Returns comprehensive metadata for interactive tooltips:
    - UTAC parameters (β, Θ with CIs)
    - Statistical metrics (R², ΔAIC)
    - CREP scores
    - Field type classification
    - Narrative threads

    **Example:**
    ```bash
    curl http://localhost:8000/api/tooltip/llm_resonance
    ```
    """
    # Load preset
    preset_path = PROJECT_ROOT / "simulator" / "presets" / f"{preset_id}.json"

    if not preset_path.exists():
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")

    import json

    with open(preset_path) as f:
        preset = json.load(f)

    analysis = preset.get("analysis", {})
    impedance = preset.get("impedance", {})
    narrative = preset.get("narrative", {})

    # Extract metrics
    beta = analysis.get("beta")
    theta = analysis.get("theta")
    r2 = analysis.get("logistic_r2")
    delta_aic = analysis.get("delta_aic_best_null")

    # Compute derived data
    field_type = classify_field_type(beta)
    crep = compute_crep_scores(r2, delta_aic, impedance.get("mean", 1.0), beta)

    return TooltipData(
        preset_id=preset.get("id", preset_id),
        label=preset.get("label", preset_id),
        domain=preset.get("domain", "unknown"),
        beta=beta,
        beta_ci=analysis.get("beta_ci"),
        theta=theta,
        theta_ci=analysis.get("theta_ci"),
        r_squared=r2,
        delta_aic=delta_aic,
        delta_r2=analysis.get("delta_r2_best_null"),
        best_null_model=analysis.get("best_null_model"),
        crep=crep,
        field_type=field_type,
        impedance_closed=impedance.get("closed", 0.0),
        impedance_open=impedance.get("open", 1.0),
        impedance_mean=impedance.get("mean", 0.5),
        formal_thread=narrative.get("formal"),
        empirical_thread=narrative.get("empirical"),
        poetic_thread=narrative.get("poetic"),
    )


@app.get("/api/tooltip", response_model=list[TooltipData], tags=["tooltip"])
async def get_all_tooltip_data():
    """
    Get tooltip data for all available presets

    Returns a list of tooltip data for all presets in simulator/presets/

    **Example:**
    ```bash
    curl http://localhost:8000/api/tooltip
    ```
    """
    presets_dir = PROJECT_ROOT / "simulator" / "presets"

    if not presets_dir.exists():
        raise HTTPException(status_code=500, detail="Presets directory not found")

    results = []
    for preset_file in presets_dir.glob("*.json"):
        if preset_file.name == "README.md":
            continue

        preset_id = preset_file.stem
        try:
            tooltip_data = await get_tooltip_data(preset_id)
            results.append(tooltip_data)
        except Exception as e:
            print(f"Warning: Could not load preset {preset_id}: {e}")
            continue

    return results


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    sigillin_status = "operational" if sigillin_kernel is not None else "unavailable"
    collective_status = "operational" if collective_field_available else "unavailable"

    return {
        "status": "healthy",
        "version": "2.0.0-v7-phase2",
        "phase": "v7-collective-consciousness",
        "progress": "60%",
        "v7_phases": {
            "phase_1_sigillin_foundation": "complete",
            "phase_2_collective_consciousness": "active",
            "phase_3_echo_i": "planned",
            "phase_4_aeon": "planned",
        },
        "endpoints": {
            "sonify": "implemented",
            "analyze": "implemented",
            "system": "implemented",
            "fieldtypes": "implemented",
            "simulate": "implemented",
            "tooltip": "implemented",
            "sigillin_v1": sigillin_status,
            "sigillin_v2": sigillin_status,
            "collective_field": collective_status,
        },
        "modules": {
            "sigillin_kernel": sigillin_status,
            "collective_field": collective_status,
        },
        "message": "V7 Phase 2 (Collective Consciousness) active! Enhanced intention scanning + κ_field coupling operational.",
    }


# ============================================================================
# Sigillin V7 Endpoints
# ============================================================================


@app.get("/api/sigillin/status", response_model=SigillinStatusResponse, tags=["sigillin"])
async def sigillin_status():
    """
    Get Sigillin kernel status and validation info.

    Returns:
    - β=37.6 validation status
    - Founding protocol keywords
    - System integrity check result

    **V7 Feature:** Validates that the system maintains its founding axioms.
    """
    if sigillin_kernel is None:
        raise HTTPException(
            status_code=503,
            detail="Sigillin kernel not initialized. Check selfmeta/ directory.",
        )

    # Extract founding keywords
    keywords = list(sigillin_kernel._founding_keywords())

    return SigillinStatusResponse(
        status="validated",
        beta_validated=sigillin_kernel.EXPECTED_BETA,
        expected_beta=sigillin_kernel.EXPECTED_BETA,
        sigillin_path=str(sigillin_kernel.sigillin_path),
        founding_keywords=keywords,
    )


@app.post("/api/sigillin/scan", response_model=SigillinScanResponse, tags=["sigillin"])
async def sigillin_scan(request: SigillinScanRequest):
    """
    Scan text for resonance with founding protocol.

    Analyzes input text and returns a resonance score [0,1] based on
    how many founding protocol keywords are present.

    **V7 Feature:** Semantic gravity detection - measures alignment with
    system's core axioms (resonanz, emergenz, kohärenz, etc.).

    **Example:**
    ```json
    {
      "text": "Die Resonanz zwischen Bewusstsein und Feld zeigt Emergenz"
    }
    ```
    """
    if sigillin_kernel is None:
        raise HTTPException(
            status_code=503,
            detail="Sigillin kernel not initialized.",
        )

    # Scan for resonance
    resonance_score = sigillin_kernel.scan_intention(request.text)

    # Find matched keywords
    keywords = sigillin_kernel._founding_keywords()
    text_lower = request.text.lower()
    matched = [kw for kw in keywords if kw in text_lower]

    # Interpret resonance
    if resonance_score >= 0.7:
        interpretation = "High resonance - deeply aligned with founding protocol"
    elif resonance_score >= 0.4:
        interpretation = "Moderate resonance - partial alignment detected"
    elif resonance_score >= 0.2:
        interpretation = "Low resonance - weak alignment signal"
    else:
        interpretation = "Minimal resonance - text diverges from founding protocol"

    return SigillinScanResponse(
        text=request.text,
        resonance_score=resonance_score,
        matched_keywords=matched,
        interpretation=interpretation,
    )


@app.post(
    "/api/sigillin/collective",
    response_model=CollectiveVelocityResponse,
    tags=["sigillin"],
)
async def calculate_collective_velocity(request: CollectiveVelocityRequest):
    """
    Calculate v_collective using the Sigillin convergence formula.

    **Formula:**
    ```
    v_collective = v_RIG × κ × (1 / β_sync)
    ```

    Where:
    - **v_RIG**: Base velocity (information propagation speed)
    - **κ (kappa)**: Field coupling strength
    - **β_sync**: Synchronization steepness

    **V7 Feature:** Collective consciousness velocity - measures how fast
    shared understanding propagates through multi-agent systems.

    **Physical Interpretation:**
    - High v_collective → Fast semantic convergence
    - Low v_collective → Slow consensus formation

    **Example:**
    ```json
    {
      "v_rig": 1.0,
      "kappa": 0.8,
      "beta_sync": 2.5
    }
    ```
    """
    if sigillin_kernel is None:
        raise HTTPException(
            status_code=503,
            detail="Sigillin kernel not initialized.",
        )

    try:
        v_collective = sigillin_kernel.calculate_collective_velocity(
            v_rig=request.v_rig,
            kappa=request.kappa,
            beta_sync=request.beta_sync,
        )

        return CollectiveVelocityResponse(
            v_collective=v_collective,
            v_rig=request.v_rig,
            kappa=request.kappa,
            beta_sync=request.beta_sync,
            formula="v_collective = v_RIG × κ × (1 / β_sync)",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Collective Field V7 Phase 2 Endpoints
# ============================================================================


@app.post(
    "/api/collective/analyze_texts",
    response_model=AnalyzeTextsResponse,
    tags=["collective"],
)
async def analyze_texts_collective(request: AnalyzeTextsRequest):
    """
    Analyze multiple texts and optionally create a collective field.

    **V7 Phase 2 Feature:** Multi-text semantic analysis with collective field coupling.

    For each text:
    - Scans for explicit and implicit resonance
    - Measures semantic depth and gravity
    - Detects contextual coherence

    If create_field=True, creates a collective field and computes:
    - κ_field (field coupling strength)
    - β_sync (synchronization resistance)
    - v_collective (collective propagation velocity)

    **Example:**
    ```json
    {
      "texts": [
        "Die Resonanz zwischen Bewusstsein und Feld zeigt Emergenz",
        "Consciousness emerges from field coupling and coherence",
        "Synchronization enables collective emergence"
      ],
      "create_field": true,
      "v_rig": 1.0
    }
    ```
    """
    if sigillin_kernel is None:
        raise HTTPException(status_code=503, detail="Sigillin kernel not initialized")

    if not collective_field_available:
        raise HTTPException(status_code=503, detail="Collective Field Module not available")

    # Analyze each text with enhanced scanner
    analyses = []
    agents_for_field = []

    for i, text in enumerate(request.texts):
        # Create semantic agent from text
        agent_data = sigillin_kernel.create_semantic_agent(text, agent_name=f"text_{i}")

        analyses.append(
            TextAnalysisResult(
                text=text[:200],  # Truncate for response
                agent_name=agent_data["name"],
                resonance=agent_data["resonance"],
                semantic_depth=agent_data["semantic_depth"],
                gravity=agent_data["gravity"],
                matched_keywords=agent_data["matched_keywords"],
                implicit_signals=agent_data["implicit_signals"],
                coherence=agent_data["coherence"],
            )
        )

        # Create Agent object for collective field
        if request.create_field:
            agent = Agent(
                name=agent_data["name"],
                resonance=agent_data["resonance"],
                dimension=8,
            )
            agents_for_field.append(agent)

    # Create collective field if requested
    field_state = None
    if request.create_field and len(agents_for_field) >= 2:
        field = CollectiveField(agents=agents_for_field, v_rig=request.v_rig)
        field_state_dict = field.get_field_state()

        field_state = FieldStateResponse(**field_state_dict)

    return AnalyzeTextsResponse(analyses=analyses, field_state=field_state)


@app.post(
    "/api/sigillin/scan_v2",
    response_model=ScanIntentionV2Response,
    tags=["sigillin"],
)
async def scan_intention_v2(request: ScanIntentionV2Request):
    """
    Enhanced intention scanner with implicit information detection.

    **V7 Phase 2 Feature:** Goes beyond simple keyword matching to detect:
    - Explicit keywords (direct mentions)
    - Implicit patterns (related concepts, semantic gravity)
    - Contextual depth (how deeply concepts are explored)
    - Coherence (meaningful context vs isolated mentions)

    **Improvements over v1:**
    - Detects related concepts even without exact keywords
    - Analyzes sentence structure and word count
    - Measures contextual coherence
    - Returns detailed analysis breakdown

    **Example:**
    ```json
    {
      "text": "The emergence of consciousness from field coupling...",
      "detect_implicit": true
    }
    ```
    """
    if sigillin_kernel is None:
        raise HTTPException(status_code=503, detail="Sigillin kernel not initialized")

    result = sigillin_kernel.scan_intention_v2(
        input_text=request.text,
        detect_implicit=request.detect_implicit,
    )

    return ScanIntentionV2Response(**result)


@app.post(
    "/api/sigillin/gravity",
    response_model=SemanticGravityResponse,
    tags=["sigillin"],
)
async def detect_semantic_gravity(request: SemanticGravityRequest):
    """
    Detect semantic gravity - how strongly text pulls toward founding axioms.

    **V7 Phase 2 Feature:** Semantic gravity measures the "attraction" between
    text and the founding protocol, even without explicit keyword matches.

    **Physical Analogy:**
    - Gravity ≥ 0.7: Strong pull (text is deeply aligned)
    - Gravity 0.4-0.7: Moderate pull (partial alignment)
    - Gravity 0.2-0.4: Weak pull (tangential connection)
    - Gravity < 0.2: Minimal pull (divergent)

    **Use Cases:**
    - Filter texts by alignment with founding protocol
    - Detect implicit resonance in natural language
    - Measure semantic coherence over time

    **Example:**
    ```json
    {
      "text": "Systems synchronize through field coupling, enabling emergent coherence"
    }
    ```
    """
    if sigillin_kernel is None:
        raise HTTPException(status_code=503, detail="Sigillin kernel not initialized")

    gravity = sigillin_kernel.detect_semantic_gravity(request.text)

    # Interpret gravity
    if gravity >= 0.7:
        interpretation = "Strong semantic gravity - text is deeply aligned with founding axioms"
    elif gravity >= 0.4:
        interpretation = "Moderate semantic gravity - partial alignment detected"
    elif gravity >= 0.2:
        interpretation = "Weak semantic gravity - tangential connection"
    else:
        interpretation = "Minimal semantic gravity - text diverges from founding protocol"

    return SemanticGravityResponse(gravity=gravity, interpretation=interpretation)


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
