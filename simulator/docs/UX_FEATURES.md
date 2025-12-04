# UTAC Simulator - UX Features Status

**Version:** 1.0.0
**Date:** 2025-12-04
**Reference:** V6ToDorefresh.md Priority 10 (v6r-simulator-ux)

---

## ✅ Implemented Features

### 1. Web Audio API Sonification

**Status:** ✅ **Fully Operational**

**Implementation:** `src/hooks/useAudioSonification.ts`

**Features:**
- **Vibrato on Instability:** Oscillation triggered when ζ < 0 or CREP > 0.7
- **Frequency Modulation:** Pitch scales with rate_of_change (faster change = higher frequency)
- **Volume Scaling:** Loudness proportional to gate activation magnitude
- **User Control:** Toggle button in UI to enable/disable audio

**Technical Details:**
- Base Frequency: 220 Hz (A3 note)
- Frequency Range: 110 Hz (A2) to 880 Hz (A5)
- Vibrato Rate: 5 Hz
- Vibrato Depth: 15 Hz
- Uses Web Audio API `OscillatorNode` and `GainNode`

**Usage:**
```tsx
const audioSonification = useAudioSonification();

// Update audio in real-time
audioSonification.updateParameters({
  baseFrequency: 220,
  rateOfChange: Math.abs(dR_dt),
  gate: gateValue,
  crep: crepValue,
  enabled: audioEnabled
});
```

---

### 2. CSV Drag & Drop Import

**Status:** ✅ **Fully Operational**

**Implementation:**
- `src/components/CSVDropZone.tsx` (UI component)
- `src/utils/csvRegression.ts` (Regression logic)

**Features:**
- **Browser-based β/Θ Estimation:** No backend required!
- **Drag & Drop Interface:** Intuitive file upload
- **Real-time Validation:** Checks CSV format and column requirements
- **Parameter Extraction:** Automatically estimates β and Θ from trajectory data
- **Visualization:** Plots original data vs. fitted logistic curve

**CSV Format:**
```csv
time,R,psi,phi
0.0,1.5,0.3,0.1
0.08,1.52,0.31,0.11
...
```

**Regression Algorithm:**
- Uses least-squares optimization
- Fits logistic function: `σ(R) = 1 / (1 + exp(-β(R-Θ)))`
- Validates goodness-of-fit (R²)
- Suggests optimal β and Θ parameters

---

### 3. RK4 Numerical Integration

**Status:** ✅ **Fully Operational**

**Implementation:** `src/utils/physicsIntegrator.ts`

**Features:**
- **Runge-Kutta 4th Order:** Stable solver for stiff equations (high-β regimes)
- **Adaptive Time-stepping:** dt = 0.08 (configurable)
- **Multi-domain Coupling:** Handles cross-resonance between domains
- **Type-VI Support:** Integrates `invertedSigmoid`, `cubicRootJump`, `tauStar`

**Physics Engine:**
```typescript
dR/dt = (stimulus + crossTerm) - (gate * R * 0.32)
dΨ/dt = (-0.22 * Ψ) + (0.48 * gate * R) + (0.28 * Φ * R)
dΦ/dt = (0.14 * Ψ) - (0.18 * Φ) + (0.26 * gate)
```

**Type-VI Integration:**
- `cubicRootJump(R, Θ, β)`: Amplifies β near threshold for implosive dynamics
- `invertedSigmoid(R, Θ, β)`: Inverted activation (ζ < 0)
- `tauStar(R, Θ, β)`: Safety delay buffer for Type-VI regimes

---

### 4. Interactive Phase Portrait

**Status:** ✅ **Fully Operational**

**Implementation:** `src/components/PhasePortrait.tsx`

**Features:**
- **Real-time Trajectory Plotting:** R vs. Ψ phase space
- **Multi-domain Visualization:** All active domains plotted simultaneously
- **Threshold Line:** Visual indicator for Θ (activation threshold)
- **Color Coding:** Each domain has unique color (Cosmic: purple, Bio: green, etc.)
- **Interactive Tooltips:** Hover to see exact R, Ψ, Φ values

