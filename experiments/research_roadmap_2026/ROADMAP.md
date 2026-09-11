# Forschungsroadmap für Unified Mandala und Feldtheorie

Wir entwickeln aus den experimentellen Ideen beider Repositories ein zusammenhängendes Forschungsprogramm. Im Mittelpunkt steht die Frage, wie Grenzen, Beobachtung und veränderliche Kopplungen Information erhalten, Struktur erzeugen und anpassungsfähige Dynamik ermöglichen. Der erste Versuch zum geometrischen Verschnitt ist bereits ausgeführt. Er liefert eine überprüfbare Messgrundlage und einen konkreten nächsten Schritt.

Die Reihenfolge folgt dem Erkenntnisgewinn pro überschaubarem Experiment. Wir beginnen mit kleinen Systemen, deren Zustand vollständig bekannt ist. Danach untersuchen wir dynamische Aufgaben, adaptive Strukturen und zusätzliche Beschreibungsebenen. Quantenaliasing, kosmische Verzweigung und offene Formeln erhalten eigene Entwicklungswege. Der Rahmen umfasst ungefähr drei Monate konzentrierter Arbeit; Fortschritt und Umfang richten sich nach den Ergebnissen der einzelnen Etappen.

Diese Roadmap baut auf dem Forschungsatlas zu unified-mandala und Feldtheorie auf. Die GitHub-Hauptstände wurden am 11. September 2026 erneut abgeglichen: unified-mandala a76052842cbb9e6cb5ba70b36b1350feb35ad70a und Feldtheorie 546c606f6ca15acec152c14f99fa6806a839596a. Die nachfolgenden Quellen verweisen auf diese festgelegten Fassungen. Neue Arbeit liegt im eigenen Branch codex/experimental-roadmap-geometric-waste. Historische Texte, Ergebnisse und Arbeitsstände bleiben erhalten.

## 1 Wissenschaftliche Richtung und Arbeitsweise

Der gemeinsame Kern lässt sich als Kette von Fragen formulieren. Ein System besitzt Mikrozustände und Regeln. Eine Grenze oder ein Beobachter entscheidet, was davon zugänglich ist. Vergröberung verliert Unterschiede. Adaptive Kopplung verändert, welche Unterschiede für eine Aufgabe nützlich sind. Eine neue Beschreibungsebene kann entstehen, wenn sie Vorhersagen mit geringerem Aufwand ermöglicht. Diese Kette verbindet die ursprünglichen Membranideen mit Verschnitt, morphologischem Computing, Lantern und relationalem RIG. [1](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/universum-simulationen/binary_existence_matrix.py) [2](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/membrane_solver.py) [3](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/hypothese_morphological_computing/hypothese_morphological_computing.md) [4](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_rig_literature_convergence_2026-08.md)

Wir führen möglichst ein Hauptmodell und eine Auswertung gleichzeitig zur Entscheidungsreife. Daneben bleibt ein kleiner Theoriepfad offen. Als anfängliche Zeitverteilung schlage ich etwa 60 Prozent für das aktuelle Experiment, 25 Prozent für Formalisierung und Gegenmodelle und 15 Prozent für Dokumentation und verständliche Darstellungen vor. Das ist eine Arbeitsregel, keine gemessene optimale Aufteilung.

**Ein Experiment ist abgeschlossen**, wenn seine Frage, Annahmen, Datenherkunft, Messregel, Gegenmodelle, Ergebnisse und Grenzen zusammen lesbar sind und eine andere Person es nachrechnen kann. Ein negatives Resultat erfüllt diese Bedingung ebenso. Ein grüner Softwaretest belegt eine geprüfte Programmeigenschaft; die wissenschaftliche Tragweite wird gesondert beurteilt.

Neue Erkenntnisse werden an die alten Ideen angehängt. Eine widerlegte Implementierung führt zu einem dokumentierten Gegenbeispiel und gegebenenfalls einer neuen Variante. Die ursprüngliche Formel bleibt mit ihrer Herkunft auffindbar. Dadurch lässt sich später erkennen, ob eine Idee gescheitert ist, eine Messung ungeeignet war oder erst die notwendige Operationalisierung fehlte.

## 2 Das Forschungsportfolio

| Pfad | Forschungsfrage | Einstieg und Reihenfolge |
|---|---|---|
| Geometrischer Verschnitt | Welche Unterschiede gehen bei einer Beobachtung verloren, und wann erklärt Geometrie diesen Verlust? | Erster Hauptpfad; exakte Kalibrierung abgeschlossen |
| Metastabilität und adaptive Grenzen | Wann hilft bewegliche Ordnung bei einer extern gestellten Aufgabe? | Zweiter Hauptpfad; baut auf geprüften Messungen auf |
| Morphologisches Computing | Rechnet eine veränderliche Struktur nach Abzug ihrer Umbaukosten besser? | Ausbau des zweiten Pfads |
| Dimension und Beobachter | Wann benötigt eine Vorhersage mehr Koordinaten oder mehr Gedächtnis? | Dritter Hauptpfad; nach einer verlässlichen dynamischen Basis |
| Quantenaliasing | Kann ein explizites deterministisches Modell relative Phasen und mehrere Messbasen erklären? | Eigenständiger Theoriepfad mit kleinem Minimaltest |
| Stellar Forge und Genesis | Welche Regeln erhalten Vielfalt in Populationen künstlicher Universen? | Spätere kontrollierte Simulation |
| Offene Formeln und relationales RIG | Welche Definitionen ergeben eigenständige, unterscheidbare Vorhersagen? | Fortlaufendes Register mit gezielten Wiederaufnahmen |
| Scope und Forschungsbelege | Können spätere Modelle frühere Fehler unter gleichen Voraussetzungen vermeiden? | Schlanke Verbindung zwischen Versuchen und Auswertungen |

