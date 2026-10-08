# Lantern-Netz reaktivieren: fachlich geprüfter Implementierungsplan

**Version 2.0 · 7. Oktober 2026 · Übergabe an Claude-Code**

Status: Umsetzungsplan für ein isoliertes Forschungslabor. Die technischen Entwicklungsarbeiten sind spezifiziert; das Studienprotokoll bleibt bis zum lokalen Integrations-, Numerik- und Budgetnachweis **nicht eingefroren**. Die beigefügten Skripte sind Kontrollwerkzeuge, keine implementierte Forschungspipeline. Es wurde kein Decoder trainiert und keine neue Forschungsserie gerechnet.

## 1. Entscheidung und Zielbild

**Empfehlung: Lantern im Feldtheorie-Repo als kleines Labor für dynamische Speicherung und verteilte Auslesbarkeit reaktivieren.** SCF kommt anschließend als optionaler Prüfadapter hinzu. Die originale Lantern-Simulation, abgeschlossene Mandala-Runden M0–M12 und SCF werden für diesen Schritt nicht umgebaut.

Das Vorhaben hat einen wissenschaftlich sinnvollen Kern: Eine bekannte dynamische Vorschrift, eine explizite Schreiboperation und ein begrenzter Beobachtungszugang erlauben zu untersuchen, welcher Inhalt später tatsächlich rekonstruiert werden kann. Die vorhandene Kopplungsmatrix ist dabei eine zu prüfende Modellvorschrift. Ihre historischen EM-, Bewusstseins- und Universalitätsdeutungen werden durch einen erfolgreichen Rekonstruktionsversuch nicht bestätigt.

Vier Fähigkeiten werden getrennt behandelt:

| Stufe | Frage | Dafür erforderlicher Versuch |
|---|---|---|
| A: Spurerhalt | Bleibt eine einmal geschriebene Eingabe später lesbar? | Alle Knoten beobachtbar; Vergleich mit freier Drift |
| B: Verteilte Auslesbarkeit | Erreicht Eingabeinformation unbeschriebene Knoten? | Schreib- und Leseknoten strikt disjunkt |
| C: Robustheit | Übersteht die Rekonstruktion Störung und konkurrierende Eingaben? | Eigenes Rausch-/Interferenzprotokoll |
| D: Assoziativer Abruf | Kann ein Teilhinweis ein zuvor gelerntes Muster abrufen? | Lernbare Speicherung, Musterbibliothek und Teilhinweis-Test |

Die erste Umsetzung umfasst A und B. C und D bleiben echte Folgestudien. Ein negativer Kopplungseffekt bei A verhindert B nicht: Informationsverteilung und lokale Haltbarkeit können unterschiedliche Ziele sein.

## 2. Prüfgrundlage und Vertrauensgrenzen

Gelesen wurden alle sechs übergebenen Dateien: ursprünglicher Plan, beide Reviews, JSON, YAML und Quelleninventar. JSON und YAML stimmen inhaltlich überein. Der SHA-256 der ursprünglichen Planfassung stimmt mit dem dort eingetragenen Wert überein.

Der lokale Stand `d1c56267ae81e90f9ebd7d5d195fea818b5f3930` ist laut Johann absichtlich nur auf seiner Festplatte vorhanden. Das ist **kein Repository-Fehler**. Hier konnte GitHub-`main` bei `2da5414c8a58ffbcf8a963c9b1f9a96202e3300a` gelesen werden. Die **elf im Inventar aufgeführten Dateien** stimmen als LF-Blobbytes mit den angegebenen Hashes überein. Daraus folgt Dateigleichheit für diese Quellen, keine Gleichheit der vollständigen Checkouts.

Zusätzlich gelesen: `pyproject.toml` und Root-`AGENTS.md`. Die Root-Governance beschreibt sich selbst als `narrative/docs` und verweist auf Eltern; Claude muss lokal die tatsächlich einschlägigen Regeln und etwaige `CLAUDE.md` prüfen. Keine Governance-Datei allein zur Vereinfachung des Vorhabens umschreiben. Trilayer-Dokumentation wird mit einer maßgeblichen JSON-Struktur und daraus erzeugtem YAML eingehalten.

Hier tatsächlich ausgeführt:

- unabhängige Rekonstruktion der Kopplungsformel aus Registry-Werten;
- Vergleich gegen vier gezielt aus dem Quelltext extrahierte Originalmethoden;
- Vergleich von 200 Phasenschritten gegen die ausgewählte Originalmethode;
- 22 analytische/numerische Kontrollgruppen ohne Feldtheorie- oder SCF-Imports.

**Nicht ausgeführt:** kompletter Registry-Import, `CollectiveField`, Hauptsimulation, Alt-Testsuite, Mandala-Pipeline, Decodertraining, Aeons Rekonstruktionspilot, Forschungsrechnung. Die AST-Auswahl in `audit_legacy_source.py` ist ausdrücklich kein Ersatz für den lokalen Importtest.

Die Kontrollumgebung war Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. Diese Bibliotheksversionen liegen teilweise außerhalb der gelesenen Feldtheorie-Paketgrenzen. Die Rechnung prüft die Mathematik; die unterstützte Projektumgebung muss Claude separat nachweisen. Keine globale Paketaktualisierung aus diesen Versionsnummern ableiten.

## 3. Fachliches Review des bisherigen Plans

### 3.1 Was übernommen wird

Kontinuierliche, neue Zielvektoren; gleichanteilsfreie Kodierung; positive Messunsicherheit; relative Phasen; Trennung von Training, Auswahl und Test; starke ungekoppelte Referenz; explizite Negativkontrollen; getrennte Artefakt- und Ergebnisfreigabe. Das sind tragfähige Grundlagen.

Aeons zentrale Einwände sind berechtigt: Der ursprüngliche Nachweis `G > 0,05` bei `tau=1` ist nach seinem bekannten Entwicklungspiloten wenig überraschend, die Zeitachse ist zu kurz, ein einzelner Satz Kodierungsorte begrenzt die Aussage und die Originalschleifen brauchen einen Laufzeitnachweis. Seine Zahlen bleiben **fremdberichtete Entwicklungsergebnisse**, da Pilotcode, Rohvorhersagen und Laufmanifest hier nicht vorlagen.

### 3.2 Was präzisiert oder korrigiert wird

