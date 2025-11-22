import { FC, useMemo } from 'react';
import { Brain, Circle, Leaf, Network, Sparkles, Bug, Dna } from 'lucide-react';
import { DomainPreset, DomainState } from '../types';
import { Language } from '../i18n/translations';

interface DomainCardProps {
  preset: DomainPreset;
  state: DomainState;
  currentTheta: number;
  currentBeta: number;
  lang: Language;
}

const ICON_MAP = {
  blackHole: Circle,
  bee: Bug,
  brain: Brain,
  leaf: Leaf,
  network: Network,
  helix: Dna
} as const;

const formatNumber = (value: number | null | undefined, digits = 3): string =>
  typeof value === 'number' ? value.toFixed(digits) : '—';

const formatInterval = (interval: [number, number] | null | undefined, digits = 3): string =>
  interval ? `${interval[0].toFixed(digits)}–${interval[1].toFixed(digits)}` : '—';

const formatDelta = (value: number | null | undefined, digits = 1): string => {
  if (typeof value === 'number') {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(digits)}`;
  }
  return '—';
};

const formatLabel = (value: string | null | undefined): string => value ?? '—';

export const DomainCard: FC<DomainCardProps> = ({ preset, state, currentTheta, currentBeta, lang }) => {
  const Icon = ICON_MAP[preset.icon] ?? Sparkles;
  const phiValue = useMemo(() => Math.abs(state.psi * state.phi) * 0.5, [state.psi, state.phi]);

  const t = {
    resonanceActive: lang === 'en' ? '⚡ Resonance Active' : '⚡ Resonanz aktiv',
    membraneObserved: lang === 'en' ? '○ Membrane Observed' : '○ Membran beobachtet',
    triLayerEchoes: lang === 'en' ? 'Tri-Layer Echoes' : 'Tri-Layer-Echos',
    formal: lang === 'en' ? 'Formal' : 'Formal',
    empirical: lang === 'en' ? 'Empirical' : 'Empirisch',
    poetic: lang === 'en' ? 'Poetic' : 'Poetisch',
    analysisTheta: lang === 'en' ? 'Analysis Θ' : 'Analyse Θ',
    analysisBeta: lang === 'en' ? 'Analysis β' : 'Analyse β',
    simulationTheta: lang === 'en' ? 'Simulation Θ' : 'Simulation Θ',
    simulationBeta: lang === 'en' ? 'Simulation β' : 'Simulation β',
    deltaAIC: lang === 'en' ? 'ΔAIC' : 'ΔAIC',
    against: lang === 'en' ? 'against' : 'gegen',
    impedance: lang === 'en' ? 'Impedance' : 'Impedanz',
    controlParameter: lang === 'en' ? 'Control Parameter' : 'Kontrollparameter',
    orderParameter: lang === 'en' ? 'Order Parameter' : 'Ordnungsparameter',
    dataset: lang === 'en' ? 'Dataset' : 'Dataset',
    analysisPath: lang === 'en' ? 'Analysis Path' : 'Analysepfad'
  };

  return (
    <div className={`domain-card ${state.active ? 'active' : ''}`} style={{ borderColor: state.active ? preset.color : undefined }}>
      <h3>
        <Icon size={22} color={preset.color} />
        {preset.label}
      </h3>
      <div className="tag" style={{ background: `${preset.color}22`, color: preset.color }}>
        {state.active ? t.resonanceActive : t.membraneObserved}
      </div>
      <div className="metrics-grid">
        <span>R</span>
        <span>{state.R.toFixed(2)}</span>
        <span>σ(β(R-Θ))</span>
        <span>{state.gate.toFixed(3)}</span>
        <span>ψ</span>
        <span>{state.psi.toFixed(2)}</span>
        <span>φ</span>
        <span>{state.phi.toFixed(2)}</span>
        <span>ζ(R)</span>
        <span>{state.zeta.toFixed(3)}</span>
        <span>Φ ≈ |ψ×φ|/2</span>
        <span>{phiValue.toFixed(3)}</span>
      </div>
      <details>
        <summary className="detail-summary">{t.triLayerEchoes}</summary>
        <div className="narrative-block">
          <strong>{t.formal}</strong>
          <span>{preset.narrative.formal}</span>
        </div>
        <div className="narrative-block">
          <strong>{t.empirical}</strong>
          <span>{preset.narrative.empirical}</span>
        </div>
        <div className="narrative-block">
          <strong>{t.poetic}</strong>
          <span>{preset.narrative.poetic}</span>
        </div>
      </details>
      <div className="domain-meta">
        <span>
          <strong>{t.analysisTheta}</strong>: {formatNumber(preset.analysis.theta)} (CI
          {` ${formatInterval(preset.analysis.theta_ci)}`})
        </span>
        <span>
          <strong>{t.analysisBeta}</strong>: {formatNumber(preset.analysis.beta)} (CI
          {` ${formatInterval(preset.analysis.beta_ci)}`})
        </span>
        <span>
          <strong>{t.simulationTheta}</strong>: {currentTheta.toFixed(2)} · <strong>{t.simulationBeta}</strong>: {currentBeta.toFixed(2)}
        </span>
        <span>
          <strong>{t.deltaAIC}</strong>: {formatDelta(preset.analysis.delta_aic_best_null)} {t.against}
          {` ${formatLabel(preset.analysis.best_null_model)}, `}
          R²={formatNumber(preset.analysis.logistic_r2)}
        </span>
        <span>
          <strong>{t.impedance}</strong>: {preset.impedance.definition} (⟨ζ⟩={preset.impedance.mean.toFixed(3)})
        </span>
        <span>
          <strong>{t.controlParameter}</strong>: {preset.control_parameter}
        </span>
        <span>
          <strong>{t.orderParameter}</strong>: {preset.order_parameter}
        </span>
        {preset.references?.dataset ? (
          <span>
            <strong>{t.dataset}</strong>: <code>{preset.references.dataset}</code>
          </span>
        ) : null}
        <span>
          <strong>{t.analysisPath}</strong>: <code>{preset.analysis.result_path}</code>
        </span>
        {preset.references?.notes ? <span>{preset.references.notes}</span> : null}
      </div>
    </div>
  );
};
