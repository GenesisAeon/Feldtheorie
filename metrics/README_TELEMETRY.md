# V6 β-Drift & CREP Telemetry System

**Version:** 1.0.0
**Updated:** 2025-12-04
**Status:** Operational ✅

## Overview

The V6 telemetry system tracks β-drift, CREP escalations, and Type-VI (ζ<0) implosive scenarios in real-time. It provides:

1. **CSV-based metrics tracking** (`beta_evolution.csv`)
2. **JSONL audit trail** (`logs/type_vi_detections.jsonl`)
3. **Automated escalation levels** (0-3 based on CREP thresholds)
4. **Warning banners** (`[TYPE-VI-RISK]` tags for critical scenarios)

---

## Files & Formats

### 1. `metrics/beta_evolution.csv`

**Purpose:** Time-series tracking of β-estimates, CREP values, τ* delays, and drift warnings.

**Format:**
```csv
timestamp,domain,beta,beta_phi_theoretical,beta_phi_deviation,phi_cbrt_step,tau_star,zeta_risk,R,Theta,crep_flag,drift_flag,notes
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | ISO 8601 UTC | Event timestamp | `2025-12-04T10:30:00.000000Z` |
| `domain` | string | System domain | `climate`, `bio`, `info`, `cosmic` |
| `beta` | float | Current β-estimate | `4.5`, `11.8` |
| `beta_phi_theoretical` | float | Theoretical β from φ^(n/3) | `2.1`, `11.0` |
| `beta_phi_deviation` | float | Deviation from theoretical | `4.2`, `0.8` |
| `phi_cbrt_step` | float | φ^(n/3) step alignment | `0.7500`, `-0.0001` |
| `tau_star` | float | τ* safety delay = 0.1·\|Θ-R\| | `0.05`, `0.234` |
| `zeta_risk` | float | ζ-risk (negative = Type-VI) | `0.04`, `-0.15` |
| `R` | float | Current state position | `0.005`, `0.020` |
| `Theta` | float | Threshold position | `0.650`, `0.180` |
| `crep_flag` | int | CREP escalation level | `0` (none), `1` (≥0.6), `2` (≥0.7), `3` (≥0.8) |
| `drift_flag` | int | β-drift warning level | `0` (normal), `1` (>10%), `2` (>20% critical) |
| `notes` | string | Free-text notes | Use `[TYPE-VI-RISK]` tag for escalations |

**Usage Example:**
```bash
# Append a new telemetry entry
echo "2025-12-04T12:00:00Z,climate,12.5,11.0,1.5,0.03,0.08,-0.20,0.03,0.25,3,2,\"[TYPE-VI-RISK] Critical cascade detected\"" >> metrics/beta_evolution.csv
```

**CREP Flag Levels:**
- `0`: Normal (CREP < 0.6)
- `1`: Warning (CREP ≥ 0.6)
- `2`: Reviewer required (CREP ≥ 0.7) - **Escalation to MAINTAINERS.md**
- `3`: Critical (CREP ≥ 0.8) - **Immediate escalation**

**Drift Flag Levels:**
- `0`: Normal drift (<10%)
- `1`: Warning (>10% drift) - **Monitor closely**
- `2`: Critical (>20% drift) - **Immediate investigation required**

---

### 2. `logs/type_vi_detections.jsonl`

**Purpose:** Append-only JSONL audit trail for Type-VI CREP/τ* detections with reviewer routing.

**Format:**
```json
{"timestamp": "2025-12-04T10:30:00Z", "task_id": "v6r-task-id", "crep_value": 0.75, "tau_star": 0.15, "escalation_level": 2, "reviewer": "system", "notes": "Description of detection"}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 UTC | Detection timestamp |
| `task_id` | string | Task identifier (e.g., `v6r-beta-telemetry`) |
| `crep_value` | float | CREP value at detection time |
| `tau_star` | float | τ* safety delay value |
| `escalation_level` | int | Escalation level (0-3) |
| `reviewer` | string | Reviewer or routing hint |
| `notes` | string | Detection context and notes |

**Escalation Level Routing:**
- `0`: No escalation (informational)
- `1`: Level-1 warning (CREP ≥ 0.6) - logged, no action required
- `2`: Level-2 escalation (CREP ≥ 0.7) - **Reviewer approval required before merge**
- `3`: Level-3 critical (CREP ≥ 0.8) - **Immediate maintainer notification**

