# Ergebnis KV-V5: Mittelwert gegen Verteilung

Protokoll `protocol_v5.json` (sha256 `902d75767f9407dc…`), deterministisch, dt 0.5 Myr (Auflösungsprüfung mit 0.25 Myr), 100 Myr. Python 3.11.9, NumPy 2.4.6, SciPy 1.15.3.

**Reichweite:** synthetisches Zwei-Zonen-Modell mit deklarierten Erträgen. Keine Sternphysik, keine Beobachtungsaussage, kein JWST-Bezug.

r(t) = (Z̄_A − Z̄_B)/Z̄_B: A heterogen (Z = 0 und 0,02), B homogen (0,01 und 0,01); beide Anfangszustände haben dasselbe Z̄ = 0,01.

| Regel | k [1/Myr] | max abs(r) (Vorzeichen) | r bei 100 Myr | t_sep [Myr] | Pop-III-Masse A [M☉] | Auflösung Z̄ (A/B) | Auflösung Pop III (A) | Bilanzfehler |
|---|---|---|---|---|---|---|---|---|
| L | 0.0 | +2.061e-15 | -1.785e-16 | – | 0 | evaluated (2.7e-03) / evaluated (2.7e-03) | evaluated (0.0e+00) | 1.2e-15 |
| L | 0.01 | -4.285e-15 | -4.285e-15 | – | 0 | evaluated (2.7e-03) / evaluated (2.7e-03) | evaluated (0.0e+00) | 3.3e-15 |
| L | 0.1 | +1.649e-15 | -7.142e-16 | – | 0 | evaluated (2.7e-03) / evaluated (2.7e-03) | evaluated (0.0e+00) | 4.3e-15 |
| P3 | 0.0 | +3.935e-02 | +1.561e-02 | 5.0 | 2.963e+04 | evaluated (3.3e-03) / evaluated (2.7e-03) | evaluated (1.2e-03) | 1.0e-15 |
| P3 | 0.01 | +6.951e-03 | +2.612e-03 | – | 5000 | evaluated (5.2e-03) / evaluated (2.7e-03) | numerical_failure (1.0e+00) | 3.5e-15 |
| P3 | 0.1 | +6.951e-03 | +2.612e-03 | – | 5000 | evaluated (5.2e-03) / evaluated (2.7e-03) | numerical_failure (1.0e+00) | 4.3e-15 |
| S | 0.0 | -2.531e-02 | -2.061e-02 | 20.0 | 0 | evaluated (2.2e-03) / evaluated (2.5e-03) | evaluated (0.0e+00) | 1.0e-15 |
| S | 0.01 | -1.287e-02 | -7.578e-03 | 25.0 | 0 | evaluated (2.2e-03) / evaluated (2.5e-03) | evaluated (0.0e+00) | 3.3e-15 |
| S | 0.1 | -2.584e-03 | -1.178e-03 | – | 0 | evaluated (2.2e-03) / evaluated (2.5e-03) | evaluated (0.0e+00) | 4.2e-15 |

| Regel | Z̄ B gegen C (max rel.) | Orakel 5 bei t = 0: Z̄_A, Z̄_B, f0_A, f0_B |
|---|---|---|
| L | 0.0e+00 | 0.01, 0.01, 0.5, 0 |
| P3 | 0.0e+00 | 0.01, 0.01, 0.5, 0 |
| S | 0.0e+00 | 0.01, 0.01, 0.5, 0 |

Erwartungen aus den Regeln (vor dem Lauf im Protokoll-Commit festgehalten):

- L: |r(t)| <= 1e-12 zu allen Zeiten und für alle k; der Mittelwert ist exakt hinreichend.
- Alle Regeln: B und C stimmen bis 1e-12 überein (zwei identische homogene Zonen = eine Zone).
- P3: r > 0, solange sich der Effekt der ersten Pop-III-Rückgaben auswirkt; |r| sinkt mit wachsendem k. Pop-III-Masse nur in A, in B gleich 0.
- S: r < 0 (die heterogene Verteilung erzeugt weniger Metalle, Konkavität); |r| sinkt mit wachsendem k.
- P3 und S brechen die Mittelwert-Suffizienz mit entgegengesetztem Vorzeichen. Aus Z̄ allein lässt sich ohne Kenntnis der Regel nicht entscheiden, welcher Mechanismus wirkt.
- f0_A fällt bei k > 0 im ersten Austauschschritt auf 0; f_primordial_origin bleibt > 0.
- Bei k > 0 überschreitet Zone 0 in A die Schwelle z_crit nach etwa z_crit/(0,02 k) Myr, also unterhalb von dt. Die Pop-III-Masse ist dann durch dt bestimmt und voraussichtlich nicht aufgelöst (D4 -> numerical_failure für diese Größe).
- Bestätigungen dieser Erwartungen prüfen die Regeln und ihre Umsetzung; sie sind keine Aussage über reale Sternpopulationen.