Klima bleibt ein gepflegter bestehender Anwendungsbereich. Für dieses Programm werden vor allem theoretische Modelle und Experimente weiterentwickelt. Oberflächen entstehen dort, wo sie eine Messung, einen Übergang oder einen Gegenvergleich verständlich machen.

## 3 Der bereits ausgeführte Startversuch

### 3.1 Was genau untersucht wurde

GW-EXACT-001 untersucht ein binäres Gitter mit 4 mal 4 Zellen. Es enthält insgesamt 65.536 mögliche Zustände. Zusätzlich betrachten wir die 12.870 Zustände mit genau acht belegten Zellen, um die Dichte konstant zu halten. In beiden Mengen sind alle zugelassenen Zustände gleich wahrscheinlich. Der Versuch enthält keine zeitliche Entwicklung und keine thermodynamische Temperatur.

Die Beobachter sehen entweder den vollständigen Zustand, nur die Gesamtbelegung, die vier Belegungszahlen der 2 mal 2 Blöcke oder diese Blockzahlen zusammen mit der Grenzlänge. Die Grenzlänge zählt ungleiche Nachbarpaare auf einem periodischen Gitter. Sie ist eine geometrische Eigenschaft der Grenzflächen; Löcher und Betti-Zahlen werden hier noch nicht gemessen.

Die Hauptgröße ist H(X gegeben Y), die verbleibende Ungewissheit über den Mikrozustand X nach Kenntnis der Beobachtung Y. Sie wird in Bit pro gesamtem Gitter angegeben. Als zweite Größe berechnen wir den kleinstmöglichen mittleren Anteil falsch rekonstruierter Zellen unter der exakt bekannten Verteilung. Diese beiden Größen beantworten unterschiedliche Fragen. [5](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/entropy_geometric_waste/entropy_geometric_waste.md)

### 3.2 Das erste Ergebnis

| Beobachtung bei genau acht belegten Zellen | Verbleibende Ungewissheit in Bit | Optimaler zellenweiser Fehler |
|---|---|---|
| Vollständiger Zustand | 0,000000 | 0,000000 |
| Nur Gesamtbelegung | 13,651724 | 0,500000 |
| Vier Blockbelegungen | 8,392551 | 0,338462 |
| Blockbelegungen und Grenzlänge | 6,330079 | 0,338462 |
| Blockbelegungen und durchmischte Grenzlabels mit Seed 11 | 6,040198 | 0,318230 |

Die Grenzlänge liefert hier rund 2,062472 zusätzliche Bit über die Blockbelegungen hinaus. Der optimale Fehler für die einzelne Zelle bleibt jedoch unverändert. Für das Ensemble aller Zustände tritt dieselbe Unterscheidung auf: Die verbleibende Entropie sinkt von 7,877444 auf 5,914209 Bit, während der zellenweise Fehler bei 0,312500 bleibt.

Die durchmischten Grenzlabels erhalten dieselbe Häufigkeitsverteilung wie die echte Grenzlänge, sind aber willkürlich auf die Mikrozustände verteilt. Sie ergeben in den drei festgelegten Diagnosevarianten sogar mehr zusätzliche Information. Das ist kein realistischer geometrischer Sensor: Seine Umsetzung würde eine nichtlokale Zuordnung der Zustände voraussetzen. Der Vergleich zeigt, dass zusätzliche Information und die besondere Erklärungskraft einer geometrischen Größe getrennt beurteilt werden müssen.

**Der erreichte Erkenntnisstand ist eine Kalibrierung.** Die Messung funktioniert für die deklarierten endlichen Ensembles. Eine universelle Entropieformel, ein Flächengesetz, topologische Defekte oder Gravitation wurden nicht bestätigt oder widerlegt. Das breite Konzept bleibt offen; der Versuch präzisiert, welche Schlussfolgerungen eine spätere Messung tragen könnte.

### 3.3 Was bereits überprüfbar vorliegt

Protokoll und Programm wurden vor dem ersten Ergebnislauf unter Commit 620a5ce3425f9da741c6444e12ce5b26c029771e festgehalten. Sieben gezielte Tests bestehen, darunter analytisch bekannte Entropiegrenzen, eine unabhängige Binomialformel für Blockbelegungen, vorgegebene Grenzfiguren, Symmetrien und der Schutz bereits existierender Ergebnisordner.

Die Ergebnisdateien enthalten Python- und NumPy-Versionen sowie SHA256-Prüfsummen für Protokoll und Programm. Klassenstatistiken stehen als CSV, Beobachtungen als JSONL bereit. Die vollständige Feldtheorie-Testsuite wurde für diesen eigenständigen Pilotversuch nicht ausgeführt. Die Auswertung stammt bislang vom implementierenden Assistenten. Eine unabhängige zweite KI-Prüfung und die menschliche Interpretation stehen noch aus.

## 4 Geometrischer Verschnitt als Hauptpfad

