# Ergebnis SF-001-V2: S00/S01 Modellpopulationen

Protokoll `protocol_v2.json` (sha256 `243ede8d8433bab5…`), Wurzel-Seed 3226149665, 30 Replikate je Bedingung, 60 Generationen, Obergrenze 200, 100 Gründer. Python 3.11.9, NumPy 2.4.6.

**Reichweite:** künstliche Modellpopulationen mit einer ausdrücklich künstlichen Reproduktionsregel. Keine Aussage über Kosmologie, Schwarze Löcher oder Naturkonstanten.

Mittelwert ± Standardabweichung über Replikate (E1/E2 nur über nicht ausgestorbene Replikate). E1 ist durch Konstruktion an die Selektionsregel gebunden; E2–E5 gehen nicht in die Selektion ein.

| Bedingung | E1 Fehlanpassung | E1 Referenz | E2 Typentropie [Bit] | E2 Referenz | E3 Gründerlinien | E4 ausgestorben | E5 Individuen-Generationen |
|---|---|---|---|---|---|---|---|
| N0: neutral, ohne Mutation | 1.204 ± 0.387 | 1.200 | 1.525 ± 0.335 | 2.322 | 6.7 ± 1.7 | 0.00 | 11828 ± 23 |
| N1: neutral, Mutation 0,05 | 0.984 ± 0.144 | 1.009 | 2.072 ± 0.152 | 2.255 | 6.5 ± 1.3 | 0.00 | 11826 ± 24 |
| S0: selektiv, ohne Mutation | 0.000 ± 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 | 5.1 ± 1.4 | 0.00 | 11835 ± 19 |
| S1: selektiv, Mutation 0,01 | 0.038 ± 0.020 | 0.039 | 0.257 ± 0.108 | 0.280 | 5.3 ± 1.3 | 0.00 | 11835 ± 19 |
| S2: selektiv, Mutation 0,05 | 0.189 ± 0.045 | 0.184 | 0.888 ± 0.154 | 0.894 | 4.9 ± 1.4 | 0.00 | 11836 ± 17 |
| S3: selektiv, Mutation 0,2 | 0.552 ± 0.049 | 0.555 | 1.739 ± 0.079 | 1.771 | 5.1 ± 1.0 | 0.00 | 11836 ± 18 |
| E: selektiv, gelöschte Typvererbung (M = pi 1^T, pi gleichverteilt) | 1.208 ± 0.055 | 1.200 | 2.310 ± 0.008 | 2.322 | 6.2 ± 1.3 | 0.00 | 11828 ± 23 |

Die Referenz ist die deterministische Frequenzrekursion ohne Obergrenze und ohne Drift. Sie ist kein Erwartungswert der endlichen Population (Plan §7) und dient nur zur Einordnung.

Erwartungen aus den Regeln (vor dem Lauf im Protokoll festgehalten):

- N0: Typanteile driften zufällig; die Zahl der Gründerlinien sinkt (Koaleszenz), die Typentropie bleibt im Mittel hoch, sinkt aber je Replikat durch Drift.
- S0: Typ 2 setzt sich durch; Typentropie und Linienzahl fallen stark.
- S1-S3: Mutations-Selektions-Gleichgewicht; mit steigendem mu steigt die Typentropie und die Fehlanpassung E1.
- E: Die Typverteilung bleibt nahe pi; Selektion erzeugt keine Anpassung, weil die Typvererbung gelöscht ist.
- Diese Erwartungen folgen aus den Regeln selbst. Ihre Bestätigung ist eine Prüfung der Implementierung, keine Entdeckung.
