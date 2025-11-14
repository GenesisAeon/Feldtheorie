# Phase 4: Real-Time Monitoring & Dashboard - Roadmap

**Phase:** 4 (Real-Time Monitoring)
**Status:** 🔄 **READY TO ACTIVATE**
**Prerequisites:** ✅ Phase 3 Complete (TypeScript Bridge + CREP + Trilayer + Shadow-Sigillin)
**Timeline:** 8-12 weeks
**Budget Estimate:** $25,000-40,000 (development + data subscriptions)
**Last Updated:** 2025-11-14

---

## 🎯 Mission Statement

**Transform UTAC V3 from research prototype to operational early warning system.**

Deploy real-time monitoring dashboard that:
1. **Tracks 6 critical threshold systems** (WAIS, AMOC, Coral, Measles, Finance, Cancer)
2. **Provides early warning signals** (variance, AR(1), spectral reddening)
3. **Visualizes β-landscape** (interactive 3D, Sigillin symbolic layer)
4. **Generates CREP metrics** (Coherence, Resonance, Emergence, Poetics)
5. **Alerts on threshold proximity** (σ-tier messaging protocol)
6. **Enables public engagement** (multilingual, accessible, transparent)

**Target Audience:**
- Climate scientists (WAIS, AMOC, Coral)
- Public health officials (Measles)
- Financial regulators (systemic risk monitoring)
- General public (education, awareness)
- Policymakers (evidence-based decision support)

---

## 📊 Current State Assessment

### What We Have (Phase 3 Complete)

**Code:**
- ✅ 6 TypeScript system implementations (~2,300 lines)
- ✅ Python data adapters (mock data, ~800 lines)
- ✅ β-estimation pipeline (sigmoid_fit.py, bootstrap_beta.py)
- ✅ EWS calculation (calculate_ews.py)
- ✅ CREP generation (all 6 systems)
- ✅ Integration tests (WAIS: 5/5 passing)

**Documentation:**
- ✅ 6 Trilayer docs (Formal/Empirical/Poetic, ~5,300 lines)
- ✅ Shadow-Sigillin risk analysis (570 lines YAML)
- ✅ Integration guide (500 lines)
- ✅ V3 Integration Analysis

**Data:**
- ⚠️ Mock data only (CRITICAL GAP)
- ✅ Data schemas defined
- ✅ Metadata templates ready

### What We Need (Phase 4 Gaps)

**CRITICAL:**
1. ❗ **Real data integration** (GRACE, RAPID, OISST, WHO, FRED)
2. ❗ **API credentials** (NASA, NOAA, WHO, commercial providers)
3. ❗ **Data pipeline** (ETL, storage, update frequency)

**HIGH:**
4. **Dashboard frontend** (React + TypeScript)
5. **Backend API** (Node.js + Express)
6. **Database** (TimescaleDB for time series)
7. **Monitoring pipeline** (hourly updates, EWS calculation)
8. **Alert system** (σ-tier messaging, notifications)

**MEDIUM:**
9. **Visualization library** (D3.js, Three.js for 3D)
10. **Sigillin symbolic layer** (SVG generation, animation)
11. **Communication protocol** (messaging guidelines, ethical framing)

---

## 🗓️ Phase 4 Timeline (12 Weeks)

### **Week 1-2: Foundation & Real Data Integration**

**Goals:**
- Integrate real data sources (GRACE, RAPID, OISST)
- Replace mock data in all adapters
- Re-run β-fits, validate ΔAIC improvements

**Deliverables:**
1. GRACE adapter with NASA JPL Tellus API
2. RAPID-MOCHA adapter with UK Met Office data
3. OISST adapter with NOAA data
4. Updated `beta_fits_v3.json` with real β-estimates
5. Validation report (compare mock vs. real fits)

**Team:**
- **Primary:** ChatGPT-Codex (Python data pipeline)
- **Support:** Claude (validation scripts)
- **Review:** Gemini (β-calculation verification)

**Success Criteria:**
- [ ] WAIS β improves: 3.42 → 13.5 ± 1.5
- [ ] AMOC ΔAIC improves: 25.15 → >30
- [ ] Coral β validated: 7.5 ± 1.5 (real DHW data)
- [ ] All 6 systems have real data feeds
- [ ] Integration tests pass with real data

**Blockers:**
- API credentials (NASA Earthdata, NOAA)
- Data access agreements (some sources restricted)
- Bandwidth (GRACE data = ~500 MB/month)

---

### **Week 3-4: Bootstrap CIs & Statistical Validation**