GW-PRED-002 soll klären, ob geometrische Eigenschaften den Verlust oder die Vorhersagbarkeit auf neuen strukturierten Zustandsmengen besser erklären als Dichte, Auflösung und ein gleich großes Informationsbudget. Dies ist eine neue Hypothese mit neuem Protokoll. Der eben ausgeführte Pilot zählt als Entwicklungswissen und darf dabei nicht als unberührter Testsatz ausgegeben werden.

Zunächst wählen wir einen klaren wissenschaftlichen Zielwert. Eine Möglichkeit ist der Fehler bei der Vorhersage des nächsten Zustands unter festgelegten Zellregeln. Eine andere ist die bedingte Entropie einer exakt bekannten oder zuverlässig geschätzten Verteilung. Wir sollten diese Größen zunächst getrennt untersuchen, damit eine Verbesserung der einen nicht nachträglich als Erfolg bei der anderen erscheint.

Die ersten strukturierten Familien können kompakte Cluster, Streifen, periodische Muster und kontrolliert verrauschte Felder umfassen. Ganze Familien oder Dynamikregime werden für die spätere Prüfung zurückgehalten. Eine zufällige Aufteilung sehr ähnlicher Nachbarbilder wäre zu leicht. Dichte, Gittergröße, Blockgröße, Randbedingung und Rauschpegel müssen entweder fixiert oder ausdrücklich variiert werden.

**Referenzen:** ein Modell mit Dichte und Auflösung; eines mit den beobachtbaren Blockzahlen; ein geometrisches Modell mit Grenzlänge und später Komponenten oder Löchern; mindestens eine zusätzliche Messung mit vergleichbarer Kodierungslänge. Falls ein Merkmal den vollständig verborgenen Mikrozustand benötigt, ist es zunächst eine erklärende Analysegröße. Als nutzbarer Sensor muss es aus den tatsächlich zugänglichen Daten berechenbar sein.

Bei größeren Gittern ist die exakte Zustandsverteilung normalerweise nicht vollständig aufzählbar. Ein empirischer Entropieschätzer kann dann durch zu wenige Wiederholungen stark verzerrt sein. Vor seiner Verwendung werden Lernkurven, bekannte Grenzfälle und Stichprobenabhängigkeit geprüft. Wenn das nicht ausreichend gelingt, wird vor dem Bestätigungslauf eine Vorhersageaufgabe gewählt, deren Fehler direkt auf neuen Daten messbar ist.

**Entscheidung:** Wir führen diesen Pfad weiter, wenn ein vorab definierter praktischer Vorteil auf unberührten Familien erhalten bleibt und nicht allein durch zusätzliche Bits, größere Modelle oder höhere Sensoraufwände erklärbar ist. Verschwindet der Vorteil, behalten wir den Befund und prüfen gezielt, ob das Modell nur für eine enger definierte Strukturklasse interessant ist. Die Mindestverbesserung wird anhand der Kalibrierung und des Verwendungszwecks vor Öffnung des Testsatzes numerisch festgelegt.

## 5 Metastabilität und adaptive Grenzen

Der Kristall-Tod-Gedanke erhält eine Aufgabe außerhalb seiner eigenen bevorzugten Kennzahlen: Kann ein gekoppeltes Netzwerk vergangene Eingaben erinnern und neue Eingaben besser vorhersagen, wenn begrenzte Unordnung erhalten bleibt? Lantern, Solar Driver, Membransolver und Gardener liefern dafür unterschiedliche Ansatzpunkte. Wir wählen zunächst einen einzigen dynamischen Kern. [6](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/README.md) [7](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/models/phase_dynamics.py) [2](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/membrane_solver.py)

MS-001 vergleicht feste Kopplung, zufällige Störungen und kohärenzabhängige Störungen. Eine vierte Variante mit veränderlichen Kanten folgt erst, wenn der Vergleich ohne Umbau verständlich ist. Identische Eingabefolgen und gepaarte Startbedingungen erlauben einen fairen Unterschied zwischen Varianten. Ein lineares Gedächtnismodell und ein einfacher fester Reservoiransatz dienen als zusätzliche Referenzen.

Als erste Aufgabe eignet sich die Rekonstruktion verzögerter Eingaben. Danach folgt die Vorhersage einer kontrollierten nichtlinearen Folge mit einem Wechsel ihrer Erzeugungsregel. Hauptgröße ist der Fehler auf neuen Folgen. Gedächtnistiefe, Erholungszeit und Rechenaufwand bilden getrennte Ergänzungen. Globale und lokale Kohärenz werden beobachtet, entscheiden aber nicht allein über Erfolg.

Der vorhandene Netzwerk-Φ-Wert bleibt zunächst ein gekennzeichneter Proxy. Seine Reaktion auf getrennte Komponenten und Gewichtsskalierung wird dokumentiert. Der Wert 1/16 ist ein vorab benannter Kandidat in einer allgemeinen Parametersuche. Er bekommt keinen Sonderstatus durch eine Zielfunktion, die ihn selbst vorgibt. [8](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/models/emergence_metrics.py) [9](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v11_gardener/ecosystem/multi_agent_system.py)

**Entscheidung:** Eine adaptive Regel ist interessant, wenn sie bei vergleichbarer Modellgröße, Eingabemenge und Kosten eine robustere Leistung erreicht. Erzielen zufällige Störungen denselben Nutzen günstiger, ist dies ein wertvolles Ergebnis für den Mechanismus. Beobachten wir nur einen veränderten Kohärenzverlauf, bleibt die Leistungshypothese unbelegt.

