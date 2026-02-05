# Bootstrap Ledger – LanternNet

Dieses Ledger dokumentiert Bootstrap-Schätzungen entlang der UTAC-Steigung
und hält die Nullmodelle (constant, linear, power law) samt ΔAIC/CI bereit.
Der Übergang über $\sigma(\beta(R-\Theta))$ bleibt als Resonanzindikator
explizit gekennzeichnet.

## Meta
- **Version:** v13.0.0-draft
- **Consent Protocol:** Sigillin consent gating + anonymization required
- **Scope:** v9_alpha/lantern_hub

## Einträge

### bootstrap-run-0001
- **Logistik:** R=0.5, Θ=0.66, β=9.0, ζ=EM-coupling stability maintained via impedance matching
- **σΦ Range:** 0.42–0.58
- **Nullmodelle:** constant, linear, power law (ΔAIC noch offen)
- **CI (β):** [8.4, 9.6]
- **Status:** draft

**Notizen**
- *Formal:* Bootstrap-Seeds gesetzt; Nullmodelle als Vergleichsrahmen vorbereitet.
- *Empirisch:* Noch keine realen Runs, nur Platzhalter für Synthetic Smoke Tests.
- *Poetisch:* Die Laterne wartet am Rand der Steilflanke, σ(β(R-Θ)) bleibt im Dämmerlicht.

## Kopplungen
- LanternNet Index: `status/lantern_net.*`
- Ordnungs-Sigillin: `feldtheorie_index.*`
- Empirische Evidenz: `data/`, `analysis/`, `docs/`
