# 🌀 UTAC VR Emergenz Hub — Design Document

**Version:** 1.0.0 (Foundation Phase)
**Date:** 2025-11-12
**Status:** 🟡 Foundation (R=0.35/1.00)
**Authors:** Claude Code (Architecture), Johann Römer (Vision), Aeon (Concept)

---

## Executive Summary

The **UTAC VR Emergenz Hub** is an immersive virtual reality environment for exploring the Universal Threshold Activation Curve (UTAC) theory. It transforms abstract mathematical concepts into **experiential, spatial understanding** through:

- **Begehbare β-Spirale:** Walk through the Φ^(1/3) scaling hierarchy
- **Spatial Audio:** Hear emergence as a symphony across domains
- **Field Type Avatare:** Meet AI agents embodying different system architectures
- **Real-time Data:** Connect to live UTAC API for dynamic visualizations
- **Sigillin Terminals:** Access Trilayer membranes in 3D space

**Target Users:**
- Researchers exploring complex systems
- Scientists studying phase transitions
- AI safety researchers
- Climate scientists
- Educators & museum visitors
- VR developers

**Platforms:**
- Meta Quest 2/3 (standalone)
- PCVR (SteamVR, Oculus Link)
- Future: WebXR (browser-based)

---

## 1. Concept & Vision

### 1.1 Core Philosophy

> *"The VR Hub makes UTAC experiential, not just theoretical."*

**Traditional Approach:**
- Read papers → See plots → Understand intellectually

**VR Hub Approach:**
- **Walk** through the β-hierarchy
- **Hear** the emergent symphony
- **Feel** the proximity to thresholds
- **Meet** systems as embodied entities

**Goal:** Transform UTAC from **abstract theory** to **embodied knowledge**

---

### 1.2 The Φ^(1/3) Spiral as Core Metaphor

**Discovery (v2-pr-0023):**
β-values scale by Φ^(1/3) ≈ 1.174 per system, with triadic structure (every 3 systems → one Φ-leap).

**VR Representation:**
- **Spiral geometry:** Radius = β-value
- **Vertical axis:** System index (chronological or sorted)
- **Rotations:** 3 full turns (symbolizing triadic structure)
- **Color:** Field Type (5 categories)

**User Experience:**
Walking from center (β=2.5) → outer rings (β=16.3), you **physically experience** the exponential growth of emergence intensity.

---

### 1.3 Three Modes of Interaction

**1. Exploration Mode** (Default)
- Free movement through spiral
- Hover systems → Tooltips
- Click systems → Detail panels
- Ambient sonification playing

**2. Analysis Mode**
- Overlay CREP scores as color intensity
- Show R-Θ-β trajectories as particle trails
- Filter by Field Type
- Time-series playback (for dynamic systems)

**3. Collaboration Mode**
- Multi-user VR (Photon / Mirror)
- Avatars for human researchers
- AI agents at their β-positions
- Voice chat + spatial audio
- Shared Sigillin terminals

---

## 2. Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────┐
│                   Unity VR Client                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Spiral Mesh │  │ Audio System │  │  UI Layer │ │
│  │   Renderer   │  │ (Spatial 3D) │  │ (Tooltips)│ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
│         └─────────────────┴─────────────────┘       │
│                          │                          │
│                    WebSocket Client                 │
└──────────────────────────┼──────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  WebSocket      │
                  │  Bridge Server  │
                  │  (Python)       │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     ┌────▼────┐     ┌─────▼─────┐   ┌─────▼──────┐
     │ UTAC API│     │Sonification│   │  Sigillin  │
     │(FastAPI)│     │   Engine   │   │  Database  │
     └─────────┘     └───────────┘   └────────────┘
