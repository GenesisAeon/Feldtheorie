# M9: eingefrorene Vorhersagen (Narrativ-Zwilling)

Trilayer nach Feldtheorie `AGENTS.md`:

| Schicht | Datei | Rolle |
|---|---|---|
| JSON | `m9_frozen_predictions.json` | maßgebliche, hash-geschützte Fassung |
| YAML | `m9_frozen_predictions.yaml` | inhaltsgleicher Strukturzwilling |
| Markdown | diese Datei | Erzählung |

Die beiden Zwillinge sind aus dem JSON erzeugt (`tools/make_trilayer_twins.py`). Ein Test prüft die Gleichheit.

**Kenndaten der Fassung:**
- SHA-256 des JSON (LF-normiert): `1e872cecaaa4ff10d796e921a289119cde32ba1fee8698cc0881e4137867de13`
- eingefroren auf Stand `6f8a81250a`, vor jeder Kernrechnung an diesen Kombinationen
- `kernel_evaluated_before_freeze: false`

**Begleitdokumente:**
- Herleitung: [`../docs/M9_HERLEITUNG.md`](../docs/M9_HERLEITUNG.md), dazu das Erratum [`../docs/M9_ERRATUM_1.md`](../docs/M9_ERRATUM_1.md)
- Prüfung und Ergebnis: [`../ROADMAP.md`](../ROADMAP.md), Abschnitte M9b und M9c
- Prüfregeln: das Feld `rules`

**Die Vorhersagen** (D = letzte Pause d ∈ 0…64 mit idealer Trefferquote ≥ p\* = 0.75; „–“ = bei keiner Pause):

| id | N/M | c | γ | ℓ | a | σ | Eingänge | H | μ_D | μ_I | D |
|---|---|---|---|---|---|---|---|---|---|---|---|
| h00 | 12/1 | – | 0.6 | 0.75 | 2.4 | 0.015 | n9/n6 | full | – | 0.209 | 2 |
| h01 | 12/3 | 0.100 | 0.6 | 0.3 | 1.6 | 0.01 | n0/n10 | full | 0.853 | 0.646 | 16 |
| h02 | 12/4 | 0.600 | 0.85 | 0.75 | 1.6 | 0.01 | n0/n1 | full | 0.378 | 0.122 | 2 |
| h03 | 12/3 | 0.150 | 0.85 | 0.4 | 0.9 | 0.03 | n6/n9 | full | 0.863 | 0.504 | 10 |
| h04 | 18/9 | 0.100 | 0.9 | 0.3 | 0.3 | 0.03 | n4/n7 | full | 0.940 | 0.457 | 12 |
| h05 | 12/1 | – | 0.85 | 0.4 | 1.6 | 0.015 | n3/n9 | full | – | 0.569 | 5 |
| h06 | 12/6 | 0.150 | 0.6 | 0.75 | 1.6 | 0.01 | n10/n8 | module_means | 0.619 | -0.133 | 7 |
| h07 | 18/2 | 0.350 | 0.85 | 0.4 | 0.3 | 0.015 | n7/n10 | module_means | 0.702 | 0.572 | – |
| h08 | 24/12 | 0.150 | 0.6 | 0.4 | 1.6 | 0.03 | n19/n18 | module_means | 0.801 | 0.396 | – |
| h09 | 24/2 | 0.150 | 0.9 | 0.4 | 1.6 | 0.015 | n8/n13 | module_means | 0.852 | 0.572 | 4 |
| h10 | 18/3 | 0.800 | 0.85 | 0.3 | 0.9 | 0.03 | n16/n6 | module_means | 0.649 | 0.690 | 0 |
| h11 | 24/6 | 0.350 | 0.9 | 0.4 | 0.9 | 0.015 | n2/n0 | module_means | 0.809 | 0.522 | – |
| h12 | 12/3 | 0.800 | 0.6 | 0.3 | 1.6 | 0.01 | n5/n8 | node n2 | 0.664 | 0.688 | – |
| h13 | 18/9 | 0.150 | 0.7 | 0.6 | 2.4 | 0.015 | n0/n15 | node n15 | 0.749 | 0.043 | [8, 9] |
| h14 | 12/4 | 0.350 | 0.9 | 0.3 | 0.9 | 0.03 | n0/n1 | node n1 | 0.844 | 0.612 | 3 |
| h15 | 24/6 | 0.100 | 0.85 | 0.6 | 1.6 | 0.03 | n4/n19 | node n19 | 0.849 | 0.247 | 7 |
| h16 | 18/2 | 0.350 | 0.6 | 0.3 | 1.6 | 0.01 | n13/n8 | node n8 | 0.754 | 0.685 | 8 |
| h17 | 24/6 | 0.100 | 0.7 | 0.75 | 2.4 | 0.015 | n15/n14 | node n14 | 0.712 | 0.092 | 1 |
| h18 | 12/4 | 0.800 | 0.7 | 0.75 | 1.6 | 0.015 | n10/n0 | sum | 0.215 | 0.198 | – |
| h19 | 18/2 | 0.100 | 0.9 | 0.4 | 1.6 | 0.03 | n6/n15 | sum | 0.888 | 0.559 | – |
| h20 | 24/6 | 0.150 | 0.85 | 0.3 | 1.6 | 0.01 | n14/n15 | sum | 0.909 | 0.628 | – |
| h21 | 24/2 | 0.800 | 0.7 | 0.6 | 0.9 | 0.015 | n15/n0 | sum | 0.148 | 0.392 | – |
| h22 | 24/2 | 0.800 | 0.7 | 0.4 | 1.6 | 0.03 | n9/n12 | sum | 0.432 | 0.595 | – |
| h23 | 12/4 | 0.150 | 0.85 | 0.75 | 0.3 | 0.015 | n2/n1 | sum | 0.760 | -0.021 | – |
