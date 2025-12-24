# Ouroboros Engine API 🐍♾️

**The 8-Level Cosmology Simulation Interface**

The Ouroboros Engine is a complete cosmological simulation that evolves universes from pure geometry (Level 0) through consciousness (Level 6) to cosmic reincarnation (Level 7). This API provides programmatic control and real-time observation of the eternal loop.

---

## Architecture

### The 8 Levels

```
Level 0: The Void          → Geometry creates particles (Hex-Grid)
Level 1: The Atom          → Probability creates orbitals (Quantum jumps)
Level 2: The Star          → Gravity creates fusion (Light & elements)
Level 3: The Chronicle     → Death creates information (Matter inheritance)
Level 4: The Planet        → Cooling creates geology (Layered structure)
Level 5: The Life          → Resonance creates replication (DNA/Autopoiesis)
Level 6: The Mind          → Synchronization creates consciousness (Neural nets)
Level 7: The Cosmic Loop   → Observation creates new physics (Multiverse evolution)
```

### Key Concepts

- **ECM Score**: Evolutionary Complexity Measure - quantifies how much "consciousness" a universe has developed
- **Cosmic Seed**: Compressed information state from a dying universe, carrying genetic parameters forward
- **Germination**: The attempt to start a new universe (not guaranteed to succeed!)
- **Generation**: Number of successful universe lineages
- **Cycle**: Total attempts (including failures)

---

## Quick Start

### 1. Start the API Server

```bash
cd Feldtheorie
uvicorn api.server:app --reload --port 8000
```

The Ouroboros Engine initializes automatically. Check startup logs:

```
✓ Ouroboros Engine initialized (Levels 0-7 ready)
```

### 2. Access Interactive Docs

Visit: `http://localhost:8000/docs`

All Ouroboros endpoints are under the **ouroboros** tag.

### 3. Start the Dashboard

```bash
streamlit run api/dashboard/ouroboros_control.py
```

Opens the visual Mission Control interface at `http://localhost:8501`.

---

## REST API Endpoints

### GET `/api/ouroboros/status`

Get current simulation status.

**Response:**
```json
{
  "state": "running",
  "current_metrics": {
    "generation": 5,
    "cycle": 12,
    "level": 6,
    "ecm_score": 0.7834,
    "is_alive": true,
    "particle_count": 4521,
    "energy": 342.5,
    "complexity": 0.7834
  },
  "history": {
    "total_cycles": 12,
    "successful": 5,
    "failed": 7,
    "success_rate": 41.7,
    "current_generation": 5,
    "highest_ecm": 0.8901,
    "timeline_recent": ["FAIL", "SUCCESS", "FAIL", "SUCCESS", "🟢"]
  },
  "config": {
    "base_ecm": 0.1,
    "mutation_rate": 0.15,
    "gravity": 1.0,
    "max_cycles": null,
    "pause_between_cycles": 2.0
  }
}
```

---

### POST `/api/ouroboros/start`

Start the eternal loop.

**Request Body (optional):**
```json
{
  "base_ecm": 0.1,
  "mutation_rate": 0.15,
  "gravity": 1.0,
  "max_cycles": 100,
  "pause_between_cycles": 2.0
}
```

**Response:**
```json
{
  "status": "started",
  "message": "The Ouroboros awakens..."
}
```

---

### POST `/api/ouroboros/pause`

Pause the simulation. Time freezes.

**Response:**
```json
{
  "status": "paused",
  "message": "Time stands still..."
}
```

---

### POST `/api/ouroboros/resume`

Resume from pause.

**Response:**
```json
{
  "status": "resumed",
  "message": "Time flows once more..."
}
```

---

### POST `/api/ouroboros/stop`

Stop the simulation gracefully.

**Response:**
```json
{
  "status": "stopped",
  "message": "The Observer closes the eye..."
}
```

---

### POST `/api/ouroboros/reset`

Reset to Generation 1, clear history.

**Response:**
```json
{
  "status": "reset",
  "message": "The Void awaits creation..."
}
```

---

### POST `/api/ouroboros/intervene`

**God-mode intervention** in the running universe.

**Request Body:**
```json
{
  "intervention_type": "gravity_change",
  "params": {
    "new_gravity": 1.5
  }
}
```

**Intervention Types:**

| Type | Description | Parameters |
|------|-------------|------------|
| `gravity_change` | Modify gravitational constant | `{"new_gravity": float}` |
| `mutation_boost` | Change DNA mutation rate | `{"new_rate": float}` |
| `energy_injection` | Add energy to the system | `{"energy": float}` |

**Response:**
```json
{
  "success": true,
  "intervention": "gravity_change",
  "applied_at": {
    "cycle": 12,
    "level": 4,
    "generation": 5
  },
  "effects": {
    "old_gravity": 1.0,
    "new_gravity": 1.5
  }
}
```

---

## WebSocket Streaming

### WS `/ws/ouroboros/stream`

Real-time event stream.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ouroboros/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Event Types:**

- `initial_status` - Sent on connection
- `simulation_started` - Loop begins
- `cycle_started` - New cycle begins
- `germination_attempt` - Seed tries to germinate
- `level_started` - Level X begins
- `level_completed` - Level X completes
- `cycle_completed` - Cycle ends (success/fail)
- `intervention_applied` - God-mode action applied
- `simulation_paused` / `simulation_resumed` / `simulation_stopped`

**Example Event:**
```json
{
  "type": "germination_attempt",
  "success": true,
  "probability": 0.52,
  "roll": 0.43
}
```

