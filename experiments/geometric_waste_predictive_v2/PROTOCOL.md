# Geometrischer Verschnitt und Vorhersage unter begrenzter Beobachtung

**Protokoll:** GW-PRED-002, Version 1.0.0. **Roadmap:** G02. **Stand:** spezifiziert, noch nicht implementiert oder ausgeführt. Dieses Protokoll wird vor der Erzeugung seiner Trainings- und Testdaten versioniert. Die spätere ausführbare Implementierung und ihr Abgleich mit dem Protokoll müssen zusätzlich vor dem Bestätigungslauf festgehalten werden. Dies ist eine interne Vorabfestlegung, keine externe Präregistrierung.

## Forschungsfrage

Verbessert eine begrenzte geometrische Zusatzmessung die Vorhersage des nächsten Zustands eines binären Gitters auf vorher unbenutzten Strukturklassen? Verglichen wird mit anderen Messungen bei gleicher maximaler Übertragungslänge und demselben vorab festgelegten Lernverfahren.

GW-EXACT-001 hat gezeigt, warum die Zielgröße ausdrücklich festgelegt werden muss: Zusätzliche Grenzinformation verringerte dort die bedingte Entropie, während der optimale zellenweise Rekonstruktionsfehler unverändert blieb. GW-PRED-002 misst deshalb einen zeitlichen Vorhersagefehler. Er schätzt keine Entropie und prüft weder ein universelles Entropiegesetz noch thermodynamische oder kosmologische Aussagen.

**Präzise Hypothese:** Der Beobachter GEOMETRY erreicht auf zwei zurückgehaltenen Strukturklassen einen praktisch relevanten niedrigeren mittleren Vorhersagefehler als die auf Validierungsdaten gewählte Vergleichsstrategie. Ein positives Ergebnis gilt für die hier festgelegte Dynamik, Dichte, Quantisierung, Modellklasse und Datenverteilung. Es belegt keine Überlegenheit gegenüber allen denkbaren Sensoren oder Lernalgorithmen.

## System und vorherzusagende Größe

X ist ein binäres Gitter mit 16 mal 16 Zellen und periodischen Randbedingungen. Jeder Anfangszustand enthält genau 128 belegte Zellen. Ein Zeitschritt wird synchron berechnet: Eine Zelle ist danach belegt, wenn sie genau drei belegte Zellen in ihrer achtzelligen Moore-Nachbarschaft hat oder wenn sie bereits belegt ist und genau zwei belegte Nachbarn hat. Das Zentrum zählt nicht als Nachbar. Es wird genau ein Schritt vorhergesagt; nach diesem Schritt ist die Belegung nicht auf 128 beschränkt.

Das Gitter wird in 16 beschriftete Blöcke von 4 mal 4 Zellen zerlegt. Alle Arrays und Blöcke verwenden Zeilenreihenfolge. Die Zielgröße y besteht aus den 16 Belegungsanteilen dieser Blöcke nach dem Schritt. Der Verlust eines Beispiels ist der Mittelwert der 16 absoluten Abweichungen zwischen vorhergesagten und tatsächlichen Belegungsanteilen. Ein Fehler von 0,01 entspricht im Mittel 0,16 Zellen je Block. Er ist kein Fehlermaß für die Rekonstruktion einzelner Mikrozellen.

Familienname, Zufallsseed, Erzeugungsparameter, vollständiger Mikrozustand und zukünftiger Zustand werden dem Vorhersagemodell nicht als zusätzliche Eingaben gegeben. Der Simulator darf sie für Erzeugung und Prüfung verwenden. Die Sensoren lesen ausschließlich den Anfangszustand.

## Beobachter und Übertragungsbudget

