# Studienansicht M9–M12

Lokale, rein lesende Präsentation der abgeschlossenen Forschungsrunde. Einstieg:
`http://127.0.0.1:8765/studies.html` beim bestehenden Labordienst. Das Frontend liegt im
unified-mandala-Worktree unter `experiments/memory_lab`. Die Studienansicht startet
keinen Versuch, kein Training und keine Neuauswertung.

## Daten und Vertrauen

`../study_data/manifest.json` enthält Quellen-IDs, SHA-256 der **rohen Bytes**, Herkunft,
historische Anker, Pflichtabhängigkeiten, Bindungen, Tabellen und die Feldzuordnung
jeder Zahl. `manifest.yaml` ist die identische JSON-kompatible YAML-Fassung; nur JSON
wird vom Dienst geladen. Dieses Dokument ist die narrative Fassung.

`../studies.py` pinnt den Manifest-Hash. Jeder Abruf liest, prüft und parst denselben
Bytepuffer. Alle Abhängigkeiten einer Studie müssen passen, einschließlich Dokumenten
und M9-Erratum. Einzelne unbeschädigte Werte aus einer ungültigen Studie werden nicht
weiter angezeigt. Andere Studien bleiben unabhängig verfügbar. Keine Caches oder
automatisch ermittelten Sollhashes. `.gitattributes` verhindert Zeilenendenumwandlung
im ganzen Anzeigesnapshot.

Die Dateien unter `study_data/sources` sind **unveränderte Kopien**, keine neu gerechneten
Forschungsergebnisse. Die Pfade der Originale stehen im Manifest. Der Loader benötigt
diese ursprünglichen Pfade nicht; seine Prüfung bezieht sich auf die gepinnte Kopie.
Die Oberfläche sagt ausdrücklich, dass damit nicht laufend die Original-Arbeitsdateien
überwacht werden. Ein Hashvergleich ist keine kryptografisch beglaubigte Autorschaft.

Für M10–M12 werden die Ergebnisdateien zusätzlich gegen bereits vorhandene unabhängige
Review-Hashbelege gebunden. Bei M9 ist die Bindung an die eingefrorenen Vorhersagen und
deren Herleitung vorhanden. Für das M9-Ergebnis existiert außerdem ein historischer
Vollhash: `review-m8-m9/REVIEW_MANIFEST.json` (2026-10-03), Eintrag
`review/results/m9/m9-evaluation--8d353dbc88.json`, SHA-256 `8d353dbc…e857`, gleich den
jetzigen Bytes. Die gespeicherten Auswertungen von M10–M12 haben keinen historischen
Vollhash und sind transparent als **neuer Anzeigesnapshot** gepinnt. Ihre angezeigten
bestätigenden Werte und Freigaben sind per Wertgleichheit an die historischen
Review-Datensätze gebunden (`other_source`-Bindungen im Manifest):
M10 Kontraste und Freigabe ↔ `astra-m10-review/RESULT_CHECK.json`; M11 bestätigende
Kontraste, Hauptfall-Lernkurve und Freigabe ↔ `astra-m11-review/RESULT_CHECK_78c2d2f.json`;
M12 R-a/R-σ (Mittel, Intervall, p, Holm-p) und Freigabe ↔
`astra-m12-review/result-d79b7b2/verification.json`. Die übrigen M11-Fälle sind nur über
die run_id zugeordnet; die beschreibenden M12-Kurven und ΔB/ΔG sind nur durch diesen
Snapshot belegt. Keine rückwirkende Präregistrierung.

### Pin-Historie

| Pin (Manifest-SHA-256) | Quell-Commit | Stand |
|---|---|---|
| `d3417b1345e88db53960247448f7651e596707f81397b58583858b5a2468c195` | `7e4a242863` (2026-10-06) | abgelöst |
| `c02f7685ecda35856e99eeac63f2ef4a23512821fb354c36f4a299a6bf771062` | dieser Commit (2026-10-12) | aktiv |

Änderungsgrund (Claude-Review 2026-10-11, Befunde B3–B6, B10; Astra ASTRA-2026-10-12-02
empfiehlt, Johann hat den Wechsel am 2026-10-12 freigegeben): Es ändert sich **nur das
Manifest**; alle 30 Quellkopien sind bytegleich, alle angezeigten Werte gleich.
- B3: M11-Hauptzeilen benennen die Schätzart („LDA exakt“; MLP − LDA „auf denselben
  Testepisoden“) und erklären die kleine Abweichung zur Lernkurvendifferenz.
- B4: 14 neue Wertbindungen der M10–M12-Auswertungen an die Review-Datensätze (siehe
  oben); vorher hätte eine veränderte, neu gepinnte M12-Auswertung angezeigt werden können.
- B5: M9-Herkunftstext nennt den historischen Vollhash.
- B6: `zero_display` nur am Feld M10 H-N p_Holm (Beleg `m10-integration.md:17`).
- B10: das vorhergesagte M9-D-Band kommt aus der eingefrorenen Vorhersage
  (`m9-prediction /held_out/i/prediction/D_interval`), nicht aus der Ergebniskopie.

Historische Belege und Quellkopien sind unverändert.

