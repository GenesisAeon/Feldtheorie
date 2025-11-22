# Phase 4 System Architecture - Technical Specification

**Document Type:** Technical Architecture
**Phase:** 4 (Real-Time Monitoring)
**Version:** 1.0.0
**Last Updated:** 2025-11-14

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL DATA SOURCES                     │
├───────────┬───────────┬──────────┬──────────┬──────────┬─────────┤
│  GRACE/   │  RAPID-   │  NOAA    │   WHO    │  FRED    │  TCGA   │
│  GRACE-FO │  MOCHA    │  OISST   │  Disease │ Economic │ Cancer  │
│  (WAIS)   │  (AMOC)   │ (Coral)  │ (Measles)│(Finance) │ (Cancer)│
└─────┬─────┴─────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬────┘
      │           │          │          │          │          │
      v           v          v          v          v          v
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Adapters (Python)                                   │  │
│  │  - grace_wais_adapter.py      (Ice mass balance)         │  │
│  │  - rapid_amoc_adapter.py      (AMOC strength)            │  │
│  │  - oisst_coral_adapter.py     (SST, DHW)                 │  │
│  │  - who_measles_adapter.py     (Case counts, coverage)    │  │
│  │  - fred_finance_adapter.py    (VIX, spreads)             │  │
│  │  - tcga_cancer_adapter.py     (Immune infiltrate)        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Features:                                                       │
│  - Hourly cron jobs (configurable frequency)                    │
│  - Exponential backoff retry (network failures)                 │
│  - Data validation (schema checks, outlier detection)           │
│  - Logging (successful/failed ingestions)                       │
│  - Metadata tracking (source, timestamp, version)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYSIS & COMPUTATION LAYER                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  UTAC Analysis Pipeline (Python)                          │  │
│  │                                                            │  │
│  │  1. β-Estimation:                                         │  │
│  │     - fit_utac_beta.py (sigmoid, ensemble, CIs)          │  │
│  │     - bootstrap_beta.py (n=1000, percentile method)      │  │
│  │     Output: beta_fits_v3.json                            │  │
│  │                                                            │  │
│  │  2. Early Warning Signals:                                │  │
│  │     - calculate_ews.py (variance, AR(1), spectral)       │  │
│  │     - kendall_tau_trends.py (significance testing)       │  │
│  │     Output: ews_signals.json                             │  │
│  │                                                            │  │
│  │  3. CREP Metrics:                                         │  │
│  │     - crep_metrics.py (coherence, resonance, emergence)  │  │
│  │     - crep_poetics_generator.py (narrative synthesis)    │  │
│  │     Output: crep_metrics_v3.json                         │  │
│  │                                                            │  │
│  │  4. Coupled Dynamics:                                     │  │
│  │     - coupled_utac_model.py (cascade simulation)         │  │
│  │     - coupling_matrix.yaml (w_ij coefficients)           │  │
│  │     Output: coupled_activation.json                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TimescaleDB (PostgreSQL Extension)                       │  │
│  │                                                            │  │
│  │  Tables:                                                   │  │
│  │  - system_states         (current state snapshots)       │  │
│  │  - timeseries_data       (historical observations)       │  │
│  │  - ews_signals           (variance, AR(1), spectral)     │  │
│  │  - crep_metrics          (coherence, resonance, ...)     │  │
│  │  - alerts                (σ-tier notifications)          │  │
│  │  - audit_log             (data ingestions, errors)       │  │
│  │                                                            │  │
│  │  Optimizations:                                           │  │
│  │  - Hypertables (automatic partitioning by time)          │  │
│  │  - Continuous aggregates (pre-computed rollups)          │  │
│  │  - Compression (90% reduction on old data)               │  │
│  │  - Retention policies (12 months granular, 5 years agg)  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  REST API (Node.js + Express + TypeScript)               │  │
│  │                                                            │  │
│  │  Endpoints:                                                │  │
│  │  GET  /api/systems                (list all)             │  │
│  │  GET  /api/systems/:id/state      (current state)        │  │
│  │  GET  /api/systems/:id/timeseries (historical)           │  │
│  │  GET  /api/systems/:id/ews        (early warnings)       │  │
│  │  GET  /api/systems/:id/crep       (CREP metrics)         │  │
│  │  GET  /api/systems/:id/trilayer   (documentation)        │  │
│  │  POST /api/systems/:id/simulate   (scenario testing)     │  │
│  │  GET  /api/alerts                 (active alerts)        │  │
│  │  POST /api/alerts/:id/acknowledge (mark handled)         │  │
│  │  GET  /api/coupling               (cascade matrix)       │  │
│  │  WS   /ws/systems                 (real-time updates)    │  │
│  │                                                            │  │
│  │  Features:                                                 │  │
│  │  - Authentication (JWT, API keys)                         │  │
│  │  - Rate limiting (100 req/min per user)                  │  │
│  │  - CORS (configurable origins)                           │  │
│  │  - Caching (Redis, 5-minute TTL)                         │  │
│  │  - WebSockets (live updates, sub/pub)                    │  │
│  │  - OpenAPI 3.0 spec (auto-generated docs)                │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           v
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Dashboard (React + TypeScript)                           │  │
│  │                                                            │  │
│  │  Pages:                                                    │  │
│  │  1. Overview Dashboard                                    │  │
│  │     - 6 System Cards (status, σ, distance to tipping)    │  │
│  │     - Global σ-status (R̄, Θ, β aggregated)              │  │
│  │     - Active alerts banner (top notification bar)        │  │
│  │                                                            │  │
│  │  2. System Detail View (one per system)                  │  │
│  │     - Trilayer display (Formal/Empirical/Poetic)         │  │
│  │     - Time series charts (D3.js)                         │  │
│  │     - EWS panel (variance, AR(1), spectral)              │  │
│  │     - CREP gauges (circular progress bars)               │  │
│  │     - Data source links (transparency)                   │  │
│  │                                                            │  │
│  │  3. β-Landscape 3D View                                  │  │
│  │     - Three.js scene (X=system, Y=β, Z=distance)         │  │
│  │     - Interactive (rotate, zoom, tooltips)               │  │
│  │     - Color by urgency (red/yellow/green/blue)           │  │
│  │                                                            │  │
│  │  4. Sigillin Symbolic View                               │  │
│  │     - SVG-based geometric sigils                         │  │
│  │     - Pulsation (urgency-driven animation)               │  │
│  │     - Coupling network graph (edges = w_ij)              │  │
│  │                                                            │  │
│  │  5. Alert History & Log                                  │  │
│  │     - Chronological list (filterable by system/severity) │  │
│  │     - Acknowledgment status                              │  │
│  │     - Export (CSV, JSON)                                 │  │
│  │                                                            │  │
│  │  6. Documentation Hub                                     │  │
│  │     - Embedded trilayer docs (markdown rendering)        │  │
│  │     - Shadow-Sigillin (risk transparency)                │  │
│  │     - Methodology (UTAC v3.0 overview)                   │  │
│  │     - Data provenance (sources, licensing)               │  │
│  │                                                            │  │
│  │  Components:                                               │  │
│  │  - SystemCard (overview, CREP)                           │  │
│  │  - TimeSeriesChart (D3.js line/area)                     │  │
│  │  - BetaLandscape3D (Three.js scene)                      │  │
│  │  - EWSPanel (variance, AR(1), spectral)                  │  │
│  │  - CREPGauge (circular progress)                         │  │
│  │  - SigillinCanvas (SVG + animation)                      │  │
│  │  - AlertBanner (top notification)                        │  │
│  │  - TrilayerModal (embedded docs)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & ALERTING                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  EWS Monitoring Pipeline (Python + Scheduler)            │  │
│  │                                                            │  │
│  │  Hourly Tasks:                                            │  │
│  │  1. Fetch latest data (all 6 systems)                    │  │
│  │  2. Calculate EWS (rolling 180-day window)               │  │
│  │  3. Check alert thresholds:                              │  │
│  │     - Variance increase > 20% → WATCH                    │  │
│  │     - AR(1) increase > 15% → WARNING                     │  │
│  │     - Distance to tipping < 10% → ALERT                  │  │
│  │  4. Generate CREP metrics                                │  │
│  │  5. Update database (system_states, ews_signals, crep)   │  │
│  │  6. Emit alerts (if thresholds crossed)                  │  │
│  │  7. Log execution (audit_log)                            │  │
│  │                                                            │  │
│  │  Alert Channels:                                          │  │
│  │  - Dashboard (WebSocket push)                            │  │
│  │  - Email (subscriber list)                               │  │
│  │  - RSS feed (utac-monitor.org/alerts.rss)               │  │
│  │  - API webhook (external integrations)                   │  │
│  │  - Twitter/X (opt-in, public alerts)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  System Monitoring (Prometheus + Grafana)                │  │
│  │                                                            │  │
│  │  Metrics:                                                  │  │
│  │  - API response time (p50, p95, p99)                     │  │
│  │  - Database query latency                                │  │
│  │  - Ingestion success rate (%)                            │  │
│  │  - WebSocket connections (concurrent)                    │  │
│  │  - Dashboard page load time                              │  │
│  │  - Error rate (5xx responses)                            │  │
│  │  - Uptime (%)                                             │  │
│  │                                                            │  │
│  │  Alerts (internal):                                       │  │
│  │  - API p95 > 500ms → Slack notification                  │  │
│  │  - Error rate > 1% → PagerDuty escalation                │  │
│  │  - Uptime < 99.5% → Email to devops                      │  │
│  │  - Disk usage > 80% → Auto-scale trigger                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌──────────────┐
│ GRACE/NASA   │
│ (Ice mass)   │
└──────┬───────┘
       │
       v