1. **Nicht bloß die Erfolgsschwelle hochsetzen.** Eine auf mittlere Decoderleistung kalibrierte Zeit liefert nicht automatisch die bessere wissenschaftliche Frage. Wir behalten einen festen Zeitbereich und schätzen eine Kurve sowie einen vorab definierten Integralwert. Bekannte Pilotdaten werden offengelegt.
2. **Kontraktion ist nicht endliche mathematische Auslöschung.** Die glatte rauschfreie Kuramoto-ODE besitzt bei endlicher Zeit einen invertierbaren Fluss auf dem Torus. Unterschiede können unter Messrauschen praktisch unlesbar werden, obwohl sie mathematisch fortbestehen. Die Euler-Abbildung erbt diese Aussage nicht automatisch.
3. **Zwanzig Kontexte sind keine zwanzig Netzarchitekturen.** Neue Frequenzen und Schreib-/Leseorte erweitern die untersuchte Kontextverteilung, während dieselbe Registry-Matrix fest bleibt. Der Bericht nennt das ausdrücklich.
4. **Gewichtete Stärke statt bloß Grad.** Alle 561 möglichen ungerichteten Kanten sind positiv. Jeder binäre Grad beträgt 33. Ein „degree-preserving shuffle“ der binären Topologie wäre hier trivial. Eine geeignete Referenz erhält die gewichteten Knotensummen und verändert die Gewichte.
5. **Zwei Clipping-Zahlen.** 187 Kanten werden schon bei `kappa` auf 1 begrenzt. Nach Multiplikation mit dem Impedanzfaktor liegen nur neun Endgewichte bei 1. Die Zwischenstufe betrifft ein Drittel aller Kanten und muss mitberichtet werden.
6. **Ein Import-Audithook ist keine Sandbox.** Er liefert Diagnoseereignisse. Wenn echte Netzwerk-/Schreibisolation behauptet wird, muss sie auf Prozessebene/OS-Ebene durchgesetzt und geprüft werden; andernfalls heißt das Artefakt nur „beobachtete Importzugriffe“ [S7].
7. **Nullkontrollen brauchen nicht `G≈0` in beide Richtungen.** Ein überangepasster Decoder ohne Zielinformation kann deutlich negatives G haben. Eine Regel `abs(G)<3 SE` würde solche korrekten Negativkontrollen falsch beanstanden. Harte Zielunabhängigkeit plus einseitiger Alarm auf positive Scheinerfolge ist angemessen.
8. **Eine kleine p-Zahl löst die Scope-Frage nicht.** Auch eine stabile Leistungsdifferenz über viele Trainingssätze bleibt eine Aussage über die definierte synthetische Aufgabe und Kontextverteilung.

## 4. Reproduzierbare Bestandsbefunde

| Kennzahl | Unabhängig berechnet |
|---|---:|
| Knoten / ungerichtete positive Kanten | 34 / 561 |
| Mittleres Kantengewicht | 0,6410037880529563 |
| Kleinste / größte gewichtete Knotensumme | 0,8286366711648625 / 25,086797192035903 |
| Experimentelle Skalierung `g=1/max(strength)` | 0,03986160498469138 |
| Zweiter Eigenwert von `gL` | 0,03403007351083512 |
| Größter Eigenwert von `gL` | 1,038685843274879 |
| `kappa` vor Impedanzanpassung begrenzt | 187 Kanten |
| Endgewicht `C_ij=1` | 9 Kanten |
| Größte Differenz Nachbau / ausgewählte Quellmethoden | 2,22·10⁻¹⁶ |
| Phasendifferenz nach 200 Schritten im Kontrollfall | 5,55·10⁻¹⁷ rad |

`seed-morph-compute-001` besitzt die kleinste, `seed-wolfmessing-001` die größte Knotensumme. Die beiden Metaquest-Knoten haben identische für die Kopplung relevante Parameter. Alte Summary-Werte der YAML wie `average_coupling: 0.44` sind keine aktuell berechneten Resultate und dürfen nicht als solche angezeigt werden.

Das Original baut C in YAML-Einfügereihenfolge. Alle Eingangsarrays und Ausgaben werden gemeinsam auf lexikographische ID-Reihenfolge permutiert. Ein Hash ohne zugehörige ID-Liste reicht nicht.

`coupling_targets` wird geladen, aber bei dieser Matrixberechnung nicht verwendet. Die Matrix ist somit kein empirisch gemessener Domänentransfergraph. Sie kodiert eine numerische Ähnlichkeitsvorschrift aus Metadaten. Insbesondere definiert der Code keinen physikalisch begründeten Maßstabswechsel zwischen dimensionsloser Beta-Differenz und `wavelength_cm/10` im Exponenten. Die alten Konstanten bleiben für die Reproduktion erhalten, aber ohne neuen physikalischen Geltungsanspruch.

## 5. Mathematischer Kern und überprüfbare Vorhersagen

### 5.1 Dynamik, Schreiben und Auslesen

Für positive symmetrische C mit Nulldiagonale:

\[
\dot\theta_i=\omega_i+g\sum_j C_{ij}\sin(\theta_j-\theta_i),\qquad
\theta(0)=\phi\mathbf1+aEu.
\]

Es gilt `u~Uniform([-1,1]^4)`, `a=0.35`, `E^T E=I_4`, `1^T E=0`. Vier disjunkte Paare tragen je `+1/sqrt(2),-1/sqrt(2)`. `phi` ist unabhängig und pro Episode gleichverteilt auf `[-pi,pi)`. Zustände werden zirkulär behandelt.

Beobachtung: ein Snapshot `theta+epsilon` mit unabhängigen Knotenfehlern `epsilon_i~N(0,0.03²)`. Sinus und Kosinus der Differenzen zu einem zulässigen Referenzknoten bilden die Merkmale. Der Referenzfehler ist geteilt: Für m nichtreferenzielle Phasendifferenzen lautet die lineare Rauschkovarianz

\[
R=\sigma_{obs}^2(I_m+\mathbf1\mathbf1^T).
\]

Das sind nicht `2m` unabhängige Sensorfehler. Sinus/Kosinus vermeiden Wrap-Sprünge, verdoppeln aber nicht die lokale Zahl der Phasenfreiheitsgrade. Auch daraus folgt noch keine globale Kapazitätsschranke für alle nichtlinearen Auslesefunktionen.

### 5.2 Was man bereits analytisch weiß

Bei `C=0` und ohne Prozessrauschen gilt exakt `theta(t)=wrap(theta(0)+omega*t)`. Die Drift ist episodenunabhängig und kann von einem je Zeitpunkt trainierten Decoder gelernt werden. Lange Haltbarkeit dieser Referenz ist zu erwarten, kein Implementierungsfehler.

Für zwei gleiche Eigenfrequenzen und Kantenstärke k erfüllt die Differenz

\[
\dot\delta=-2k\sin\delta,\qquad
\delta(t)=2\arctan\!\left[\tan\!\left(\frac{\delta_0}{2}\right)e^{-2kt}\right]
\]

auf dem passenden Zweig `|delta0|<pi`. Bei `delta0=.4,k=.7,t=1.3`: `delta=0.0656648863608956`. Der Zustand kontrahiert, bleibt aber bei endlicher Zeit unterscheidbar. Mehr Synchronisation kann weniger gut messbare Inhaltsunterschiede bedeuten.

### 5.3 Linearer Erklärungsadapter

Nahe einem synchronen Zustand mit gleichen Frequenzen gilt für kleine Abweichungen `x_dot=-gLx`, `L=diag(C1)-C`, also

\[
H(t)=D_Oe^{-gLt}aE,
\]

wobei `D_O` ausschließlich die erlaubten Leseknoten und deren Referenz verwendet. Singulärwerte von `R^{-1/2}H` zeigen lokale, rauschgewichtete Sichtbarkeit der vier Inhaltsrichtungen. Für dieses lineare Beobachtungsmodell ist `H^T R^{-1}H` die Fisher-Informationsmatrix. Sie ist weder ein gemessener Bitwert noch eine globale Aussage für die nichtlineare Sinus/Kosinus-Pipeline.

