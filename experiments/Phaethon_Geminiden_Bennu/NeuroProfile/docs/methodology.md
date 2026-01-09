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

## Falsifizierbarkeit

- **Nullmodelle:** linear, power law, constant.
- **ΔAIC-Guard:** Ziel ΔAIC ≥ 10; jede Analyse protokolliert CI.
- **Proxy-Status:** v_RIG bleibt konzeptuell, bis Hochfrequenzsensorik verfügbar ist.

## Ethik & Consent

- Keine realen EEG-Daten ohne explizite Zustimmung.
- Ergebnis-Export in `data/results.json` nur mit anonymisierten IDs.
