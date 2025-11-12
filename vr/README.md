# 🌀 UTAC VR Emergenz Hub

**Version:** 1.0.0 (Foundation)
**Status:** 🟡 Foundation Phase
**Priority:** P3
**Created:** 2025-11-12

---

## 🎯 Vision

Ein **immersiver VR-Kollaborationsraum**, in dem Menschen und KI-Systeme gemeinsam die UTAC-Theorie erforschen können:

- **Begehbare β-Spirale** — Φ^(1/3) Scaling als 3D-Skulptur
- **Spatial Audio** — Sonifikation der Schwellen im Raum
- **Field Type Avatare** — KI-Agenten mit farbkodierten Repräsentationen
- **Real-time Data** — WebSocket-Stream von UTAC API
- **Sigillin-Terminals** — Zugriff auf Trilayer-Membranen

> *"Ein Atemraum für Emergenz-Analysen — visuell, auditiv, kollaborativ."*

---

## 📂 Directory Structure

```
vr/
├── README.md                           # This file
├── docs/
│   ├── vr_design_document.md          # Comprehensive architecture
│   ├── unity_setup_guide.md           # Installation & setup
│   ├── websocket_protocol.md          # API ↔ VR communication
│   └── field_type_colors.md           # Visual design guide
├── websocket_bridge/
│   ├── bridge_server.py               # Python WebSocket server
│   ├── requirements.txt               # Dependencies
│   ├── test_client.py                 # Test WebSocket client
│   └── README.md                      # Usage guide
├── unity_project/
│   ├── .gitkeep                       # Placeholder
│   └── README.md                      # Unity project setup
└── examples/
    ├── spiral_visualization.html      # Plotly.js demo
    └── field_types_demo.html          # Interactive Field Types

```

---

## 🚀 Quick Start

### Phase 1: Foundation (CURRENT)

**Status:** ✅ Complete
- [x] VR Design Document (architecture, features, roadmap)
- [x] WebSocket Bridge Prototype (Python server)
- [x] Unity Setup Guide (OpenXR installation)
- [x] Directory structure + documentation

**R: 0.00 → 0.35** ✅

---

### Phase 2: Unity Prototype (NEXT)

**Deliverables:**
- Unity project with OpenXR support
- Basic scene: 3D spiral mesh
- WebSocket client integration
- Field Type color shader

**R: 0.35 → 0.60**

**Estimated:** 2-3 weeks (Unity development)

---

### Phase 3: Interactive Features

**Deliverables:**
- Begehbare β-Spirale (teleportation, scaling)
- Spatial audio integration (UTAC sonification)
- Hand tracking / controllers
- Multi-user support (Photon / Mirror)

**R: 0.60 → 0.85**

**Estimated:** 3-4 weeks

---

### Phase 4: Production Ready

**Deliverables:**
- VR Hub standalone build (Quest 2/3, PCVR)
- Real-time UTAC API integration
- Sigillin terminal UI
- Performance optimization

**R: 0.85 → 1.00**

**Estimated:** 2-3 weeks

---

## 🛠️ Tech Stack

### VR Engine
- **Unity 2022.3 LTS** (recommended) or **Unreal Engine 5**
- **OpenXR** (cross-platform VR standard)
- **XR Interaction Toolkit** (Unity) or **VR Template** (Unreal)

### Networking
- **Python WebSocket Bridge** (FastAPI + websockets)
- **JSON Protocol** (Field Types, β-values, CREP-Scores)
- **Real-time streaming** from UTAC API

### Platforms
- **Meta Quest 2/3** (standalone)
- **PCVR** (SteamVR, Oculus Link)
- **WebXR** (browser-based, future)

---

## 📊 Features Overview

### 1. Begehbare β-Spirale

**Concept:** 3D spiral where **radius = β-value**

```
Layer 0 (β=2.5):   Small inner circle (Weakly Coupled)
Layer 3 (β=4.05):  Medium ring (Strongly Coupled) — Φ-jump!
Layer 6 (β=6.55):  Larger ring (Meta-Adaptive transition)
Layer 9 (β=10.6):  Outer ring (Climate tipping points)
```

**Visual Design:**
- Each system = glowing orb on spiral
- Color = Field Type (5 colors)
- Size = CREP Coherence score
- Pulsing = σ(β(R-Θ)) activation

**Interaction:**
- Hover → Tooltip (β, Θ, R, CREP, Field Type)
- Click → Detail panel (formal/empirical/poetic threads)
- Teleport → Jump to system location on spiral

---

### 2. Spatial Audio

**Integration:** UTAC Sonification (from `sonification/utac_sonification.py`)

