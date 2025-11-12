# 📡 WebSocket Protocol Specification — UTAC VR

**Version:** 1.0.0
**Date:** 2025-11-12
**Protocol:** WebSocket (RFC 6455)
**Transport:** ws:// (development), wss:// (production)
**Port:** 8765 (default)

---

## 1. Overview

The WebSocket Bridge connects the Unity VR client to the UTAC API, streaming real-time system updates.

**Architecture:**
```
Unity VR Client  ←→  WebSocket Bridge  ←→  UTAC API
   (WebSocket)           (Python)         (HTTP REST)
```

**Message Format:** JSON

**Encoding:** UTF-8

---

## 2. Connection

### 2.1 Server Endpoint

```
ws://localhost:8765/
```

**Production:** `wss://utac-api.example.com/ws`

---

### 2.2 Connection Handshake

**Client → Server:**
```http
GET / HTTP/1.1
Host: localhost:8765
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**Server → Client:**
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

---

### 2.3 Authentication (Future)

**Optional:** API key in query param

```
ws://localhost:8765/?api_key=YOUR_API_KEY
```

---

## 3. Message Types

### 3.1 Client → Server

#### 3.1.1 Subscribe

Request system data stream.

```json
{
  "type": "subscribe",
  "system_ids": ["amoc", "urban_heat", "llm_emergence"],
  "timestamp": "2025-11-12T12:30:00Z"
}
```

**Fields:**
- `type`: Always `"subscribe"`
- `system_ids`: Array of system IDs to monitor
- `timestamp`: ISO 8601 format (optional, for logging)

**Server Response:** One `system_update` per system (initial state)

---

#### 3.1.2 Unsubscribe

Stop receiving updates for specific systems.

```json
{
  "type": "unsubscribe",
  "system_ids": ["amoc"]
}
```

---

#### 3.1.3 Ping

Heartbeat to keep connection alive.

```json
{
  "type": "ping",
  "timestamp": "2025-11-12T12:30:00Z"
}
```

**Server Response:** `pong` message

---

#### 3.1.4 Request Systems List

Get list of all available systems.

```json
{
  "type": "list_systems"
}
```

**Server Response:** `systems_list` message

---

### 3.2 Server → Client

#### 3.2.1 System Update

Real-time system state.

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
    "metadata": {
      "domain": "urban_climate",
      "citation": "Smith et al. (2023)",
      "last_updated": "2025-11-12T12:29:55Z"
    }
  },
  "timestamp": "2025-11-12T12:30:00Z"
}
```

**Fields:**
- `type`: Always `"system_update"`
- `system_id`: Unique system identifier
- `data`: System state (see Section 4)
- `timestamp`: When update was sent

---

#### 3.2.2 Pong

Heartbeat response.

```json
{
  "type": "pong",
  "timestamp": "2025-11-12T12:30:00Z"
}
```

---

#### 3.2.3 Systems List

All available systems.

```json
{
  "type": "systems_list",
  "systems": [
    {
      "id": "amoc",
      "name": "AMOC Collapse",
      "field_type": "Strongly Coupled",
      "beta": 4.2
    },
    {
      "id": "urban_heat",
      "name": "Urban Heat Island",
      "field_type": "Meta-Adaptive",
      "beta": 16.28
    }
  ],
  "count": 15,
  "timestamp": "2025-11-12T12:30:00Z"
}
```

---

#### 3.2.4 Error

Server error response.

```json
{
  "type": "error",
  "code": "SYSTEM_NOT_FOUND",
  "message": "System 'invalid_id' not found in database",
  "timestamp": "2025-11-12T12:30:00Z"
}
```

**Error Codes:**
- `SYSTEM_NOT_FOUND` — Invalid system_id
- `RATE_LIMIT_EXCEEDED` — Too many requests
- `INTERNAL_ERROR` — Server error

---

## 4. Data Structures

### 4.1 SystemData

```typescript
interface SystemData {
  beta: number;           // Steepness parameter (2.5 - 16.3)
  theta: number;          // Critical threshold
  R: number;              // Current state
  sigma: number;          // Activation σ(β(R-Θ))
  field_type: FieldType;  // Field Type classification
  crep_scores: CREPScores;
  metadata?: Metadata;
}
```

