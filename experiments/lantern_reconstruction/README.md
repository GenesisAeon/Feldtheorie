# Lantern-Rekonstruktionslabor

Ein isoliertes Entwicklungslabor. Es soll prüfen, wann das vorhandene Lantern-Netz eingeschriebenen Inhalt bewahrt, wann es ihn verteilt und wann es ihn praktisch unlesbar macht. Die beiden Aufgaben bleiben getrennt:

- **A – Spurerhalt:** Bleibt eine geschriebene Eingabe später lesbar, wenn alle Knoten beobachtbar sind?
- **B – Verteilte Auslesbarkeit:** Lässt sie sich an Knoten rekonstruieren, die nicht beschrieben wurden? Auch der Referenzknoten muss dabei unbeschrieben bleiben.

**Maßgeblich:** [Implementierungsplan Version 2.0](reference/review_package_2026-10-07/LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md) und [Fachreview](reference/review_package_2026-10-07/LANTERN_FACHREVIEW.md); Arbeitspakete LR0–LR9, Fortschritt in der [Roadmap](ROADMAP.md).

**Regeln:**
- Die Originalmodule (`v9_alpha/`, `models/`) und die Mandala-Runden M0–M12 bleiben unverändert.
- Es gibt keine Forschungsrechnung vor dem LR6-Freeze-Kandidaten und einer dokumentierten Freigabe.
- Alles bleibt auf D:, ohne Merge und ohne Push.

**Tests** werden ausdrücklich aufgerufen, weil das Root-pytest nur `tests/` sammelt:
`python -m pytest experiments/lantern_reconstruction/tests`
