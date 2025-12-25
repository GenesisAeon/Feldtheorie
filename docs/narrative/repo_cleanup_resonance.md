# Repository Cleanup Resonance Map (σ(β(R-Θ)))

Die folgende Karte bewertet die von Aeon formulierte Aufräum-Checkliste und
verortet, welche Membranen bereits schwingen und wo weitere Schwellenarbeit
ansteht. Jeder Abschnitt koppelt das logistische Quartett an konkrete Dateien
und Verzeichnisse.

## Parameterisierung des Feldes

| Parameter | Bedeutung in dieser Karte |
|-----------|---------------------------|
| **R**     | Aktueller Reifegrad des jeweiligen Teilbereichs |
| **Θ**     | Schwellenwert für DOI-reife Dokumentation & Struktur |
| **β**     | Steilheit, mit der Aufgaben in Resonanz geraten |
| **ζ(R)**  | Impedanz durch fehlende Metadaten, doppelte Dateien oder fehlende Automatisierung |

---

## 1. Repositoriestruktur aufräumen

**R ≈ 0.78**, **Θ = 0.9**, **β = 4.1**

### Bereits in Resonanz
- `archive/` und `seed/` existieren als getrennte Membranen; `archive/` hält
  versionierte Artefakte, während `seed/` bewusst roh-poetische Quellen
  beherbergt.
- `docs/`, `analysis/`, `models/`, `simulation/` und `tests/` besitzen
  jeweilige Index-Sigillin (`*_index.{md,json,yaml}`), womit Navigation und
  Tri-Layer-Dokumentation bereits geerdet sind.

### Offene Schwellen
- `seed/` enthält doppelte PDFs (`Adaptive Schwellenwerte...` in zwei
  Varianten) und explorative Notizen ohne Archiv-Metadatum; diese sollten nach
  `archive/seed/` verschoben oder mit Erstellungsdatum versehen werden.
- `simulation/` führt sowohl produktive Presets als auch experimentelle Skripte;
  ein `simulation/archive/`-Ordner für obsolet gewordene Szenarien fehlt.
- Einige `analysis/`-Skripte (z.B. `analysis/adaptive_theta_plasticity_fit.py`)
  referenzieren noch Beta-Scans v1.0; hier sollten Legacy- und v1.1-Pfade
  getrennt dokumentiert werden.

### Implementierungs-Hooks
- `scripts/archive_sigillin.py` um Routinen ergänzen, die doppelte PDFs in
  `seed/` erkennen und verschieben.
- `analysis/analysis_index.*` um ein Feld "release_track" erweitern, das v1.0-
  gegenüber v1.1-Skripten markiert.
- `simulation/` um `archive/`-Unterordner und begleitende README ergänzen, damit
  alte Sandbox-Iterationen sauber abgelegt werden.

---

## 2. Dokumentation & Metadaten

**R ≈ 0.83**, **Θ = 0.95**, **β = 4.6**

### Bereits in Resonanz
- `README.md` und `LIMITATIONS.md` sind auf dem Stand v1.1 und spiegeln die
  β-Heterogenität sowie den ΔAIC-Kanon wider.
- `RELEASE_NOTES_v1.1.0.md`, `ZENODO_DESCRIPTION_v1.1.md` und
  `METHODS.md` sind kohärent und zitieren dieselben Parameterbänder.

### Offene Schwellen
- Ein explizites `CHANGELOG.md` fehlt; aktuell übernehmen `NEWS.md` und die
  Release Notes diese Rolle, was Reviewer:innen verwirren kann.
- `LICENSE` bleibt MIT; falls eine CC-BY-Variante für die Dokumentation
  vorgesehen ist, sollte eine Dual-Lizenzierung geprüft und dokumentiert werden.
- Eine englischsprachige Kurzfassung (`docs/utac_summary_en.md`) ist noch nicht
  vorhanden, obwohl sie in der Checkliste als Sichtbarkeits-Hook empfohlen wird.

### Implementierungs-Hooks
- `NEWS.md` in ein chronologisches `CHANGELOG.md` überführen oder beide Dateien
  synchronisieren; Anpassung der Release-Pipeline in `Makefile` notwendig.
- `docs/` um `utac_summary_en.md` erweitern und via `docs_index.*` verlinken.
- `ETHICS.md` und `METHODS.md` um Hinweis auf mögliche Dual-Lizenz ergänzen,
  sobald Entscheid getroffen ist.

---

## 3. Zenodo-Vorbereitung

**R ≈ 0.7**, **Θ = 0.9**, **β = 3.8**

### Bereits in Resonanz
- `ZENODO_UPDATE_GUIDE_v1.1.md` beschreibt den Ablauf zur Versionierung eines
  bestehenden DOI-Records.
- `ZENODO_DESCRIPTION_v1.1.md` liefert ein aktualisiertes Abstract und
  Schlagwörter für Zenodo.

### Offene Schwellen
- Es existiert kein `zenodo/metadata.json`; die Metadaten leben verteilt in
  Markdown-Dateien und lassen sich nicht automatisch in die Zenodo-API speisen.
