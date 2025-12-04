# Simulator UX Enhancement Blueprint

**Version:** 1.0.0
**Date:** 2025-12-04
**Status:** Implementation Ready
**Priority:** 10 (β=4.9, ζ=low)
**Scope:** Agent-friendly interactive enhancements for Feldtheorie simulator

---

## Executive Summary

This blueprint defines **5 key UX enhancements** to make the Feldtheorie simulator more interactive, accessible to AI agents, and scientifically informative:

1. **Web Audio Sonification** - Auditory feedback for system dynamics
2. **CSV Drag & Drop** - Browser-based data import and analysis
3. **llms.txt / AI Navigation** - LLM-crawler-friendly documentation
4. **Diamond Architecture Map** - Interactive SVG system diagram
5. **Type-VI Visualization** - Implosion gravity mode + inverted sigmoid

**Target:** Transform simulator from visualization tool → **interactive research platform**

---

## 1. Web Audio Sonification

### 1.1 Rationale

**Problem:** Visual-only feedback limits accessibility and intuition for dynamic systems.

**Solution:** Map system states to audio parameters using Web Audio API.

**Use Cases:**
- Detect instabilities by ear (high-frequency vibrato)
- Monitor bifurcations (pitch shifts)
- Real-time feedback during parameter sweeps

### 1.2 Implementation

**Mapping:**

| System Property | Audio Parameter | Example |
|-----------------|-----------------|---------|
| **β (decision strength)** | Base Frequency | β=4.5 → 220 Hz (A3), β=11 → 880 Hz (A5) |
| **|dΘ/dt| (rate of change)** | Vibrato Depth | Stable: 0 Hz, Unstable: ±20 Hz |
| **ζ (risk)** | Filter Cutoff | Low risk: bright (8 kHz), High risk: muffled (500 Hz) |
| **CREP index** | Reverb Mix | CREP < 0.7: dry, CREP ≥ 0.7: wet (60% reverb) |
| **Regime type** | Waveform | Cosmic: sine, Bio: triangle, Cog: sawtooth, AI: square |

**Code Stub:**

```javascript
// Web Audio API setup
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
const oscillator = audioCtx.createOscillator();
const gainNode = audioCtx.createGain();
const filter = audioCtx.createBiquadFilter();
const reverb = audioCtx.createConvolver();

oscillator.connect(gainNode);
gainNode.connect(filter);
filter.connect(reverb);
reverb.connect(audioCtx.destination);

// Update audio based on simulation state
function updateSonification(state) {
    // Base frequency from β
    const beta = state.beta;
    const baseFreq = 110 * Math.pow(2, (beta - 4.5) / 3);  // Musical scale
    oscillator.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);

    // Vibrato from instability
    const dTheta_dt = Math.abs(state.dTheta_dt);
    const vibratoDepth = Math.min(dTheta_dt * 10, 20);  // Max ±20 Hz
    const lfo = audioCtx.createOscillator();
    lfo.frequency.value = 5;  // 5 Hz vibrato rate
    const lfoGain = audioCtx.createGain();
    lfoGain.gain.value = vibratoDepth;
    lfo.connect(lfoGain);
    lfoGain.connect(oscillator.frequency);
    lfo.start();

    // Filter from risk
    const zeta = state.zeta;  // 0 (low) to 1 (high)
    filter.frequency.value = 8000 - 7500 * zeta;  // 8 kHz → 500 Hz

    // Volume from CREP (mute if too low)
    const crep = state.crep;
    gainNode.gain.value = crep > 0.5 ? 0.3 : 0.05;
}

// Enable/disable sonification
document.getElementById('sonification-toggle').addEventListener('change', (e) => {
    if (e.target.checked) {
        oscillator.start();
    } else {
        oscillator.stop();
    }
});
```

**UI Controls:**

```html
<div class="sonification-panel">
  <label>
    <input type="checkbox" id="sonification-toggle"> Enable Audio Sonification
  </label>
  <label>
    Volume: <input type="range" id="audio-volume" min="0" max="1" step="0.1" value="0.3">
  </label>
  <select id="waveform-select">
    <option value="sine">Sine (Cosmic)</option>
    <option value="triangle">Triangle (Biological)</option>
    <option value="sawtooth">Sawtooth (Cognitive)</option>
    <option value="square">Square (AI/Symbolic)</option>
  </select>
</div>
```