┌──────────────────┐      ┌──────────────────┐
│ grace_adapter.py │─────>│ TimescaleDB      │
│ - Fetch          │      │ timeseries_data  │
│ - Transform      │      └────────┬─────────┘
│ - Validate       │               │
└──────────────────┘               │
                                   v
┌───────────────────┐      ┌──────────────────┐
│ fit_utac_beta.py  │<─────│ Query data       │
│ - Sigmoid fit     │      │ (180-day window) │
│ - Bootstrap CI    │      └──────────────────┘
│ - ΔAIC calc       │
└────────┬──────────┘
         │
         v
┌──────────────────┐      ┌──────────────────┐
│ beta_fits.json   │─────>│ TimescaleDB      │
│ {                │      │ system_states    │
│   β: 13.5,       │      └────────┬─────────┘
│   CI: [12,15],   │               │
│   ΔAIC: 18.2     │               │
│ }                │               │
└──────────────────┘               │
                                   │
┌──────────────────┐               │
│ calculate_ews.py │<──────────────┘
│ - Variance       │
│ - AR(1)          │
│ - Spectral       │
└────────┬─────────┘
         │
         v
┌──────────────────┐      ┌──────────────────┐
│ ews_signals.json │─────>│ TimescaleDB      │
│ {                │      │ ews_signals      │
│   variance: +5.7%│      └────────┬─────────┘
│   ar1: +0.5%,    │               │
│   spectral: 13.15│               │
│ }                │               │
└──────────────────┘               │
                                   │