## 6 Morphologisches Computing

MC-001 erweitert den geprüften dynamischen Kern um veränderliche Verbindungen. Die Architektur soll eine Aufgabe leichter lösbar machen, indem sich ihre Struktur anpasst. Das verbindet die adaptive neuronale Membran aus unified-mandala mit den topologischen Eingriffen in Feldtheorie. Die Umbaukosten sind Teil der Frage. [10](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/aeon-neural-membrane/aeonUniversalMembrane.ts) [3](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/hypothese_morphological_computing/hypothese_morphological_computing.md)

Wir vergleichen eine feste Architektur, eine zufällig umgebaute Architektur und eine regelgeleitet adaptive Architektur. Bei jeder Variante werden Anzahl aktiver Verbindungen, Zustandsaktualisierungen, Trainingsschritte, Umbauereignisse und Speicherbedarf gezählt. Aus Operationen werden erst dann Joule, wenn ein belastbares Hardware- und Kostenmodell hinzukommt.

Eine besonders informative Aufgabe ist eine kontrollierte Änderung der Signalstruktur: Zuerst sind lokale Beziehungen nützlich, später länger reichende. Damit kann eine Umbaupolitik einen echten Zielkonflikt lösen. Wir messen, wie viel sie vor und nach dem Wechsel gewinnt und wann ihre kumulierten Einsparungen den Aufwand des Umbaus übersteigen.

**Entscheidung:** Der Pfad geht weiter, wenn sich ein nachvollziehbarer Bereich günstiger Gesamtkosten ergibt, der auch gegen zufälligen Umbau und eine ausreichend große feste Referenz besteht. Andernfalls bleibt die Strukturänderung eine interessante Dynamik ohne belegten Rechenvorteil. Ein anschaulicher Netzverlauf wäre hier eine sinnvolle menschliche Oberfläche, sobald er dieselben Messdaten wie die Auswertung nutzt.

## 7 Dimension Beobachtung und relationales RIG

DIM-001 untersucht, wann eine zusätzliche Beschreibungsebene benötigt wird. Wir beginnen mit einer bekannten Dynamik und einem Beobachter, der nur einen Ausschnitt oder eine langsamere Abtastung erhält. Modelle mit mehr Koordinaten, mehr zeitlicher Erinnerung und flexibleren nichtlinearen Funktionen treten gegeneinander an. [11](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v9_dimensional_emergence.md) [4](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_rig_literature_convergence_2026-08.md)

Die zentrale Größe ist die kleinste Beschreibung, die eine vorher festgelegte Vorhersagequalität auf neuen Daten erreicht. Zusätzliche Parameter und längere Eingabegeschichte kosten Komplexität. Die Darstellung wird zunächst als rekonstruierte Geometrie oder effektive Beschreibung bezeichnet. Eine reale neue Raumdimension wäre eine eigenständige physikalische Behauptung.

Eine Voraussetzung ist ein belastbarer dynamischer Kern. Beim vorhandenen Genesis Cube verändert ein globaler Phasenfaktor allein keine Dichte. Eine spätere Wellenvariante benötigt räumliche Kopplung, definierte Randbedingungen, Einheiten und Prüfungen von Normerhaltung sowie Zeitschritt- und Gitterkonvergenz. Diese Variante entsteht als neuer Experimentpfad, während der historische Cube erhalten bleibt. [12](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/genesis_cube.py) [13](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/pipelines/wavefunction/psi_field.py)

Das relationale RIG kann dazu beitragen, Systemdauer, Vorhersagefähigkeit und Makroinformation auf explizite Rollen abzubilden. Der negative RIG-v0-Versuch bleibt dabei ein eigenständiger Befund. Seine Definitionen werden nicht nachträglich so verändert, dass er erfolgreich erscheint. Neue Größen erhalten neue Protokollnummern; der bereits versiegelte EEG-Holdout bleibt versiegelt. [14](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_RIG_ORIGIN_AND_STATUS.md) [15](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/experiments/rig_v0_scoping/RIG_v0_SCOPING.md) [16](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/experiments/rig_v0_scoping/RESULTS.md)

**Entscheidung:** Interessant ist ein stabiler Wechsel der nötigen Beschreibung, der gegen mehr Gedächtnis und bessere Vergleichsmodelle bestehen bleibt. Ein bloßer Ausschlag eines Dimensionsschätzers genügt dafür nicht. Erst nach diesem Vergleich entscheiden wir, ob der Mechanismus eine weitergehende geometrische Theorie motiviert.

## 8 Quantenaliasing als eigener Theoriepfad

QA-001 beginnt mit einem sehr kleinen Modell aus deterministischer Zustandsentwicklung, Beobachtungsregel und Messausgabe. Die vorhandenen Texte diskutieren bereits Bell und Superdeterminismus. Der offene Kern ist deshalb präziser: Wie entstehen aus den Regeln relative Phasen, Interferenz und konsistente Ergebnisse in mehreren Messbasen? [17](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/hypothese_quantum_aliasing/hypothese_quantum_aliasing.md) [18](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/V4-Grundlagen/Quantenmechanik%20als%20dimensionales%20Aliasing.pdf)

Eine reine zeitliche Mischung klassischer Zustände bildet zunächst Häufigkeiten. Der erste Prüfstein ist ein Zwei-Wege-Versuch mit veränderter relativer Phase. Parameter und Ausleseregel werden an einem festgelegten Teil der Einstellungen bestimmt. Anschließend muss das Modell weitere Einstellungen vorhersagen. Die Zielformel darf nicht unbemerkt als Ausleseregel eingebaut werden.

