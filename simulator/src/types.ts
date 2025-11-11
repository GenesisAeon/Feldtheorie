export type ModulationKind = 'sin' | 'tanh';

export interface StimulusSpec {
  base: number;
  amplitude: number;
  frequency: number;
  noise: number;
  modulation?: {
    type: ModulationKind;
    amplitude: number;
    frequency: number;
  };
}

export interface SimulationConfig {
  theta: number;
  beta: number;
  initial_R: number;
  initial_psi: number;
  initial_phi: number;
  stimulus: StimulusSpec;
}

export interface AnalysisSummary {
  result_path: string;
  theta: number | null;
  theta_ci: [number, number] | null;
  beta: number | null;
  beta_ci: [number, number] | null;
  logistic_r2: number | null;
  delta_aic_best_null: number | null;
  delta_r2_best_null: number | null;
  best_null_model: string | null;
}

export interface ImpedanceProfile {
  definition: string;
  closed: number;
  open: number;
  mean: number;
}

export interface NarrativeThreads {
  formal: string;
  empirical: string;
  poetic: string;
}

export interface DomainPreset {
  id: string;
  label: string;
  domain: string;
  featured: boolean;
  color: string;
  icon: 'blackHole' | 'bee' | 'brain' | 'leaf' | 'network' | 'helix';
  control_parameter: string;
  order_parameter: string;
  analysis: AnalysisSummary;
  impedance: ImpedanceProfile;
  simulation: SimulationConfig;
  narrative: NarrativeThreads;
  poetic_messages: string[];
  references?: {
    dataset?: string;
    notes?: string;
  };
}

export interface DomainState {
  id: string;
  label: string;
  R: number;
  psi: number;
  phi: number;
  zeta: number;
  gate: number;
  theta: number;
  beta: number;
  active: boolean;
}

export interface TrajectoryPoint {
  time: number;
  value: number;
}

// ============================================================================
// Tooltip System Types (v2-feat-ext-001)
// ============================================================================

/**
 * CREP Scores: Coherence, Resilience, Empathy, Propagation
 * Measures of system quality in UTAC framework
 */
export interface CREPScores {
  coherence: number;      // 0-1: Internal consistency
  resilience: number;     // 0-1: Recovery capacity
  empathy: number;        // 0-1: Cross-domain resonance
  propagation: number;    // 0-1: Signal transmission
}

/**
 * Field Type Classification
 * Five UTAC field types with different β-characteristics
 */
export type FieldType =
  | 'weakly_coupled'       // β < 2.5
  | 'high_dimensional'     // β ∈ [2.5, 4.0]
  | 'strongly_coupled'     // β ∈ [4.0, 5.5]
  | 'physically_constrained' // β ∈ [5.5, 10.0]
  | 'meta_adaptive';       // β > 10.0

export interface FieldTypeInfo {
  type: FieldType;
  description: string;
  beta_range: [number, number];
  color: string;
}

/**
 * Complete Tooltip Data
 * All information needed for rich interactive tooltips
 */
export interface TooltipData {
  // Basic identification
  preset_id: string;
  label: string;
  domain: string;

  // UTAC parameters (from AnalysisSummary)
  beta: number | null;
  beta_ci?: [number, number] | null;
  theta: number | null;
  theta_ci?: [number, number] | null;

  // Statistical metrics
  r_squared: number | null;
  delta_aic: number | null;
  delta_r2: number | null;
  best_null_model: string | null;

  // CREP scores
  crep?: CREPScores;

  // Field type classification
  field_type?: FieldTypeInfo;

  // Impedance (ζ)
  impedance_closed: number;
  impedance_open: number;
  impedance_mean: number;

  // Narrative context
  formal_thread?: string;
  empirical_thread?: string;
  poetic_thread?: string;
}
