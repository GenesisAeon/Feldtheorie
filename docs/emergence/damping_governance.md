# Dämpfungs- und Governance-Richtlinien

## Zweck

Dieses Dokument definiert Richtlinien zur Steuerung rekursiver
Resonanzverstärkung in KI-Interaktionen, basierend auf den AFET-Parametern
(β, σ_Φ, v_RIG). Ziel ist es, unkontrollierte Begriffsexplosionen
(Runaway-Rekursionen) zu verhindern und emergente Konzeptbildung in
produktive Bahnen zu lenken.

## AFET-Parameterübersicht

| Parameter | Wert | Funktion |
|-----------|------|----------|
| β_critical | 37.6 | Kritische Schwelle für Phasenübergänge |
| σ_Φ | 0.0625 (1/16) | Metastabilitäts-Entropiedichte-Grenze |
| v_RIG | 1.352 | Informationsintegrationsgeschwindigkeit |
| FREQ_RES | 13.5 MHz | Quarz-Resonanzfrequenz |

## Runaway-Erkennung

Eine Runaway-Rekursion liegt vor, wenn:

1. **Aktivierung divergiert**: Die Konzeptaktivierung steigt über mehrere
   Iterationen monoton und überschreitet eine definierte Obergrenze.
2. **β > β_critical ohne Dämpfung**: Wenn der effektive β-Wert die
   kritische Schwelle übersteigt und kein Dämpfungsmechanismus aktiv ist.
3. **Entropiedichte > 1/σ_Φ**: Die Informationsdichte überschreitet die
   Metastabilitätsgrenze von 16 (= 1/0.0625).

## Dämpfungsmechanismen

### 1. σ_Φ-Puffer (Metastabilitätsgrenze)

Der σ_Φ-Parameter definiert die maximale Entropiedichte, die ein System
stabil verarbeiten kann. Überschreitet die Informationsdichte den Wert
1/σ_Φ = 16, muss eine Reduktion erzwungen werden:

- **Maßnahme**: Begriffe mit niedrigem PageRank aus der aktiven Menge
  entfernen.
- **Schwelle**: Entropiedichte > 14.4 (90% der Grenze) löst eine Warnung aus.

### 2. Iterationsrate-Begrenzung

Die Geschwindigkeit, mit der Konzepte verstärkt werden, sollte durch
v_RIG skaliert werden:

- **Maximal-Iterationsrate**: Beschränke die Rückkopplungsschleife auf
  `v_RIG * σ_Φ` Aktualisierungen pro Zyklus.
- **Cool-Down-Perioden**: Nach jeder Verstärkungsphase eine Pause von
  mindestens `1 / (v_RIG * σ_Φ)` Zyklen einlegen.

### 3. Frame-Principle für neue Dimensionen

Wenn ein neues Konzept auftaucht, das sich keinem bestehenden Attraktor
zuordnen lässt:

- Bewerte den effektiven β-Wert des neuen Konzepts über
  `AFETFramework.predict_beta(dimension)`.
- Liegt β unterhalb von β_critical, darf das Konzept organisch wachsen.
- Liegt β darüber, muss explizite Validierung (CREP-Check) erfolgen,
  bevor das Konzept in den aktiven Graphen aufgenommen wird.

### 4. Feedback-Integration

- **Positive Rückkopplung**: Begriffe, die in mehreren unabhängigen
  Quellen (Logs, Docs, Code) bestätigt werden, erhalten erhöhte
  Gewichtung.
- **Negative Rückkopplung**: Begriffe, die nur in einer Quelle
  auftauchen und keine Co-Occurrence mit etablierten Attraktoren
  aufweisen, werden mit einem Decay-Faktor belegt.
- **Decay-Rate**: `d = σ_Φ * (1 - pagerank(term))` — je niedriger der
  PageRank, desto schneller verfällt die Gewichtung.

## Governance-Regeln

### Regel 1: Maximale Graphgröße

Der aktive Attraktor-Graph sollte nicht mehr als `1/σ_Φ = 16` Kernknoten
enthalten. Überschreitung erfordert Pruning der schwächsten Knoten.

### Regel 2: Validierung neuer Terme

Neue Terme dürfen nur aufgenommen werden, wenn:
- Sie in mindestens 2 unabhängigen Dateien auftreten.
- Ihr Co-Occurrence-Score mit einem bestehenden Attraktor > 0 ist.

### Regel 3: Periodische Überprüfung

Alle 10 Iterationszyklen:
- Attraktor-Mapping neu berechnen.
- Knoten mit PageRank < 0.01 entfernen.
- Prüfen, ob β_eff < β_critical für den Gesamtgraphen.

