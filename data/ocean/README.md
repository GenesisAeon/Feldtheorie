# Oceanic Threshold Data Staging (UTAC v1.3)

Reservoir für AMOC-Transport und verbundene Ozean-Kaskaden.

- **R:** Overturning Strength (Sverdrup)
- **Θ:** 14.0 (RAPID Array Schwellenwert laut Manifest)
- **β:** Zielbereich 9.6 ± 1.0
- **ζ(R):** Tiefenwasserbildung ↔ Windstress Interferenz

## Umsetzungsschritte
1. RAPID/CMEMS Zeitreihen laden
2. 90-Tage-Mittel, Normierung, Anomalien
3. Logistic Fit via `analysis/potential_cascade_lab.py`
4. ΔAIC-Guards (linear, power law, state-space)
5. Metadata (`amoc_transport.metadata.json`) erstellen

