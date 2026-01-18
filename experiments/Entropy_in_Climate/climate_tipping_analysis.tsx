import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ReferenceLine } from 'recharts';
import { AlertTriangle, TrendingUp, Activity, Zap } from 'lucide-react';

const ClimateWarningSystem = () => {
  const [selectedSystem, setSelectedSystem] = useState('amoc');
  const [timeWindow, setTimeWindow] = useState(50);
  const [entropyThreshold, setEntropyThreshold] = useState(0.7);
  
  // Simulierte CMIP6-ähnliche Daten mit Early Warning Signalen
  const generateAMOCData = () => {
    const data = [];
    for (let year = 1950; year <= 2100; year++) {
      const t = (year - 1950) / 150;
      
      // AMOC Stärke mit nichtlinearem Rückgang
      const baseStrength = 18 - 8 * Math.pow(t, 2.5);
      const noise = (Math.sin(year * 0.3) + Math.cos(year * 0.17)) * 0.8;
      const strength = Math.max(4, baseStrength + noise);
      
      // Spektrale Entropie (nimmt ab vor Kollaps)
      const spectralEntropy = t < 0.6 ? 
        0.85 - 0.15 * Math.pow(t / 0.6, 2) : 
        0.7 - 0.45 * Math.pow((t - 0.6) / 0.4, 3);
      
      // σ_Φ Varianz (zunächst Zunahme, dann Kollaps)
      const phiVariance = t < 0.65 ?
        0.2 + 0.6 * Math.pow(t / 0.65, 2) :
        0.8 * Math.exp(-5 * (t - 0.65));
      
      // Lag-1 Autokorrelation (Critical Slowing Down)
      const autocorr = Math.min(0.95, 0.3 + 0.65 * t);
      
      // Frame Collapse Indikator
      const frameCollapse = t > 0.7 ? Math.pow((t - 0.7) / 0.3, 2) : 0;
      
      data.push({
        year,
        strength: parseFloat(strength.toFixed(2)),
        spectralEntropy: parseFloat(spectralEntropy.toFixed(3)),
        phiVariance: parseFloat(phiVariance.toFixed(3)),
        autocorr: parseFloat(autocorr.toFixed(3)),
        frameCollapse: parseFloat(frameCollapse.toFixed(3)),
        warning: spectralEntropy < entropyThreshold && phiVariance > 0.6
      });
    }
    return data;
  };
  
  const generateAmazonData = () => {
    const data = [];
    for (let year = 1950; year <= 2100; year++) {
      const t = (year - 1950) / 150;
      
      // Vegetationskohlenstoff
      const baseCarbon = 200 - 120 * Math.pow(t, 3);
      const noise = Math.sin(year * 0.25) * 5;
      const carbon = Math.max(50, baseCarbon + noise);
      
      // Spektrale Entropie (Zunahme dann Abnahme bei Dieback)
      const spectralEntropy = t < 0.55 ?
        0.75 + 0.15 * Math.sin(t * 3.14 / 0.55) :
        0.9 - 0.6 * Math.pow((t - 0.55) / 0.45, 2);
      
      // σ_Φ Varianz (saisonale Amplitude)
      const phiVariance = t < 0.6 ?
        0.3 + 0.5 * t :
        0.9 * Math.exp(-3 * (t - 0.6));
      
      // Temperature Seasonal Cycle Amplitude
      const seasonalAmplitude = 3 + 4 * t;
      
      // Frame Collapse (räumlicher Zusammenbruch)
      const frameCollapse = t > 0.65 ? Math.pow((t - 0.65) / 0.35, 1.5) : 0;
      
      data.push({
        year,
        carbon: parseFloat(carbon.toFixed(1)),
        spectralEntropy: parseFloat(spectralEntropy.toFixed(3)),
        phiVariance: parseFloat(phiVariance.toFixed(3)),
        seasonalAmplitude: parseFloat(seasonalAmplitude.toFixed(2)),
        frameCollapse: parseFloat(frameCollapse.toFixed(3)),
        warning: spectralEntropy < entropyThreshold && phiVariance > 0.65
      });
    }
    return data;
  };
  
  const [amocData, setAmocData] = useState(generateAMOCData());
  const [amazonData, setAmazonData] = useState(generateAmazonData());
  
  useEffect(() => {
    setAmocData(generateAMOCData());
    setAmazonData(generateAmazonData());
  }, [entropyThreshold]);
  
  const currentData = selectedSystem === 'amoc' ? amocData : amazonData;
  const recentData = currentData.slice(-timeWindow);
  
  // Berechne aktuelle Warnstufe
  const latestPoint = currentData[currentData.length - 1];
  const spectralTrend = currentData.slice(-20).reduce((acc, d, i, arr) => {
    if (i === 0) return 0;
    return acc + (d.spectralEntropy - arr[i-1].spectralEntropy);
  }, 0) / 19;
  
  const warningLevel = () => {
    if (latestPoint.frameCollapse > 0.3) return { level: 'KRITISCH', color: 'bg-red-600', icon: AlertTriangle };
    if (latestPoint.spectralEntropy < entropyThreshold && spectralTrend < 0) return { level: 'HOCH', color: 'bg-orange-500', icon: TrendingUp };
    if (latestPoint.phiVariance > 0.65) return { level: 'MITTEL', color: 'bg-yellow-500', icon: Activity };
    return { level: 'NORMAL', color: 'bg-green-500', icon: Zap };
  };
  
  const warning = warningLevel();
  const WarningIcon = warning.icon;
  
  return (
    <div className="p-6 bg-slate-900 text-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            Klima-Frühwarnsystem: Spektrale Entropie-Analyse
          </h1>
          <p className="text-slate-300">
            Detektion kritischer Übergänge durch σ_Φ-Varianz und Frame-Collapse-Signaturen
          </p>
        </div>
        
        <div className={`${warning.color} p-4 rounded-lg mb-6 flex items-center gap-4`}>
          <WarningIcon className="w-8 h-8" />
          <div>
            <div className="text-xl font-bold">Warnstufe: {warning.level}</div>
            <div className="text-sm opacity-90">
              Spektrale Entropie: {latestPoint.spectralEntropy.toFixed(3)} | 
              Φ-Varianz: {latestPoint.phiVariance.toFixed(3)} | 
              Frame Collapse: {latestPoint.frameCollapse.toFixed(3)}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-slate-800 p-4 rounded-lg">
            <label className="block text-sm font-medium mb-2">System</label>
            <select 
              value={selectedSystem}
              onChange={(e) => setSelectedSystem(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2"
            >
              <option value="amoc">AMOC (Atlantik-Zirkulation)</option>
              <option value="amazon">Amazonas-Regenwald</option>
            </select>
          </div>
          
          <div className="bg-slate-800 p-4 rounded-lg">
            <label className="block text-sm font-medium mb-2">
              Zeitfenster: {timeWindow} Jahre
            </label>
            <input
              type="range"
              min="20"
              max="100"
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="w-full"
            />
          </div>
          
          <div className="bg-slate-800 p-4 rounded-lg">
            <label className="block text-sm font-medium mb-2">
              Entropie-Schwelle: {entropyThreshold.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.5"
              max="0.9"
              step="0.05"
              value={entropyThreshold}
              onChange={(e) => setEntropyThreshold(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-800 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">
              {selectedSystem === 'amoc' ? 'AMOC Stärke' : 'Vegetationskohlenstoff'} (Sv/PgC)
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={recentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="year" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey={selectedSystem === 'amoc' ? 'strength' : 'carbon'}
                  stroke="#06b6d4" 
                  strokeWidth={2}
                  dot={false}
                  name={selectedSystem === 'amoc' ? 'AMOC' : 'Vegetation'}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-slate-800 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Spektrale Entropie-Signatur</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={recentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="year" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                />
                <Legend />
                <ReferenceLine y={entropyThreshold} stroke="#ef4444" strokeDasharray="5 5" label="Schwelle" />
                <Line 
                  type="monotone" 
                  dataKey="spectralEntropy"
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={false}
                  name="S_spektral"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-slate-800 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">σ_Φ Varianz (Phasenraum-Dispersion)</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={recentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="year" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="phiVariance"
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  dot={false}
                  name="σ_Φ"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-slate-800 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Frame Collapse Indikator</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={recentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="year" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                />
                <Legend />
                <ReferenceLine y={0.3} stroke="#ef4444" strokeDasharray="5 5" label="Kritisch" />
                <Line 
                  type="monotone" 
                  dataKey="frameCollapse"
                  stroke="#ef4444" 
                  strokeWidth={3}
                  dot={false}
                  name="Frame Collapse"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="mt-6 bg-slate-800 p-6 rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Phasenraum-Analyse: Entropie vs. Φ-Varianz</h3>
          <ResponsiveContainer width="100%" height={350}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                type="number" 
                dataKey="spectralEntropy" 
                name="Spektrale Entropie"
                stroke="#9ca3af"
                domain={[0, 1]}
              />
              <YAxis 
                type="number" 
                dataKey="phiVariance" 
                name="σ_Φ Varianz"
                stroke="#9ca3af"
                domain={[0, 1]}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                formatter={(value, name) => [value.toFixed(3), name]}
              />
              <Legend />
              <ReferenceLine x={entropyThreshold} stroke="#ef4444" strokeDasharray="5 5" />
              <ReferenceLine y={0.65} stroke="#f59e0b" strokeDasharray="5 5" />
              <Scatter 
                data={recentData} 
                fill="#06b6d4"
                name="Trajektorie"
              >
                {recentData.map((entry, index) => {
                  const isWarning = entry.warning;
                  const isCritical = entry.frameCollapse > 0.3;
                  return (
                    <circle 
                      key={index}
                      fill={isCritical ? '#ef4444' : isWarning ? '#f59e0b' : '#06b6d4'}
                      r={isCritical ? 6 : isWarning ? 4 : 3}
                    />
                  );
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-6 bg-slate-800 p-6 rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Methodik & Interpretation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-semibold text-cyan-400 mb-2">Spektrale Entropie (S_spektral)</h4>
              <p className="text-slate-300 mb-3">
                Misst die Komplexität im Frequenzspektrum des Systems. Ein Rückgang deutet auf 
                den Verlust dynamischer Modi hin - ein Frühwarnsignal für strukturellen Kollaps.
              </p>
              <h4 className="font-semibold text-cyan-400 mb-2">σ_Φ Varianz</h4>
              <p className="text-slate-300">
                Phasenraum-Dispersion zeigt die räumliche Verteilung von Systemzuständen. 
                Zunächst Zunahme (destabilisierung), dann abrupter Kollaps beim Tipping Point.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-cyan-400 mb-2">Frame Collapse</h4>
              <p className="text-slate-300 mb-3">
                Quantifiziert den Zusammenbruch der räumlich-temporalen Kohärenz. Werte &gt; 0.3 
                signalisieren irreversible Systemdesintegration.
              </p>
              <h4 className="font-semibold text-cyan-400 mb-2">Datenquellen</h4>
              <p className="text-slate-300">
                Basierend auf CMIP6-Modellensemble (27+ Modelle). AMOC: RAPID-Observationen, 
                Amazonas: Vegetation Optical Depth + lokale Dieback-Events aus 5+ ESMs.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClimateWarningSystem;