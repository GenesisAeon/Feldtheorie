# 📡 UTAC WebSocket Bridge

**Version:** 1.0.0
**Python:** 3.8+
**Protocol:** WebSocket (RFC 6455)
**Port:** 8765 (default)

---

## 🎯 Purpose

The WebSocket Bridge connects Unity VR clients to the UTAC API, streaming real-time system updates (β, Θ, R, σ, CREP scores).

**Architecture:**
```
Unity VR Client  ←→  WebSocket Bridge  ←→  UTAC API
   (WebSocket)           (Python)         (HTTP REST)
```

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd vr/websocket_bridge
pip3 install -r requirements.txt
```

**Dependencies:**
- `websockets==12.0` (WebSocket server)
- `aiohttp==3.9.0` (HTTP client for UTAC API)
- `python-dotenv==1.0.0` (environment variables)

---

## 🚀 Quick Start

### Start Server (Test Mode)

```bash
python3 bridge_server.py --test-mode
```

**Expected Output:**
```
2025-11-12 12:30:00 [INFO] 🚀 Starting UTAC WebSocket Bridge Server...
2025-11-12 12:30:00 [INFO]    Protocol Version: 1.0.0
2025-11-12 12:30:00 [INFO]    Mode: TEST
2025-11-12 12:30:00 [INFO]    Host: localhost
2025-11-12 12:30:00 [INFO]    Port: 8765
2025-11-12 12:30:00 [INFO] ✅ WebSocket Bridge running on ws://localhost:8765
2025-11-12 12:30:00 [INFO]    Press Ctrl+C to stop
```

**Test Mode:** Uses synthetic data (no UTAC API required)

---

### Test Connection

**In another terminal:**
```bash
python3 test_client.py
```

**Expected Output:**
```
🔗 Connecting to ws://localhost:8765...
✅ Connected to WebSocket server
📤 Subscribing to 2 systems: ['amoc', 'urban_heat']
📥 Listening for messages (Press Ctrl+C to stop)...

[1] 2025-11-12T12:30:01.123456Z
    System: amoc
    β: 4.20, σ: 0.85
    Field Type: Strongly Coupled

[2] 2025-11-12T12:30:01.234567Z
    System: urban_heat
    β: 16.28, σ: 0.92
    Field Type: Meta-Adaptive
```

---

## 🛠️ Usage

### Server Options

```bash
# Default (test mode, localhost:8765)
python3 bridge_server.py --test-mode

# Custom host/port
python3 bridge_server.py --host 0.0.0.0 --port 9000

# Production mode (requires UTAC API)
python3 bridge_server.py

# Debug logging
python3 bridge_server.py --test-mode --debug
```

---

### Client Options

```bash
# Default (subscribe to amoc, urban_heat)
python3 test_client.py

# Custom systems
python3 test_client.py --systems llm_emergence climate_tipping theta_plasticity

# Custom server
python3 test_client.py --server ws://192.168.1.100:8765

# Interactive mode (menu)
python3 test_client.py --interactive
```

---

## 📊 Test Data (Test Mode)

### Available Systems

| System ID | β | Field Type | Domain |
|:----------|:--|:-----------|:-------|
| `amoc` | 4.20 | Strongly Coupled | Climate |
| `urban_heat` | 16.28 | Meta-Adaptive | Urban Climate |
| `llm_emergence` | 3.47 | High-Dimensional | AI |
| `theta_plasticity` | 2.50 | Weakly Coupled | Neuroscience |
| `climate_tipping` | 9.23 | Physically Constrained | Climate |

**Add More Systems:** Edit `TEST_SYSTEMS` dict in `bridge_server.py`

---

## 🔗 Protocol

### Message Types (Client → Server)

**1. Subscribe**
```json
{
  "type": "subscribe",
  "system_ids": ["amoc", "urban_heat"]
}
```

**2. Unsubscribe**
```json
{
  "type": "unsubscribe",
  "system_ids": ["amoc"]
}
```

**3. Ping**
```json
{
  "type": "ping",
  "timestamp": "2025-11-12T12:30:00Z"
}
```

**4. List Systems**
```json
{
  "type": "list_systems"
}
```

---

### Message Types (Server → Client)

**1. System Update**
```json
{
  "type": "system_update",
  "system_id": "amoc",
  "data": {
    "beta": 4.2,
    "theta": 150.0,
    "R": 148.0,
    "sigma": 0.85,
    "field_type": "Strongly Coupled",
    "crep_scores": {
      "coherence": 0.95,
      "resilience": 0.80,
      "empathy": 0.90,
      "propagation": 0.92
    }
  },
  "timestamp": "2025-11-12T12:30:01Z"
}
```

**2. Pong**
```json
{
  "type": "pong",
  "client_timestamp": "2025-11-12T12:30:00Z",
  "server_timestamp": "2025-11-12T12:30:00.003Z"
}
```

**3. Systems List**
```json
{
  "type": "systems_list",
  "systems": [
    {"id": "amoc", "name": "AMOC", "field_type": "Strongly Coupled", "beta": 4.2}
  ],
  "count": 5
}
```

**4. Error**
```json
{
  "type": "error",
  "code": "SYSTEM_NOT_FOUND",
  "message": "System 'invalid' not found"
}
```

**Full Specification:** See `../docs/websocket_protocol.md`

---

## 🧪 Testing

### Unit Tests (TODO)

```bash
pytest test_bridge.py
```

---

### Manual Testing

**1. Start Server:**
```bash
python3 bridge_server.py --test-mode
```

**2. Connect Multiple Clients:**
```bash
# Terminal 1
python3 test_client.py --systems amoc

