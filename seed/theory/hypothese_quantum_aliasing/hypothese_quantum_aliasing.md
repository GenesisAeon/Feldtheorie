# Quantenaliasing als dimensionaler Schatten

**ID:** theory-quantum-aliasing  
**Status:** Aktiv (v1.0.0)  
**Trilayer:** YAML / JSON / MD  
**UTAC-Kopplung:** Type-6 Implosion (Alias-Schatten als Trigger)

## Kernidee
Superposition erscheint nur, weil die zugrunde liegende Dynamik schneller oszilliert als die Detektor-Abtastrate. \(R\) ist die Frequenz der dimensionalen Schleife (0D→1D→…), \(\Theta\) die Messrate. Überschreitet \(R>\Theta\), entfaltet \(\sigma(\beta(R-\Theta))\) einen Alias-Schatten – ein scheinbarer Zustand, der nur ein Faltungsprodukt ist.

## Drei Thesen
1. **Aliasing statt Superposition:** Beschleunigt man die Abtastung, verschwinden die Schatten; bleibt der Alias bestehen, ist die höhere Dynamik real.
2. **Dimensionale Schleife:** Jede Projektion entlang der 0D→1D→2D→3D→… Sequenz wirft einen zeitversetzten Schatten; Phasenversatz offenbart die Reihenfolge.
3. **Type-6 Konsequenz:** Wenn Alias-Schatten und energetische Schwelle synchronisieren, entsteht der abrupte Implosionssprung, den wir als Type-6 beobachten.

## UTAC-Verknüpfung
- **Type-6:** Alias-Frequenz dient als Frühwarnung für Implosionen; Dekohärenz-Fenster \(\zeta(R)\) steuert, wann Beobachter echte Dynamik vs. Schatten sehen.
- **Simulator-Hooks:** Oversampling- und Alias-Sweeps in `simulator/`-Pipelines; Phasen- und Energie-Spektren loggen, um Nullmodelle zu testen.

## Falsifizierbarkeit & Nullmodelle
- **Nullmodell 1:** Genuine Superposition (Born-Formalismus) → wenn Alias bei Oversampling verschwindet, bleibt dieses Modell.
- **Nullmodell 2:** Thermischer Dekohärenzsprung → wenn Phasenfolge nicht mit Alias-Frequenzen korreliert.
- **Checkpoints:** Oversampling-Experimente, zeitlich variierte Basiswahl, ΔAIC gegen Nullmodelle.
- **Recovery:** Alias fehlt → Archivierung; Alias instabil → \(\zeta(R)\) erhöhen, Messrate anpassen.

## Quellen & Sigillin-Brücken
- seed/V4-Grundlagen/Quantenmechanik als dimensionales Aliasing.pdf  
- seed/V4-Grundlagen/Suche.txt

**Ordnungs-Sigillin:** seed/seed_index.{yaml,json,md}  
**Bedeutungs-Sigillin:** seed/codexfeedback.{yaml,json,md}  
**Schatten-Sigillin:** seed/shadow_sigillin/**
