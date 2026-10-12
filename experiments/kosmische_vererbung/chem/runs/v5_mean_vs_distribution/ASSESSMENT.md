# Bewertung KV-V5: Mittelwert gegen Verteilung

> **Korrektur-Vermerk (12. Oktober 2026): durch V5c eingeschränkt.** Siehe [`../v5c_resolution/ASSESSMENT.md`](../v5c_resolution/ASSESSMENT.md); Protokoll `c63688884d`, Lauf `34e44de295`. Dieser V5-Bericht, die Daten und die Ergebnisdateien bleiben unverändert.
>
> - **Die P3-Werte bei k > 0 sind Rasterartefakte.** Das betrifft r_max = 6,95e-3 und die Pop-III-Masse von 5000 M☉. Ereignisgenau beträgt die Pop-III-Masse 500,25 bzw. 50,025 M☉, und r ist etwa zehnfach kleiner. Diese Massen sind Werte der im Runner gewählten Bündelung (gültig für dt ≥ t*), keine kontinuierlichen Integrale; kontinuierlich wären es 500,125 bzw. 50,024 M☉.
> - **P3 bei k = 0,01:** r ist fern der Rückgabesprünge klein positiv (4–7e-4).
> - **P3 bei k = 0,1:** r ist fern der Rückgabesprünge nicht von 0 unterscheidbar. Gemeint ist die vorab gesetzte numerische Auflösung (|r| ≤ atol = 10⁻⁴), kein statistischer Test.
> - **An den Rückgabesprüngen** (Vielfache von 10 Myr) ist r nicht aufgelöst, bei k = 0,01 wie bei k = 0,1.
> - **„Entgegengesetzte Vorzeichen P3/S“ gilt belastbar nur für k = 0.** Unberührt bleiben P3 bei k = 0, S und L.
> - **timeseries.json:** Die Werte für P3 bei k > 0 sind nicht als P3-Signal zu verwenden.
> - **Mittelwert-Suffizienz (Ergänzung nach Astras Review ASTRA-2026-10-12-03):** Der Satz unten, Z̄ sei bei L „exakt hinreichend“, gilt nur für die hier verglichenen Anfangszustände A, B und C mit derselben festgelegten (leeren) Vorgeschichte. Er ist keine allgemeine Suffizienz von Z̄. Die SCF-Kontrolle KV2 zeigt, dass bei veränderter Rückgabevorgeschichte selbst unter L derselbe heutige Mittelwert zu verschiedenen nächsten Mittelwerten führt.

Lauf nach `protocol_v5.json`, festgelegt in Commit `bec0d1bc5b` vor dem Lauf. Daten: `raw.json`, Auswertung `results.json`/`results.yaml`/`RESULTS.md`, Zeitreihen für SCF in `timeseries.json`. Das Modell ist synthetisch: keine Sternphysik, keine Beobachtungsaussage, kein JWST-Bezug.

r(t) = (Z̄_A − Z̄_B)/Z̄_B. A ist heterogen (Zonen mit Z = 0 und 0,02), B homogen (0,01 und 0,01), C eine Zone mit 0,01. Die Primärauflösung ist dt = 0,5 Myr.

## Erwartungen einzeln

