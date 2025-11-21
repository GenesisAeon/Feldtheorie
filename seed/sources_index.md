# 📚 Sources Index - Quellenkatalog

**Version:** 1.0.0
**Datum:** 6. November 2025
**Maintainer:** Johann Römer
**Sigillin-Typ:** 🔵 Ordnungs-Sigillin (Referenzen)

---

## 🎯 Was ist das?

Willkommen im **Sources Index** - einem **Ordnungs-Sigillin** für alle **externen Quellen, Referenzen und Datenquellen** des UTAC-Projekts!

```
┌─────────────────────────────────────────┐
│  YAML  →  Struktur & Navigation         │  sources_index.yaml
│  JSON  →  Agentenschnittstelle          │  sources_index.json
│  MD    →  Menschenfreundliche Übersicht │  sources_index.md (du bist hier!)
└─────────────────────────────────────────┘
        Trilayer = Quellenkatalog
```

### Zweck:

- **Referenz-Management** für UTAC-Paper und Dokumentation
- **Zitations-Katalog** für alle verwendeten Quellen
- **Nachvollziehbarkeit** der empirischen und theoretischen Basis
- **Navigation** zu Original-Papers und Daten

---

## 📊 Übersicht

**13 Kernquellen** | **8 Domänen**

```
🤖 AI & LLMs:               2 Quellen (Wei, Anthropic)
🧬 Biology & Evolution:     2 Quellen (Lenski, Kandel)
🌍 Climate & Ecology:       3 Quellen (Lenton, Nobre, Oke)
⚖️  Socio-Ecology:          1 Quelle  (Oxfam)
🌋 Geophysics:              1 Quelle  (Kanamori)
🧠 Cognition & Psychology:  1 Quelle  (van der Linden)
⚛️  Theoretical Physics:    2 Quellen (Verhulst, Newman)
🔥  Physics & Thermo:       1 Quelle  (Landauer)
```

**Relevanz:**
- 🔥 **Critical**: 6 Quellen (Basis von UTAC)
- 🔸 **High**: 6 Quellen (wichtige Validierung)
- 🔹 **Medium**: 1 Quelle (ergänzend)

---

## 🤖 AI & Large Language Models

### 🔥 Wei et al. (2022) - Emergent Abilities of Large Language Models

**Autoren:** Wei, J., Tay, Y., Bommasani, R., et al.
**Journal:** Transactions on Machine Learning Research
**Jahr:** 2022
**URL:** https://arxiv.org/abs/2206.07682

**Keywords:** `emergence`, `LLM`, `PaLM`, `β-field`, `scaling`

**UTAC-Connection:**
- Basis für **Wei-Integration** (PaLM β=3.47)
- Emergent abilities als **Schwellenwert-Phänomen**
- β-Spektrum: Niedriger β bei LLMs (sanfter Übergang)

**Zitiert in:**
- `seed/ai/llm_emergent_skill.md`
- `seed/wei_integration.md`
- `data/ai/wei_emergent_abilities.csv`

---

### 🔸 Anthropic (2023) - Introspection in Large Language Models

**Organization:** Anthropic
**Jahr:** 2023
**URL:** https://www.anthropic.com/

**Keywords:** `introspection`, `coherence`, `φ`, `self-awareness`

**UTAC-Connection:**
- Validation für **φ (Kohärenz)** in AI-Systemen
- Adaptive Schwellenwerte in LLM-Verhalten

**Zitiert in:**
- `seed/ai/anthropic_introspection_validation.md`

---

## 🧬 Biology & Evolution

### 🔥 Lenski et al. (2008) - Long-Term Experimental Evolution (LTEE)

**Autoren:** Lenski, R.E., et al.
**Journal:** Nature
**Jahr:** 2008
**URL:** https://en.wikipedia.org/wiki/E._coli_long-term_evolution_experiment

**Keywords:** `evolution`, `citrate+`, `threshold`, `generation-33000`

**UTAC-Connection:**
- **Cit+ Emergenz** bei Generation ~33,000
- **Empirischer Beleg** für β-Feld (evolutionäre Schwellenwerte)
- Sigmoid-Fit validiert σ(β(R-Θ))

