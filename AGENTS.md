# Feldtheorie Agenten-Charter 2.0

> σ(β(R-Θ)) pulsiert bereits auf der Steilflanke. Dieses Charter sorgt dafür, dass
> jeder Agent — Mensch oder Maschine — ohne zusätzliche Initialisierung weiterbauen
> kann. R misst offene Arbeiten quer durch System, Wissenschaftsprojekt und Metaquest,
> Θ ist in den Sigillin-Membranen und dem UTAC-Statuskartogramm dokumentiert,
> β≈4.8 hält Aktivierungen scharf, und ζ(R) wird über BreakPoint-Rituale,
> Telemetrie und Codexpflege gedämpft.

---

## 1. Feld-Orientierung

1. **Trilayer-Prinzip bewahren.** Jede neue Laterne erscheint gleichzeitig als
   YAML (Struktur), JSON (Agentennerv) und Markdown (Stimme). Ohne Tri-Layer kein Merge.
2. **Logistische Sprache verwenden.** Beschreibe immer $(R, \Theta, \beta, \zeta(R))$
   und den Übergang über $\sigma(\beta(R-\Theta))$. Verknüpfe technische Aussagen mit
   poetischer Resonanz (Membranen, Dämmerungen, Laternen).
3. **Kopplungspflicht.** Verweise von Bedeutungs-Sigillin auf die entsprechenden
   Ordnungs-Sigillin (`feldtheorie_index.*`, `seed_index.*`) und auf empirische Belege
   (`analysis/`, `data/`, `docs/`).
4. **Falsifizierbarkeit sichern.** Jede Behauptung braucht ein Nullmodell (linear,
   power law, …) plus ΔAIC/CI-Metriken. Schatten-Sigillin beschreiben Wiederherstellung.
5. **UTAC Status Matrix lesen.** `docs/utac_status_alignment_v1.2.md` ist das aktuelle
   Observatorium. Ergänze dort neue Brücken und vermerke offene Lücken.

---

## 2. Sigillin-Systeme

### 2.1 Bedeutungs-Sigillin
- Hüte die langfristigen Bedeutungs-Membranen (`seed/bedeutungssigillin/**`).
- Bei Änderungen **niemals überschreiben** – Versionieren und im Codex dokumentieren.
- Neue Metaquest-Strukturen:
  - `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.*` – Bridge Dashboard
    zwischen System- und Kampagnenlaternen.
  - `seed/bedeutungssigillin/system/metaquest/metaquest_system_map.*` – Automationsknochen.
  - `seed/bedeutungssigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_map.*` –
    Kampagnenresonanz.

### 2.2 Schatten-Sigillin
- Katalogisiere Risiken und Recovery-Rituale (`seed/shadow_sigillin/**`).
- Jede Licht-Änderung verlangt den Spiegel in Schatten inkl. Codex-ID.
- Neue Brückenwächter:
  - `seed/shadow_sigillin/metaquest/metaquest_shadow_index.*`
  - `seed/shadow_sigillin/system/metaquest/metaquest_system_shadow.*`
  - `seed/shadow_sigillin/wissenschaftsprojekt/metaquest/metaquest_campaign_shadow.*`

### 2.3 Codex-Feedback (Fraktaltagebuch)
- `seed/codexfeedback.{yaml,json,md}` ist Pflicht. Struktur pro Eintrag:
  - ID, Titel, Scope, $(R, \Theta, \beta)$, Resonanzstatus, formale/empirische/poetische
    Notizen, ISO-Timestamp.
- Statusverlauf: *draft → primed → active → resonant → completed → archived*.
- Änderungen an Bedeutungs-/Schatten-Sigillin **ohne** Codex-Eintrag erzeugen
  den Incident `sys-shadow-002`.

### 2.4 FraktaltagebuchV2 - Scope-Isolation für V2.0

**WICHTIG:** Ab jetzt gilt eine **Trennung zwischen v1.x und v2.0 Entwicklung**!

- **Für v1.x Maintenance:** Nutze weiterhin `seed/codexfeedback.*` (wie gehabt)
- **Für v2.0 Features:** Nutze `seed/FraktaltagebuchV2/v2_codex.*` (NEU!)

