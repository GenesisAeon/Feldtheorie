# Bewertung KV-V5c: Auflösungsstudie

**Grundlage:**
- Protokoll `protocol_v5c.json`, festgelegt in Commit `c63688884d` vor dem Lauf; Ergebnisse in `RESULTS.md` und `results.json`/`results.yaml`, Rohdaten in `raw.json`.
- 144 Läufe, alle abgeschlossen, 0 Fehlschläge; Laufzeit etwa 26 Minuten.
- Maximaler relativer Bilanzfehler: 4,4·10⁻¹⁴.
- Synthetisches Modell, numerische Studie. Keine Sternphysik.

## Erwartungen einzeln

| # | Erwartung | Ergebnis | Status |
|---|---|---|---|
| E1 | L: abs(r) ≤ 1e-12 in beiden Schemata, alle dt | max abs(r) = 2,6e-14 | bestätigt |
| E2 | grid, P3, k > 0: Pop-III-Masse = 1e4·dt, nicht konvergent | 5000 / 2500 / 1250 / 625 M☉ bei k = 0,01 und 0,1 | bestätigt (`numerical_failure`) |
| E3 | event, P3, k > 0: Pop-III-Masse = 500,25 bzw. 50,025 M☉ bei allen dt | 500,2501667968 bzw. 50,0250166806 M☉ bei allen dt; Abweichung vom Handwert etwa 1e-11 relativ | bestätigt (`evaluated`) |
| E4 | P3, k = 0: grid = event, Konvergenz erster Ordnung gegen 29 554,47 | 29 627,5 / 29 590,9 / 29 572,7 / 29 563,6 M☉, in beiden Schemata identisch; Differenz der feinsten Stufen 9,1 M☉ | bestätigt (`evaluated`) |
| E5 | event, P3, k > 0: r konvergiert, klein (etwa 7e-4 / 7e-5); bei k = 0,1 nicht von 0 unterscheidbar | Nach Protokollkriterien nur r_max_signed bei k = 0,01 konvergiert (+6,96e-4, wie geschätzt). r_final bei k = 0,01 sowie r_max_signed und r_final bei k = 0,1 sind `numerical_failure`; dort wechselt bzw. schrumpft r mit dt. | **nicht bestätigt** (nur teilweise) |
| E6 | grid, P3, k > 0: r halbiert sich mit dt, nicht konvergent | r_max 6,95e-3 / 3,48e-3 / 1,74e-3 / 8,7e-4 | bestätigt (`numerical_failure`) |
| E7 | S: grid = event, r konvergiert, nahe KV-V5 | in beiden Schemata identisch; alle sechs S-Größen `evaluated`; r_max −2,54e-2 / −1,28e-2 / −2,35e-3 für k = 0 / 0,01 / 0,1 (KV-V5: −2,53e-2 / −1,29e-2 / −2,58e-3) | bestätigt |
| E8 | Bilanzfehler < 1e-9 | 4,4e-14 | bestätigt |

## Nachträgliche Analyse (nicht im Protokoll vorgesehen)

Sie erklärt E5. Betrachtet wird r(t) im event-Schema für P3 bei k > 0, je Beobachtungszeitpunkt.

| t [Myr] | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 100 |
|---|---|---|---|---|---|---|---|---|
| k = 0,01, dt 0,5 | +6,96e-4 | −4,44e-3 | +4,73e-4 | −3,74e-3 | +4,35e-4 | −3,43e-3 | +3,98e-4 | −2,15e-3 |
| k = 0,01, dt 0,0625 | +6,96e-4 | +3,64e-4 | +4,75e-4 | +3,42e-4 | +4,38e-4 | +3,12e-4 | +4,02e-4 | +1,95e-4 |
| k = 0,1, dt 0,5 | +6,96e-5 | −5,38e-3 | +4,73e-5 | −4,57e-3 | +4,34e-5 | −4,19e-3 | +3,97e-5 | −2,62e-3 |
| k = 0,1, dt 0,0625 | +6,96e-5 | −5,85e-4 | +4,75e-5 | −4,92e-4 | +4,38e-5 | −4,50e-4 | +4,02e-5 | −2,82e-4 |

