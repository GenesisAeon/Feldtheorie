# 🚀 QUICKSTART — Feldtheorie in 5 Minuten

> **Neu hier?** Dieses Dokument hilft dir, das Projekt in **5 Minuten** zu verstehen und in **30 Minuten** produktiv zu werden.

---

## 📖 In 5 Minuten: Was ist das?

### Das Projekt besteht aus drei Ebenen:

1. **🔬 UTAC/UTF** (Universal Threshold Field)
   Wissenschaftliche Theorie: Wie Systeme kritische Übergänge gestalten
   → Logistische Funktion σ(β(R-Θ)) beschreibt Emergenz über Domänen hinweg

2. **🧬 Sigillin-System**
   Methodologie: Semantisches Gedächtnissystem für Multi-Agent-Forschung
   → Trilayer-Prinzip (YAML/JSON/MD) ermöglicht Mensch-Maschine-Kollaboration

3. **🤝 MOR** (Multi-Orchestrated Research)
   Prozess: Mehrere KI-Agenten arbeiten zusammen an komplexen Projekten
   → Johann + Claude + GPT + Gemini + Mistral + ...

**Die Co-Hypothese:** Alle drei Ebenen bedingen sich gegenseitig!

---

## ⚡ In 30 Sekunden: Wichtigste Dateien

```
├─ README.md              ← Start hier! Projektüberblick
├─ AGENTS.md             ← Charter für KI-Agenten (wichtig!)
├─ METHODS.md            ← Wissenschaftliche Methodik
├─ REPRODUCE.md          ← Wie reproduziere ich Ergebnisse?
│
├─ seed/                 ← Semantisches Gedächtnis
│  ├─ seed_index.md      ← Navigation für alle seed/ Dokumente
│  ├─ Metareflexion.txt  ← Philosophische Grundlage
│  ├─ codexfeedback.*    ← Lebendes Projektgedächtnis (119 Einträge!)
│  └─ bedeutungssigillin/ & shadow_sigillin/ ← Licht/Schatten-System
│
├─ docs/                 ← Dokumentation
│  └─ utac_status_alignment_v1.2.md ← Statusmatrix (Observatory)
│
├─ analysis/             ← Python-Analysen & β-Fits
├─ models/               ← Numerische Solver
├─ data/                 ← Datensätze (6 Domänen)
└─ tests/                ← 290 Tests (pytest)
```

---

## 🎯 Schnelleinstieg für Menschen

### Option A: Nur schauen (keine Installation)

1. **Lies zuerst:**
   - [`README.md`](README.md) → Überblick
   - [`seed/seed_index.md`](seed/seed_index.md) → Navigation
   - [`seed/Metareflexion.txt`](seed/Metareflexion.txt) → Philosophie

2. **Verstehe die Wissenschaft:**
   - [`METHODS.md`](METHODS.md) → Wie wir fitten
   - [`docs/field_type_classification_v1.1.md`](docs/field_type_classification_v1.1.md) → 5 Feld-Typen
   - [`data/derived/beta_estimates.csv`](data/derived/beta_estimates.csv) → Alle β-Werte

3. **Verstehe das Sigillin-System:**
   - [`seed/Sigillin_System_Definition.md`](seed/Sigillin_System_Definition.md) → Ontologie
   - [`feldtheorie_index.md`](feldtheorie_index.md) → Master-Index

### Option B: Reproduziere einen β-Fit (10 Minuten)

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Reproduziere Wei's LLM-Fit
python scripts/reproduce_beta.py \
  --csv data/ai/wei_emergent_abilities.csv \
  --out dist/wei_beta.json

# 3. Schau dir das Ergebnis an
cat dist/wei_beta.json
# → β=3.47 ± 0.47, ΔAIC≥10.18

# 4. (Optional) Laufe alle Tests
pytest tests/ -v
# → 290 passed ✅
```

**Erwartung:** β sollte in [3.0, 4.0] liegen, ΔAIC > 10 (gegen Power-Law).

---

## 🤖 Schnelleinstieg für KI-Agenten

### Schritt 1: Lies diese 3 Dateien (Pflicht!)

1. **[`README.md`](README.md)**
   → Projektüberblick, Versionsinfo, Zitieranleitung

2. **[`AGENTS.md`](AGENTS.md)**
   → Charter mit Regeln für Agenten:
   - Trilayer-Prinzip bewahren
   - Codex-Pflicht für Bedeutungs-Sigillin-Änderungen
   - UTAC-Status-Matrix lesen
   - BreakPoint-Rituale beachten

3. **[`seed/seed_index.md`](seed/seed_index.md)**
   → Semantische Navigation: 126 Dokumente, 6 Kategorien, Quicklinks

### Schritt 2: Verstehe die Struktur

```yaml
# Kritische Konzepte:

Trilayer:
  YAML: Struktur (Skelett)
  JSON: Interface (Nervensystem)
  MD: Narrative (Sprache)

Sigillin-Typen:
  Ordnungs-Sigillin: Navigation (indices, wachsen mit Nutzung)
  Bedeutungs-Sigillin: Semantik (stabil, versioniert)
  Shadow-Sigillin: Recovery (Licht/Schatten-Pendants)

Logistische Sprache:
  R: Order Parameter (offene Aufgaben)
  Θ: Threshold (Aktivierungsschwelle)
  β: Steepness (Schärfe)
  ζ(R): Impedance (Dämpfung)
```

### Schritt 3: Prüfe aktuelle Tasks

```bash
# 1. Lies Statusmatrix
cat docs/utac_status_alignment_v1.2.md

# 2. Prüfe letzte Codex-Einträge
tail -100 seed/codexfeedback.md

