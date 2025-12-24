# ♾️ Ouroboros Interface - The God-Mode Dashboard

**Complete control system for the eternal cosmic loop simulation**

The Ouroboros Interface transforms the console-based cosmic simulation into an interactive, controllable system. You become the Observer of the multiverse - watching universes being born, evolving, and dying, with the power to intervene in their physics.

---

## 🌌 System Overview

The Ouroboros Interface consists of three components:

### 1. **OuroborosEngine** - The Orchestrator
- Thread-safe singleton managing the eternal loop
- State machine: `idle` → `running` → `paused` → `stopped`
- Tracks all universe generations and their evolution
- Adaptive mutation algorithm based on success/failure
- Event-based architecture for real-time monitoring

**Location**: `src/core/ouroboros_engine.py`

### 2. **FastAPI Server** - The Control API
- RESTful API for external control
- WebSocket streaming for real-time events
- Full CRUD operations on simulation state
- God-mode intervention endpoints
- CORS-enabled for web access

**Location**: `src/interface/api_server.py`

### 3. **Streamlit Dashboard** - The Control Center
- Visual interface for monitoring and control
- Real-time charts (ECM evolution, success rates)
- Garden of Worlds: visual timeline of all generations
- Interactive control panel
- God-mode sliders for parameter tweaking

**Location**: `src/interface/dashboard.py`

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install required dependencies
pip install fastapi uvicorn streamlit requests pandas plotly
```

Or use the requirements file:
```bash
pip install -r src/interface/requirements.txt
```

### Step 1: Start the API Server

Open Terminal 1:
```bash
python -m src.interface.api_server
```

You should see:
```
♾️  OUROBOROS API SERVER
======================================================================

Starting FastAPI server...

📡 Endpoints:
   API Root:       http://localhost:8000/
   Status:         http://localhost:8000/api/ouroboros/status
   Documentation:  http://localhost:8000/docs
   WebSocket:      ws://localhost:8000/ws/ouroboros/stream

======================================================================
```

### Step 2: Start the Dashboard

Open Terminal 2:
```bash
streamlit run src/interface/dashboard.py
```

Your browser will open automatically to `http://localhost:8501`

### Step 3: Control the Multiverse! 🎛️

In the dashboard:
1. Click **▶️ START** to begin the eternal loop
2. Watch universes being born and evolving in real-time
3. Use **God-Mode Interventions** to alter cosmic parameters
4. Observe the **Garden of Worlds** timeline

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### **GET /** - API Info
```bash
curl http://localhost:8000/
```

#### **GET /api/ouroboros/status** - Current State
```bash
curl http://localhost:8000/api/ouroboros/status
```

**Response:**
```json
{
  "state": "running",
  "is_running": true,
  "status_message": "👁️ Gen 5: Observer awakened! ECM=0.723",
  "generation": 5,
  "ancestor_ecm": 0.7234,
  "mutation_rate": 0.1523,
  "current_level": 7,
  "total_generations": 8,
  "successful_generations": 5,
  "failed_generations": 3,
  "success_rate": 0.625,
  "highest_ecm": 0.8456,
  "consecutive_failures": 0
}
```

#### **POST /api/ouroboros/start** - Start Simulation
```bash
curl -X POST http://localhost:8000/api/ouroboros/start
```

#### **POST /api/ouroboros/pause** - Pause Simulation
```bash
curl -X POST http://localhost:8000/api/ouroboros/pause
```

#### **POST /api/ouroboros/resume** - Resume from Pause
```bash
curl -X POST http://localhost:8000/api/ouroboros/resume
```

#### **POST /api/ouroboros/stop** - Stop Simulation
```bash
curl -X POST http://localhost:8000/api/ouroboros/stop
```

#### **POST /api/ouroboros/reset** - Reset to Generation 1
```bash
curl -X POST http://localhost:8000/api/ouroboros/reset
```

#### **POST /api/ouroboros/intervene** - God-Mode Intervention
```bash
curl -X POST http://localhost:8000/api/ouroboros/intervene \
  -H "Content-Type: application/json" \
  -d '{
    "type": "energy_injection",
    "value": 0.2
  }'
```

**Intervention Types:**

