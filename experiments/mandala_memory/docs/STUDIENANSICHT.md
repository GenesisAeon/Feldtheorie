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
deren Herleitung vorhanden. Ein separater historischer Vollhash des M9-Ergebnisses war
bei der Bestandsaufnahme nicht nachgewiesen. Die betroffenen Artefakte, insbesondere
gespeicherte Auswertungen, sind deshalb transparent als **neuer Anzeigesnapshot**
gepinnt. Keine rückwirkende Präregistrierung. Die unabhängige Prüfung dieses neuen
Anzeigestands durch Claude steht noch aus.

Die vollständigen Quelldateien sind über feste IDs als Text abrufbar. Keine frei
übergebenen Dateipfade, Shell-Endpunkte oder externen Dienste. Modellgewichte werden
nicht geladen oder an den Browser geschickt; M12-Modellmanifest und Modell-Freeze
dokumentieren ihre Herkunft.

## Darstellung

- M9: Überblick sowie 24 auswählbare Kombinationen mit D und dessen vorhergesagtem
  Band. Die Auswertung speichert Kurvenwerte nur bei d=0/4/8/16. Nur diese Punkte werden
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
M10 p=0 wird gemäß geprüftem Ergebnistext als `< 10⁻¹² (numerisch 0)` dargestellt.
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

Noch kein unabhängiges Claude-Review und keine Integration in main. Die neue Ansicht
ist ein Präsentationsvorhaben, keine Forschungsstudie M13. Frozen Code, Protokolle und
Originalergebnisse von M0–M12 bleiben unverändert.