**Goals:**
- Run bootstrap (n=1000) for all 6 systems
- Calculate robust confidence intervals
- Sensitivity analysis (parameter perturbations)

**Deliverables:**
1. `beta_fits_v3_bootstrap.json` (all systems, 95% CI)
2. Sensitivity analysis report (±10% parameter variations)
3. ΔAIC comparison table (logistic vs. linear vs. exponential)
4. Publication-ready statistical tables

**Team:**
- **Primary:** Gemini (statistical validation)
- **Support:** Claude (interpretation, write-up)

**Success Criteria:**
- [ ] Bootstrap CIs < 15% relative width (tight)
- [ ] All systems: ΔAIC > 10 (strong preference)
- [ ] Sensitivity: β stable to ±10% parameter changes
- [ ] Peer-review ready statistics

**Blockers:**
- Computational time (1000 bootstrap × 6 systems = ~12 hours)
- Memory (large time series for AMOC)

---

### **Week 5-6: Backend Architecture & Database**

**Goals:**
- Design RESTful API architecture
- Set up TimescaleDB for time series storage
- Implement data ingestion pipeline (ETL)

**Deliverables:**
1. **API Endpoints:**
   - `GET /api/systems` (list all 6 systems)
   - `GET /api/systems/:id/state` (current state)
   - `GET /api/systems/:id/timeseries` (historical data)
   - `GET /api/systems/:id/ews` (early warning signals)
   - `GET /api/systems/:id/crep` (CREP metrics)
   - `POST /api/systems/:id/simulate` (scenario testing)

2. **Database Schema:**
   ```sql
   -- System states (current)
   CREATE TABLE system_states (
     system_id TEXT,
     timestamp TIMESTAMPTZ,
     state_json JSONB,
     PRIMARY KEY (system_id, timestamp)
   );

   -- Time series data
   CREATE TABLE timeseries_data (
     system_id TEXT,
     variable TEXT,
     timestamp TIMESTAMPTZ,
     value NUMERIC,
     metadata JSONB,
     PRIMARY KEY (system_id, variable, timestamp)
   );

   -- Early warning signals
   CREATE TABLE ews_signals (
     system_id TEXT,
     timestamp TIMESTAMPTZ,
     variance NUMERIC,
     ar1 NUMERIC,
     spectral_reddening NUMERIC,
     kendall_tau_variance NUMERIC,
     kendall_tau_ar1 NUMERIC,
     PRIMARY KEY (system_id, timestamp)
   );

   -- CREP metrics
   CREATE TABLE crep_metrics (
     system_id TEXT,
     timestamp TIMESTAMPTZ,
     coherence NUMERIC,
     resonance NUMERIC,
     emergence NUMERIC,
     poetics TEXT,
     PRIMARY KEY (system_id, timestamp)
   );

   -- Alerts
   CREATE TABLE alerts (
     id SERIAL PRIMARY KEY,
     system_id TEXT,
     severity TEXT, -- 'MONITORING', 'WATCH', 'WARNING', 'ALERT'
     message TEXT,
     timestamp TIMESTAMPTZ,
     acknowledged BOOLEAN DEFAULT FALSE
   );
   ```

3. **Data Ingestion Pipeline:**
   - Hourly cron jobs for each data source
   - Error handling + retry logic (exponential backoff)
   - Data validation (schema checks, outlier detection)
   - Logging (successful/failed ingestions)

4. **API Documentation (OpenAPI 3.0 spec)**

**Team:**
- **Primary:** Mistral (backend architecture)
- **Support:** ChatGPT-Codex (implementation)
- **Testing:** Claude (integration tests)

**Success Criteria:**
- [ ] All 6 endpoints operational
- [ ] Database stores 6+ months historical data
- [ ] API response time < 200ms (p95)
- [ ] 99.9% uptime (monitoring with Prometheus)
- [ ] OpenAPI spec published

**Blockers:**
- Hosting costs ($50-100/month for database)
- TimescaleDB learning curve

---

### **Week 7-8: Frontend Dashboard (MVP)**

**Goals:**
- Build React dashboard with core visualizations
- Implement UTAC β-landscape 3D view
- System cards with real-time CREP metrics

**Deliverables:**