Die gemeinsame Basis sind die 16 aktuellen Blockbelegungen n von 0 bis 16. Sie werden als n/16 an das Modell übergeben. Eine einfache feste Kodierung benötigt fünf Bit je Block, insgesamt 80 Bit. Ihre bekannte Summenbedingung wird nicht zur Kompression genutzt. Hinzu kommen vier Messwerte mit jeweils vier möglichen Symbolen, also maximal acht Bit. Alle erlernten Varianten erhalten 20 numerische Eingabekomponenten; nicht vorhandene Zusatzwerte sind null.

| Kennung | Vier zusätzliche Eingaben | Maximal zusätzlich übertragene Bit |
|---|---|---|
| BASE | Vier konstante Nullen | 0; acht Bit dürfen ungenutzt bleiben |
| GEOMETRY | Quantisierte interne Grenzlänge je 8 mal 8 Quadrant | 8 |
| MICRO | Quantisierte Belegung eines zentralen 2 mal 2 Fensters je Quadrant | 8 |
| COARSE | Quantisierter Kontrast der bereits bekannten Blockbelegungen je Quadrant | 8 redundant; keine neue Information über die Basis hinaus |
| SHUFFLED | Gemeinsam permutierte Viererpakete der GEOMETRY-Zusätze | 8; ausschließlich diagnostische Kontrolle |

**GEOMETRY:** In jedem der vier 8 mal 8 Quadranten zählen wir ungleiche horizontale und vertikale Nachbarpaare innerhalb des Quadranten. Es gibt 112 solche Kanten. Quadrantengrenzen und periodische Verbindungen über diese Grenzen zählen für den Sensor nicht mit. Für Grenzlänge L gilt q = floor(4L/113), also q in {0,1,2,3}. Die Eingabe ist q/3. Das ist ein Grenzflächenmerkmal, kein Loch- oder Betti-Schätzer.

**MICRO:** In jedem Quadranten werden die vier Zellen mit lokalen Zeilen- und Spaltenindizes 3 und 4 gelesen, jeweils nullbasiert. Das Fenster schneidet die Grenze der darunterliegenden 4 mal 4 Blöcke. Mit k belegten Zellen gilt q = min(k,3), Eingabe q/3. Die Werte drei und vier werden absichtlich zusammengefasst. Fensterposition und Quantisierung werden nicht anhand von Ergebnissen optimiert.

**COARSE:** Die vier bereits bekannten Belegungsanteile eines Quadranten heißen p00, p01, p10 und p11. D ist der Mittelwert von |p00-p01|, |p10-p11|, |p00-p10| und |p01-p11|. Mit q = min(3,floor(4D)) ist die Eingabe q/3. Ein Vorteil dieser Variante wäre ein Effekt der Merkmalsdarstellung, obwohl keine zusätzliche Mikrozustandsinformation übertragen wird.

**SHUFFLED:** Die vier GEOMETRY-Werte eines Beispiels bleiben als Paket zusammen. Die Pakete werden innerhalb jedes vollständigen Datensplits über Beispiele permutiert, unabhängig zwischen Training, Validierung und Tests. Familien werden dabei nicht getrennt. Die Permutation darf feste Punkte enthalten. Dieser nichtlokale Diagnosesensor gehört nicht zur Auswahl der produktiven Vergleichsstrategie.

Gleiche maximale Kodierungslänge bedeutet weder gleiche Shannon-Entropie noch gleiche bedingte Information. Die tatsächlichen Symbolhäufigkeiten und die bedingte Zusatzinformation sind durch das Acht-Bit-Limit nicht festgelegt. Auch die Messkosten sind verschieden: GEOMETRY benötigt 448 Kantenvergleiche; MICRO liest 16 ausgewählte Zellen; COARSE verwendet schon übertragene Werte. Diese Aufwände werden getrennt protokolliert. Das Experiment behauptet keine Gleichheit des Energiebedarfs.

## Strukturklassen und Erzeugung