Bei heterogenen Frequenzen kann der synchrone Start auseinanderlaufen. Dann ist `exp(-gLt)` nur ein Vergleichsmodell. Für eine genauere lokale Analyse entlang einer Referenztrajektorie `theta_bar(t)`:

\[
\dot J=A(t)J,\quad J(0)=aE,\quad
A_{ij}=gC_{ij}\cos(\bar\theta_j-\bar\theta_i)\ (i\ne j),\quad
A_{ii}=-\sum_{j\ne i}A_{ij}.
\]

Vergleich mit zentrierten Finite-Differenzen bei mehreren Störamplituden, ohne Differenzen über einen Wrap-Sprung. Ein kleiner Sichtbarkeitswert erklärt eine mögliche Schwierigkeit; er beweist keine globale Nichtidentifizierbarkeit.

### 5.4 Ein harter Kontrollfall für verteilte Auslesbarkeit

Vier Knoten, Einheitskanten `(0,2),(2,3),(3,1)`, `g=1`, `omega=0`. Eingabe `x(0)=u(1,-1,0,0)/sqrt(2)`, Ausgabe `y=x2-x3`. Für die lineare Dynamik ist

\[
y(t)=u\,e^{-2t}\sinh(\sqrt2 t).
\]

Am Anfang ist die Fernausgabe exakt null. Ihr Maximum liegt bei `t=atanh(1/sqrt(2))/sqrt(2)=0.6232252401402304`, mit Verstärkungsfaktor `0.28752355827362913`. Danach nimmt sie wieder ab. Die positive Fernantwort trotz abnehmender Gesamtzustandsnorm ist kein Widerspruch.

Beim vollständigen uniformen Graphen mit gleicher Eigenfrequenz bleibt die entsprechende unbeschriebene Ausgabe dagegen null: Die gleichanteilsfreie Eingabe liegt in einer symmetrischen Mode. Dieser Kontrollfall verhindert den Fehlschluss „jede Kopplung verteilt automatisch nutzbare Information“. Er beweist keinen Lantern-Vorteil bei heterogenen Frequenzen.

## 6. Zwei getrennte Studienprotokolle

### A / `retention_v2`: Spurerhalt als Schätzproblem

Primär: zeitabhängige Rekonstruktionsgüte und Differenz zu ungekoppelt, **ohne vorgegebene Erfolgserwartung**. Das ursprüngliche `G>.05` bei `tau=1` entfällt als bestätigende Hauptthese. Stattdessen: alle vorab festgelegten Zeitpunkte und ein fester gewichteter Kurvenmittelwert. Eine weitere Erhöhung der Schwelle allein wegen Aeons Pilot erfolgt nicht.

### B / `remote_readout_v1`: Information außerhalb der Schreibknoten

Pro Kontext werden 34 IDs zufällig permutiert: erste acht = Schreibknoten in vier Paaren; nächste neun = Leseknoten; letzter dieser neun = Referenz. Die übrigen 17 Knoten vermitteln Dynamik, sind für diesen Decoder unbeobachtet. Schreib- und Lesemengen sind disjunkt. **Auch der Referenzknoten muss unbeschrieben sein.** Sonst könnte der Decoder Zielinformation über die Referenz erhalten, obwohl alle ausgewählten Ausgangsknoten leer sind.

B hat 16 Sinus/Kosinus-Merkmale. A verwendet alle 34 Knoten und dieselbe Referenz, also 66 Merkmale. Jede Aufgabe bekommt eigene Decoder. Eine direkte Aussage „B ist schwerer wegen der Topologie“ wäre ohne Sensorbudget-Vergleich zu stark; der Vergleich A/B ist zunächst beschreibend.

B untersucht verteilte Auslesbarkeit nach einer Impulseingabe, **keinen automatischen assoziativen Abruf**. Ohne Kopplung ist der spätere Beobachtungszustand unabhängig von u. Mit vollständiger Trennung aller Zufallsströme beträgt der populationsoptimale MSE der informationsfreien Vorhersage `1/3`.

### Gemeinsame Defaults

| Parameter | Festgelegter Entwurfswert |
|---|---|
| Registry | 34 Knoten, unveränderte Kopplungsrezeptur |
| Skalierung | `g=1/max(row_sum(C_lantern))`, für alle Referenzen desselben Kontexts gleich |
| Zeitraster | `[0,0.5,1,2,3,5,10]` Modellzeiteinheiten |
| Integration | `dt=.02`, nur nach Konvergenznachweis |
| Frequenzen | je Kontext neuer Vektor `N(0,.1²)`, danach zentriert |
| Kontexte | 20 unabhängige Ziehungen von Frequenzen und Ortspermutation |
| Daten je Kontext | 1000 Training / 250 Auswahl / 1000 Test |
| Inhalt / Impuls | vier unabhängige Uniform-Koordinaten / `.35 rad` |
| Mess-/Prozessrauschen | `.03 rad` / 0 |
| Primärer Decoder | Ridge |
| Sekundärer Decoder | kleiner MLP, nur vor Freeze spezifizierte Zellen |

Der Wechsel zu Ridge als Primärdecoder reduziert Komplexität und macht den Mechanismusvergleich klarer. Ein MLP wird nicht je nach Testgewinner zum Primärmodell befördert.

Ein Kontext umfasst Frequenzen, Orte und alle Lernzufallsquellen. Er ist die inferentielle Einheit. Episoden, Zeitpunkte und vier Ausgabekoordinaten sind keine zusätzlichen unabhängigen Netzreplikate. Die zulässige Population lautet: **zufällig gezogene Frequenz-/Ortskontexte auf dieser einen Registry-Matrix, unter der angegebenen Trainingsprozedur**.

Für den Vergleich mit `strength_surrogate` gehört außerdem dessen unabhängige Ziehung zum Kontext. Die bekannten Entwicklungsseeds 900000–900104 aus Aeons Bericht bleiben ausgeschlossen. Die endgültigen Masterseeds und die vollständige Kontextliste werden vor Forschung erzeugt und im Freeze verankert; keine Auswahl anhand späterer Güte.

## 7. Referenzen und faire Vergleiche

1. `lantern`: originale Matrix mit g.
2. `uncoupled`: Nullmatrix, identische übrige Bedingungen.
3. `uniform_total`: `C_ij = sum(C)/(n(n-1))` für `i!=j`. Gleiches Gesamtgewicht, nicht gleiche Knotensummen.
4. `strength_surrogate`: symmetrische Gewichtsmatrix mit gleicher Nulldiagonale und denselben Knotensummen wie C; Werte bleiben in `[0,1]`.

Für eine implementierbare Stärke-Referenz vier verschiedene Knoten a,b,c,d ziehen und folgende symmetrischen Einträge ändern:

`w_ab+=delta; w_cd+=delta; w_ac-=delta; w_bd-=delta`.

Der zulässige Bereich ist

`lo=max(-w_ab,-w_cd,w_ac-1,w_bd-1)` und
`hi=min(1-w_ab,1-w_cd,w_ac,w_bd)`.