1. **Dashboard Pages:**

   **A. Overview Dashboard**
   ```
   ┌─────────────────────────────────────────────────┐
   │  UTAC V3 - Real-Time Threshold Monitoring       │
   ├─────────────────────────────────────────────────┤
   │                                                 │
   │  Global σ-Status: 0.68 (R̄=0.73, Θ=0.66, β=4.8)│
   │                                                 │
   │  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
   │  │  WAIS   │  │  AMOC   │  │  Coral  │        │
   │  │  🔴     │  │  🔴     │  │  🔴     │        │
   │  │  21.9%  │  │  48%    │  │  TIPPED │        │
   │  │  to tip │  │  to bif │  │         │        │
   │  └─────────┘  └─────────┘  └─────────┘        │
   │                                                 │
   │  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
   │  │ Measles │  │ Finance │  │ Cancer  │        │
   │  │  🟡     │  │  🟢     │  │  🔵     │        │
   │  │  5162   │  │  POST-  │  │  THER-  │        │
   │  │  cases  │  │  EVENT  │  │  APEUTIC│        │
   │  └─────────┘  └─────────┘  └─────────┘        │
   │                                                 │
   │  Active Alerts: 3                              │
   │  - WAIS variance +5.7% (approaching threshold) │
   │  - AMOC AR(1) +7.7% (critical slowing)        │
   │  - Coral SST >1.4°C (post-tipping)            │
   └─────────────────────────────────────────────────┘
   ```

   **B. System Detail View (e.g., WAIS)**
   ```
   ┌─────────────────────────────────────────────────┐
   │  WAIS - West Antarctic Ice Sheet                │
   │  β=13.5 | Θ=1.5°C | Status: AT TIPPING         │
   ├─────────────────────────────────────────────────┤
   │                                                 │
   │  📐 FORMAL                                      │
   │  σ(β(R-Θ)) = 0.78                             │
   │  Distance to tipping: 21.9%                    │
   │  Time to tipping: 20 ± 23 years               │
   │                                                 │
   │  📊 EMPIRICAL                                   │
   │  [Time Series Graph: Mass Balance 2002-2024]  │
   │  Current: -1593 Gt/year (accelerating)        │
   │  Temperature: 1.17°C above pre-industrial     │
   │                                                 │
   │  🌊 POETIC                                      │
   │  "The ice remembers millennia, but forgets    │
   │   in decades. 21.9% to irreversibility."      │
   │                                                 │
   │  🔬 EARLY WARNING SIGNALS                      │
   │  [Graph: Variance over time]                  │
   │  Variance: +5.7% ✅                           │
   │  AR(1): +0.5% ❌                              │
   │  Spectral: 13.15 ✅                           │
   │                                                 │
   │  💚 CREP METRICS                                │
   │  Coherence:  0.78 ████████░░                  │
   │  Resonance:  0.30 ███░░░░░░░                  │
   │  Emergence:  0.68 ███████░░░                  │
   │                                                 │
   │  [View Trilayer Doc] [Download Data]          │
   └─────────────────────────────────────────────────┘
   ```

   **C. β-Landscape 3D View**
   ```
   Interactive 3D visualization:

   X-axis: System index (0-5)
   Y-axis: β-parameter (0-15)
   Z-axis: Distance to tipping (0-1)

   Color: Urgency (red=CRITICAL, yellow=HIGH, green=MEDIUM, blue=LOW)
   Size: Real-world impact magnitude (log scale)

   User can:
   - Rotate/zoom (OrbitControls)
   - Hover for tooltip (β, Θ, σ, status)
   - Click to navigate to system detail
   - Toggle Sigillin layer (symbolic overlay)
   ```

   **D. Sigillin Symbolic View**
   ```
   SVG-based symbolic representation:

   Each system = Sigillin (geometric sigil):
   - Type-2 (Thermodynamic): Flame geometry
   - Type-3 (Electrochemical): Lattice geometry
   - Type-4 (Informational): Network geometry

   Color: Status (red=TIPPED, orange=APPROACHING, green=STABLE)
   Pulsation: Urgency (fast pulse = CRITICAL)
   Line thickness: β-parameter (thicker = steeper)

   Layout: Hexagonal grid (coupled systems connected)
   ```

2. **UI Components (React + TypeScript):**
   - `<SystemCard>` (overview, CREP metrics)
   - `<TimeSeriesChart>` (D3.js line chart)
   - `<BetaLandscape3D>` (Three.js scene)
   - `<EWSPanel>` (variance, AR(1), spectral)
   - `<CREPGauge>` (circular progress bars)
   - `<SigillinCanvas>` (SVG symbolic layer)
   - `<AlertBanner>` (top notification bar)
   - `<TrilayerModal>` (embedded docs viewer)

