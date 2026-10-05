# M11 – Ergebnis: die vorhandene Erinnerung besser auslesen

Eingefroren: Tag `m11-freeze` (Commit 1a5423f), Protokoll `c25c9cdd…`, Referenzen `bfaaba5f…`, geprüfter Code `10cd638`, gebunden an den M10-Freeze. Ausgewertet nur mit dem eingefrorenen Referenzartefakt. Bayes-Werte B sind Monte-Carlo-Schätzungen; ihr Standardfehler (SE ≤ 9·10⁻⁵) wird getrennt ausgewiesen und ist in den Seed-Intervallen nicht enthalten.

## Ablauf: zwei Versuche

1. **Erster Versuch `m11-research-20261005T034640-10450239`: unvollständig.**
   - Der Rechner ging für 3 h in den Ruhezustand (00:46–03:46, laut Windows-Systemprotokoll). Danach brach der Lauf protokollgemäß mit `aborted_timeout` ab, nach 83 von 320 Zeilen.
   - Das Gate gab ihn nicht frei. Die Datei bleibt unverändert (SHA-256 `8723f978…`).
   - Die Teilwerte wurden weder angesehen noch ausgewertet.
   - Belege: `ABBRUCH_…md`, `NACHTRAG_2026-10-05_zweiter_Versuch.md` im Ergebnisordner.
2. **Zweiter Versuch `m11-research-20261005T114106-e996e301`, nach dokumentierter Freigabe von Johann/Astra.**
   - Code, Protokoll, Seeds und Budget waren unverändert; während des Laufs war der Ruhezustand blockiert.
   - Status `complete`, 4845 s bei einer Grenze von 5400 s, Gate **freigegeben**.
   - Alle folgenden Zahlen stammen aus diesem Lauf.

Entwicklungsbefunde aus der Implementierungsphase zählen nicht als Bestätigung.

## Konfirmatorisch (20 Seeds, einseitiges t mit df 19, δ = 0,01, Holm)

| Kontrast | Mittel | 95 %-t-Intervall | p (Holm) | Befund |
|---|---|---|---|---|
| **C-Daten:** LDA(16000) − LDA(1000) > δ | 0,0017 | [0,0013; 0,0021] | 1 | **nicht bestätigt** |
| **C-Modell:** MLP(1000) − LDA(1000) > δ | 0,0220 | [0,0154; 0,0285] | 0,0011 | **bestätigt** |

Zu den beiden Kontrasten:
- **C-Daten:** Mehr Trainingsdaten verbessern LDA im Hauptfall zwar messbar, aber um deutlich weniger als die vorab gesetzte Relevanzschwelle von 0,01. „Nicht bestätigt“ heißt hier nicht „kein Effekt“, sondern „unter der Relevanzschwelle“.
- **C-Modell:** Bei gleicher Trainingsgröße und auf denselben Testdaten liest das kleine MLP die Erinnerung besser aus als LDA.

## Beschreibend: Zerlegung der Lücke im Hauptfall (modular, N-Ablenkung, d = 4)

B = 0,9116, L_found = 0,7775, LDA(∞) = 0,7774, NM(∞) = 0,6346.

| Anteil der Lücke B − LDA(1000) = 0,136 | Wert |
|---|---|
| B − L_found (obere Schranke der Nichtlinearitätslücke) | 0,134 |
| L_found − LDA(∞) (Kriteriumslücke) | 0,0001 |
| LDA(∞) − LDA(1000) (Stichprobenlücke, vorzeichenbehaftet) | 0,0018 |

Fast die ganze Lücke von LDA zur Bayes-Grenze liegt daran, dass die beste lineare Regel (soweit gefunden) prinzipiell nicht weiter kommt. Weder das Kriterium noch die Trainingsgröße erklären sie. L_found ist numerisch gefunden, kein bewiesenes Optimum; deshalb ist der erste Term eine obere Schranke.

| Verfahren | n = 250 | 1000 | 4000 | 16000 |
|---|---|---|---|---|
| NM | 0,635 | 0,634 | 0,635 | 0,635 |
| LDA | 0,772 | 0,776 | 0,777 | 0,777 |
| MLP | 0,767 | 0,798 | 0,879 | 0,889 |
| geschlossener Anteil des MLP (gegen LDA(1000), gepaarter Bootstrap) | −0,07 | 0,16 [0,12; 0,20] | 0,76 [0,75; 0,76] | 0,84 [0,83; 0,84] |

Was die Tabelle zeigt:
- Das nichtlineare Auslesen schließt bei n = 16000 rund 84 % der Lücke. Es bleibt ein Abstand von 0,022 zur Bayes-Grenze.
- Bei n = 250 ist das MLP schlechter als LDA. Der Gewinn hängt also an der Trainingsgröße, die bei LDA kaum etwas bringt.
- Beide Achsen, Verfahren und Daten, wirken nur gemeinsam.

## Kontrollen

- **K0 (ohne Ablenkung, beide Netze):** Alle Verfahren konvergieren gegen B. Die Restlücke bei n = 16000 ist ≤ 0,0004.
- **Uniform, F+:** Hier ist die lineare Regel schon Bayes-optimal (L_found = LDA(∞) = B bis auf 10⁻⁷). Das MLP bringt keinen Vorteil, bei kleinem n liegt es sogar leicht darunter. Der geschlossene Anteil ist hier mangels Lücke korrekt N/A.

## Einordnung, ohne Gewinnerbehauptung

Im Hauptfall steckt die Information, die LDA verfehlt, in einer nichtlinearen Struktur der Zustände: Die Ablenkungsmuster bilden eine Mischung. Ein besseres Auslesen kann sie mit genug Daten weitgehend nutzen, das Mandala selbst bleibt unverändert. Das gilt für dieses Netz, diese Ablenkung und diese Verzögerung, nicht allgemein. Das kleine MLP ist ein Beispiel für nichtlineares Auslesen, kein bestes Verfahren.
