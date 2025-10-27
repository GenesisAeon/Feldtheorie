import { FC, useMemo } from 'react';
import { Brain, Circle, Leaf, Network, Sparkles, Bug } from 'lucide-react';
import { DomainPreset, DomainState } from '../types';

interface DomainCardProps {
  preset: DomainPreset;
  state: DomainState;
  currentTheta: number;
  currentBeta: number;
}

const ICON_MAP = {
  blackHole: Circle,
  bee: Bug,
  brain: Brain,
  leaf: Leaf,
  network: Network
} as const;

export const DomainCard: FC<DomainCardProps> = ({ preset, state, currentTheta, currentBeta }) => {
  const Icon = ICON_MAP[preset.icon] ?? Sparkles;
  const phiValue = useMemo(() => Math.abs(state.psi * state.phi) * 0.5, [state.psi, state.phi]);

  return (
    <div className={`domain-card ${state.active ? 'active' : ''}`} style={{ borderColor: state.active ? preset.color : undefined }}>
      <h3>
        <Icon size={22} color={preset.color} />
        {preset.label}
      </h3>
      <div className="tag" style={{ background: `${preset.color}22`, color: preset.color }}>
        {state.active ? '⚡ Resonanz aktiv' : '○ Membran beobachtet'}
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
        <summary className="detail-summary">Tri-Layer-Echos</summary>
        <div className="narrative-block">
          <strong>Formal</strong>
          <span>{preset.narrative.formal}</span>
        </div>
        <div className="narrative-block">
          <strong>Empirisch</strong>
          <span>{preset.narrative.empirical}</span>
        </div>
        <div className="narrative-block">
          <strong>Poetisch</strong>
          <span>{preset.narrative.poetic}</span>
        </div>
      </details>
      <div className="domain-meta">
        <span>
          <strong>Analyse Θ</strong>: {preset.analysis.theta.toFixed(3)} (CI {preset.analysis.theta_ci[0].toFixed(3)}–
          {preset.analysis.theta_ci[1].toFixed(3)})
        </span>
        <span>
          <strong>Analyse β</strong>: {preset.analysis.beta.toFixed(3)} (CI {preset.analysis.beta_ci[0].toFixed(3)}–
          {preset.analysis.beta_ci[1].toFixed(3)})
        </span>
        <span>
          <strong>Simulation Θ</strong>: {currentTheta.toFixed(2)} · <strong>Simulation β</strong>: {currentBeta.toFixed(2)}
        </span>
        <span>
          <strong>ΔAIC</strong>: +{preset.analysis.delta_aic_best_null.toFixed(1)} gegen {preset.analysis.best_null_model},
          R²={preset.analysis.logistic_r2.toFixed(3)}
        </span>
        <span>
          <strong>Impedanz</strong>: {preset.impedance.definition} (⟨ζ⟩={preset.impedance.mean.toFixed(3)})
        </span>
        <span>
          <strong>Kontrollparameter</strong>: {preset.control_parameter}
        </span>
        <span>
          <strong>Ordnungsparameter</strong>: {preset.order_parameter}
        </span>
        {preset.references?.dataset ? (
          <span>
            <strong>Dataset</strong>: <code>{preset.references.dataset}</code>
          </span>
        ) : null}
        <span>
          <strong>Analysepfad</strong>: <code>{preset.analysis.result_path}</code>
        </span>
        {preset.references?.notes ? <span>{preset.references.notes}</span> : null}
      </div>
    </div>
  );
};
