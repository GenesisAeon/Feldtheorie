# Climate Threshold Data Staging (UTAC v1.3)

Diese Laterne hält die globalen Urban-Heat- und Amazon-Hydro-Datensätze.

- **R (Kontrollparameter):** Temperatur-Δ bzw. SPI/Feuchte-Indizes
- **Θ (Schwelle):** Zielwerte laut `data/utac_v1_3_data_manifest.yaml`
- **β (Steilheit):** Erwartete Werte > 13 für Urban Heat, ~14 für Amazon Resilience
- **ζ(R) (Impedanz):** Kopplung Bodenfeuchte ↔ anthropogene Wärme

## Aufgaben
1. Rohdaten-Download (NASA UHI, CHIRPS/IMERG)
2. Harmonisierung & Rasterung (0.1°–0.25°)
3. Logistic Fit via `analysis/climate_beta_extractor.py`
4. Nullmodelle (linear, power law, spline) dokumentieren
5. Metadata-Dateien `.metadata.json` ablegen

## Aktivierungen (Stand 2026-03-26)

- **Urban Heat Intensity (`urban_heat_intensity.csv`)** ist integriert. Der Fit via `analysis/climate_beta_extractor.py` liefert Θ≈3.20 K, β≈14.27 mit ΔAIC≈1484 gegen lineare Nullmodelle.  Die Resultate liegen in `analysis/results/urban_heat_global_fit.json` sowie `analysis/results/outlier_validator_report.json`.
- **Amazon Hydro (`amazon_precip_evapo.nc`)** steht weiterhin aus; Metadaten bleiben aktiv.

Bis zur vollständigen Dateneinbindung der weiteren Laternen hält dieses README den logistischen Rahmen offen.

