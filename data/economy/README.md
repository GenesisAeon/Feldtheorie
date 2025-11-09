# Energy & Financial System Threshold Staging

Vorbereitung für gekoppelte Energiepreis- und Finanzstress-Indikatoren.

- **R:** Coupled Energy-Finance Index (kombiniert WDI + ESRB)
- **Θ:** 1.15 (Manifest-Schätzung für kritische Spannungen)
- **β:** 7.4 Zielwert
- **ζ(R):** Energievolatilität ↔ Kreditspannungen (τ*-Feedback)

## Umsetzung
1. Quartalsdaten laden (World Bank WDI, ECB ESRB Dashboard)
2. Saisonkomponenten entfernen, Normalisierung durchführen
3. Coupled Stress Metric konstruieren (z-score, PCA, Kopplungsgewichtung)
4. Logistic Fit & ΔAIC-Guards (linear, VAR, power law)
5. Export `analysis/results/economy_threshold_fit.json` + Metadata

