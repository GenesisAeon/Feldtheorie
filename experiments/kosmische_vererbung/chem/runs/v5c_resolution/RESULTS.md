# Ergebnis KV-V5c: Auflösungsstudie

Protokoll `protocol_v5c.json` (sha256 `12d82f76b5578bc6…`), deterministisch. Python 3.11.9, NumPy 2.4.6, SciPy 1.15.3. Fehlgeschlagene Läufe: 0. Maximaler relativer Bilanzfehler: 4.4e-14.

Konvergenz: Vergleich der feinsten Schrittweiten 0,125 und 0,0625 mit absoluter und relativer Toleranz (siehe Protokoll).

| Größe | Schema | dt 0,5 | dt 0,25 | dt 0,125 | dt 0,0625 | Status | Hinweis |
|---|---|---|---|---|---|---|---|
| L|k=0.0|r_max_signed | grid | 2.06087e-15 | 4.80684e-15 | 7.35668e-15 | -1.96669e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.0|r_max_signed | event | 2.06087e-15 | 4.80684e-15 | 7.35668e-15 | -1.96669e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.0|r_final | grid | -1.78545e-16 | -1.25197e-15 | 4.65419e-15 | 1.09242e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.0|r_final | event | -1.78545e-16 | -1.25197e-15 | 4.65419e-15 | 1.09242e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.01|r_max_signed | grid | -4.28507e-15 | -4.91304e-15 | -6.82402e-15 | -2.55551e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.01|r_max_signed | event | -4.28507e-15 | -4.91304e-15 | -6.82402e-15 | -2.55551e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.01|r_final | grid | -4.28507e-15 | -1.96738e-15 | 8.95037e-16 | 3.93986e-15 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.01|r_final | event | -4.28507e-15 | -1.96738e-15 | 8.95037e-16 | 3.93986e-15 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.1|r_max_signed | grid | 1.6487e-15 | -3.58467e-15 | 1.00187e-14 | 1.55804e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.1|r_max_signed | event | 1.6487e-15 | -3.58467e-15 | 1.00187e-14 | 1.55804e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.1|r_final | grid | -7.14179e-16 | -3.21936e-15 | 6.98129e-15 | 1.55804e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| L|k=0.1|r_final | event | -7.14179e-16 | -3.21936e-15 | 6.98129e-15 | 1.55804e-14 | evaluated | nicht von 0 unterscheidbar (|r| <= atol) |
| P3|k=0.0|r_max_signed | grid | 0.0393476 | 0.0404397 | 0.0409891 | 0.0412646 | evaluated |  |
| P3|k=0.0|r_max_signed | event | 0.0393476 | 0.0404397 | 0.0409891 | 0.0412646 | evaluated |  |
| P3|k=0.0|r_final | grid | 0.0156141 | 0.0156347 | 0.015645 | 0.0156501 | evaluated |  |
| P3|k=0.0|r_final | event | 0.0156141 | 0.0156347 | 0.015645 | 0.0156501 | evaluated |  |
| P3|k=0.0|pop3 | grid | 29627.5 | 29590.9 | 29572.7 | 29563.6 | evaluated |  |
| P3|k=0.0|pop3 | event | 29627.5 | 29590.9 | 29572.7 | 29563.6 | evaluated |  |
| P3|k=0.01|r_max_signed | grid | 0.00695072 | 0.00347657 | 0.00173859 | 0.00086937 | numerical_failure |  |
| P3|k=0.01|r_max_signed | event | -0.00443836 | -0.00170112 | 0.000695864 | 0.000695857 | evaluated |  |
| P3|k=0.01|r_final | grid | 0.00261207 | 0.00130825 | 0.000654677 | 0.000327477 | numerical_failure |  |
| P3|k=0.01|r_final | event | -0.00215151 | -0.000811423 | -0.000140535 | 0.000195121 | numerical_failure |  |
| P3|k=0.01|pop3 | grid | 5000 | 2500 | 1250 | 625 | numerical_failure |  |
| P3|k=0.01|pop3 | event | 500.25 | 500.25 | 500.25 | 500.25 | evaluated |  |
| P3|k=0.1|r_max_signed | grid | 0.00695072 | 0.00347657 | 0.00173859 | 0.00086937 | numerical_failure |  |
| P3|k=0.1|r_max_signed | event | -0.00538285 | -0.00264814 | -0.00127369 | -0.00058468 | numerical_failure |  |
| P3|k=0.1|r_final | grid | 0.00261207 | 0.00130825 | 0.000654677 | 0.000327477 | numerical_failure |  |
| P3|k=0.1|r_final | event | -0.00262085 | -0.00128504 | -0.000616292 | -0.000281708 | numerical_failure |  |
| P3|k=0.1|pop3 | grid | 5000 | 2500 | 1250 | 625 | numerical_failure |  |
| P3|k=0.1|pop3 | event | 50.025 | 50.025 | 50.025 | 50.025 | evaluated |  |
| S|k=0.0|r_max_signed | grid | -0.0253135 | -0.025377 | -0.0254082 | -0.0254237 | evaluated |  |
| S|k=0.0|r_max_signed | event | -0.0253135 | -0.025377 | -0.0254082 | -0.0254237 | evaluated |  |
| S|k=0.0|r_final | grid | -0.0206084 | -0.02072 | -0.0207759 | -0.0208039 | evaluated |  |
| S|k=0.0|r_final | event | -0.0206084 | -0.02072 | -0.0207759 | -0.0208039 | evaluated |  |
| S|k=0.01|r_max_signed | grid | -0.0128668 | -0.0128216 | -0.0127984 | -0.0127866 | evaluated |  |
| S|k=0.01|r_max_signed | event | -0.0128668 | -0.0128216 | -0.0127984 | -0.0127866 | evaluated |  |
| S|k=0.01|r_final | grid | -0.00757802 | -0.00756976 | -0.00756563 | -0.00756359 | evaluated |  |
| S|k=0.01|r_final | event | -0.00757802 | -0.00756976 | -0.00756563 | -0.00756359 | evaluated |  |
| S|k=0.1|r_max_signed | grid | -0.00258374 | -0.00245253 | -0.00238739 | -0.00235494 | evaluated |  |
| S|k=0.1|r_max_signed | event | -0.00258374 | -0.00245253 | -0.00238739 | -0.00235494 | evaluated |  |
| S|k=0.1|r_final | grid | -0.00117821 | -0.00112023 | -0.00109151 | -0.00107723 | evaluated |  |
| S|k=0.1|r_final | event | -0.00117821 | -0.00112023 | -0.00109151 | -0.00107723 | evaluated |  |