Bei `hi<=lo` unverändert fortfahren und den degenerierten Schritt zählen; sonst delta uniform in `[lo,hi]` ziehen. Entwurf: 20.000 Vorschläge je Kontext, Start jeweils vom Original C, unabhängiger Nullmodellstrom. Alle Matrixinvarianten nachrechnen. Die Vorschlagszahl und etwaige Änderungen werden vor Freeze festgeschrieben. Frobenius-Abstand, Gewichtsverteilung und Spektrum der Surrogate berichten.

**Keine Behauptung eines exakten uniformen Zufallsensembles:** Mischungsdauer und Zielverteilung sind hier nicht bewiesen. Der Name benennt die Konstruktion, nicht mehr. Gewichtshistogramm und einzelne Eigenwerte bleiben im Allgemeinen nicht erhalten. Eine reine Knotenpermutation ist dagegen ein isomorphes Netz und gehört als Invarianztest, nicht als neue Strukturreferenz, in die Suite.

Alle Bedingungen teilen innerhalb eines Kontexts Ziele und Messfehler. Trainings-, Validierungs- und Testpartitionen bleiben unabhängig. Jede Bedingung hat einen eigenen Fit. Für B sind sämtliche Sensor- und Referenzindizes gleich. Alle Bedingungen rechnen mit demselben g; Referenzen nicht separat normalisieren und damit unbemerkt das Vergleichsbudget verändern.

## 8. Ausleser ohne unvollständige Trainingsdefinition

Ridge: Standardisierung nur aus Training; konstante Spalten bekommen Skalierung 1; Interzept unbestraft. Definiere die Zielfunktion explizit als

\[
\frac1N\|XW+\mathbf1b^T-U\|_F^2+\lambda\|W\|_F^2.
\]

Das Lambda-Raster lautet `[1e-4,1e-3,1e-2,1e-1,1,10,100]`. Kleinster Validierungs-MSE gewinnt, bei exakt gleichem Wert die größere Regularisierung. Wenn `sklearn.Ridge` verwendet wird, muss dessen nicht gemittelte Residuenkonvention mit `alpha=N*lambda` berücksichtigt werden. Solver und Bibliotheksversion speichern.

MLP-Entwurf: `d→32 tanh→4 linear`, Adam, Lernrate `1e-3`, Batchgröße 64, höchstens 500 Epochen, drei Initialisierungen, frühes Stoppen mit Patience 30 und absoluter Verbesserungsgrenze `1e-6`. Eigener gespeicherter Validierungssplit; keine versteckte zweite Datenaufteilung. Bestes Checkpoint pro Initialisierung, dann beste Validierungsleistung; Tie-Break kleinste Initialisierungs-ID. Regularisierung und Initialisierungsverfahren müssen im lokalen Entwicklungsnachweis explizit festgelegt werden, bevor dieses optionale Modul einfrierbar ist. Ridge blockiert nicht auf MLP.

Vorhersagen werden für den Hauptverlust auf `[-1,1]` projiziert, Rohwerte ebenfalls gespeichert. Der vorher festgelegte Projektionsschritt darf nach Testeinsicht nicht geändert werden.

Speichere standardisierte Featuredefinition, Reihenfolge, alle Gewichte, Interzept, Skalierung, Hyperparameter, Validierungsentscheidung und Softwareversionen. NPZ ohne Pickle bzw. rein numerische Arrays; striktes JSON ohne NaN/Infinity. Keine ungeprüften Pickle-/Joblib-Dateien als Austauschformat.

## 9. Kennzahlen, Inferenz und Ergebnisregeln

Pro Episode `loss=mean_j((u_hat_j-u_j)^2)`, Primärvergleich `loss_zero=mean_j(u_j²)`.

`S=1-3*mean(loss)` und `G=3*mean(loss_zero-loss)` werden getrennt berichtet. G kann negativ werden. Ein endlicher Testdatensatz mit kleinen Zielwerten kann für die Nullausgabe ein großes positives S haben, während G exakt null ist. Kontrollfall K19 liefert `S=.925,G=0`.

Für jeden Kontext und jede Bedingung bilde einen fest gewichteten Kurvenmittelwert A aus den sieben G-Werten: Trapezregel auf `z=log(1+tau)`, geteilt durch `log(11)`. Dies ist eine **vorab definierte Rasterkennzahl**, keine zertifizierte kontinuierliche Integral- oder Horizontschätzung. Gewichte stehen im JSON und Kontrollfall K21.

### A: Schätzung ohne künstliche Erfolgsprüfung

Berichte Mittelwert/SD und zweiseitiges 95%-t-Intervall über die 20 Kontextwerte für `A_lantern`, `A_uncoupled` und deren gepaarte Differenz. Zeitkurvenintervalle sind punktweise; keine simultane Deckung behaupten. Einzelkontexte vollständig anzeigen. Bei Null-Standardfehler: deskriptiver degenerierter Fall, keine automatisch unendliche Teststatistik. Das t-Intervall ist bei n=20 eine modellabhängige Approximation, kein exaktes Verteilungsfreiheitsversprechen.

### B: zwei vorab festgelegte bestätigende Aussagen

Der konkrete Vorschlag für einen späteren Freeze ist:

- H-B1: `E[A_lantern_remote] > .05`;
- H-B2: `E[A_lantern_remote - A_strength_surrogate_remote] > .05`.

Jeweils einseitiger t-Test auf den gepaarten Kontextgrößen minus .05, anschließend Holm-Korrektur über genau diese zwei p-Werte bei Familienniveau .05. Primär nur Ridge. Der Mindestwert .05 bedeutet eine gewichtete MSE-Verbesserung von `.05/3`, **keine bereits bewiesene praktische oder biologische Relevanz**. Diese Bewertungsentscheidung wird vor Freeze dokumentiert; sie darf nicht anhand der Lantern-Forschungsergebnisse optimiert werden.

Ergänzend rohe Effektintervalle und zwei simultan konservative Bonferroni-95%-Intervalle ausgeben (`t`-Quantil `.9875`, df=19). Die unadjustierten Intervalle nicht als simultan bezeichnen. Die ungekoppelte B-Referenz ist zusätzlich eine starke strukturelle Kontrolle; sie begründet allein keine Lantern-Spezifität.

| Ergebnis | Zulässige Aussage |
|---|---|
| B1 und B2 bestanden, alle Gates grün | Verteilte Auslesbarkeit und Vorteil gegenüber diesem Stärke-Surrogat unter dem Protokoll |
| Nur B1 bestanden | Verteilte Auslesbarkeit gezeigt; kein belegter spezifischer Vorteil gegenüber der Strukturreferenz |
| Keine bestanden | Festgelegte Nachweise nicht erreicht; kein allgemeiner Unmöglichkeitsbeweis |
| Kontrollen oder Integrität fehlerhaft | Technisch nicht interpretierbarer Lauf, unabhängig von p-Werten |

Ein signifikanter Unterschied von null beweist nicht automatisch einen Mindestunterschied .05. Ein nichtsignifikanter Unterschied beweist keine Äquivalenz; dafür wäre ein eigenes TOST-/Äquivalenzprotokoll nötig. Ein Sign-Flip-Test ist ohne Symmetrie-/Randomisierungsannahme nicht automatisch exakt.

