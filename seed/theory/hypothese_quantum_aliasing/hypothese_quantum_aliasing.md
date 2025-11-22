# Quantenmechanik als dimensionales Aliasing

**ID:** theory-011  
**Status:** Aktiv (v1.0.0)  
**Trilayer:** YAML / JSON / MD  
**UTAC-Kopplung:** Type-6 Implosion (Samplinggrenze / Alias-Schatten)

## Kernidee
Superposition ist ein Wahrnehmungsfehler: Ein schneller Dimensionswechsel \(0D \to 1D \to \dots \to nD\) oszilliert unterhalb der Planck-Zeit. Messungen sampeln zu langsam und sehen nur den Alias-Schatten dieser höherdimensionalen Ordnung. Sobald \(R\) (Oszillationsfrequenz) die Abtastrate \(\Theta\) überholt, steigt \(\sigma(\beta(R-\Theta))\) und die vermeintliche Superposition erscheint.

## Zwei Thesen
1. **Aliasing ≠ Superposition:** Die beobachtete Mehrwertigkeit ist das Alias einer schnelleren Oszillation.  
   *Nullmodell:* Standard-Superpositionsmodell ohne Aliasing.  
   *ΔAIC-Test:* Interferenz-Phasenverschiebung bei erhöhter Abtastrate vs. Standardmodell.  
   *Brücke:* \(\sigma(\beta(R-\Theta))\) steigt, wenn Oszillation die Samplingrate überholt; Schatten statt realer Zustände.
2. **Höherdimensionale Ordnung:** Die Oszillation tastet eine Ordnung in höherer Dimensionalität ab; sichtbar bleiben nur projizierte Schatten.  
   *Nullmodell:* Rein dreidimensionale Dynamik ohne höherdimensionale Projektion.  
   *Discriminator:* Skalenbruch in Spektren/Interferenz, sobald Messgeräte Nyquist erreichen.  
   *Resonanz:* Erfüllt die Messung Nyquist, flacht \(\sigma(\beta(R-\Theta))\) ab und die Schatten verblassen.

## Falsifizierbarkeit & Recovery
- **Checkpoints:** Samplingrate erhöhen und Interferenzmuster prüfen; UTAC-Simulation der dimensionalen Oszillation vs. Standard-Superposition; Spektren auf aliasbedingte Peaks analysieren.  
- **Recovery:** Keine Alias-Signale → Standardmodell beibehalten, Hypothese archivieren; bei Mess-Drift Shadow-Sigillin aktivieren und Sampling neu kalibrieren.

## Quellen & Brücken
- seed/V4-Grundlagen/Quantenmechanik als dimensionales Aliasing.pdf  
- seed/V4-Grundlagen/Suche.txt  

**Ordnungs-Sigillin:** seed/seed_index.{yaml,json,md}  
**Bedeutungs-Sigillin:** seed/codexfeedback.{yaml,json,md}  
**Schatten-Sigillin:** seed/shadow_sigillin/** (Recovery bei Mess-Drift)