Alle Zufallsziehungen sind unabhängig, soweit nicht ausdrücklich gekoppelt. Normalrauschen ist standardnormal und unabhängig pro Zelle. Uniforme reelle Ziehungen verwenden ein links geschlossenes, rechts offenes Intervall. Aus jedem reellen Scorefeld werden die 128 höchsten Werte belegt. Bei exakt gleichen Scores gewinnt der kleinere flache Zellenindex. Dadurch ist die Anfangsdichte immer exakt ein Halb.

1. **iid:** 256 unabhängige uniforme Scores zwischen null und eins.
2. **smooth:** Vier unabhängige Zentren mit je zwei uniformen Koordinaten zwischen null und 16. Eine gemeinsame Breite s wird gleichverteilt aus {1,5; 2,5; 3,5} gewählt. Die vier Amplituden a sind uniform zwischen minus eins und eins. Der Score einer Zelle ist die Summe a mal exp(-d²/(2s²)) über die Zentren plus 0,25 mal Normalrauschen. d ist die kürzeste euklidische Entfernung auf dem 16er-Torus.
3. **axial:** Ein Frequenzindex k aus {1,2,3,4}, ein Richtungsvektor (a,b) aus {(1,0),(0,1)} und eine Phase phi zwischen null und 2pi werden gleichverteilt gezogen. Score = cos(2pi k(ar+bc)/16 + phi) + 0,35 mal Normalrauschen.
4. **diagonal:** Wie axial, aber (a,b) aus {(1,1),(1,-1)}. Diese Familie ist vollständig für den Test zurückgehalten.
5. **tiles:** Eine Kachelbreite w aus {2,4,8} und zwei ganzzahlige Verschiebungen u,v aus {0,...,15} werden gleichverteilt gezogen. Der Score ist (-1) hoch [floor(((r+u) mod 16)/w) + floor(((c+v) mod 16)/w)] plus 0,5 mal Normalrauschen. Diese Familie ist vollständig für den Test zurückgehalten.

Anschließend erhält jede Maske eine zufällige Rotation aus {0,90,180,270 Grad}, eine optionale Spiegelung an der Spaltenachse und eine ganzzahlige Verschiebung in beiden Richtungen. Die Reihenfolge ist Rotation, Spiegelung, Verschiebung. Sensoren und Ziel werden aus dem so transformierten Zustand berechnet. Scoreparameter und Transformationen werden zur Reproduktion aufgezeichnet.

Die Unterscheidung zwischen Trainings- und Testfamilien ist eine festgelegte Form von Verteilungswechsel. Sie stellt keinen universellen Test aller geometrischen Strukturen dar. Die zwei zurückgehaltenen Familien werden nicht zur Auswahl der Modellklasse, Quantisierung oder Erfolgsschwelle genutzt.

## Splits und Wiederholungen

Es gibt 20 vollständige Wiederholungen. Jede erzeugt und trainiert neu. Pro Wiederholung umfasst das Training 128 Beispiele je iid, smooth und axial, insgesamt 384. Die Validierung enthält 64 je dieser drei Familien, insgesamt 192. Ein separater Test innerhalb bekannter Familien enthält ebenfalls 64 je Familie. Der primäre Test enthält 128 diagonal und 128 tiles. Insgesamt sind das 1.024 Beispiele je Wiederholung und 20.480 Beispiele im Bestätigungslauf.

Innerhalb einer Wiederholung werden Duplikate und Äquivalente unter den acht Quadrat-Symmetrien und allen ganzzahligen Torusverschiebungen splitübergreifend ausgeschlossen. Der kanonische Schlüssel ist die lexikographisch kleinste Zeilenfolge der 256 binären Werte unter diesen Transformationen. Verglichen wird die vollständige Folge; ein SHA256-Wert darf zusätzlich als Index dienen. Komplementieren gehört nicht zur Äquivalenzrelation. Wiederholungen besitzen getrennte Duplikatregister.

