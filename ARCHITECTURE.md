# Feldtheorie Architecture Documentation

> **Purpose:** Visual guide to the repository structure, information flows, and system interactions.

**Version:** 1.0
**Updated:** 2025-11-10
**Audience:** Developers, contributors, architects

---

## Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [The Trilayer System](#the-trilayer-system)
3. [Sigillin Memory Architecture](#sigillin-memory-architecture)
4. [Code Architecture](#code-architecture)
5. [Information Flows](#information-flows)
6. [Metaquest Bridge](#metaquest-bridge)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Data Flow](#data-flow)

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FELDTHEORIE REPOSITORY                           │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   UTAC/UTF       │  │ Sigillin System  │  │       MOR        │ │
│  │   (Science)      │◄─┤   (Method)       │─►│   (Process)      │ │
│  │                  │  │                  │  │                  │ │
│  │ σ(β(R-Θ))       │  │ Trilayer:        │  │ Multi-Agent      │ │
│  │ Field Types      │  │ YAML+JSON+MD     │  │ Collaboration    │ │
│  │ ΔAIC ≥ 10       │  │ Ordnung/Bedeutung│  │ Johann+Claude+…  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│           │                     │                      │           │
│           └─────────────────────┴──────────────────────┘           │
│                              │                                     │
│                    Co-Hypothese: All three                         │
│                    layers co-constitute                            │
│                    each other                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Trilayer System

### Concept: Three Synchronized Representations

Every important document exists in **three synchronized formats**:

```
┌──────────────────────────────────────────────────────────┐
│                    TRILAYER PRINCIPLE                     │
│                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌────────────┐ │
│  │    YAML     │     │    JSON     │     │  Markdown  │ │
│  │  (Skelett)  │────►│ (Nerven-    │────►│  (Stimme)  │ │
│  │             │     │  system)    │     │            │ │
│  │ Structure   │     │ Interface   │     │ Narrative  │ │
│  │ Hierarchy   │     │ Machine API │     │ Human-read │ │
│  │ Navigation  │     │ Agents      │     │ Context    │ │
│  └─────────────┘     └─────────────┘     └────────────┘ │
│        ▲                    ▲                   ▲        │
│        │                    │                   │        │
│        └────────────────────┴───────────────────┘        │
│                   Must stay synchronized!                │
│                  (checked by sigillin_sync.py)           │
└──────────────────────────────────────────────────────────┘
```

### Example: seed_index Trilayer

```
seed/
├── seed_index.yaml      ← Structure (categories, tags)
│   {
│     categories: [...]
│     documents: [...]
│   }
│
├── seed_index.json      ← Interface (machine-parseable)
│   {
│     "version": "1.0",
│     "documents": [
│       {...}
│     ]
│   }
│
└── seed_index.md        ← Narrative (human-browseable)
    # Seed Index
    ## Categories
    - Category 1
      - Document A
```

**Synchronization Check:**
```bash
python scripts/sigillin_sync.py report --roots seed/
# Output: gaps: 0 → ✅ Synchronized
```

---

## Sigillin Memory Architecture

### Two Types: Ordnung (Navigation) vs. Bedeutung (Semantics)

```
┌────────────────────────────────────────────────────────────────────┐
│                    SIGILLIN ARCHITECTURE                           │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              ORDNUNGS-SIGILLIN (Navigation)                │   │
│  │                                                            │   │
│  │  Purpose: Help you find things                            │   │
│  │  Changes: Frequently (with every addition)                │   │
│  │  Example: Indices, catalogs                               │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ seed_index.* │  │ docs_index.* │  │feldtheorie_  │   │   │
│  │  │              │  │              │  │   index.*    │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  │                                                            │   │
│  │  Metaphor: Nerve pathways (guide, don't store)           │   │
│  │  Maintenance: Archive when > 100 entries or > 50 KB      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              │ Reference/Point to                  │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           BEDEUTUNGS-SIGILLIN (Semantics)                  │   │
│  │                                                            │   │
│  │  Purpose: Store stable knowledge                          │   │
│  │  Changes: Rarely (semantic stability)                     │   │
│  │  Example: Theory docs, concepts, principles               │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │Metareflexion │  │ FinalerPlan  │  │  Sigillin    │   │   │
│  │  │   .txt       │  │    .txt      │  │ System Def   │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  │                                                            │   │
│  │  Metaphor: Synapses (encode patterns, connections)       │   │
│  │  Maintenance: NEVER overwrite! Create new version         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  Rule: Every Bedeutungs-Sigillin change requires Codex entry!     │
└────────────────────────────────────────────────────────────────────┘
```

### Light/Shadow System

```
┌──────────────────────────────────────────────────────────────┐
│               LIGHT / SHADOW ARCHITECTURE                     │
│                                                              │
│  For every primary component (Light), there's a             │
│  corresponding recovery playbook (Shadow)                    │
│                                                              │
│  seed/                                                       │
│  ├── bedeutungssigillin/          ← LIGHT (Primary)         │
│  │   ├── system/                                            │
│  │   │   └── system_meaning_map.* ────┐                    │
│  │   │                                 │                    │
│  │   ├── wissenschaftsprojekt/         │ Mirrors            │
│  │   │   └── campaign_meaning_map.*────┤                    │
│  │   │                                 │                    │
│  │   └── metaquest/                    │                    │
│  │       └── metaquest_meaning_index.* │                    │
│  │                                     │                    │
│  └── shadow_sigillin/            ← SHADOW (Recovery)        │
│      ├── system/                       │                    │
│      │   └── system_shadow_map.* ◄─────┘                    │
│      │                                                       │
│      ├── wissenschaftsprojekt/                              │
│      │   └── campaign_shadow_guard.*                        │
│      │                                                       │
│      └── metaquest/                                         │
│          └── metaquest_shadow_guard.*                       │
│                                                              │
│  When a Shadow alarm fires (sys-shadow-001, etc.):          │
│    1. Read corresponding shadow file                        │
│    2. Follow "Playbook" section                             │
│    3. Update Codex with recovery action                     │
│    4. Verify fix with CI                                    │
└──────────────────────────────────────────────────────────────┘
```

### Codex Feedback: Living Memory

```
┌──────────────────────────────────────────────────────────────┐
│                  CODEX FEEDBACK SYSTEM                        │
│                                                              │
│  seed/codexfeedback.{yaml,json,md}                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Entry pr-draft-0001                                 │   │
│  │  ├─ Scope: What changed                             │   │
│  │  ├─ (R, Θ, β): Logistic parameters                  │   │
│  │  ├─ Formal Thread:   Technical details              │   │
│  │  ├─ Empirical Thread: Metrics, evidence             │   │
│  │  ├─ Poetic Thread:    Narrative context             │   │
│  │  └─ Timestamp: ISO 8601                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                        │                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Entry pr-draft-0002                                 │   │
│  │  └─ ...                                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                        │                                     │
│                       ...                                    │
│                        │                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Entry pr-draft-0113 (latest as of 2025-11-10)      │   │
│  │  └─ ...                                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Total: 119 entries                                          │
│  Function: Git log + Changelog + Project journal            │
│  Enforced by: .github/workflows/codex-guard.yml             │
└──────────────────────────────────────────────────────────────┘
```

---

## Code Architecture

### Directory Structure

```
Feldtheorie/
│
├── analysis/              ← Python analysis scripts
│   ├── beta_meta_regression_v2.py      (Meta-regression)
│   ├── llm_beta_extractor.py           (LLM fits)
│   ├── climate_beta_extractor.py       (Climate fits)
│   ├── resonance_fit_pipeline.py       (General pipeline)
│   └── results/                        (JSON outputs)
│       ├── llm_beta_extractor.json
│       ├── climate_beta_summary.json
│       └── ...
│
├── models/                ← Numerical solvers
│   ├── membrane_solver.py              (Main solver)
│   ├── coupled_threshold_field.py      (Coupled fields)
│   ├── logistic_envelope.py            (Envelope dynamics)
│   ├── coherence_term.py               (Semantic coupling)
│   └── resonant_impedance.py           (ζ(R) profiles)
│
├── data/                  ← Datasets + metadata
│   ├── ai/                             (LLM datasets)
│   │   ├── wei_emergent_abilities.csv
│   │   └── wei_emergent_abilities.metadata.json
│   ├── climate/                        (Climate datasets)
│   ├── cognition/                      (Cognition datasets)
│   ├── astrophysics/                   (QPO, etc.)
│   └── derived/                        (β-estimates, covariates)
│       ├── beta_estimates.csv
│       └── domain_covariates.csv
│
├── tests/                 ← 290 pytest tests
│   ├── test_membrane_solver.py
│   ├── test_llm_beta_extractor.py
│   ├── test_sigillin_sync.py (planned)
│   └── ...
│
├── scripts/               ← Automation & utilities
│   ├── reproduce_beta.py               (Reproduce fits)
│   ├── sigillin_sync.py                (Check trilayer sync)
│   ├── archive_sigillin.py             (Archive management)
│   └── crep_parser.py                  (CREP validation)
│
├── seed/                  ← Semantic memory
│   ├── bedeutungssigillin/             (Meaning layer)
│   ├── shadow_sigillin/                (Recovery layer)
│   ├── codexfeedback.*                 (Project memory)
│   ├── seed_index.*                    (Navigation)
│   └── utf-living-glossary.md          (Vocabulary)
│
├── docs/                  ← Documentation
│   ├── utac_status_alignment_v1.2.md   (Status matrix)
│   ├── metaquest_parity_brief.md       (Sync checklist)
│   ├── field_type_classification_v1.1.md
│   └── ...
│
├── .github/workflows/     ← CI/CD
│   ├── ci.yml                          (Main CI)
│   ├── tests.yml                       (Test suite)
│   ├── sigillin-health.yml             (Trilayer checks)
│   └── codex-guard.yml                 (Codex enforcement)
│
├── QUICKSTART.md          ← 5-minute onboarding
├── AGENTS.md              ← AI agent charter (poetic)
├── AGENTS_PLAIN.md        ← AI agent charter (plain)
├── ARCHITECTURE.md        ← This document!
└── README.md              ← Project overview
```

### Module Dependencies

```
┌───────────────────────────────────────────────────────────────┐
│                    MODULE DEPENDENCY GRAPH                     │
│                                                               │
│  analysis/                                                    │
│  ├─ llm_beta_extractor.py                                    │
│  │  └─► models.sigmoid_fit (logistic fitting)               │
│  │  └─► data/ai/wei_emergent_abilities.csv                  │
│  │                                                            │
│  ├─ beta_meta_regression_v2.py                               │
│  │  └─► data/derived/beta_estimates.csv                     │
│  │  └─► data/derived/domain_covariates.csv                  │
│  │  └─► sklearn, statsmodels (external)                     │
│  │                                                            │
│  └─ resonance_fit_pipeline.py                                │
│     └─► models.membrane_solver                               │
│     └─► models.coupled_threshold_field                       │
│                                                               │
│  models/                                                      │
│  ├─ membrane_solver.py                                       │
│  │  └─► coherence_term.semantic_coupling_term               │
│  │  └─► resonant_impedance                                  │
│  │                                                            │
│  ├─ coupled_threshold_field.py                               │
│  │  └─► membrane_solver (composition)                       │
│  │                                                            │
│  └─ sigmoid_fit.py                                           │
│     └─► scipy.optimize.curve_fit                            │
│                                                               │
│  scripts/                                                     │
│  ├─ sigillin_sync.py                                         │
│  │  └─► yaml, json (stdlib/external)                        │
│  │  └─► seed/bedeutungssigillin/**                          │
│  │  └─► seed/shadow_sigillin/**                             │
│  │                                                            │
│  └─ reproduce_beta.py                                        │
│     └─► analysis.llm_beta_extractor (or others)             │
│                                                               │
│  tests/                                                       │
│  └─► All modules (test everything)                           │
└───────────────────────────────────────────────────────────────┘
```

---

## Information Flows

### 1. Data → Analysis → Results Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE                               │
│                                                                 │
│  ┌─────────────┐                                               │
│  │  Raw Data   │                                               │
│  │  CSV files  │                                               │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                               │
│  │  Metadata   │  ← .metadata.json (provenance, license)      │
│  │  Validation │                                               │
│  └──────┬──────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                   │
│  │  analysis/*_extractor.py                │                   │
│  │  ├─ Load CSV                            │                   │
│  │  ├─ Normalize (0-1 or log-transform)    │                   │
│  │  ├─ Fit σ(β(R-Θ))                      │                   │
│  │  ├─ Fit null models (linear, power-law) │                   │
│  │  ├─ Compute ΔAIC, R², Bootstrap CI      │                   │
│  │  └─ Export JSON                          │                   │
│  └──────┬──────────────────────────────────┘                   │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐                                           │
│  │ analysis/results/│  ← JSON outputs                          │
│  │ *.json          │     {β, Θ, ΔAIC, R², CI, ...}            │
│  └──────┬──────────┘                                           │
│         │                                                       │
│         ├──────► Manuscript (paper/)                           │
│         ├──────► Simulator (simulator/presets/)                │
│         └──────► Meta-regression (beta_meta_regression_v2.py)  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Codex Update Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  CODEX UPDATE WORKFLOW                        │
│                                                              │
│  Developer makes change                                      │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────┐                                   │
│  │ Is it a Bedeutungs-  │                                   │
│  │ Sigillin change?     │                                   │
│  └──┬───────────────┬───┘                                   │
│     │ NO            │ YES                                   │
│     │               │                                       │
│     ▼               ▼                                       │
│  Commit      ┌────────────────┐                            │
│  directly    │ Create Codex   │                            │
│              │ entry in       │                            │
│              │ seed/          │                            │
│              │ codexfeedback.*│                            │
│              │                │                            │
│              │ Format:        │                            │
│              │ - ID: pr-draft-│                            │
│              │   XXXX         │                            │
│              │ - Scope        │                            │
│              │ - (R,Θ,β)     │                            │
│              │ - Formal       │                            │
│              │ - Empirical    │                            │
│              │ - Poetic       │                            │
│              │ - Timestamp    │                            │
│              └────┬───────────┘                            │
│                   │                                         │
│                   ▼                                         │
│              Update all 3 layers:                          │
│              - codexfeedback.yaml                          │
│              - codexfeedback.json                          │
│              - codexfeedback.md                            │
│                   │                                         │
│                   ▼                                         │
│              Commit together                               │
│                   │                                         │
│                   ▼                                         │
│              Push to remote                                │
│                   │                                         │
│                   ▼                                         │
│         ┌─────────────────────┐                            │
│         │ CI: codex-guard.yml │                            │
│         │ Checks:             │                            │
│         │ - Bedeutungs-Sigillin│                           │
│         │   changed?          │                            │
│         │ - codexfeedback.*   │                            │
│         │   updated?          │                            │
│         └────┬────────────────┘                            │
│              │                                              │
│         ┌────┴────┐                                        │
│    PASS │         │ FAIL                                   │
│         ▼         ▼                                        │
│       Merge   Block PR                                     │
│               (sys-shadow-002)                             │
└──────────────────────────────────────────────────────────────┘
```

### 3. Trilayer Synchronization Flow

```
┌───────────────────────────────────────────────────────────────┐
│              TRILAYER SYNC CHECK (CI)                         │
│                                                               │
│  Git push                                                     │
│     │                                                         │
│     ▼                                                         │
│  ┌─────────────────────────────────┐                         │
│  │ .github/workflows/              │                         │
│  │ sigillin-health.yml             │                         │
│  │                                 │                         │
│  │ Runs:                           │                         │
│  │ python scripts/sigillin_sync.py │                         │
│  │   report --roots seed/          │                         │
│  └──────────┬──────────────────────┘                         │
│             │                                                 │
│             ▼                                                 │
│  ┌──────────────────────────┐                                │
│  │ Check each trilayer:     │                                │
│  │                          │                                │
│  │ For base_name in files:  │                                │
│  │   - Does .yaml exist?    │                                │
│  │   - Does .json exist?    │                                │
│  │   - Does .md exist?      │                                │
│  │                          │                                │
│  │   - version match?       │                                │
│  │   - updated match?       │                                │
│  │   - sigil match?         │                                │
│  └──────────┬───────────────┘                                │
│             │                                                 │
│        ┌────┴────┐                                           │
│    gaps=0 │      │ gaps>0                                    │
│           ▼      ▼                                           │
│         PASS   FAIL                                          │
│                 │                                            │
│                 └──► CI fails with message:                  │
│                      "Trilayer gaps detected!                │
│                       Please sync YAML/JSON/MD"              │
└───────────────────────────────────────────────────────────────┘
```

---

## Metaquest Bridge

The **Metaquest Bridge** coordinates between **System** (automation) and **Wissenschaftsprojekt** (campaign).

```
┌────────────────────────────────────────────────────────────────────┐
│                    METAQUEST BRIDGE ARCHITECTURE                    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   METAQUEST BRIDGE                           │ │
│  │           (Central Coordination Point)                       │ │
│  │                                                              │ │
│  │  seed/bedeutungssigillin/metaquest/                         │ │
│  │  └── metaquest_meaning_index.*                              │ │
│  │                                                              │ │
│  │  Function: Synchronize timestamps, codex IDs, telemetry     │ │
│  │  Metric: σ(β(R-Θ)) ≈ 0.317 (partial sync)                  │ │
│  └───────────┬────────────────────────────┬────────────────────┘ │
│              │                            │                      │
│              │                            │                      │
│      ┌───────▼────────┐          ┌───────▼────────┐            │
│      │   SYSTEM       │          │ WISSENSCHAFTS- │            │
│      │  (Automation)  │          │    PROJEKT     │            │
│      │                │          │  (Campaign)    │            │
│      │ ┌────────────┐ │          │ ┌────────────┐ │            │
│      │ │  Compass   │ │          │ │  Compass   │ │            │
│      │ │            │ │          │ │            │ │            │
│      │ │ Status:    │ │          │ │ Status:    │ │            │
│      │ │ - Scripts  │ │          │ │ - Paper    │ │            │
│      │ │ - CI       │ │          │ │ - Outreach │ │            │
│      │ │ - Indices  │ │          │ │ - Zenodo   │ │            │
│      │ │ - Tests    │ │          │ │ - arXiv    │ │            │
│      │ └────────────┘ │          │ └────────────┘ │            │
│      │                │          │                │            │
│      │ ┌────────────┐ │          │ ┌────────────┐ │            │
│      │ │ Meaning    │ │          │ │ Meaning    │ │            │
│      │ │ Map        │ │          │ │ Map        │ │            │
│      │ │            │ │          │ │            │ │            │
│      │ │ Details:   │ │          │ │ Details:   │ │            │
│      │ │ - Lanterns │ │          │ │ - Lanterns │ │            │
│      │ │ - Gaps     │ │          │ │ - Gaps     │ │            │
│      │ │ - Impl.    │ │          │ │ - Roadmap  │ │            │
│      │ └────────────┘ │          │ └────────────┘ │            │
│      │                │          │                │            │
│      │ ┌────────────┐ │          │ ┌────────────┐ │            │
│      │ │ Shadow     │ │          │ │ Shadow     │ │            │
│      │ │ Guard      │ │          │ │ Guard      │ │            │
│      │ │            │ │          │ │            │ │            │
│      │ │ Recovery:  │ │          │ │ Recovery:  │ │            │
│      │ │ - Alarms   │ │          │ │ - Alarms   │ │            │
│      │ │ - Playbooks│ │          │ │ - Playbooks│ │            │
│      │ └────────────┘ │          │ └────────────┘ │            │
│      └────────────────┘          └────────────────┘            │
│              │                            │                      │
│              └────────────┬───────────────┘                      │
│                           │                                      │
│                ┌──────────▼──────────┐                          │
│                │  Parity Brief       │                          │
│                │                     │                          │
│                │  Checks:            │                          │
│                │  1. Telemetry sync  │                          │
│                │  2. Simulator sync  │                          │
│                │  3. Endorsement log │                          │
│                │  4. Codex mirror    │                          │
│                └─────────────────────┘                          │
│                                                                  │
│  When Bridge detects drift → Shadow alarm fires                 │
│  → Consult recovery playbook → Update Codex                     │
└────────────────────────────────────────────────────────────────────┘
```

### Metaquest Sync Workflow

```
System Update (e.g., script runs):
  1. scripts/sigillin_sync.py executed
  2. Timestamp: 2025-11-07T21:52:52Z
  3. Write to: analysis/sigillin_sync/latest.json
  4. Update Bridge: metaquest_meaning_index.md
  5. Update System Compass
     │
     ▼
Campaign checks Bridge
     │
     ▼
Sees timestamp → ✅ Both sides know same state

Campaign Update (e.g., manuscript revised):
  1. Edit: paper/manuscript_v1.0.tex
  2. Create Codex entry: pr-draft-XXXX
  3. Update Bridge with codex ID
  4. Update Campaign Compass
     │
     ▼
System checks Bridge
     │
     ▼
Sees codex ID → ✅ Both sides know same state
```

---

## CI/CD Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                        CI/CD ARCHITECTURE                         │
│                                                                  │
│  GitHub Push / Pull Request                                      │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  .github/workflows/ci.yml (Main CI)                        │ │
│  │  ├─ Lint (ruff, black --check)                            │ │
│  │  ├─ Tests (pytest -q)                                     │ │
│  │  ├─ Type check (mypy, optional)                           │ │
│  │  └─ Coverage (coverage run -m pytest)                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  .github/workflows/tests.yml (Enhanced Tests)              │ │
│  │  ├─ Create venv                                            │ │
│  │  ├─ Install requirements.txt                              │ │
│  │  ├─ pytest tests/ -v --cov (290 tests)                    │ │
│  │  └─ Check coverage threshold (≥29%)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  .github/workflows/sigillin-health.yml (Trilayer)          │ │
│  │  ├─ Run sigillin_sync.py report                           │ │
│  │  ├─ Parse gaps from JSON output                           │ │
│  │  ├─ Fail if gaps > 0                                      │ │
│  │  └─ Run archive_sigillin.py --recount                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  .github/workflows/codex-guard.yml (Codex Check)           │ │
│  │  ├─ Detect Bedeutungs-Sigillin changes                    │ │
│  │  ├─ Check if codexfeedback.* updated                      │ │
│  │  ├─ Fail if not (sys-shadow-002)                          │ │
│  │  └─ Verify new entry format                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                      │
│           ▼                                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  .github/workflows/resonance-ci.yml (Optional)             │ │
│  │  └─ Additional resonance checks                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                      │
│      ┌────┴────┐                                                │
│   ALL PASS │   │ ANY FAIL                                       │
│            ▼   ▼                                                │
│          ✅    ❌                                                │
│        Merge   Block                                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Complete Data Journey

```
┌─────────────────────────────────────────────────────────────────────┐
│                     COMPLETE DATA JOURNEY                           │
│                                                                     │
│  1. DATA ACQUISITION                                                │
│     │                                                               │
│     ▼                                                               │
│  ┌──────────────┐                                                  │
│  │ External     │  (Wei 2022, Lenski LTEE, Climate datasets...)   │
│  │ Sources      │                                                  │
│  └──────┬───────┘                                                  │
│         │                                                           │
│         ▼                                                           │
│  2. DATA CURATION                                                   │
│     │                                                               │
│  ┌──────────────────────────────────────┐                          │
│  │ data/<domain>/<dataset>.csv          │                          │
│  │ data/<domain>/<dataset>.metadata.json│                          │
│  │                                      │                          │
│  │ Metadata includes:                   │                          │
│  │ - provenance (source, license)       │                          │
│  │ - variables (R, response, units)     │                          │
│  │ - preprocessing notes                │                          │
│  └──────┬───────────────────────────────┘                          │
│         │                                                           │
│         ▼                                                           │
│  3. ANALYSIS                                                        │
│     │                                                               │
│  ┌──────────────────────────────────────┐                          │
│  │ analysis/*_extractor.py              │                          │
│  │                                      │                          │
│  │ Steps:                               │                          │
│  │ 1. Load CSV + metadata               │                          │
│  │ 2. Preprocess (normalize, log)       │                          │
│  │ 3. Fit logistic: σ(β(R-Θ))         │                          │
│  │ 4. Fit nulls: linear, power, exp    │                          │
│  │ 5. Bootstrap β (1000 iterations)     │                          │
│  │ 6. Compute ΔAIC, R²                 │                          │
│  │ 7. Export JSON                       │                          │
│  └──────┬───────────────────────────────┘                          │
│         │                                                           │
│         ▼                                                           │
│  4. RESULTS STORAGE                                                 │
│     │                                                               │
│  ┌──────────────────────────────────────┐                          │
│  │ analysis/results/<dataset>.json      │                          │
│  │                                      │                          │
│  │ Contains:                            │                          │
│  │ - β, Θ, L (fit parameters)          │                          │
│  │ - β_ci (confidence interval)         │                          │
│  │ - delta_aic_* (vs nulls)            │                          │
│  │ - r_squared                          │                          │
│  │ - timestamp                          │                          │
│  └──────┬───────────────────────────────┘                          │
│         │                                                           │
│         ├──────────► 5a. META-REGRESSION                            │
│         │              │                                            │
│         │              ▼                                            │
│         │           ┌─────────────────────────────┐                │
│         │           │ beta_meta_regression_v2.py  │                │
│         │           │                             │                │
│         │           │ Aggregates all β-estimates  │                │
│         │           │ Regresses on covariates     │                │
│         │           │ Explains 68% variance (v1.1)│                │
│         │           └──────┬──────────────────────┘                │
│         │                  │                                        │
│         │                  ▼                                        │
│         │           data/derived/                                   │
│         │           ├─ beta_estimates.csv                           │
│         │           └─ domain_covariates.csv                        │
│         │                                                           │
│         ├──────────► 5b. MANUSCRIPT                                 │
│         │              │                                            │
│         │              ▼                                            │
│         │           paper/manuscript_v1.0.tex                       │
│         │           (Cites results via DOI)                         │
│         │                                                           │
│         └──────────► 5c. SIMULATOR                                  │
│                        │                                            │
│                        ▼                                            │
│                     simulator/presets/<dataset>.json                │
│                     (UI uses β, Θ for interactive exploration)     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## System State Transitions

### How σ(β(R-Θ)) Governs Repository State

```
┌──────────────────────────────────────────────────────────────────┐
│            REPOSITORY STATE AS σ(β(R-Θ))                         │
│                                                                  │
│  R = Order Parameter (open tasks, missing features)              │
│  Θ = Threshold (readiness criteria, completion requirements)     │
│  β = Steepness (how quickly tasks activate once started)         │
│  ζ(R) = Impedance (resistance: tech debt, complexity)           │
│                                                                  │
│  State 1: R << Θ (Far below threshold)                          │
│  ├─ Status: Planning phase                                      │
│  ├─ σ ≈ 0 (dormant)                                             │
│  └─ Action: Design, prototyping                                 │
│                                                                  │
│  State 2: R ≈ Θ (Approaching threshold)                         │
│  ├─ Status: Active development                                  │
│  ├─ σ ≈ 0.5 (transitioning)                                     │
│  ├─ ζ(R) rising (complexity increases)                          │
│  └─ Action: Implement, test, document                           │
│                                                                  │
│  State 3: R > Θ (Above threshold)                               │
│  ├─ Status: Release-ready                                       │
│  ├─ σ ≈ 1.0 (activated)                                         │
│  ├─ ζ(R) damped (automation reduces manual work)                │
│  └─ Action: Release, DOI minting, publication                   │
│                                                                  │
│  Current State (2025-11-10):                                     │
│  ├─ UTAC v1.1: σ ≈ 0.95 (near-complete, DOI ready)             │
│  ├─ Documentation: σ ≈ 0.70 (improved, more needed)             │
│  ├─ Automation: σ ≈ 0.60 (CI in place, coverage needs work)    │
│  └─ Community: σ ≈ 0.20 (nascent, needs growth)                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Principles

### 1. **Trilayer Everywhere**
Every important document exists in YAML + JSON + MD. This enables:
- **Humans:** Browse MD with context
- **Machines:** Parse YAML/JSON efficiently
- **Agents:** Understand structure + narrative

### 2. **Light/Shadow Duality**
For every primary component (Light), maintain:
- **Shadow:** Recovery playbook for when things break
- **Alarms:** Explicit error codes (sys-shadow-00X)
- **Playbooks:** Step-by-step recovery procedures

### 3. **Codex as Memory**
Every significant change is logged in `seed/codexfeedback.*`:
- **Enforced by CI:** codex-guard.yml blocks PRs without entries
- **Trilayer format:** Formal + Empirical + Poetic threads
- **Timestamped:** ISO 8601 for temporal tracking

### 4. **Falsification First**
Every claim requires ΔAIC ≥ 10 vs null models:
- **Nulls:** Linear, power-law, exponential
- **Metrics:** AIC, BIC, R², Bootstrap CI
- **Documented:** In every analysis result JSON

### 5. **Automation with Guards**
CI enforces quality gates:
- **Tests:** 290 pytest tests must pass
- **Trilayer:** sigillin_sync.py checks gaps
- **Codex:** codex-guard.yml checks updates
- **Coverage:** Minimum 29% (target: 50%+)

---

## Navigation Tips

### For New Developers

**Start here:**
1. `QUICKSTART.md` — 5-minute overview
2. `ARCHITECTURE.md` — This document (you're here!)
3. `REPRODUCE.md` — Run your first β-fit
4. `AGENTS_PLAIN.md` — Working guidelines

**Then explore:**
- `analysis/` — See how fits are done
- `models/` — Understand solvers
- `tests/` — Learn expected behavior

### For New AI Agents

**Priority reads:**
1. `AGENTS.md` or `AGENTS_PLAIN.md` — Your charter
2. `seed/utf-living-glossary.md` — Vocabulary (poetisch ↔ technisch)
3. `docs/utac_status_alignment_v1.2.md` — Current state
4. `seed/codexfeedback.md` — Recent history (last 10 entries)

**Working rules:**
- Always update Trilayer (YAML + JSON + MD)
- Always create Codex entry for Bedeutungs-Sigillin changes
- Always run tests before pushing
- Always check `sigillin_sync.py report` before committing

### For External Researchers

**Scientific content:**
- `README.md` — Project overview
- `METHODS.md` — Statistical methodology
- `METRICS.md` — Quantitative definitions
- `docs/field_type_classification_v1.1.md` — 5 Field Types (η²=0.68!)
- `paper/manuscript_v1.0.tex` — Full manuscript

**Data:**
- `data/` — All datasets with metadata
- `analysis/results/` — All fit results
- `data/derived/beta_estimates.csv` — Aggregated β values

---

## Glossary: Architecture Terms

| Term | Meaning |
|------|---------|
| **Trilayer** | YAML + JSON + MD synchronized representations |
| **Ordnungs-Sigillin** | Navigation files (indices), change frequently |
| **Bedeutungs-Sigillin** | Semantic files (theory), change rarely |
| **Shadow** | Recovery playbook for each primary component |
| **Codex** | Living project memory (seed/codexfeedback.*) |
| **Bridge** | Metaquest coordination between System & Campaign |
| **Guard** | CI check that enforces quality gates |
| **Parity** | Synchronization state (Δparity = 0 is ideal) |
| **σ(β(R-Θ))** | Logistic function describing state transitions |
| **ΔAIC** | Statistical guard (≥10 means strong evidence) |

For full glossary, see: `seed/utf-living-glossary.md`

---

## Future Architecture

### Planned Enhancements

1. **Test Coverage → 50%+**
   - Priority: `sigillin_sync.py`, `archive_sigillin.py`
   - Shadow alarm testing
   - Codex guard logic testing

2. **Telemetry Dashboard**
   - Aggregate metrics from all sources
   - Real-time sync status
   - HTML dashboard or JSON API

3. **Automated Index Updates**
   - CI hook: Update indices on file additions
   - Eliminate manual sync burden

4. **Community Portal**
   - GitHub Discussions activated
   - Contributor onboarding wizard
   - Interactive simulator public instance

---

**Version:** 1.0
**Created:** 2025-11-10
**Maintainer:** Johann Römer + Community

**Feedback?** → [GitHub Issues](https://github.com/GenesisAeon/Feldtheorie/issues)

*"The architecture breathes with the field — update when resonances shift."* 🌊