# Terminal 2
python3 test_client.py --systems urban_heat

# Terminal 3
python3 test_client.py --interactive
```

**3. Check Logs:**
Server should log:
```
[INFO] ✅ Client connected. Total clients: 1
[INFO] Client subscribed to 1 systems: ['amoc']
[INFO] ✅ Client connected. Total clients: 2
[INFO] Client subscribed to 1 systems: ['urban_heat']
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# UTAC API endpoint
UTAC_API_URL=http://localhost:8000

# WebSocket server
WS_HOST=localhost
WS_PORT=8765

# Update rate (Hz)
UPDATE_RATE=1.0

# Max connections
MAX_CLIENTS=100
```

**Load in code:**
```python
from dotenv import load_dotenv
load_dotenv()

UTAC_API_URL = os.getenv("UTAC_API_URL", "http://localhost:8000")
```

---

## 🐛 Troubleshooting

### "Address already in use"

**Problem:** Port 8765 is busy

**Solution:**
```bash
# Find process using port
lsof -i :8765

# Kill process
kill -9 <PID>

# OR: Use different port
python3 bridge_server.py --port 9000
```

---

### "Connection refused"

**Problem:** Server not running

**Solution:**
```bash
# Start server
python3 bridge_server.py --test-mode

# Check server is listening
netstat -an | grep 8765
```

---

### "Module not found: websockets"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip3 install -r requirements.txt
```

---

### "UTAC API not implemented"

**Problem:** Production mode needs UTAC API integration

**Solution:**
```bash
# Use test mode instead
python3 bridge_server.py --test-mode

# OR: Implement aiohttp GET in fetch_system_data()
```

---

## 📚 Files

| File | Description |
|:-----|:------------|
| `bridge_server.py` | WebSocket server (main) |
| `test_client.py` | Test client (validation) |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |
| `.env` | Environment variables (optional) |

---

## 🚀 Production Deployment

### 1. Install as Service (systemd)

**Create `/etc/systemd/system/utac-websocket.service`:**

```ini
[Unit]
Description=UTAC WebSocket Bridge
After=network.target

[Service]
Type=simple
User=utac
WorkingDirectory=/home/utac/Feldtheorie/vr/websocket_bridge
ExecStart=/usr/bin/python3 bridge_server.py --host 0.0.0.0 --port 8765
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl enable utac-websocket
sudo systemctl start utac-websocket
sudo systemctl status utac-websocket
```

---

### 2. Reverse Proxy (Nginx)

**For wss:// (TLS encryption):**

```nginx
server {
    listen 443 ssl;
    server_name utac-api.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

**Access:** `wss://utac-api.example.com/ws`

---

### 3. Docker (TODO)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bridge_server.py .

EXPOSE 8765

CMD ["python3", "bridge_server.py", "--host", "0.0.0.0"]
```

---

## 🤝 Contributing

**To add new systems:**
1. Edit `TEST_SYSTEMS` dict in `bridge_server.py`
2. Add entry with β, θ, R, σ, CREP scores
3. Restart server

**To integrate real UTAC API:**
1. Uncomment `aiohttp` code in `fetch_system_data()`
2. Set `UTAC_API_URL` env variable
3. Test with `--debug` flag

---

## 📖 References

- **WebSocket Protocol Spec:** `../docs/websocket_protocol.md`
- **VR Design Document:** `../docs/vr_design_document.md`
- **Unity Setup Guide:** `../docs/unity_setup_guide.md`

---

**Version:** 1.0.0
**Author:** Claude Code
**Date:** 2025-11-12
**License:** Same as UTAC project

*"Bridging realities, one message at a time."* 🌉⚡