Die Annahmereihenfolge ist Training, Validierung, Test bekannter Familien, Test neuer Familien; innerhalb der ersten drei Splits iid, smooth, axial und zuletzt diagonal, tiles. Gleichwertige Wiederholungen einer Maske werden verworfen und in derselben Familie neu gezogen. Nach 10.000 erfolglosen Kandidaten für einen einzigen benötigten Platz bricht der Lauf als unvollständig ab. Die Annahmeregel konditioniert spätere Splits auf bereits akzeptierte Muster; Ablehnungsraten werden je Familie und Split berichtet. Eine hohe Ablehnungsrate rechtfertigt keine stille Änderung der Erzeugung.

Die Seeds stehen in protocol.json. Die konkrete RNG-Familie ist NumPy PCG64. Pro Kombination aus Wiederholung, Split und Familie wird ein eigener Stream aus SeedSequence([master_seed, repeat_index, split_id, family_id]) erzeugt; repeat_index ist 0 bis 19. IDs sind explizit in der Konfiguration hinterlegt. SHUFFLED nutzt einen separaten Stream mit shuffle_seed und der Split-ID. Ein Profilinglauf darf ausschließlich die drei Entwicklungsfamilien und den separaten development_seed verwenden.

## Lernverfahren und Referenzen

Die fünf erlernten Beobachter verwenden dieselbe quadratische Ridge-Regression mit 16 Ausgaben. Aus den 20 Eingaben z entstehen ein Interzept, 20 lineare Terme und 210 Produkte z_i z_j mit i kleiner oder gleich j, insgesamt 231 Spalten. Die nichtkonstanten Spalten werden anhand des Trainingsmittels und der Trainingsstandardabweichung mit ddof=0 standardisiert. Eine Nullvarianzspalte wird auf null gesetzt. Der Interzept bleibt eins und wird nicht bestraft.

Je Ausgabe minimieren wir den mittleren quadratischen Trainingsfehler plus lambda mal die Summe der quadrierten Koeffizienten ohne Interzept. Lambda wird aus {0,000001; 0,0001; 0,01; 1} gewählt. Es gewinnt der niedrigste mittlere Validierungs-MAE, bei exakt gleichem Wert das größere Lambda. Validierungs- und Testvorhersagen werden vor Berechnung des Verlusts auf [0,1] begrenzt. Es gibt keinen anschließenden Fit auf Training plus Validierung.

Die Strategien teilen sich Trainingsbeispiele, Zielwerte, Gitter und Hyperparameterbudget. Gleiche maximale Spaltenzahl bedeutet keine gleiche effektive Modellkomplexität: redundante oder konstante Merkmale können Rang und effektive Freiheitsgrade reduzieren. Diese Größen sowie ausgewählte Lambdas werden mit ausgegeben.

Zusätzlich gibt es PERSISTENCE, das ohne Training die aktuellen Blockbelegungsanteile als Vorhersage nutzt. Eine Referenz mit vollständigem Mikrozustand berechnet den festgelegten Schritt direkt; ihr Fehler muss null sein. Sie ist eine Implementierungsprüfung mit größerem Informationszugang und nimmt nicht am Acht-Bit-Vergleich teil.

Pro Wiederholung wird auf der Validierung genau eine Vergleichsstrategie aus BASE, MICRO, COARSE und PERSISTENCE ausgewählt. Bei exakt gleichem Validierungs-MAE entscheidet diese aufgelistete Reihenfolge. GEOMETRY wird primär mit dieser vorab definierten Auswahlprozedur verglichen. Ergebnisse gegen jede einzelne Referenz werden zusätzlich ausgewiesen. Die Auswahl erfolgt niemals anhand von Testwerten.

## Primäre Auswertung und Entscheidung

Zuerst wird der MAE je Beispiel, dann je Testfamilie und schließlich als gleich gewichteter Mittelwert der beiden unbekannten Familien berechnet. Für jede Wiederholung ist Delta der MAE der ausgewählten Vergleichsstrategie minus der MAE von GEOMETRY. Positives Delta bedeutet bessere Geometrievorhersage. Der primäre Schätzer ist der Mittelwert dieser 20 gepaarten Deltas.