Die vollständigen Quelldateien sind über feste IDs als Text abrufbar. Keine frei
übergebenen Dateipfade, Shell-Endpunkte oder externen Dienste. Modellgewichte werden
nicht geladen oder an den Browser geschickt; M12-Modellmanifest und Modell-Freeze
dokumentieren ihre Herkunft.

## Darstellung

- M9: Überblick sowie 24 auswählbare Kombinationen mit D und dessen vorhergesagtem
  Band aus der eingefrorenen Vorhersage. Die Auswertung speichert Kurvenwerte nur bei d=0/4/8/16. Nur diese Punkte werden
  mit den entsprechenden gespeicherten Vorhersagebandgrenzen gezeigt. Keine rekonstruierte
  65-Punkte-Kurve. Keine Zustandsanimation ohne gespeicherte Zustandsdaten.
- M10: beide Hauptkontraste, Bayes-Komponenten der nahen Ablenkung und getrennt die
  Decoderverluste im modularen tanh-Netz bei d=4.
- M11: beide Hauptkontraste und gespeicherte Lernkurven der vier Fälle. Nearest-Mean/LDA
  exakt auf der Modellverteilung, MLP auf Testepisoden; die Schätzarten sind benannt.
  Nur der vollständige zweite Versuch. Der erste Versuch bleibt als Abbruch im
  Integrationsbericht dokumentiert; keine Teilwerte werden ausgewählt.
- M12: beide Endpunkttests, getrennte Amplituden-/Rauschansichten und gespeicherte
  Änderungen ΔB/ΔG. Keine Interpolation, keine neue Mittelwert- oder Intervallrechnung.

„Quelldaten geprüft“ bezeichnet technische Integrität. „Analytisch hergeleitet“,
„numerisch geprüft“, „bestätigend“ und „beschreibend“ bezeichnen unterschiedliche
Belegarten; das Testresultat steht separat. Im Spielbereich gilt „explorativ“.
Geltungsbereich steht sowohl am Studienkopf als auch direkt an der Darstellung.

Trefferquoten werden in Prozent, Unterschiede in Prozentpunkten angezeigt. Runden und
Skalieren für die Anzeige ist erlaubt; die API enthält die originalen Zahlen samt
JSON-Pointer. Holm gilt nur für p-Werte, nicht automatisch für die angezeigten Intervalle.
Ein p-Wert 0 wird nur dort als Schranke dargestellt, wo das Manifest ein feldspezifisches
`zero_display` mit Beleg führt (derzeit M10 H-N p_Holm: `< 10⁻¹² (numerisch 0)` gemäß
`m10-integration.md:17`); sonst neutral „0 (numerisch; siehe Quelle)“.
„Nicht bestätigt“ wird nicht zu „kein Effekt“ umgedeutet.

## Schnittstellen und Trennung

- GET `/api/studies`: feste vier Studien-IDs, keine Ergebniszahlen.
- GET `/api/studies/<id>`: vollständige validierte Darstellung oder HTTP 409 ohne Zahlen.
- GET `/api/studies/<id>/sources/<quellen-id>`: erlaubte Quelle nach erneuter Prüfung
  aller Abhängigkeiten dieser Studie. Unbekannte IDs: HTTP 404.
- Statisch: `/studies.html`, `/studies.js`, `/studies.css`.
- Bestehende POST-Routen `/api/run` und `/api/lab` bleiben explorativ und protokolliert.
  Die Studienseite benutzt sie nicht, auch nicht beim Bereichswechsel.

Antworten sind `Cache-Control: no-store`. Wechsel der Studie/Darstellung, „Erneut prüfen“
und Rückkehr auf den sichtbaren Browser-Tab prüfen neu. Die angezeigte Prüfzeit ist
der letzte Abruf, keine kontinuierliche Integritätsgarantie. Eine fehlgeschlagene
Prüfung entfernt alte Werte und Statusmarkierungen. Keine automatische Reparatur.

## Prüfungen und Grenzen der Abnahme

`tests/test_studies.py` prüft alle Feldübernahmen und Unverändertheit der Quellen,
gezielte Korruption, fehlendes Erratum, Schemawerte, falsche Laufzuordnung, Quell-ID-
Whitelist sowie GET-Routen ohne Rechen-/Protokollaufrufe. Tests arbeiten an Kopien.
Der Pflichtlauf bleibt der des Laborordners. Keine neuen Forschungsrechnungen für Tests.

Browserprüfung: alle 38 Darstellungen, 514 Tabellenfelder, Quellenlinks, schmale Ansicht,
Wechsel zum Spielbereich und zurück sowie sichtbare Ablehnung einer absichtlich
beschädigten separaten Quellenkopie. Belege und reproduzierbare Prüfskripte liegen lokal
unter `D:/mandala/mandala-memory-results/studies-review/`. Keine öffentlichen URLs.

Unabhängiges Claude-Review: `studies-review/claude-review-2026-10-11/REVIEW.md` (lokal).
Keine Integration in main. Die neue Ansicht
ist ein Präsentationsvorhaben, keine Forschungsstudie M13. Frozen Code, Protokolle und
Originalergebnisse von M0–M12 bleiben unverändert.