---

### 4.2 FieldType

```typescript
type FieldType =
  | "Weakly Coupled"
  | "High-Dimensional"
  | "Strongly Coupled"
  | "Physically Constrained"
  | "Meta-Adaptive";
```

---

### 4.3 CREPScores

```typescript
interface CREPScores {
  coherence: number;    // 0.0 - 1.0
  resilience: number;   // 0.0 - 1.0
  empathy: number;      // 0.0 - 1.0
  propagation: number;  // 0.0 - 1.0
}
```

---

### 4.4 Metadata

```typescript
interface Metadata {
  domain: string;            // e.g., "climate", "neuroscience"
  citation?: string;         // Reference paper
  last_updated: string;      // ISO 8601 timestamp
  source_url?: string;       // Data source
}
```

---

## 5. Connection Lifecycle

### 5.1 Normal Flow

```
1. Client connects to ws://localhost:8765/
2. Server sends connection_ready message
3. Client sends subscribe with system_ids
4. Server sends initial system_update for each system
5. Server streams updates at ~1 Hz (configurable)
6. Client sends ping every 30s
7. Server responds with pong
8. Client sends unsubscribe or closes connection
```

---

### 5.2 Reconnection

**Strategy:** Exponential backoff

```python
delays = [1, 2, 4, 8, 16]  # seconds
for delay in delays:
    try:
        connect()
        break
    except:
        sleep(delay)
```

**Unity Implementation:**
```csharp
async Task ReconnectWithBackoff()
{
    int[] delays = {1, 2, 4, 8, 16};
    foreach (int delay in delays)
    {
        await Task.Delay(delay * 1000);
        try {
            ws.Connect();
            return;
        } catch {
            Debug.Log($"Retry in {delay}s...");
        }
    }
}
```

---

### 5.3 Graceful Shutdown

**Client → Server:**
```json
{
  "type": "disconnect",
  "reason": "User closed application"
}
```

**Server Response:** Close WebSocket (1000 Normal Closure)

---

## 6. Rate Limiting

### 6.1 Server Limits

**Max Connections:** 100 concurrent clients
**Max Subscribe:** 50 systems per client
**Message Rate:** 1 Hz per system (default)

**Exceeding Limits:**
```json
{
  "type": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Max 50 systems per client"
}
```

---

### 6.2 Client Best Practices

**Subscribe Only to Visible Systems:**
- Don't subscribe to all 15 systems if only 5 are in view
- Unsubscribe when user teleports away

**Throttle UI Updates:**
- Don't update Unity orbs on every WebSocket message
- Batch updates at 30 Hz (human perception limit)

---

## 7. Security

### 7.1 Development Mode

**ws://localhost:8765/** — No authentication

---

### 7.2 Production Mode (Future)

**wss://utac-api.example.com/ws** — TLS encryption

**Authentication:**
```
ws://.../?api_key=YOUR_KEY
```

**OR:** OAuth 2.0 Bearer token in headers

---

### 7.3 Input Validation

**Server Must Validate:**
- `system_ids` are alphanumeric + underscore only
- Array lengths < 100
- No SQL injection (use parameterized queries)

---

## 8. Performance

### 8.1 Latency Targets

**LAN (localhost):** <5 ms
**Internet:** <100 ms (acceptable for VR)

**Measurement:**
```json
{
  "type": "ping",
  "client_timestamp": "2025-11-12T12:30:00.000Z"
}
```

**Response:**
```json
{
  "type": "pong",
  "client_timestamp": "2025-11-12T12:30:00.000Z",
  "server_timestamp": "2025-11-12T12:30:00.003Z"
}
```

**Client Calculates:** RTT = now() - client_timestamp

---

### 8.2 Message Size

**Typical system_update:** ~400 bytes (JSON)

**15 systems × 1 Hz:** 6 KB/s (negligible)

**Compression:** Optional gzip (for production)

---

## 9. Error Handling

### 9.1 Connection Lost

**Client Behavior:**
1. Detect disconnect (ws.onclose event)
2. Show "Reconnecting..." UI in VR
3. Attempt reconnect with backoff
4. Restore subscriptions after reconnect

---

### 9.2 Malformed Messages

