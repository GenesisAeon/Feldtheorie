/**
 * RK4 Physics Integrator for UTAC Logistic Resonance
 *
 * Implements Runge-Kutta 4th order integration for Type-VI implosive scenarios
 * with τ*-safety buffer to handle stiff equations (β>15).
 *
 * References:
 * - activation_gaps_tau_star.md (τ*-default: 0.1·|Θ−R|)
 * - type6_crep_tau_star_checklist.md (CREP governance)
 * - FinalyzeVorschlägeGemini.txt:60-181 (RK4 specification)
 */

import { clamp, cubicRootJump, invertedSigmoid, tauStar } from './logistic';

/**
 * State vector for UTAC dynamics
 */
export interface SimulationState {
  R: number;      // Resource/Reality level
  psi: number;    // Ψ field (wavefunction resonance)
  phi: number;    // Φ field (golden ratio coupling)
  t: number;      // Time
}

/**
 * Simulation parameters
 */
export interface SimulationParams {
  theta: number;         // Threshold
  beta: number;          // Steepness
  coupling: number;      // Cross-domain coupling strength
  stimulus: number;      // External forcing
  zeta: number;         // Impedance (ζ)
  useTypeVI?: boolean;  // Enable Type-VI implosive mode
}

/**
 * Derivative vector dState/dt
 */
interface Derivatives {
  dR: number;
  dPsi: number;
  dPhi: number;
}

/**
 * Compute derivatives for UTAC logistic resonance system
 *
 * @param state Current state
 * @param t Current time
 * @param params System parameters
 * @returns Derivatives dR/dt, dψ/dt, dφ/dt
 */
export function computeDerivatives(
  state: SimulationState,
  t: number,
  params: SimulationParams
): Derivatives {
  const { R, psi, phi } = state;
  const { theta, beta, coupling, stimulus, zeta, useTypeVI } = params;

  // Type-VI implosive gate if enabled
  let gate: number;
  let effectiveBeta = beta;

  if (useTypeVI && R > theta) {
    effectiveBeta = clamp(cubicRootJump(R, theta, beta), 0.5, 18);
    gate = invertedSigmoid(R, theta, effectiveBeta);
  } else {
    // Standard logistic gate
    gate = 1 / (1 + Math.exp(-beta * (R - theta)));
  }

  // Logistic growth with resonance coupling
  const growth = gate * (1 - R / 10) * R;
  const resonance = coupling * psi * Math.sin(phi);
  const damping = -zeta * (R - theta);

  const dR = growth + resonance + damping + stimulus;

  // Ψ field dynamics (wavefunction resonance)
  const psiDamping = 0.05 * psi;
  const psiCoupling = 0.1 * (R - theta) * Math.cos(phi);
  const dPsi = psiCoupling - psiDamping;

  // Φ field dynamics (phase evolution with golden ratio)
  const PHI = 1.618034;
  const phaseVelocity = PHI * Math.sqrt(Math.abs(R - theta) + 0.1);
  const dPhi = phaseVelocity;

  return { dR, dPsi, dPhi };
}

/**
 * Single RK4 integration step with τ*-safety buffer
 *
 * @param state Current state
 * @param dt Time step
 * @param params System parameters
 * @returns New state after dt
 */
export function rk4Step(
  state: SimulationState,
  dt: number,
  params: SimulationParams
): SimulationState {
  const { t, R } = state;
  const { theta, beta, useTypeVI } = params;

  // τ*-safety buffer for Type-VI implosive scenarios
  let effectiveDt = dt;
  if (useTypeVI && R > theta) {
    const amplifiedBeta = clamp(cubicRootJump(R, theta, beta), 0.5, 18);
    const tau = Math.abs(tauStar(R, theta, amplifiedBeta));

    // Adaptive time step: dt ≤ 0.1·τ* for numerical stability
    const tauBuffer = 0.1 * tau;
    effectiveDt = Math.min(dt, tauBuffer);
  }

  // RK4 four stages
  // k1 = f(t, y)
  const k1 = computeDerivatives(state, t, params);

  // k2 = f(t + dt/2, y + k1·dt/2)
  const state2: SimulationState = {
    R: state.R + k1.dR * effectiveDt / 2,
    psi: state.psi + k1.dPsi * effectiveDt / 2,
    phi: state.phi + k1.dPhi * effectiveDt / 2,
    t: t + effectiveDt / 2
  };
  const k2 = computeDerivatives(state2, t + effectiveDt / 2, params);

  // k3 = f(t + dt/2, y + k2·dt/2)
  const state3: SimulationState = {
    R: state.R + k2.dR * effectiveDt / 2,
    psi: state.psi + k2.dPsi * effectiveDt / 2,
    phi: state.phi + k2.dPhi * effectiveDt / 2,
    t: t + effectiveDt / 2
  };
  const k3 = computeDerivatives(state3, t + effectiveDt / 2, params);

  // k4 = f(t + dt, y + k3·dt)
  const state4: SimulationState = {
    R: state.R + k3.dR * effectiveDt,
    psi: state.psi + k3.dPsi * effectiveDt,
    phi: state.phi + k3.dPhi * effectiveDt,
    t: t + effectiveDt
  };
  const k4 = computeDerivatives(state4, t + effectiveDt, params);

  // Weighted average: y_new = y + (k1 + 2k2 + 2k3 + k4) · dt/6
  return {
    R: state.R + (k1.dR + 2*k2.dR + 2*k3.dR + k4.dR) * effectiveDt / 6,
    psi: state.psi + (k1.dPsi + 2*k2.dPsi + 2*k3.dPsi + k4.dPsi) * effectiveDt / 6,
    phi: state.phi + (k1.dPhi + 2*k2.dPhi + 2*k3.dPhi + k4.dPhi) * effectiveDt / 6,
    t: t + effectiveDt
  };
}

/**
 * Euler integration (for comparison/fallback)
 *
 * @param state Current state
 * @param dt Time step
 * @param params System parameters
 * @returns New state after dt
 */
export function eulerStep(
  state: SimulationState,
  dt: number,
  params: SimulationParams
): SimulationState {
  const derivatives = computeDerivatives(state, state.t, params);

  return {
    R: state.R + derivatives.dR * dt,
    psi: state.psi + derivatives.dPsi * dt,
    phi: state.phi + derivatives.dPhi * dt,
    t: state.t + dt
  };
}