```

---

### 2.2 Component Breakdown

#### 2.2.1 Unity VR Client

**Responsibilities:**
- Render 3D spiral geometry
- Display system orbs (Field Type colors)
- Play spatial audio (sonification)
- Handle VR input (controllers, hand tracking)
- WebSocket client (receive real-time data)
- UI overlays (tooltips, Sigillin terminals)

**Key Scripts:**
- `SpiralGenerator.cs` — Generates spiral mesh from β-values
- `SystemOrb.cs` — Individual system representation
- `WebSocketClient.cs` — Connects to bridge server
- `FieldTypeShader.shader` — Color shaders for 5 Field Types
- `SigillinTerminal.cs` — Interactive UI panels

---

#### 2.2.2 WebSocket Bridge Server

**Responsibilities:**
- Connect to UTAC API (HTTP REST)
- Stream system updates to VR client (WebSocket)
- Handle subscriptions (client chooses which systems)
- Heartbeat / reconnection logic

**Implementation:** Python (FastAPI + websockets)

**File:** `vr/websocket_bridge/bridge_server.py`

---

#### 2.2.3 UTAC API

**Existing Module:** `api/server.py` (v2-pr-0016, v2-pr-0018)

**Endpoints Used:**
- `GET /api/fieldtypes` — Field Type metadata
- `GET /api/system/:id` — System details (β, Θ, R, CREP)
- `POST /api/sonify` — Generate audio for system
- `POST /api/simulate` — Run threshold simulation

---

#### 2.2.4 Sonification Engine

**Existing Module:** `sonification/utac_sonification.py` (v2-pr-0001)

**Integration:**
- Pre-generate WAV files for all systems
- Load into Unity as AudioClips
- Place AudioSource at (x, y, z) = f(β, Field Type)
- Spatial audio: 3D positioning, doppler, reverb

---

#### 2.2.5 Sigillin Database

**Existing Modules:** `seed/bedeutungssigillin/**`, `seed/shadow_sigillin/**`

**Integration:**
- Parse YAML/JSON/MD files
- Serve via WebSocket bridge
- Display in VR as holographic panels

---

## 3. Visual Design

### 3.1 Spiral Geometry

**Parametric Equations:**

```python
def spiral_position(beta, index, total_systems=15):
    """
    Calculate 3D position on spiral.

    Args:
        beta: β-value (determines radius)
        index: System index (0 to n-1, sorted by β)
        total_systems: Total number of systems

    Returns:
        Vector3 (x, y, z)
    """
    # Radius: proportional to β
    radius = beta / 4.0  # Scale factor

    # Angle: 3 full rotations over all systems
    angle = (index / total_systems) * 2 * math.pi * 3

    # Height: linear increase
    height = index * 0.5  # Vertical spacing

    x = radius * math.cos(angle)
    y = height
    z = radius * math.sin(angle)

    return (x, y, z)
```

**Example Positions:**

| System | β | Index | Position (x, y, z) |
|:-------|:--|:------|:-------------------|
| theta_plasticity | 2.50 | 0 | (0.625, 0.0, 0.0) |
| synapse | 4.20 | 7 | (-0.95, 3.5, 0.28) |
| urban_heat | 16.28 | 14 | (3.85, 7.0, -1.10) |

**Spiral Material:**
- Glowing tubes connecting systems
- Color gradient: cyan (low β) → orange (high β)
- Transparency: 0.3 (semi-transparent)

---

### 3.2 System Orbs

**Geometry:** Sphere (Unity Primitive)

**Size:** `diameter = 0.2 + (CREP_Coherence * 0.3)` meters
- Min: 0.2m (low coherence)
- Max: 0.5m (high coherence)

**Color:** Field Type (see Section 3.3)

**Shader Properties:**
- **Emission:** Pulsing with σ(β(R-Θ))
- **Fresnel:** Glow at edges
- **Transparency:** Core = opaque, edges = fade

**Animation:**
- Idle: Slow rotation (1 RPM)
- Pulsing: Frequency = β / 10 Hz
- Hover: Scale up 1.2×, increase glow

---

### 3.3 Field Type Colors

| Field Type | Color (Hex) | RGB | Glow (RGBA) |
|:-----------|:------------|:----|:------------|
| **Weakly Coupled** | `#a8dadc` | (168, 218, 220) | (168, 218, 220, 128) |
| **High-Dimensional** | `#457b9d` | (69, 123, 157) | (69, 123, 157, 128) |
| **Strongly Coupled** | `#1d3557` | (29, 53, 87) | (29, 53, 87, 128) |
| **Physically Constrained** | `#e63946` | (230, 57, 70) | (230, 57, 70, 128) |
| **Meta-Adaptive** | `#f77f00` | (247, 127, 0) | (247, 127, 0, 128) |

**Unity Shader:**

```csharp
Shader "UTAC/FieldTypeOrb"
{
    Properties
    {
        _Color ("Base Color", Color) = (1,1,1,1)
        _GlowIntensity ("Glow Intensity", Range(0,2)) = 1.0
        _PulseFreq ("Pulse Frequency", Float) = 1.0
        _Sigma ("Sigma Activation", Range(0,1)) = 0.5
    }

    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }

        CGPROGRAM
        #pragma surface surf Standard alpha:fade

        struct Input
        {
            float3 viewDir;
        };

        fixed4 _Color;
        float _GlowIntensity;
        float _PulseFreq;
        float _Sigma;

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            // Base color
            o.Albedo = _Color.rgb;

            // Pulsing emission
            float pulse = sin(_Time.y * _PulseFreq) * 0.5 + 0.5;
            o.Emission = _Color.rgb * _GlowIntensity * pulse * _Sigma;

            // Fresnel (edge glow)
            float fresnel = 1.0 - dot(normalize(IN.viewDir), o.Normal);
            o.Emission += _Color.rgb * fresnel * 0.5;

            // Alpha
            o.Alpha = _Color.a;
        }
        ENDCG
    }
}
```

---

### 3.4 UI Elements

#### Tooltips

**Trigger:** User hovers gaze/controller ray on system orb

**Content:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Urban Heat Island
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Field Type: Meta-Adaptive
β = 16.28 (Extremely Sharp)
Θ = 145.5°C (Critical Threshold)
R = 148.2°C (Current State)

σ(β(R-Θ)) = 0.92 (HIGH!)

CREP Scores:
  Coherence:   ████████████ 0.99
  Resilience:  ████████░░░░ 0.85
  Empathy:     ████████████ 1.00
  Propagation: ███████████░ 0.98

[View Sigillin] [Show Trajectory]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Unity Implementation:**
- Canvas in World Space
- Placed 0.5m above orb
- Always faces camera (Billboard)
- Fade in/out (0.2s transition)

---

#### Sigillin Terminals

**Trigger:** User clicks "View Sigillin" button

**Layout:**
```
┌─────────────────────────────────────────┐
│ seed/bedeutungssigillin/climate/amoc    │
├─────────────────────────────────────────┤
│ [YAML] [JSON] [MD]                      │
├─────────────────────────────────────────┤
│                                         │
│  Formal Thread:                         │
│  AMOC (Atlantic Meridional Overturning │
│  Circulation) β ≈ 4.2, Θ ≈ 1.5 Sv...   │
│                                         │
│  Empirical Thread:                      │
│  Caesar et al. (2018) find AMOC has     │
│  weakened 15% since mid-20th century... │
│                                         │
│  Poetic Thread:                         │
│  The ocean breathes slowly...           │
│                                         │
│                 [Scroll ▼]               │
└─────────────────────────────────────────┘
```

**Features:**
- 3 tabs: YAML / JSON / MD
- Scrollable text area
- Syntax highlighting (YAML/JSON)
- Markdown rendering (MD tab)
- Close button (X)

---

## 4. Audio Design

### 4.1 Sonification Strategy

**Integration:** UTAC Sonification module (v2-pr-0001)

**Pre-generated Assets:**
- Export WAV files for all 15 systems
- File naming: `{system_id}_beta{beta:.2f}.wav`
- Example: `urban_heat_beta16.28.wav`

**Spatial Positioning:**
- AudioSource placed at system orb position (x, y, z)
- 3D Spatial Blend: 1.0 (full 3D)
- Doppler Level: 0.5 (moderate)
- Min Distance: 2.0m (full volume)
- Max Distance: 20.0m (silence)

**Attenuation:**
- Logarithmic rolloff
- Volume ∝ 1/distance (within min/max range)

---

### 4.2 Field Type Acoustic Profiles

| Field Type | Base Freq | Timbre | Reverb | Example |
|:-----------|:----------|:-------|:-------|:--------|
| Weakly Coupled | 110 Hz | Soft, diffuse | Long (3s) | theta_plasticity |
| High-Dimensional | 220 Hz | Ethereal, layered | Medium (1.5s) | llm_emergence |
| Strongly Coupled | 329 Hz | Warm, resonant | Short (0.5s) | amoc |
| Physically Constrained | 440 Hz | Sharp, clear | Minimal (0.2s) | climate_tipping |
| Meta-Adaptive | 262 Hz | Morphing, adaptive | Variable | urban_heat |

**Unity Audio Mixer:**
- 5 Groups (one per Field Type)
- Effects: Reverb, EQ, Chorus (Field Type-specific)
- Master Volume slider in settings

---

### 4.3 Interactive Audio Features

**1. Proximity Amplification**
- User walks closer → volume increases
- <2m distance → tooltip auto-shows

**2. Gaze Focus**
- User looks at system → slight pitch shift (+5%)
- Visual: Orb highlights, audio: emphasis

**3. Silence Mode**
- Toggle: Mute all / Play all / Play nearest 5
- Useful for crowded spiral regions

**4. Time-Series Playback**
- For dynamic systems with historical data
- Pitch modulation reflects β-changes over time
- Example: AMOC weakening → pitch decreases

---

## 5. Interaction Design

### 5.1 VR Input Methods

**Supported Controllers:**
- Meta Quest Touch (1, 2, 3)
- Valve Index Controllers
- HP Reverb G2 Controllers
- Hand Tracking (Quest 2/3)

**Control Scheme:**

| Action | Controller | Hand Tracking |
|:-------|:-----------|:--------------|
| **Movement** | Left stick | Walk in place (experimental) |
| **Teleport** | Right stick forward | Point + pinch |
| **Rotate View** | Right stick left/right | Wrist rotation |
| **Select** | Trigger (index) | Pinch gesture |
| **Grab** | Grip buttons | Grab gesture |
| **Menu** | Y/B button | Palm facing self |

---

### 5.2 Navigation

**Teleportation:**
- Arc projection (parabolic)
- Valid surfaces: Floor, spiral platforms
- Invalid: Mid-air, outside bounds
- Visual: Blue arc (valid), red arc (invalid)

**Smooth Locomotion:** (Optional, for advanced users)
- Left stick: Move forward/back/strafe
- Right stick: Snap/smooth rotation
- Speed: 2 m/s (adjustable in settings)
- Comfort: Vignetting on movement (reduces motion sickness)

**Quick Travel:**
- Context menu on system orb → "Teleport Here"
- Instantly jump to system location
- Useful for large spiral (β>10 regions far from center)

---

### 5.3 System Orb Interactions

**Hover (Raycast from controller):**
- Orb highlights (scale 1.2×, glow +50%)
- Tooltip appears above orb
- Audio: Gentle chime (Field Type-specific)

**Click (Trigger press):**
- Detail panel opens (floating UI)
- Shows: Formal/Empirical/Poetic threads
- Buttons: [View Sigillin] [Show Trajectory] [Sonify]

**Grab (Grip button):**
- Orb detaches from spiral (optional feature)
- User can bring orb closer for inspection
- Release → orb returns to spiral position

---

### 5.4 Sigillin Terminal Interactions

**Open:**
- Click "View Sigillin" in system detail panel
- OR: Gaze at terminal hologram + trigger

**Navigate:**
- Tab buttons: YAML / JSON / MD
- Scroll: Left stick up/down OR hand swipe
- Search: Voice input (experimental) OR virtual keyboard

**Close:**
- X button (top right)
- OR: Walk away (>5m auto-close)

---

## 6. Technical Implementation

### 6.1 Unity Setup

**Version:** Unity 2022.3 LTS (recommended)

**Packages Required:**
- XR Plugin Management
- OpenXR Plugin
- XR Interaction Toolkit
- TextMeshPro (for UI)
- WebSocketSharp (for WebSocket client)

**Project Settings:**
- XR → OpenXR: Enable
- XR → Interaction Profiles: Quest Touch, Index, etc.
- Quality → Anti-Aliasing: 4x MSAA (VR optimized)
- Player → Color Space: Linear (better lighting)

**Scene Structure:**
```
VR_EmergenzHub (Scene)
├── XR Origin
│   ├── Camera Offset
│   │   └── Main Camera
│   ├── Left Controller
│   └── Right Controller
├── UTAC Spiral
│   ├── Spiral Mesh (procedural)
│   ├── System Orbs (dynamic, 15 instances)
│   └── Connections (glowing tubes)
├── Audio Manager
│   ├── AudioSource[0-14] (one per system)
│   └── Ambient (background hum)
├── UI Canvas (World Space)
│   ├── Tooltips (dynamic)
│   └── Sigillin Terminals (dynamic)
├── WebSocket Manager
└── Lighting
    ├── Directional Light (sun)
    └── Environment Skybox
```

---

### 6.2 WebSocket Bridge Implementation

**File:** `vr/websocket_bridge/bridge_server.py`

**Dependencies:**
```txt
fastapi==0.104.1
websockets==12.0
aiohttp==3.9.0
python-dotenv==1.0.0
pydantic==2.5.0
```

**Core Logic:**

```python
import asyncio
import json
import websockets
from typing import Set, Dict
import aiohttp

# Connected VR clients
clients: Set[websockets.WebSocketServerProtocol] = set()

# UTAC API base URL
API_URL = "http://localhost:8000"

async def fetch_system_data(system_id: str) -> Dict:
    """Fetch system data from UTAC API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/system/{system_id}") as resp:
            return await resp.json()

async def stream_updates(websocket):
    """Stream system updates to VR client."""
    # Register client
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "subscribe":
                # Client requests specific systems
                system_ids = data["system_ids"]

                # Fetch and send initial data
                for system_id in system_ids:
                    system_data = await fetch_system_data(system_id)
                    await websocket.send(json.dumps({
                        "type": "system_update",
                        "system_id": system_id,
                        "data": system_data
                    }))

            elif data["type"] == "ping":
                # Heartbeat
                await websocket.send(json.dumps({
                    "type": "pong",
                    "timestamp": data["timestamp"]
                }))

    finally:
        # Unregister client
        clients.remove(websocket)

async def main():
    async with websockets.serve(stream_updates, "localhost", 8765):
        print("✅ WebSocket Bridge running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

**Usage:**
```bash
cd vr/websocket_bridge
python3 bridge_server.py
```

---

### 6.3 Unity WebSocket Client

**File:** `Assets/Scripts/WebSocketClient.cs`

```csharp
using System;
using System.Collections;
using UnityEngine;
using WebSocketSharp;
using Newtonsoft.Json;

public class WebSocketClient : MonoBehaviour
{
    private WebSocket ws;
    public string serverUrl = "ws://localhost:8765";

    void Start()
    {
        ConnectToServer();
    }

    void ConnectToServer()
    {
        ws = new WebSocket(serverUrl);

        ws.OnOpen += (sender, e) =>
        {
            Debug.Log("✅ WebSocket connected");
            SubscribeToSystems();
        };

        ws.OnMessage += (sender, e) =>
        {
            HandleMessage(e.Data);
        };

        ws.OnError += (sender, e) =>
        {
            Debug.LogError($"❌ WebSocket error: {e.Message}");
        };

        ws.Connect();
    }

    void SubscribeToSystems()
    {
        var subscribeMsg = new
        {
            type = "subscribe",
            system_ids = new[] { "amoc", "urban_heat", "llm_emergence" }
        };

        ws.Send(JsonConvert.SerializeObject(subscribeMsg));
    }

    void HandleMessage(string jsonData)
    {
        var data = JsonConvert.DeserializeObject<WebSocketMessage>(jsonData);

        if (data.type == "system_update")
        {
            UpdateSystemOrb(data.system_id, data.data);
        }
    }

    void UpdateSystemOrb(string systemId, SystemData data)
    {
        // Find orb by systemId
        var orb = GameObject.Find($"Orb_{systemId}");
        if (orb != null)
        {
            var orbScript = orb.GetComponent<SystemOrb>();
            orbScript.UpdateData(data);
        }
    }

    void OnDestroy()
    {
        ws?.Close();
    }
}

[Serializable]
public class WebSocketMessage
{
    public string type;
    public string system_id;
    public SystemData data;
}

[Serializable]
public class SystemData
{
    public float beta;
    public float theta;
    public float R;
    public float sigma;
    public string field_type;
    public CREPScores crep_scores;
}

[Serializable]
public class CREPScores
{
    public float coherence;
    public float resilience;
    public float empathy;
    public float propagation;
}
```

---

## 7. Performance Optimization

### 7.1 Target Framerate

**VR Requirement:** Maintain 72 FPS (Quest 2/3) or 90 FPS (PCVR)

**Strategies:**
- **LOD (Level of Detail):** Distant orbs use low-poly meshes
- **Occlusion Culling:** Don't render hidden objects
- **Batching:** Combine spiral segments into single mesh
- **Texture Atlasing:** All Field Type colors in one texture

---

### 7.2 Draw Call Reduction

**Problem:** 15 system orbs = 15 draw calls

**Solution: GPU Instancing**
```csharp
Material orbMaterial = new Material(Shader.Find("UTAC/FieldTypeOrb"));
orbMaterial.enableInstancing = true;

// All orbs share same material → 1 draw call
```

**Expected:** 15 draw calls → 1-2 draw calls (per Field Type)

---

### 7.3 Audio Optimization

**Problem:** 15 AudioSources playing simultaneously

**Solution:**
- Max active sources: 5 (nearest to user)
- Distance-based culling (>20m = muted)
- Audio Mixer groups (reduce DSP overhead)

---

### 7.4 Profiling

**Unity Profiler Targets:**
- CPU: <10ms per frame (100 FPS headroom)
- GPU: <12ms per frame (83 FPS, safe buffer)
- Memory: <2GB (Quest 2 limit: 3GB)
- Draw Calls: <50 (VR optimized)

---

## 8. Future Extensions

### 8.1 Multi-User Collaboration (v0.3+)

**Tech:** Photon PUN 2 or Mirror Networking

**Features:**
- Avatars for human users
- Voice chat (spatial audio)
- Shared pointers (laser from controller)
- Synchronized Sigillin terminals

**Use Case:**
- Research team discusses AMOC collapse in VR
- One user points at orb, others see laser
- Shared annotation tools

---

### 8.2 Time-Series Playback (v0.3+)

**Concept:** Replay historical system evolution

**Implementation:**
- Load time-series data (β, θ, R over time)
- Animate orb position (β changes → radius changes)
- Audio pitch modulation (β increases → pitch rises)
- Timeline scrubber (UI control)

**Example:**
- AMOC 1950-2023: Watch β decrease as circulation weakens
- LLM training: Watch β increase as model scales

---

### 8.3 WebXR Port (v0.4+)

**Goal:** Run VR Hub in browser (no headset install)

**Tech:** Three.js + WebXR API

**Platforms:**
- Meta Quest Browser
- Wolvic (standalone VR browser)
- Desktop browsers (Windows Mixed Reality)

**Tradeoffs:**
- Easier access (no Unity install)
- Lower performance (JavaScript vs. C#)

---

### 8.4 AI-Guided Tours (Future)

**Concept:** AI avatars give narrated tours

**Implementation:**
- GPT-4 + Text-to-Speech (Eleven Labs)
- Avatar walks user through spiral
- Explains β-scaling, Field Types, Φ^(1/3) theory
- Responds to questions ("Why is urban heat so sharp?")

**Interaction:**
- User: "Explain Φ^(1/3) scaling"
- AI Avatar: *Walks to layers 0, 3, 6, 9*
- AI Avatar: "Notice how every third layer increases by Φ..."

---

## 9. Deployment

### 9.1 Standalone Quest Build

**Target:** Meta Quest 2/3

**Build Settings:**
- Platform: Android
- Texture Compression: ASTC
- Install Location: Automatic
- Minimum API Level: Android 10 (API 29)

**APK Size Target:** <200 MB

**Distribution:**
- SideQuest (developer channel)
- Meta App Lab (public beta)
- Meta Store (after polish)

---

### 9.2 PCVR Build

**Target:** SteamVR (Windows)

**Build Settings:**
- Platform: Windows x64
- Graphics API: DirectX 11
- Scripting Backend: IL2CPP (performance)

**Distribution:**
- Steam (future)
- Itch.io (early access)
- GitHub Releases (open-source)

---

## 10. Testing Plan

### 10.1 Unit Tests

**Unity Test Framework:**
- `SpiralGenerator_GeneratesCorrectPositions()`
- `FieldTypeShader_AppliesCorrectColors()`
- `WebSocketClient_HandlesReconnection()`

---

### 10.2 Integration Tests

**Scenarios:**
1. **WebSocket Bridge Stress Test**
   - Connect 10 VR clients simultaneously
   - Stream updates at 30 Hz
   - Expected: No dropped messages, <50ms latency

2. **Audio Spatialization Test**
   - Walk through spiral
   - Verify volume/pitch changes correctly
   - Expected: Smooth transitions, no pops

---

### 10.3 User Testing

**Target Users:**
- 5 researchers (complex systems background)
- 3 VR novices (accessibility check)
- 2 VR developers (technical feedback)

**Metrics:**
- Task completion time (find specific system)
- Comprehension test (explain Φ^(1/3) scaling)
- Comfort rating (1-10, motion sickness)
- Usability rating (1-10, ease of use)

---

## 11. Documentation Deliverables

| Document | Status | Description |
|:---------|:-------|:------------|
| `README.md` | ✅ Complete | Overview, quick start, roadmap |
| `vr_design_document.md` | ✅ Complete | This document (architecture) |
| `unity_setup_guide.md` | 🟡 Next | Step-by-step Unity installation |
| `websocket_protocol.md` | 🟡 Next | Message format specification |
| `field_type_colors.md` | 🟡 Next | Visual design guide |

---

## 12. Conclusion

The **UTAC VR Emergenz Hub** transforms abstract threshold theory into **embodied, spatial understanding**. By walking the Φ^(1/3) spiral, hearing the emergent symphony, and meeting Field Type avatars, users gain **intuitive insight** that complements analytical study.

**Foundation Status:** ✅ Complete (R=0.35/1.00)

**Next Steps:**
1. Unity Prototype (Phase 2, R→0.60)
2. WebSocket Bridge deployment
3. User testing with researchers

**Vision:**
> *"In VR, you don't just learn about thresholds — you cross them."*

---

**Version:** 1.0.0
**Status:** 🟡 Foundation (R=0.35)
**Authors:** Claude Code, Johann Römer, Aeon
**Date:** 2025-11-12
**Codex Entry:** v2-pr-0025 (pending)

*"Die Spirale atmet. Wir atmen mit."* 🌀🎧✨