┌──────────────────┐               │
│ crep_metrics.py  │<──────────────┘
│ - Coherence      │
│ - Resonance      │
│ - Emergence      │
│ - Poetics        │
└────────┬─────────┘
         │
         v
┌──────────────────┐      ┌──────────────────┐
│ crep_metrics.json│─────>│ TimescaleDB      │
│ {                │      │ crep_metrics     │
│   coherence: 0.78│      └────────┬─────────┘
│   resonance: 0.30│               │
│   emergence: 0.68│               │
│   poetics: "..." │               │
│ }                │               │
└──────────────────┘               │
                                   │
                                   v
┌─────────────────────────────────────────┐
│ REST API (Express)                      │
│ GET /api/systems/wais/state            │
│ → Returns: β, EWS, CREP, current state │
└────────┬────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────┐
│ Dashboard (React)                       │
│ - Fetch data via API                   │
│ - Render charts (D3.js)                │
│ - Display CREP gauges                  │
│ - Show trilayer docs                   │
│ - WebSocket for live updates           │
└─────────────────────────────────────────┘
```

---

## 🗄️ Database Schema (TimescaleDB)

### Table: `system_states`
Stores current state snapshots for each system.

```sql
CREATE TABLE system_states (
  system_id TEXT NOT NULL,             -- 'wais', 'amoc', 'coral', etc.
  timestamp TIMESTAMPTZ NOT NULL,      -- State snapshot time
  state_json JSONB NOT NULL,           -- Full state (flexible schema)
  PRIMARY KEY (system_id, timestamp)
);

