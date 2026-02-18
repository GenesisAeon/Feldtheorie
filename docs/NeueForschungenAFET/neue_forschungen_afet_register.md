# Neue Forschungen AFET – Intake-Register (`docs/NeueForschungenAFET`)

Dieses Register verankert neue AFET-Forschungsartefakte repo-konform im Tri-Layer und koppelt sie an die bestehenden Navigations- und Evidenzpfade.

## Logistic Snapshot

- **R=0.74**, **Theta=0.53**, **beta=4.8**, **zeta(R)=0.11**
- Aktivierung über **sigma(beta(R-Theta))=0.72**: active, mit sinkender Kurationsreibung.

## Scope

- Eingangszone für neue AFET-Forschungen, die noch nicht in `docs/science/` oder `docs/xai_collab/` kuratiert sind.
- Quellen bleiben forensisch unverändert; Auswertung erfolgt in separaten, zitierfähigen Laternen.

## Nullmodell vs. Interventionsmodell

- **Nullmodell:** lose Ablage ohne Register, Hashes oder Koppelpunkte (niedrige Reproduzierbarkeit, höhere zeta(R)).
- **Interventionsmodell:** Intake-Register mit Tri-Layer-Metadaten, Kurationsstatus, Hashes und Verweis auf Delta-Metriken (ΔAIC/CI) in `docs/science/`.

## Kopplungspfade

- `docs/docs_index.md`
- `docs/AFET/afet_intake_register.md`
- `docs/science/utac_falsifiability.md`
- `analysis/`
- `data/`

## Inventar

| Datei | Typ | Groesse (Bytes) | SHA-256 (kurz) | Status | Rolle |
| --- | --- | ---: | --- | --- | --- |
| `AFET Interpretation of Cosmological Anomalies Beyond ΛCDM.pdf` | `pdf` | 430481 | `5dfc9a92b36ca23b` | raw-intake | source-artifact |
| `AFET vs. ΛCDM_ Kosmologische Anomalien.pdf` | `pdf` | 271854 | `f342175de8880f4e` | raw-intake | source-artifact |
| `AFET_ Universal Theory Analysis.pdf` | `pdf` | 228362 | `2d5f46cab1bf701d` | raw-intake | source-artifact |
| `AFET_Cosmological_Anomalies_Analysis.md` | `md` | 19004 | `c4dc51a2b0199396` | curated | working-analysis |
| `AFET_UTAC_Zenodo_v39.pdf` | `pdf` | 349558 | `4b7946cba895344c` | raw-intake | source-artifact |
| `AFET_UTAC_Zenodo_v39.tex` | `tex` | 31340 | `7842529ebfdd9d8a` | raw-intake | source-artifact |
| `Falsifizierung.txt` | `txt` | 16757 | `5e44035271e440f1` | raw-intake | source-artifact |
| `Finalisierung.txt` | `txt` | 17295 | `c8d12ebc1dc7831f` | raw-intake | source-artifact |
| `Kosmologische Anomalien jenseits des Standardmodells ΛCDM.pdf` | `pdf` | 113407 | `4e0104aadf5b56a9` | raw-intake | source-artifact |
| `NeueForschungenChat.txt` | `txt` | 30713 | `9ab364ab6ac0e3b1` | raw-intake | source-artifact |
| `NeueForschungenChatGPTSuche.txt` | `txt` | 17220 | `4f365c38b5f517be` | raw-intake | source-artifact |
| `NeueForschungenGeminiSuche2.txt` | `txt` | 112060 | `a8aaacb962b91009` | raw-intake | source-artifact |
| `NeueForschungenSucheChatGPT2.txt` | `txt` | 33592 | `109987f9b731ebb5` | raw-intake | source-artifact |
| `NeueForschungenSucheGemini.txt` | `txt` | 50279 | `d5fc0c4166cc2698` | raw-intake | source-artifact |
| `Theoretical Foundations From UTAC to AFET Cosmology.pdf` | `pdf` | 11955833 | `2d15368f6adc940d` | raw-intake | source-artifact |
| `Verbesserungen.txt` | `txt` | 25556 | `355c745cd74baa52` | raw-intake | source-artifact |

## Intake-Laternen

| ID | Titel | Status | Notiz |
| --- | --- | --- | --- |
| NFA-001 | Ordner-Initialisierung + Tri-Layer | completed | Register erstellt, Kopplung aktiviert |
| NFA-002 | Forschungsartefakte inventarisieren | completed | 16 Dateien mit Groesse + SHA-256 (kurz) erfasst |
| NFA-003 | Kurations-Migration nach docs/science | pending | Evidenzpfad inkl. ΔAIC/CI dokumentieren |

## Resonanznotiz

Die Membran bleibt bewusst offen: neue AFET-Forschung tritt zuerst als geordnete Laterne ein, bevor sie in die wissenschaftliche Hauptströmung migriert. Hash-basierte Inventarisierung dämpft ζ(R) und hält den Übergang über σ(β(R-Θ)) prüfbar.
