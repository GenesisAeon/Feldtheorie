/**
 * Field Type Classifier for UTAC
 *
 * Classifies systems into 5 field types based on β (criticality parameter)
 *
 * v2-feat-ext-001: Tooltip System
 */

import { FieldType, FieldTypeInfo } from '../types';

/**
 * Field Type Ranges and Descriptions
 * Based on UTAC Sonification & Meta-Regression Analysis
 */
export const FIELD_TYPE_DEFINITIONS: Record<FieldType, FieldTypeInfo> = {
  weakly_coupled: {
    type: 'weakly_coupled',
    description: 'Weakly Coupled: Gradual transitions, low coupling',
    beta_range: [0, 2.5],
    color: '#a8dadc'  // Soft cyan
  },
  high_dimensional: {
    type: 'high_dimensional',
    description: 'High-Dimensional: Complex state spaces (AI, neural)',
    beta_range: [2.5, 4.0],
    color: '#457b9d'  // Steel blue
  },
  strongly_coupled: {
    type: 'strongly_coupled',
    description: 'Strongly Coupled: Resonant systems (climate, ecology)',
    beta_range: [4.0, 5.5],
    color: '#1d3557'  // Navy
  },
  physically_constrained: {
    type: 'physically_constrained',
    description: 'Physically Constrained: Hard constraints (astrophysics)',
    beta_range: [5.5, 10.0],
    color: '#e63946'  // Crimson
  },
  meta_adaptive: {
    type: 'meta_adaptive',
    description: 'Meta-Adaptive: Extreme nonlinearity (urban systems)',
    beta_range: [10.0, Infinity],
    color: '#f77f00'  // Burnt orange
  }
};

/**
 * Classify field type based on β value
 *
 * @param beta - Criticality parameter (slope of logistic curve)
 * @returns Field type information
 *
 * @example
 * classifyFieldType(3.47) // → high_dimensional (LLM)
 * classifyFieldType(4.2)  // → strongly_coupled (AMOC)
 * classifyFieldType(16.3) // → meta_adaptive (Urban Heat)
 */
export function classifyFieldType(beta: number | null | undefined): FieldTypeInfo {
  if (beta === null || beta === undefined) {
    // Default to high-dimensional if unknown
    return FIELD_TYPE_DEFINITIONS.high_dimensional;
  }

  if (beta < 2.5) {
    return FIELD_TYPE_DEFINITIONS.weakly_coupled;
  } else if (beta < 4.0) {
    return FIELD_TYPE_DEFINITIONS.high_dimensional;
  } else if (beta < 5.5) {
    return FIELD_TYPE_DEFINITIONS.strongly_coupled;
  } else if (beta < 10.0) {
    return FIELD_TYPE_DEFINITIONS.physically_constrained;
  } else {
    return FIELD_TYPE_DEFINITIONS.meta_adaptive;
  }
}

/**
 * Get all field types as array (for legends, dropdowns, etc.)
 */
export function getAllFieldTypes(): FieldTypeInfo[] {
  return Object.values(FIELD_TYPE_DEFINITIONS);
}

/**
 * Get field type color by beta value
 * Convenience function for plotting
 */
export function getFieldTypeColor(beta: number | null | undefined): string {
  return classifyFieldType(beta).color;
}