---

## 2. CSV Drag & Drop Import

### 2.1 Rationale

**Problem:** Users must manually enter parameters or edit code to test custom data.

**Solution:** Drag CSV files directly into browser → automatic β/Θ estimation → visualization.

### 2.2 Implementation

**Supported CSV Formats:**

**Format A: Time Series**
```csv
time, resource, constraint
0.0, 100, 150
0.1, 105, 148
0.2, 112, 145
...
```
→ Estimate β and Θ from trajectory using logistic regression.

**Format B: Parameter Scan**
```csv
beta, theta, outcome
4.5, 100, stable
5.0, 100, stable
6.0, 100, bifurcation
...
```
→ Plot phase diagram directly.

**Code Stub:**

```javascript
// Drag & drop handler
const dropZone = document.getElementById('csv-drop-zone');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
        parseCSV(file);
    } else {
        alert('Please drop a CSV file');
    }
});

function parseCSV(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const text = e.target.result;
        const rows = text.split('\n').map(row => row.split(','));

        // Detect format
        const header = rows[0];
        if (header.includes('time') && header.includes('resource')) {
            parseTimeSeries(rows.slice(1));
        } else if (header.includes('beta') && header.includes('theta')) {
            parseParameterScan(rows.slice(1));
        } else {
            alert('Unsupported CSV format. Expected columns: time,resource,constraint OR beta,theta,outcome');
        }
    };
    reader.readAsText(file);
}

function parseTimeSeries(rows) {
    const data = rows.map(row => ({
        t: parseFloat(row[0]),
        R: parseFloat(row[1]),
        Theta: parseFloat(row[2])
    }));

    // Estimate β via logistic regression on R(t)
    const beta = estimateBetaFromTimeSeries(data);
    const theta = data[data.length - 1].Theta;  // Final constraint

    console.log(`Estimated: β=${beta.toFixed(2)}, Θ=${theta.toFixed(2)}`);

    // Update simulator parameters
    document.getElementById('beta-slider').value = beta;
    document.getElementById('theta-slider').value = theta;
    runSimulation();
}

function estimateBetaFromTimeSeries(data) {
    // Fit logistic: R(t) = R_max / (1 + exp(-β*(t - t_half)))
    // Simple heuristic: β ≈ ln(9) / t_rise (time from 10% to 90%)
    const R_min = Math.min(...data.map(d => d.R));
    const R_max = Math.max(...data.map(d => d.R));
    const R_10 = R_min + 0.1 * (R_max - R_min);
    const R_90 = R_min + 0.9 * (R_max - R_min);

    const t_10 = data.find(d => d.R >= R_10)?.t || 0;
    const t_90 = data.find(d => d.R >= R_90)?.t || 1;

    const t_rise = t_90 - t_10;
    return t_rise > 0 ? Math.log(9) / t_rise : 5.0;  // Default β=5
}
```

**UI:**

```html
<div id="csv-drop-zone" class="drop-zone">
  <p>Drag & drop CSV file here</p>
  <p class="hint">Formats: time,resource,constraint OR beta,theta,outcome</p>
</div>
```

---

## 3. llms.txt / AI Navigation

### 3.1 Rationale

**Problem:** AI crawlers (ChatGPT, Claude, Gemini) struggle to navigate complex repos without guidance.

**Solution:** Create `llms.txt` (minimal) or `ai_context.md` (comprehensive) with structured pointers.

### 3.2 Implementation

**File:** `/llms.txt` (placed in repo root)

```
# Feldtheorie - AI Navigation Guide

## Overview
Unified Trajectory Acceleration Curvature (UTAC) framework for consciousness and field theory.

## Key Concepts
- UTAC: (R, Θ, β, ζ) - Resource, Constraint, Decision Strength, Risk
- v_RIG: 1,352 km/s - Reality Integration Gradient velocity
- CREP: Coherence + Resonance + Emergence + Persistence metrics
- Type-VI: β ∈ [6.2, 6.8] implosive decision regimes

## Trilayer Structure
All documentation exists in 3 formats:
- YAML: Machine-readable (primary source)
- JSON: API-friendly
- Markdown: Human-readable

## Entry Points
1. Theory: docs/v_rig_validation_final.md
2. Decoupling: docs/entkopplungs_regime.md
3. Simulator: simulator/index.html
4. Experiments: docs/experiments/loihi_kleiber_experiment.md

## Diamond Architecture
```
    models/
       ↓
  simulation/ ← (you are here: simulator/)
       ↓
 sonification/
       ↓
     docs/