-- Convert to hypertable (TimescaleDB partitioning)
SELECT create_hypertable('system_states', 'timestamp');

-- Index for fast queries
CREATE INDEX idx_system_states_id ON system_states(system_id);

-- Retention policy (keep 12 months granular, 5 years aggregated)
SELECT add_retention_policy('system_states', INTERVAL '12 months');
```

**Example Row:**
```json
{
  "system_id": "wais",
  "timestamp": "2025-11-14T12:00:00Z",
  "state_json": {
    "mass_balance_Gt": -2202912.87,
    "mass_loss_rate_Gt_per_year": -1592.5,
    "temperature_anomaly_C": 1.172,
    "distance_to_tipping": 0.2188,
    "beta": 13.5,
    "theta": 1.5,
    "sigma": 0.78
  }
}
```

### Table: `timeseries_data`
Historical observations for all variables.

```sql
CREATE TABLE timeseries_data (
  system_id TEXT NOT NULL,
  variable TEXT NOT NULL,              -- 'mass_balance', 'temperature', etc.
  timestamp TIMESTAMPTZ NOT NULL,
  value NUMERIC NOT NULL,
  metadata JSONB,                      -- Source, quality flags, etc.
  PRIMARY KEY (system_id, variable, timestamp)
);

SELECT create_hypertable('timeseries_data', 'timestamp');

-- Compression (90% reduction on data >1 month old)
ALTER TABLE timeseries_data SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'system_id,variable'
);

SELECT add_compression_policy('timeseries_data', INTERVAL '1 month');
```

### Table: `ews_signals`
Early warning signals (variance, AR(1), spectral).

```sql
CREATE TABLE ews_signals (
  system_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  variance NUMERIC,
  variance_change_percent NUMERIC,     -- Relative to baseline
  ar1 NUMERIC,
  ar1_change_percent NUMERIC,
  spectral_reddening NUMERIC,
  kendall_tau_variance NUMERIC,        -- Significance test
  kendall_tau_ar1 NUMERIC,
  p_value_variance NUMERIC,
  p_value_ar1 NUMERIC,
  PRIMARY KEY (system_id, timestamp)
);

SELECT create_hypertable('ews_signals', 'timestamp');
```

### Table: `crep_metrics`
CREP metrics (Coherence, Resonance, Emergence, Poetics).

```sql
CREATE TABLE crep_metrics (
  system_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  coherence NUMERIC NOT NULL CHECK (coherence BETWEEN 0 AND 1),
  resonance NUMERIC NOT NULL CHECK (resonance BETWEEN 0 AND 1),
  emergence NUMERIC NOT NULL CHECK (emergence BETWEEN 0 AND 1),
  poetics TEXT NOT NULL,               -- Human-readable narrative
  PRIMARY KEY (system_id, timestamp)
);

SELECT create_hypertable('crep_metrics', 'timestamp');
```

### Table: `alerts`
System alerts (σ-tier messaging).

```sql
CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  system_id TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('MONITORING', 'WATCH', 'WARNING', 'ALERT')),
  message TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_by TEXT,
  acknowledged_at TIMESTAMPTZ
);

-- Index for active alerts
CREATE INDEX idx_alerts_active ON alerts(acknowledged) WHERE acknowledged = FALSE;
```

### Table: `audit_log`
Data ingestion and error tracking.

```sql
CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  operation TEXT NOT NULL,             -- 'data_ingestion', 'ews_calculation', etc.
  system_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAILURE', 'PARTIAL')),
  details JSONB,                       -- Error messages, retry count, etc.
  duration_ms INTEGER
);

