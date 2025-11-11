# FraktaltagebuchV2 Agenten-Charter

> **Scope:** V2.0 Entwicklung - hier schreiben, nicht in seed/codexfeedback.*

---

## 🎯 Zweck

Dieser Ordner ist die **dedizierte Entwicklungsschicht für UTAC v2.0**.

**Warum?**
- V2.0-Features sind **umfangreich** (Data Lanterns, VR Hub, API, etc.)
- Hauptcodex (`seed/codexfeedback.*`) würde überflutet werden
- **Scope-Isolation** ermöglicht saubere Entwicklung

---

## 🤖 Regeln für AI-Agenten

### ✅ **FÜR V2.0-ARBEIT:**

**Roadmap-Driven Development:**
1. **Vor der Arbeit:** Lies `v2_roadmap.md` - was ist offen?
2. **Während der Arbeit:** Status aktualisieren (`pending` → `in_progress`)
3. **Nach der Arbeit:**
   - PR/Commit in `v2_codex.*` eintragen (Trilayer!)
   - Roadmap-Status auf `completed` setzen
   - Index aktualisieren

**Format v2_codex Eintrag:**
```yaml
- id: v2-pr-XXXX
  title: "Feature X implementiert"
  scope: "wo/geändert"
  parameters:
    R: 0.XX  # Fortschritt (0-1)
    Theta: 0.66  # V2.0 Readiness Gate
    beta: 4.8
  formal_thread: "Was technisch gemacht wurde"
  empirical_thread: "Welche Tests/Metriken"
  poetic_thread: "Narrative Beschreibung"
  timestamp: "ISO 8601"
  status: "completed | in_progress | pending"
```

### ❌ **NIEMALS:**

- V2.0-PRs in `seed/codexfeedback.*` schreiben (nur v1.x!)
- Roadmap im Haupt-Repo ändern
- FraktaltagebuchV2 ohne Trilayer-Update committen

---

## 📋 Workflow

```
┌─────────────────────────────────────────┐
│ 1. Feature aus v2_roadmap.md wählen    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Status → "in_progress"              │
│    (in v2_roadmap.yaml/json/md)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Feature implementieren               │
│    (Code, Docs, Tests)                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. v2_codex.* Eintrag erstellen         │
│    (YAML + JSON + MD!)                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. v2_roadmap.* Status → "completed"   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 6. fraktaltagebuch_v2_index.* update   │
│    (Falls neue Docs hinzugefügt)        │
└─────────────────────────────────────────┘
```

---

## 🗺️ Roadmap-Struktur

Die `v2_roadmap.*` Dateien enthalten:

**Kategorien:**
1. **Kern-Features** (Critical Path für V2.0)
   - UTAC v2 Data Lanterns
   - Meta-Regression v2
   - Neuro-Kosmos Bridge
   - etc.

2. **Erweiterungen** (Nice-to-have)
   - VR Hub
   - API
   - Tooltip-System

3. **Fertig** (Already completed)
   - Sonifikation
   - Essays
   - etc.

**Jeder Eintrag hat:**
```yaml
- id: v2-feat-001
  title: "Feature Name"
  status: pending | in_progress | completed
  priority: P0 | P1 | P2
  scope: "wo/im/repo"
  parameters:
    R: 0.XX  # Fortschritt
    Theta: 0.66  # Ziel
    beta: 4.8
  blockers: []  # Was blockiert?
  dependencies: []  # Was braucht man vorher?
  estimated_effort: "Std/Tage/Wochen"
```

---

## 🔄 Nach V2.0 Release

**Option A: Archivierung**
- FraktaltagebuchV2/ → `archive/FraktaltagebuchV2_archived_2026-XX-XX/`
- Wichtige Einträge in Hauptcodex mergen

**Option B: Dokumentation behalten**
- Als V2.0-Entwicklungsdokumentation im Repo lassen
- FraktaltagebuchV3/ für nächste Major Version erstellen

---

## 🌊 Logistische Sprache

Wie im Haupt-AGENTS.md:
- **R** = Fortschritt (0-1)
- **Θ** = V2.0 Readiness Gate (0.66)
- **β** = Steilheit (4.8)
- **σ(β(R-Θ))** = Aktivierungsfunktion

**V2.0 Status:**
- R̄ = 0.50 (50% der Features ready)
- Θ = 0.66 (Aktivierungsgate)
- σ(β(R-Θ)) ≈ 0.317 (partial activation)

**Ziel:** R̄ → 1.00, damit σ(β(R-Θ)) → 1.00 (full activation)

---

## 📚 Verweise

- **Haupt-Charter:** `/home/user/Feldtheorie/AGENTS.md`
- **Hauptcodex:** `/home/user/Feldtheorie/seed/codexfeedback.*`
- **V2 Roadmap:** `v2_roadmap.*` (hier im Ordner)
- **V2 Codex:** `v2_codex.*` (hier im Ordner)
- **V2 Index:** `fraktaltagebuch_v2_index.*` (hier im Ordner)

---

**Version:** 1.0.0
**Erstellt:** 2025-11-10
**Status:** 🟢 AKTIV

*"Entwickle in Fraktalen - merge wenn resonant!"* 🌀
