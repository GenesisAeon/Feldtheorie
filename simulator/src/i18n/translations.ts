/**
 * i18n Translations for Transdisciplinary Field Simulator
 * Supports English (en) and German (de)
 */

export type Language = 'en' | 'de';

export interface Translations {
  // Header
  title: string;
  subtitle: string;
  description: string;

  // Controls
  universalParameters: string;
  criticalThreshold: string;
  steepness: string;
  coupling: string;
  noiseScaling: string;
  controls: string;
  start: string;
  pause: string;
  reset: string;
  poetic: string;
  time: string;
  crossResonance: string;

  // Domain Card
  resonanceActive: string;
  membraneObserved: string;
  triLayerEchoes: string;
  formal: string;
  empirical: string;
  poeticNarrative: string;
  analysisTheta: string;
  analysisBeta: string;
  simulationTheta: string;
  simulationBeta: string;
  deltaAIC: string;
  against: string;
  impedance: string;
  controlParameter: string;
  orderParameter: string;
  dataset: string;
  analysisPath: string;

  // Charts
  reservoirDynamics: string;
  reservoirDescription: string;
  phasePortrait: string;
  phasePortraitDescription: string;
  fieldTypeDistribution: string;
  fieldTypeDistributionDescription: string;
  crepDashboard: string;
  coherence: string;
  resilience: string;
  empathy: string;
  propagation: string;

  // Footer
  footerNote: string;

  // Field Types
  fieldTypes: {
    weakly_coupled: string;
    high_dimensional: string;
    strongly_coupled: string;
    physically_constrained: string;
    meta_adaptive: string;
  };

  // Tabs
  timeSeries: string;
  phaseSpace: string;
  statistics: string;
  language: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    title: 'Transdisciplinary Threshold Field Simulator',
    subtitle: 'Universal Threshold Field · coupled membranes for black holes, bee swarms, and language models.',
    description: 'Controls influence the universal quartet (R, Θ, β, ζ(R)). Null models and data paths are anchored in each card.',

    universalParameters: 'Universal Parameters',
    criticalThreshold: 'Θ (Critical Threshold)',
    steepness: 'β (Steepness)',
    coupling: 'Coupling Γ',
    noiseScaling: 'Noise Scaling',
    controls: 'Controls',
    start: 'Start',
    pause: 'Pause',
    reset: 'Reset',
    poetic: 'Poetic',
    time: 'Time',
    crossResonance: 'Cross-Resonance',

    resonanceActive: '⚡ Resonance Active',
    membraneObserved: '○ Membrane Observed',
    triLayerEchoes: 'Tri-Layer Echoes',
    formal: 'Formal',
    empirical: 'Empirical',
    poeticNarrative: 'Poetic',
    analysisTheta: 'Analysis Θ',
    analysisBeta: 'Analysis β',
    simulationTheta: 'Simulation Θ',
    simulationBeta: 'Simulation β',
    deltaAIC: 'ΔAIC',
    against: 'against',
    impedance: 'Impedance',
    controlParameter: 'Control Parameter',
    orderParameter: 'Order Parameter',
    dataset: 'Dataset',
    analysisPath: 'Analysis Path',

    reservoirDynamics: 'Reservoir Dynamics R(t)',
    reservoirDescription: 'Lines show the trajectory of the order parameter R per domain. The red line marks the current threshold Θ; when curves rise above it, the membrane opens (σ(β(R-Θ)) → 1) and poetic mode signals resonance.',
    phasePortrait: 'Phase Portrait (R, Ψ)',
    phasePortraitDescription: 'Phase space representation showing the relationship between reservoir R and field Ψ. Trajectories reveal attractor dynamics and threshold crossing behavior.',
    fieldTypeDistribution: 'Field Type Distribution',
    fieldTypeDistributionDescription: 'Distribution of active domains across five UTAC field types based on β values. Colors indicate different criticality regimes.',
    crepDashboard: 'CREP Scores',
    coherence: 'Coherence',
    resilience: 'Resilience',
    empathy: 'Empathy',
    propagation: 'Propagation',

    footerNote: 'Simulator version links analysis paths from `analysis/results/*.json` to the cards displayed here. ΔAIC and R² values come directly from falsification routines; adjustments to controls should always be viewed against null models.',

