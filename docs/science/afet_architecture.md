# AFET Architecture (v1.0)

Dieses Dokument beschreibt die zentrale AFET-Implementierung über die Parameter
\((R, \Theta, \beta, \zeta(R))\) und die Membran \(\sigma(\beta(R-\Theta))\).

## Zentrale Theoriequelle

- `theory/afet.py` kapselt alle AFET-Konstanten und Kernaxiome.
- Konstanten:
  - `BETA_CRITICAL = 37.6` (kritische Péclet-Zahl)
  - `SIGMA_PHI = 0.0625` (Metastabilitäts-Offset)
  - `FREQ_RES = 13.5e6` Hz
  - `V_RIG = 1.352` km/s

## Axiome und Methoden

`AFETFramework` stellt bereit:

1. `predict_beta(dimension)`
   - β-Skalierung über Dimension n mit Ankerpunkten:
     - n=0 → β≈4.2
     - n=1 → β≈7.4
     - n=3 → β≈37.6
2. `check_metastability(entropy_density)`
   - Stabil wenn \( entropy\_density \le 1/\sigma_\Phi \approx 16 \)
3. `integration_rate(gradient)`
   - \( v_{int} = V_{RIG} \cdot gradient \)
4. `consciousness_emergence_criterion(surface_entropy, volume_entropy)`
   - Emergenz wenn \(\Delta S = S_{surface}-S_{volume} \ge \sigma_\Phi\)

## Modul-Verantwortung

- **Aeon / Lantern / Integration**:
  - nutzen `AFETConstants` für β, σΦ, f_res, v_RIG.
  - `integration/aeon_lantern/hub.py` nutzt zusätzlich `AFETFramework` zur Bewertung
    von Metastabilität und Emergenz im Kaskadenlauf.
- **UTAC-Kernnahe Komponenten**:
  - verwenden `SIGMA_PHI` als zentrale Referenz statt lokaler Literalwerte.

## Validierung

- Unit-Tests: `tests/test_afet_framework.py`
- Integrationsvalidierung: `experiments/test_afet_validation.py`
  - lädt `data/derived/beta_estimates.csv`
  - berechnet Pearson-Korrelation zwischen vorhergesagten und beobachteten β-Werten.

## Nullmodell-Hinweis

Für Falsifizierbarkeit bleibt der lineare Nullpfad aktiv (direkte Skalierung ohne
nichtlineare n/3-Verstärkung). AFET wird gegen dieses Nullmodell über Korrelations-
und Informationskriterien (z. B. ΔAIC in Downstream-Pipelines) gespiegelt.