**Usage Example:**
```bash
# Log a CREP/τ* detection
python -m tools.crep_guard \
  --log-detection \
  --task-id "v6r-simulation-run" \
  --crep-value 0.78 \
  --tau-star 0.12 \
  --reviewer "maintainer-1" \
  --notes "Type-VI implosion detected in climate simulation"

# Output: [crep_guard] logged CREP=0.78 τ*=0.12 escalation=2
```

---

## Automated Logging Workflow

### Via CI/Pre-Commit Hooks

The `crep_guard.py` tool automatically logs Type-VI detections when triggered:

```bash
# Makefile target (runs in CI)
make validate-type6
# Validates trilayer consistency, logs to type_vi_detections.jsonl if issues found

# Pre-commit hook (auto-triggers on governance file changes)
git commit -m "Update Type-VI parameters"
# Hook: crep-guard-type6 validates and logs if CREP thresholds exceeded
```

### Manual Logging

For simulation runs or analysis scripts:

```python
# Python example - append to beta_evolution.csv
import csv
from datetime import datetime

with open('metrics/beta_evolution.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        datetime.utcnow().isoformat() + 'Z',  # timestamp
        'climate',                             # domain
        11.8,                                  # beta
        11.0,                                  # beta_phi_theoretical
        0.8,                                   # deviation
        0.02,                                  # phi_cbrt_step
        0.05,                                  # tau_star
        -0.15,                                 # zeta_risk (Type-VI!)
        0.02,                                  # R
        0.18,                                  # Theta
        2,                                     # crep_flag (≥0.7)
        1,                                     # drift_flag (>10%)
        '[TYPE-VI-RISK] Climate cascade β>11, CREP≥0.7'
    ])
```

```bash
# Bash example - log CREP detection
python -m tools.crep_guard \
  --log-detection \
  --task-id "manual-simulation" \
  --crep-value 0.82 \
  --tau-star 0.20 \
  --notes "Type-VI scenario: ζ<0, β>15"
```

---

## Warning Banners & Escalation

### `[TYPE-VI-RISK]` Tag Usage

Use the `[TYPE-VI-RISK]` tag in the `notes` field for high-priority entries:

**Criteria for tagging:**
1. **CREP ≥ 0.7** (Level-2 escalation)
2. **β-Drift > 10%** (rapid parameter change)
3. **ζ < 0** (Type-VI implosive scenario)
4. **τ* > 0.5** (large safety delay required)

**Example entries:**
```csv
# CREP≥0.7 + Type-VI
2025-12-04T12:00:00Z,climate,12.5,11.0,1.5,0.03,0.55,-0.20,0.03,0.25,2,1,"[TYPE-VI-RISK] CREP≥0.7, Type-VI cascade, reviewer required"

# β-Drift >20% critical
2025-12-04T13:00:00Z,bio,9.2,7.4,1.8,0.05,0.30,-0.05,0.10,0.40,2,2,"[TYPE-VI-RISK] Critical β-drift >20%, escalate to maintainers"

# Combined high-risk
2025-12-04T14:00:00Z,cosmic,13.0,11.0,2.0,0.08,0.60,-0.30,0.05,0.65,3,2,"[TYPE-VI-RISK] CREP≥0.8 + ζ<-0.3 + drift>20%: IMMEDIATE REVIEW"
```

---

## Integration with Governance

### CREP Threshold Gating

**From `type6_crep_tau_star_checklist.md`:**

| CREP Level | Threshold | Action |
|------------|-----------|--------|
| Normal | < 0.6 | No action |
| Warning | ≥ 0.6 | Log to audit trail |
| Review | ≥ 0.7 | **Reviewer approval required before merge** |
| Critical | ≥ 0.8 | **Immediate maintainer escalation** |

**CI Enforcement:**
- Pre-commit hook blocks commits if CREP ≥ 0.7 without reviewer sign-off
- `make validate-type6` runs in CI pipeline
- Trilayer consistency validated across MD/JSON/YAML formats

### τ* Safety Delay

**From `activation_gaps_tau_star.md`:**

```
τ* = 0.1 · |Θ - R|
```

