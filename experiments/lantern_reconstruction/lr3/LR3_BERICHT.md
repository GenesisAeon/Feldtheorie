# LR3 – Aufgaben und Referenzen (Bericht)

Trilayer: [`lr3_status.json`](lr3_status.json) (maßgeblich), [`lr3_status.yaml`](lr3_status.yaml), dieser Bericht. Die Parameter stehen in [`protocol/study_defaults.json`](../protocol/study_defaults.json) (Entwicklungswerte, **nicht** eingefroren).

## Gebaut

| Modul | Inhalt |
|---|---|
| `streams.py` | benannte PCG64-Ströme `(study, context, split, role, episode)`, Rollen 10–70, Splits getrennt; Aeons Seeds 900000–900104 werden abgewiesen; kein `hash()`, kein globaler RNG |
| `contexts.py` | Ortspermutation (8 Schreibknoten in 4 Paaren, 9 Leseknoten, der letzte davon ist die Referenz) und zentrierte Frequenzen je Kontext |
| `encoding.py` | Schreiben θ(0) = φ·1 + a·E·u einmalig bei t = 0; Kontrollen „kein Impuls“ und „Reset“ |
| `observation.py` | A: 33 Differenzen zur Kontextreferenz, also 66 Merkmale; B: 8 Leseknoten und Referenz, alle unbeschrieben, also 16 Merkmale; strukturell geprüft |
| `surrogates.py` | `uncoupled`, `uniform_total` und das Stärke-Surrogat (Vier-Knoten-Umschichtung, 20 000 Vorschläge, eigener Strom, Invariantenbericht); **keine** Behauptung eines uniformen Ensembles |
| `episodes.py` | Ziele, Phasen und Messfehler je Episode und Rolle; je Kontext, Split, Bedingung und Kontrolle **eine** RK4-Trajektorie (AE-01), abgelesen an den 7 Zeitpunkten |

## Abnahmen (Plan § 14)

- **Referenzknoten-Leak, negativ getestet:**
  - Bei t = 0 sind B's Merkmale für verschiedene u **identisch**.
  - Mit einer beschriebenen Referenz wären sie es nicht; das ist im Test vorgeführt.
  - Ohne Kopplung bleiben B's Merkmale an **allen** 7 Zeitpunkten u-unabhängig. Das fängt die Planmutanten 7, 8 und 10.
- **Reset und Nullimpuls:** identische Zustände für verschiedene u zu allen Zeiten.
- **Surrogatinvarianten:**
  - symmetrisch, Diagonale 0, Werte in [0, 1];
  - Knotensummen bis 10⁻¹² (Entwicklungsziehung: 7·10⁻¹⁵);
  - Frobenius-Abstand > 1;
  - reproduzierbar, mit eigener Ziehung je Kontext.

**Harte Gates aus § 10:**
- Schreib- und Lesemenge sind disjunkt, die Referenz ist unbeschrieben.
- Das Schreiben ist exakt.
- Matrix und Frequenzen bleiben unverändert; es gibt keinen globalen RNG.
- Messfehler werden pro Episode, Zeit und Knoten vergeben, zwischen den Aufgaben geteilt und stammen jeweils aus dem eigenen Rollenstrom.
- Batch-Unabhängigkeit gilt.
- Die gemeinsame Permutation aller Knotenobjekte erhält die Merkmale; Planmutant 2, der nur C permutiert, wird erkannt.
- Die Splits sind getrennt.
- Die informationsfreie B-Basis liegt bei E[u²] = 1/3.

## Prüfungen

**Tests:** 165/165 über alle Lantern-Tests.

**Ad-hoc-Mutation:** 13/14 erkannt, darunter die Planmutanten 7, 8, 9 und 10.
- **Äquivalent:** die Schreibknotenprüfung in B. Sie ist ein doppelter Schutz neben „genau die Leseknoten“ und der disjunkten Kontextprüfung.
- **Zwei echte Testlücken** sind geschlossen:
  - Messfehler aus dem Zielstrom gezogen; jetzt kommt jede Ziehung aus ihrem eigenen Rollenstrom.
  - Dasselbe Surrogat für alle Kontexte über `coupling_matrices`; jetzt wird der Produktionspfad getestet.

**Laufzeit in der Entwicklung:** etwa 27 ms je Episode und Bedingung (RK4, 500 Schritte). Der volle Umfang (2250 × 4 × 20) ist auf rund 80 min **geschätzt**; LR5 misst ihn.

**Offen:**
- Ridge und die Decoderkennzahl (≤ 0,01) in LR4;
- Benchmark und CI in LR5;
- Master-Seeds und Kontextliste beim Freeze (LR6).

Es gab keine Forschungsrechnung. Originalmodule und M0–M12 sind unverändert; es gab keinen Freeze, keinen Merge und keinen Push.

## Nachtrag nach `REVIEW_LR3` (Übergaben zwischen den Modulen)

**Zuerst reproduziert:**
- (Kontext 0,9, Episode 1,9) ergab denselben Stromschlüssel wie (0, 1).
- `[1, 1.9]` lieferte zwei identische Episoden mit den IDs (1, 1).
- Ein Batch aus Kontext 0 lief unter Kontext 1.
- `chunk = -1` gab einen ungefüllten Puffer zurück.
- Ein Iterator verlor seine Episoden-IDs.

| Befund | Korrektur |
|---|---|
| **R1** Stromkennungen | Alle Schlüsselteile (Studie, Kontext, Episode, Zusatz) werden **vor** jeder Umwandlung als echte nichtnegative Ganzzahlen geprüft. Episoden-IDs werden genau einmal materialisiert, Duplikate abgewiesen, leere Batches abgewiesen. |
| **R2** Bindung | Der Batch trägt Studie, Kontext, Kontext-Fingerabdruck und Konfigurations-SHA. `simulate` prüft das samt Formen und Endlichkeit **vor** jeder Dynamik. `ContextSpec` wird strukturell validiert: echte Ganzzahlen, vier disjunkte Paare, Schreib- und Leseknoten sowie Referenz gleich der gespeicherten Permutation. |
| **R3** Chunk | Er wird vor jeder Allokation als positive echte Ganzzahl geprüft. Es gibt keine pauschale Nullinitialisierung. |
| **Ergänzungen** | Der Surrogat-Invariantenbericht bleibt erhalten (`coupling_matrices_with_report`, mit Kontext, Fingerabdruck, Stromschlüssel und Vorschlagszahl). Die Vorschlagszahl ist strikt: 0 wird nicht still zum Standard. Die Konfiguration ist tief unveränderlich und über `config_sha256()` an die Datei gebunden. |

**Danach:** Alle fünf Fälle werden abgewiesen, und der Iterator behält seine IDs.

**Mutation der neuen Verträge:** 13/13. Zwei Überlebende im ersten Lauf waren eine echte Testlücke: Grobe Negativfälle wurden erst von späteren Prüfungen abgefangen. Dafür gibt es jetzt sonst gültige Permutationsabweichungen als Tests.

**Tests:** 182/182.
