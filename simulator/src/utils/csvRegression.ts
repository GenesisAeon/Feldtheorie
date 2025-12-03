/**
 * CSV Parser with Browser-based Logistic Regression
 *
 * Estimates β (steepness) and Θ (threshold) from time-series data
 * using simple least-squares fitting of logistic curve.
 *
 * Expected CSV format:
 * - Column 1: time or index
 * - Column 2: resource value (R)
 * - Optional Column 3: label/domain
 *
 * References:
 * - FinalyzeVorschlägeGemini.txt:79-161 (CSV Drag&Drop spec)
 * - V6ToDorefresh.md Priority 10 (Simulator-UX)
 */

export interface DataPoint {
  t: number;
  R: number;
}

export interface RegressionResult {
  beta: number;
  theta: number;
  r_squared: number;
  data: DataPoint[];
  label?: string;
}

/**
 * Parse CSV string into data points
 */
export function parseCSV(csvText: string): DataPoint[] {
  const lines = csvText.trim().split('\n');
  const data: DataPoint[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || line.startsWith('#')) continue; // Skip comments and empty lines

    const parts = line.split(/[,\t;]/); // Support comma, tab, semicolon
    if (parts.length < 2) continue;

    const t = parseFloat(parts[0]);
    const R = parseFloat(parts[1]);

    if (!isNaN(t) && !isNaN(R)) {
      data.push({ t, R });
    }
  }

  return data;
}

/**
 * Logistic function: σ(t) = 1 / (1 + exp(-β(t - Θ)))
 */
function logistic(t: number, beta: number, theta: number): number {
  return 1 / (1 + Math.exp(-beta * (t - theta)));
}

/**
 * Simple grid search to estimate β and Θ
 * This is a lightweight browser-friendly approach
 */
export function estimateBetaTheta(data: DataPoint[]): RegressionResult {
  if (data.length < 3) {
    // Not enough data, return defaults
    return {
      beta: 4.236,
      theta: 5.0,
      r_squared: 0,
      data
    };
  }

  // Normalize R values to [0, 1] for fitting
  const R_values = data.map(d => d.R);
  const R_min = Math.min(...R_values);
  const R_max = Math.max(...R_values);
  const R_range = R_max - R_min || 1;

  const normalizedData = data.map(d => ({
    t: d.t,
    R: (d.R - R_min) / R_range
  }));

  // Grid search parameters
  const t_values = data.map(d => d.t);
  const t_min = Math.min(...t_values);
  const t_max = Math.max(...t_values);
  const t_mid = (t_min + t_max) / 2;

  // Search ranges
  const beta_candidates = [0.5, 1, 2, 4, 6, 8, 10, 12, 15];
  const theta_offsets = [-0.5, -0.25, 0, 0.25, 0.5, 1.0];

  let bestBeta = 4.236;
  let bestTheta = t_mid;
  let bestSSE = Infinity;

  // Grid search
  for (const beta of beta_candidates) {
    for (const offset of theta_offsets) {
      const theta = t_mid + offset * (t_max - t_min);

      // Compute Sum of Squared Errors
      let sse = 0;
      for (const point of normalizedData) {
        const predicted = logistic(point.t, beta, theta);
        const error = point.R - predicted;
        sse += error * error;
      }

      if (sse < bestSSE) {
        bestSSE = sse;
        bestBeta = beta;
        bestTheta = theta;
      }
    }
  }

  // Compute R² (coefficient of determination)
  const R_mean = normalizedData.reduce((sum, d) => sum + d.R, 0) / normalizedData.length;
  let ssTot = 0;
  let ssRes = 0;

  for (const point of normalizedData) {
    const predicted = logistic(point.t, bestBeta, bestTheta);
    ssRes += (point.R - predicted) ** 2;
    ssTot += (point.R - R_mean) ** 2;
  }

  const r_squared = ssTot > 0 ? 1 - ssRes / ssTot : 0;

  // Scale theta back to original range if needed
  // For display purposes, keep theta in time units
  return {
    beta: bestBeta,
    theta: bestTheta,
    r_squared: Math.max(0, Math.min(1, r_squared)),
    data
  };
}

/**
 * Full CSV processing pipeline: parse + estimate
 */
export function processCSV(csvText: string, label?: string): RegressionResult {
  const data = parseCSV(csvText);
  const result = estimateBetaTheta(data);
  return { ...result, label };
}

/**
 * Generate example CSV for testing
 */
export function generateExampleCSV(): string {
  const lines = ['# time,resource'];
  const beta = 6;
  const theta = 5;
  const noise = 0.05;

  for (let t = 0; t <= 10; t += 0.5) {
    const R = logistic(t, beta, theta) + (Math.random() - 0.5) * noise;
    lines.push(`${t.toFixed(1)},${R.toFixed(4)}`);
  }

  return lines.join('\n');
}
