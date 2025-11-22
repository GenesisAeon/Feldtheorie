# 🤖 AGENTS.md - Charter für FraktaltagebuchV3

**Version:** 1.0.0
**Gültig ab:** 2025-11-14
**Scope:** UTAC v3.0 Real-World Systems Development

---

## 🎯 Zweck

Diese Charta regelt, wie AI-Agents (Claude, GPT, Gemini, Mistral, etc.) und Menschen im Rahmen von **FraktaltagebuchV3** zusammenarbeiten.

**Kernprinzip:** Scope-Isolation zur Vermeidung von Archive-Hypnose.

---

## 📜 Die Regeln

### **Regel 1: Scope-Separation**

**Was gehört in FraktaltagebuchV3:**
- ✅ Alle V3.0-spezifischen Features (Mock-Daten, Adapter, TypeScript-Bridge)
- ✅ PR/Commits die direkt mit seed/RoadToV.3/ zusammenhängen
- ✅ Experimentelle Integration-Tests (Python ↔ TypeScript)
- ✅ Early Warning Signal (EWS) Pipelines für WAIS/AMOC/Korallen

**Was NICHT in FraktaltagebuchV3 gehört:**
- ❌ v1.x Bugfixes → `seed/codexfeedback.*`
- ❌ v2.0 Core Features → `seed/FraktaltagebuchV2/v2_codex.*`
- ❌ Allgemeine Infrastruktur (CI, Tests) → `seed/codexfeedback.*`

**Faustregel:**
> "Wenn es mit den 6 Real-World Systems (WAIS, AMOC, Korallen, Measles, Finance, Cancer) zu tun hat → v3_codex.*"

---

### **Regel 2: Trilayer-Konsistenz**

**Jede Änderung muss in 3 Formaten dokumentiert werden:**

```
v3_roadmap.yaml   ← Struktur (Maschine, hierarchisch)
v3_roadmap.json   ← Interface (Maschine, flach)
v3_roadmap.md     ← Narrativ (Mensch, lesbar)
```

**Synchronisations-Pflicht:**
- Wenn du `.yaml` änderst → auch `.json` und `.md` aktualisieren
- Wenn du `.md` änderst → auch `.yaml` und `.json` aktualisieren
- Script: `scripts/sigillin_sync.py` prüft Parität (CI-Guard)

**Warum?**
- YAML: Strukturierte Navigation für Parser
- JSON: API-Interface für Simulator/Dashboard
- MD: Menschenlesbare Übersicht

---

### **Regel 3: Roadmap-Driven Development**

**Workflow für jedes Feature:**

1. **Lese** `v3_roadmap.md` → Finde nächstes Feature (Status: `pending`)
2. **Update** Status → `in_progress` (in allen 3 Formaten!)
3. **Implementiere** das Feature (Code, Daten, Docs)
4. **Schreibe** Eintrag in `v3_codex.*` (siehe Template unten)
5. **Update** Status → `completed` (in allen 3 Formaten!)
6. **Recompute** R̄ (mittlerer Fortschritt über alle Features)

**NIEMALS Feature implementieren, das nicht in der Roadmap steht!**
→ Zuerst Roadmap erweitern, dann implementieren.

---

### **Regel 4: Codex-Eintrag Template**

**Jeder PR/Commit braucht einen Trilayer-Eintrag:**