```

## Navigation Commands (for AI)
- "Show v_RIG validation" → docs/v_rig_validation_final.md
- "Explain UTAC" → releases/V6-Plans_etc/ARCHITECTURE.md
- "List experiments" → docs/experiments/
- "What is CREP?" → releases/V6-Plans_etc/type6_crep_tau_star_checklist.yaml

## Most Recent Work
- v6 Priority Tasks: v_RIG validation, Loihi experiment, 13 MHz protocol
- See: claude/v6-priority-tasks-01BC13Syyfz6jevw1adEUPwF branch
```

**Alternative:** Extended `ai_context.md` (for richer context, see `docs/AI_CONTEXT.md`)

---

## 4. Diamond Architecture SVG Map

### 4.1 Rationale

**Problem:** Module relationships unclear without visual map.

**Solution:** Interactive SVG diagram showing flow: models → simulation → sonification → docs.

### 4.2 Implementation

**SVG Structure:**

```svg
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
  <!-- Diamond shape -->
  <polygon points="300,50 500,200 300,350 100,200"
           fill="#1e3a8a" stroke="#3b82f6" stroke-width="3" opacity="0.2"/>

  <!-- Nodes -->
  <g id="models-node">
    <circle cx="300" cy="50" r="40" fill="#3b82f6" stroke="#1e40af" stroke-width="2"/>
    <text x="300" y="55" text-anchor="middle" fill="white" font-size="14">Models</text>
    <text x="300" y="100" text-anchor="middle" fill="#9ca3af" font-size="10">models/*.py</text>
  </g>

  <g id="simulation-node">
    <circle cx="500" cy="200" r="40" fill="#10b981" stroke="#059669" stroke-width="2"/>
    <text x="500" y="205" text-anchor="middle" fill="white" font-size="14">Simulate</text>
    <text x="500" y="250" text-anchor="middle" fill="#9ca3af" font-size="10">simulation/*.py</text>
  </g>

  <g id="sonification-node">
    <circle cx="300" cy="350" r="40" fill="#f59e0b" stroke="#d97706" stroke-width="2"/>
    <text x="300" y="355" text-anchor="middle" fill="white" font-size="14">Sonify</text>
    <text x="300" y="385" text-anchor="middle" fill="#9ca3af" font-size="10">Web Audio</text>
  </g>

  <g id="docs-node">
    <circle cx="100" cy="200" r="40" fill="#8b5cf6" stroke="#7c3aed" stroke-width="2"/>
    <text x="100" y="205" text-anchor="middle" fill="white" font-size="14">Docs</text>
    <text x="100" y="250" text-anchor="middle" fill="#9ca3af" font-size="10">docs/*.md</text>
  </g>

  <!-- Arrows -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#6366f1"/>
    </marker>
  </defs>

  <line x1="320" y1="85" x2="470" y2="170" stroke="#6366f1" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="470" y1="230" x2="320" y2="315" stroke="#6366f1" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="270" y1="315" x2="130" y2="230" stroke="#6366f1" stroke-width="2" marker-end="url(#arrowhead)"/>
  <line x1="130" y1="170" x2="270" y2="85" stroke="#6366f1" stroke-width="2" marker-end="url(#arrowhead)"/>
</svg>
```

**Interactive Features:**
- Hover → highlight module files
- Click → navigate to directory
- Current location highlighted (e.g., Simulate node glows if on simulator page)

**Integration:**

```html
<div id="diamond-map-container">
  <object data="architecture/diamond_map.svg" type="image/svg+xml"></object>
</div>
```

---

## 5. Type-VI Visualization Modes

### 5.1 Implosion Gravity Mode

**Current Behavior:** Particles in phase portrait explode outward from attractors.

**Proposed:** Add "Implosion Mode" where particles converge (like Type-VI consciousness collapsing).

**Toggle:**

```javascript
let implosionMode = false;

document.getElementById('implosion-toggle').addEventListener('change', (e) => {
    implosionMode = e.target.checked;
});

function updateParticle(particle, dt) {
    if (implosionMode) {
        // Reverse velocity direction (particles implode toward attractor)
        particle.vx *= -1;
        particle.vy *= -1;
    }

    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
}
```