Wir dokumentieren für jede Variante, welche Annahmen über Lokalität, verborgene Zustände, Messkontext und Unabhängigkeit der Einstellungen gelten. Ein Modell mit Messabhängigkeit benötigt eine explizite gemeinsame Verteilung. Es muss zeigen, was diese Annahme zusätzlich erklärt oder vorhersagt; der Verweis auf Unterabtastung allein ersetzt diesen Schritt nicht.

**Entscheidung:** Liefert die Variante nur eine klassische Mischung, wird genau diese Leistung festgehalten. Liefert sie phasenabhängige Vorhersagen, prüfen wir, ob deren Struktur abgeleitet oder bereits vorgegeben wurde. Ein nächster Ausbau folgt erst auf einen nachvollziehbaren Minimalmechanismus. Die kosmische Deutung kann währenddessen als offener theoretischer Zusammenhang bestehen bleiben.

## 9 Stellar Forge und kosmische Modellpopulationen

SF-001 untersucht Vererbung, Mutation und Vielfalt in Populationen künstlicher Universen. UniverseDNA und MultiverseManager liefern bereits konkrete Bausteine. Der Forschungsgegenstand ist zunächst die Population von Modellen mit erklärten Regeln und Budgets. [19](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/v4_stellar_forge/universe_dna.py) [20](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/v4_stellar_forge/multiverse_manager.py)

Die erste Vergleichsreihe enthält neutrale Verzweigung, feste Selektionsregeln und evolvierbare Mutationsstärken. Jedes Universum erhält dasselbe Budget an simulierten Schritten. Zusätzlich wird die Gesamtpopulation begrenzt, damit eine Linie nicht allein durch mehr Rechenzeit erfolgreicher wirkt. Reproduktionsereignisse, Überleben, Vielfalt und Erholung nach Parameteränderungen werden getrennt gemessen.

Die wichtigste Gegenprobe fragt, ob der gewünschte Zustand bereits durch die gewählte Fitnessfunktion erzwungen wird. Daher werden zusätzliche Erfolgskriterien vor dem Lauf festgelegt, die ausschließlich zur späteren Auswertung dienen und nicht in die Selektion eingehen. Unterschiedliche Reproduktionsregeln und faire Ressourcenbegrenzungen gehören zum Versuch.

**Entscheidung:** Robust entstehende Vielfalt oder eine überprüfbare Beziehung zwischen Vererbungsgenauigkeit und Anpassung wären Ergebnisse über künstliche Evolution. Ein Übergang zur beobachtbaren Kosmologie benötigt danach eine eigenständige Zuordnung von Modellgrößen zu Messdaten. Dieser zusätzliche Schritt wird ausdrücklich geplant, sobald ein enger Kandidat dafür existiert.

## 10 Offene Formeln bewahren und gezielt wieder aufnehmen

Ein Formelregister erhält für jeden Ansatz den Originaltext, Urheberschaft, Symboldefinitionen, Einheiten, Annahmen, Gültigkeitsbereich, vorhandene Gegenbeispiele und einen möglichen nächsten Test. Einträge können offen, operationalisiert, für einen Bereich gestützt, unter einer konkreten Interpretation widerlegt oder vorläufig zurückgestellt sein. Diese Zustände gelten für präzise Aussagen und Varianten.

| Ansatz oder Symbol | Zu klärende Frage | Bedingung für die Wiederaufnahme |
|---|---|---|
| Logistische Steilheit beta | Wie hängt der Wert von Einheit und Skalierung der Eingabe ab? | Gleiche normierte Eingabe oder explizite Skalentransformation |
| Goldener Schnitt und Phi-Potenzen | Werden bevorzugte Werte vorgegeben oder entstehen sie aus anderen Regeln? | Freie Alternativen und Vorhersagen ohne eingebauten Attraktor |
| Netzwerk-Φ | Welche Eigenschaft misst der konkrete Proxy? | Verhalten bei Zerlegung und Skalierung sowie Nutzen für eine externe Aufgabe |
| Zielwert 1/16 | Ist er ein robuster günstiger Bereich oder die eingebaute Sollgröße? | Vorab definierter Vergleich mit benachbarten und frei optimierten Werten |
| v_RIG | Welche messbaren Größen und Einheiten erzeugen eine unterscheidbare Vorhersage? | Operationalisierung ohne Rückschluss aus dem gewünschten Zahlenwert |
| sigma im jeweiligen Modul | Handelt es sich um Streuung, Kohärenzabstand oder eine andere Größe? | Eindeutige Messregel und Herkunft an jedem Ergebnis |
| Entropie als Verschnitt | Welche Verteilung und welcher Beobachter definieren den Verlust? | Kalibrierte Messung und geometrischer Zusatznutzen im passenden Vergleich |

Die vorhandene Herkunftsnotiz zu v_RIG dokumentiert Johanns eigene Gedankenexperimente und ihren spekulativen Status. Die aktuelle relationale Fassung ist der Ausgangspunkt für neue Tests. Der negative RIG-v0-Befund betrifft seine konkrete Proxydefinition; er entscheidet nicht pauschal über sämtliche Konstanten oder mögliche spätere Formulierungen. [14](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_RIG_ORIGIN_AND_STATUS.md) [4](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_rig_literature_convergence_2026-08.md) [16](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/experiments/rig_v0_scoping/RESULTS.md)

