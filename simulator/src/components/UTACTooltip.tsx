/**
 * UTAC Rich Tooltip Component
 *
 * Custom tooltip for Recharts with β, Θ, R², ΔAIC, CREP scores
 *
 * v2-feat-ext-001: Tooltip System
 */

import { TooltipProps } from 'recharts';
import { TooltipData } from '../types';

interface UTACTooltipProps extends TooltipProps<number, string> {
  tooltipData?: Map<string, TooltipData>;
  showCREP?: boolean;
  showFieldType?: boolean;
  showNarrative?: boolean;
}

/**
 * Format number with precision
 */
function fmt(value: number | null | undefined, precision: number = 2): string {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(precision);
}

/**
 * Format confidence interval
 */
function fmtCI(ci: [number, number] | null | undefined): string {
  if (!ci) return '';
  return `[${fmt(ci[0])}, ${fmt(ci[1])}]`;
}

/**
 * UTAC Rich Tooltip Component
 *
 * Displays comprehensive system metrics on hover:
 * - Basic: Time, Value
 * - UTAC: β, Θ (with CIs)
 * - Stats: R², ΔAIC
 * - CREP: Coherence, Resilience, Empathy, Propagation
 * - Field Type: Classification & description
 * - Narrative: Poetic/Empirical context (optional)
 */
export const UTACTooltip: React.FC<UTACTooltipProps> = ({
  active,
  payload,
  label,
  tooltipData,
  showCREP = true,
  showFieldType = true,
  showNarrative = false
}) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  // Get the data point
  const dataPoint = payload[0];
  const presetId = dataPoint.dataKey as string; // e.g., 'llm_resonance'
  const value = dataPoint.value as number;
  const color = dataPoint.color;

  // Get tooltip metadata if available
  const metadata = tooltipData?.get(presetId);

  return (
    <div
      style={{
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        border: `2px solid ${color || '#4b5563'}`,
        borderRadius: '8px',
        padding: '12px 16px',
        color: '#f9fafb',
        fontSize: '13px',
        lineHeight: '1.5',
        maxWidth: '320px',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
        fontFamily: 'ui-monospace, monospace'
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '8px', borderBottom: '1px solid #374151', paddingBottom: '8px' }}>
        <div style={{ fontWeight: 'bold', fontSize: '14px', color: color }}>
          {metadata?.label || presetId}
        </div>
        <div style={{ fontSize: '11px', color: '#9ca3af' }}>
          {metadata?.domain || 'Unknown Domain'}
        </div>
      </div>

      {/* Time & Value */}
      <div style={{ marginBottom: '8px' }}>
        <div><span style={{ color: '#9ca3af' }}>Time:</span> {fmt(label as number, 1)}</div>
        <div><span style={{ color: '#9ca3af' }}>σ(β(R-Θ)):</span> <strong>{fmt(value, 3)}</strong></div>
      </div>

      {/* UTAC Parameters */}
      {metadata && (
        <>
          <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px', color: '#60a5fa' }}>
              UTAC Parameters
            </div>
            <div>
              <span style={{ color: '#9ca3af' }}>β:</span>{' '}
              <strong>{fmt(metadata.beta)}</strong>
              {metadata.beta_ci && (
                <span style={{ fontSize: '11px', color: '#6b7280' }}> {fmtCI(metadata.beta_ci)}</span>
              )}
            </div>
            <div>
              <span style={{ color: '#9ca3af' }}>Θ:</span>{' '}
              <strong>{fmt(metadata.theta)}</strong>
              {metadata.theta_ci && (
                <span style={{ fontSize: '11px', color: '#6b7280' }}> {fmtCI(metadata.theta_ci)}</span>
              )}
            </div>
          </div>

          {/* Statistical Metrics */}
          <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px', color: '#34d399' }}>
              Model Fit
            </div>
            <div>
              <span style={{ color: '#9ca3af' }}>R²:</span> <strong>{fmt(metadata.r_squared, 3)}</strong>
            </div>
            <div>
              <span style={{ color: '#9ca3af' }}>ΔAIC:</span> <strong>{fmt(metadata.delta_aic, 1)}</strong>
              {metadata.delta_aic && metadata.delta_aic > 10 && (
                <span style={{ fontSize: '11px', color: '#34d399' }}> ✓ Significant</span>
              )}
            </div>
            {metadata.best_null_model && (
              <div style={{ fontSize: '11px', color: '#6b7280' }}>
                vs. {metadata.best_null_model}
              </div>
            )}
          </div>

          {/* Field Type */}
          {showFieldType && metadata.field_type && (
            <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px', color: '#f59e0b' }}>
                Field Type
              </div>
              <div
                style={{
                  padding: '4px 8px',
                  backgroundColor: metadata.field_type.color,
                  borderRadius: '4px',
                  fontSize: '11px',
                  color: '#fff',
                  fontWeight: 'bold'
                }}
              >
                {metadata.field_type.type.replace('_', ' ').toUpperCase()}
              </div>
              <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
                {metadata.field_type.description}
              </div>
              <div style={{ fontSize: '10px', color: '#6b7280' }}>
                β ∈ [{fmt(metadata.field_type.beta_range[0], 1)}, {fmt(metadata.field_type.beta_range[1], 1)}]
              </div>
            </div>
          )}

          {/* CREP Scores */}
          {showCREP && metadata.crep && (
            <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px', color: '#a78bfa' }}>
                CREP Scores
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', fontSize: '11px' }}>
                <div>
                  <span style={{ color: '#9ca3af' }}>Coherence:</span> {fmt(metadata.crep.coherence, 2)}
                </div>
                <div>
                  <span style={{ color: '#9ca3af' }}>Resilience:</span> {fmt(metadata.crep.resilience, 2)}
                </div>
                <div>
                  <span style={{ color: '#9ca3af' }}>Empathy:</span> {fmt(metadata.crep.empathy, 2)}
                </div>
                <div>
                  <span style={{ color: '#9ca3af' }}>Propagation:</span> {fmt(metadata.crep.propagation, 2)}
                </div>
              </div>
            </div>
          )}

          {/* Impedance */}
          <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px', color: '#fb7185' }}>
              Impedance (ζ)
            </div>
            <div style={{ fontSize: '11px' }}>
              <span style={{ color: '#9ca3af' }}>Closed:</span> {fmt(metadata.impedance_closed, 2)} |{' '}
              <span style={{ color: '#9ca3af' }}>Open:</span> {fmt(metadata.impedance_open, 2)} |{' '}
              <span style={{ color: '#9ca3af' }}>Mean:</span> {fmt(metadata.impedance_mean, 2)}
            </div>
          </div>

          {/* Narrative (Optional) */}
          {showNarrative && metadata.poetic_thread && (
            <div style={{ marginTop: '8px', borderTop: '1px solid #374151', paddingTop: '8px' }}>
              <div style={{ fontSize: '11px', fontStyle: 'italic', color: '#d1d5db' }}>
                "{metadata.poetic_thread.substring(0, 100)}..."
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
