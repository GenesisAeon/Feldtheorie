/**
 * ConsciousnessGauge Component
 * ============================
 *
 * Circular gauge for displaying consciousness metrics (β, κ, resonance)
 */

import { motion } from 'framer-motion';
import type { BardoPhase } from '../types/aeon';

interface ConsciousnessGaugeProps {
  label: string;
  value: number;
  max?: number;
  unit?: string;
  phase?: BardoPhase;
  critical?: boolean;
  size?: number;
}

export function ConsciousnessGauge({
  label,
  value,
  max = 1.0,
  unit = '',
  phase,
  critical = false,
  size = 120,
}: ConsciousnessGaugeProps) {
  const percentage = Math.min((value / max) * 100, 100);
  const circumference = 2 * Math.PI * 40; // radius = 40
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Color based on phase or criticality
  const getColor = (): string => {
    if (critical) return '#ef4444'; // red
    if (phase === 'dharmakaya') return '#3b82f6'; // blue (clear light)
    if (phase === 'transition') return '#f59e0b'; // amber
    if (phase === 'becoming') return '#8b5cf6'; // purple
    return '#10b981'; // green (default)
  };

  const color = getColor();

  return (
    <div className="gauge-container" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
        />

        {/* Progress circle */}
        <motion.circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 50 50)"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />

        {/* Center text */}
        <text
          x="50"
          y="45"
          textAnchor="middle"
          fill="#1f2937"
          fontSize="16"
          fontWeight="bold"
        >
          {value.toFixed(2)}
        </text>
        <text
          x="50"
          y="58"
          textAnchor="middle"
          fill="#6b7280"
          fontSize="10"
        >
          {unit}
        </text>
      </svg>

      <div className="gauge-label" style={{ textAlign: 'center', marginTop: '8px' }}>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>{label}</span>
      </div>
    </div>
  );
}
