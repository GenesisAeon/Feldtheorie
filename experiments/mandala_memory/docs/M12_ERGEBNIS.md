# M12 – Ergebnis: Robustheit des festgehaltenen Auslesens

**Leitfrage:** Wie verändert sich die Ausleseleistung bei anderer Ablenkungsamplitude oder anderem Messrauschen, wenn die trainierten Decoder unverändert bleiben?

**Fall:** modulares Netz, nahe Ablenkung, d = 4. Ausgangsbedingung c₀: Amplitude 0,6, σ = 0,02. Die Decoder sind MLP und LDA, je 20 Modelle, einmal in c₀ trainiert mit n = 16 000.

## Ablauf und Belege

| Schritt | Stand | Ergebnis |
|---|---|---|
| Plan Fassung 2 | `d1acc4a` | – |
| Implementierung, Review-Fixes | `ba5dabc`, `15edfbd` | Nachprüfung durch Astra |
| Protokoll-Freeze | `f3a5bc2`, Tag `m12-freeze` | Protokoll `f3174a7d…`; einzige Codeänderung: die Freeze-Konstante |
| Referenzphase, einmalig | `331f422` | 56 s; B(c) mit 2·10⁶ MC-Ziehungen je Bedingung, Populations-LDA exakt |
| Smoke | – | vollständig, strukturell gültig, keine Alarme; wie vorgesehen nicht freigegeben und nicht interpretiert |
| Trainingsphase, einmalig | – | 2343 s, Ruhezustand blockiert; jeder Seed mit bitgleichem Roundtrip |
| Modell-Freeze | `e8e53a8`, Tag `m12-models` | Manifest `e128de27…`; NPZ als binär versioniert; Git-Blob gleich Datei |
| Robustheitsauswertung, einmalig | `093d34f` | Lauf `m12-research-20261005T170243-972cca01`, 35 s, Ergebnis-SHA-256 `90d4ac29…` |

Es gab je Phase genau einen Versuch, ohne Abbruch und ohne Wiederholung. Ergebnis, Auswertung und Lesefassung liegen unter `D:/mandala/mandala-memory-results/m12/research/`.

**Freigabe:** strukturell gültig; Diagnosen D1 bis D4 (194 Prüfungen) ohne Alarm. D1: B(c₀) = 0,9114 gegen den M10-Wert 0,9116, Differenz −0,00017 bei einer Toleranz von 0,0005.

## Konfirmatorisch (20 Seeds, einseitiger t-Test, df = 19, δ = 0,01, Holm)

**Frage:** Ist das fixierte MLP an den beiden erhöhten Endpunkten um mehr als 0,01 besser als die fixierte LDA, gemessen auf denselben Testepisoden?

| Test | Bedingung | MLP − LDA | unadjustiertes 95 %-t-Intervall | p (Holm) | Befund |
|---|---|---|---|---|---|
| R-a | Amplitude 0,9 | +0,104 | [0,103; 0,105] | < 10⁻³⁰ | **bestätigt** |
| R-σ | σ = 0,03 | +0,043 | [0,042; 0,043] | < 10⁻³⁰ | **bestätigt** |

Nicht getestet wurden die Nichtunterlegenheit gegenüber c₀ und die Erhaltung der Größe des Ausgangsvorteils (+0,113). Beim Rauschen schrumpft der Vorteil deutlich und besteht trotzdem.

## Beschreibend

ΔB ist die Änderung der Bayes-Leistung, angegeben als Schätzwert mit seinem MC-SE (≤ 1,4·10⁻⁴); ein Seed-Intervall gibt es dafür nicht. ΔG ist die Änderung des Abstands zur Bayes-Grenze. Bei beiden Größen heißt ein positives Vorzeichen „schlechter als in c₀“. Die Seed-Intervalle der Verluste sind sehr eng (meist ±0,001).