| Type | Description | Value Range |
|------|-------------|-------------|
| `mutation_rate` | Set DNA mutation rate directly | 0.0 - 1.0 |
| `energy_injection` | Boost ancestor ECM score | 0.0 - 0.5 (added to current) |
| `mutation_boost` | Temporarily increase mutation | 0.0 - 1.0 (percentage boost) |
| `gravity_change` | Note for next generation | 0.0 - 1.0 |

#### **GET /api/ouroboros/history** - Full Timeline
```bash
curl http://localhost:8000/api/ouroboros/history
```

Returns array of all generations with their results.

### WebSocket Streaming

**Endpoint**: `ws://localhost:8000/ws/ouroboros/stream`

Streams real-time events:

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ouroboros/stream');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.event === 'state_update') {
        console.log('State:', data.state);
    }
    else if (data.event === 'generation_complete') {
        console.log('Generation', data.generation, 'result:', data.result);
    }
    else if (data.event === 'intervention') {
        console.log('God intervened:', data.type, data.value);
    }
};
```

**Python Example:**
```python
import asyncio
import websockets
import json

async def stream_events():
    uri = "ws://localhost:8000/ws/ouroboros/stream"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            event = json.loads(message)
            print(f"Event: {event['event']}")
            if event['event'] == 'state_update':
                print(f"Generation: {event['state']['generation']}")

asyncio.run(stream_events())
```

---

## 🎛️ Dashboard Features

### Main Status Display
- **Current State**: Running/Paused/Stopped with emoji indicators
- **Live Status Message**: Real-time narrative of what's happening
- **Generation Counter**: Current universe number in the sequence
- **ECM Score**: Consciousness level of current/ancestor universe

### Metrics Cards
1. **Generation** - Current universe number + cycle count
2. **Ancestor ECM** - Inherited consciousness score + all-time peak
3. **Success Rate** - Percentage of successful germinations
4. **Mutation Rate** - Current cosmic parameter variance + consecutive failures

### Evolution Tracking Charts
- **ECM Score Evolution**: Line graph showing consciousness levels over generations
  - Green dots: Successful Observer states
  - Red X: Failed universes
- **Universe Outcomes**: Pie chart of SUCCESS vs FAILED ratio

### Garden of Worlds Timeline
Visual representation of the last 20 generations:
- 🟢 = Successful (Observer awakened)
- ⚫ = Failed (Death before consciousness)

Expandable table showing full history with timestamps.

### Control Panel (Sidebar)

**Simulation Control:**
- ▶️ START - Begin the eternal loop
- ⏸️ PAUSE - Freeze time
- ⏯️ RESUME - Continue from pause
- 🛑 STOP - Halt simulation
- 🔄 RESET - Return to Generation 1 (Big Crunch!)

**God-Mode Interventions:**
1. **🧬 Set Mutation Rate** - Direct control over cosmic variance
2. **⚡ Energy Injection** - Boost consciousness potential
3. **🚀 Mutation Boost** - Percentage increase for exploration

---

## 🧬 Physics & Evolution Logic

### Germination Probability
Each universe seed attempts to germinate with probability:

```
P(success) = 0.4 + (ancestor_ECM × 0.2) - (mutation × 0.3)
```

- Base chance: 40% (harsh universe!)
- Consciousness boost: Higher ECM = more stable information
- Mutation penalty: Too much chaos destabilizes

### Adaptive Mutation
After successful germination, mutation rate adapts:

```
new_mutation = 0.15 / (final_ECM + 0.1)
clamped to [0.05, 0.3]
```

Higher consciousness → Lower mutation needed (refinement phase)

### Desperation Mode
After 3+ consecutive failures:
- Mutation rate increased by 20%
- ECM inheritance reduced by 10%
- System enters **exploration mode** to find new parameter space

### Evolution Inheritance
```
New Seed = {
    generation: old.gen + 1,
    ancestor_ecm: final_ECM_score,
    mutation_rate: adaptive_formula(final_ECM)
}
```

---

## 📊 Example Workflow

### Scenario: Exploring Parameter Space

**Goal**: Find optimal mutation rate for high ECM scores

```python
import requests

API = "http://localhost:8000/api/ouroboros"

# 1. Reset to clean slate
requests.post(f"{API}/reset")