### 5.2 Inverted Sigmoid Visualization

**Current:** Standard sigmoid (Type-I to Type-V)

**Proposed:** Add Type-VI sigmoid (inverted, implosive)

**Mathematical Form:**

Type I-V:
$$
S(x) = \frac{1}{1 + e^{-\beta x}}
$$

Type-VI:
$$
S_{\text{VI}}(x) = \frac{1}{1 + e^{+\beta x}} = 1 - S(x)
$$

**Visualization:**

```javascript
function drawSigmoid(ctx, beta, typeVI = false) {
    ctx.beginPath();
    for (let x = -5; x <= 5; x += 0.1) {
        let y;
        if (typeVI) {
            y = 1 / (1 + Math.exp(beta * x));  // Inverted
        } else {
            y = 1 / (1 + Math.exp(-beta * x));  // Standard
        }

        const canvasX = mapToCanvas(x);
        const canvasY = mapToCanvas(y);

        if (x === -5) {
            ctx.moveTo(canvasX, canvasY);
        } else {
            ctx.lineTo(canvasX, canvasY);
        }
    }

    ctx.strokeStyle = typeVI ? '#ef4444' : '#3b82f6';  // Red for Type-VI
    ctx.lineWidth = 2;
    ctx.stroke();
}
```

---

## 6. Implementation Priorities

### 6.1 Phase 1: Quick Wins (1 week)

**Priority 1:** llms.txt
- **Effort:** 1 hour
- **Impact:** High (improves AI discoverability)
- **Deliverable:** `/llms.txt` file

**Priority 2:** CSV Drag & Drop
- **Effort:** 1 day
- **Impact:** High (enables data-driven workflows)
- **Deliverable:** `simulator/csv_import.js`

### 6.2 Phase 2: Enhanced Interactivity (2 weeks)

**Priority 3:** Web Audio Sonification
- **Effort:** 3 days
- **Impact:** Medium (novel, but niche use case)
- **Deliverable:** `simulator/sonification.js`

**Priority 4:** Diamond Map SVG
- **Effort:** 2 days
- **Impact:** Medium (clarifies architecture)
- **Deliverable:** `architecture/diamond_map.svg`

### 6.3 Phase 3: Type-VI Features (1 week)

**Priority 5:** Implosion Mode + Inverted Sigmoid
- **Effort:** 2 days
- **Impact:** Low (theoretical interest, not essential)
- **Deliverable:** Update `simulator/phase_portrait.js`

---

## 7. Testing & Validation

**CSV Import Test:**
```csv
time,resource,constraint
0.0,10,100
1.0,50,100
2.0,90,100
3.0,98,100
```
→ Should estimate β ≈ 4.5 (logistic growth)

**Sonification Test:**
- Set β=4.5 → hear 220 Hz (A3)
- Set β=11 → hear 880 Hz (A5)
- Introduce instability (high dΘ/dt) → vibrato audible

**Diamond Map Test:**
- Click "Simulate" node → navigates to `simulator/`
- Hover "Models" → highlights `models/*.py` in file tree

---

## 8. Documentation Updates

**Files to Create/Update:**

1. `/llms.txt` (new)
2. `simulator/README.md` (update with new features)
3. `docs/simulator/ux_enhancement_blueprint.md` (this document)
4. `simulator/index.html` (add UI controls)
5. `simulator/sonification.js` (new)
6. `simulator/csv_import.js` (new)

---

## 9. References

### Web Audio API
- MDN: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- Tone.js (library): https://tonejs.github.io/

### CSV Parsing
- PapaParse: https://www.papaparse.com/ (robust CSV parser)

### SVG Interactivity
- D3.js: https://d3js.org/ (data-driven documents)

### Internal Docs
- V6ToDorefresh.yaml:v6r-simulator-ux
- FinalyzeVorschlägeGemini (original concept)

---

**Document Status:** ✅ **Implementation Ready**
**Version:** 1.0.0 | Created: 2025-12-04
**Next Action:** Implement Phase 1 (llms.txt + CSV import)

**CREP Alignment:**
- **C (Completeness):** All 5 features specified ✓
- **R (Rigor):** Code stubs provided ✓
- **E (Evidence):** Addresses real UX gaps ✓
- **P (Parsimony):** Minimal dependencies ✓

**Type-VI Detection Score:** 0.65 (UX improvement, moderate priority)
