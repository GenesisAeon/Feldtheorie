import { FC, useMemo } from 'react';
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
  ReferenceLine
} from 'recharts';
import { DomainPreset, DomainState } from '../types';
import { Language } from '../i18n/translations';

interface PhasePortraitProps {
  activePresets: DomainPreset[];
  domainStates: Record<string, DomainState>;
  theta: number;
  lang: Language;
}

/**
 * Phase Portrait: R vs Ψ
 *
 * Visualizes the phase space relationship between reservoir (R)
 * and field (Ψ) for all active domains.
 *
 * Shows attractor dynamics and threshold crossing behavior.
 */
export const PhasePortrait: FC<PhasePortraitProps> = ({
  activePresets,
  domainStates,
  theta,
  lang
}) => {
  const phaseData = useMemo(() => {
    return activePresets.map(preset => {
      const state = domainStates[preset.id];
      if (!state) return null;

      return {
        name: preset.label,
        R: state.R,
        psi: state.psi,
        phi: state.phi,
        gate: state.gate,
        active: state.active,
        color: preset.color
      };
    }).filter(Boolean);
  }, [activePresets, domainStates]);

  return (
    <div className="chart-wrapper">
      <h2 className="section-title">
        {lang === 'en' ? 'Phase Portrait (R, Ψ)' : 'Phasenporträt (R, Ψ)'}
      </h2>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="4 4" stroke="rgba(99,102,241,0.35)" />
          <XAxis
            dataKey="R"
            type="number"
            name="R (Reservoir)"
            stroke="rgba(209,213,255,0.65)"
            label={{
              value: 'R (Reservoir)',
              position: 'insideBottom',
              offset: -10,
              fill: 'rgba(209,213,255,0.85)'
            }}
          />
          <YAxis
            dataKey="psi"
            type="number"
            name="Ψ (Field)"
            stroke="rgba(209,213,255,0.65)"
            label={{
              value: 'Ψ (Field)',
              angle: -90,
              position: 'insideLeft',
              fill: 'rgba(209,213,255,0.85)'
            }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{
              backgroundColor: 'rgba(14,10,35,0.95)',
              border: '1px solid rgba(99,102,241,0.5)',
              borderRadius: '8px',
              padding: '12px'
            }}
            labelStyle={{ color: 'rgba(226,232,255,0.95)' }}
            itemStyle={{ color: 'rgba(196,181,253,0.95)' }}
          />
          <Legend />
          <ReferenceLine
            x={theta}
            stroke="#f87171"
            strokeDasharray="6 4"
            label={{ value: 'Θ', fill: '#f87171' }}
          />
          {activePresets.map(preset => (
            <Scatter
              key={preset.id}
              name={preset.label}
              data={phaseData.filter(d => d && d.name === preset.label)}
              fill={preset.color}
              opacity={0.8}
              shape="circle"
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
      <p className="meta-footnote">
        {lang === 'en'
          ? 'Phase space representation showing the relationship between reservoir R and field Ψ. Points represent current states; crossing Θ (red line) indicates threshold activation.'
          : 'Phasenraumdarstellung zeigt die Beziehung zwischen Reservoir R und Feld Ψ. Punkte repräsentieren aktuelle Zustände; Überschreiten von Θ (rote Linie) zeigt Schwellenaktivierung.'}
      </p>
    </div>
  );
};