3. **Styling:**
   - Dark theme (default, easier on eyes for monitoring)
   - Accessibility (WCAG 2.1 AA compliant)
   - Responsive (desktop, tablet, mobile)
   - Color palette (diverging: blue-white-red for thresholds)

**Team:**
- **Primary:** ChatGPT-Codex (React components)
- **Design:** Aeon (UI/UX, Sigillin symbolic design)
- **Accessibility:** Claude (WCAG audit)

**Success Criteria:**
- [ ] MVP dashboard loads < 2 seconds
- [ ] All 6 systems displayed with real data
- [ ] 3D β-landscape interactive (60 fps)
- [ ] CREP metrics update live (WebSocket)
- [ ] Trilayer docs embedded (markdown rendering)
- [ ] Mobile-responsive

**Blockers:**
- Three.js learning curve (3D performance)
- D3.js time series optimization (large datasets)

---

### **Week 9-10: Monitoring Pipeline & Alert System**

**Goals:**
- Implement automated EWS calculation (hourly)
- Design σ-tier alert system
- Communication protocol for public messaging

**Deliverables:**

1. **EWS Monitoring Pipeline:**
   ```python
   # Pseudocode
   def monitoring_pipeline():
       while True:
           for system in SYSTEMS:
               # 1. Fetch latest data
               data = fetch_latest_data(system)

               # 2. Calculate EWS
               ews = calculate_ews(data, window=180)  # 180-day rolling

               # 3. Check thresholds
               if ews.variance_increase > 0.20:  # +20% variance
                   emit_alert(system, "WATCH", "Variance increasing")

               if ews.ar1_increase > 0.15:  # +15% AR(1)
                   emit_alert(system, "WARNING", "Critical slowing detected")

               if system.distance_to_tipping < 0.10:  # <10% to threshold
                   emit_alert(system, "ALERT", "Approaching tipping point")

               # 4. Update CREP
               crep = calculate_crep(system)
               store_crep(system, crep)

               # 5. Log
               log_state(system, ews, crep)

           sleep(3600)  # Run every hour
   ```

2. **σ-Tier Alert System:**
   ```
   Alert Levels (based on σ activation state):

   🟢 MONITORING (σ < 0.3):
      - Status: "System stable, routine monitoring"
      - Action: None
      - Frequency: Weekly digest

   🟡 WATCH (σ = 0.3-0.6):
      - Status: "Early warning signals detected"
      - Action: Increase monitoring frequency, notify experts
      - Frequency: Daily updates
      - Example: WAIS variance +5.7%

   🟠 WARNING (σ = 0.6-0.8):
      - Status: "Approaching threshold, intervention window closing"
      - Action: Activate response teams, public communication
      - Frequency: Real-time alerts
      - Example: AMOC AR(1) +7.7%, Ditlevsen window 2025-2095

   🔴 ALERT (σ > 0.8):
      - Status: "Threshold crossed or imminent"
      - Action: Emergency protocols, international coordination
      - Frequency: Immediate, continuous
      - Example: Coral reefs 84% bleached (σ=0.95, POST-TIPPING)
   ```

3. **Communication Protocol:**

   **Principles:**
   - **Transparency:** Show data, methods, uncertainty
   - **Context:** Explain what threshold means (not "doom")
   - **Actionability:** What can be done (not fatalism)
   - **Humility:** Acknowledge limitations (Shadow-Sigillin)

   **Templates:**

   *WATCH Alert (Example: WAIS)*
   ```
   UTAC WATCH ALERT - West Antarctic Ice Sheet

   SIGNAL: Variance in ice mass loss increased +5.7% over past 6 months

   CONTEXT: Early warning signals suggest system approaching
   critical threshold (currently 21.9% away). This is NOT a
   prediction of collapse, but an indicator of reduced resilience.

   THRESHOLD: If warming exceeds 1.5°C above pre-industrial,
   irreversible collapse becomes likely (3-5m sea level rise
   over centuries).

   CURRENT STATUS: 1.17°C warming, accelerating mass loss
   (-1593 Gt/year)

   ACTIONABILITY: Rapid emissions reduction can prevent threshold
   crossing. Current trajectory projects crossing ~2050s.

   UNCERTAINTY: β=13.5 ± 1.5 (95% CI). Threshold may be crossed
   earlier (2035) or later (2070). Cascade coupling to AMOC
   not yet modeled.

   DATA SOURCE: NASA GRACE/GRACE-FO (public domain)
   METHOD: UTAC v3.0 (DOI: 10.5281/zenodo.17472834)

   NEXT UPDATE: Daily monitoring, weekly public report
   ```

