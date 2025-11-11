# 🎨 UTAC Tooltip System API

**Version:** 2.0.0
**Feature:** v2-feat-ext-001
**Status:** ✅ Implemented

---

## 📋 Overview

The UTAC Tooltip System provides rich, interactive metadata for visualizations. It combines:

- **UTAC Parameters:** β, Θ (with confidence intervals)
- **Statistical Metrics:** R², ΔAIC, best null model
- **CREP Scores:** Coherence, Resilience, Empathy, Propagation
- **Field Type Classification:** 5 categories based on β-ranges
- **Narrative Threads:** Formal, empirical, poetic context

---

## 🔌 API Endpoints

### GET `/api/tooltip/{preset_id}`

Get rich tooltip data for a specific preset.

**Parameters:**
- `preset_id` (path, string, required): Preset identifier (e.g., `llm_resonance`)

**Response:** `TooltipData` object

**Example:**
```bash
curl http://localhost:8000/api/tooltip/llm_resonance
```

**Response:**
```json
{
  "preset_id": "llm_resonance",
  "label": "LLM Emergence",
  "domain": "AI/Neural",
  "beta": 3.47,
  "beta_ci": [3.12, 3.82],
  "theta": 45.2,
  "theta_ci": [42.8, 47.6],
  "r_squared": 0.987,
  "delta_aic": 156.3,
  "delta_r2": 0.423,
  "best_null_model": "exponential",
  "crep": {
    "coherence": 0.987,
    "resilience": 0.675,
    "empathy": 1.0,
    "propagation": 0.421
  },
  "field_type": {
    "type": "high_dimensional",
    "description": "High-Dimensional: Complex state spaces (AI, neural)",
    "beta_range": [2.5, 4.0],
    "color": "#457b9d"
  },
  "impedance_closed": 0.85,
  "impedance_open": 1.35,
  "impedance_mean": 1.10,
  "formal_thread": "LLMs exhibit sharp capability emergence...",
  "empirical_thread": "GPT-3 (175B params) shows...",
  "poetic_thread": "The model whispers at 44 billion parameters..."
}
```

---

### GET `/api/tooltip`

Get tooltip data for all available presets.

**Parameters:** None

**Response:** Array of `TooltipData` objects

**Example:**
```bash
curl http://localhost:8000/api/tooltip
```

**Response:**
```json
[
  { "preset_id": "llm_resonance", "label": "LLM Emergence", ... },
  { "preset_id": "amoc_collapse", "label": "AMOC Collapse", ... },
  { "preset_id": "urban_heat", "label": "Urban Heat Island", ... },
  ...
]
```

---

## 📊 Data Models

### TooltipData

Complete tooltip metadata structure.

```typescript
interface TooltipData {
  // Identification
  preset_id: string;
  label: string;
  domain: string;

  // UTAC Parameters
  beta: number | null;
  beta_ci?: [number, number] | null;
  theta: number | null;
  theta_ci?: [number, number] | null;

  // Statistical Metrics
  r_squared: number | null;
  delta_aic: number | null;
  delta_r2: number | null;
  best_null_model: string | null;

  // CREP Scores
  crep?: CREPScores;

  // Field Type
  field_type?: FieldTypeInfo;

  // Impedance (ζ)
  impedance_closed: number;
  impedance_open: number;
  impedance_mean: number;

  // Narrative
  formal_thread?: string;
  empirical_thread?: string;
  poetic_thread?: string;
}
```

### CREPScores

Quality metrics for UTAC systems (0-1 scale).

```typescript
interface CREPScores {
  coherence: number;     // Internal consistency (R²-based)
  resilience: number;    // Recovery capacity (impedance-based)
  empathy: number;       // Cross-domain resonance (ΔAIC-based)
  propagation: number;   // Signal transmission (β-based)
}
```

### FieldTypeInfo

Field type classification based on β-parameter.

```typescript
interface FieldTypeInfo {
  type: 'weakly_coupled' | 'high_dimensional' | 'strongly_coupled' |
        'physically_constrained' | 'meta_adaptive';
  description: string;
  beta_range: [number, number];
  color: string;  // Hex color code
}
```

**Field Type Ranges:**

| Type | β Range | Description | Color |
|------|---------|-------------|-------|
| Weakly Coupled | 0 - 2.5 | Gradual transitions, low coupling | #a8dadc |
| High-Dimensional | 2.5 - 4.0 | Complex state spaces (AI, neural) | #457b9d |
| Strongly Coupled | 4.0 - 5.5 | Resonant systems (climate, ecology) | #1d3557 |
| Physically Constrained | 5.5 - 10.0 | Hard constraints (astrophysics) | #e63946 |
| Meta-Adaptive | > 10.0 | Extreme nonlinearity (urban systems) | #f77f00 |

---

## 🎯 Use Cases

### 1. Interactive Plots (Plotly/D3.js)

```javascript
// Fetch all tooltip data
fetch('http://localhost:8000/api/tooltip')
  .then(res => res.json())
  .then(data => {
    // Use in Plotly hovertemplate
    const trace = {
      x: data.map(d => d.beta),
      y: data.map(d => d.r_squared),
      hovertemplate: '<b>%{text}</b><br>' +
                    'β: %{x:.2f}<br>' +
                    'R²: %{y:.3f}<br>' +
                    'ΔAIC: %{customdata[0]:.1f}<br>' +
                    'Field Type: %{customdata[1]}<br>' +
                    '<extra></extra>',
      text: data.map(d => d.label),
      customdata: data.map(d => [d.delta_aic, d.field_type.type])
    };
    Plotly.newPlot('plot', [trace]);
  });
```

