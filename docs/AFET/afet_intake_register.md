# AFET Intake Register (`docs/AFET`)

Diese Intake-Laterne haelt die AFET-Quellen repo-konform in einem Tri-Layer fest.

## Logistic Snapshot

- **R=0.78**, **Theta=0.56**, **beta=4.8**, **zeta(R)=0.09**
- Aktivierung ueber **sigma(beta(R-Theta))=0.73**: Release-resonant. Kuration abgeschlossen, Zenodo-Paket vorbereitet.

## Inventory

### Kuratierte Artefakte

| Datei | Typ | Groesse (Bytes) | SHA-256 (kurz) | Rolle |
| --- | --- | ---: | --- | --- |
| `AFET_Universal_Framework_Paper_final.md` | `md` | 48735 | `af89462a24b1b021` | Hauptmanuskript (Markdown) |
| `Afet universal framework paper final.pdf` | `pdf` | 560609 | `221fb8fed6f34b8b` | Hauptmanuskript (PDF) |
| `preprint_v12_consciousness.md` | `md` | 6267 | `415bf9c0fcc35a11` | v12 Bewusstseins-Preprint |
| `PERPLEXITY_INTEGRATION_SUMMARY.md` | `md` | 7804 | `cd112b2c2a223d2d` | Perplexity-Integration Changelog |
| `Perplexity integration summary final.pdf` | `pdf` | 327128 | `0c017c63b3e12734` | Perplexity-Integration (PDF) |
| `DOIListe.txt` | `txt` | 1627 | `6a02e4dc29c92ac2` | DOI-Quellliste (38 DOIs) |
| `doi_citation_table.md` | `md` | — | — | Strukturierte DOI-Citationstabelle |

### Raw Sources (forensisch erhalten)

| Datei | Typ | Groesse (Bytes) | SHA-256 (kurz) | Status |
| --- | --- | ---: | --- | --- |
| `1. Hauptthesen und Schluesselkonzepte-1.pdf` | `pdf` | 50453 | `3799d0734230f200` | raw-intake |
| `AFET-Parameter und physikalische Konstanten_ Emergenzen_.pdf` | `pdf` | 259913 | `a7cb52d2fcd55ddf` | raw-intake |
| `AFET-RepoUmsetzung.txt` | `txt` | 8494 | `1eaefe68e138a4a2` | raw-intake |
| `AFETSucheChatGPTAgent_paper.txt` | `txt` | 8816 | `ee9b5798f5137dd5` | raw-intake |
| `AFET_ Theoriefundament und Repository-Integration.pdf` | `pdf` | 315037 | `ae9d5dea4102ea98` | raw-intake |
| `AFET_ParameterSucheGemini.txt` | `txt` | 74791 | `195b33d3c02c6139` | raw-intake |
| `BiologischeVerantwortung.txt` | `txt` | 12241 | `9989a35318f64a33` | raw-intake |
| `Feld-Entrophie_Theorie.txt` | `txt` | 19744 | `d0fad13c4c0c9ce7` | raw-intake |
| `Feldtheorie aeon Modul.pdf` | `pdf` | 49648 | `9b5f7d9c7d2f0703` | raw-intake |
| `GeminiSucheAFET.txt` | `txt` | 80829 | `5c2ac0b2ad87009e` | raw-intake |
| `GeminiSucheDOIListe.txt` | `txt` | 84359 | `cbd8414716642bc7` | raw-intake |
| `General Field Entropy Theory (AFET).pdf` | `pdf` | 110680 | `fac590feee2cbc98` | raw-intake |
| `Philosophical Implications of the General Field Entropy Theory.pdf` | `pdf` | 69540 | `f20e77c2353fa0c1` | raw-intake |
| `SucheChatGPTDeepResearch.txt` | `txt` | 8254 | `e51f6d3c9061c835` | raw-intake |
| `UTAC zu AFET_ DOI-Recherche und Entwicklung.docx` | `docx` | 6211648 | `c966a94351f139a8` | raw-intake |
| `UTAC zu AFET_ DOI-Recherche und Entwicklung.pdf` | `pdf` | 249328 | `b23178792231a1ca` | raw-intake |
| `f87ed29c-b329-4429-afb2-ff3a21d68c6a.jpg` | `jpg` | 216825 | `715a431dbf0e5a9a` | raw-intake |
| `xAIkollab.txt` | `txt` | 21257 | `1f18d6d88009f0c1` | raw-intake |

## Aktionen

| ID | Aufgabe | Status |
|----|---------|--------|
| AFET-A1 | Rohdokumente forensisch erhalten | completed |
| AFET-A2 | Inhaltliche Extraktion (Markdown-first) | completed |
| AFET-A3 | DOI-Citationstabelle mit Phasen + DAIC | completed |
| AFET-A4 | Zenodo-Release-Paket (releases/vAFET-1.0/) | completed |

## Kuration & Falsifizierbarkeit

- **Nullmodell:** Nur Dateiablage ohne strukturierte Metadaten (schlecht reproduzierbar, hohe zeta(R)).
- **Interventionsmodell:** Intake-Register mit Hashes + Aktionsstatus (niedrigere zeta(R), hoehere Nachvollziehbarkeit).

## Kopplungspfade

- `docs/docs_index.md` (Dokumentations-Navigation)
- `docs/xai_collab/xai_collab_index.md` (AFET-Kollaborationspaket)
- `releases/vAFET-1.0/` (Zenodo-Release-Manifest)
- `analysis/` und `data/` (empirische Anbindung)
