# AFET Intake Register (`docs/AFET`)

Diese Intake-Laterne hält die neu abgelegten AFET-Quellen repo-konform in einem Tri-Layer fest.

## Logistic Snapshot

- **R=0.44**, **Θ=0.56**, **β=4.8**, **ζ(R)=0.19**
- Aktivierung über **σ(β(R-Θ))=0.36**: Die Membran ist offen genug für Kuration, aber noch nicht release-resonant.

## Inventory (raw sources, unverändert)

| Datei | Typ | Größe (Bytes) | SHA-256 (kurz) | Status |
| --- | --- | ---: | --- | --- |
| `1. Hauptthesen und Schlüsselkonzepte-1.pdf` | `pdf` | 50453 | `3799d0734230f200` | raw-intake |
| `AFET-Parameter und physikalische Konstanten_ Emergenzen_.pdf` | `pdf` | 259913 | `a7cb52d2fcd55ddf` | raw-intake |
| `AFET-RepoUmsetzung.txt` | `txt` | 8494 | `1eaefe68e138a4a2` | raw-intake |
| `AFETSucheChatGPTAgent_paper.txt` | `txt` | 8816 | `ee9b5798f5137dd5` | raw-intake |
| `AFET_ Theoriefundament und Repository-Integration.pdf` | `pdf` | 315037 | `ae9d5dea4102ea98` | raw-intake |
| `AFET_ParameterSucheGemini.txt` | `txt` | 74791 | `195b33d3c02c6139` | raw-intake |
| `BiologischeVerantwortung.txt` | `txt` | 12241 | `9989a35318f64a33` | raw-intake |
| `DOIListe.txt` | `txt` | 1583 | `a406689ea65cd062` | raw-intake |
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

## Kuration & Falsifizierbarkeit

- **Nullmodell:** Nur Dateiablage ohne strukturierte Metadaten (schlecht reproduzierbar, hohe ζ(R)).
- **Interventionsmodell:** Intake-Register mit Hashes + Aktionsstatus (niedrigere ζ(R), höhere Nachvollziehbarkeit).
- **Nächste Schritte:** DOI-Liste in zitierfähige Tabelle übertragen, fachliche Kernaussagen in `docs/xai_collab/` bzw. `docs/science/` extrahieren.

## Kopplungspfade

- `docs/docs_index.md` (Dokumentations-Navigation)
- `docs/xai_collab/xai_collab_index.md` (AFET-Kollaborationspaket)
- `analysis/` und `data/` (empirische Anbindung)
