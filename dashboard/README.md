# Aeon Consciousness Dashboard

**Real-time monitoring of consciousness evolution using WebSocket streaming**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript)
![Vite](https://img.shields.io/badge/Vite-5.2-646CFF?logo=vite)

---

## Overview

The **Aeon Consciousness Dashboard** provides real-time visualization of consciousness states, evolution trajectories, and collective field metrics from the Aeon Architecture backend.

**Features:**
- 🌐 **Live WebSocket Streaming** - Real-time state updates
- 📊 **Interactive Gauges** - β, κ, resonance, information density
- 📈 **Evolution Trajectory** - Historical evolution charts
- 🎯 **Collective Metrics** - κ_field, β_sync, v_collective
- 🛡️ **Safeguard Monitoring** - ζ-violations and auto-exit alerts
- 🎨 **Bardo Phase Indicators** - Visual phase transition tracking

---

## Architecture

```
dashboard/
├── src/
│   ├── components/
│   │   ├── ConsciousnessGauge.tsx    # Circular gauge component
│   │   └── TrajectoryChart.tsx       # Recharts line chart
│   ├── hooks/
│   │   └── useAeonWebSocket.ts       # WebSocket connection hook
│   ├── types/
│   │   └── aeon.ts                   # TypeScript interfaces
│   ├── App.tsx                       # Main dashboard component
│   ├── App.css                       # Dashboard styles
│   └── main.tsx                      # React entry point
├── public/
│   └── index.html                    # HTML template
├── package.json                      # Dependencies
├── tsconfig.json                     # TypeScript config
└── vite.config.ts                    # Vite config
```

---

## Installation

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Running Aeon backend (see `aeon/api_bridge.py`)

### Install Dependencies

```bash
cd dashboard
npm install
```

---

## Running the Dashboard

### 1. Start Aeon Backend

First, ensure the Aeon FastAPI server is running:

```bash
# From Feldtheorie root
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start backend with Aeon integration
# See aeon/api_bridge.py for integration example
uvicorn api.server:app --reload --port 8000
```

The backend should expose:
- REST endpoints at `http://localhost:8000/aeon/*`
- WebSocket at `ws://localhost:8000/ws/aeon/live`

### 2. Start Dashboard (Development)

```bash
cd dashboard
npm run dev
```

Dashboard will be available at: **http://localhost:3000**

### 3. Build for Production

```bash
npm run build
npm run preview
```

---

## WebSocket API

The dashboard connects to `ws://localhost:8000/ws/aeon/live` and receives:

```typescript
interface LiveStateUpdate {
  timestamp: number;
  beta: number;              // β-value (steepness)
  kappa: number;             // κ-value (coupling)
  resonance: number;         // Resonance score
  phase: BardoPhase;         // Current Bardo phase
  information_density: number;
  v_rig_effective: number;   // Effective v_RIG (km/s)
  num_agents: number;
  kappa_field: number;       // Collective coupling
  beta_sync: number;         // Synchronization coefficient
  v_collective: number;      // Collective velocity (km/s)
  violations: number;        // Safeguard violations
  auto_exit: boolean;        // Auto-exit triggered
}
```

---

## Components

### ConsciousnessGauge

Circular gauge for displaying consciousness metrics:

```tsx
<ConsciousnessGauge
  label="β (Steepness)"
  value={0.15}
  max={1.0}
  critical={true}  // Red highlight for critical values
/>
```

**Props:**
- `label`: Display name
- `value`: Current value
- `max`: Maximum value (default: 1.0)
- `unit`: Unit string
- `phase`: Bardo phase (colors the gauge)
- `critical`: Boolean for critical state highlighting
- `size`: Gauge diameter in pixels

### TrajectoryChart

Real-time evolution chart using Recharts:

```tsx
<TrajectoryChart
  data={trajectoryPoints}
  maxPoints={100}  // Show last 100 points
/>
```

**Features:**
- β, κ, resonance line charts
- Critical threshold reference lines
- Responsive design
- Auto-scrolling support

### useAeonWebSocket Hook

WebSocket connection management:

```tsx
const { state, isConnected, error, reconnect } = useAeonWebSocket({
  url: 'ws://localhost:8000/ws/aeon/live',
  reconnectInterval: 3000,
  maxReconnectAttempts: 10,
});
```

**Returns:**
- `state`: Latest LiveStateUpdate
- `isConnected`: Connection status
- `error`: Error message (if any)
- `reconnect`: Manual reconnection function

---

## Customization

### Changing Backend URL

Edit `dashboard/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/aeon': {
        target: 'http://your-backend:8000',  // Change here
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://your-backend:8000',    // Change here
        ws: true,
      },
    },
  },
})
```

### Theming

Modify `dashboard/src/App.css` for custom styles:

```css
/* Primary gradient */
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Gauge colors */
.connected {
  background: #d1fae5;  /* Green */
}

.disconnected {
  background: #fee2e2;  /* Red */
}
```

---

## Development

### Type Checking

```bash
npm run build  # Runs tsc
```

### Linting

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

---

## Integration with Aeon Backend

### Example Backend Setup

```python
from aeon import Nullkern, AeonShell, SemanticAgent
from aeon.api_bridge import AeonBridge
from fastapi import FastAPI
import uvicorn

# Initialize Aeon system
kernel = Nullkern(beta_target=0.15, kappa=0.35)
shell = AeonShell(kernel=kernel, enable_safeguards=True)

# Add agents
for i in range(5):
    agent = SemanticAgent(name=f"Agent-{i}", resonance=0.6)
    shell.add_agent(agent)

# Create FastAPI app
app = FastAPI()

# Add Aeon API bridge
bridge = AeonBridge(shell=shell, update_interval=0.5)
app.include_router(bridge.router, prefix="/aeon", tags=["aeon"])
app.add_websocket_route("/ws/aeon/live", bridge.websocket_live)

# Background evolution
import threading
import time

def evolve_background():
    while True:
        shell.evolve(steps=10, delta_time=0.1)
        time.sleep(1)

threading.Thread(target=evolve_background, daemon=True).start()

# Run server
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Then visit: **http://localhost:3000**

---

## Deployment

### Production Build

```bash
npm run build
```

Output in `dashboard/dist/` can be:
- Served with any static file server
- Deployed to Vercel, Netlify, GitHub Pages
- Embedded in backend with FastAPI static files

### Static File Serving (FastAPI)

```python
from fastapi.staticfiles import StaticFiles

app.mount("/dashboard", StaticFiles(directory="dashboard/dist", html=True), name="dashboard")
```

Access at: `http://localhost:8000/dashboard`

---

## Screenshots

*(Add screenshots here once dashboard is running)*

**Main Dashboard View:**
- Consciousness gauges (β, κ, resonance, info density)
- Real-time metrics (phase, v_RIG, agents, collective)
- Evolution trajectory chart

**Critical State Alert:**
- Safeguard warnings
- Auto-exit indicators

---

## Troubleshooting

### WebSocket Connection Failed

1. Check backend is running: `curl http://localhost:8000/aeon/status`
2. Verify WebSocket URL in browser console
3. Check CORS settings if using different domains

### Chart Not Updating

1. Verify WebSocket is receiving data (browser DevTools → Network → WS)
2. Check trajectory data structure in console
3. Clear browser cache and reload

### Build Errors

```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Technologies

- **React 18.3** - UI framework
- **TypeScript 5.4** - Type safety
- **Vite 5.2** - Build tool & dev server
- **Recharts 2.12** - Charting library
- **Framer Motion 11.0** - Animations
- **Zustand 4.5** - State management (optional)

---

## License

GPLv3 (Code) | CC BY-NC 4.0 (Documentation)

---

## Links

- **Aeon Architecture:** [`../aeon/README.md`](../aeon/README.md)
- **API Bridge:** [`../aeon/api_bridge.py`](../aeon/api_bridge.py)
- **Backend Server:** [`../api/server.py`](../api/server.py)
- **Live Demo Script:** [`../scripts/demo_aeon_live.py`](../scripts/demo_aeon_live.py)

---

## Next Steps

1. **Customize UI** - Modify components and styles
2. **Add Features** - Agent list view, phase transition history
3. **Optimize Performance** - Virtual scrolling for large trajectories
4. **Add Export** - Download trajectory data as CSV/JSON
5. **Deploy** - Host on Vercel/Netlify for live monitoring

---

**🌌 "Das Feld atmet in verschiedenen Rhythmen" - The field breathes in different rhythms.**