SELECT create_hypertable('audit_log', 'timestamp');
SELECT add_retention_policy('audit_log', INTERVAL '6 months');
```

---

## 🌐 API Specification (OpenAPI 3.0)

### Core Endpoints

#### `GET /api/systems`
List all monitored systems.

**Response:**
```json
[
  {
    "id": "wais",
    "name": "West Antarctic Ice Sheet",
    "utac_type": "Type-2: Thermodynamic",
    "beta": 13.5,
    "status": "AT_TIPPING_POINT",
    "urgency": "CRITICAL",
    "last_updated": "2025-11-14T12:00:00Z"
  },
  // ... 5 more systems
]
```

#### `GET /api/systems/:id/state`
Get current system state.

**Parameters:**
- `id` (path): System identifier (`wais`, `amoc`, etc.)

**Response:**
```json
{
  "system_id": "wais",
  "timestamp": "2025-11-14T12:00:00Z",
  "beta": 13.5,
  "theta": 1.5,
  "sigma": 0.78,
  "distance_to_tipping": 0.2188,
  "mass_balance_Gt": -2202912.87,
  "temperature_anomaly_C": 1.172,
  "ews": {
    "variance_change": 0.057,
    "ar1_change": 0.005,
    "spectral_reddening": 13.15
  },
  "crep": {
    "coherence": 0.78,
    "resonance": 0.30,
    "emergence": 0.68,
    "poetics": "The ice remembers millennia, but forgets in decades."
  }
}
```

#### `GET /api/systems/:id/timeseries`
Get historical time series data.

**Parameters:**
- `id` (path): System identifier
- `variable` (query): Variable name (`mass_balance`, `temperature`, etc.)
- `start` (query): ISO timestamp (optional, default: -30 days)
- `end` (query): ISO timestamp (optional, default: now)
- `resolution` (query): `hourly`, `daily`, `monthly` (default: `daily`)

**Response:**
```json
{
  "system_id": "wais",
  "variable": "mass_balance",
  "resolution": "daily",
  "data": [
    {"timestamp": "2024-01-01T00:00:00Z", "value": -2100000},
    {"timestamp": "2024-01-02T00:00:00Z", "value": -2100500},
    // ... more points
  ],
  "metadata": {
    "source": "NASA GRACE/GRACE-FO",
    "units": "Gigatonnes",
    "count": 274
  }
}
```

#### `GET /api/systems/:id/ews`
Get early warning signals.

**Response:**
```json
{
  "system_id": "wais",
  "timestamp": "2025-11-14T12:00:00Z",
  "variance": {
    "current": 6.28e6,
    "baseline": 5.94e6,
    "change_percent": 5.7,
    "kendall_tau": 0.290,
    "p_value": 0.001,
    "status": "SIGNIFICANT"
  },
  "ar1": {
    "current": 0.359,
    "baseline": 0.357,
    "change_percent": 0.5,
    "kendall_tau": -0.012,
    "p_value": 0.84,
    "status": "NOT_SIGNIFICANT"
  },
  "spectral_reddening": 13.15
}
```

#### `POST /api/systems/:id/simulate`
Run scenario simulation (coupled dynamics).

**Request Body:**
```json
{
  "scenario": "warming_1.5C",
  "parameters": {
    "temperature_anomaly": 1.5,
    "co2_ppm": 450
  },
  "time_horizon_years": 50
}
```

**Response:**
```json
{
  "system_id": "wais",
  "scenario": "warming_1.5C",
  "results": {
    "time_to_tipping_years": 45,
    "uncertainty_years": 23,
    "final_sigma": 0.95,
    "trajectory": [
      {"year": 2025, "sigma": 0.78},
      {"year": 2030, "sigma": 0.82},
      // ... more points
    ]
  }
}
```

#### `GET /api/alerts`
Get active alerts.

**Query Parameters:**
- `severity` (optional): Filter by severity (`MONITORING`, `WATCH`, `WARNING`, `ALERT`)
- `acknowledged` (optional): Filter by acknowledgment status (`true`, `false`)

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "system_id": "wais",
      "severity": "WATCH",
      "message": "Variance increased +5.7% (approaching threshold)",
      "timestamp": "2025-11-14T12:00:00Z",
      "acknowledged": false
    },
    // ... more alerts
  ],
  "count": 3
}
```