Erwartungen (vor dem Lauf im Protokoll-Commit festgehalten):

- E1 L: |r(t)| <= 1e-12 in beiden Schemata und bei allen dt.
- E2 grid, P3, k > 0: pop3_mass_formed = eps*M*dt (5000/2500/1250/625 M_sun); konvergiert nicht -> numerical_failure.
- E3 event, P3, k > 0: pop3_mass_formed = 500,25 bzw. 50,025 M_sun bei allen dt (bis 1e-6 relativ) -> evaluated.
- E4 P3, k = 0: grid = event; Konvergenz erster Ordnung gegen 29554,47 M_sun; Differenz der feinsten Stufen etwa 9 M_sun -> evaluated.
- E5 event, P3, k > 0: r konvergiert und ist deutlich kleiner als in KV-V5 (grobe Schätzung proportional zur Pop-III-Masse: etwa 7e-4 bei k = 0,01 und 7e-5 bei k = 0,1; nicht bindend). Bei k = 0,1 liegt |r| voraussichtlich unter atol und ist dann nicht von 0 unterscheidbar.
- E6 grid, P3, k > 0: r halbiert sich weiter mit dt und konvergiert nicht gegen den ereignisgenauen Wert innerhalb der Folge -> numerical_failure.
- E7 S: grid = event (keine Schwelle); r konvergiert; Werte nahe KV-V5.
- E8 Bilanzfehler < 1e-9 relativ in allen Läufen.
- Ehrlich möglich: Konvergiert auch das ereignisgenaue Schema nicht, wird das als numerical_failure berichtet; dann ist die Pop-III-Frage in diesem Modell offen.