**Warum?**
- V2.0-Entwicklung ist umfangreich (Data Lanterns, VR Hub, API, etc.)
- Hauptcodex würde überflutet werden (Archive-Hypnose!)
- **FraktalImplementierungstechnik** ermöglicht saubere Scope-Isolation

**Struktur:**
```
seed/FraktaltagebuchV2/
├── README.md                   # Konzept & Workflow
├── AGENTS.md                   # Charter für V2-Arbeit
├── v2_roadmap.{yaml,json,md}   # Was ist zu tun?
├── v2_codex.{yaml,json,md}     # V2 PR/Commit-Log
└── fraktaltagebuch_v2_index.*  # Navigation
```

**Workflow für V2-Features:**
1. Lies `seed/FraktaltagebuchV2/v2_roadmap.md` → Feature auswählen
2. Implementiere Feature
3. **Eintrag in `seed/FraktaltagebuchV2/v2_codex.*`** erstellen (Trilayer!)
4. **NICHT** in `seed/codexfeedback.*` schreiben!
5. Roadmap-Status aktualisieren

**Nach V2.0 Release:**
- Wichtige Einträge aus `v2_codex.*` in `codexfeedback.*` mergen
- FraktaltagebuchV2/ archivieren oder als V2-Dokumentation behalten
- Optional: FraktaltagebuchV3/ für nächste Major Version

**Siehe:** `seed/FraktaltagebuchV2/README.md` für vollständige Dokumentation

---

## 3. Arbeitsrhythmus

1. **Vor dem Arbeiten** – Lies die letzten Codex-Einträge, prüfe UTAC-Status und
   Bridge-Dashboard (`metaquest_meaning_index.*`).
2. **Währenddessen** – Notiere ΔAIC, $R^2$, Telemetrie, BreakPoint-Bezüge.
3. **Nach dem Arbeiten** – Aktualisiere Tri-Layer, Indizes, Codex und – falls nötig –
   UTAC-Statusabschnitte.
4. **Automationshygiene** – Pflege `scripts/archive_sigillin.py`, `scripts/sigillin_sync.py`
   (geplant) und CI-Hooks, damit Indizes & Codex automatisch geprüft werden.

---

## 4. Quickstart für neue Agenten

1. **Lesen:**
   - `docs/utac_status_alignment_v1.2.md`
   - `seed/Manuskriptfinalisierung und Kampagnenstart.pdf`
   - `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`
   - `seed/shadow_sigillin/metaquest/metaquest_shadow_index.md`
2. **Indices prüfen:** `feldtheorie_index.*`, `seed_index.*`, `docs/docs_index.*`.
3. **Tests/Telemetrie:** nutze Makefile (`make preset-guard`, `make docs-index`) und
   plane `sigillin_sync`-Runs.
4. **Release-Ready?** – Bridge-Dashboard ≥ aktuelle Codex-ID, Paritätsbrief vollständig,
   BreakPoint-Verweise in System & Kampagne aktiv.

---

## 5. Eskalations-Matrix

| Auslöser | Aktion |
| -------- | ------ |
| Bedeutungs-/Shadow-Sigillin geändert | Tri-Layer aktualisieren, Indizes refreshen, Codex-Eintrag schreiben |
| Metaquest-Brücke meldet Stau | Bridge-Dashboard + Beacons synchronisieren, Telemetrie timestampen, UTAC-Matrix ergänzen |
| Δindex-Parität > 0 | `scripts/archive_sigillin.py --refresh`, Parser laufen lassen, Ergebnis dokumentieren |
| Telemetrie > 1 Sprint alt | Manuelles `sigillin_sync`, Ergebnis in Codex + UTAC eintragen, Automation reparieren |

---

## 6. Release-Schutz

- **Merge-Blocker:** Kein Merge ohne aktualisierten Codex-Entry, wenn Bedeutungs- oder
  Schatten-Sigillin berührt wurden.
- **Brücken-Nullmodell:** Falls die Metaquest-Brücke stumm ist (kein Timestamp/Codex-ID),
  Launch-Aufgaben sofort pausieren → `mq-bridge-shadow-001`.
- **Archiv-Hygiene:** Überschüssige Sigillin-Versionen regelmäßig mit
  `scripts/archive_sigillin.py` archivieren, dabei Brückeneinträge kontrollieren.

---

Wenn du diese Leitlinien hältst, bleibt das Feld resonant und jede neue Laterne findet
sofort Anschluss.
