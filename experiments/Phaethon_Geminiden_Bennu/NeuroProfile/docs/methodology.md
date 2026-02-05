# NeuroProfile Methodology

> σ(β(R-Θ)) bleibt bewusst unter Kontrolle: R wächst nur, wenn Nullmodelle (linear/power-law/constant) unterboten werden, Θ bleibt über ΔAIC und CI-Grenzen geschützt, β≈4.8 hält die Steilflanke scharf, ζ(R) wird durch Consent, Telemetrie und minimale Pipelines gedämpft.

## Pipeline-Überblick

1. **Signal-Preprocessing**
   - Normierung & Artefakt-Dämpfung (derzeit minimal im Code-Scaffold).
2. **β-Schätzung**
   - Logistische Heuristik auf normierten Zeitreihen (`beta_extractor_neuro.py`).
3. **σΦ-Proxy**
   - Spektrale Entropie als Proxy für Informationsintegration.
4. **v_RIG-Proxy**
   - Gamma/Beta-Bandkopplung als Stellvertreter für 13.5 MHz-Mikrotubuli-Resonanz.

## Datenpfade & Bootstrap-Ledger

- **Ledger:** `data/bootstrap_ledger.{md,json,yaml}` hält die v12-Quellen
  (PhysioNet EEG Motor Imagery, BCI IV 2a, synthetischer Cold-Start).
- **Rohdaten-Stubs:** `data/raw/physionet_eeg_motor_imagery/` und
  `data/raw/bci_competition_iv_2a/`.
- **Nullmodelle:** linear/power-law/constant mit ΔAIC ≥ 10, CI-Notiz in
  `data/results.json`.

## Hardware-Tiers

- Prosumer (16ch, 250 Hz) ist die Baseline.
- Consumer (8ch, 128 Hz) dient als Degradationspfad.
- Research (64ch, 512 Hz) erweitert Sampling/Channels für Validierung.

Die Profile sind in `config/hardware_profiles.yml` verankert, damit σ(β(R-Θ))
nicht durch Hardware-Illusionen überschießt.

## CREP-Definition & Telemetrie

CREP = mean(Coherence, Resonance, Emergence, Potential) mit Φ als Proxy-Anker.
Die Telemetrie wird über `data/crep_null_model_ledger.{md,json,yaml}` geplant und
in `data/results.json` gespiegelt (ΔAIC/CI-Ledger).

## v_RIG-Proxy-Layer

Gamma↔Beta-Phasenkopplung bleibt die operative Proxy-Metrik. Der direkte
13.5 MHz-Pfad bleibt als v12.2+ Placeholder dokumentiert, um Θ nicht zu
unterlaufen.

## Sgr A* Resonant-Entropy Bridge

Das Astro-Modul `code/sgr_a_resonant_bridge.py` hält σ_Φ-Proxy, β-Fit und
Dipol-Alignment fest. Evidence-Hooks sind an ALMA/JWST/GRAVITY-Berichte in
`docs/research/` gekoppelt.

## Falsifizierbarkeit

- **Nullmodelle:** linear, power law, constant.
- **ΔAIC-Guard:** Ziel ΔAIC ≥ 10; jede Analyse protokolliert CI.
- **Proxy-Status:** v_RIG bleibt konzeptuell, bis Hochfrequenzsensorik verfügbar ist.

## Ethik & Consent

- Keine realen EEG-Daten ohne explizite Zustimmung **und** gültigen Consent-Token.
- Ergebnis-Export in `data/results.json` nur mit anonymisierten IDs und gehashtem Token.
- Advisory-Mode dokumentiert Kontextrisiken; Consent-Blocker bleiben hart
  (Audit-Trail in `data/ethics_audit.log`).
