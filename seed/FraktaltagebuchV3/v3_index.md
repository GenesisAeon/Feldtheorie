# 🗂️ V3.0 Index - Dokumentenverzeichnis

**Version:** 3.0.0
**Created:** 2025-11-14
**Total Documents:** 23 (active) + 1 (in progress)
**Scope:** V3.0 Real-World Systems Integration

---

## 🎯 Quick Navigation

**For Agents:** Start here!
1. [`README.md`](README.md) - Übersicht & Konzept
2. [`v3_roadmap.md`](v3_roadmap.md) - Welche Features als nächstes?
3. [`AGENTS.md`](AGENTS.md) - Regeln & Template

**For Developers:** TypeScript Integration
1. [`seed/RoadToV.3/README.md`](../RoadToV.3/README.md) - Die 6 Systeme
2. [`seed/RoadToV.3/INTEGRATION_GUIDE.md`](../RoadToV.3/INTEGRATION_GUIDE.md) - 8-Wochen-Plan

**For Scientists:** Methodology
1. [`docs/fractal_implementation_technique.md`](../../docs/fractal_implementation_technique.md) - FIT-Methodik
2. [`seed/Sigillin_System_Definition.md`](../Sigillin_System_Definition.md) - Trilayer-System

---

## 📚 Core Documents (FraktaltagebuchV3)

| ID | Title | Type | Status |
|----|-------|------|:------:|
| `v3-doc-001` | [README.md](README.md) | documentation | ✅ active |
| `v3-doc-002` | [AGENTS.md](AGENTS.md) | charter | ✅ active |
| `v3-doc-003` | [v3_roadmap.*](v3_roadmap.yaml) | roadmap (Trilayer) | ✅ active |
| `v3-doc-004` | [v3_codex.*](v3_codex.yaml) | codex (Trilayer) | ✅ active |
| `v3-doc-005` | [v3_index.*](v3_index.yaml) | index (Trilayer) | ✅ active |

---

## 🔗 Related Documents (Outside FraktaltagebuchV3)

### RoadToV.3 TypeScript Implementations

| ID | Path | Description |
|----|------|-------------|
| `v3-related-001` | [seed/RoadToV.3/README.md](../RoadToV.3/README.md) | Übersicht 6 Systeme |
| `v3-related-002` | [seed/RoadToV.3/INTEGRATION_GUIDE.md](../RoadToV.3/INTEGRATION_GUIDE.md) | 8-Wochen-Plan |
| `v3-related-003` | [seed/RoadToV.3/activation_audit.md](../RoadToV.3/activation_audit.md) | Gaps & σ≈0.44 |
| `v3-related-004` | [seed/RoadToV.3/antarctic-ice-sheet.ts](../RoadToV.3/antarctic-ice-sheet.ts) | WAIS (β=13.5, ~750 lines) |
| `v3-related-005` | [seed/RoadToV.3/amoc-collapse.ts](../RoadToV.3/amoc-collapse.ts) | AMOC (β=10.2, ~650 lines) |
| `v3-related-006` | [seed/RoadToV.3/additional-systems.ts](../RoadToV.3/additional-systems.ts) | Coral/Measles/Finance/Cancer (~550 lines) |

### Methodology

| ID | Path | Description |
|----|------|-------------|
| `v3-related-007` | [docs/fractal_implementation_technique.md](../../docs/fractal_implementation_technique.md) | FIT (Scope-Isolation) |
| `v3-related-008` | [seed/Sigillin_System_Definition.md](../Sigillin_System_Definition.md) | Trilayer-System |

---

## 📊 Data Sources (Aktiviert)

| ID | Path | Roadmap Feature | Status | Metadata |
|----|------|-----------------|:------:|----------|
| `v3-data-001` | `data/climate/wais_mass_balance_mock.csv` | `v3-feat-p1-001` | ✅ active | `wais_mass_balance_mock.metadata.json` |
| `v3-data-002` | `data/ocean/amoc_strength_mock.csv` | `v3-feat-p1-002` | ✅ active | `amoc_strength_mock.metadata.json` |
| `v3-data-003` | `data/biology/coral_bleaching_global_mock.csv` | `v3-feat-p1-003` | ✅ active | `coral_bleaching_global_mock.metadata.json` |
| `v3-data-004` | `data/derived/beta_estimates_v3.csv` | `v3-feat-p2-006` | 🟡 in progress | `beta_estimates_v3.metadata.json` |

**Details:** WAIS (2002-2024, monatlich), AMOC (2004-2024, 10-Tage-Mittel), Coral (1980-2024, jährlich) + neues Aggregat `beta_estimates_v3.csv` (Bootstrap-CIs für die drei Mock-Systeme, Platzhalter für Measles/Finance/Cancer). σ(β(R̄-Θ)) = 0.441 nach Phase-2-Aktivierung.