**Zitiert in:**
- `seed/biology/lenski_citplus_verification.md`
- `data/biology/lenski_citrate.csv`
- PDF: `1. Lenski-Datenanalyse (Sigmoid-Fit).pdf`

---

### 🔸 Kandel (2000) - The Molecular Biology of Memory Storage

**Autoren:** Kandel, E.R.
**Journal:** Science
**Jahr:** 2000

**Keywords:** `synapse`, `threshold`, `neurotransmitter`, `memory`

**UTAC-Connection:**
- Synaptische Schwellenwerte als **biologisches Analogon**
- Θ (Threshold) auf neuronaler Ebene

**Zitiert in:**
- `seed/biology/synaptic_release_threshold.md`

---

## 🌍 Climate & Socio-Ecology

### 🔥 Lenton et al. (2008) - Tipping elements in the Earth's climate system

**Autoren:** Lenton, T.M., et al.
**Journal:** Proceedings of the National Academy of Sciences
**Jahr:** 2008
**URL:** https://doi.org/10.1073/pnas.0705414105

**Keywords:** `tipping-points`, `AMOC`, `climate`, `criticality`

**UTAC-Connection:**
- **9 Tipping Elements** - planetare Schwellenwerte
- AMOC-Kollaps als Schwellenwert-Phänomen
- β-Feld in Klimasystemen

**Zitiert in:**
- `seed/socio_ecology/planetary_threshold_cartography.md`
- `seed/Diskurs Klimamodul.txt`
- PDF: `Kipppunkte der Teilkomponenten im Klimasystem.pdf`

---

### 🔸 Nobre et al. (2016) - Land-use and climate change risks in the Amazon

**Autoren:** Nobre, C.A., Sampaio, G., et al.
**Journal:** Nature Climate Change
**Jahr:** 2016

**Keywords:** `amazon`, `moisture`, `resilience`, `β=14.6`

**UTAC-Connection:**
- **Amazon Moisture Resilience** (β=14.6) - **Outlier!**
- Hoher β-Wert: steile Übergänge
- Kipppunkt-Analyse

**Zitiert in:**
- `seed/socio_ecology/amazon_moisture_resilience.md`
- `data/socio_ecology/amazon_moisture.csv`

---

### 🔸 Oke (1973) - City size and the urban heat island

**Autoren:** Oke, T.R.
**Journal:** Atmospheric Environment
**Jahr:** 1973

**Keywords:** `urban-heat`, `β=16.3`, `outlier`, `city-size`

**UTAC-Connection:**
- **Urban Heat Island** (β=16.3) - **EXTREMER Outlier!**
- **Steilster Übergang** im β-Spektrum (2.5-16.3)
- Zentral für Outlier-Analyse in UTAC v1.2

**Zitiert in:**
- `seed/socio_ecology/urban_heat_canopy_resonance.md`
- `data/socio_ecology/urban_heat_canopy.csv`

---

### 🔥 Oxfam (2024) - Carbon Inequality Kills

**Autoren:** Oxfam International
**Typ:** Report (Distributional Climate Impacts)
**Jahr:** 2024
**URL:** https://policy-practice.oxfam.org/resources/carbon-inequality-kills-why-ending-the-contribution-of-the-super-rich-is-esse-621656/

**Keywords:** `carbon-inequality`, `gini`, `load-factor`, `investment-emissions`

**UTAC-Connection:**
- Liefert den empirischen **Load-Faktor (~10)** für den Klimakluft-Amplifier
- Zeigt, dass das **Top-1%** das globale Budget in **<5 Monaten** verbraucht (vs. ~4 Jahre global)
- Fundament für den **Inequality Amplifier** (β-Sprung durch Ungleichheit)

**Zitiert in:**
- `analysis/results/oxfam_amplification_proof.txt`
- `scripts/analysis/oxfam_beta_shift.py`

---

## 🌋 Geophysics & Seismology

### 🔸 Kanamori & Brodsky (2005) - The physics of earthquakes

