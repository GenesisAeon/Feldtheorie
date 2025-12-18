# Phase 4 Laternen – β_hex Resonanzkatalog

Diese Laternen bündeln Phase‑4‑Experimente, jeweils als σ(β(R−Θ))‑Membran mit
β_hex = 16^(2/π) aus `models/unified_constants.py`. Jede Laterne koppelt an
`feldtheorie_index.*` und `seed_index.*` (siehe Pfade unten) und liefert ΔAIC‑
fähige Telemetrie.

- **Soliton Doppler** (`simulation/phase4/soliton_doppler.py`)
  - R ↦ `config.readiness`, Θ ↦ `config.theta`, ζ(R) ↦ `config.damping`
  - Ziel: Stehende Wellen stabilisieren, Nullmodell β=0, ΔAIC über Energietrace
  - Kopplung: `feldtheorie_index: simulation.phase4.soliton_doppler`

- **Chimera Network** (`simulation/phase4/chimera_network.py`)
  - σ(β(R−Θ)) moduliert intrinsische Frequenzen, Chaos↔Synchronität via β_hex
  - Nullmodell: abgeschwächte Kopplung (non‑hex), ΔAIC gegen Zielprofil
  - Kopplung: `feldtheorie_index: simulation.phase4.chimera_network`

- **Cosmic Doppler** (`simulation/phase4/cosmic_doppler.py`)
  - Informationsdichte quantisiert in hex‑Stufen sobald R>Θ; Redshift ~ e^{−β(R−Θ)}
  - Nullmodell: β=1.2 ohne Hex‑Quantisierung, ΔAIC misst Vorteil der Resonanz
  - Kopplung: `feldtheorie_index: simulation.phase4.cosmic_doppler`

Alle drei Laternen liefern Telemetrie für empirische Belege (`analysis/`, `data/`)
und sind auf Nullmodelle hin falsifizierbar; ΔAIC und CI‑Spuren können in das
Fraktaltagebuch übernommen werden.