20 Kontexte sind eine Ressourcenentscheidung, kein nachgewiesener Powerwert. Entwicklung muss Präzision und numerische Streuung berichten. Falls eine größere Stichprobe erforderlich erscheint, erfolgt die Änderung vor Forschungs-Freeze mit Begründung, nicht bis zum ersten günstigen p-Wert.

## 10. Kontrollen und Numerik-Gates

### Harte, deterministische Gates

- Identische Rohquellen/zulässige LF-Normalisierung; korrekte ID-Permutation; keine doppelten IDs.
- Endliche Arrays, exakte Shapes, keine Bool-Werte als Parameter, keine negativen/ungültigen Kopplungen still abschneiden.
- `theta_threshold` getrennt von `phase_rad`; `evolve_network()` in diesem Labor verboten.
- Matrix und Frequenzen vor/nach jeder Episode unverändert.
- Gleichzeitiges Permutieren aller IDs, Matrizen, Eingaben und Ausgaben ändert keine physikalische Vorhersage.
- Globale Rotation ändert relative Merkmale nicht.
- Reset/kein Impuls erzeugen bei denselben unabhängigen Störvariablen exakt dieselben Zustände für unterschiedliche u.
- In B: keine Schreibkoordinate, kein beschriebener Referenzknoten und kein aus Schreibknoten berechnetes Aggregat im Beobachtungsoperator.
- Kein Ziel, Seed, Episodenzähler, Modellindex oder Inhaltslabel in `predict(features)`.
- Vorhersagesnapshot ist derselbe für eingefrorenen und neu trainierten Vergleichsdecoder.

### Empirische Kontrollen

Bei A muss die Sofortablesung des Ridge-Decoders über die Entwicklungskontexte im Mittel `G0>.90` erreichen. Dies ist ein Pipeline-Gate, keine Forschungsbehauptung. Bei B muss die Sofortablesung zielunabhängig sein; dieselbe .90-Regel wäre dort offensichtlich falsch.

Reset, kein Impuls und permutierte Trainingsziele: vollständige Kontrollkurven berichten. Zusätzliche Alarmprüfung auf unerwartet positives G für Ridge in den zwei Aufgaben bei `tau=1,5`: 12 vorab bestimmte Kontrollzellen. Pro Zelle testzielbezogene Permutationen innerhalb jedes Kontexts, Vorhersagen fest; 9.999 Permutationen, `p=(1+b)/(1+B)`, Holm über 12 bei .01. Ein Alarm sperrt die wissenschaftliche Freigabe bis zur Untersuchung; stark negative G-Werte sind kein Leakalarm. Permutationstests ergänzen die strukturellen Gates und beweisen für sich keine vollständige Leakage-Freiheit.

### Integrationsnachweise

1. Neue gebatchte Euler-Fassung gegen Originalkern: mindestens 100 deterministische Entwicklungszustände, 500 Schritte, verschiedene Matrixgrößen/Skalen einschließlich Nullmatrix; zirkulärer Maximalabstand ≤`1e-12` für die geprüften gut konditionierten Fälle. Keine Behauptung bitgleicher BLAS-Ergebnisse auf jedem Rechner.
2. Getrennte ODE-Genauigkeit: mindestens 32 vorab gespeicherte synthetische Entwicklungsfälle mit Größen bis 34, Zeiten bis 10; `dt,dt/2,dt/4` plus hochgenaue `solve_ivp`-Referenz. Maximaler zirkulärer Abstand zu dieser Referenz ≤`.005 rad`; Decoderkennzahländerung ≤`.01` auf demselben Entwicklungs-Testpanel.
3. Scheitert `.02`, vor Freeze zuerst `.01`, dann `.005` prüfen. Keine stille dt-Änderung im Forschungsbericht. Matrixskala und Frequenzbereich in den Kontrollfällen abdecken.
4. Analytische Zwei-Knoten-Lösung, freie Drift und linearer Ferntransfer als unabhängige Orakel.

Die hier beigefügten 22 Kontrollen erfüllen nur den analytischen Teil. Die umfassenden Integrations- und Mutationsnachweise müssen an Claudes tatsächlicher Implementierung laufen.

## 11. Architektur und Datenverträge

Neuer Bereich `experiments/lantern_reconstruction/`, in eigenem Worktree auf D:. Keine Änderung des alten wissenschaftlichen Modells durch diesen Plan.

| Modul | Vertrag |
|---|---|
| `legacy_probe.py` | Einmaliger separater Worker: Importmanifest, Registry-Lader, C exportieren, Nebeneffekte protokollieren |
| `registry_adapter.py` | Validierte immutable Kopie: IDs, C, Metadaten; keine CollectiveField-Abhängigkeit zur Laufzeit |
| `dynamics.py` | Reine vektorisierte Drift/Euler-Funktion; explizite Arrays, keine globale Zufallsquelle |
| `encoding.py` | u und E schreiben; keine Änderung von C/omega |
| `observation.py` | erlaubte Knoten/Referenz, Messrauschen, feste Feature-Reihenfolge |
| `surrogates.py` | Uniform und gewichtete Vierkanten-Umschichtung mit Invariantenbericht |
| `decoders.py` | Fit mit Train/Val; Predict ausschließlich Merkmale |
| `linear_diagnostics.py` | H(t), weiß gemachte Singulärwerte; später Tangentengleichung |
| `metrics.py` | Verluste, S, G, fester Rastermittelwert, Kontextinferenz |
| `artifacts.py` | Strikte Schemas, Quell-/Arrayhashes, numerischer Modell-Roundtrip |
| `runner.py` / `evaluate.py` | Entwicklung/Smoke/Training/Test als getrennte Phasen |
| `tests/` / `protocol/` | Synthetische Tests, Negativkontrollen, Freeze-Dateien |

Datentypen mindestens `RegistrySnapshot`, `ContextSpec`, `EpisodeBatch`, `ObservationSpec`, `DecoderArtifact`, `EvaluationReport`. Jedes Objekt führt Schema-Version und feste Dimensionen. Decoder-Objekte enthalten keine Zielgeneratoren. Der Evaluator importiert keine Fit-Funktion.

Zufallsströme: `SeedSequence` mit stabilen numerischen Rollenkennungen und explizitem BitGenerator. Streamschlüssel z.B. `(study_id,context_id,split_id,role_id,episode_id)`. Rollen separat für Ortswahl, omega, u, globale Phase, Messrauschen, Surrogat und Decoder. Keine Python-`hash()`-Seeds. Nicht aus bedingungsabhängigem RNG-Verbrauch ableiten. Teilen von Beobachtungsrauschen zwischen Referenzen ist absichtliche Paarung, Teilen zwischen Train/Val/Test ist verboten. Reproduzierbarkeit auch nach Änderung von Batchgröße und Ausführungsreihenfolge prüfen [S8].