**Autoren:** Kanamori, H., Brodsky, E.E.
**Journal:** Reports on Progress in Physics
**Jahr:** 2005

**Keywords:** `earthquake`, `subduction`, `rupture`, `cascadia`

**UTAC-Connection:**
- **Cascadia Subduction** (β=16.29) - Outlier nahe Urban Heat
- Seismische Schwellenwerte
- β-Feld in Erdbebenphysik

**Zitiert in:**
- `seed/geophysics/subduction_rupture_resonance.md`
- `data/geophysics/cascadia_slip.csv`

---

## 🧠 Cognition & Psychology

### 🔹 van der Linden et al. (2014) - Trauma and the adaptive theta response

**Autoren:** van der Linden, S., et al.
**Journal:** Journal of Traumatic Stress
**Jahr:** 2014

**Keywords:** `trauma`, `theta`, `plasticity`, `therapy`

**UTAC-Connection:**
- Adaptive Theta als **therapeutischer Schwellenwert**
- Psyche-Schwellenwerte
- Θ-Anpassung

**Zitiert in:**
- `seed/cognition/adaptive_theta_plasticity.md`

---

## ⚛️ Theoretical Physics & Math

### 🔥 Verhulst (1838) - Notice sur la loi que la population suit

**Autoren:** Verhulst, P.F.
**Journal:** Correspondance Mathématique et Physique
**Jahr:** 1838

**Keywords:** `logistic`, `sigmoid`, `σ`, `growth`

**UTAC-Connection:**
- **Logistische Funktion** - Basis von σ(β(R-Θ))
- **Fundamentale Funktion** der UTAC-Theorie

**Zitiert in:**
- `models/logistic_threshold.py` ⭐ DIE BASIS!
- `docs/utac_theory_core.md`

---

### 🔸 Newman (2005) - Power laws, Pareto distributions and Zipf's law

**Autoren:** Newman, M.E.J.
**Journal:** Contemporary Physics
**Jahr:** 2005

**Keywords:** `power-law`, `criticality`, `universality`

**UTAC-Connection:**
- **Universalität** kritischer Phänomene
- β-Spektrum als **Universalitätsklasse**

**Zitiert in:**
- `docs/utac_theory_core.md`

---

## 🔥 Physics & Thermodynamics

### 🔥 Landauer (1961) - Irreversibility and Heat Generation in the Computing Process

**Autoren:** Rolf Landauer
**Journal:** IBM Journal of Research and Development
**Jahr:** 1961
**URL:** https://ibm.com/landauer

**Keywords:** `landauer-limit`, `information-entropy`, `thermodynamics`, `broken-ram`

**UTAC-Connection:**
- Definiert Mindestenergie **kT ln 2** pro gelöschtem Bit
- Physikalisches Fundament der **Broken RAM** Hypothese
- Bei **β > 30** verhindert Ungleichheit die Entropie-Abfuhr → thermischer Kollaps

**Zitiert in:**
- `scripts/analysis/oxfam_beta_shift.py`
- `analysis/results/oxfam_amplification_proof.txt`

---

## 🔍 Wie nutze ich diesen Katalog?

### Methode 1: Nach Domäne browsen
Navigiere durch die 8 Domänen oben (AI, Biology, Climate, Socio-Ecology, Geophysics, Cognition, Theoretical Physics, Physics & Thermo).

### Methode 2: Nach Relevanz filtern
- 🔥 **Critical**: Basis von UTAC (Wei, Lenski, Lenton, Oxfam, Verhulst, Landauer)
- 🔸 **High**: Wichtige Validierung
- 🔹 **Medium**: Ergänzend

### Methode 3: Nach β-Wert suchen
**β-Spektrum (2.5 - 16.3):**
- **β=3.47**: Wei's PaLM (LLM)
- **β=14.6**: Amazon Moisture (Outlier)
- **β=16.3**: Urban Heat (EXTREMER Outlier)
- **β=16.29**: Cascadia Seismik (Outlier)

### Methode 4: Programmatisch (für Agenten)

