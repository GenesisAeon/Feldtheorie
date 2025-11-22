import { FC, useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { DomainPreset, DomainState, CREPScores } from '../types';
import { Language } from '../i18n/translations';

interface CREPDashboardProps {
  activePresets: DomainPreset[];
  domainStates: Record<string, DomainState>;
  lang: Language;
}

/**
 * Compute CREP scores for a domain
 *
 * CREP: Coherence, Resilience, Empathy, Propagation
 * Quality metrics for UTAC systems
 */
function computeCREP(preset: DomainPreset, state: DomainState): CREPScores {
  const beta = preset.analysis.beta || 4.0;
  const r2 = preset.analysis.logistic_r2 || 0;
  const deltaAIC = preset.analysis.delta_aic_best_null || 0;

  // Coherence: How well does the logistic model fit? (R²)
  const coherence = Math.max(0, Math.min(1, r2));

  // Resilience: Statistical strength (ΔAIC normalized)
  const resilience = Math.max(0, Math.min(1, deltaAIC / 100));

  // Empathy: Cross-domain coupling strength (gate × coupling potential)
  const empathy = Math.max(0, Math.min(1, state.gate * (state.phi / 10)));

  // Propagation: Signal transmission capacity (β normalized)
  // Higher β → steeper transitions → stronger propagation
  const propagation = Math.max(0, Math.min(1, beta / 15));

  return {
    coherence,
    resilience,
    empathy,
    propagation
  };
}

/**
 * CREP Dashboard
 *
 * Visualizes CREP scores (Coherence, Resilience, Empathy, Propagation)
 * for all active domains using both bar and radar charts.
 */
export const CREPDashboard: FC<CREPDashboardProps> = ({
  activePresets,
  domainStates,
  lang
}) => {
  const crepData = useMemo(() => {
    return activePresets.map(preset => {
      const state = domainStates[preset.id];
      if (!state) return null;

      const crep = computeCREP(preset, state);
      return {
        name: preset.label,
        ...crep,
        color: preset.color,
        total: (crep.coherence + crep.resilience + crep.empathy + crep.propagation) / 4
      };
    }).filter(Boolean);
  }, [activePresets, domainStates]);

  const radarData = useMemo(() => {
    if (crepData.length === 0) return [];

    const labels = lang === 'en'
      ? ['Coherence', 'Resilience', 'Empathy', 'Propagation']
      : ['Kohärenz', 'Resilienz', 'Empathie', 'Propagation'];

    return labels.map((label, idx) => {
      const keys = ['coherence', 'resilience', 'empathy', 'propagation'] as const;
      const key = keys[idx];

      const entry: any = { metric: label };
      crepData.forEach(d => {
        if (d) entry[d.name] = d[key];
      });
      return entry;
    });
  }, [crepData, lang]);

  const avgCREP = useMemo(() => {
    if (crepData.length === 0) return 0;
    return crepData.reduce((sum, d) => sum + (d?.total || 0), 0) / crepData.length;
  }, [crepData]);

  return (
    <div className="chart-wrapper">
      <h2 className="section-title">
        {lang === 'en' ? 'CREP Quality Scores' : 'CREP-Qualitäts-Scores'}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Bar Chart: Total CREP */}
        <div>
          <h3 style={{ fontSize: '1rem', color: 'rgba(226,232,255,0.85)', marginBottom: '0.5rem' }}>
            {lang === 'en' ? 'Aggregate CREP Score' : 'Gesamt-CREP-Score'}
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart
              data={crepData}
              margin={{ top: 10, right: 10, left: 10, bottom: 60 }}
            >
              <CartesianGrid strokeDasharray="4 4" stroke="rgba(99,102,241,0.35)" />
              <XAxis
                dataKey="name"
                stroke="rgba(209,213,255,0.65)"
                angle={-30}
                textAnchor="end"
                height={80}
              />
              <YAxis
                stroke="rgba(209,213,255,0.65)"
                domain={[0, 1]}
                ticks={[0, 0.25, 0.5, 0.75, 1]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(14,10,35,0.95)',
                  border: '1px solid rgba(99,102,241,0.5)',
                  borderRadius: '8px',
                  padding: '12px'
                }}
                formatter={(value: number) => value.toFixed(3)}
              />
              <Bar dataKey="total" name={lang === 'en' ? 'Total CREP' : 'Gesamt-CREP'}>
                {crepData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry?.color || '#888'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar Chart: CREP Components */}
        <div>
          <h3 style={{ fontSize: '1rem', color: 'rgba(226,232,255,0.85)', marginBottom: '0.5rem' }}>
            {lang === 'en' ? 'CREP Components' : 'CREP-Komponenten'}
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(99,102,241,0.35)" />
              <PolarAngleAxis
                dataKey="metric"
                stroke="rgba(209,213,255,0.65)"
                style={{ fontSize: '0.85rem' }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 1]}
                stroke="rgba(209,213,255,0.65)"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(14,10,35,0.95)',
                  border: '1px solid rgba(99,102,241,0.5)',
                  borderRadius: '8px',
                  padding: '12px'
                }}
                formatter={(value: number) => value.toFixed(3)}
              />
              <Legend />
              {crepData.map((entry, idx) => (
                entry && (
                  <Radar
                    key={idx}
                    name={entry.name}
                    dataKey={entry.name}
                    stroke={entry.color}
                    fill={entry.color}
                    fillOpacity={0.3}
                  />
                )
              ))}
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div
        style={{
          marginTop: '1rem',
          padding: '1rem',
          background: 'rgba(99,102,241,0.15)',
          borderRadius: '8px',
          border: '1px solid rgba(99,102,241,0.35)'
        }}
      >
        <p style={{ margin: 0, color: 'rgba(226,232,255,0.95)', fontSize: '0.95rem' }}>
          <strong>
            {lang === 'en' ? 'Average CREP Score:' : 'Durchschnittlicher CREP-Score:'}
          </strong>{' '}
          {avgCREP.toFixed(3)}
        </p>
        <p className="meta-footnote" style={{ margin: '0.5rem 0 0 0' }}>
          {lang === 'en'
            ? 'CREP measures system quality: Coherence (fit quality R²), Resilience (statistical strength ΔAIC), Empathy (cross-domain coupling), and Propagation (signal transmission capacity β).'
            : 'CREP misst Systemqualität: Kohärenz (Anpassungsgüte R²), Resilienz (statistische Stärke ΔAIC), Empathie (domänenübergreifende Kopplung) und Propagation (Signalübertragungskapazität β).'}
        </p>
      </div>
    </div>
  );
};
