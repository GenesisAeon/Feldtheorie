# Phaethon, Geminiden & Bennu Archiv (Tri-Layer Index)

Dieses Verzeichnis bündelt PDFs, Suchlogs und Notizen zum Phaethon/Geminiden/Bennu-Programm. Die Inhalte sind jetzt repokonform über ein Tri-Layer-Inventar dokumentiert:

- **JSON:** `phaethon_inventory.json`
- **YAML:** `phaethon_inventory.yaml`
- **Markdown (dieses Dokument):** Schnellüberblick & Nutzungshinweise

## Inventar-Überblick

| Kategorie          | Anzahl |
| ------------------ | -----: |
| Papers (PDF)       | 16     |
| AI-Suchlogs (TXT)  | 11     |
| Notizen (TXT)      | 3      |
| Code/Figuren       | 2      |
| Metadaten (JSON/MD)| 5      |

**Anomalie:** `SucheGemini_Phaethon, Geminiden und der Stern von Bethlehem.txt` ist leer und sollte bei Bedarf mit Inhalt ersetzt oder entfernt werden.

## Nutzung

1. **Bestandsaufnahme:** Greife auf `phaethon_inventory.(json|yaml)` zu, um Dateityp, Größe und (bei Suchlogs) das AI-System zu sehen.
2. **Lückenprüfung:** `phaethon_analysis_report.json` fasst Kategorien, AI-Counts und Anomalien für Quick-Checks zusammen.
3. **Weiterverarbeitung:** Nutze `chimera_state_model.py` und `bennu_chimera_simulation.png` als Startpunkte für die im `STRATEGIC_ROADMAP.md` skizzierten Modelle.

## Nächste Schritte (Empfehlung)

- Fehlende Inhalte nachziehen (insbesondere die leere Gemini-Datei) und anschließend das Inventar via kurzem Python-Snippet erneut erzeugen.
- Für neue Papers oder Logs stets alle drei Inventar-Schichten aktualisieren (JSON, YAML, Markdown), damit Downstream-Tools sie konsistent lesen können.
