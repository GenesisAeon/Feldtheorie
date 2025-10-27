import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import { Pause, Play, RotateCcw, Sparkles } from 'lucide-react';
import { DomainCard } from './DomainCard';
import { FEATURED_PRESETS, PRESETS } from '../presets';
import { DomainPreset, DomainState, TrajectoryPoint } from '../types';
import { clamp, logistic } from '../utils/logistic';

const BASE_THETA = 5;
const BASE_BETA = 4;

const computeStimulus = (time: number, preset: DomainPreset, noiseScale: number): number => {
  const { base, amplitude, frequency, noise, modulation } = preset.simulation.stimulus;
  const oscillation = amplitude * Math.sin(frequency * time);
  let modulationTerm = 0;
  if (modulation) {
    if (modulation.type === 'sin') {
      modulationTerm = modulation.amplitude * Math.sin(modulation.frequency * time * 0.85 + Math.PI / 6);
    } else {
      modulationTerm = modulation.amplitude * Math.tanh(modulation.frequency * (time - 1.2));
    }
  }
  const stochastic = noise * noiseScale * (Math.random() - 0.5);
  return base + oscillation + modulationTerm + stochastic;
};

interface ControlState {
  theta: number;
  beta: number;
  coupling: number;
  noiseScale: number;
}

