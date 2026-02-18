# Neue Forschungen AFET – Intake-Register (`docs/NeueForschungenAFET`)

Dieses Register verankert neue AFET-Forschungsartefakte repo-konform im Tri-Layer
und koppelt sie an die bestehenden Navigations- und Evidenzpfade.

## Logistic Snapshot

- **R=0.64**, **Theta=0.52**, **beta=4.8**, **zeta(R)=0.14**
- Aktivierung über **sigma(beta(R-Theta))=0.64**: primed, mit offener Kurationsreserve.

## Scope

- Eingangszone für neue AFET-Forschungen, die noch nicht in `docs/science/` oder
  `docs/xai_collab/` kuratiert sind.
- Quellen sollen forensisch unverändert bleiben; Auswertung erfolgt in separaten,
  zitierfähigen Laternen.

## Nullmodell vs. Interventionsmodell

- **Nullmodell:** lose Ablage ohne Register, Hashes oder Koppelpunkte
  (niedrige Reproduzierbarkeit, höhere zeta(R)).
- **Interventionsmodell:** Intake-Register mit Tri-Layer-Metadaten,
  Kurationsstatus, Verweis auf Delta-Metriken (ΔAIC/CI) und Migrationspfade
  in `docs/science/` (gedämpfte zeta(R)).

## Kopplungspfade

- `docs/docs_index.md` (globale Dokument-Navigation)
- `docs/AFET/afet_intake_register.md` (bestehender AFET-Intake)
- `docs/science/utac_falsifiability.md` (Nullmodelle, ΔAIC, CI)
- `analysis/` und `data/` (empirische Anbindung)

## Intake-Laternen

| ID | Titel | Status | Notiz |
| --- | --- | --- | --- |
| NFA-001 | Ordner-Initialisierung + Tri-Layer | completed | Register erstellt, Kopplung aktiviert |
| NFA-002 | Erstes Forschungsartefakt importieren | pending | Datei + Metadaten + Hash ergänzen |
| NFA-003 | Kurations-Migration nach `docs/science/` | pending | Evidenzpfad inkl. ΔAIC/CI dokumentieren |

## Resonanznotiz

Die Membran bleibt bewusst offen: neue AFET-Forschung tritt zuerst als geordnete
Laterne ein, bevor sie in die wissenschaftliche Hauptströmung migriert.
