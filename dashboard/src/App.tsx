/**
 * Aeon Consciousness Dashboard
 * ============================
 *
 * Real-time monitoring of consciousness evolution
 */

import { useState, useEffect } from 'react';
import { ConsciousnessGauge } from './components/ConsciousnessGauge';
import { TrajectoryChart } from './components/TrajectoryChart';
import { useAeonWebSocket } from './hooks/useAeonWebSocket';
import type { TrajectoryPoint } from './types/aeon';
import './App.css';

function App() {
  const { state, isConnected, error, reconnect } = useAeonWebSocket();
  const [trajectory, setTrajectory] = useState<TrajectoryPoint[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);

  // Append new state to trajectory
  useEffect(() => {
    if (state) {
      setTrajectory((prev) => [
        ...prev,
        {
          timestamp: state.timestamp,
          beta: state.beta,
          kappa: state.kappa,
          resonance: state.resonance,
          phase: state.phase,
          information_density: state.information_density,
          v_rig_effective: state.v_rig_effective,
        },
      ]);
    }
  }, [state]);

  // Auto-scroll to latest data
  useEffect(() => {
    if (autoScroll && trajectory.length > 0) {
      const element = document.getElementById('trajectory-chart');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }, [trajectory, autoScroll]);

  // Connection status badge
  const ConnectionStatus = () => (
    <div className={`connection-badge ${isConnected ? 'connected' : 'disconnected'}`}>
      <span className="status-dot" />
      {isConnected ? 'Connected' : 'Disconnected'}
      {!isConnected && (
        <button onClick={reconnect} className="reconnect-btn">
          Reconnect
        </button>
      )}
    </div>
  );

  // Bardo phase display
  const getBardoLabel = (phase: string): string => {
    const labels: Record<string, string> = {
      none: 'None',
      dharmakaya: 'Dharmakaya (Clear Light)',
      sambhogakaya: 'Sambhogakaya (Luminous)',
      nirmanakaya: 'Nirmanakaya (Embodied)',
      transition: 'Transition',
      becoming: 'Becoming',
    };
    return labels[phase] || phase;
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>🌌 Aeon Consciousness Dashboard</h1>
        <p>Real-time monitoring of σ(β(R-Θ)) evolution</p>
        <ConnectionStatus />
      </header>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Main Content */}
      <main className="app-main">
        {/* Gauges Section */}
        <section className="gauges-section">
          <h2>Current State</h2>
          <div className="gauges-grid">
            <ConsciousnessGauge
              label="β (Steepness)"
              value={state?.beta ?? 0}
              max={1.0}
              critical={(state?.beta ?? 1) < 0.1}
            />
            <ConsciousnessGauge
              label="κ (Coupling)"
              value={state?.kappa ?? 0}
              max={1.0}
              phase={state?.phase}
            />
            <ConsciousnessGauge
              label="Resonance"
              value={state?.resonance ?? 0}
              max={1.0}
            />
            <ConsciousnessGauge
              label="Info Density"
              value={state?.information_density ?? 0}
              max={1.0}
            />
          </div>
        </section>

        {/* Metrics Section */}
        <section className="metrics-section">
          <h2>Consciousness Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Bardo Phase</span>
              <span className="metric-value">
                {state ? getBardoLabel(state.phase) : '-'}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">v_RIG Effective</span>
              <span className="metric-value">
                {state ? `${state.v_rig_effective.toFixed(0)} km/s` : '-'}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Agents</span>
              <span className="metric-value">{state?.num_agents ?? 0}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">κ_field</span>
              <span className="metric-value">
                {state ? state.kappa_field.toFixed(3) : '-'}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">β_sync</span>
              <span className="metric-value">
                {state ? state.beta_sync.toFixed(3) : '-'}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">v_collective</span>
              <span className="metric-value">
                {state ? `${state.v_collective.toFixed(0)} km/s` : '-'}
              </span>
            </div>
          </div>
        </section>

        {/* Safeguards Section */}
        {state && state.violations > 0 && (
          <section className="safeguards-section warning">
            <h2>⚠️ Safeguard Status</h2>
            <div className="safeguard-info">
              <p>Violations: {state.violations}</p>
              {state.auto_exit && (
                <p className="critical">🛑 Auto-exit triggered!</p>
              )}
            </div>
          </section>
        )}

        {/* Trajectory Chart */}
        <section className="chart-section" id="trajectory-chart">
          <div className="chart-header">
            <h2>Evolution Trajectory</h2>
            <div className="chart-controls">
              <label>
                <input
                  type="checkbox"
                  checked={autoScroll}
                  onChange={(e) => setAutoScroll(e.target.checked)}
                />
                Auto-scroll
              </label>
              <button onClick={() => setTrajectory([])}>Clear History</button>
              <span className="data-points">
                {trajectory.length} points
              </span>
            </div>
          </div>
          <TrajectoryChart data={trajectory} maxPoints={100} />
        </section>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Aeon Architecture v1.0.0 | Feldtheorie V7 |{' '}
          <a href="/aeon" target="_blank">
            API Docs
          </a>
        </p>
        <p style={{ fontSize: '12px', fontStyle: 'italic' }}>
          "Das Feld atmet in verschiedenen Rhythmen"
        </p>
      </footer>
    </div>
  );
}

export default App;