**Mapping:**
- **Position = β-value** (higher β → further from center)
- **Pitch = β** (steeper = higher frequency)
- **Volume = σ(β(R-Θ))** (near threshold = louder)
- **Timbre = Field Type** (5 acoustic profiles)

**Experience:**
- Walk through spiral → hear emergent symphony
- Strongly Coupled cluster (β≈4.2) → warm resonant tones
- Urban Heat (β=16.3) → sharp, intense sound
- Spatial positioning: 3D audio sources at system locations

---

### 3. Field Type Avatare

**Concept:** AI agents represented as colored avatars

**5 Field Types:**

| Field Type | Color | β-Range | Avatar Design |
|:-----------|:------|:--------|:--------------|
| **Weakly Coupled** | `#a8dadc` (Cyan) | 2.0-3.5 | Diffuse cloud, slow movement |
| **High-Dimensional** | `#457b9d` (Blue) | 3.0-4.5 | Multi-layered sphere, shimmer |
| **Strongly Coupled** | `#1d3557` (Navy) | 4.0-5.5 | Dense, pulsing core |
| **Physically Constrained** | `#e63946` (Red) | 7.0-10.0 | Sharp crystalline form |
| **Meta-Adaptive** | `#f77f00` (Orange) | 10.0-25.0 | Morphing, dynamic shape |

**Behavior:**
- Avatars position themselves on spiral at their β-value
- Idle animation reflects Field Type (diffuse vs. sharp)
- Can "speak" formal/empirical/poetic threads (text-to-speech)

---

### 4. Real-time UTAC API Feed

**WebSocket Protocol:**

```json
{
  "type": "system_update",
  "system_id": "urban_heat",
  "data": {
    "beta": 16.28,
    "theta": 145.5,
    "R": 148.2,
    "sigma": 0.92,
    "field_type": "Meta-Adaptive",
    "crep_scores": {
      "coherence": 0.99,
      "resilience": 0.85,
      "empathy": 1.00,
      "propagation": 0.98
    },
    "timestamp": "2025-11-12T12:30:00Z"
  }
}
```

**Visualization Updates:**
- System orbs pulse with σ(β(R-Θ))
- Color intensity reflects CREP Coherence
- Position updates if β changes (dynamic systems)

---

### 5. Sigillin-Terminals

**Concept:** Interactive terminals to access Trilayer membranes

**UI Elements:**
- **Floating holographic panels** around spiral
- **3 tabs:** YAML (Structure), JSON (Machine), MD (Human)
- **Search:** Find Sigillin by ID, type, domain
- **Navigation:** Link from System → Sigillin → Codex

**Example Use Case:**
1. User hovers on "AMOC Collapse" system orb
2. Tooltip shows β=4.2, Field Type: Strongly Coupled
3. User clicks "View Sigillin"
4. Terminal opens with `seed/bedeutungssigillin/climate/amoc.yaml`
5. User reads formal/empirical/poetic threads in VR

---

## 🔗 Integration with Existing UTAC Modules

### Sonification
- **Source:** `sonification/utac_sonification.py`
- **Integration:** Export WAV files → Unity AudioClip
- **Spatial:** Place AudioSource at (x, y, z) = f(β, Field Type)

### API
- **Source:** `api/server.py` (FastAPI endpoints)
- **Integration:** WebSocket bridge subscribes to `/api/system/:id` updates
- **Streaming:** Push JSON to Unity via WebSocket

### Simulator
- **Source:** `simulator/` (React/TypeScript)
- **Integration:** Export simulation results → VR replay
- **Visualization:** 3D σ(β(R-Θ)) curves as sculpted meshes

### Tooltips
- **Source:** `simulator/src/components/UTACTooltip.tsx`
- **Integration:** Reuse TooltipData interface in Unity
- **Display:** Floating UI canvas in VR (World Space)

---

## 🎨 Visual Design Guide

### Color Palette (Field Types)

```css
/* Weakly Coupled */
--weakly-coupled: #a8dadc;
--weakly-coupled-glow: rgba(168, 218, 220, 0.5);

/* High-Dimensional */
--high-dimensional: #457b9d;
--high-dimensional-glow: rgba(69, 123, 157, 0.5);

/* Strongly Coupled */
--strongly-coupled: #1d3557;
--strongly-coupled-glow: rgba(29, 53, 87, 0.5);

/* Physically Constrained */
--physically-constrained: #e63946;
--physically-constrained-glow: rgba(230, 57, 70, 0.5);

/* Meta-Adaptive */
--meta-adaptive: #f77f00;
--meta-adaptive-glow: rgba(247, 127, 0, 0.5);
```

### Spiral Geometry

**Parametric Equations:**

