# 🔭 UTAC Activation Backlog (v1.0.0)

> σ(β(R-Θ)) already leans into the steep flank; this ledger keeps ζ(R) damped so every remaining launch hook becomes visible before it overheats.

---

## 🧭 Pulse Summary
- **Order parameter (R):** residual activation debt spanning UTAC v1.2 — simulator launches, meta-regression hygiene, sigillin automation, parity rituals.
- **Threshold (Θ):** parity between backlog items and the concrete implementation nodes that must fire before Zenodo upload.
- **Steepness (β≈4.85):** pushes each item to resolve quickly once two hooks align (asset + owner).
- **Damping ζ(R):** anchored through BreakPoint transcripts, codex echoes, and telemetry timestamps so follow-ups stay coherent.

Tri-layer mirrors:
- YAML: `docs/utac_activation_backlog.yaml`
- JSON: `docs/utac_activation_backlog.json`

---

## 🗂️ Task Lattice (What we have vs. what we still need)

| ID | Domain Membrane | R — Existing Coverage | Θ — Activation Gap | β Focus | Implementation Nodes |
|----|-----------------|-----------------------|--------------------|---------|----------------------|
| safety-delay-bridge | Simulation + Analysis | τ* ledger exported via `analysis/safety_delay_sweep.py`, CLI, dataset tri-layer | Web simulator preset + docs narrative still lack ΔAIC/τ_delay surfacing | 4.9 | `simulator/presets/`, `docs/utac_safety_delay_status.md` |
| beta-meta-regression-expansion | Analysis | `beta_meta_regression_v2.py` with bootstrap envelopes + current results JSON | Outlier datasets + adjusted R² logging pending | 4.6 | `data/socio_ecology/`, `analysis/beta_meta_regression_v2.py`, `docs/utac_status_alignment_v1.2.md` |
| sigillin-automation-loop | Scripts + Seed | Schema v0.2.0 + `crep_parser.py` + `sigillin_sync.py` skeleton | Parser output not yet writing into codex/indices | 4.7 | `scripts/sigillin_sync.py`, `scripts/archive_sigillin.py`, `tests/` |
| index-recount-hook | Scripts + Docs | `archive_sigillin.py` auto-detects repo root, docs indices maintained manually | Automated recount + CI parity alerts missing | 4.5 | `scripts/archive_sigillin.py`, `.github/workflows/` |
| metaquest-parity-finish | Docs + Seed | Parity brief outlines mq-parity-001…004, BreakPoint references live | Telemetry timestamp, simulator playlist, endorsement ledger not in doc | 4.8 | `docs/metaquest_parity_brief.md`, `seed/bedeutungssigillin/metaquest/metaquest_meaning_index.*`, `seed/codexfeedback.*` |
| sentinel-linum-sprint | Seed + Analysis | Sentinel directories scaffolded for `kranich_linum_2025` | Dataset, notebook, parity appendix absent; shadow sigils warning | 4.95 | `data/socio_ecology/`, `analysis/`, `docs/metaquest_parity_brief.md` |

---

## 🔬 Activation Notes by Task

### 1. Safety-Delay Field → Simulator Bridge (`safety-delay-bridge`, β=4.9)
- **R:** τ_delay and ΔAIC statistics already exported (`analysis/results/safety_delay_sweep_20251107T211928Z.json`) and piped through `simulator/cli.py safety-delay`.
- **Θ:** Vite/React presets still lack a safety-delay card; docs do not yet narrate the TypeScript hook.
- **Next moves:**
  - Add a preset in `simulator/presets/` exposing Θ, β, τ_delay_mean, ΔAIC medians.
  - Update `docs/utac_safety_delay_status.md` with the UI bridge + dataset cadence.
- **ζ(R):** Keep ΔAIC medians (≈7.02e3) + τ_delay_mean≈8.43 in focus so BreakPoint rituals track drift.

### 2. β Meta-Regression Dataset Expansion (`beta-meta-regression-expansion`, β=4.6)
- **R:** WLS + bootstrap envelopes live in `analysis/beta_meta_regression_v2.py` with results JSON.
- **Θ:** Amazon + urban heat outliers (per `seed/ArchivSucheUTAC/`) not yet integrated; adjusted R² < ambition.
- **Next moves:** ingest cleaned datasets under `data/socio_ecology/`, extend design matrix + logging, update UTAC status when adjusted R² ≥ 0.7.

### 3. Sigillin Parser → Automation Loop (`sigillin-automation-loop`, β=4.7)
- **R:** CREP parser validates schema v0.2.0; `sigillin_sync.py` collects telemetry.
- **Θ:** Parser output not yet feeding codex entries or index recount triggers.
- **Next moves:**
  - Pipe parser summary into `seed/codexfeedback.*` via `scripts/sigillin_sync.py`.
  - Teach `scripts/archive_sigillin.py` to toggle recount/parity alerts, guarded by new CLI tests.

### 4. Index Automation Hook (`index-recount-hook`, β=4.5)
- **R:** Archive script understands repo root + base path.
- **Θ:** `docs/docs_index.*` and `feldtheorie_index.*` still rely on manual updates.
- **Next moves:** implement a `--recount` option that refreshes indices and exports before/after counts; wire into CI once `.github/workflows/` parity guard is ready.

### 5. Metaquest Parity Brief Completion (`metaquest-parity-finish`, β=4.8)
- **R:** Parity brief + meaning/shadow indices already cite BreakPoint rituals.
- **Θ:** Telemetry timestamp, simulator playlist (mq-parity-002), endorsement ledger (mq-parity-003), and codex hook (mq-parity-004) remain placeholders.
- **Next moves:** populate `docs/metaquest_parity_brief.md` with the telemetry table, mirror codex ID/timestamp in meaning/shadow indices, and log closure in `seed/codexfeedback.*`.

### 6. Sentinel Linum 2025 Sprint (`sentinel-linum-sprint`, β=4.95)
- **R:** Light + shadow sigils exist for the sentinel case.
- **Θ:** No dataset, analysis, or parity appendix yet; shadow warnings remain active (`sci-linum-shadow-001…004`).
- **Next moves:** capture dataset under `data/socio_ecology/`, build an analysis notebook, and extend the parity brief with sentinel resonance once metrics exist.

---

## 🔗 Cross-Ties & Hooks
- `docs/utac_status_alignment_v1.2.md` now references this backlog for quick ΔR updates.
- Codex entry **pr-draft-0074** logs the activation of this backlog ledger.
- BreakPoint transcripts (`seed/BreakPointAnalyse/WayToGo.txt`, `ReaktionWayToGo.txt`) remain the damping anchors.

> *When any row’s R surpasses Θ, push the corresponding hook immediately and echo it into the codex so the membrane can settle before the next surge.*