Das Register soll auch Änderungen an Bedeutungen sichtbar machen. Bei einer linearen Umskalierung der logistischen Eingabe muss sich beispielsweise die numerische Steilheit entsprechend ändern. Eine vermeintlich universelle Zahl kann sonst nur eine gemeinsame Konvention widerspiegeln. Solche Prüfungen helfen, die produktiven Teile einer Formel freizulegen, bevor wir Rechenzeit in große Fits investieren. [21](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/utac_microscopic_abm.py) [22](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/rg_flow_simulator.py) [23](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/theory/afet.py)

Für jede Wiederaufnahme gilt ein kurzer Ablauf: ursprüngliche Aussage rekonstruieren, stärkste noch tragfähige Fassung benennen, ein möglichst einfaches Gegenmodell bauen und eine unterscheidbare Vorhersage festhalten. Erst danach wird entschieden, ob eine größere Simulation angemessen ist.

## 11 Scope als Gedächtnis für Versuche und Gegenbelege

Der Arbeitsablauf folgt der besprochenen Rollenverteilung. Ein Modell implementiert oder führt einen Test aus. Ein anderes Modell erhält das eingefrorene Protokoll, Rohdaten, Codeversion und Ergebnisbehauptungen und rekonstruiert entscheidende Teile unabhängig. Johann entscheidet über die inhaltliche Deutung und Richtung. Scope kann die Verbindungen zwischen Voraussetzungen, Aktionen, Beobachtungen und Gegenbeispielen auffindbar machen.

Ein späteres Modell kann dadurch einen früheren Fehler vermeiden, wenn es den passenden Kontext findet und die Begründung versteht. Ob dies tatsächlich gelingt, wird mit einer eigenen Wiederholungsaufgabe geprüft: dieselbe Fehlerklasse mit verändertem Beispiel, einmal mit dem relevanten Forschungsgedächtnis und einmal ohne. Gemessen werden Fehlerhäufigkeit, richtige Begründung und zusätzliche Kosten. Modellversion, Aufgabenmaterial und Zugriff auf frühere Lösungen müssen festgehalten werden.

Für umfangreiche Spuren brauchen wir drei Zugangsebenen: eine kurze menschliche Ergebnisnotiz, strukturierte Belege mit Pfaden und Prüfsummen und die vollständigen Beobachtungsdaten. Die Kurzfassung verlinkt ihre Belege. Eine zweite KI muss nicht Millionen Ereignisse unterschiedslos lesen; sie benötigt reproduzierbare Abfragen, auffällige Übergänge und die Möglichkeit, die zugrunde liegende Spur zu prüfen.

Der Pilot liefert dafür bereits Protokoll, Ergebnis-JSON, Klassen-CSV, neutrales Beobachtungs-JSONL und ein Review-Paket. Ein tatsächlicher Scope-Adapter ist noch nicht implementiert. Sein Format wird erst nach Prüfung der dann aktuellen Scope-Schnittstelle festgelegt. Die vorhandene Unterscheidung zwischen Beobachtung, Modell, Expertise und Proxy bietet einen geeigneten Ausgangspunkt. [24](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/epistemic/src/evidence.ts)

## 12 Etappen und Entscheidungspunkte

Die folgenden Zeitfenster sind eine Planungsannahme bei regelmäßigen gemeinsamen Arbeitssitzungen. Sie sind keine automatische Ausführung im Hintergrund und keine Zusage, dass alle Theorien innerhalb von zwölf Wochen entschieden werden. Wenn ein Ergebnis neue Voraussetzungen schafft, verschiebt sich die nächste Etappe entsprechend.

| Etappe | Ungefähres Zeitfenster | Ergebnis und Entscheidung |
|---|---|---|
| E0 Messgrundlage | Jetzt | GW-EXACT-001 ausgeführt; unabhängige Nachrechnung als nächster Prüfschritt |
| E1 Verschnitt unter kontrollierten Bedingungen | Wochen 1 bis 3 | GW-PRED-002 mit eingefrorenem Design, neuen Testfamilien und klarer Aussage zum Zusatznutzen |
| E2 Dynamik mit externer Aufgabe | Wochen 3 bis 6 | MS-001 vergleicht feste, zufällige und adaptive Störung; Entscheidung über den Umbaupfad |
| E3 Struktur und Beschreibung | Wochen 6 bis 9 | MC-001 oder DIM-001 als Hauptversuch, ausgewählt anhand des Erkenntnisstands |
| E4 Theorieprüfung | Wochen 9 bis 12 | QA-001 oder SF-001 als enger Minimalversuch; ein ausgewählter Formelansatz wird operationalisiert |
| E5 Synthese | Nach den entscheidenden Läufen | Zusammenhängender Forschungsbericht mit Ergebnissen, Grenzen und verbleibenden Hypothesen |

Nach jeder Etappe wird ein kurzer Entscheidungsvermerk erstellt: Was hat sich geändert? Welche Alternative erklärt den Befund ebenfalls? Was ist der nächste trennende Versuch? Welche offenen Ideen bleiben unverändert offen? Ein Ergebnis wird erst nach dieser Prüfung in eine übergreifende Aussage eingebaut.

