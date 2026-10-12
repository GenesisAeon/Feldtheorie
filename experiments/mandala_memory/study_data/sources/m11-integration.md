# Integration M11 in Feldtheorie main (lokal, 2026-10-05)

- **Merge:** `aba59bf6ba` (`--no-ff`) von Branch `mandala-memory` mit Stand `c06dff1c4e` in main, Vorgänger `2e1fe3dd2d`.
- **Tags:** Sicherung `backup/main-vor-m11-2026-10-05`, geprüfter Stand `reviewed/mandala-memory-c06dff1`, Freeze `m11-freeze` (1a5423f).
- Der Ordner `experiments/mandala_memory` auf main ist baumgleich mit dem Branch.
- **Nicht gepusht.** Fremde, unversionierte Dateien in der Hauptarbeitskopie blieben unberührt.

## Ablauf M11

1. Plan, Fassung 2: `56f3341`. Implementierung: `c864678`. Review-Fixes R5–R9: `e3f89c8`. Zeitbudget Option A (5400 s): `10cd638`. Service-Fix M6: `a622d43`.
2. Einmalige Referenzphase, danach Freeze `1a5423f`: Protokoll `c25c9cdd…`, Referenzen `bfaaba5f…`, geprüfter Code `10cd638`, gebunden an den M10-Freeze. Smoke-Lauf: 2 Seeds, nicht freigegeben, wie vorgesehen.
3. **Forschung, Versuch 1** `m11-research-20261005T034640-10450239`:
   - Der Rechner ging 3 h in den Ruhezustand, der Lauf brach mit `aborted_timeout` ab.
   - Nicht freigegeben, nicht ausgewertet, gesperrt. SHA-256 `8723f978…`, unverändert.
4. **Forschung, Versuch 2** `m11-research-20261005T114106-e996e301`:
   - Nach dem datierten Nachtrag und der dokumentierten Freigabe durch Johann/Astra.
   - `complete` nach 4845 s, **freigegeben**. SHA-256 `ede727c2…`.
5. Ergebnisdoku `78c2d2f`, Formulierungen nach `ERGEBNISPRUEFUNG_78c2d2f` präzisiert in `c06dff1`. Dabei wurde nur Dokumentation geändert.

## Ergebnis (Details: `experiments/mandala_memory/docs/M11_ERGEBNIS.md`)

- **C-Modell bestätigt:** MLP(1000) − LDA(1000) = +0,0220, unadjustiertes 95 %-t-Intervall [0,0154; 0,0285], p_Holm = 0,0011.
- **C-Daten nicht bestätigt:** LDA(16000) − LDA(1000) = +0,0017, Intervall [0,0013; 0,0021]. Ein kleiner positiver Effekt liegt vor, aber unter der Schwelle von 0,01.
- **Beschreibend:** Das MLP schließt bei n = 16000 rund 84 % der LDA(1000)-Lücke zur Bayes-Schätzung. B − L_found = 0,134 ist nur eine obere Schranke der Nichtlinearitätslücke.

## Prüfungen nach dem Merge (auf main)

- Freeze-Konsistenz in einem frischen Prozess bestätigt: Konstante, Protokoll, Referenzen, Code-Hashes und M10-Bindung stimmen.
- Neuauswertung von Versuch 2 auf main: freigegeben und identisch mit der gespeicherten `evaluation.json`.
- Versuch 1 bleibt nicht freigegeben.
- Pflicht-Labortestlauf (`MANDALA_LAB_REQUIRED=1`): **342/342**.
- Linux- und Mutationstests liefen zuletzt beim Service-Fix: 171/326 und 90/90. Seitdem hat sich am Code nur `FROZEN_PROTOCOL_SHA256` geändert, dazu kamen Tests, die auf den eingefrorenen Zustand umgestellt wurden. Deshalb wurden sie nicht erneut ausgeführt.