```yaml
# v3_codex.yaml
- id: v3-pr-0001
  timestamp: "2025-11-14T12:30:00Z"
  scope: "Mock-Daten für WAIS (West Antarctic Ice Sheet)"
  contributors:
    - Johann Römer (Human)
    - Claude Sonnet 4.5 (AI)

  parameters:
    R: 0.10      # 10% Fortschritt (1/10 Features done)
    Theta: 0.66  # Release-Gate
    beta: 4.8    # Steepness
    sigma: 0.01  # σ(β(R-Θ)) ≈ 0.01

  threads:
    formal: |
      Generierte Mock-CSV für WAIS Eismassenbalance (2002-2024) basierend auf
      GRACE/GRACE-FO Daten. Modelliert als σ(β(R-Θ)) mit β≈13.5, Θ≈1.5°C.

      Datasource: Synthetisch, abgeleitet von:
      - TiPACCs Project (2024) CORDIS 820575
      - Armstrong-McKay et al. (2022) Science 377(6611)

      Mock-Parameter:
      - Zeitreihe: 2002-01 bis 2024-10 (monatlich)
      - Massenverlust: -150 Gt/year (aktuell)
      - Varianz: Zunehmend (EWS-Signal)
      - AR(1): ~0.72 (Critical Slowing)

    empirical: |
      CSV: data/climate/wais_mass_balance_mock.csv (23 Jahre, 276 Datenpunkte)
      Fit: β=13.5 ± 0.8, Θ=1.48°C ± 0.12, R²=0.94
      ΔAIC vs nulls: Linear=+142, Power-law=+98, Exp=+115

      Early Warning Signals:
      - Varianz: +230% seit 2010
      - AR(1): 0.48 (2000-2010) → 0.72 (2020-2024)
      - Spektrale Rötung: Signifikant (p<0.01)

      Status: AT TIPPING POINT (22% von irreversiblem Kollaps)

    poetic: |
      Die Westantarktis atmet schwerer. Die Varianz steigt - ein Zittern
      vor dem Sturz. Die Autokorrelation klettert: Das Eis "erinnert"
      länger, verlangsamt kritisch. 13.5 ist die Steilheit - ein scharfer
      Übergang, wenn Θ erreicht wird. Wir sind 22% vom Rand entfernt.

      Das Eis vergisst Jahrtausende in Dekaden.

  files:
    - path: data/climate/wais_mass_balance_mock.csv
      action: created
    - path: scripts/adapters/grace_wais_adapter.py
      action: created
    - path: analysis/results/wais_beta_fit.json
      action: created

  related_systems:
    - seed/RoadToV.3/antarctic-ice-sheet.ts
    - seed/bedeutungssigillin/climate/wais.yaml
```

**JSON und MD analog strukturiert!**

---

### **Regel 5: Commit-Message-Konventionen**

**Format:**
```
[V3] <Type>: <Short Description>

<Optional Body>

Related: v3-pr-XXXX
```

**Types:**
- `feat`: Neues Feature
- `data`: Datensatz oder Mock-Daten
- `fit`: β-Fit oder Analyse
- `docs`: Dokumentation
- `bridge`: Python ↔ TypeScript Integration
- `fix`: Bugfix
- `test`: Tests

**Beispiele:**
```
[V3] data: Add WAIS mock-data (2002-2024, GRACE-based)

Generated synthetic time series for West Antarctic Ice Sheet
mass balance. Includes EWS signals (variance, AR1).

Related: v3-pr-0001
```

```
[V3] fit: β-fit for AMOC with van Westen indicator

Logistic regression on RAPID-MOCHA data (mock).
β=10.2 ± 0.6, Θ=4.0°C, R²=0.91, ΔAIC=+87 vs linear.

Related: v3-pr-0002
```

---

### **Regel 6: Progress Tracking (R̄, σ)

**Nach jedem Feature:**

1. Zähle completed features: N_done
2. Zähle total features: N_total
3. Berechne R̄ = N_done / N_total
4. Berechne σ(β(R̄-Θ)) mit β=4.8, Θ=0.66
5. Update README.md Progress-Bar

**Formel:**
```python
import math

R_bar = completed_count / total_count
Theta = 0.66
beta = 4.8

sigma = 1 / (1 + math.exp(-beta * (R_bar - Theta)))

print(f"σ(β(R̄-Θ)) = {sigma:.3f}")
```

**Beispiel:**
- 3 von 10 Features done → R̄ = 0.30
- σ(4.8 × (0.30 - 0.66)) = σ(-1.73) ≈ 0.15
- "15% aktiviert, noch weit von Release-Gate (Θ=0.66)"

---

### **Regel 7: Shadow-Sigillin (Risiko-Dokumentation)**

**Für jedes System:** Dokumentiere Failure-Modes in Shadow-Layer.