Als Produkt dieser ersten Forschungsrunde erwarte ich wenige belastbare Experimente, ein gemeinsames Begriffs- und Formelregister und eine nachvollziehbare Linie von der ursprünglichen Membranidee zu den geprüften Modellen. Ein enger wissenschaftlicher Beitrag kann daraus entstehen, sobald auch eine gezielte Neuheitsrecherche und eine unabhängige Reproduktion vorliegen.

## 13 Ressourcen und technische Umsetzung

Die aktuelle Arbeitsumgebung bietet ungefähr acht CPU-Kerne Rechenbudget und 14 GiB Arbeitsspeicher. Das reicht für den exakten Pilotversuch und kleine dynamische Vergleichsläufe. Diese Angaben sind eine Momentaufnahme der verfügbaren Umgebung. Ein GPU-Zugang, ein externer Cluster oder ein separat abrechenbares Cloudkonto sind bislang nicht nachgewiesen.

Die GitHub-Verbindung funktioniert; der erste Forschungsbranch und der eingefrorene Protokollcommit wurden erfolgreich angelegt. Die hier vorhandenen Quellen sind heruntergeladene Repository-Arbeitskopien. Ein Laufwerk von Johanns PC ist in dieser Sitzung nicht eingebunden. Ein später bestätigter Zugriff auf lokale Repos wird mit deren tatsächlichem Arbeitsstand abgeglichen, bevor Änderungen übertragen werden.

Für E1 beginnen wir mit einem begrenzten Batch: höchstens etwa 30 Minuten Laufzeit, ein bis zwei Rechenprozesse und maximal 2 GiB erwartete Ergebnisdaten. Nach einem gemessenen Kurzlauf rechnen wir den größeren Umfang hoch. Diese Grenzen sind vorgeschlagene Arbeitsbudgets, keine garantierte technische Schranke. Für spätere Läufe werden Abbruch- und Speichergrenzen ausdrücklich in den Runner eingebaut.

Zusätzliche Cloudressourcen werden erst dann eingeplant, wenn ein konkreter Versuch sie benötigt. Der Auftrag enthält dann Anzahl der Läufe, Ressourcenbedarf, maximale Laufzeit, Kostenobergrenze, Speicherort und eine fortsetzbare Ergebnissicherung. Die jetzige Freigabe begründet kein bestimmtes Budget für kostenpflichtige externe Dienste. Für den bereits ausgeführten Pilotversuch wurde kein separater Rechendienst gebucht.

Technisch bleiben neue Experimente zunächst in Feldtheorie unter experiments/. Bestehende Modelle werden über kleine Adapter eingebunden. unified-mandala liefert die historischen Grundlagen und bei Bedarf ausgewählte lauffähige Komponenten. Eine großflächige Zusammenführung der Repositories ist dafür nicht erforderlich.

## 14 Konkrete Arbeitspakete

Die maschinenlesbare Fassung roadmap.json und ihre YAML-Entsprechung enthalten dieselben Arbeitspaket-IDs, Abhängigkeiten und Abschlussbedingungen. Die Zustände beziehen sich auf diese Lieferung. Ein geplantes Paket ist weder bereits gestartet noch automatisch delegiert.

| ID | Arbeitspaket | Voraussetzung | Abschlussbedingung |
|---|---|---|---|
| R00 | Roadmap und Quellen festhalten | Forschungsatlas | Markdown, JSON, YAML und lesbares Dokument vorhanden |
| G00 | Exakte Verschnittkalibrierung | R00 als Arbeitsrichtung | Protokoll vor Lauf fixiert; Ergebnis und sieben Prüfungen vorhanden |
| G01 | Unabhängige Nachrechnung | G00 | Zweite Implementierung prüft Entropie, Rekonstruktion und Aussagen |
| G02 | Strukturierten Verschnittversuch definieren | G00 | Zielwert, Datenfamilien, Sensorzugang und Budgets festgelegt |
| G03 | Bestätigungslauf durchführen | G01 und G02 | Eingefrorene Auswertung auf neuen Familien samt Unsicherheit |
| M00 | Einen dynamischen Kern anbinden | R00 | Zustandsfolgen, Eingaben und Kosten reproduzierbar exportiert |
| M01 | Metastabilität an Aufgabe messen | M00 | Feste, zufällige und adaptive Varianten fair verglichen |
| M02 | Topologie mit Umbaukosten vergleichen | M01 | Gesamtnutzen und Amortisationsbereich bestimmt |
| D00 | Beobachter und Gedächtnisreferenz bauen | M00 | Bekannte Dynamik mit kontrolliert fehlender Information |
| D01 | Beschreibungswechsel untersuchen | D00 | Dimension, Gedächtnis und Modellflexibilität gegeneinander geprüft |
| Q00 | Aliasing-Minimalmodell formulieren | R00 | Zustand, Dynamik, Beobachter und Messannahmen vollständig |
| Q01 | Phasen- und Basiswechsel prüfen | Q00 | Vorhersagen für nicht zur Anpassung genutzte Einstellungen |
| S00 | Universumsverzweigung budgetieren | R00 | Gleiche Zeit je Modell und begrenzte Gesamtpopulation |
| S01 | Vererbung und Vielfalt vergleichen | S00 | Neutralität, Selektion und Mutation nachvollziehbar getrennt |
| F00 | Begriffe und Formeln registrieren | R00 | Herkunft, Einheiten, Status und nächste Prüfung je Kandidat |
| F01 | Einen offenen Ansatz operationalisieren | F00 | Eigenständige Vorhersage mit passendem Gegenmodell |
| K00 | Scope-Anschluss definieren | G00 | Aktuelle Schnittstelle geprüft; Beleg- und Ereignisformat festgelegt |
| K01 | Fehlervermeidung durch Gedächtnis testen | K00 | Neue Aufgaben mit und ohne relevante Spur fair verglichen |
| P00 | Einen Befund unabhängig reproduzieren | Mindestens G03 oder M01 | Reproduktion mit Abweichungsbericht und bestätigtem Geltungsbereich |
| P01 | Engen Forschungsbeitrag ausarbeiten | P00 | Neuheitsprüfung, Methoden, Gegenbefunde und reproduzierbare Belege |

