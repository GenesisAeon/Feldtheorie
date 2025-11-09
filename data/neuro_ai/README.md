# Neuro–AI Hybrid Activation Staging

Diese Laterne bereitet den Vergleich hippocampaler EEG-Signaturen mit Transformer-Aktivierungen vor.

- **R:** Stimulus Complexity Index / Prompt Depth
- **Θ:** 0.48 (Manifest-Schätzung)
- **β:** 6.1 Zielsteigung
- **ζ(R):** Replay ↔ Attention-Head Resonanz

## Workflow
1. EEG Datensatz (OpenNeuro) auswählen, Stimulus-Markup extrahieren
2. LLM Prompt-Log Telemetrie alignen (Timestamp-Synchronisation)
3. Gemeinsamen Aktivationsraum konstruieren (CCA/Manifold)
4. Logistic Fits & Nullmodelle (`randomized_prompt_baseline`, `phase_scrambled_surrogate`)
5. Metadata & Datenschutzhinweise dokumentieren

