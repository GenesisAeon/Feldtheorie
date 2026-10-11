# Kosmische Vererbung (SF-001-Erweiterung)

Arbeitsort für die Pakete V2–V6 des Plans „Kosmische Vererbung, chemische Anreicherung und SCF“ (27. September 2026). Planung, Befunde und Status stehen **nicht** hier, sondern in der gemeinsamen Roadmap: [ROADMAP.md, Abschnitt „Kosmische Vererbung“](../research_roadmap_2026/ROADMAP.md) sowie `roadmap.json`/`roadmap.yaml` unter `cosmic_inheritance`.

Stand 11. Oktober 2026: V0, V1 und V2 sind abgenommen; V2 (S00/S01) liegt in [sf001/](sf001/README.md). V3, der chemische Basiskern, liegt in [chem/](chem/README.md) und wartet auf die Abnahme.

Tests laufen ausdrücklich, weil das Root-`pytest` nur `tests/` sammelt:

```
python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
```

Die Belege aus den Nachbarrepos werden geprüft, wenn `implosive-origin-utac` und `unified-mandala` neben diesem Repository liegen oder unter `KV_EXTERNAL_REPOS` zu finden sind. Sonst werden diese Prüfungen mit Begründung übersprungen.