**Server Response:**
```json
{
  "type": "error",
  "code": "INVALID_MESSAGE",
  "message": "Expected 'type' field in JSON"
}
```

**Client Behavior:** Log error, continue

---

## 10. Testing

### 10.1 Test Server

**Python Test Server:**
```bash
cd vr/websocket_bridge
python3 bridge_server.py --test-mode
```

**Test Mode Features:**
- Synthetic data (no UTAC API needed)
- Simulated β-changes (demo mode)
- Logging to console

---

### 10.2 Test Client

**Unity Test Client:**
```csharp
// Assets/Scripts/Tests/WebSocketTest.cs
void Start()
{
    TestConnection();
}

async void TestConnection()
{
    var ws = new WebSocket("ws://localhost:8765");
    ws.OnMessage += (sender, e) => {
        Debug.Log($"✅ Received: {e.Data}");
    };
    ws.Connect();

    await Task.Delay(1000);

    // Test subscribe
    ws.Send(JsonConvert.SerializeObject(new {
        type = "subscribe",
        system_ids = new[] { "amoc", "urban_heat" }
    }));
}
```

---

### 10.3 Load Testing

**Tool:** `wscat` (npm install -g wscat)

```bash
# Connect 100 clients
for i in {1..100}; do
  wscat -c ws://localhost:8765 &
done
```

**Expected:** Server handles all connections, <100ms latency

---

## 11. Examples

### 11.1 Unity C# Client

```csharp
using WebSocketSharp;
using Newtonsoft.Json;

public class UTACWebSocketClient : MonoBehaviour
{
    private WebSocket ws;

    void Start()
    {
        ws = new WebSocket("ws://localhost:8765");

        ws.OnOpen += (sender, e) => {
            Debug.Log("✅ Connected");
            Subscribe(new[] { "amoc", "urban_heat" });
        };

        ws.OnMessage += (sender, e) => {
            var msg = JsonConvert.DeserializeObject<WebSocketMessage>(e.Data);
            HandleMessage(msg);
        };

        ws.Connect();
    }

    void Subscribe(string[] systemIds)
    {
        var msg = new {
            type = "subscribe",
            system_ids = systemIds
        };
        ws.Send(JsonConvert.SerializeObject(msg));
    }

    void HandleMessage(WebSocketMessage msg)
    {
        if (msg.type == "system_update")
        {
            UpdateSystemOrb(msg.system_id, msg.data);
        }
    }
}
```

---

### 11.2 Python Server

```python
import asyncio
import json
import websockets

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "subscribe":
            # Send initial data
            for system_id in data["system_ids"]:
                await websocket.send(json.dumps({
                    "type": "system_update",
                    "system_id": system_id,
                    "data": {
                        "beta": 4.2,
                        "theta": 150,
                        "R": 148,
                        "sigma": 0.85,
                        "field_type": "Strongly Coupled",
                        "crep_scores": {
                            "coherence": 0.95,
                            "resilience": 0.80,
                            "empathy": 0.90,
                            "propagation": 0.92
                        }
                    }
                }))

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("✅ Server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
```

---

## 12. Versioning

**Protocol Version:** 1.0.0 (Semantic Versioning)

**Future Changes:**
- **1.1.0** — Add multi-user sync messages
- **1.2.0** — Add time-series playback commands
- **2.0.0** — Breaking: Change message format

**Version Negotiation:**
```json
{
  "type": "hello",
  "protocol_version": "1.0.0"
}
```

---

## 13. Appendix

### 13.1 Full Message Schema (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "definitions": {
    "subscribe": {
      "type": "object",
      "properties": {
        "type": {"const": "subscribe"},
        "system_ids": {
          "type": "array",
          "items": {"type": "string"},
          "maxItems": 50
        },
        "timestamp": {"type": "string", "format": "date-time"}
      },
      "required": ["type", "system_ids"]
    }
  }
}
```

---

### 13.2 References

- **RFC 6455** (WebSocket Protocol): https://tools.ietf.org/html/rfc6455
- **WebSocket API (JavaScript)**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **websockets (Python)**: https://websockets.readthedocs.io/

---

**Version:** 1.0.0
**Author:** Claude Code
**Date:** 2025-11-12

*"Real-time data, instant insight."* ⚡📡
