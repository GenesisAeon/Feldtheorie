# UTAC Framework v4.0.0-alpha: Mirror Machine & Criticality Monitoring

## Abstract
Dieses Repository enthält die Referenzimplementierung der "Mirror Machine Architecture". Das System kombiniert Echtzeit-Datenströme (AMOC, WAIS, Coral) mit thermodynamischen Grenzwert-Analysen, um den Systemparameter $\beta$ (inverses Temperaturfeld) dynamisch zu schätzen. Ziel dieser Alpha-Version ist die technische Validierung der Sensor-Kopplung und die Reproduzierbarkeit der `state_verdict` Logik.

## Paketinhalt
1. `theory/`: formalisiert die zugrundeliegende Physik (Quantum Aliasing, Morphological Computing).
2. `sensors/`: Python-Adapter für externe Klimadatenquellen (RAPID, GRACE, NOAA).
3. `simulation/`: enthält den `mirror_machine_auditorium.py` Controller.
4. `data/derived/`: liefert die Referenzwerte `beta_estimates.csv` für Visualisierungen.

## Reproduktions-Anleitung (Quickstart)
1. `pip install -r requirements.txt`
2. `python scripts/monitoring/ews_pipeline.py` (Data Ingest)
3. `python scripts/simulation/mirror_machine_auditorium.py` (State Analysis)
4. `python scripts/analysis/visualize_oxfam_wall.py` (Visualization Output)

## Hinweise zum Release-Build
- Status: UTAC V4.0 Alpha Release "Mirror Machine"; Theorie-Module und Sensoren sind implementiert.
- Korrektur: Entfernt esoterische oder meta-reflektive Hinweise; Fokus auf technisches Framework zur Reproduktion von Systemzuständen.
- Tonfall: akademisch, präzise, reproduzierbar. Keine binären Artefakte im Paket, nur Generatoren und Referenzdaten.
