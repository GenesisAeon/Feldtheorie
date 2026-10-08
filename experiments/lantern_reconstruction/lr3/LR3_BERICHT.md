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

**Stand `d43427d`:** laut Claude geprüft. Astras unabhängige Nachprüfung steht im nächsten Abschnitt.

## Nachtrag nach der Nachprüfung `LANTERN_LR3_NACHREVIEW_2026-10-08` (Beobachtungs- und Messverträge)

**Geprüft wurde:** das Reviewpaket `GenesisAeon/mandala-memory-reviews` @ `caa0ef82`, also der Lantern-Stand `d43427d`.

**Ergebnis der Nachprüfung:** Die fünf Gegenfälle aus `REVIEW_LR3` sind behoben; Astras 44 eigene Kontrollen bestehen. Zugleich fand die Nachprüfung **neue** Lücken (F1, F2, E1, E2). Sie bestätigt also **nicht**, dass „alles unabhängig geprüft“ ist. Der Standardpfad erzeugt gültige Eingaben. Daraus folgt keine Widerlegung bisheriger Werte; es gab ohnehin noch keine Forschungsrechnung.

**Zuerst am Stand `d43427d` reproduziert**, mit eigenem Skript und mit Astras Skript (44/44 Kontrollen, F1 und F2 offen):

- **F1a:** `ObservationSpec('b', Schreibknoten, Referenz)` wurde akzeptiert. Zwischen den Zielen u und −u unterschieden sich die Merkmale bei t = 0 um genau 0,4353948827558046. Eine gültige B-Sicht zeigt 0,0.
- **F1b:** Der Knoten −26 entspricht unter NumPy-Indizierung der Referenz 8. Er wurde akzeptiert. Das Merkmalspaar war dann konstant (sin 0, cos 1), die Form blieb (4, 66).
- **F2:** Rauschen der Form (4, 1) wurde übertragen und fiel in den Referenzdifferenzen exakt heraus. Der Abstand zu den rauschfreien Merkmalen war genau 0. Auch NaN wurde akzeptiert.
- **E1:** Leseknoten als Gleitkommazahlen wurden akzeptiert, weil `(8.0,) == (8,)` gilt.
- **E2:** Die Schlüssel `(6321068099, 1, 0, 30, 0)` und `(2026100803, 4294967297, 0, 30, 0)` lieferten identische Zufallszahlen (hier NumPy 2.2.6).

| Befund | Korrektur |
|---|---|
| **F1** Beobachtungsspezifikation | `check_observation` prüft jetzt zuerst den Kontext (`check_context`). Die Aufgabe muss genau `'A'` oder `'B'` sein. Jeder Knoten und die Referenz müssen **vor** ihrer Benutzung echte Ganzzahlen in [0, 34) sein. Die Referenz muss die des Kontexts sein. A muss genau alle Nicht-Referenzknoten in aufsteigender Reihenfolge enthalten, B genau `read_nodes[:-1]`. Neu ist `observe(ctx, spec, states, eps)`: der validierte Forschungseinstieg, über den LR4 seine Merkmale bezieht. Die Klasse allein garantiert keine Gültigkeit. |
| **F2** Messarrays | `features` verlangt reelle Arrays (Ganzzahl oder Gleitkomma; bool, komplex und Objekt werden abgewiesen). Sie müssen endlich und zweidimensional mit Form (n, 34), n ≥ 1, sein, und `states` und `eps` müssen **dieselbe** Form haben. Das wird vor jeder Addition und Indizierung geprüft; implizites Broadcasting gibt es nicht mehr. Aufgabe und Indizes prüft der kontextfreie Kern ebenfalls. Für gültige Eingaben ist die Rechnung unverändert. |
| **E1** Kontext | Jeder Leseknoten und die Referenz werden einzeln als echte Ganzzahlen in [0, 34) geprüft, und zwar vor dem Tupelvergleich. |
| **E2** Stromschlüssel | Die Lücke ist durch einen dokumentierten Wertebereich geschlossen: Jede numerische Schlüsselkomponente liegt in [0, 2³²) und belegt damit genau ein 32-Bit-Wort der SeedSequence. Größere IDs bräuchten eine versionierte, gerahmte Kodierung; das wäre eine Protokolländerung. |

**Danach:**
- **Astras Skript mit `--expect-fixed`:** 44/44 Kontrollen, keine offenen Pflichtbefunde, Exit 0. F1, F2, E1 und E2 werden mit klaren Meldungen abgewiesen.
- **Alt gegen neu:** 173 Digests gültiger Aufrufe sind zwischen `d43427d` und dem Fix bitgleich:
  - 20 Kontext-Fingerabdrücke;
  - Batches für train, val und test;
  - Ströme bis 2³² − 1;
  - Surrogate;
  - A/B-Merkmale über 4 Matrizen × 3 Kontrollen × 2 Kontexte;
  - Ganzzahl- und float32-Eingaben.
- **Gezielte Mutation der neuen Wächter:** 18/18 werden von `test_lr3_nachreview.py` getötet. Im ersten Lauf waren es 17/18: Die Breitenprüfung überlebte, weil alle Formfälle auf beiden Seiten verschieden waren. Das war eine echte Testlücke; sie ist durch Fälle mit gleicher falscher Breite auf beiden Seiten geschlossen.

**Tests:** 233/233 (bisher 182, dazu 51 in `tests/test_lr3_nachreview.py`).

**Belege** (Prüfausgaben vorher und nachher, Alt/Neu-Digests, Mutationsprotokoll): `D:/mandala/mandala-memory-results/lantern/lr3_nachreview/`.

**Offen:** Astras Nachprüfung dieses Fixes.
