# Fachreview: Reaktivierung des Lantern-Netzes

**7. Oktober 2026 · geprüft gegen die sechs übergebenen Unterlagen und elf hashidentische GitHub-Quelldateien**

## Urteil

**GO für ein isoliertes Entwicklungsprojekt. Noch kein GO für einen eingefrorenen Forschungsversuch.** Das ist eine fachliche Reifegradbewertung, keine fehlende Berechtigung für die hier beauftragte Planung. Die Idee ist sinnvoll, wenn „Gedächtnis“ als konkret messbare Rekonstruktionsleistung definiert wird. Der bisherige Plan schützt bereits gut vor vielen Leaks; seine Hauptfrage macht die spezielle Rolle des Netzes allerdings kaum sichtbar.

Empfehlung: ein gemeinsamer technischer Kern, zwei getrennte Aufgaben. A untersucht den Erhalt einer eingeschriebenen Spur. B untersucht Auslesbarkeit an unbeschriebenen Knoten. Erst danach kommen Robustheit, zeitlich überlagerte Inhalte und assoziatives Abrufen.

## Was unabhängig bestätigt wurde

Die ursprünglichen JSON-/YAML-Strukturen sind gleich und der Planhash stimmt. Alle elf angegebenen Git-Blob-SHA-256 stimmen mit den abgerufenen GitHub-Dateien überein. Der lokale Commit `d1c5626...` wurde bewusst nicht gepusht, wie Johann klargestellt hat. Der vollständige lokale Checkout einschließlich späterer Mandala-Arbeiten konnte hier nicht geprüft werden.

Die Aussagen über YAML-Reihenfolge, ungenutzte `coupling_targets`, globale NumPy-Seeds, breite Paketimporte und die Verwechslung von Schwellenwert und Phase bei `evolve_network` sind im gelesenen Quelltext nachvollziehbar. Die Alt-Testdatei importiert freie Kopplungsfunktionen, während die Bridge nur entsprechende Methoden definiert; dieser Schnittstellenwiderspruch ist statisch bestätigt. Ein vollständiger pytest-Lauf wurde hier nicht ausgeführt.

Ein unabhängiger Formelnachbau stimmt mit vier ausgewählten, aus der Originalklasse extrahierten Methoden auf maximal `2.220446049250313e-16` überein. Die Phasenschrittfunktion wurde ebenfalls als ausgewählte Originalmethode, ohne Paketinitialisierungen, ausgeführt. Nach 200 Schritten betrug die Abweichung der vektorisierten Vergleichsformel `5.551115123125783e-17 rad`. Diese Auswahl umgeht gerade die Importnebeneffekte; deshalb bestätigt sie **nicht** deren Beherrschung im späteren Adapter.

22 unabhängige Kontrollgruppen wurden erfolgreich ausgeführt. Sie prüfen u.a. Kodierung, globale Phaseninvarianz, freie Drift, Referenzrauschen, exakte Zwei-Knoten-Dynamik, analytischen Ferntransfer, Zeitreskalierung, Stärke-erhaltende Umschichtung und Unterschiede zwischen S und G. Das ist kein Ersatz für eine Produktionsregression oder einen Forschungsnachweis.

## Priorisierte Befunde

| ID | Gewicht | Befund | Konsequenz im neuen Plan |
|---|---|---|---|
| F01 | Zentral | Rekonstruktion aus direkt beschriebenen Zuständen kann schon ohne Kopplung gelingen | Spurerhalt als Schätzung; verteilte Auslesbarkeit als eigene Aufgabe |
| F02 | Zentral | Neue Seeds/Frequenzen/Orte bei festem C sind keine Netzpopulation | Aussagen ausdrücklich auf Kontextverteilung dieser Registry begrenzen |
| F03 | Neu, wichtig | Vollständiger Graph: binärer Grad überall 33 | Gewichtete Knotensummen erhalten; kein bedeutungsloser binärer Shuffle |
| F04 | Neu, wichtig | 187 begrenzte `kappa`-Zwischenwerte, nur neun Endwerte exakt 1 | Beide Stufen und ihre Wirkung getrennt dokumentieren |
| F05 | Wichtig | Endliche deterministische Kontraktion vernichtet Unterschiede nicht automatisch | Numerik, Messgenauigkeit und Decoderbeschränkung getrennt interpretieren |
| F06 | Neu, wichtig | Ein beschriebener Referenzknoten könnte die B-Aufgabe verraten | Auch Referenz und jedes abgeleitete Feature müssen quellfrei sein |
| F07 | Neu, wichtig | `abs(G)<3 SE` beanstandet auch legitime negative Nullkontrollwerte | Strukturelle Unabhängigkeit, einseitiger positiver Alarm |
| F08 | Wichtig | `sys.addaudithook` allein erzwingt keine sichere Isolation | Auditbeobachtung und OS-Isolation unterschiedlich benennen |
| F09 | Neu, operativ | Ein Hash des NPZ-Containers ist nicht dasselbe wie kanonische Arrayidentität | Zwei Hashbegriffe; gespeichertes Original separat verifizieren |
| F10 | Neu, operativ | Root-pytest sammelt den vorgeschlagenen neuen Ordner nicht automatisch | Expliziter CI-Aufruf des neuen Testpfads |
| F11 | Wichtig | Zwei Stunden Laufzeit sind noch nicht belegt, größeres Raster erhöht Arbeit | Gebatchter Kern, gemeinsame Trajektorien, Benchmark vor Freeze |
| F12 | Präzisierung | Forschungsverbot bei jedem Abbruch ist unnötig grob | Deterministisches Resume derselben eingefrorenen Rechnung erlaubt; Ergebniswahl verboten |