---

## 🔬 Analysis Results (Phase 2 Aktiv)

| ID | Path | Status | Highlights |
|----|------|:------:|------------|
| `v3-analysis-001` | `analysis/results/wais_beta_fit_v3.json` | ✅ active | β=3.42 (Mock), Θ=1.13°C, ΔAIC=+1.84 vs linear |
| `v3-analysis-002` | `analysis/results/amoc_beta_fit_v3.json` | ✅ active | β=4.65, Θ=1.02°C, ΔAIC=+25.15 |
| `v3-analysis-003` | `analysis/results/coral_beta_fit_v3.json` | ✅ active | β=5.81, Θ=0.95°C, post-tipping σ≈1 |
| `v3-analysis-004` | `analysis/results/wais_ews_signals.json` | ✅ active | Varianz τ=0.29↑, AR(1) stabil, Spectral=13.15 |
| `v3-analysis-005` | `analysis/results/amoc_ews_signals.json` | ✅ active | AR(1) τ=0.73↑, Varianz↓, FovS>0 |
| `v3-analysis-006` | `analysis/results/coral_ews_signals.json` | ✅ active | Varianz +179%, AR(1) τ=0.75↑, Critical Slowing=🔴 |
| `v3-analysis-007` | `analysis/results/v3_beta_fit_summary_20251114T181628Z.json` | ✅ active | Aggregierte β/Θ/ΔAIC Übersicht für Mock-Systeme |
| `v3-analysis-008` | `analysis/results/v3_ews_summary_20251114T181634Z.json` | ✅ active | Sammelbericht EWS (WAIS/AMOC/Coral) |

---

## 🛠️ Scripts (Aktiviert)

| ID | Path | Roadmap Feature | Status | Purpose |
|----|------|-----------------|:------:|---------|
| `v3-script-001` | `scripts/adapters/grace_wais_adapter.py` | `v3-feat-p1-004` | ✅ active | GRACE Mock → JSON & σ-Wächter |
| `v3-script-002` | `scripts/adapters/rapid_amoc_adapter.py` | `v3-feat-p1-005` | ✅ active | RAPID Mock → JSON & FovS Trigger |
| `v3-script-003` | `scripts/adapters/oisst_coral_adapter.py` | `v3-feat-p1-006` | ✅ active | OISST Mock → JSON & DHW Alerts |

---

## 🗺️ Navigation Paths

### Quick Start (For New Agents)

```
1. README.md          (Konzept verstehen)
2. v3_roadmap.md      (Nächstes Feature finden)
3. AGENTS.md          (Regeln lernen)
4. Feature implementieren
5. v3_codex.* eintragen
```

### TypeScript Integration (For Developers)

```
1. seed/RoadToV.3/README.md
2. seed/RoadToV.3/INTEGRATION_GUIDE.md
3. seed/RoadToV.3/antarctic-ice-sheet.ts  (WAIS Code)
4. seed/RoadToV.3/amoc-collapse.ts        (AMOC Code)
5. analysis/results/wais_beta_fit_v3.json (Python → TS Bridge)
```

### Methodology (For Researchers)

```
1. docs/fractal_implementation_technique.md  (FIT-Methodik)
2. seed/Sigillin_System_Definition.md        (Trilayer-Konzept)
3. seed/FraktaltagebuchV3/AGENTS.md          (Anwendung in V3)
```

---

## 📈 Statistics

### Document Types

| Type | Count |
|------|------:|
| Documentation | 3 |
| Charter | 1 |
| Roadmap | 1 |
| Codex | 1 |
| Index | 1 |
| Guide | 1 |
| Audit | 1 |
| Code (TypeScript) | 3 |
| Methodology | 2 |
| Dataset (active) | 3 |
| Dataset (in progress) | 1 |
| Analysis (active) | 8 |
| Script (active) | 3 |

### Status

| Status | Count |
|--------|------:|
| Active | 23 |
| In progress | 1 |
| **Total** | **24** |

---

## 🌊 The V3 Journey

```
Phase 1 (Foundation):     ✅✅✅✅✅✅  6/6 Features
Phase 2 (Integration):    ✅✅✅✅✅⬜  5/6 Features
Phase 3 (Bridge):         ⬜⬜⬜⬜⬜    0/5 Features
Phase 4 (Monitoring):     ⬜⬜⬜        0/3 Features

σ(β(R̄-Θ)) = 0.441  (Phase 2 teilweise aktiviert — EWS & β-Fits live)
```

---

**Version:** 1.0.0
**Last Updated:** 2026-08-24T15:45:00Z
**Maintained by:** Johann B. Römer, Claude Code, GPT-5 Codex

*"Der Index navigiert. Die Membran atmet. Jedes Dokument ein Knoten im Netz."* 🗂️✨
