/**
 * Tooltip Data Builder
 *
 * Extracts and builds rich tooltip data from DomainPreset
 *
 * v2-feat-ext-001: Tooltip System
 */

import { DomainPreset, TooltipData, CREPScores } from '../types';
import { classifyFieldType } from './fieldTypeClassifier';

/**
 * Extract CREP scores from preset JSON filename
 *
 * CREP scores are encoded in preset filenames or metadata.
 * For now, we'll compute heuristic scores based on analysis metrics.
 *
 * TODO: Add explicit CREP scores to preset JSON files in future versions
 *
 * @param preset - Domain preset
 * @returns CREP scores (0-1 scale)
 */
function extractCREPScores(preset: DomainPreset): CREPScores | undefined {
  const { analysis, impedance } = preset;

  // If we don't have analysis data, can't compute CREP
  if (!analysis.logistic_r2 || !analysis.delta_aic_best_null) {
    return undefined;
  }

  // Heuristic CREP computation:
  // - Coherence: R² (how well model fits)
  // - Resilience: Impedance mean (recovery capacity)
  // - Empathy: Normalized ΔAIC (cross-domain transferability)
  // - Propagation: β-dependent (signal transmission efficiency)

  const coherence = Math.min(1.0, analysis.logistic_r2);

  const resilience = Math.min(1.0, impedance.mean / 2.0);

  const empathy = Math.min(1.0, analysis.delta_aic_best_null / 100.0);

  const beta = analysis.beta || 4.0;
  const propagation = Math.min(1.0, 1.0 / (1.0 + Math.exp(-0.2 * (beta - 5.0))));

  return {
    coherence,
    resilience,
    empathy,
    propagation
  };
}

/**
 * Build complete tooltip data from preset
 *
 * @param preset - Domain preset with all metadata
 * @returns Complete tooltip data object
 *
 * @example
 * const preset = PRESETS.find(p => p.id === 'llm_resonance');
 * const tooltipData = buildTooltipData(preset);
 * console.log(tooltipData.beta, tooltipData.field_type.description);
 */
export function buildTooltipData(preset: DomainPreset): TooltipData {
  const { analysis, impedance, narrative } = preset;

  return {
    // Basic identification
    preset_id: preset.id,
    label: preset.label,
    domain: preset.domain,

    // UTAC parameters
    beta: analysis.beta,
    beta_ci: analysis.beta_ci,
    theta: analysis.theta,
    theta_ci: analysis.theta_ci,

    // Statistical metrics
    r_squared: analysis.logistic_r2,
    delta_aic: analysis.delta_aic_best_null,
    delta_r2: analysis.delta_r2_best_null,
    best_null_model: analysis.best_null_model,

    // CREP scores
    crep: extractCREPScores(preset),

    // Field type classification
    field_type: classifyFieldType(analysis.beta),

    // Impedance
    impedance_closed: impedance.closed,
    impedance_open: impedance.open,
    impedance_mean: impedance.mean,

    // Narrative threads
    formal_thread: narrative.formal,
    empirical_thread: narrative.empirical,
    poetic_thread: narrative.poetic
  };
}

/**
 * Build tooltip data for multiple presets
 */
export function buildTooltipDataMap(presets: DomainPreset[]): Map<string, TooltipData> {
  const map = new Map<string, TooltipData>();
  presets.forEach(preset => {
    map.set(preset.id, buildTooltipData(preset));
  });
  return map;
}
