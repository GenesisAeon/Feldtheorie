# GW-PRED-002: abgeschlossener Entwicklungslauf

Stand 11. September 2026. Die Implementierung funktioniert auf dem festgelegten Entwicklungsdatensatz. Alle 25 Prüfungen sind grün; die vollständige Zustandsprüfung und eine Wiederaufnahme sind erfolgreich. Die wissenschaftliche Bestätigungsprüfung ist noch offen.

Das Protokoll wurde in `065ee4d9207cc88d76f02a75a72c82ca3ad28e5d` vor der Implementierung festgehalten. Der Lauf verwendete den anschließend gesicherten Code aus `584b79500e912dffc17e03832802ac6a94f7bb45`. Protokolldateien und wissenschaftliche Parameter wurden nach Sichtung der Entwicklungswerte nicht verändert.

## Umfang und Beobachtung

Erzeugt wurden 384 Trainingszustände und 192 Validierungszustände aus iid, smooth und axial, je Familie 128 beziehungsweise 64. Jeder Startzustand hat genau 128 belegte Zellen. Der separate Entwicklungsseed war 2026091199. Es gab keine Ablehnungen wegen symmetriegleicher Duplikate. Beide Testsplits und die Generatorfamilien diagonal und tiles bleiben unbenutzt. Es wurden null bestätigende Wiederholungen vorbereitet.

| Beobachter | Validierungs-MAE | Lambda | Designrang | Effektive Freiheitsgrade |
|---|---:|---:|---:|---:|
| BASE | 0.107762 | 0.01 | 136 | 91.160 |
| GEOMETRY | 0.105022 | 0.01 | 210 | 137.142 |
| MICRO | 0.108874 | 1.0 | 210 | 30.693 |
| COARSE | 0.107699 | 1.0 | 208 | 31.848 |
| SHUFFLED | 0.109161 | 1.0 | 210 | 31.535 |
| PERSISTENCE | 0.309916 | – | – | – |

Die vorab definierte Vergleichsauswahl wählt COARSE. GEOMETRY liegt auf dieser Validierung um 0.002677 MAE-Punkte darunter. Diese Werte dienten auch zur Wahl von Lambda und Vergleichsstrategie; sie liefern keine unberührte Testschätzung. Aus einer Entwicklungswiederholung wird weder ein bestätigendes Konfidenzintervall noch eine Aussage über die unbekannten Familien abgeleitet. Der Unterschied auf der Validierung lässt die geometrische Idee als prüfbare Möglichkeit offen, beantwortet ihre Hauptfrage aber noch nicht.

## Verifikation und Ressourcen

Alle 576 gespeicherten Startzustände wurden aus ihren protokollierten RNG-Zuständen rekonstruiert. Für jeden Zustand wurden Dichte, Familie, Split und exakter kanonischer Schlüssel kontrolliert. Eine separat formulierte Zell-für-Zell-Regel erzeugt sämtliche gespeicherten Zielwerte mit MAE null. Gespeicherte Features, Vorhersagen und Validierungswerte stimmen mit ihrer Neuberechnung überein.

Eine tatsächliche Wiederaufnahme bewahrte die 13 vorhandenen Dateien bytegenau und ergänzte genau einen Ressourcenbericht. Ein CLI-Aufruf der Auswertung ohne Reviewnachweise brach vor der Erzeugung eines Ausgabeordners ab. Diese Eigenprüfungen ersetzen keine unabhängige Nachrechnung.

Der erste Batch benötigte 0.563 Sekunden aktive Laufzeit und maximal 43.61 MiB residenten Speicher bei einem Prozess und einem numerischen Thread. Die Laufzeit ist eine Messung dieser Umgebung, keine Prognose für sämtliche Bestätigungsläufe. Nach Wiederaufnahme umfassen die Rohdateien 3,753,365 Byte; das vollständige Archiv benötigt 814,279 Byte. Timer, virtueller Speicher und Ausgabevolumen werden durch den Runner begrenzt.

## Daten und Wiederholung

[DEVELOPMENT.json](DEVELOPMENT.json) und [DEVELOPMENT.yaml](DEVELOPMENT.yaml) enthalten denselben vollständigen Status, Umgebungsangaben, Prüfungen, Zahlen und Ressourcenberichte. [development_001.tar.gz](runs/development_001.tar.gz) enthält alle 14 unveränderten JSON-Rohdateien einschließlich Zuständen, RNG-Metadaten, Features, Vorhersagen und Fits. Jedes Archivmitglied wurde bytegenau gegen seinen Ursprung geprüft.

Archiv-SHA-256: `3ee95971ac92ade16071a6ca74a283fae6db5657aa65b68de1d00d11a9bfad58`.

Aus einem frischen Checkout im Versuchsordner:

```bash
tar -xzf runs/development_001.tar.gz -C runs
python audit_development.py runs/development_001
python -m unittest -v test_predictive
```

Entpacken setzt voraus, dass `runs/development_001` noch nicht existiert. Das Audit benötigt dieselbe aufgezeichnete Quell- und Python/NumPy/Plattformsignatur. Für eine neue Berechnung mit dem gesicherten Runner:

```bash
python runner.py development --output runs/development_new --code-commit 584b79500e912dffc17e03832802ac6a94f7bb45
```

## Nächster Prüfpunkt

G01 benötigt die unabhängige Nachrechnung des exakten Vorversuchs. Zusätzlich braucht dieser Runner den dokumentierten Protokollabgleich, einschließlich der noch nicht ausgeführten Generatorzweige für unbekannte Familien. [IMPLEMENTATION.md](IMPLEMENTATION.md) beschreibt die Prüfnachweise und Befehle. Danach werden alle zwanzig Trainings-/Validierungsfits eingefroren; erst anschließend öffnet `evaluate` die Testdaten. Der gesamte Repository-Testlauf und die tatsächlich freigegebene Auswertung wurden bisher nicht ausgeführt. Der bestehende RIG-EEG-Holdout bleibt unberührt.