    fieldTypes: {
      weakly_coupled: 'Weakly Coupled',
      high_dimensional: 'High-Dimensional',
      strongly_coupled: 'Strongly Coupled',
      physically_constrained: 'Physically Constrained',
      meta_adaptive: 'Meta-Adaptive'
    },

    timeSeries: 'Time Series',
    phaseSpace: 'Phase Space',
    statistics: 'Statistics',
    language: 'Language'
  },

  de: {
    title: 'Transdisziplinärer Schwellenfeld-Simulator',
    subtitle: 'Universal Threshold Field · gekoppelte Membranen für Schwarze Löcher, Bienenschwärme und Sprachmodelle.',
    description: 'Regler beeinflussen das universelle Quartett (R, Θ, β, ζ(R)). Nullmodelle und Datenpfade sind in jeder Karte verankert.',

    universalParameters: 'Universal-Parameter',
    criticalThreshold: 'Θ (kritischer Schwellenwert)',
    steepness: 'β (Steilheit)',
    coupling: 'Kopplung Γ',
    noiseScaling: 'Rauschskalierung',
    controls: 'Steuerung',
    start: 'Start',
    pause: 'Pause',
    reset: 'Reset',
    poetic: 'Poetisch',
    time: 'Zeit',
    crossResonance: 'Cross-Resonanz',

    resonanceActive: '⚡ Resonanz aktiv',
    membraneObserved: '○ Membran beobachtet',
    triLayerEchoes: 'Tri-Layer-Echos',
    formal: 'Formal',
    empirical: 'Empirisch',
    poeticNarrative: 'Poetisch',
    analysisTheta: 'Analyse Θ',
    analysisBeta: 'Analyse β',
    simulationTheta: 'Simulation Θ',
    simulationBeta: 'Simulation β',
    deltaAIC: 'ΔAIC',
    against: 'gegen',
    impedance: 'Impedanz',
    controlParameter: 'Kontrollparameter',
    orderParameter: 'Ordnungsparameter',
    dataset: 'Dataset',
    analysisPath: 'Analysepfad',

    reservoirDynamics: 'Reservoir-Dynamik R(t)',
    reservoirDescription: 'Linien zeigen den Verlauf des Ordnungsparameters R pro Domäne. Der rote Strich markiert die aktuelle Schwelle Θ; sobald die Kurven darüber hinaussteigen, öffnet sich die Membran (σ(β(R-Θ)) → 1) und der Poetik-Modus meldet die Resonanz.',
    phasePortrait: 'Phasenporträt (R, Ψ)',
    phasePortraitDescription: 'Phasenraumdarstellung zeigt die Beziehung zwischen Reservoir R und Feld Ψ. Trajektorien enthüllen Attraktor-Dynamik und Schwellenüberschreitungsverhalten.',
    fieldTypeDistribution: 'Feldtyp-Verteilung',
    fieldTypeDistributionDescription: 'Verteilung der aktiven Domänen über fünf UTAC-Feldtypen basierend auf β-Werten. Farben zeigen verschiedene Kritikalitätsregime.',
    crepDashboard: 'CREP-Scores',
    coherence: 'Kohärenz',
    resilience: 'Resilienz',
    empathy: 'Empathie',
    propagation: 'Propagation',

    footerNote: 'Simulator-Version verknüpft Analyse-Pfade aus `analysis/results/*.json` mit den hier angezeigten Karten. ΔAIC- und R²-Werte stammen direkt aus den Falsifikationsroutinen; Anpassungen an den Reglern sollten immer gegen die Nullmodelle im Blick behalten werden.',

    fieldTypes: {
      weakly_coupled: 'Schwach Gekoppelt',
      high_dimensional: 'Hochdimensional',
      strongly_coupled: 'Stark Gekoppelt',
      physically_constrained: 'Physikalisch Beschränkt',
      meta_adaptive: 'Meta-Adaptiv'
    },

    timeSeries: 'Zeitreihen',
    phaseSpace: 'Phasenraum',
    statistics: 'Statistiken',
    language: 'Sprache'
  }
};

export function getTranslation(lang: Language): Translations {
  return translations[lang] || translations.en;
}