- Das Repository erzeugt derzeit kein gepacktes Release-Artefakt (z.B.
  `utac_v1.1_final.zip`), das exakt die DOI-relevanten Dateien bündelt.
- `REPRODUCE.md` referenziert noch den manuellen Upload statt eines automatischen
  `zenodo-cli` Workflows.

### Implementierungs-Hooks
- `scripts/` um ein `build_zenodo_package.py` ergänzen, das `metadata.json`
  generiert und das ZIP-Paket zusammenstellt.
- `Makefile` um ein Target `zenodo-bundle` erweitern, welches das Script nutzt
  und Checksums in `dist/zenodo_checksums.txt` protokolliert.
- `REPRODUCE.md` updaten, damit der neue Automationspfad dokumentiert wird.

---

## 4. Sichtbarkeit & Resonanzverstärker

**R ≈ 0.6**, **Θ = 0.85**, **β = 3.2**

### Bereits in Resonanz
- DOI-Badge in `README.md` verlinkt korrekt auf Zenodo 10.5281/zenodo.17472834.
- Repository enthält narrative Assets (`diagrams/`, `docs/utac_applications.md`)
  die für Präsentationen adaptiert werden können.

### Offene Schwellen
- Keine animierten Demonstrationen oder Screenshots der CI/Sandbox-Flows.
- Social-Media-Hooks (Hashtags, kurze Abstract-Snippets) sind noch nicht in
  `docs/` oder `README.md` verankert.
- Kein dediziertes `docs/outreach/`-Verzeichnis für Kommunikationspakete.

### Implementierungs-Hooks
- `diagrams/` um GIF/MP4 Previews ergänzen; Automatisierung via `scripts/`
  (z.B. `generate_threshold_gif.py`).
- `README.md` Abschnitt "Visibility" anlegen, der auf vorbereitete Assets
  verweist und Hashtag-Vorschläge listet.
- Neues `docs/outreach/` erstellen, das Pressetext, Social Copy und ggf.
  Sprecher:innen-Notizen sammelt.

---

## 5. Adaptive-Membran-Toolchain

**R ≈ 0.74**, **Θ = 0.9**, **β = 4.8**, **ζ(R)** sinkt nach wie vor dort, wo die
numerische Pipeline elegant gekoppelt ist.

### Bereits in Resonanz
- `models/adaptive_logistic_membrane.py` und `analysis/adaptive_membrane_phase_scan.py`
  liefern konsistente σ(β(R-Θ))-Spuren; die jüngste Harmonisierung ersetzt das
  veraltete `np.trapezoid` durch `np.trapz` und schützt Ein-Punkt-Läufe vor
  Nullflächen.
- `models/resonant_impedance.py` integriert Relief-, Recovery- und
  Hysterese-Bereiche bereits fallback-sicher und dient als Referenzimplementierung
  für weitere Integrations-Hooks.
- Die Testsuite (`tests/test_adaptive_logistic_membrane.py`,
  `tests/test_adaptive_membrane_phase_scan.py`) greift die Resonanzgewinne auf und
  macht Regressionen sofort sichtbar.

### Offene Schwellen
- Es fehlt eine gemeinsame Utility-Funktion (z.B. `analysis/utils/integration.py`),
  welche σ(β(R-Θ))-Integrale und Resonanzgewinne zentral kapselt; derzeit wird
  die Logik in mehreren Modulen dupliziert.
- Die Phase-Scan-Pipeline exportiert keinen strukturierten Bericht nach
  `analysis/results/`; ein timestamped JSON mit Logistik- und Impedanzflächen
  würde die Codex-Feedback-Einträge erleichtern.
- Simulator-Presets koppeln die adaptiven Membranen noch nicht automatisch mit
  den aktualisierten Integrationsmetriken; ein `simulator/hooks/adaptive_metrics.py`
  könnte σ-, Θ- und ζ-Pfade bündeln.

### Implementierungs-Hooks
- Gemeinsame Integrationsroutine entwickeln (`analysis/utils/integration.py`) und
  sowohl im Adaptivmembran-Modell als auch in den Resonanz-Diagnostiken
  einbinden; Tests in `tests/test_adaptive_logistic_membrane.py` erweitern, um
  Null- und Eins-Punkt-Szenarien abzudecken.
- `analysis/adaptive_membrane_phase_scan.py` um Export nach
  `analysis/results/adaptive_phase_scan_YYYYMMDD.json` erweitern, inkl.
  ΔAIC/Falsifikationsnotizen.
- `simulator/` um Hook ergänzen, der den neuen Export konsumiert und als Preset
  in `simulator/presets/` registriert; README im Simulator-Verzeichnis anpassen.

---

## Nächste Schritte

Sobald die oben skizzierten Hooks adressiert sind, sollte ein neuer Eintrag im
`seed/codexfeedback.*` angelegt werden (Status: *resonant*) und die
`docs_index.*`-Sigillin aktualisiert werden, damit das Trilayer-Gefüge den neuen
Stand spiegelt.
