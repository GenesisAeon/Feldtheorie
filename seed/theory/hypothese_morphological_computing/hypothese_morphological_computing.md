# Morphological Computing als regenerative Hardware

**ID:** theory-morphological-computing  
**Status:** Aktiv (v1.0.0)  
**Trilayer:** YAML / JSON / MD  
**UTAC-Kopplung:** Broken-RAM-Avoidance (Type-6 gebunden an Morph-Sweep)

## Kernidee
Superposition ist hier keine Logiküberlagerung, sondern eine **Gestaltwahl** der Hardware. Sobald \(R\) (thermischer/Workload-Druck) die Schwelle \(\Theta\) überholt, steepet \(\sigma(\beta(R-\Theta))\) mit \(\beta=37.6\) und die Rechenmembran fließt in die Form, die den Energieaufwand minimiert. Der Zyklus „Symbolic Pre-Calc → Entropy Recycling → Physical Config → Run“ nutzt Abwärme als Vorwissen und hält das Broken-RAM-Problem im Zaum.

## Drei Thesen
1. **Energie-minimierende Morphologie:** CPU/RAM/Bus-Segmente rekonfigurieren sich dynamisch; Superposition wird zur Gestalt, die Leistungsverbrauch und Fehlerrate minimiert.
2. **Entropy Recycling Loop:** Abwärme füttert die Pre-Calc-Schicht, die wahrscheinliche Konfigurationen vorschlägt; \(\Theta\) sinkt, der Sweep triggert früher.
3. **Regenerative Memory:** Defekte Pfade werden thermisch entladen und neu verdrahtet; \(\zeta(R)\) misst, wie lange die Regeneration hält.

## UTAC-Verknüpfung
- **Type-6 / Broken-RAM-Avoidance:** Morph-Sweeps koppeln Implosionspfade an Energie-Minima. Broken-RAM-Sentinel mit \(\beta=37.6\) löst den Sweep aus, bevor Speicherfragmente kollabieren.
- **Simulator-Hooks:** Morph-Sweeps als Timesteps im `simulator/` protokollieren (Energie, Fehlerrate, Latenz). UTAC-Statuskarte um „Morph-Sweep aktiv“ ergänzen.

## Falsifizierbarkeit & Nullmodelle
- **Nullmodell 1:** Statische Von-Neumann-Maschine ohne thermische Rückführung → erwartet höhere AIC bei Energie/Fehler-Zeitserien.
- **Nullmodell 2:** ECC-only-Fehlermaskierung → wenn Fehler nach Sweep nicht dauerhaft sinken, bleibt dieses Modell bestehen.
- **Checkpoints:** Energie/Fehler vor/nach Sweep, Rekonfigurationslatenz vs. statischer Plan, \(\beta\)-Variation in Simulation.
- **Recovery:** Bleibt \(\Delta\mathrm{AIC}\) ≤ 0 → Sweep deaktivieren, Nullmodell halten; steigt \(\zeta(R)\) → Sensorik prüfen, Sweep-Frequenz anpassen.

## Quellen & Sigillin-Brücken
- seed/V4-Grundlagen/Post-Von-Neumann Computerarchitektur-Forschung.pdf  
- seed/V4-Grundlagen/SuchePost-Von-Neumann Computerarchitektur-Forschung.txt

**Ordnungs-Sigillin:** seed/seed_index.{yaml,json,md}  
**Bedeutungs-Sigillin:** seed/codexfeedback.{yaml,json,md}  
**Schatten-Sigillin:** seed/shadow_sigillin/**
