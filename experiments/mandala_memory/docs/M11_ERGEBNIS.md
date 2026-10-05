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

| Kontrast | Mittel | unadjustiertes 95 %-t-Intervall | p (Holm) | Befund |
|---|---|---|---|---|
| **C-Daten:** LDA(16000) − LDA(1000) > δ | 0,0017 | [0,0013; 0,0021] | 1 | **nicht bestätigt** |
| **C-Modell:** MLP(1000) − LDA(1000) > δ | 0,0220 | [0,0154; 0,0285] | 0,0011 | **bestätigt** |

Zu den beiden Kontrasten:
- **C-Daten:** Mehr Trainingsdaten verbessern LDA im Hauptfall zwar messbar, aber um deutlich weniger als die vorab gesetzte Relevanzschwelle von 0,01. „Nicht bestätigt“ heißt hier nicht „kein Effekt“: Ein kleiner positiver Effekt ist mit den Daten vereinbar und durch das unadjustierte Intervall gestützt. Er liegt aber unter der Relevanzschwelle.
- **C-Modell:** Bei gleicher Trainingsgröße und auf denselben Testdaten liest das kleine MLP die Erinnerung besser aus als LDA.

## Beschreibend: Zerlegung der Lücke im Hauptfall (modular, N-Ablenkung, d = 4)

B = 0,9116, L_found = 0,7775, LDA(∞) = 0,7774, NM(∞) = 0,6346.

| Anteil der Lücke B − LDA(1000) = 0,136 | Wert |
|---|---|
| B − L_found (obere Schranke der Nichtlinearitätslücke) | 0,134 |
| L_found − LDA(∞) (Kriteriumslücke) | 0,0001 |
| LDA(∞) − LDA(1000) (Stichprobenlücke, vorzeichenbehaftet) | 0,0018 |

Die Populations-LDA und die beste gefundene lineare Regel liegen hier sehr nahe beieinander. Gegenüber dieser numerischen linearen Referenz verbleibt fast die gesamte Lücke zur Bayes-Schätzung. Ob eine andere lineare Regel wesentlich besser wäre, ist durch die Optimierung nicht ausgeschlossen.

B − L_found = 0,134 ist eine obere Schranke der unbekannten Nichtlinearitätslücke, mit zusätzlicher MC-Unsicherheit von B. Es ist keine kausale Zuordnung von 0,134 zur Nichtlinearität. Die Holm-Korrektur gilt für die p-Werte; die Intervalle in der Kontrasttabelle sind unadjustiert.

| Verfahren | n = 250 | 1000 | 4000 | 16000 |
|---|---|---|---|---|
| NM | 0,635 | 0,634 | 0,635 | 0,635 |
| LDA | 0,772 | 0,776 | 0,777 | 0,777 |
| MLP | 0,767 | 0,798 | 0,879 | 0,889 |
| geschlossener Anteil des MLP (gegen LDA(1000), gepaarter Bootstrap) | −0,07 | 0,16 [0,12; 0,20] | 0,76 [0,75; 0,76] | 0,84 [0,83; 0,84] |

Was die Tabelle zeigt:
- Der geschlossene Anteil ist beschreibend und relativ zur LDA(1000)-Lücke. Er ist bedingt auf die eingefrorene Bayes-Schätzung, deren MC-SE separat berichtet wird.
- Bei n = 16000 schließt das MLP rund 84 % dieser Lücke. Es bleibt ein Abstand von 0,022 zur Bayes-Schätzung.
- Bei festem n = 1000 ist das MLP-Lernverfahren besser als LDA. Über die untersuchten Trainingsmengen steigt die MLP-Leistung deutlich stärker als die LDA-Leistung; bei n = 250 liegt es noch darunter.
- Ein formaler Interaktionstest oder ein universelles Erfordernis beider Änderungen wurde nicht nachgewiesen.

## Prüfungen und Korrekturen

Astras Ergebnisprüfung `ERGEBNISPRUEFUNG_78c2d2f.md` hat die Auswertung unabhängig reproduziert: vollständige Übereinstimmung, gültiger Freeze, korrekte Freigabe, Hash des ersten Laufs unverändert. Sie hat außerdem die Formulierungen dieses Dokuments präzisiert. Daten, Protokoll und eingefrorener Code blieben dabei unverändert.

## Kontrollen

- **K0 (ohne Ablenkung, beide Netze):** Analytisch liegen hier zwei Gaußverteilungen mit gleicher Kovarianz vor; die lineare Bayes-Regel ist also begründet. Die endlich trainierten Verfahren erreichen B bis auf die berichtete Restlücke, bei n = 16000 höchstens 0,0004.
- **Uniform, F+:** Die Populations-LDA und L_found erreichen innerhalb der Genauigkeit der übernommenen Bayes-Schätzung dieselbe Leistung. Ein relevanter Spielraum für das MLP ist hier nicht erkennbar, und bei kleinem n liegt es leicht darunter. Der geschlossene Anteil ist mangels Lücke N/A.

## Einordnung, ohne Gewinnerbehauptung

Im Hauptfall erreicht dieses nichtlineare Lernverfahren (kleines MLP) bei genügend Trainingsdaten deutlich mehr als die geprüften linearen Verfahren (NM, LDA und die gefundene lineare Referenz). Das Mandala selbst bleibt unverändert. Welche Eigenschaft der Zustandsverteilung das MLP nutzt, ist damit nicht nachgewiesen; die Mischstruktur aus Ablenkungsmustern ist eine naheliegende, nicht geprüfte Erklärung. Das gilt für dieses Netz, diese Ablenkung und diese Verzögerung, nicht allgemein. Das kleine MLP ist ein Beispiel für nichtlineares Auslesen, kein bestes Verfahren.