`study_id` bezeichnet hier die gemeinsame physische Versuchsserie für A/B. Nur Decoder und Beobachtungsansicht erhalten zusätzlich `task_id`; Zielvektor und Trajektorie bleiben gemeinsam. Messfehler werden pro Episode, Knoten und Auslesezeit adressiert; beide Aufgaben erhalten auf gemeinsam beobachteten Knoten dieselben Fehler. Als feste Rollen-IDs vorschlagen: Orte 10, Frequenzen 20, Ziele 30, globale Phase 40, Messung 50, Surrogat 60, Decoder 70. Der jeweilige Zeitpunkt bzw. Initialisierungsindex kommt als zusätzliche Komponente hinzu. Ein gespeicherter Streamplan mit eindeutigen Schlüsseln ist verbindlicher als das zufällige Aufrufmuster von `spawn()`.

Zum Legacy-Import: Unterprozess mit festem `PYTHONHASHSEED`, `PYTHONDONTWRITEBYTECODE=1`, bewusst gesetzten D:-Cachepfaden und erlaubten Importwurzeln. Ein Audithook protokolliert Zugriffe; unabhängige Generatoren schützen Episoden. Danach Original-C exportieren und Worker beenden. Die Forschungsphase lädt nur das verifizierte Snapshot-Artefakt. Damit wird der globale RNG-Verbrauch des Altimports aus dem Versuchspfad entfernt, ohne die Altmodule umzuschreiben.

## 12. Artefakte, Freezes und Wiederaufnahme

Die Zustandsmaschine lautet `development → smoke_passed → code_protocol_frozen → trained → model_frozen → evaluated → reviewed`. Ein Lauf kann zusätzlich `failed_integrity`, `numerically_invalid`, `interrupted` oder `incomplete` werden. **Keiner dieser Status darf durch einen günstigen Score überschrieben werden.**

Artefakt-DAG: Quellmanifest → Protokoll → Kontextmanifest → Zustands-/Featurepartitionsmanifest → Modelle → Vorhersagen → Evaluation. Testziele bleiben vor der Evaluationsphase außerhalb des Trainerzugriffs. Falls vollständige OS-Trennung nicht eingerichtet ist, wird dies als Verfahrensschutz bezeichnet, nicht als manipulationssichere Geheimhaltung.

Quellhashes: Git-Blob und rohe Worktreebytes getrennt. LF-Normalisierung nur für deklarierte Textquellen, nie willkürlich auf Binärdateien. `NPZ` byteweise hashen für das konkrete gespeicherte Artefakt; zusätzlich kanonische Arrayidentität aus Schema, Shape, dtype/Endianness und C-order-Daten bilden. ZIP-Zeitstempel/Kompression können Dateibytes verändern, obwohl Arrays gleich sind. Ein beliebiges neu erzeugtes NPZ muss daher nicht denselben Containerhash haben.

`.gitattributes`: eingefrorene Textprotokolle `text eol=lf`, NPZ `-text`; auscheckbare LF-Bytes auch mit `core.autocrlf=true` prüfen. Hashdatei und Selbsthash nicht zyklisch voneinander abhängig machen. Für erwartete Hashes muss es einen unabhängigen Protokoll-/Reviewanker geben.

Die alte Regel „bei jedem Infrastrukturabbruch zwingend ganz neuer Versuch“ wird operationalisiert: deterministische Wiederaufnahme **derselben** run_id an überprüften Chunk-Grenzen ist zulässig, wenn Protokoll, Daten, RNG-Zuordnung und bereits geschriebene Ergebnisse unverändert bleiben. Atomare Writes, append-only Ereignislog, keine Auswahl günstiger Wiederholungen. Testwiederholung nach Ergebnisinspektion, geänderte Hyperparameter oder andere Seeds benötigen eine neue Studienversion. Abgebrochene/fehlgeschlagene Versuche bleiben sichtbar.

Eine Exklusivsperre gilt pro Studien-Freeze und Phase unabhängig vom Zielordner. Fehlende Zellen, falsche Samplezahl, veränderte Modelle, doppelte Kontext-IDs und NaN führen zu Gate-Fehlern. Technisch vollständig, wissenschaftlich interpretierbar und Hypothese bestätigt sind drei getrennte Felder.

## 13. Ressourcen und CI

Alle Arbeitsumgebungen, Temp-/Cachedateien und Artefakte auf D: gemäß bestehender Arbeitsweise. Die Implementierung nutzt vorhandene NumPy/SciPy/PyYAML/scikit-learn-Abhängigkeiten; kein neuer Frameworkzwang. CPU genügt für den geplanten Umfang, vorbehaltlich Benchmark.

Trajektorien je Kontext, Split und Kopplung nur einmal berechnen und an sieben Zeitpunkten abgreifen. A/B und Decoder teilen dieselben erlaubten Zustände; B erhält nur seinen eigenen Beobachtungsoperator. Kein erneuter Integrationslauf pro Decoder. Batched Schrittfunktion muss die Differenz `theta_j-theta_i` verwenden; eine vertauschte Achse kehrt Kopplung um.

Geplante Vollkonfiguration Ridge: 20 Kontexte × 4 Kopplungen × 2 Aufgaben × 7 Zeiten = **1120 Fits**, einschließlich redundanter t=0-Zellen, die kontrolliert wiederverwendet werden können. Bei jeweils 2250 Episoden und 500 Schritten sind es ohne Wiederverwendung äquivalente **90 Millionen Episoden-Schritte**; reale Laufzeit hängt stark von der Batchimplementierung ab. Keine Zusage „zwei Stunden“ ohne lokale Messung.

Benchmark höchstens fünf Minuten je Messlauf; getrennt Zeiten für Dynamik, Ridge, optional MLP, Persistenz und Evaluation messen. Peak-RAM und echte Artefaktmenge erfassen. Entwurfsbudget: zwei Stunden für Produktion/Training und 30 Minuten Evaluation, RAM/Artefakte je unter 1 GiB. Nur technisch erzwungene Limits so benennen. Bei Überschreitung vor Freeze zunächst MLP und zusätzliche Sensitivitäten streichen; verbleibt Überlast, explizite Protokollrevision statt stiller Ergebnislücken.

Keine 3D-Differenztensoren für sämtliche Episoden und Zeiten zugleich halten; kleine Batches. Blockdauer begrenzen, monotone und UTC-Zeit protokollieren, Schlafunterbrechungen erkennen. D:-Notebook mit Netzteil und prozessgebundener Schlafverhinderung wie in der vorhandenen Arbeitsweise, ohne dauerhafte Systemänderung.

Neue Tests explizit in CI aufrufen: Das gelesene Root-Pytest sammelt standardmäßig nur `tests`, nicht `experiments/.../tests`. Getrennte Jobs für Kernkontrollen, Legacy-Adapter/Import und Smoke. Keine vollständige Forschungsserie bei jedem Push. Unterstützte Projekt-Python-Version plus eine weitere tatsächlich unterstützte Version; Versionsabhängigkeiten dokumentieren.

## 14. Konkrete Roadmap mit Abnahmen

Die Kennungen LR0–LR9 sind Arbeitspakete; A/B sind Studienprotokolle. So kollidieren sie nicht mit Mandala-M- oder SCF-Seriennummern.

