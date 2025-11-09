# Climate Threshold Data Staging (UTAC v1.3)

Diese Laterne reserviert den Raum für globale Urban-Heat- und Amazon-Hydro-Datensätze.

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

Bis zur Dateneinbindung bleiben Dateien leer; dieses README verankert den logistischen Rahmen.