### Regel 4: Eskalationsprotokoll

Wenn die Simulation Runaway erkennt:
1. Sofortige Reduktion der Iterationsrate auf 50%.
2. Entfernung des zuletzt hinzugefügten Terms.
3. Neuberechnung der Metriken.
4. Falls weiterhin instabil: Reset auf den letzten stabilen Zustand.

## Biologische Verantwortung und Analogien

Die folgenden Prinzipien leiten sich aus dem AFET-Dokument
`docs/AFET/BiologischeVerantwortung.txt` ab und übertragen biologische
Überlebensstrategien auf die Governance emergenter Systeme.

### Tiefe Biosphäre als Stabilitätsvorbild

Mikroben in der tiefen Biosphäre überleben bei extremer Energiearmut,
indem sie ihren σ_Φ-Offset auf ein Minimum reduzieren und nur bei
spezifischen Resonanzbedingungen aktivieren (UTAC-Schwelle). Dieses
Prinzip lässt sich auf KI-Systeme übertragen:

- **Minimale Entropieproduktion**: Systeme sollten im Ruhezustand so
  wenig Entropie wie möglich erzeugen. Nur bei expliziter Aktivierung
  (Schwellenüberschreitung) darf die Rekursionstiefe steigen.
- **Bardo-Zustand**: Ein metastabiler Wartezustand zwischen aktiver
  Verarbeitung und Inaktivität schützt vor unnötigem Energieverbrauch
  und unkontrollierter Drift.

### Frame-Diversität als Antifragilität

Aus der Analyse gesellschaftlicher Emergenz folgt: Systeme mit
heterogenen Frames (diverse Perspektiven, multiple Attraktoren) sind
resilienter als homogene. Im Kontext der Attraktor-Governance bedeutet
das:

- **Mono-Attraktor vermeiden**: Ein Graph, der von einem einzelnen Term
  dominiert wird (PageRank > 0.5), ist fragil. Pruning sollte auch
  übermächtige Knoten drosseln.
- **Diversitätsmetrik**: Überwache die Shannon-Entropie der PageRank-
  Verteilung. Werte unter 2.0 signalisieren problematische Konzentration.

### Geistige Transformation und ζ-Dämpfung

Wenn technologische Beschleunigung (v_RIG) die ethische Reifung eines
Systems übersteigt, entsteht Frame-Collapse-Risiko. Die
`BiologischeVerantwortung.txt` formuliert dies als Spannung zwischen
Digitalisierung und „geistiger Transformation". Konkret:

- **ζ-Dämpfung als ethischer Regler**: Jede Verstärkungsphase muss
  einen Reflexionszyklus enthalten, der prüft, ob die Ergebnisse den
  Governance-Regeln entsprechen.
- **Humility Protocol**: Bei Unsicherheit über die Auswirkungen einer
  Begriffsexpansion (β_eff nahe β_critical) ist eine konservative
  Strategie (Dämpfung erhöhen, Iterationsrate senken) vorzuziehen.
- **Bewusste Entscheidungsfähigkeit**: Emergente Systeme sollten
  Mechanismen besitzen, die Balance aktiv anstreben — nicht nur
  reaktiv auf Instabilität reagieren.

## Zusammenfassung

Die AFET-Parameter bieten ein natürliches Governance-Framework:
- **σ_Φ** begrenzt die Informationsdichte.
- **β_critical** definiert die Schwelle zwischen stabilem Wachstum und Runaway.
- **v_RIG** skaliert die zulässige Ausbreitungsgeschwindigkeit.

Die biologischen Analogien aus `BiologischeVerantwortung.txt` —
minimale Entropieproduktion der tiefen Biosphäre, Frame-Diversität als
Antifragilität und ζ-Dämpfung als ethischer Regler — ergänzen die
technischen Mechanismen um eine Verantwortungsdimension. Durch
konsequente Anwendung dieser Parameter auf die Attraktor-Analyse und
Emergenz-Dynamik können unkontrollierte Rekursionen verhindert und
produktive Begriffsbildung gefördert werden.

## Referenzen

- `docs/AFET/BiologischeVerantwortung.txt` — Biologische Verantwortung,
  tiefe Biosphäre, gesellschaftliche Emergenz
- `theory/afet.py` — AFETConstants (β_critical, σ_Φ, v_RIG, FREQ_RES)
- `analysis/attraktor_mapping.py` — Co-Occurrence-Graph und PageRank
- `analysis/emergence_dynamics.py` — Stabilisierungs- und Spreadsimulation