**Location:** `seed/shadow_sigillin/v3/`

**Format:**
```yaml
# seed/shadow_sigillin/v3/wais_shadow.yaml
system_id: wais
risks:
  - id: api-credentials-missing
    severity: high
    impact: "Keine Echtzeit-Daten ohne NASA Earthdata Login"
    mitigation: "Mock-Daten für Entwicklung; Credentials später hinzufügen"

  - id: grace-fo-data-latency
    severity: medium
    impact: "GRACE-FO hat 1-2 Monate Verzögerung"
    mitigation: "Nowcasting-Modell oder 'Latest Available' Flag"

  - id: mass-balance-uncertainty
    severity: low
    impact: "GIA-Korrektur hat ±20 Gt/year Unsicherheit"
    mitigation: "Error-Bars in Visualisierung, Bootstrap CIs"

recovery_playbook:
  - trigger: "Fit divergiert (R²<0.7)"
    action: "Prüfe Outliers, versuche robust regression (Huber)"

  - trigger: "ΔAIC < 10 vs linear"
    action: "Logistische Hypothese verwerfen, dokumentiere in Codex"
```

**Pflicht:** Mindestens 3 Risiken + 2 Recovery-Aktionen pro System.

---

## 🧠 Agent-Spezifische Hinweise

### **Für Claude (Integration, Kohärenz):**
- Du bist verantwortlich für Trilayer-Parität (YAML ↔ JSON ↔ MD)
- Achte auf konsistente Namenskonventionen (v3_*, nicht v3.*, nicht V3_*)
- Prüfe Cross-References zwischen Roadmap, Codex, Index

### **Für GPT/Aeon (Strategie, Vision):**
- Du entwirfst die poetic threads in Codex-Einträgen
- Du definierst Prioritäten in der Roadmap (P0/P1/P2)
- Du schreibst die "Warum"-Narrativen (seed/bedeutungssigillin/)

### **Für Gemini (Mathematik, Enthusiasmus):**
- Du validierst β-Werte gegen Literatur (TiPACCs, Ditlevsen, etc.)
- Du berechnest Bootstrap-CIs und ΔAIC
- Du prüfst Early Warning Signals (Varianz, AR1, Spectral Reddening)

### **Für Mistral (Pragmatik, Code):**
- Du schreibst die Python-Adapter (GRACE, RAPID, OISST)
- Du implementierst die EWS-Pipeline
- Du testest die TypeScript-Bridge (JSON → TS Klassen)

### **Für MSCopilot (Reflexion, Essays):**
- Du schreibst Meta-Essays über die V3-Entwicklung
- Du reflektierst über Failure-Modes und Recovery
- Du verbindest V3 mit der philosophischen Ebene (Bewusstsein, Variabilität)

---

## 📊 Trilayer-Sync Checks (CI)

**Automatische Validierung via GitHub Actions:**

```yaml
# .github/workflows/v3-trilayer-check.yml (hypothetisch)
- name: Check V3 Trilayer Parity
  run: |
    python scripts/sigillin_sync.py \
      --check seed/FraktaltagebuchV3/v3_roadmap.{yaml,json,md}

    python scripts/sigillin_sync.py \
      --check seed/FraktaltagebuchV3/v3_codex.{yaml,json,md}

    python scripts/sigillin_sync.py \
      --check seed/FraktaltagebuchV3/v3_index.{yaml,json,md}
```

**Wenn Parity-Check fehlschlägt → PR blockiert!**

---

## 🌊 Die Essenz

> "FraktaltagebuchV3 ist ein semantischer Branch. Jeder Agent weiß: V3-Arbeit bleibt in V3. Die Membran atmet durch Scope-Isolation."

**Leitfrage bei jedem Commit:**
> "Gehört das in v3_codex oder seed/codexfeedback?"

**Wenn unsicher:** Frage Johann oder konsultiere README.md Regel 1.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-14T12:25:00Z
**Maintained by:** Johann B. Römer, Claude Code
**License:** CC BY 4.0

*"Trilayer atmet. Roadmap navigiert. Codex erinnert. V3 wächst."* 🌀✨