F03/F04 wurden an der tatsächlichen Registry nachgerechnet. F06 ist ein prospektiver Architekturfehler, nicht ein nachgewiesener Bug in existierendem Remote-Code; diese Aufgabe ist noch nicht implementiert. Auch F09/F10 sind Anforderungen an die geplante Umsetzung, keine Behauptung, dass bereits neue Forschungsdaten beschädigt wurden.

## Wie Aeons Review einzuordnen ist

Aeon liefert einen nützlichen explorativen Hinweis: Sein Ridge-Pilot deutet darauf hin, dass die ursprüngliche Schwelle leicht erreichbar und die ungekoppelte Referenz stärker ist. Diese Werte werden im neuen Protokoll als bereits bekannte Entwicklungsinformation deklariert. Ohne seine Skripte und Rohresultate wurden sie hier nicht unabhängig reproduziert.

Die Idee eigener Frequenz-/Ortsziehungen wird übernommen. Ihre Bezeichnung als „Netzpopulation“ wird präzisiert. Die Idee einer gewichtsgematchten Referenz wird übernommen, aber als konkret definierte Gewichtsumverteilung implementiert. Der Vorschlag, den Hauptzeitpunkt so zu wählen, dass Ridge eine gewünschte mittlere Güte erreicht, wird nicht zum Standard: Das verlegt lediglich die Messung und erhöht nicht automatisch ihren Erkenntniswert. Ein fester Kurvenmittelwert vermeidet die nachträgliche Suche nach einem spektakulären Punkt.

Die Begründung „ungekoppelt gut, weil nicht kontrahierend“ ist für die praktische Messaufgabe verständlich. Mathematisch bleibt jedoch auch eine kontrahierende glatte ODE bei endlicher Zeit invertierbar. Deshalb darf ein schlechter Decoder nicht als Beweis für verschwundene Information gelten.

## Was hier wissenschaftlich anschlussfähig ist

Das Vorhaben passt zur etablierten Untersuchung von Rekonstruktion aus transienten dynamischen Zuständen, wie etwa White, Lee und Sompolinsky sie für lineare rekurrente Netze formulieren. Lantern ist ein anderer, nichtlinearer Modellfall; eine Übertragung ihrer Resultate erfordert eigene Voraussetzungen und Nachweise.

Die neue Rolle des Netzes wird über den Schreib-/Beobachtungsoperator greifbar. Im kleinen linearen Kontrollfall kann ein Signal an entfernten Ausgängen zunächst wachsen, während die Gesamtzustandsnorm fällt. So lassen sich Verteilung, Dämpfung und begrenzte Messbarkeit in einem gemeinsamen mathematischen Bild untersuchen, ohne verschiedene Modellgegenstände gleichzusetzen.

Ein wichtiger Gegenfall ist der vollständig uniforme Graph: Unter symmetrischen Anfangsbedingungen und gleichen Frequenzen können unbeschriebene Ausgänge exakt leer bleiben. Kopplung ist daher keine hinreichende Erklärung für nutzbare Übertragung. Die Kombination aus positivem Kontrollfall und starkem Gegenfall ist informativer als eine einzelne neue Erfolgsmetrik.

Für spätere Erweiterungen sind drei Literaturanschlüsse besonders geeignet: Information Processing Capacity für echte Eingabeströme; korrekt diskretisierte stochastische Dynamik für Robustheit; Hopfield-/Conceptor-Referenzen für den späteren Wechsel zu trainierter Musterspeicherung. Diese Funktionen gehören nicht unbemerkt in den ersten Versuch.

## Abschluss- und Freigabekriterien

Claude soll lokal zunächst LR0–LR6 fertigstellen: Bestandsabgleich, Import- und Matrixadapter, geprüfter numerischer Kern, getrennte Aufgaben, Ridge/Evaluator, sichere Artefakte, CI und Budget. Erst dann liegt ein ausführbarer Freeze-Kandidat vor.

Die jetzige Planung nimmt keine Genehmigung von Forschungsresultaten vorweg. Ein technisch korrekter Nullbefund ist ein erfolgreicher Abschluss des Untersuchungsauftrags. Ein positiver Befund darf nur im dokumentierten Scope formuliert werden: synthetische Eingaben, eine Registry-Matrix, festgelegte Frequenz-/Ortsverteilung, Beobachtung und Ausleser.

Kein Merge, Push, Release, Umbau alter Module oder Zugriff auf Johanns Festplatte wurde hier durchgeführt. Die Quelldateien dienen ausschließlich als gelesene bzw. selektiv ausgeführte Referenz. Die neue Roadmap kann direkt als Implementierungsauftrag übergeben werden; die noch erforderlichen lokalen Nachweise stehen als konkrete Gates darin.

Primärquellen, DOI-Links, Lesestatus und sämtliche methodischen Details stehen im Abschnitt „Quellenregister“ des [Implementierungsplans](LANTERN_REAKTIVIERUNG_IMPLEMENTIERUNGSPLAN.md).