Ein zweiseitiges 95-Prozent-Perzentilintervall entsteht durch 10.000 Bootstrap-Ziehungen der 20 vollständigen Wiederholungen mit Zurücklegen. Die Intervallgrenzen sind die Quantile 0,025 und 0,975 der Bootstrap-Mittelwerte, mit linearer Quantilinterpolation. Zellen, Blöcke und Beispiele werden nicht als unabhängige Wiederholungen gezählt. Das Intervall beschreibt die Variation dieser wiederholten Erzeugungs- und Trainingsprozedur; eine formale Powergarantie besteht bei 20 Wiederholungen nicht.

Als praktisch relevanter Vorteil ist vor dem Lauf ein mittleres Delta von mindestens 0,01 festgelegt. Dies ist eine Arbeitsentscheidung entsprechend 0,16 Zellen je Block, kein aus Daten abgeleiteter Naturwert. Eine Unterstützung der engen Hypothese wird nur gemeldet, wenn alle folgenden Bedingungen erfüllt sind:

- Der mittlere Vorteil gegenüber der ausgewählten Vergleichsstrategie beträgt mindestens 0,01.
- Die untere Grenze des primären 95-Prozent-Intervalls liegt über null.
- Der mittlere Vorteil gegenüber BASE beträgt ebenfalls mindestens 0,01.
- In keiner der beiden unbekannten Familien ist GEOMETRY im Mittel um mehr als 0,005 schlechter als die ausgewählte Vergleichsstrategie.

Diese gemeinsam erforderlichen Bedingungen verhindern, dass ein großer Gewinn auf einer Familie eine starke Verschlechterung auf der anderen verdeckt. Die Unsicherheitsintervalle weiterer Referenzvergleiche und der Test bekannter Familien sind deskriptiv; aus ihnen wird keine zweite bestätigende Hauptaussage ausgewählt. Relative Verbesserungen werden ergänzend angegeben; bei Referenzfehler null wird keine relative Quote berechnet.

Liegt die obere Grenze des primären Intervalls unter 0,01, spricht der Versuch gegen einen praktisch relevanten Vorteil in diesem Design. Liegt sie sogar unter null, spricht er für einen Nachteil. Überschneidet das Intervall null oder 0,01, ohne die Entscheidungsregel zu erfüllen, bleibt die entsprechende Aussage unsicher. Bei einem verletzten Familienkriterium wird der Befund als heterogen beschrieben. Eine fehlende Unterstützung ist keine pauschale Widerlegung der ursprünglichen Verschnittidee.

## Vor dem Bestätigungslauf erforderliche Prüfungen

Die Implementierung muss Handbeispiele für leeres Feld, stabile Viererzelle und Blinker sowie periodische Übergänge prüfen. Dichte- und Mengenprüfungen müssen alle Startzustände, Splits und Sensorbereiche erfassen. GEOMETRY besitzt bekannte Grenzfälle L=0 und L=112. Die vier Quantisierungsbereiche müssen vollständig und disjunkt sein. MICRO-Fenster und Quadrantenreihenfolge werden anhand eines beschrifteten Feldes kontrolliert.

Die kanonische Duplikaterkennung muss gedrehte, gespiegelte und verschobene Kopien erkennen. Die Auswertung benötigt synthetische Zahlenbeispiele mit bekannten MAEs, Vergleichsgewinnern und Bootstrap-Grenzfällen. Ein Test muss nachweisen, dass Änderungen an Testzielwerten keinen Einfluss auf Features, Modellparameter, Lambda oder die Auswahl der Vergleichsstrategie haben. Ein vollständiger Zustandszugang muss den Zukunftszustand fehlerfrei liefern.