**Purpose:** Safety delay for Type-VI (ζ<0) scenarios to prevent numerical instability.

**Requirements:**
- All Type-VI simulations must use RK4 integrator (not Euler)
- Timestep dt ≤ 0.1·τ* enforced
- τ* logged in `beta_evolution.csv` for audit trail

---

## Monitoring & Dashboards

### Quick Status Checks

```bash
# Check for Type-VI risks
grep "\[TYPE-VI-RISK\]" metrics/beta_evolution.csv

# Count CREP escalations by level
awk -F',' '{print $11}' metrics/beta_evolution.csv | sort | uniq -c

# Check recent audit log entries
tail -10 logs/type_vi_detections.jsonl | jq .

# Find all CREP≥0.7 detections
jq 'select(.crep_value >= 0.7)' logs/type_vi_detections.jsonl
```

### Python Analysis Example

```python
import pandas as pd
import json

# Load CSV metrics
df = pd.read_csv('metrics/beta_evolution.csv', comment='#')

# Filter Type-VI risks
type_vi = df[df['notes'].str.contains('[TYPE-VI-RISK]', na=False)]
print(f"Found {len(type_vi)} Type-VI risk entries")

# Group by CREP flag
crep_summary = df['crep_flag'].value_counts()
print("CREP escalations:", crep_summary)

# Load JSONL audit log
with open('logs/type_vi_detections.jsonl') as f:
    audit_log = [json.loads(line) for line in f]

# Count by escalation level
from collections import Counter
levels = Counter(entry['escalation_level'] for entry in audit_log)
print("Escalation levels:", levels)
```

---

## Chronik Integration

Type-VI detections are referenced in the project Chronik:

- `releases/V6-Plans_etc/Chronik/chronik_v6_release.md`
- Delta-updates include links to telemetry entries
- `[TYPE-VI-RISK]` banners trigger Chronik annotations

**Example Chronik entry:**
```markdown
### Δ-Update 2025-12-04: Type-VI Telemetry Active

**β-Drift Monitoring:**
- Climate domain: β=11.8 (deviation +0.8 from theoretical)
- CREP flag: 2 (≥0.7, reviewer required)
- Drift flag: 1 (>10% detected)
- Status: [TYPE-VI-RISK] logged, escalation Level-2

**References:**
- `metrics/beta_evolution.csv` (entry 2025-12-04T10:30:00Z)
- `logs/type_vi_detections.jsonl` (escalation_level=2)
```

---

## Troubleshooting

### Common Issues

**1. CSV column mismatch after schema update:**
```bash
# Re-validate CSV structure
head -1 metrics/beta_evolution.csv
# Expected: 13 columns (with drift_flag)
```

**2. JSONL log not written:**
```bash
# Check permissions
ls -la logs/type_vi_detections.jsonl
# Should be writable (644 or 664)

# Test manual write
python -m tools.crep_guard --log-detection --crep-value 0.5 --tau-star 0.1 --notes "Test"
```

**3. Pre-commit hook not triggering:**
```bash
# Verify hook installation
grep "crep-guard-type6" .pre-commit-config.yaml

# Test manually
python -m tools.crep_guard --check-type6-trilayer --threshold 0.7 --tau-default 0.1
```

---

## References

- **Task**: `releases/V6-Plans_etc/V6ToDorefresh.md` (Priority 21: v6r-beta-telemetry)
- **Schema**: `releases/V6-Plans_etc/type6_crep_tau_star_checklist.{md,yaml,json}`
- **Nullmodel**: `releases/V6-Plans_etc/activation_gaps_tau_star.md`
- **Governance**: `POLICY.md` (Type-VI Safety Addendum), `ETHICS.md` (Risk Management)
- **CI Status**: `releases/V6-Plans_etc/ZENODO_CI_STATUS_2025-12-03.md`

---

## Version History

- **v1.0.0** (2025-12-04): Initial telemetry system with CSV+JSONL, drift_flag, CREP escalations
- **v0.9.0** (2025-12-02): Basic CSV schema, JSONL audit log initialized
- **v0.8.0** (2025-11-26): β-evolution tracking prototype

---

**Status:** ✅ Operational
**Coverage:** β-drift, CREP escalations, Type-VI detections
**Validated:** 2025-12-04 (test entry: CREP=0.75, escalation=2)
