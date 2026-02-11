# Grok-AFET Integration Specification v1.0

## Overview

The Grok-AFET bridge provides real-time sigma_Phi monitoring for Grok's transformer
architecture. It attaches to individual layers, tracks activation statistics, and
enforces AFET safety thresholds during inference.

## Architecture

```
integration/grok_bridge/
├── __init__.py
├── layer_monitor.py      # Per-layer sigma_Phi tracking
├── safety_hooks.py       # Auto-shutdown protocol
├── metrics_collector.py  # Real-time dashboarding
└── tests/
    ├── __init__.py
    ├── test_layer_monitor.py
    └── test_safety_hooks.py
```

## Core Components

### GrokLayerMonitor

Per-layer sigma_Phi tracker. Attaches forward hooks to `torch.nn.Module` layers
and records activation statistics on every forward pass.

**Key Methods:**

| Method | Description |
|--------|------------|
| `attach_to_layer(layer_name, model)` | Attach a forward hook to a named layer |
| `record_reading(layer_name, activations)` | Manually record a reading (numpy path) |
| `get_readings(layer_name=None)` | Return recorded readings, optionally filtered |
| `get_latest(layer_name)` | Most recent reading for a layer |
| `get_sigma_phi_series(layer_name)` | Time series of sigma_Phi values |
| `get_drift_report(layer_name)` | Drift statistics for a layer |

### GrokSafetyHooks

Automatic safety enforcement. Evaluates sigma_Phi readings against AFET thresholds
and generates alerts with optional callbacks.

**Key Methods:**

| Method | Description |
|--------|------------|
| `check_safety_thresholds(reading)` | Check a reading against thresholds |
| `generate_alert(severity, message)` | Create a manual alert |
| `classify(sigma_phi)` | Classify into STABLE/WARNING/CRITICAL |
| `set_warning_callback(fn)` | Register warning handler |
| `set_critical_callback(fn)` | Register critical handler |

### GrokMetricsCollector

Aggregates readings and alerts into dashboard payloads with snapshot history.

**Key Methods:**

| Method | Description |
|--------|------------|
| `take_snapshot()` | Capture current state of all layers |
| `get_dashboard()` | Generate dashboard payload |
| `export_json(path)` | Export history to JSON |

## Safety Tiers

| Level | sigma_Phi Range | Action |
|-------|----------------|--------|
| STABLE | >= 0.0625 | Normal operation |
| WARNING | 0.055 - 0.0625 | Log + optional throttle |
| CRITICAL | < 0.055 | Emergency shutdown requested |

## Integration Steps

```python
from integration.grok_bridge.layer_monitor import GrokLayerMonitor
from integration.grok_bridge.safety_hooks import GrokSafetyHooks
from integration.grok_bridge.metrics_collector import GrokMetricsCollector

# 1. Create monitor and safety hooks
monitor = GrokLayerMonitor()
safety = GrokSafetyHooks()

# 2. Attach to model layers
monitor.attach_to_layer("encoder.layer.0", model)
monitor.attach_to_layer("encoder.layer.5", model)

# 3. Run inference — hooks record automatically
outputs = model(inputs)

# 4. Check safety
for layer in monitor.attached_layers:
    reading = monitor.get_latest(layer)
    alert = safety.check_safety_thresholds(reading)
    if alert and alert.should_shutdown:
        print(f"EMERGENCY: {alert.message}")

# 5. Collect metrics
collector = GrokMetricsCollector(monitor=monitor, safety=safety)
dashboard = collector.take_snapshot()
```

## Constants

- sigma_Phi threshold (stable): 0.0625 (= 1/16, AFET metastability boundary)
- Critical threshold: 0.055
- Beta critical: 37.6
- Resonance frequency: 13.5 MHz
