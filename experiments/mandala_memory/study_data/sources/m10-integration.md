# Lokale Integration M10 in Feldtheorie-`main` (2026-10-04)

**Auftrag:** `astra-m10-review/ERGEBNISPRUEFUNG_M10.md`: Dokumentation präzisieren, dann lokal integrieren. Kein Push.

| | Commit / Tag |
|---|---|
| Ausgangsstand `main` | `15a24d85af` (Integration R5–R8) |
| Freeze | `7b31300` (Tag `m10-freeze`): Protokoll `84d2b523…c345`, geprüfter Code `6f2acfd2a8a153c8f48bc50194cbcf651a510758` |
| Ergebnisdoku | `c9e9ffd` |
| Doku-Präzisierung (Ergebnisprüfung) | `317f8ee` (Tag `reviewed/mandala-memory-317f8ee`) |
| **`main` nach Integration** | **`2e1fe3dd2d`** (`--no-ff`-Merge) |

**Präzisiert** (nur README/ROADMAP; Daten, Protokoll und eingefrorener Code unverändert):
1. Die Symmetrie hat die tanh-Hypothese H-N motiviert. Bewiesene Störungsfreiheit (A2) gilt nur für den linearen Zwilling.
2. „Keine messbare Störung“ bei F/F+ heißt: innerhalb der Monte-Carlo-Auflösung kein Verlust erkennbar, nicht bewiesene Wirkungslosigkeit. H-F+ bleibt „nicht bestätigt“.
3. Decoderverluste (Nearest-Mean 29,9, LDA 15,75 gegen Bayes 2,36 Prozentpunkte) sind echte Leistungsverluste. Die Ursache ist durch den Vergleich allein nicht isoliert (Anisotropie, endliche Trainingsdaten und Modellklasse sind nicht getrennt geprüft).
4. p = 0 ist numerische Rundung von 1 − Φ(Z); berichtet als p_Holm < 10⁻¹².
5. Aussagen über Pausen gelten nur für die geprüften d = 3, 4, 6.

**Geprüft nach der Integration** (im Hauptcheckout `D:/mandala/Feldtheorie`):
- Seit `m10-freeze` haben sich nur `README.md` und `ROADMAP.md` geändert.
- Der Laborordner in `main` ist identisch mit dem Branch; außerhalb davon hat sich nichts geändert.
- Freeze-Konsistenz: Konstante = Protokoll = Freeze-Datensatz, Code-Prüfsummen gleich, geprüfter Commit `6f2acfd…`.
- Pflicht-Labortestlauf: **306/306**, 0 übersprungen.
- Ergebnisdatei unverändert: SHA-256 `db114706f10a335194ed5756d25470662f8780c5f9a877a8e67811c0594cb54d`, gleich dem Wert der Ergebnisprüfung.

**Nicht erneut ausgeführt:** Forschungsrechnung, Linux-Stufen, Mutationsprüfung (seit dem Freeze keine Codeänderung). **Kein Push.**