4. **Notification Channels:**
   - Dashboard (top banner)
   - Email (subscriber list)
   - RSS feed
   - API webhook (for external integrations)
   - Social media (Twitter/X, opt-in)
   - Scholarly alerts (arXiv, Zenodo updates)

**Team:**
- **Primary:** Claude (communication protocol design)
- **Ethics Review:** Aeon (messaging ethics, anti-alarmism audit)
- **Implementation:** Mistral (notification infrastructure)

**Success Criteria:**
- [ ] EWS pipeline runs hourly without errors
- [ ] Alert latency < 5 minutes (signal → notification)
- [ ] Communication protocol approved by ethics review
- [ ] Zero false positives in first month (tuning)
- [ ] Public messaging clear, non-alarmist, actionable

**Blockers:**
- False positive tuning (sensitivity vs. specificity)
- Email deliverability (spam filters)
- Ethics review timeline (external board)

---

### **Week 11: Coupled Multi-System Model (MVP)**

**Goals:**
- Implement basic cascade coupling (WAIS ↔ AMOC)
- Extend UTAC to coupled dynamics
- Validate against literature (TiPACCs, Ditlevsen)

**Deliverables:**

1. **Coupled UTAC Formulation:**
   ```
   Independent (current):
   σᵢ = f(Rᵢ, Θᵢ, βᵢ)

   Coupled (new):
   σᵢ = f(Rᵢ, Θᵢ, βᵢ, Σⱼ wᵢⱼ σⱼ)

   Where:
   wᵢⱼ = coupling strength (0-1)

   Cascade matrix W:

           WAIS  AMOC  Coral  Measles  Finance  Cancer
   WAIS    1.0   0.2   0.1    0.0      0.0      0.0
   AMOC    0.15  1.0   0.3    0.0      0.0      0.0
   Coral   0.0   0.1   1.0    0.0      0.0      0.0
   Measles 0.0   0.0   0.0    1.0      0.0      0.0
   Finance 0.0   0.0   0.0    0.0      1.0      0.0
   Cancer  0.0   0.0   0.0    0.0      0.0      1.0

   Interpretation:
   - WAIS → AMOC: +0.2 (freshwater input weakens AMOC)
   - AMOC → WAIS: +0.15 (heat redistribution affects ice)
   - AMOC → Coral: +0.3 (ocean circulation affects coral habitats)
   - Others: Independent (for MVP)
   ```

2. **Implementation (TypeScript):**
   ```typescript
   class CoupledUTACModel {
     private systems: UTACSystem[];
     private couplingMatrix: number[][];

     calculateCoupledActivation(systemId: string): number {
       const i = this.systems.findIndex(s => s.id === systemId);
       const system = this.systems[i];

       // Base activation (independent)
       const R = system.getControlParameter();
       const Theta = system.getThreshold();
       const beta = system.getBeta();
       const sigma_base = 1 / (1 + Math.exp(-beta * (R - Theta)));

       // Coupling term
       let coupling = 0;
       for (let j = 0; j < this.systems.length; j++) {
         if (i !== j) {
           const w_ij = this.couplingMatrix[i][j];
           const sigma_j = this.systems[j].getActivation();
           coupling += w_ij * sigma_j;
         }
       }

       // Coupled activation (weighted sum)
       const alpha = 0.7; // Weight for base vs. coupling
       const sigma_coupled = alpha * sigma_base + (1 - alpha) * coupling;

       return sigma_coupled;
     }
   }
   ```

3. **Validation:**
   - Compare coupled vs. independent predictions
   - Literature check: TiPACCs coupling estimates
   - Sensitivity: How does w_ij affect outcomes?

4. **Visualization:**
   - Network graph (nodes=systems, edges=coupling strengths)
   - Cascade simulation (animate tipping propagation)

**Team:**
- **Primary:** Gemini (coupling matrix derivation from literature)
- **Implementation:** ChatGPT-Codex (TypeScript)
- **Validation:** Claude (compare to published models)

**Success Criteria:**
- [ ] Coupled model implemented for 3 systems (WAIS, AMOC, Coral)
- [ ] w_ij estimates validated against literature (±20%)
- [ ] Cascade simulation shows realistic propagation
- [ ] Dashboard displays coupling network graph

**Blockers:**
- Literature estimates of coupling strength (sparse data)
- Computational complexity (6x6 matrix, iterative)
- Validation data scarce (few multi-system studies)

---

### **Week 12: Testing, Documentation & Launch**

**Goals:**
- End-to-end testing (integration, load, security)
- Finalize documentation (user guides, API docs)
- Soft launch (limited audience)