Vor Erzeugung der Testzustände werden Protokollhash, Codecommit, Umgebung, alle 20 Fits, Lambdas, Skalierungsparameter und Vergleichswahlen unveränderlich festgehalten. Die Modellfamilie und Lambda-Kandidaten stehen bereits in diesem Protokoll; nur die hier erlaubte Auswahl auf Entwicklungsdaten ist zulässig. Eine unabhängige Prüfung von G01 und ein dokumentierter Implementierungsabgleich mit diesem Protokoll gehören zu den Voraussetzungen von G03.

## Ausführung und Ergebnissicherung

Vorgesehen sind höchstens zwei Rechenprozesse, 30 Minuten aktive Laufzeit pro fortsetzbarem Batch, 4 GiB Arbeitsspeicher für den Runner und 2 GiB Ergebnisdaten. Die spätere Implementierung muss diese Grenzen prüfen und bei Erreichen geordnet anhalten. Ein Profilinglauf auf Entwicklungsdaten prüft den Bedarf. Eine Vergrößerung des Budgets wird dokumentiert; wissenschaftliche Einstellungen bleiben bei einer reinen Fortsetzung unverändert.

Jeder neue Lauf benötigt einen neuen Ordner. Es gibt keine Überschreibung und keine Löschung früherer Ergebnisse. Teilstände enthalten Manifest, bisherige Eingaben, RNG-Zustände oder stabile Beispiel-IDs, Fits und Prüfsummen. Ein unvollständiger Lauf wird nicht durch Weglassen ungünstiger Wiederholungen in einen vollständigen umgedeutet. Nach Öffnung eines Testsatzes sind Änderungen am wissenschaftlichen Design explorativ und benötigen für eine neue Bestätigung einen neuen, noch unbenutzten Testplan.

Erforderliche Ausgaben sind ein Manifest mit Protokoll- und Codehash, Umgebungsdatei, Erzeugungsparameter und Splitzugehörigkeiten, Startzustände, Zielwerte, Sensorwerte, Modellparameter, eingefrorene Auswahlentscheidungen, Vorhersagen je Beispiel und Beobachter, aggregierte Verluste, Bootstrap-Auswertung, Ablehnungsraten und Ressourcenverbrauch. Die Ergebnisnotiz benennt ausdrücklich, was ausgeführt, geprüft, unabhängig nachgerechnet oder noch offen ist.

## Herkunft und Verbindung zum Forschungsprogramm

Die konzeptuelle Ausgangsidee stammt aus Johann Benjamin Römers Arbeit unter GenesisAeon. Diese Vorhersageaufgabe ist eine neu vorgeschlagene Operationalisierung. Sie ersetzt die historischen Formulierungen nicht.

- [Ursprüngliche Verschnittidee](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/entropy_geometric_waste/entropy_geometric_waste.md).
- [Erster Kalibrierungsversuch und Grenzen](https://github.com/GenesisAeon/Feldtheorie/blob/ff86d7f35a70a75bfccc74f7c2059348b65dd15f/experiments/geometric_waste_v1/runs/calibration_v1/RESULTS.md).
- [Roadmap und Arbeitspakete](../research_roadmap_2026/ROADMAP.md).
- [Ordnungsindex](../../seed/seed_index.md).

<!-- CUSTOM_RULES -->
Die Versuchsspezifikation liegt als Markdown, JSON und YAML vor. Messdaten entstehen erst mit der späteren Implementierung. Geprüft wird Vorhersage unter fester Beobachtung; es wird kein logistischer Übergang sigma(beta(R-Theta)) und keine Ressourcendynamik (R, Theta, beta, zeta(R)) angepasst. AIC ist hier nicht die gewählte Zielgröße: die Auswertung verwendet neue Testdaten, gepaarte Unterschiede und Konfidenzintervalle. Ein Merge ist kein Ersatz für eine unabhängige Nachrechnung. Der bestehende RIG-EEG-Holdout wird nicht benutzt.
<!-- /CUSTOM_RULES -->