**Befund:**
- **Fern der Rückgabesprünge** (t = 5, 15, 25, … Myr) ist r bei allen dt bis auf etwa 1 % gleich und positiv. Bei k = 0,01 liegt es bei 4–7·10⁻⁴, bei k = 0,1 bei 4–7·10⁻⁵; dieses liegt unter atol (10⁻⁴) und ist damit nicht von 0 unterscheidbar.
- **Zu den Zeitpunkten 10, 20, …, 100 Myr** dominiert ein Artefakt, das etwa proportional zu dt ist:
  - In A teilt der Schwellenübergang den ersten Schritt bei t* (0,05 bzw. 0,005 Myr). Die Sterngruppe, die danach für den Rest des Schritts gebildet wird (Masse ∝ dt − t*), gibt erst bei t* + 10 Myr zurück.
  - In B gibt die entsprechende Gruppe genau bei 10 Myr zurück, im Beobachtungszeitpunkt.
  - Diese Teilung pflanzt sich alle 10 Myr fort; 10 Teilungen je Lauf entsprechen genau diesem Muster.
  - Weil die Rückgabe im Modell ein Sprung ist, vergleicht r dort A und B um t* versetzt am Sprung. Der Effekt schrumpft mit dt, ist bei dt = 0,0625 aber noch nicht abgeklungen.
- Eine Richardson-Extrapolation aus 0,125 und 0,0625 deutet auch an den Sprungzeitpunkten auf positive Grenzwerte hin: etwa +1e-3 bei k = 0,01 und +1e-4 bei k = 0,1. Das ist eine Extrapolation, kein Messwert.
- Das Raster-Schema hat bei k > 0 ein anderes Artefakt: Die Pop-III-Masse ε·M·dt hält r positiv und proportional zu dt.

## Was das für die V5-Aussage „P3: r > 0 bei k > 0“ bedeutet

- **Die V5-Zahlen für P3 bei k > 0 waren Rasterartefakte.** Das dort gemeldete r_max von 6,95·10⁻³ entsteht aus der Pop-III-Masse von einem Rasterschritt; ereignisgenau ist sie zehn- bzw. hundertmal kleiner.
- **Bei k = 0,01** bleibt das Vorzeichen r > 0 fern der Rückgabesprünge erhalten und ist dort konvergiert. Der Betrag ist mit 4–7·10⁻⁴ aber etwa zehnmal kleiner als in V5 berichtet.
- **Bei k = 0,1** ist r fern der Sprünge nicht von 0 unterscheidbar (≤ 7·10⁻⁵ < atol). An den Sprungzeitpunkten ist es nicht aufgelöst. Die V5-Aussage „r > 0“ ist für k = 0,1 nach diesem Protokoll **nicht belegt**.
- **Unberührt bleiben:**
  - P3 bei k = 0 (r_max +4,13e-2, konvergiert);
  - S bei allen k (r < 0, konvergiert);
  - L (r = 0).
- **Die V5-Kernaussage gilt damit nur noch eingeschränkt.** „P3 und S brechen die Mittelwert-Suffizienz mit entgegengesetztem Vorzeichen“ ist belastbar für k = 0 und schwach belastbar für k = 0,01, wo das P3-Vorzeichen fern der Sprünge positiv ist, der Betrag aber klein. Für k = 0,1 ist der P3-Effekt nicht von 0 unterscheidbar; dort zeigt nur S eine aufgelöste Abweichung vom Mittelwertmodell.
- Unverändert gilt: Eine Mittelwert-Unzureichendheit belegt keinen Mechanismus.

## Offene numerische Frage

Ein sauberer Vergleich an den Rückgabesprüngen bräuchte zweierlei:
- entweder Beobachtungszeitpunkte, die nicht auf Sprüngen liegen, oder eine über die Lebensdauer verteilte statt punktförmige Rückgabe;
- ein Schema, in dem das Pop-II-Restintervall nach dem Schwellenübergang nicht als Ganzes zu einem versetzten Zeitpunkt gebildet wird.

Das wäre ein neues Protokoll. Es wurde hier nicht nachgeschoben.