**Deliverables:**

1. **Testing Suite:**
   - **Integration tests:** API → Database → Dashboard (E2E)
   - **Load tests:** 1000 concurrent users (stress test)
   - **Security audit:** OWASP Top 10 (penetration testing)
   - **Accessibility audit:** WCAG 2.1 AA (screen reader, keyboard nav)

2. **Documentation:**
   - **User Guide:** How to navigate dashboard, interpret alerts
   - **API Documentation:** OpenAPI spec, example queries
   - **Developer Guide:** How to contribute, extend systems
   - **Data Provenance:** Sources, licensing, update frequency
   - **Methodology:** UTAC v3.0 overview, β-estimation, EWS

3. **Deployment:**
   - **Hosting:** Cloud provider (AWS/GCP/Azure)
   - **Domain:** `utac-monitor.org` (or similar)
   - **SSL:** HTTPS (Let's Encrypt)
   - **CDN:** CloudFlare (performance + DDoS protection)
   - **Monitoring:** Prometheus + Grafana (uptime, performance)

4. **Soft Launch:**
   - **Audience:** 100-500 invited users (scientists, policymakers)
   - **Feedback mechanism:** Built-in survey, GitHub issues
   - **Timeline:** 2-4 weeks beta period
   - **Metrics:** Engagement (page views, time on site, alerts acknowledged)

5. **Launch Announcement:**
   - **Blog post:** Introducing UTAC V3 Real-Time Monitoring
   - **Preprint update:** Zenodo v3.1 (include dashboard link)
   - **Social media:** Coordinated announcement (Twitter, LinkedIn)
   - **Press outreach:** Science journalists (Science, Nature News)

**Team:**
- **Testing:** Claude + ChatGPT-Codex (automated tests)
- **Documentation:** Aeon (user-facing narratives)
- **DevOps:** Mistral (deployment pipeline)
- **Communications:** All AIs collaborate on announcement

**Success Criteria:**
- [ ] All tests passing (100% integration, 95% code coverage)
- [ ] Load test: 1000 users, <3s page load
- [ ] Security: No critical vulnerabilities
- [ ] Accessibility: WCAG 2.1 AA compliant
- [ ] Documentation: Complete (user + developer)
- [ ] Soft launch: 100+ beta users
- [ ] Feedback: >80% positive satisfaction

**Blockers:**
- Hosting costs ($200-500/month)
- Load testing infrastructure
- Security audit (may require external consultant)

---

## 🎯 Success Metrics (Phase 4 KPIs)

### Technical Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Real data coverage** | 6/6 systems | 0/6 | 🔴 Not started |
| **β-fit ΔAIC** | >10 all systems | 1.84-25 (mock) | 🟡 Needs real data |
| **Dashboard uptime** | 99.5% | N/A | 🔴 Not deployed |
| **API response time (p95)** | <200ms | N/A | 🔴 Not deployed |
| **EWS calculation frequency** | Hourly | N/A | 🔴 Not deployed |
| **Alert latency** | <5 min | N/A | 🔴 Not deployed |

### User Engagement Metrics

| Metric | Target (Month 1) | Target (Month 6) |
|--------|------------------|------------------|
| **Monthly active users** | 500 | 5,000 |
| **Page views** | 10,000 | 100,000 |
| **Avg. session duration** | 5 min | 8 min |
| **Alert subscriptions** | 200 | 2,000 |
| **API requests** | 5,000 | 50,000 |

### Impact Metrics

| Metric | Target (Year 1) |
|--------|-----------------|
| **Scientific citations** | 50+ (dashboard + paper) |
| **Media mentions** | 20+ (press coverage) |
| **Policy references** | 5+ (IPCC, WHO reports) |
| **Educational use** | 10+ universities (coursework) |
| **Open-source contributors** | 20+ (GitHub PRs) |

---

## 🚧 Risk Matrix & Mitigation

### CRITICAL Risks

**R1: Real Data Access Denied**
- **Probability:** Medium (30%)
- **Impact:** CRITICAL (blocks Phase 4)
- **Mitigation:**
  - Apply for NASA Earthdata account (free, approved in 2-5 days)
  - NOAA data is public domain (no restrictions)
  - WHO data available via API (registration required)
  - Fallback: Use historical datasets (not real-time but validated)

**R2: β-Fits Don't Improve with Real Data**
- **Probability:** Low (10%)
- **Impact:** HIGH (undermines UTAC validity)
- **Mitigation:**
  - Mock data designed conservatively (underestimates β)
  - Literature validation (β-estimates match published values)
  - Sensitivity analysis (robust to data sources)
  - Shadow-Sigillin already documents this risk

**R3: Hosting Costs Exceed Budget**
- **Probability:** Medium (40%)
- **Impact:** MEDIUM (delays deployment)
- **Mitigation:**
  - Start with cheap hosting ($20/month Heroku/Railway)
  - Optimize database (compression, retention policies)
  - Static site generation (reduce server load)
  - Apply for academic grants (NSF, EU Horizon)

### HIGH Risks

**R4: False Positive Alerts (Alarmism)**
- **Probability:** Medium (50%)
- **Impact:** HIGH (credibility damage)
- **Mitigation:**
  - Conservative thresholds (tune on historical data)
  - Human-in-the-loop review (before public alerts)
  - Communication protocol (emphasize uncertainty)
  - Shadow-Sigillin transparency (admit false positives)

**R5: Dashboard Performance (3D rendering)**
- **Probability:** Medium (30%)
- **Impact:** MEDIUM (poor UX)
- **Mitigation:**
  - Optimize Three.js (LOD, frustum culling)
  - Fallback to 2D for mobile
  - Progressive enhancement (static first, 3D optional)
  - Load testing early (Week 7)

### MEDIUM Risks

**R6: Coupled Model Validation Fails**
- **Probability:** High (60%)
- **Impact:** LOW (nice-to-have, not critical)
- **Mitigation:**
  - Defer to Phase 5 if needed
  - MVP focuses on independent systems
  - Coupling is research frontier (acceptable uncertainty)

**R7: Ethical Review Delays Launch**
- **Probability:** Low (20%)
- **Impact:** MEDIUM (2-4 week delay)
- **Mitigation:**
  - Start ethics review early (Week 3)
  - Parallel process (don't block development)
  - Clear communication protocol (reduces review scope)

---

## 💰 Budget Breakdown

### Development (One-Time)

| Item | Cost | Notes |
|------|------|-------|
| **Multi-AI Coordination** | $8,000 | Claude + ChatGPT + Gemini + Mistral + Aeon (12 weeks × ~$150/week/AI) |
| **Data API Subscriptions** | $2,000 | GRACE, RAPID, OISST, WHO (some free, some commercial) |
| **Cloud Hosting Setup** | $1,000 | Initial deployment, database migration |
| **Security Audit** | $3,000 | External consultant (OWASP Top 10) |
| **Design Assets** | $1,500 | Sigillin graphics, logo, branding |
| **Contingency (20%)** | $3,100 | Unexpected costs |
| **TOTAL** | **$18,600** | |

### Operational (Monthly)

| Item | Cost/Month | Notes |
|------|------------|-------|
| **Cloud Hosting** | $200-500 | Database, API, CDN (scales with traffic) |
| **Data Subscriptions** | $100-300 | Some APIs charge per request |
| **Monitoring Tools** | $50 | Prometheus Cloud, error tracking |
| **Domain + SSL** | $15 | utac-monitor.org + Let's Encrypt |
| **TOTAL** | **$365-865** | |

### Year 1 Total: ~$23,000-28,000

**Funding Sources:**
- Academic grants (NSF, EU Horizon, national climate programs)
- Open-source sponsorship (GitHub Sponsors, Patreon)
- Institutional partnerships (universities, IPCC, WHO)
- Philanthropic foundations (climate, public health)

---

## 🌊 Trilayer Integration

### How Phase 4 Embodies Trilayer Philosophy

**FORMAL LAYER (Dashboard Backend):**
- Mathematical rigor: β-ensembles, CIs, ΔAIC
- Reproducible: API returns raw data + methods
- Falsifiable: Shadow-Sigillin documents limitations

**EMPIRICAL LAYER (Real Data Pipeline):**
- Grounded: GRACE, RAPID, OISST (not simulations)
- Transparent: Data sources linked, provenance documented
- Validated: Bootstrap CIs, sensitivity analysis

**POETIC LAYER (Dashboard Frontend):**
- Meaningful: CREP poetics displayed alongside numbers
- Human: Trilayer docs embedded (not just graphs)
- Ethical: Communication protocol (not alarmism)

**All three layers visible in UI:**
- Formal: Equations, parameters, confidence intervals
- Empirical: Time series, current state, data sources
- Poetic: CREP poetics, threshold narratives, human impact

**The dashboard IS the trilayer, made interactive.**

---

## 🎨 Sigillin Protocol for Phase 4

### Dashboard as Living Sigillin

**Ordnungs-Sigillin (Navigation):**
- System index (6 systems)
- Alert log (chronological)
- Data catalog (sources, metadata)

**Bedeutungs-Sigillin (Meaning):**
- Trilayer docs (embedded markdown)
- CREP poetics (semantic layer)
- Shadow-Sigillin (risk transparency)

**Shadow-Sigillin (Honesty):**
- Limitations displayed (not hidden)
- Uncertainty emphasized (CIs, sensitivity)
- False positives acknowledged (when they occur)

**The dashboard is not just a tool—it's a semantic interface between UTAC theory and human understanding.**

---

## 📊 Activation Criteria (Phase 4 → Phase 5)

**Phase 4 is COMPLETE when:**

- [x] All 6 systems have real data feeds
- [x] β-fits validated (ΔAIC > 10 for all)
- [x] Bootstrap CIs calculated (95%)
- [x] Dashboard deployed (uptime >99%)
- [x] EWS pipeline operational (hourly)
- [x] Alert system functional (σ-tier messaging)
- [x] Trilayer docs embedded (all 6)
- [x] Soft launch completed (100+ users)
- [x] Documentation complete (user + API + developer)
- [x] Ethics review approved (communication protocol)

**Phase 5 will focus on:**
- Coupled multi-system model (full cascade dynamics)
- Spatial β-heterogeneity (regional resolution)
- Scenario testing (policy interventions)
- International deployment (multilingual, COP30 presentation)
- Community engagement (citizen science, education)

**R̄ projection (Phase 4 complete):**
```
Current: R̄ = 0.73, σ = 0.64 (Phase 3 end)
Phase 4 target: R̄ = 0.85, σ = 0.78
Increase: +16% (real data + dashboard + monitoring)
```

---

## 🚀 Next Steps (Week 1 Activation)

**Immediate Actions (This Week):**

1. **Data Access:**
   - [ ] Apply for NASA Earthdata account
   - [ ] Register for NOAA OISST API
   - [ ] Contact RAPID-MOCHA for data access
   - [ ] WHO API registration (measles data)

2. **Team Coordination:**
   - [ ] Brief ChatGPT-Codex on data pipeline tasks
   - [ ] Brief Gemini on statistical validation
   - [ ] Brief Mistral on backend architecture
   - [ ] Brief Aeon on Sigillin design

3. **Infrastructure Setup:**
   - [ ] Choose cloud provider (AWS/GCP/Azure)
   - [ ] Set up TimescaleDB instance
   - [ ] Configure CI/CD pipeline (GitHub Actions)
   - [ ] Initialize monitoring (Prometheus)

4. **Documentation:**
   - [ ] Update v3_roadmap.md with Phase 4 activation
   - [ ] Create Phase 4 sprint board (GitHub Projects)
   - [ ] Log activation in codex (Sigillin entry)

**First Sprint (Week 1-2):**
- Focus: Real data integration (CRITICAL path)
- Deliverable: WAIS β improves from 3.42 → 13.5
- Success metric: ΔAIC > 10 with real GRACE data

---

## 📚 References & Resources

**Technical:**
- GRACE/GRACE-FO Data: https://grace.jpl.nasa.gov/data/get-data/
- RAPID-MOCHA: https://www.rapid.ac.uk/rapidmoc/rapid_data/
- NOAA OISST: https://www.ncei.noaa.gov/products/optimum-interpolation-sst
- WHO Disease Outbreak News: https://www.who.int/emergencies/disease-outbreak-news

**Frameworks:**
- React: https://react.dev/
- D3.js: https://d3js.org/
- Three.js: https://threejs.org/
- TimescaleDB: https://www.timescale.com/

**UTAC Theory:**
- Römer, J. (2024). UTAC v1.0. Zenodo. DOI: 10.5281/zenodo.17472834
- Phase 3 Completion Codex: `seed/RoadToV.3/PHASE3_COMPLETION_CODEX.md`
- Trilayer Documentation: `seed/RoadToV.3/docs/*.md` (6 systems)

**Ethics:**
- Shadow-Sigillin V3: `seed/RoadToV.3/docs/shadow_sigillin_v3.yaml`
- Communication Ethics: `ETHICS.md`

---

**Document Version:** 1.0.0
**Status:** ✅ Complete - Ready for Phase 4 Activation
**Next Update:** Week 1 Sprint Report
**Activation Date:** TBD (upon approval + data access)

---

*"The threshold field holds—until the dashboard shows it doesn't. Then: informed action."*

🌊 Phase 4: **Make UTAC Operational** 🌊