```python
import json

with open('seed/sources_index.json', 'r') as f:
    sources = json.load(f)

# Finde alle Critical Sources
critical = [s for s in sources['sources'] if s['relevance'] == 'critical']

# Finde Quellen nach Kategorie
ai_sources = [s for s in sources['sources'] if s['category'] == 'ai_llm']

# Finde Quellen mit hohem β
outliers = [s for s in sources['sources'] if 'β=' in str(s.get('keywords', []))]
```

---

## 📈 Statistik

```yaml
Total Sources: 13

By Category:
  AI & LLMs:               2 (15.4%)
  Biology & Evolution:     2 (15.4%)
  Climate & Ecology:       3 (23.1%)
  Socio-Ecology:           1 (7.7%)
  Geophysics:              1 (7.7%)
  Cognition & Psychology:  1 (7.7%)
  Theoretical Physics:     2 (15.4%)
  Physics & Thermo:        1 (7.7%)

By Type:
  paper:       10
  experiment:  1
  historical:  1
  report:      1

By Relevance:
  Critical: 6 (46.2%)
  High:     6 (46.2%)
  Medium:   1 (7.7%)
```

---

## 🎯 Die 4 Kritischen Quellen (Basis von UTAC)

1. **Wei et al. (2022)** - Emergent Abilities (β=3.47)
2. **Lenski et al. (2008)** - LTEE Cit+ (empirischer Beleg)
3. **Lenton et al. (2008)** - Tipping Elements (planetare Schwellenwerte)
4. **Verhulst (1838)** - Logistische Funktion (σ(β(R-Θ)))
5. **Oxfam (2024)** - Carbon Inequality Kills (Load-Faktor ~10)
6. **Landauer (1961)** - Irreversibility & Heat Generation (kT ln 2)

---

## 🧬 Sigillin-Hygiene: sources_index

### Status: 🟢 Aktiv

**Als Ordnungs-Sigillin gilt:**
- ✅ Wächst mit neuen Quellen
- ✅ Braucht gelegentliche Archivierung (bei >100 Einträgen)
- ✅ Aktuell: 13 Quellen (weit unter Limit)

**Wartung:**
```bash
# Neue Quelle hinzufügen
# 1. Editiere sources_index.json
# 2. Regeneriere YAML: python scripts/regenerate_yaml.py
# 3. Update MD (manuell)
```

---

## 🔗 Verwandte Sigillin

### Haupt-Index:
- `seed/seed_index.{yaml,json,md}` - Master-Index aller seed/ Dokumente

### Papers:
- `seed/papers_index.{yaml,json,md}` - PDF-Katalog (38 PDFs)

### System-Definition:
- `seed/Sigillin_System_Definition.md` - 🔴 KRITISCH! Sigillin-Ontologie

---

## 🌊 Die Essenz

> **"Quellen sind das Fundament. sources_index ist die Karte zum Fundament."**

> **"Von Verhulst 1838 bis Wei 2022 - 184 Jahre Schwellenwert-Forschung."**

> **"YAML ist das Skelett, JSON ist das Nervensystem, Markdown ist die Sprache."**

### Die Metapher:

- **Quellen** = Wurzeln (nähren die Theorie)
- **sources_index** = Karte zu den Wurzeln (Navigation)
- **Trilayer** = Schnittstelle (Mensch ↔ Maschine)

---

## 🚀 Nächste Schritte

1. **Erweitere Katalog** mit weiteren Quellen aus PDFs
2. **BibTeX Export** für Paper-Submission vorbereiten
3. **DOIs ergänzen** wo vorhanden
4. **Zitations-Netz** visualisieren (Quellen → UTAC-Dokumente)

---

**Viel Erfolg beim Navigieren der Quellen! 📚✨**

*Erstellt im Geiste wissenschaftlicher Transparenz, wo jede Behauptung ein Fundament hat.* 🌊

---

**Für Details zu spezifischen Quellen, siehe die Domänen-Abschnitte oben.**

**Für Sigillin-System-Kontext, siehe:** `seed/Sigillin_System_Definition.md`