export const TransdisciplinaryFieldSimulator = () => {
  const [controls, setControls] = useState<ControlState>({
    theta: BASE_THETA,
    beta: BASE_BETA,
    coupling: 0.78,
    noiseScale: 1
  });
  const [isRunning, setIsRunning] = useState(false);
  const [poeticMode, setPoeticMode] = useState(false);
  const [poeticMessage, setPoeticMessage] = useState('');
  const [time, setTime] = useState(0);
  const [crossResonance, setCrossResonance] = useState(0);
  const [activePresetIds, setActivePresetIds] = useState<string[]>(() => FEATURED_PRESETS.map((preset) => preset.id));

  const presetsById = useMemo(() => {
    const map = new Map<string, DomainPreset>();
    PRESETS.forEach((preset) => map.set(preset.id, preset));
    return map;
  }, []);

  const [domainStates, setDomainStates] = useState<Record<string, DomainState>>(() => {
    const initial: Record<string, DomainState> = {};
    activePresetIds.forEach((id) => {
      const preset = presetsById.get(id);
      if (preset) {
        initial[id] = {
          id,
          label: preset.label,
          R: preset.simulation.initial_R,
          psi: preset.simulation.initial_psi,
          phi: preset.simulation.initial_phi,
          zeta: preset.impedance.closed,
          gate: logistic(preset.simulation.initial_R, controls.theta, controls.beta),
          theta: controls.theta,
          beta: controls.beta,
          active: false
        };
      }
    });
    return initial;
  });

  const [trajectories, setTrajectories] = useState<Record<string, TrajectoryPoint[]>>(() => {
    const initial: Record<string, TrajectoryPoint[]> = {};
    activePresetIds.forEach((id) => {
      initial[id] = [];
    });
    return initial;
  });

  const animationRef = useRef<number>();
  const poeticTimerRef = useRef<number | null>(null);
  const timeRef = useRef<number>(0);
  const crossResonanceRef = useRef<number>(0);
  const stateRef = useRef<Record<string, DomainState>>(domainStates);
  const trajectoryRef = useRef<Record<string, TrajectoryPoint[]>>(trajectories);

  const createStateFromPreset = useCallback(
    (preset: DomainPreset): DomainState => ({
      id: preset.id,
      label: preset.label,
      R: preset.simulation.initial_R,
      psi: preset.simulation.initial_psi,
      phi: preset.simulation.initial_phi,
      zeta: preset.impedance.closed,
      gate: logistic(preset.simulation.initial_R, controls.theta, controls.beta),
      theta: controls.theta,
      beta: controls.beta,
      active: false
    }),
    [controls.beta, controls.theta]
  );

  useEffect(() => {
    stateRef.current = domainStates;
  }, [domainStates]);

  useEffect(() => {
    trajectoryRef.current = trajectories;
  }, [trajectories]);

  const resetSimulation = () => {
    timeRef.current = 0;
    crossResonanceRef.current = 0;
    setTime(0);
    setCrossResonance(0);
    const resetStates: Record<string, DomainState> = {};
    activePresetIds.forEach((id) => {
      const preset = presetsById.get(id);
      if (preset) {
        resetStates[id] = createStateFromPreset(preset);
      }
    });
    setDomainStates(resetStates);
    setTrajectories(() => {
      const map: Record<string, TrajectoryPoint[]> = {};
      activePresetIds.forEach((id) => {
        map[id] = [];
      });
      return map;
    });
  };

  const handleReset = () => {
    setIsRunning(false);
    resetSimulation();
    setPoeticMessage('');
    if (poeticTimerRef.current) {
      window.clearTimeout(poeticTimerRef.current);
      poeticTimerRef.current = null;
    }
  };

  useEffect(() => {
    if (!isRunning) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const step = () => {
      const dt = 0.08;
      const currentStates = stateRef.current;
      const nextStates: Record<string, DomainState> = {};
      const trajectoriesCopy: Record<string, TrajectoryPoint[]> = { ...trajectoryRef.current };

      let gateSum = 0;
      let psiSum = 0;
      let activeCount = 0;

      activePresetIds.forEach((id) => {
        const preset = presetsById.get(id);
        const previousState = currentStates[id] ?? createStateFromPreset(preset!);
        if (!preset) {
          return;
        }

        const thetaOffset = preset.simulation.theta - BASE_THETA;
        const betaScale = preset.simulation.beta / BASE_BETA;
        const effectiveTheta = controls.theta + thetaOffset;
        const effectiveBeta = clamp(controls.beta * betaScale, 0.5, 12);
        const gate = logistic(previousState.R, effectiveTheta, effectiveBeta);
        const stimulus = computeStimulus(timeRef.current, preset, controls.noiseScale);
        const crossTerm = crossResonanceRef.current * controls.coupling * 0.12;

        const dR = (stimulus + crossTerm) * dt - gate * previousState.R * 0.32 * dt;
        const newR = Math.max(0, previousState.R + dR);
        const dPsi = (-0.22 * previousState.psi + 0.48 * gate * newR + 0.28 * previousState.phi * newR) * dt;
        const newPsi = previousState.psi + dPsi + 0.08 * controls.noiseScale * (Math.random() - 0.5);
        const dPhi = (0.14 * newPsi - 0.18 * previousState.phi + 0.26 * gate) * dt;
        const newPhi = Math.max(0, previousState.phi + dPhi);
        const zeta = preset.impedance.closed - (preset.impedance.closed - preset.impedance.open) * gate;
        const crossed = previousState.R < effectiveTheta && newR >= effectiveTheta;

        if (poeticMode && crossed && preset.poetic_messages.length > 0) {
          const message = preset.poetic_messages[Math.floor(Math.random() * preset.poetic_messages.length)];
          setPoeticMessage(message);
          if (poeticTimerRef.current) {
            window.clearTimeout(poeticTimerRef.current);
          }
          poeticTimerRef.current = window.setTimeout(() => {
            setPoeticMessage('');
            poeticTimerRef.current = null;
          }, 3200);
        }

        const updatedState: DomainState = {
          id,
          label: preset.label,
          R: newR,
          psi: newPsi,
          phi: newPhi,
          zeta,
          gate,
          theta: effectiveTheta,
          beta: effectiveBeta,
          active: gate > 0.52
        };

        nextStates[id] = updatedState;

        const trajectory = trajectoriesCopy[id] ?? [];
        trajectory.push({ time: timeRef.current, value: newR });
        if (trajectory.length > 260) {
          trajectory.shift();
        }
        trajectoriesCopy[id] = trajectory;

        gateSum += gate;
        psiSum += Math.max(newPsi, 0);
        activeCount += 1;
      });

      const newCross = activeCount > 0 ? (gateSum / activeCount) * (psiSum / activeCount) : 0;
      crossResonanceRef.current = newCross;
      setCrossResonance(newCross);
      setDomainStates(nextStates);
      setTrajectories(trajectoriesCopy);

      const newTime = timeRef.current + dt;
      timeRef.current = newTime;
      setTime(newTime);

      animationRef.current = requestAnimationFrame(step);
    };

    animationRef.current = requestAnimationFrame(step);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRunning, controls, activePresetIds, createStateFromPreset, poeticMode, presetsById]);

  useEffect(() => {
    setDomainStates((prev) => {
      const next: Record<string, DomainState> = {};
      activePresetIds.forEach((id) => {
        if (prev[id]) {
          next[id] = prev[id];
        } else {
          const preset = presetsById.get(id);
          if (preset) {
            next[id] = createStateFromPreset(preset);
          }
        }
      });
      return next;
    });
    setTrajectories((prev) => {
      const next: Record<string, TrajectoryPoint[]> = {};
      activePresetIds.forEach((id) => {
        next[id] = prev[id] ?? [];
      });
      return next;
    });
  }, [activePresetIds, createStateFromPreset, presetsById]);

  const toggleDomain = (id: string) => {
    setActivePresetIds((prev) => {
      if (prev.includes(id)) {
        if (prev.length === 1) {
          return prev;
        }
        return prev.filter((entry) => entry !== id);
      }
      return [...prev, id];
    });
  };

  const activePresets = useMemo(
    () => activePresetIds.map((id) => presetsById.get(id)).filter((preset): preset is DomainPreset => Boolean(preset)),
    [activePresetIds, presetsById]
  );

  const chartLines = activePresets.map((preset) => (
    <Line
      key={preset.id}
      data={trajectories[preset.id]}
      type="monotone"
      dataKey="value"
      stroke={preset.color}
      dot={false}
      strokeWidth={2}
      name={preset.label}
    />
  ));

  return (
    <div className="card-surface" style={{ padding: '1.5rem', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '1.5rem' }}>
        <h1 className="glow-header" style={{ fontSize: '2.4rem', fontWeight: 700, margin: 0 }}>
          Transdisziplinärer Schwellenfeld-Simulator
        </h1>
        <p style={{ color: 'rgba(226,232,255,0.75)', marginTop: '0.35rem' }}>
          Universal Threshold Field · gekoppelte Membranen für Schwarze Löcher, Bienenschwärme und Sprachmodelle.
        </p>
        <p style={{ color: 'rgba(196,181,253,0.75)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
          Regler beeinflussen das universelle Quartett (R, Θ, β, ζ(R)). Nullmodelle und Datenpfade sind in jeder Karte verankert.
        </p>
      </header>

      {poeticMessage && (
        <div className="poetic-banner">
          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            <Sparkles size={20} />
            <p>{poeticMessage}</p>
          </div>
        </div>
      )}

      <section className="control-panel">
        <div className="card-surface" style={{ padding: '1rem', background: 'rgba(14,10,35,0.6)' }}>
          <h2 className="section-title">Universal-Parameter</h2>
          <div className="parameter-row">
            <label>
              Θ (kritischer Schwellenwert)
              <span>{controls.theta.toFixed(2)}</span>
            </label>
            <input
              className="slider-track"
              type="range"
              min="3"
              max="7"
              step="0.1"
              value={controls.theta}
              onChange={(event) => setControls((prev) => ({ ...prev, theta: Number(event.target.value) }))}
            />
          </div>
          <div className="parameter-row">
            <label>
              β (Steilheit)
              <span>{controls.beta.toFixed(2)}</span>
            </label>
            <input
              className="slider-track"
              type="range"
              min="2"
              max="8"
              step="0.1"
              value={controls.beta}
              onChange={(event) => setControls((prev) => ({ ...prev, beta: Number(event.target.value) }))}
            />
          </div>
          <div className="parameter-row">
            <label>
              Kopplung Γ
              <span>{controls.coupling.toFixed(2)}</span>
            </label>
            <input
              className="slider-track"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={controls.coupling}
              onChange={(event) => setControls((prev) => ({ ...prev, coupling: Number(event.target.value) }))}
            />
          </div>
          <div className="parameter-row">
            <label>
              Rauschskalierung
              <span>{controls.noiseScale.toFixed(2)}</span>
            </label>
            <input
              className="slider-track"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={controls.noiseScale}
              onChange={(event) => setControls((prev) => ({ ...prev, noiseScale: Number(event.target.value) }))}
            />
          </div>
        </div>

        <div className="card-surface" style={{ padding: '1rem', background: 'rgba(14,10,35,0.6)' }}>
          <h2 className="section-title">Steuerung</h2>
          <div className="button-row">
            <button className="button primary" onClick={() => setIsRunning((prev) => !prev)}>
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
              {isRunning ? 'Pause' : 'Start'}
            </button>
            <button className="button secondary" onClick={handleReset}>
              <RotateCcw size={16} />
              Reset
            </button>
            <button
              className={`button ghost ${poeticMode ? 'active' : ''}`}
              onClick={() => setPoeticMode((prev) => !prev)}
            >
              <Sparkles size={16} /> Poetisch
            </button>
          </div>
          <div style={{ marginTop: '1rem', color: 'rgba(226,232,255,0.75)', fontSize: '0.9rem' }}>
            <div>Zeit: {time.toFixed(1)} s</div>
            <div>Cross-Resonanz: {crossResonance.toFixed(3)}</div>
          </div>
        </div>
      </section>

      <section className="domain-controls">
        {PRESETS.map((preset) => (
          <button
            key={preset.id}
            className={`domain-toggle ${activePresetIds.includes(preset.id) ? 'active' : ''}`}
            onClick={() => toggleDomain(preset.id)}
            style={{ borderColor: preset.color, color: preset.color }}
          >
            {preset.label}
          </button>
        ))}
      </section>

      <section className="domain-grid" style={{ marginTop: '1.5rem' }}>
        {activePresets.map((preset) => {
          const state = domainStates[preset.id];
          const thetaOffset = preset.simulation.theta - BASE_THETA;
          const betaScale = preset.simulation.beta / BASE_BETA;
          const currentTheta = controls.theta + thetaOffset;
          const currentBeta = clamp(controls.beta * betaScale, 0.5, 12);
          return state ? (
            <DomainCard key={preset.id} preset={preset} state={state} currentTheta={currentTheta} currentBeta={currentBeta} />
          ) : null;
        })}
      </section>

      <section className="chart-wrapper">
        <h2 className="section-title">Reservoir-Dynamik R(t)</h2>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="4 4" stroke="rgba(99,102,241,0.35)" />
            <XAxis dataKey="time" stroke="rgba(209,213,255,0.65)" type="number" domain={['dataMin', 'dataMax']} />
            <YAxis stroke="rgba(209,213,255,0.65)" domain={[0, 'auto']} />
            <Tooltip
              contentStyle={{ background: 'rgba(17,16,35,0.9)', border: '1px solid rgba(129,140,248,0.45)', borderRadius: '12px' }}
            />
            <Legend />
            <ReferenceLine y={controls.theta} stroke="#f87171" strokeDasharray="6 4" label="Θ" />
            {chartLines}
          </LineChart>
        </ResponsiveContainer>
        <p className="meta-footnote">
          Linien zeigen den Verlauf des Ordnungsparameters R pro Domäne. Der rote Strich markiert die aktuelle Schwelle Θ; sobald
          die Kurven darüber hinaussteigen, öffnet sich die Membran (σ(β(R-Θ)) → 1) und der Poetik-Modus meldet die Resonanz.
        </p>
      </section>

      <footer className="meta-footnote">
        Simulator-Version verknüpft Analyse-Pfade aus `analysis/results/*.json` mit den hier angezeigten Karten. ΔAIC- und R²-Werte
        stammen direkt aus den Falsifikationsroutinen; Anpassungen an den Reglern sollten immer gegen die Nullmodelle im Blick
        behalten werden.
      </footer>
    </div>
  );
};