#### `WebSocket /ws/systems`
Real-time updates (subscribe/publish).

**Client subscribes:**
```json
{
  "action": "subscribe",
  "systems": ["wais", "amoc"]
}
```

**Server pushes updates:**
```json
{
  "event": "state_update",
  "system_id": "wais",
  "timestamp": "2025-11-14T12:05:00Z",
  "data": {
    "sigma": 0.78,
    "distance_to_tipping": 0.2188
  }
}
```

---

## 🎨 Frontend Component Architecture

```
src/
├── components/
│   ├── SystemCard/
│   │   ├── SystemCard.tsx         (Overview card with CREP)
│   │   ├── SystemCard.module.css
│   │   └── SystemCard.test.tsx
│   │
│   ├── TimeSeriesChart/
│   │   ├── TimeSeriesChart.tsx    (D3.js line chart)
│   │   ├── TimeSeriesChart.module.css
│   │   └── TimeSeriesChart.test.tsx
│   │
│   ├── BetaLandscape3D/
│   │   ├── BetaLandscape3D.tsx    (Three.js scene)
│   │   ├── BetaLandscape3D.module.css
│   │   └── BetaLandscape3D.test.tsx
│   │
│   ├── EWSPanel/
│   │   ├── EWSPanel.tsx           (Variance, AR(1), spectral)
│   │   ├── EWSPanel.module.css
│   │   └── EWSPanel.test.tsx
│   │
│   ├── CREPGauge/
│   │   ├── CREPGauge.tsx          (Circular progress bar)
│   │   ├── CREPGauge.module.css
│   │   └── CREPGauge.test.tsx
│   │
│   ├── SigillinCanvas/
│   │   ├── SigillinCanvas.tsx     (SVG geometric sigils)
│   │   ├── SigillinCanvas.module.css
│   │   └── SigillinCanvas.test.tsx
│   │
│   ├── AlertBanner/
│   │   ├── AlertBanner.tsx        (Top notification bar)
│   │   ├── AlertBanner.module.css
│   │   └── AlertBanner.test.tsx
│   │
│   └── TrilayerModal/
│       ├── TrilayerModal.tsx      (Embedded markdown docs)
│       ├── TrilayerModal.module.css
│       └── TrilayerModal.test.tsx
│
├── pages/
│   ├── Dashboard.tsx              (Overview)
│   ├── SystemDetail.tsx           (System-specific)
│   ├── BetaLandscape.tsx          (3D view)
│   ├── SigillinView.tsx           (Symbolic)
│   ├── AlertHistory.tsx           (Log)
│   └── Documentation.tsx          (Trilayer docs hub)
│
├── hooks/
│   ├── useSystemState.ts          (Fetch system state)
│   ├── useTimeSeries.ts           (Fetch time series)
│   ├── useEWS.ts                  (Fetch EWS)
│   ├── useCREP.ts                 (Fetch CREP)
│   ├── useWebSocket.ts            (Real-time updates)
│   └── useAlerts.ts               (Fetch alerts)
│
├── services/
│   ├── api.ts                     (Axios client)
│   ├── websocket.ts               (WebSocket client)
│   └── formatters.ts              (Data formatting utils)
│
├── types/
│   ├── system.ts                  (System types)
│   ├── ews.ts                     (EWS types)
│   ├── crep.ts                    (CREP types)
│   └── alert.ts                   (Alert types)
│
└── utils/
    ├── calculations.ts            (Client-side UTAC calculations)
    ├── colors.ts                  (Color scales, urgency mapping)
    └── validation.ts              (Input validation)
```

---

## 🔐 Security Architecture

### Authentication & Authorization