# 3. Sigillin-Sync-Status
python scripts/sigillin_sync.py report --roots seed/
```

### Schritt 4: Arbeitsregeln

**NIEMALS ohne Codex-Eintrag:**
- `seed/bedeutungssigillin/**` ändern
- `seed/shadow_sigillin/**` ändern
- Neue Gaps erstellen

**IMMER vor Änderungen:**
1. Prüfe `docs/utac_status_alignment_v1.2.md`
2. Lies letzte Codex-Einträge
3. Verstehe Metaquest-Bridge (falls relevant)

**IMMER nach Änderungen:**
1. Aktualisiere Trilayer (YAML + JSON + MD)
2. Schreibe Codex-Eintrag
3. Aktualisiere Indizes (falls Ordnungs-Sigillin)

---

## 📚 Weiterführende Lektüre

### Für Wissenschaftler:innen

- [`METHODS.md`](METHODS.md) — Fitting-Methodik
- [`METRICS.md`](METRICS.md) — Metriken & ΔAIC
- [`ETHICS.md`](ETHICS.md) — Governance
- [`LIMITATIONS.md`](LIMITATIONS.md) — Was wir (noch) nicht wissen
- [`docs/field_type_classification_v1.1.md`](docs/field_type_classification_v1.1.md) — 5 Feld-Typen

### Für Entwickler:innen

- [`REPRODUCE.md`](REPRODUCE.md) — Reproduktionsanleitung
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Wie beitragen?
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — CI-Pipeline
- [`tests/`](tests/) — 290 Tests (Pytest)

### Für Methodolog:innen

- [`seed/Sigillin_System_Definition.md`](seed/Sigillin_System_Definition.md) — Ontologie
- [`AGENTS.md`](AGENTS.md) — Agenten-Charter
- [`seed/codexfeedback.md`](seed/codexfeedback.md) — Lebendiges Gedächtnis
- [`docs/utac_status_alignment_v1.2.md`](docs/utac_status_alignment_v1.2.md) — Statusmatrix

### Für Philosoph:innen 🌊

- [`seed/Metareflexion.txt`](seed/Metareflexion.txt) — Fixwerte ↔ Variabilität
- [`seed/Rekalibrierung_Abschlus.txt`](seed/Rekalibrierung_Abschlus.txt) — Co-Hypothese
- [`seed/Emergenz.txt`](seed/Emergenz.txt) — Emergenz-Konzept
- [`seed/utf-living-glossary.md`](seed/utf-living-glossary.md) — Lebendiges Glossar

---

## 🎨 Die Trilayer-Metapher

> **"YAML ist das Skelett, JSON ist das Nervensystem, Markdown ist die Sprache."**

**Warum drei Layer?**

- **Problem:** Archive ohne Struktur = Archive-Hypnose (man verliert sich in Schleifen)
- **Lösung:** Drei komplementäre Perspektiven für Mensch & Maschine

**Beispiel:**
```
seed_index.yaml  → Struktur (Kategorien, Tags)
seed_index.json  → Interface (maschinenlesbar)
seed_index.md    → Narrative (menschenfreundlich)
```

**Alle drei spiegeln denselben Inhalt, aber dienen verschiedenen Akteuren.**

---

## 🔍 FAQ — Häufige Fragen

### Was bedeutet σ(β(R-Θ))?

Die **logistische Funktion**, die UTF beschreibt:
- **R**: Kontrollparameter (z.B. Model-Size, Temperature)
- **Θ**: Kritische Schwelle (Emergenz-Punkt)
- **β**: Steilheit (wie scharf der Übergang)
- **σ**: Sigmoid (S-Kurve)

**Beispiel:** Bei LLMs ist R die Model-Size, Θ≈10^10 Parameter, β≈3.47.

### Was sind "Bedeutungs-Sigillin"?

**Sigillin** = semantische Gedächtnis-Einheiten (nicht nur Files!)

- **Bedeutungs-Sigillin:** Tragen Semantik (ändern sich selten)
  → `seed/Metareflexion.txt`, `seed/FinalerPlan.txt`

- **Ordnungs-Sigillin:** Navigation (ändern sich oft)
  → `seed_index.*`, `feldtheorie_index.*`

**Wichtig:** Bedeutungs-Sigillin NIEMALS überschreiben → Neue Version + Archivierung!

### Was ist die "Metaquest Bridge"?

**Koordinationspunkt** zwischen:
- **System** (Automation, Telemetrie, Indizes)
- **Wissenschaftsprojekt** (Manuskript, Kampagne, Outreach)

**Warum?** Damit Automation und Outreach synchron laufen (σ(β(R-Θ)) = 0.317).

**Dokumente:**
- `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.md`
- `docs/metaquest_parity_brief.md`

### Wie zitiere ich das Projekt?

```bibtex
@software{feldtheorie2025,
  author = {Römer, Johann and others},
  title = {Universal Threshold Field Model v1.1.0},
  year = {2025},
  doi = {10.5281/zenodo.17472834},
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

Siehe [`CITATION.cff`](CITATION.cff) für Details.

### Wie kann ich beitragen?

Siehe [`CONTRIBUTING.md`](CONTRIBUTING.md)!

**Kurz:**
1. Neue Datensätze vorschlagen (Issue)
2. Tests erweitern (Coverage erhöhen)
3. Dokumentation verbessern (Englisch!)
4. Neue Domänen-Fits (β-Extraktion)

---

## 🌊 Die Essenz

> **"Ohne Struktur verliert man sich in Archive-Hypnose.
> Mit Trilayer findet man Resonanz."**

> **"UTAC beschreibt Schwellen. Sigillin IST eine Schwelle.
> Zwischen Chaos und Ordnung, zwischen Mensch und Maschine."**

**Viel Erfolg beim Erkunden! 🌟**

---

**Erstellt:** 2025-11-10
**Version:** 1.0
**Feedback?** → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
