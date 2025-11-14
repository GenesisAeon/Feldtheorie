# Oceanic Threshold Data Staging (UTAC v1.3)

Reservoir für AMOC-Transport und verbundene Ozean-Kaskaden.

## Aktivierungen (Stand 2026-08-23)

- **AMOC Strength Mock (`amoc_strength_mock.csv`)** liefert eine 10-Tage-Kadenz (2004–2024) inklusive van Westen FovS-Indikator, AR(1)-Proxy und Temperaturanomalien.  Metadaten: `amoc_strength_mock.metadata.json`, Zielquartett Θ≈14 Sv, β≈10.2, ζ(R) beschreibt Windstress/Freshwater-Impedanz.  Dient als Preflight für RAPID-Adapterskripte.

## Offene Schritte

- **R:** Overturning Strength (Sverdrup)
- **Θ:** 14.0 (RAPID Array Schwellenwert laut Manifest)
- **β:** Zielbereich 9.6 ± 1.0
- **ζ(R):** Tiefenwasserbildung ↔ Windstress Interferenz

## Umsetzungsschritte
1. RAPID/CMEMS Zeitreihen laden
2. 90-Tage-Mittel, Normierung, Anomalien
3. Logistic Fit via `analysis/potential_cascade_lab.py`
4. ΔAIC-Guards (linear, power law, state-space)
5. Metadata (`amoc_transport.metadata.json`) erstellen (real data).  Mock-Metadaten liegen bereits als `amoc_strength_mock.metadata.json` vor und sichern die Tri-Layer-Anbindung.