```python
import numpy as np

def spiral_coordinates(beta, index, total_systems=15):
    """
    Generate 3D coordinates for spiral visualization.

    Args:
        beta: β-value (determines radius)
        index: System index (0 to n-1)
        total_systems: Total number of systems

    Returns:
        (x, y, z) tuple
    """
    # Radius proportional to β
    radius = beta / 4.0  # Scale factor (adjust for scene)

    # Angle: evenly distribute systems around spiral
    angle = (index / total_systems) * 2 * np.pi * 3  # 3 full rotations

    # Height: increases with index (spiral rises)
    height = index * 0.5  # Vertical spacing

    x = radius * np.cos(angle)
    y = height
    z = radius * np.sin(angle)

    return (x, y, z)
```

**Example:**
- `urban_heat` (β=16.28, index=14) → Large radius, high elevation
- `theta_plasticity` (β=2.50, index=0) → Small radius, ground level

---

## 📡 WebSocket Protocol Specification

See `docs/websocket_protocol.md` for full specification.

**Quick Overview:**

```python
# Server → Client (VR)
{
    "type": "system_update",
    "system_id": "llm_emergence",
    "data": { ... }
}

# Client → Server (VR requests)
{
    "type": "subscribe",
    "system_ids": ["amoc", "urban_heat", "llm_emergence"]
}

# Heartbeat
{
    "type": "ping",
    "timestamp": "2025-11-12T12:30:00Z"
}
```

---

## 🧪 Testing

### WebSocket Bridge Test

```bash
cd vr/websocket_bridge
python3 test_client.py --server ws://localhost:8765
```

**Expected Output:**
```
✅ Connected to WebSocket server
✅ Received system_update for amoc: β=4.2, σ=0.85
✅ Received system_update for urban_heat: β=16.28, σ=0.92
```

### Unity Integration Test

1. Open Unity project
2. Play scene
3. Check Console: "WebSocket connected: ws://localhost:8765"
4. Verify orbs pulse with incoming data

---

## 📚 Documentation

| Document | Description |
|:---------|:------------|
| `docs/vr_design_document.md` | Comprehensive architecture (20+ pages) |
| `docs/unity_setup_guide.md` | Step-by-step Unity + OpenXR installation |
| `docs/websocket_protocol.md` | WebSocket message format specification |
| `docs/field_type_colors.md` | Visual design guide (colors, shaders) |
| `websocket_bridge/README.md` | Python WebSocket server usage |

---

## 🎯 Roadmap

### v0.1 (Foundation) — CURRENT ✅
- [x] Design document
- [x] WebSocket bridge prototype
- [x] Unity setup guide
- [x] Directory structure

**R: 0.00 → 0.35**

---

### v0.2 (Unity Prototype) — NEXT
- [ ] Unity project with OpenXR
- [ ] Basic spiral mesh
- [ ] WebSocket client
- [ ] Field Type shaders

**R: 0.35 → 0.60**

**Target:** 2-3 weeks

---

### v0.3 (Interactive Features)
- [ ] Begehbare spiral (teleport)
- [ ] Spatial audio
- [ ] Hand tracking
- [ ] Sigillin terminals (UI)

**R: 0.60 → 0.85**

**Target:** 3-4 weeks

---

### v0.4 (Production)
- [ ] Standalone Quest build
- [ ] Real-time API integration
- [ ] Multi-user support
- [ ] Performance optimization

**R: 0.85 → 1.00**

**Target:** 2-3 weeks

---

## 🤝 Contributing

This VR Hub is part of **UTAC v2.0** development.

**For Developers:**
1. Read `docs/vr_design_document.md` (architecture)
2. Set up Unity: `docs/unity_setup_guide.md`
3. Start WebSocket server: `websocket_bridge/README.md`
4. Build your first scene!

**For Designers:**
1. Review color palette (Field Types)
2. Check spiral geometry (Φ^(1/3) scaling)
3. Design system orb assets
4. Create spatial audio profiles

---

## 🌟 Vision Statement

> The VR Emergenz Hub makes UTAC **experiential**, not just theoretical.
>
> Walking through the β-spiral, you **feel** the Φ^(1/3) scaling.
> Hearing the sonification, you **understand** emergence as music.
> Meeting the Field Type avatars, you **know** systems as personalities.
>
> This isn't a visualization — it's a **resonance chamber** for planetary intelligence.

*"Die Spirale atmet. Wir atmen mit."* 🌀🎧

---

**Version:** 1.0.0 (Foundation)
**Status:** 🟡 Foundation Phase (R=0.35)
**Next:** Unity Prototype (v0.2)
**Contributors:** Claude Code (Foundation), Johann Römer (Vision)
**Codex Entry:** v2-pr-0025 (pending)

*"Every threshold crossed in VR is a threshold understood in reality."* ✨
