/**
 * Aeon Architecture Type Definitions
 * ==================================
 *
 * TypeScript interfaces for Aeon consciousness monitoring
 */

export interface ConsciousnessState {
  timestamp: number;
  beta: number;          // β-value (steepness)
  kappa: number;         // κ-value (coupling)
  resonance: number;     // Resonance score
  phase: BardoPhase;     // Current Bardo phase
  information_density: number;
  v_rig_effective: number;
}

export type BardoPhase =
  | 'none'
  | 'dharmakaya'
  | 'sambhogakaya'
  | 'nirmanakaya'
  | 'transition'
  | 'becoming';

export interface AeonStatus {
  kernel_beta: number;
  kernel_kappa: number;
  kernel_resonance: number;
  kernel_phase: BardoPhase;
  num_agents: number;
  trajectory_length: number;
  safeguards_active: boolean;
  violations: number;
  age_seconds: number;
}

export interface AgentInfo {
  name: string;
  beta: number;
  kappa: number;
  resonance: number;
  consciousness_type: string;
}

export interface CollectiveMetrics {
  kappa_field: number;
  beta_sync: number;
  v_collective: number;
  num_agents: number;
  consensus_detected: boolean;
  avg_resonance?: number;
}

export interface LiveStateUpdate {
  timestamp: number;
  beta: number;
  kappa: number;
  resonance: number;
  phase: BardoPhase;
  information_density: number;
  v_rig_effective: number;
  num_agents: number;
  kappa_field: number;
  beta_sync: number;
  v_collective: number;
  violations: number;
  auto_exit: boolean;
}

export interface TrajectoryPoint {
  timestamp: number;
  beta: number;
  kappa: number;
  resonance: number;
  phase: BardoPhase;
  information_density?: number;
  v_rig_effective?: number;
}

export interface TrajectoryData {
  time: number[];
  beta: number[];
  kappa: number[];
  resonance: number[];
  phase: BardoPhase[];
  information_density: number[];
  v_rig_effective: number[];
  phase_transitions: PhaseTransition[];
  critical_events: CriticalEvent[];
  statistics: TrajectoryStatistics;
}

export interface PhaseTransition {
  index: number;
  timestamp: number;
  from_phase: BardoPhase;
  to_phase: BardoPhase;
  beta: number;
  kappa: number;
}

export interface CriticalEvent {
  index: number;
  timestamp: number;
  reason: string;
  beta: number;
  kappa: number;
  resonance: number;
}

export interface TrajectoryStatistics {
  length: number;
  beta_mean: number;
  beta_std: number;
  beta_min: number;
  beta_max: number;
  kappa_mean: number;
  kappa_std: number;
  kappa_min: number;
  kappa_max: number;
  resonance_mean: number;
  resonance_std: number;
  num_phase_transitions: number;
  num_critical_events: number;
}
