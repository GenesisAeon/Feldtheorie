# SF-001 V2: S00/S01 Modellpopulationen

Künstliche Modellpopulationen mit einer ausdrücklich künstlichen Reproduktionsregel (Plan §7, §5.2 Bedeutung 2). Es gibt keine kosmologische, astrophysikalische oder Schwarzloch-Deutung.

- [protocol_v2.json](protocol_v2.json): Regeln, Bedingungen, Budgets, Aussterberegel, Metriken und Erwartungen. Alles ist vor dem Lauf festgelegt und im selben Commit wie das Ergebnis eingecheckt; der Zeitpunkt ist also nicht separat per git belegt. `raw.json` enthält die SHA-256 des Protokolls und des Codes.
- [branching.py](branching.py): exakter Erwartungsoperator M diag(b) und stochastischer Simulator mit Obergrenze, Gründerlinien und Aussterberegel.
- [run_v2.py](run_v2.py) erzeugt `runs/v2_s00_s01/raw.json`.
- [evaluate_v2.py](evaluate_v2.py) wertet aus. Es importiert den Simulator nicht und schreibt `results.json`, `results.yaml` und [RESULTS.md](runs/v2_s00_s01/RESULTS.md).

Reproduktion aus dem Repository-Root:

```
python -m experiments.kosmische_vererbung.sf001.run_v2 --out <neuer Ordner>
python -m experiments.kosmische_vererbung.sf001.evaluate_v2 --run <neuer Ordner>
python -m pytest -q -p no:cacheprovider experiments/kosmische_vererbung/tests
```

## Einordnung (11. Oktober 2026)

- **Was die Regeln implizieren, tritt ein.** Unter Selektion steigt die Fehlanpassung E1 monoton mit der Mutationsrate: 0 / 0,038 / 0,189 / 0,552 für mu = 0 / 0,01 / 0,05 / 0,2. Bei gelöschter Typvererbung (E) liegt sie mit 1,208 auf dem Niveau der neutralen Population (1,204). Die stochastischen Mittel liegen nahe der deterministischen Referenz. Das prüft die Implementierung und ist keine Entdeckung.
- **Abweichung von der vorab notierten Erwartung:** Die Zahl überlebender Gründerlinien (E3) fällt unter Selektion nur wenig stärker als neutral: 5,1 ± 1,4 gegenüber 6,7 ± 1,7 von 100. Schon neutrale Drift mit Obergrenze 200 lässt in 60 Generationen über 90 % der Linien aussterben. E3 trennt Selektion und Neutralität in diesem Aufbau daher schlecht.
- **Nicht geprüft:** In keinem Replikat starb die Population aus (E4 = 0). Die Aussterberegel ist nur durch Tests belegt (K4, Galton-Watson-Orakel); über Aussterbedynamik sagt der Lauf nichts.
- **Budget:** Die verbrauchten Individuen-Generationen sind in allen Bedingungen praktisch gleich (etwa 11 830). Die Bedingungen sind in diesem Sinn fair budgetiert.
- **Nicht ausgeführt:** Der historische Mandala-Universumsbaum (F8) wurde nicht ausgeführt. Die neutralen Bedingungen N0/N1 bilden die faire, reihenfolgeunabhängige Zufallskontrolle. Cosmic Loop ist nach Entscheidung kein Vergleichsmodell.