| Paket | Inhalt und Ergebnis | Abnahme / Abhängigkeit |
|---|---|---|
| **LR0 – Lokaler Bestand** | Worktree, lokale Regeln, Hashvergleich der elf Quellen, Inventar unversionierter Dateien; ursprüngliche Pläne unverändert referenzieren | Keine fremden Änderungen überschrieben; `local_source_audit.json`; Ausgangsstand und Abweichungen erklärt |
| **LR1 – Snapshot und Import** | Isolierter Legacy-Worker, kanonische Matrix, vollständiges Importmanifest, Clippingstatistik | Loader gegen unabhängige Formel; IDs/Shapes/RNG- und Zugriffsprotokoll; kein behaupteter Sandboxschutz ohne Nachweis; nach LR0 |
| **LR2 – Numerischer Kern** | Gebatchte rauschfreie Dynamik, lineares H(t), Orakel | Originaläquivalenz, Zwei-Knoten-Lösung, Zeitreskalierung, Konvergenz bis 10; nach LR1 |
| **LR3 – Aufgaben und Referenzen** | Getrennte A/B-Beobachtungen, Streams, Uniform und Stärke-Surrogat | Referenzknoten-Leak negativ getestet; Reset/Nullimpuls; Surrogatinvarianten; nach LR2 |
| **LR4 – Ridge und Evaluation** | Streng getrennter Fit/Predict, S/G/A, Kontextintervalle, H-B1/B2 und Holm | Analytische Scores, kein Episoden-Pseudoreplikat, Artefakt-Roundtrip; nach LR3 |
| **LR5 – Laufverwaltung und CI** | Schemas, DAG, deterministisches Resume, Budgetmessung, lokale CI-Integration | Unterbrechungs-/Manipulationsmutanten erkannt; Full-import- und Smokejobs explizit; nach LR4 |
| **LR6 – Entwicklungsabnahme / Freeze-Kandidat** | Synthesepanel, optional MLP, Leistungs-/Kostenbericht, vollständig entschiedene Protokollwerte | Offene Blocker null; unabhängiger Code-/Protokollreview; bekannte Aeon-Daten deklariert; nach LR5 |
| **LR7 – Forschungsrunde A/B** | Ein eingefrorenes Training, Modellfreeze, Testauswertung, vollständige Kontexte | Alle Kontrollgates, keine nachträgliche Modellauswahl; Ergebnis darf negativ sein; nur nach LR6-Freigabe |
| **LR8 – Ergebnisbericht und SCF-Adapter** | Fähigkeitenbilanz, Fehlerfälle, erlaubte Aussagen, optional Berichtimport in SCF | Schema-/Scope-Vertrag; keine neue SCF-Dynamik; nach LR7 |
| **LR9 – Folgestudien** | C: Diffusion/Interferenz; später Streaming-Kapazität und D: Teilhinweisabruf | Je neue Modellannahme eigenes Protokoll und Referenz; kein automatisches Weiterlaufen |

LR0–LR6 ergeben bereits ein nützliches, überprüfbares Entwicklungsprodukt. Weder positiver Forschungsbefund noch Veröffentlichung sind Voraussetzung für technischen Abschluss. Eine belastbare Dauer wird nach LR5 angegeben; vorher ist jede Personentagszahl spekulativ.

## 15. Gezielte Fehlereinbauten

Mindestens folgende 18 Mutanten planen, jeweils mit testbarer Ursache und tatsächlich ausgeführtem Nachweis:

1. YAML-Reihenfolge als sortierte Reihenfolge ausgeben.
2. Nur C, nicht E/omega/Beobachtung permutieren.
3. Sinusargument umkehren.
4. `g` doppelt anwenden.
5. `theta_threshold` als Phase überschreiben.
6. Prozessrauschen mit dt statt sqrt(dt), erst im späteren SDE-Modul.
7. Zielabhängige Frequenz ergänzen.
8. Während der Pause erneut schreiben.
9. Geschriebenen Referenzknoten in B zulassen.
10. Ein Quellknotenfeature in B einschleusen.
11. Standardisierung auf Train+Test fitten.
12. Beste Initialisierung nach Test-MSE wählen.
13. Lambda-Konvention ohne Faktor N verwechseln.
14. Negatives G als ungültig verwerfen.
15. Alle Episoden als unabhängige Kontexte zählen.
16. Fehlende Rasterzelle durch Nullwert ersetzen.
17. Freigabe trotz fehlgeschlagener Reset-Kontrolle.
18. Fortsetzen nach Abbruch mit neuem Seed oder verändertem Modell.

Mutant 6 ist vor LR9 ausdrücklich `not_applicable`, nicht „bestanden“. Überlebende Mutanten und äquivalente Mutanten separat ausweisen. Die mitgelieferten 22 analytischen Kontrollen sind keine vorweggenommene Mutationserfolgsquote.

## 16. Sinnvolle spätere Erweiterungen

**C1: korrektes Prozessrauschen.** Eigener Adapter `theta_next=wrap(theta+dt*f(theta)+sigma_process*sqrt(dt)*xi)`. Für die Altvorschrift wächst die Varianz bei Horizont T nur wie `sigma²*T*dt`; für Brownsche Diffusion wie `sigma²*T`. Bei Konvergenzversuchen gemeinsame Brownsche Pfade verwenden: grobe Inkremente als Summe der feinen. Stark- und schwachfehlerbezogene Tests unterscheiden [S6]. Den Legacy-Kern nicht still „reparieren“ und anschließend alte/new Ergebnisse vermischen.

**C2: Ablenkung, Leseknotenverlust und frequenzbezogener Drift.** Eingriff zeitlich und budgetmäßig definieren, gleiche Eingriffe auf alle Referenzen. Erholung und Inhaltstreue getrennt messen; Rückkehr zu Synchronität kann zugleich Verlust des Inhalts sein.

**C3: Streaming statt einzelner Impuls.** Erst hier klassische Verzögerungsaufgaben und Information Processing Capacity einsetzen: neuer Eingabestrom, definierter Washout, mehrere vergangene Eingaben, lineare und orthogonale nichtlineare Zielfunktionen. Jaeger/White/Dambre liefern passende Grundlagen [S1–S3]. Ein hoher L1-Score ist noch keine solche Kapazitätsmessung. Schranken aus diesen Arbeiten nur unter deren Voraussetzungen und passend zur tatsächlich verwendeten Featurebasis übernehmen.

**D: echtes Musterabrufen.** Lernbare Zustands-/Gewichtsspeicherung von einer späteren Cue-Phase trennen. Zunächst kleine Hopfield- oder Conceptor-Referenz mit bekannter Aufgabe; danach ein eigener Lantern-Lernmechanismus, falls begründet [S4–S5]. Positive, feststehende Kuramoto-Kopplungen speichern nicht von selbst eine Bibliothek beliebiger Muster. Muster-ID, Cue-Anteil, Neuheitsprüfung, Interferenz und Fehlerkorrektur benötigen eigene Metriken. Durch Lerngewichte gespeicherte Information darf nicht als reine Zustandsspur bezeichnet werden.

Nicht jetzt: LLM-Agentenschicht, kosmetisches Dashboard, Hardware-/EM-Nachweis, „Bewusstseinsscore“, neue universelle Konstante oder ungeprüfte Übertragung auf biologische Organoide. Eine einfache Ansicht gespeicherter Ergebnisse ist nach LR8 sinnvoll; sie ersetzt keine kontrollierte Auswertung.