## 15 Der unmittelbar nächste Schritt

Wir beginnen mit G01 und G02. Für G01 liegt ein fertiges Review-Paket im Experimentordner. Das zweite Modell soll die entscheidenden Zahlen eigenständig nachrechnen und besonders die Interpretation der zusätzlichen Grenzinformation prüfen. Die vorhandenen sieben Tests unterstützen diese Prüfung, ersetzen sie aber nicht.

G02 erhält anschließend ein eigenes Protokoll. Meine bevorzugte Fortsetzung ist eine zeitliche Vorhersageaufgabe auf kontrollierten strukturierten Gittern, weil der Pilot bereits gezeigt hat, dass reine Informationsmenge und zellenweise Rekonstruktion auseinanderfallen können. Vor dem ersten Bestätigungslauf legen wir fest, welche Geometrie der Beobachter tatsächlich sehen darf und welches zusätzliche Informationsbudget sie kostet.

Damit steht die Richtung fest, während die theoretischen Möglichkeiten erhalten bleiben: Wir untersuchen zuerst den Verlust durch Beobachtung, danach den Nutzen beweglicher Grenzen und schließlich die Entstehung leistungsfähigerer Beschreibungen. Die exotischen Ansätze bekommen jeweils den kleinsten Versuch, der ihren eigenen offenen Schritt sichtbar machen kann.

## Quellen

1. unified-mandala: [Binary Existence Matrix](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/universum-simulationen/binary_existence_matrix.py).
2. Feldtheorie: [Membransolver mit dynamischen Rand- und Schwellenmodellen](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/membrane_solver.py).
3. Feldtheorie: [Rekursives morphologisches Computing](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/hypothese_morphological_computing/hypothese_morphological_computing.md).
4. Feldtheorie: [Literaturabgleich und relationaler Ansatz, August 2026](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_rig_literature_convergence_2026-08.md).
5. Feldtheorie: [Entropie als geometrischer Verschnitt](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/entropy_geometric_waste/entropy_geometric_waste.md).
6. Feldtheorie: [Lantern-Net: Netzwerkarchitektur und Experimente](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/README.md).
7. Feldtheorie: [Kuramoto-Phasendynamik](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/models/phase_dynamics.py).
8. Feldtheorie: [Emergenzmetriken und Φ-Proxy](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v9_alpha/models/emergence_metrics.py).
9. Feldtheorie: [Gardener: Agentenzustände und Entropiebudget](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/v11_gardener/ecosystem/multi_agent_system.py).
10. unified-mandala: [Adaptive neuronale Membran](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/aeon-neural-membrane/aeonUniversalMembrane.ts).
11. Feldtheorie: [Dimensionale Emergenz: theoretische Ausarbeitung](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v9_dimensional_emergence.md).
12. Feldtheorie: [Genesis Cube und entropische Wellenfunktion](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/genesis_cube.py).
13. Feldtheorie: [Ψ-Field-Pipeline](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/pipelines/wavefunction/psi_field.py).
14. Feldtheorie: [v_RIG: kanonische Herkunfts- und Statusnotiz](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/docs/science/v_RIG_ORIGIN_AND_STATUS.md).
15. Feldtheorie: [RIG v0: eingefrorene Versuchsspezifikation](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/experiments/rig_v0_scoping/RIG_v0_SCOPING.md).
16. Feldtheorie: [RIG v0: dokumentiertes negatives Ergebnis](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/experiments/rig_v0_scoping/RESULTS.md).
17. Feldtheorie: [Quantenaliasing: Hypothesenkern](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/hypothese_quantum_aliasing/hypothese_quantum_aliasing.md).
18. Feldtheorie: [Dimensionales Aliasing: ausführliches Theorie-PDF](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/V4-Grundlagen/Quantenmechanik%20als%20dimensionales%20Aliasing.pdf).
19. Feldtheorie: [UniverseDNA: Variation kosmischer Parameter](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/v4_stellar_forge/universe_dna.py).
20. Feldtheorie: [MultiverseManager: Prozess- und Abstammungssteuerung](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/simulation/v4_stellar_forge/multiverse_manager.py).
21. Feldtheorie: [Mikroskopisches Agentenmodell und Coarse-Graining](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/utac_microscopic_abm.py).
22. Feldtheorie: [Phänomenologische RG-Flüsse](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/models/rg_flow_simulator.py).
23. Feldtheorie: [AFET: Konstanten und Dimensionsvorhersage](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/theory/afet.py).
24. unified-mandala: [Evidenzschema mit Beobachtung, Modell, Expertise und Proxy](https://github.com/GenesisAeon/unified-mandala/blob/a76052842cbb9e6cb5ba70b36b1350feb35ad70a/packages/epistemic/src/evidence.ts).