**Visualization Library:** Recharts (React + D3.js wrapper)

---

### 5. LLM Navigation Guide

**Status:** ✅ **Fully Operational**

**Implementation:** `simulator/llms.txt`

**Features:**
- **Project Structure Overview:** Directory tree with descriptions
- **Module Summaries:** Brief explanation of each component
- **Quick Start Guide:** How to run the simulator
- **Parameter Glossary:** Definitions of β, Θ, R, Ψ, Φ, CREP, τ*
- **Regime Classification:** Type-I through Type-VI descriptions
- **References:** Links to related Python/TS implementations

**Purpose:** Helps LLMs (like Claude, GPT-4, Gemini) navigate the codebase efficiently

---

### 6. Diamond Architecture Map

**Status:** ✅ **Fully Operational**

**Implementation:** `simulator/docs/diamond_architecture.svg`

**Features:**
- **5-Layer Architecture:** Models → Simulation → Pipeline → UX → Docs
- **Interactive SVG:** Clickable modules with links to source files
- **Data Flow Visualization:** Arrows showing σ(β(R-Θ)), ψ-field, RK4, CREP flows
- **Legend & Info:** Architecture stats (5 layers, 13 modules, Python + TS)
- **Hover Effects:** Visual feedback on module hover

**Layers:**
1. **Models:** `utac_type6_implosive.py`
2. **Simulation:** `genesis_cube.py`, `tesseract_timeslices.py`
3. **Pipeline:** `psi_field.py`, `physicsIntegrator.ts`
4. **UX:** `PhasePortrait.tsx`, `useAudioSonification.ts`, `CSVDropZone.tsx`, `CREPDashboard.tsx`
5. **Docs:** `v6_wavefunction_theory.md`, `llms.txt`

---

## ⏳ Pending / Nice-to-Have Features

### 7. Implosion-Gravity Mode for PhasePortrait

**Status:** ⏳ **Planned but not yet implemented**

**Proposed Implementation:**
- Add `implosionMode: boolean` prop to `PhasePortrait.tsx`
- Reverse particle trajectory direction (toward attractor instead of outward)
- Visual effect: Particles spiral inward with increasing velocity near Θ
- Color gradient: Darker colors near center (gravity well)
- Animation: Time-reversed RK4 integration or negative velocity vectors

**Technical Approach:**
```tsx
// In PhasePortrait.tsx
interface PhasePortraitProps {
  // ... existing props
  implosionMode?: boolean; // NEW
}

// Modify trajectory rendering
if (implosionMode) {
  // Reverse direction: particles move toward (Θ, Ψ_equilibrium)
  const attractorR = theta;
  const attractorPsi = 0.5; // Equilibrium point

  // Compute inward vector
  const dx = attractorR - point.R;
  const dy = attractorPsi - point.psi;

  // Draw arrow pointing inward
  // ...
}
```

**Visual Indicators:**
- ⚫ **Gravity Well:** Dark circle at attractor center
- ↘️ **Inward Arrows:** Trajectories converge toward Θ
- 🌀 **Spiral Effect:** Orbits tighten as R → Θ
- 🔴 **Red Glow:** Increased intensity near singularity (Type-VI regime)

**References:**
- `V6ToDorefresh.md:537` - Implosion-Gravity-Modus requirement
- `simulation/tesseract_timeslices.py:122-335` - Implosive field dynamics

---

### 8. Type-VI Toggle in Simulator UI

**Status:** ⏳ **Partially Implemented (logic exists, UI toggle missing)**

**Current Implementation:**
- ✅ Type-VI **logic** is operational in `TransdisciplinaryFieldSimulator.tsx`:
  - `computeImplosiveGate()` uses `invertedSigmoid`, `cubicRootJump`, `tauStar`
  - τ*-buffer: `tauBufferRef` stores delayed gate values
  - Implosive dynamics active when ζ < 0