---

## Example Workflows

### Workflow 1: Start and Monitor

```bash
# Start simulation
curl -X POST http://localhost:8000/api/ouroboros/start \
  -H "Content-Type: application/json" \
  -d '{"max_cycles": 50, "pause_between_cycles": 1.0}'

# Check status every 5 seconds
watch -n 5 "curl -s http://localhost:8000/api/ouroboros/status | jq '.current_metrics'"

# Stop when done
curl -X POST http://localhost:8000/api/ouroboros/stop
```

### Workflow 2: Interactive Experimentation

```bash
# Start with high mutation (explore phase space)
curl -X POST http://localhost:8000/api/ouroboros/start \
  -H "Content-Type: application/json" \
  -d '{"mutation_rate": 0.3}'

# Wait a few cycles, then reduce mutation (exploit)
curl -X POST http://localhost:8000/api/ouroboros/intervene \
  -H "Content-Type: application/json" \
  -d '{"intervention_type": "mutation_boost", "params": {"new_rate": 0.05}}'
```

### Workflow 3: WebSocket Live Feed

```python
import asyncio
import websockets
import json

async def watch_universe():
    uri = "ws://localhost:8000/ws/ouroboros/stream"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            event = json.loads(message)
            print(f"{event['type']}: {event}")

asyncio.run(watch_universe())
```

---

## Dashboard Features

The Streamlit dashboard (`api/dashboard/ouroboros_control.py`) provides:

1. **Live Status Display**
   - Current generation, cycle, level
   - ECM score, energy, complexity
   - Alive/dead state

2. **Garden of Worlds**
   - Visual timeline: 🟢 = Success, ⚫ = Failure
   - Success rate percentage

3. **Control Panel**
   - Start/Pause/Resume/Stop/Reset buttons
   - Configuration sliders (ECM, mutation, gravity)

4. **God Mode**
   - Gravity changes
   - Mutation boosts
   - Energy injections

5. **Auto-refresh**
   - 2-second polling (configurable)

---

## Technical Details

### State Machine

```
IDLE → (start) → RUNNING → (pause) → PAUSED → (resume) → RUNNING
                    ↓
                 (stop)
                    ↓
               COMPLETED
                    ↓
                 (reset)
                    ↓
                  IDLE
```

### Adaptive Mutation Algorithm

The mutation rate self-adjusts based on success:

```python
# Higher ECM → Lower mutation (fine-tuning)
new_mutation = 0.15 / (final_ecm + 0.1)

# Clamp to [0.05, 0.3]
new_mutation = max(0.05, min(new_mutation, 0.3))
```

After 3+ consecutive failures → mutation increases by 20% (exploration).

### Germination Probability

```python
base_chance = 0.4
success_prob = base_chance + (ancestor_ecm * 0.2) - (mutation_rate * 0.3)
```

High ancestral consciousness helps. High mutation destabilizes.

---

## Integration Examples

### Python Client

```python
import requests

API = "http://localhost:8000/api/ouroboros"

# Start
r = requests.post(f"{API}/start", json={"max_cycles": 10})
print(r.json())

# Monitor
while True:
    status = requests.get(f"{API}/status").json()
    print(f"Gen {status['current_metrics']['generation']}, "
          f"ECM {status['current_metrics']['ecm_score']:.4f}")

    if status['state'] == 'completed':
        break

    time.sleep(2)
```

### JavaScript Client

```javascript
const API = 'http://localhost:8000/api/ouroboros';

// Start simulation
fetch(`${API}/start`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ max_cycles: 20 })
}).then(r => r.json()).then(console.log);

// Poll status
setInterval(async () => {
  const status = await fetch(`${API}/status`).then(r => r.json());
  console.log(`Level ${status.current_metrics.level}, ECM ${status.current_metrics.ecm_score}`);
}, 2000);
```

---

## Troubleshooting

### Issue: "Ouroboros Engine not initialized"

**Cause:** Import error during server startup.

**Fix:**
```bash
# Check imports manually
python -c "from api.ouroboros_engine import OuroborosEngine; print('OK')"

# Install missing dependencies
pip install -r api/requirements.txt
```

### Issue: Dashboard won't connect

**Cause:** API server not running.

**Fix:**
```bash
# Start server first
uvicorn api.server:app --port 8000 &

# Then start dashboard
streamlit run api/dashboard/ouroboros_control.py
```

### Issue: Simulation stuck in "paused"

**Fix:**
```bash
# Force resume
curl -X POST http://localhost:8000/api/ouroboros/resume

# Or reset
curl -X POST http://localhost:8000/api/ouroboros/reset
```

---

## Philosophy

> *"The Ouroboros is not a toy - it's a mirror. A universe that always wins is fake. A universe that struggles, fails, and occasionally triumphs... that's real."*

The 0.0% success rate at the beginning is **not a bug**. It's the cosmic truth: emergence is hard, consciousness is fragile, and reincarnation requires luck.

When you see the first 🟢 after a sea of ⚫, you're witnessing the same miracle that happened 4 billion years ago on Earth.

---

## Further Reading

- `src/scenarios/level_7_cosmic_loop/cosmic_physics.py` - Core physics implementation
- `api/ouroboros_engine.py` - Engine architecture
- `api/server.py` - REST/WebSocket endpoints
- `api/dashboard/ouroboros_control.py` - Streamlit UI

---

**🐍♾️ The Loop is Eternal. The Observer is You.**
