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
  theta: number;
  theta_ci: [number, number];
  beta: number;
  beta_ci: [number, number];
  logistic_r2: number;
  delta_aic_best_null: number;
  delta_r2_best_null: number;
  best_null_model: string;
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
  icon: 'blackHole' | 'bee' | 'brain' | 'leaf' | 'network';
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
