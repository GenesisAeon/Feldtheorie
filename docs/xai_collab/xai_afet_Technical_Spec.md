# Technical Specification — AFET × xAI Pilot

## 1) Scaling AFET Validation Pilot

### Goal
Run broad sweeps over `beta_values × sigma_phi_values × datasets` and persist comparable metrics.

### API

```python
run_scaling_validation(
    datasets: list[Mapping[str, object]],
    beta_values: list[float],
    sigma_phi_values: list[float],
    output_path: str | Path | None = None,
    max_workers: int = 1,
    evaluator: Callable | None = None,
) -> list[dict[str, object]]
```

### Notes
- Naive baseline: deterministic nested-grid evaluation.
- Parallel mode: thread-pool for easy migration to cluster orchestration.
- Output format: JSON with summary and full run records.

## 2) AFETSafetyMonitor

### Goal
Provide a strict guardrail around metastability drift during training/inference.

### API

```python
AFETSafetyMonitor(
    sigma_phi_threshold: float = 0.0625,
    critical_threshold: float = 0.055,
)

monitor_step(metrics: Mapping[str, float]) -> SafetyDecision
monitor_aeon_shell(shell: Any) -> SafetyDecision
```

### Decision Logic
- `sigma_phi < 0.055` → critical, raise runtime error (shutdown request).
- `0.055 <= sigma_phi < 0.0625` → warning.
- `sigma_phi >= 0.0625` → stable.

## 3) HfO₂ Neuromorphic Interface

### Goal
Freeze a partner-facing contract for co-design and simulator alignment.

### Contract Sections
- Inputs: pulse sequence, sensor feedback, calibration profile.
- Outputs: latent state embedding, σ_Φ estimate, diagnostics.
- Constraints: latency, thermal window, critical σ_Φ limit.

## 4) Climate Drift Dashboard Prototype

### Goal
Ingest climate telemetry, compute rolling σ_Φ proxy, and flag warning/critical events.

### API

```python
load_climate_timeseries(path, value_column)
compute_sigma_phi_series(values, window=12)
build_dashboard_snapshot(frame, sigma_phi_series, critical_threshold=0.055)
```

### Assumptions
- Input has `timestamp` and one numeric signal column.
- Signal is pre-normalized or on a stable scale.
- Sampling cadence is uniform after ingestion.
