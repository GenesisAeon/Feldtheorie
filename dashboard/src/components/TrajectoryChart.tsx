/**
 * TrajectoryChart Component
 * =========================
 *
 * Real-time trajectory visualization for β, κ, resonance evolution
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { TrajectoryPoint } from '../types/aeon';

interface TrajectoryChartProps {
  data: TrajectoryPoint[];
  maxPoints?: number;
}

export function TrajectoryChart({ data, maxPoints = 100 }: TrajectoryChartProps) {
  // Take last N points for performance
  const displayData = data.slice(-maxPoints);

  // Transform data for Recharts
  const chartData = displayData.map((point, index) => ({
    index,
    beta: point.beta,
    kappa: point.kappa,
    resonance: point.resonance,
    timestamp: new Date(point.timestamp * 1000).toLocaleTimeString(),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="timestamp"
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
          interval="preserveStartEnd"
        />
        <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} domain={[0, 1]} />
        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px' }} />

        {/* Critical thresholds */}
        <ReferenceLine y={0.1} stroke="#ef4444" strokeDasharray="3 3" label="Critical β" />
        <ReferenceLine y={0.2} stroke="#f59e0b" strokeDasharray="3 3" label="Bardo κ" />

        {/* Data lines */}
        <Line
          type="monotone"
          dataKey="beta"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          name="β (Steepness)"
        />
        <Line
          type="monotone"
          dataKey="kappa"
          stroke="#10b981"
          strokeWidth={2}
          dot={false}
          name="κ (Coupling)"
        />
        <Line
          type="monotone"
          dataKey="resonance"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={false}
          name="Resonance"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