## 17. Anschluss an SCF

Feldtheorie bleibt Eigentümer von Registry und Dynamik. Ein optionaler SCF-Adapter liest **nur Berichte und Protokollverträge**, führt das Altmodell nicht aus und verlangt keine Laufzeitabhängigkeit von Feldtheorie auf SCF.

| SCF-Anschluss | Präziser Inhalt |
|---|---|
| Beobachtungsfasern | Welche u sind unter dem gewählten Beobachtungsoperator unterscheidbar? Lokale Rank-Diagnose nicht mit globalem Beweis verwechseln |
| Scope-/Vertragsprüfung | Frequenzbereich, Amplitude, Zeitfenster, Sensorzugang, Messmodell und Referenz explizit |
| Epistemisches Audit | Quelle / Herleitung / Kontrollrechnung / Pilot / eingefrorene Evaluation getrennt |
| Operatorvergleich | Linearisiertes H(t) gegen nichtlineare Simulation mit gemessenem Geltungsbereich |
| Entscheidungsebene | Bei welchen Sensor- und Störbedingungen reicht die Rekonstruktionsgüte für eine vorher definierte Aufgabe? |

Zuerst lokal die aktuelle SCF-API prüfen; keine Imports anhand alter Erinnerungen erfinden. Generisches JSON-Schema genügt als erste Integrationsstufe. Keine mathematische Identität von Lantern-, SCF- und Gehirnmodellen behaupten.

## 18. Quellenregister und Lesestatus

Quellen online geprüft am 7. Oktober 2026. Eigene Herleitungen in §5 sind als solche ausgewiesen; sie werden nicht durch bloße Literaturähnlichkeit zu Literaturresultaten erklärt. Volltexte werden nicht mit dem Übergabepaket weiterverteilt.

| ID | Primärquelle | Geprüfter Zugang und konkrete Verwendung |
|---|---|---|
| S1 | Jaeger, *Short term memory in echo state networks*, GMD Report 152, 2001; [Autorenverzeichnis](https://www.ai.rug.nl/minds/pubs/), [PDF](https://www.ai.rug.nl/minds/uploads/STMEchoStatesTechRep.pdf) | Autoreneintrag und PDF vorhanden; PDF-Textextraktion gestört. Hier historische Einordnung, kein ungeprüftes Detailtheorem |
| S2 | White, Lee, Sompolinsky, *Short-Term Memory in Orthogonal Neural Networks*, PRL 92, 148102 (2004), [DOI](https://doi.org/10.1103/PhysRevLett.92.148102), [Preprint](https://arxiv.org/abs/cond-mat/0402452) | Abstract und HTML-Modellpassage gelesen; zeitliche Rekonstruktion als etablierte Aufgabenklasse. HTML-Neudarstellung enthält irreführendes 2026-Datum; bibliographisch 2004 verwenden |
| S3 | Dambre et al., *Information Processing Capacity of Dynamical Systems*, Scientific Reports 2, 514 (2012), [DOI](https://doi.org/10.1038/srep00514), [Autoreninstitution und Volltext](https://biblio.ugent.be/publication/2972574) | Abstract/Metadaten und zugängliches Verlags-PDF über UGent; Konzept und Voraussetzungen späterer Kapazitätsmessung, keine Übertragung aller Theoreme auf L1 |
| S4 | Hopfield, *Neural networks and physical systems with emergent collective computational abilities*, PNAS 79, 2554–2558 (1982), [DOI](https://doi.org/10.1073/pnas.79.8.2554), [Caltech](https://authors.library.caltech.edu/records/w41x7-8bn13) | Primärabstract und Metadaten; Abgrenzung inhaltsadressierten Abrufs von Zustandsrekonstruktion |
| S5 | Jaeger, *Using Conceptors to Manage Neural Long-Term Memories for Temporal Patterns*, JMLR 18(13), 1–43 (2017), [Artikel](https://jmlr.org/papers/v18/15-449.html) | Primärabstract; Kandidat für spätere lernbare zeitliche Muster, keine fertige Lantern-Integration |
| S6 | Higham, *An Algorithmic Introduction to Numerical Simulation of Stochastic Differential Equations*, SIAM Review 43, 525–546 (2001), [DOI](https://doi.org/10.1137/S0036144500378302) | Volltextabschnitt 4 / Euler–Maruyama und Hinweise zu starker/schwacher Konvergenz geprüft |
| S7 | Python, [sys.addaudithook](https://docs.python.org/3/library/sys.html#sys.addaudithook) | Offizielle ausdrückliche Abgrenzung von Audithooks gegen eine Sandbox |
| S8 | NumPy, [Parallel random number generation](https://numpy.org/doc/stable/reference/random/parallel.html) | Offizielle SeedSequence-/Stromtrennung; installierte Version lokal pinnen |
| S9 | Rodrigues et al., *The Kuramoto model in complex networks*, Physics Reports 610, 1–98 (2016), [DOI](https://doi.org/10.1016/j.physrep.2015.10.008), [Preprint](https://arxiv.org/abs/1511.07139) | Primärautoren-Review, Abstract/Metadaten; Einordnung der bestehenden Dynamik, kein Beleg für EM-/Bewusstseinsinterpretation |

## 19. Direktauftrag für Claude-Code

1. Diesen Plan zusammen mit dem separaten fachlichen Review lesen. Die sechs Ursprungsdateien als historische Grundlage erhalten.
2. Lokal LR0 durchführen. Eigene unversionierte Arbeiten und Mandala-Abschlüsse sichern, ohne sie automatisch zu committen oder zu ändern.
3. LR1–LR5 paketweise implementieren. Jedes Paket bekommt überprüfte Kontrollfälle, gezielte Regression und einen klaren Ergebnisbericht. Repository-Regeln und Johanns vorhandene Commit-/Push-Autorisierung beachten; dieser Plan allein erteilt keine Merge-/Release-Freigabe.
4. Mitgelieferte Orakel unverändert zunächst in der unterstützten Umgebung ausführen, dann Produktionsfunktionen gegen diese Kontrollen prüfen. Die Skripte nicht als neue produktive Dynamikbibliothek importieren.
5. In LR6 ausschließlich Entwicklung/Smoke fertigstellen und einen konkreten Freeze-Kandidaten liefern: Quellen, Hyperparameter, Streamplan, Budget, erwartetes Raster, Kontroll-/Inferenzregeln und offene Befunde.
6. LR7 erst nach technischem Gate und dokumentierter Forschungsfreigabe ausführen. Kein Forschungswert darf zur rückwirkenden Änderung des Versuchs dienen.
7. Bei negativem Ergebnis die Roadmap fachlich abschließen. Erweiterungen werden durch offene Fragen begründet, nicht durch den Wunsch, doch noch einen Gewinner zu erzeugen.

**Erwartetes Ergebnis dieser Reaktivierung:** ein verständliches und reproduzierbares Labor, das sauber beantworten kann, wann Lantern Inhalt bewahrt, wann es ihn verteilt und wann es ihn praktisch unlesbar macht.