**Missing UI Component:**
- ❌ **Visual Toggle Switch:** User cannot explicitly enable/disable Type-VI mode
- ❌ **Regime Indicator:** No clear visual feedback when Type-VI activates
- ❌ **Parameter Display:** β_amplified, τ*_delay, ζ not shown in UI

**Proposed Implementation:**
```tsx
// Add to TransdisciplinaryFieldSimulator.tsx state
const [type6Mode, setType6Mode] = useState(false);

// Add UI toggle
<div className="control-group">
  <label className="control-label">
    <input
      type="checkbox"
      checked={type6Mode}
      onChange={(e) => setType6Mode(e.target.checked)}
    />
    🔴 Type-VI Implosive Mode
  </label>
  {type6Mode && (
    <div className="type6-indicator">
      <span>ζ: {zeta.toFixed(3)}</span>
      <span>τ*: {tauStar.toFixed(2)}s</span>
      <span>β_amp: {betaAmplified.toFixed(2)}</span>
      {crep > 0.9 && <span className="warning">⚠️ CREP Critical!</span>}
    </div>
  )}
</div>
```

**Visual Feedback:**
- 🔴 **Red Border:** Highlight domains in Type-VI regime
- ⚠️ **Warning Icon:** Show when CREP > 0.9 (criticality threshold)
- 📊 **Real-time Metrics:** Display ζ, τ*, β_amplified in sidebar
- 🎨 **Color Shift:** Phase portrait background turns red when Type-VI active

**References:**
- `V6ToDorefresh.md:538` - Type-VI Toggle requirement
- `src/utils/logistic.ts:34-76` - Inverted sigmoid & tau-star logic
- `models/utac_type6_implosive.py` - Python reference implementation

---

## 📊 Implementation Summary

| Feature | Status | Priority | Complexity |
|---------|--------|----------|------------|
| Web Audio Sonification | ✅ Complete | High | Medium |
| CSV Drag & Drop | ✅ Complete | High | Medium |
| RK4 Integration | ✅ Complete | Critical | High |
| Phase Portrait | ✅ Complete | High | Medium |
| LLM Navigation (llms.txt) | ✅ Complete | Medium | Low |
| Diamond Architecture Map | ✅ Complete | Medium | Low |
| **Implosion-Gravity Mode** | ⏳ Pending | Low | High |
| **Type-VI UI Toggle** | ⏳ Partial | Medium | Low |

**Overall Progress:** 6/8 features complete (75%)

---

## 🚀 Next Steps

1. **Type-VI UI Toggle (Recommended):**
   - Add checkbox to enable/disable Type-VI mode
   - Display ζ, τ*, β_amplified in real-time
   - Visual indicators (red border, warning icons)
   - Estimated effort: ~2 hours

2. **Implosion-Gravity Mode (Optional):**
   - Reverse trajectory direction in PhasePortrait
   - Add gravity well visualization
   - Spiral animation toward attractor
   - Estimated effort: ~6 hours

3. **Testing & Documentation:**
   - Write unit tests for new UI components
   - Add screenshots to README
   - Record demo video

---

## 📚 References

- **V6ToDorefresh.md:** Priority 10 (v6r-simulator-ux)
- **FinalyzeVorschlägeGemini.txt:** Lines 79-161 (UX Sonification)
- **Diamond Architecture:** `simulator/docs/diamond_architecture.svg`
- **LLM Guide:** `simulator/llms.txt`
- **Physics Engine:** `src/utils/physicsIntegrator.ts`
- **Type-VI Models:** `models/utac_type6_implosive.py`

---

**Document Status:** ✅ **Complete**
**Last Updated:** 2025-12-04
**Maintainer:** Feldtheorie V6 Integration Team