**JWT-Based Authentication:**
```typescript
// Login flow
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "***"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123",
    "email": "user@example.com",
    "role": "scientist"
  }
}

// Subsequent requests
GET /api/systems/wais/state
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Key for External Integrations:**
```
GET /api/systems/wais/state
X-API-Key: sk_live_abc123...
```

**Rate Limiting:**
- Authenticated users: 1000 requests/hour
- API keys: 10,000 requests/hour
- Anonymous: 100 requests/hour

### Data Security

**Encryption:**
- TLS 1.3 (HTTPS only, HTTP → HTTPS redirect)
- Database connections encrypted (SSL/TLS)
- Secrets stored in environment variables (not code)

**Input Validation:**
- All API inputs validated (JSON schema)
- SQL injection prevention (parameterized queries)
- XSS prevention (React auto-escaping, DOMPurify for markdown)

**CORS Configuration:**
```typescript
app.use(cors({
  origin: ['https://utac-monitor.org', 'https://dashboard.utac-monitor.org'],
  credentials: true
}));
```

---

## 📈 Performance Optimization

### Backend

**Database:**
- TimescaleDB hypertables (automatic time-based partitioning)
- Continuous aggregates (pre-computed hourly/daily rollups)
- Compression (90% reduction on data >1 month old)
- Indexing (B-tree on system_id, timestamp)

**API:**
- Redis caching (5-minute TTL for frequently accessed data)
- Response compression (gzip, Brotli)
- Connection pooling (pg-pool, max 20 connections)
- Query optimization (EXPLAIN ANALYZE for slow queries)

### Frontend

**React:**
- Code splitting (dynamic imports for routes)
- Lazy loading (images, charts rendered on-demand)
- Memoization (useMemo, React.memo for expensive calculations)
- Virtual scrolling (large time series lists)

**Charts:**
- D3.js optimization (canvas for >1000 points, SVG for <1000)
- Three.js LOD (level of detail, reduce polygons at distance)
- Debouncing (resize, scroll events)
- Web Workers (heavy calculations off main thread)

**Assets:**
- Minification (Terser for JS, cssnano for CSS)
- Image optimization (WebP with PNG fallback)
- CDN (CloudFlare for static assets)
- Font subsetting (only load used glyphs)

---

## 🔄 Deployment Pipeline (CI/CD)

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm install
          npm run test
          npm run test:integration

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build frontend
        run: |
          cd dashboard
          npm install
          npm run build
      - name: Build API
        run: |
          cd api
          npm install
          npm run build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_KEY }}
          aws-region: us-east-1
      - name: Deploy API (ECS)
        run: |
          aws ecs update-service --cluster utac --service api --force-new-deployment
      - name: Deploy Dashboard (S3 + CloudFront)
        run: |
          aws s3 sync dashboard/dist s3://utac-dashboard
          aws cloudfront create-invalidation --distribution-id E123 --paths "/*"
      - name: Run migrations
        run: |
          npm run migrate:up
```

---

## 📊 Monitoring & Observability

### Metrics (Prometheus)

```yaml
# Key metrics to track

# API Performance
http_request_duration_seconds{endpoint="/api/systems/:id/state", quantile="0.95"}
http_requests_total{endpoint="/api/systems", status="200"}
http_requests_total{endpoint="/api/systems", status="500"}

# Database Performance
pg_query_duration_seconds{query="SELECT * FROM system_states"}
pg_connections_active
pg_connections_idle

# Data Ingestion
data_ingestion_success_total{system="wais"}
data_ingestion_failure_total{system="wais"}
data_ingestion_duration_seconds{system="wais"}

# EWS Calculation
ews_calculation_duration_seconds{system="wais"}
ews_alerts_triggered_total{severity="WARNING"}

# Frontend
page_load_duration_seconds{page="dashboard"}
websocket_connections_active
```

### Dashboards (Grafana)

**Dashboard 1: API Health**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Active connections

**Dashboard 2: Data Pipeline**
- Ingestion success rate (%)
- Ingestion latency (seconds)
- Database write throughput (rows/s)
- EWS calculation lag (minutes)

**Dashboard 3: User Engagement**
- Active users (concurrent)
- Page views (per page)
- Session duration (minutes)
- Alert subscriptions (count)

---

**Document Version:** 1.0.0
**Status:** ✅ Complete - Technical Specification Ready
**Next Review:** Week 1 Architecture Review (with team)