| # | Erwartung (Protokoll) | Ergebnis | Status |
|---|---|---|---|
| 1 | L: abs(r) ≤ 1e-12 für alle t und k | max abs(r) = 4,3e-15 | bestätigt |
| 2 | B = C bis 1e-12 (alle Regeln) | max. relative Abweichung 0,0 | bestätigt |
| 3a | P3: r > 0 | max r = +3,9e-2 (k = 0), +7,0e-3 (k = 0,01 und 0,1) | bestätigt |
| 3b | P3: abs(r) sinkt mit wachsendem k | sinkt von k = 0 auf k > 0; bei k = 0,01 und k = 0,1 identisch (6,951e-3) | **teilweise**: nicht streng monoton |
| 3c | P3: Pop-III-Masse nur in A, in B gleich 0 | A: 2,96e4 M☉ (k = 0), 5000 M☉ (k > 0); B: 0 | bestätigt |
| 4a | S: r < 0 | max abs(r) = −2,5e-2 / −1,3e-2 / −2,6e-3 | bestätigt |
| 4b | S: abs(r) sinkt mit wachsendem k | 2,5e-2 > 1,3e-2 > 2,6e-3 | bestätigt |
| 5 | P3 und S brechen die Mittelwert-Suffizienz mit entgegengesetztem Vorzeichen | P3 r > 0, S r < 0 | bestätigt |
| 6 | f0_A fällt bei k > 0 im ersten Austauschschritt auf 0; f_primordial_origin bleibt > 0 | f0_A(5 Myr) = 0 bei allen k; f_primordial_origin_A(100 Myr) = 0,374 | f_primordial_origin bestätigt. f0 = 0 bei 5 Myr ist damit vereinbar, den Zeitpunkt „erster Austauschschritt“ löst das Beobachtungsraster von 5 Myr aber nicht auf: **nicht geprüft** |
| 7 | P3, k > 0: Pop-III-Masse durch dt bestimmt, nicht aufgelöst | 5000 M☉ bei dt 0,5 gegenüber 2500 M☉ bei dt 0,25 (relative Abweichung 1,0) | bestätigt, D4-Status `numerical_failure` für diese Größe |

D5: Der Bilanzfehler liegt in allen Läufen unter 5e-15 (relativ).

Die Auflösungsprüfung D4 für Z̄ ergibt in allen Läufen höchstens 5,2e-3 relativ (Toleranz 5 %), Status `evaluated`.

## Nachträgliche Beobachtung (nicht im Protokoll vorgesehen)

D4 prüft Z̄, nicht r. Bei P3 mit k > 0 halbiert sich r mit dt: max r = 6,95e-3 bei dt 0,5 gegenüber 3,48e-3 bei dt 0,25. Ursache ist die nicht aufgelöste Pop-III-Masse (Erwartung 7); der Unterschied zwischen A und B entsteht dort fast nur aus dem ersten Pop-III-Schritt. Das r von P3 bei k > 0 ist in diesem Lauf deshalb **nicht belastbar**. Belastbar ist nur, dass es in diesem Modell klein und positiv ist.

Eine feinere Auflösung wäre ein neues Protokoll. Ich habe sie in diesem Lauf bewusst nicht nachgeschoben.

Zum Vergleich, max r bei dt 0,5 gegen dt 0,25:
- P3, k = 0: 3,93e-2 gegen 4,04e-2 (2,8 %).
- S, k = 0: −2,531e-2 gegen −2,538e-2 (0,3 %).
- S, k = 0,01: −1,287e-2 gegen −1,282e-2 (0,4 %).
- S, k = 0,1: −2,58e-3 gegen −2,45e-3 (5,3 %). Hier ist r klein; Vorzeichen und Größenordnung sind stabil, der Betrag ist nur auf etwa 5 % genau.

## Kernaussage

- **L (Nullmodell):** Bei Z-blinder, linearer Rückführung ist der Mittelwert Z̄ ein exakt hinreichender Zustand. Heterogene und homogene Anfangszustände mit gleichem Z̄ entwickeln sich ununterscheidbar (bis 4e-15).
- **P3 und S:** Beide Regeln brechen das, mit entgegengesetztem Vorzeichen.
  - P3 (Schwelle mit Pop-III-Sonderertrag): Die heterogene Verteilung reichert schneller an, r > 0.
  - S (Sättigung ohne Pop III): Sie reichert langsamer an, r < 0.
- **Folgerung:** Eine beobachtete Mittelwert-Unzureichendheit belegt deshalb **keinen** bestimmten Mechanismus, insbesondere keine Pop-III-Physik. Ohne Kenntnis der Regel ist aus Z̄ allein nicht entscheidbar, welcher Mechanismus wirkt.
- **Austausch:** Schneller Austausch zwischen den Zonen verkleinert den Unterschied (S monoton; P3 von k = 0 auf k > 0).
- **f₀:** f₀ (Zonen mit Z < 1e-5) und f_primordial_origin sind verschiedene Größen. f₀ fällt früh auf 0, während noch rund 37 % des Gases primordialer Herkunft sind.

**Reichweite:**
- zwei Zonen, synthetische Erträge, deterministisch, 100 Myr;
- keine räumliche Struktur, keine Beobachtungsoperatoren für Linien (V6) und keine realen Ertragstabellen (V4).