### 2. React Component (Recharts)

```tsx
import { UTACTooltip } from './components/UTACTooltip';
import { buildTooltipDataMap } from './utils/tooltipDataBuilder';

const MyChart = () => {
  const tooltipData = useMemo(() => buildTooltipDataMap(presets), [presets]);

  return (
    <LineChart>
      <Tooltip
        content={<UTACTooltip tooltipData={tooltipData} />}
      />
    </LineChart>
  );
};
```

### 3. External Applications

```python
import requests

# Get all tooltip data
response = requests.get('http://localhost:8000/api/tooltip')
data = response.json()

# Filter by field type
high_dim = [d for d in data if d['field_type']['type'] == 'high_dimensional']

# Sort by β
sorted_by_beta = sorted(data, key=lambda d: d['beta'] or 0, reverse=True)
```

---

## 🚀 Quick Start

### 1. Start API Server

```bash
cd api
uvicorn server:app --reload --port 8000
```

### 2. Open Demo Page

```bash
# Open in browser
open examples/tooltip_demo.html

# Or use Python HTTP server
python3 -m http.server 8080
# Then visit: http://localhost:8080/examples/tooltip_demo.html
```

### 3. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all tooltip data
curl http://localhost:8000/api/tooltip | jq

# Get specific preset
curl http://localhost:8000/api/tooltip/llm_resonance | jq
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test all presets
curl -s http://localhost:8000/api/tooltip | \
  jq -r '.[] | "\(.preset_id): β=\(.beta), R²=\(.r_squared)"'

# Test specific preset
curl -s http://localhost:8000/api/tooltip/urban_heat | \
  jq '.field_type.type'
# Expected: "meta_adaptive"
```

### Automated Tests

```bash
# Run test suite
pytest tests/test_tooltip_api.py -v

# Expected: 8 tests passing
```

---

## 📦 Integration

### Frontend (React/TypeScript)

```bash
# Types already defined in simulator/src/types.ts
# Utilities in simulator/src/utils/

npm run build  # Build simulator with tooltip support
```

### Backend (FastAPI)

```python
# Endpoints already defined in api/server.py
# Models: TooltipData, CREPScores, FieldTypeInfo

uvicorn api.server:app --reload
```

### Demo Page (HTML/Plotly)

```html
<!-- Standalone demo at examples/tooltip_demo.html -->
<!-- Uses Plotly.js for interactive visualizations -->
```

---

## 🔧 Configuration

### Custom Field Type Ranges

Edit `api/server.py`, function `classify_field_type()`:

```python
def classify_field_type(beta: Optional[float]) -> FieldTypeInfo:
    # Modify thresholds here
    if beta < 2.5:
        return FieldTypeInfo(type="weakly_coupled", ...)
    # ...
```

### Custom CREP Computation

Edit `api/server.py`, function `compute_crep_scores()`:

```python
def compute_crep_scores(r2, delta_aic, impedance_mean, beta):
    # Modify CREP formulas here
    coherence = min(1.0, r2)
    resilience = min(1.0, impedance_mean / 2.0)
    # ...
```

---

## 🐛 Troubleshooting

### Error: "Preset not found"

**Cause:** Preset JSON doesn't exist in `simulator/presets/`

**Solution:**
```bash
ls simulator/presets/*.json  # List available presets
curl http://localhost:8000/api/tooltip  # See all available IDs
```

### Error: "Cannot connect to API"

**Cause:** API server not running

**Solution:**
```bash
cd api
uvicorn server:app --reload
```

### Error: "CORS policy"

**Cause:** Demo HTML opened as `file://` instead of `http://`

**Solution:**
```bash
# Use a local HTTP server
python3 -m http.server 8080
# Open: http://localhost:8080/examples/tooltip_demo.html
```

---

## 📚 References

- **UTAC Theory:** `docs/utac_meta_theory.md`
- **Field Types:** `sonification/README.md`
- **CREP Scores:** `seed/bedeutungssigillin/*/crep_*.md`
- **API Spec:** `api/openapi.yaml`

---

## 📝 Changelog

### v2.0.0 (2025-11-11) - v2-feat-ext-001

- ✅ Added `/api/tooltip/{preset_id}` endpoint
- ✅ Added `/api/tooltip` endpoint (all presets)
- ✅ Implemented `TooltipData`, `CREPScores`, `FieldTypeInfo` models
- ✅ Created `UTACTooltip` React component (Recharts integration)
- ✅ Created demo HTML page (Plotly.js)
- ✅ Field type classifier (5 categories)
- ✅ CREP score computation
- ✅ TypeScript type definitions
- ✅ Full documentation

---

**Maintained by:** Claude Code + Johann Römer
**Status:** ✅ Complete & Production-Ready
**Feature ID:** v2-feat-ext-001

*"Tooltips jetzt mit β, Θ, R², ΔAIC, CREP & Field Types - die Laternen sprechen!"* 🎨🌀