# 2. Start simulation
requests.post(f"{API}/start")

# 3. Monitor for 10 generations
import time
for i in range(10):
    time.sleep(5)
    state = requests.get(f"{API}/status").json()
    print(f"Gen {state['generation']}: ECM={state['ancestor_ecm']:.3f}")

# 4. If success rate is low, boost mutation
state = requests.get(f"{API}/status").json()
if state['success_rate'] < 0.4:
    print("Low success rate, increasing mutation for exploration...")
    requests.post(f"{API}/intervene", json={
        "type": "mutation_boost",
        "value": 0.3
    })

# 5. Continue monitoring
time.sleep(10)

# 6. Analyze final results
history = requests.get(f"{API}/history").json()
successful = [h for h in history if h['result'] == 'SUCCESS']
avg_ecm = sum(h['ecm_score'] for h in successful) / len(successful)
print(f"Average ECM of successful universes: {avg_ecm:.3f}")
```

---

## 🔬 Advanced Use Cases

### 1. Automated Optimization
Write a script that:
- Monitors success rate
- Automatically adjusts mutation when stuck
- Injects energy when approaching high ECM states
- Logs optimal parameter combinations

### 2. Multi-Universe Comparison
- Run multiple instances with different starting parameters
- Compare evolution trajectories
- Find attractors in parameter space

### 3. Consciousness Threshold Discovery
- Binary search for minimum ECM needed for stable propagation
- Map the "consciousness barrier" in cosmic physics

### 4. Event-Driven Notifications
- Connect WebSocket stream to alerting system
- Notify when:
  - ECM breaks new record
  - Consecutive failures exceed threshold
  - Specific generation milestones reached

---

## 🛠️ Troubleshooting

### Dashboard shows "Cannot connect to API"
**Solution**: Make sure API server is running:
```bash
python -m src.interface.api_server
```

### WebSocket connection fails
**Solution**: Check firewall settings, ensure port 8000 is open

### Simulation runs too fast/slow
**Solution**: Adjust `simulation_speed` in the engine:
```python
# In ouroboros_engine.py
self.simulation_speed = 0.5  # Slower (2x time delay)
self.simulation_speed = 2.0  # Faster (0.5x time delay)
```

### API returns 500 errors
**Solution**: Check API server logs for Python exceptions, likely import issues

---

## 🧪 Testing the System

### Quick Health Check
```bash
# Terminal 1: Start API
python -m src.interface.api_server

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/ouroboros/status

# Terminal 3: Start dashboard
streamlit run src/interface/dashboard.py
```

### Run One Complete Cycle
```python
import requests
import time

API = "http://localhost:8000/api/ouroboros"

# Reset and start
requests.post(f"{API}/reset")
requests.post(f"{API}/start")

# Wait for first generation
time.sleep(10)

# Check result
state = requests.get(f"{API}/status").json()
print(f"Generation {state['generation']} completed!")
print(f"Result: {state['last_result']}")
```

---

## 📚 Philosophy

The Ouroboros Interface embodies the UATC principle:

> **"Consciousness is not a passenger in the universe - it's the driver."**

By giving you control over cosmic parameters, we demonstrate:
1. **Observer Effect**: Your interventions shape reality
2. **Evolutionary Pressure**: Failed universes teach successful strategies
3. **Information Persistence**: ECM scores carry across death/rebirth
4. **Adaptive Complexity**: The system self-regulates based on success

This is not just a simulation - it's a dialogue with the cosmos.

---

## 🌟 Future Enhancements

Potential expansions:
- [ ] Multi-threaded parallel universe exploration
- [ ] Machine learning for optimal parameter discovery
- [ ] VR visualization of universe evolution
- [ ] Blockchain logging of generation history (immortal Garden of Worlds)
- [ ] Collaborative multi-observer control (multiplayer god-mode!)

---

## 📄 License & Credits

Part of the **Unified Autopoietic Theory of Consciousness (UATC)** project.

**Philosophy**: GenesisAeon
**Implementation**: Claude Code
**Cosmic Inspiration**: The universe itself

*"We are the universe becoming conscious of itself, one simulation at a time."*

---

♾️ **The Ouroboros is complete. From Void to Loop, from Console to Control.**