| Bedingung | B | ΔB | MLP | Verlust MLP | ΔG MLP | LDA (exakt) | Verlust LDA | ΔG LDA | Vorteil MLP − LDA (Test) |
|---|---|---|---|---|---|---|---|---|---|
| c₀ | 0,911 | 0 | 0,890 | 0 | 0 | 0,777 | 0 | 0 | +0,113 |
| Amplitude 0,30 | 0,876 | +0,035 | 0,812 | +0,078 | +0,043 | 0,848 | −0,071 | −0,106 | **−0,036** |
| Amplitude 0,45 | 0,891 | +0,020 | 0,848 | +0,042 | +0,022 | 0,810 | −0,033 | −0,053 | +0,038 |
| Amplitude 0,75 | 0,921 | −0,010 | 0,880 | +0,010 | +0,020 | 0,752 | +0,026 | +0,035 | +0,129 |
| Amplitude 0,90 | 0,925 | −0,013 | 0,836 | +0,054 | +0,067 | 0,733 | +0,045 | +0,058 | +0,104 |
| σ = 0,010 | 0,998 | −0,087 | 0,993 | −0,103 | −0,016 | 0,814 | −0,036 | +0,051 | +0,179 |
| σ = 0,015 | 0,972 | −0,060 | 0,953 | −0,063 | −0,003 | 0,797 | −0,020 | +0,040 | +0,156 |
| σ = 0,025 | 0,846 | +0,065 | 0,829 | +0,061 | −0,004 | 0,757 | +0,021 | −0,045 | +0,073 |
| σ = 0,030 | 0,793 | +0,119 | 0,779 | +0,111 | −0,008 | 0,736 | +0,041 | −0,078 | +0,043 |

**Messrauschen, festgehaltenes MLP:**
- Seine Verluste und Gewinne folgen weitgehend der Informationsänderung ΔB.
- Sein Abstand zur Bayes-Grenze ändert sich nur wenig: ΔG zwischen −0,016 und −0,003, also eher etwas kleiner als in c₀.
- In diesem Raster verhält es sich gegenüber dem Rauschen also nahezu so, wie es die geänderte Trennbarkeit des Zustands vorgibt.

**Messrauschen, festgehaltene LDA:**
- Sie profitiert von weniger Rauschen weniger als die Bayes-Grenze (ΔG bis +0,051).
- Bei mehr Rauschen verliert sie weniger (ΔG bis −0,078).
- Die Zerlegung schreibt das fast ganz der Änderung des Bayes-Abstands der **bedingungsspezifischen Populations-LDA** zu (das ist die Regel des LDA-Kriteriums, nicht die beste lineare Regel).
- Der Abstand der fixierten LDA zu dieser Populationsregel ändert sich wenig, höchstens um +0,012 bei σ = 0,010.

**Ablenkungsamplitude:**
- **Bayes-Grenze:** Sie steigt in diesem Netz mit der Amplitude (0,876 → 0,925). Eine stärkere Ablenkung macht den Zustand hier also nicht schlechter trennbar. Das wird berichtet, nicht erklärt.
- **Festgehaltenes MLP:** Es verliert in **beide** Richtungen mehr, als ΔB vorgibt (ΔG +0,020 bis +0,067). Bei Amplitude 0,9 sinkt seine Leistung um 0,054, obwohl die Bayes-Leistung um 0,013 steigt. Der Abstand zur Bayes-Grenze wächst also; die Ursache ist durch diesen Versuch nicht bestimmt. In Frage kommen die Grenzen der Modellklasse, die Fehlanpassung an die neue Bedingung, endliche Daten oder Optimierung und Regularisierung.
- **Festgehaltene LDA:** Sie wird bei kleinerer Amplitude besser (0,848 bei 0,30) und bei größerer schlechter (0,733 bei 0,90). Auch das folgt nach der Zerlegung fast ganz der Populations-LDA dieser Bedingungen; der Abstand der fixierten Regel zu ihr ändert sich höchstens um +0,003.
- **Umkehr des Vorteils:** Bei Amplitude 0,30 ist die fixierte LDA um 0,036 besser als das fixierte MLP. Bei 0,45 bleibt das MLP vorn, aber nur noch mit +0,038.

## Einordnung, ohne Gewinnerbehauptung

- **Messrauschen:** Das festgehaltene MLP ist in diesem Raster robust in dem Sinn, dass seine Leistung der vorhandenen Information folgt.
- **Ablenkungsamplitude:** Es ist empfindlich gegenüber Änderungen in **beide** Richtungen; das gilt auch bei gleich gebliebener oder höherer Bayes-Trennbarkeit.
- **Vorteil gegenüber LDA:** Er besteht an beiden erhöhten Endpunkten (bestätigt), hängt aber stark von der Bedingung ab. Bei schwächerer Ablenkung kehrt er sich um.
- **Gesamtbild:** Ein in c₀ besseres gelerntes Auslesen ist nicht automatisch unter allen geänderten Bedingungen das bessere.
- **Geltungsbereich:**
  - nur dieses Netz, diese Ablenkung, d = 4 und die 9 Rasterpunkte;
  - keine Aussage zwischen oder außerhalb der Punkte;
  - kein Vergleich mit nachtrainierten Modellen;
  - synthetische Seeds, keine biologische Aussage.
- **Modelle:** Die Basismodelle sind eine neue Stichprobe, keine Wiederholung von M11. Ihre c₀-Werte (MLP 0,890, LDA 0,777) sind mit M11 vereinbar.
