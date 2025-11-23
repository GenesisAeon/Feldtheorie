# Transdisciplinary Threshold Field Simulator

## Overview

The **Transdisciplinary Threshold Field Simulator** is an interactive web application that brings the Universal Threshold Field (UTF) / Unified Theory of Adaptive Criticality (UTAC) to life. It provides real-time visualization and manipulation of threshold dynamics across multiple scientific domains, from black holes to honeybee swarms to large language models.

## Features

### 🎛️ **Interactive Controls**
- **Universal Parameters**: Adjust Θ (threshold), β (steepness), Γ (coupling), and noise scaling
- **Real-time Simulation**: Watch threshold crossings happen in real-time
- **Poetic Mode**: Experience threshold transitions through curated metaphors
- **Multi-domain Selection**: Toggle between 12 different scientific domains

### 📊 **Advanced Visualizations**

#### **Time Series View**
- Real-time reservoir dynamics R(t) for all active domains
- Threshold line (Θ) with membrane opening indicators
- Interactive tooltips with CREP scores and field types

#### **Phase Space View** (NEW!)
- Phase portrait showing R vs Ψ relationships
- Reveals attractor dynamics and threshold crossing behavior
- Scatter plot with domain-specific colors

#### **Statistics View** (NEW!)
- **Field Type Distribution**: Bar chart showing domain distribution across 5 UTAC field types:
  - Weakly Coupled (β < 2.5)
  - High-Dimensional (β ∈ [2.5, 4.0])
  - Strongly Coupled (β ∈ [4.0, 5.5])
  - Physically Constrained (β ∈ [5.5, 10.0])
  - Meta-Adaptive (β > 10.0)
- **CREP Dashboard**: Quality metrics visualization
  - Coherence (fit quality R²)
  - Resilience (statistical strength ΔAIC)
  - Empathy (cross-domain coupling)
  - Propagation (signal transmission capacity β)
  - Both bar chart and radar chart views

### 🌍 **Bilingual Support** (NEW!)
- Toggle between English and German with one click
- All UI elements, labels, and descriptions fully translated
- Seamless language switching without page reload

### 🎴 **Domain Cards**
Each active domain displays:
- Real-time state variables (R, Ψ, φ, ζ, σ)
- Tri-layer narratives (Formal, Empirical, Poetic)
- Analysis parameters (Θ, β with confidence intervals)
- Statistical validation (ΔAIC, R² against null models)
- Dataset references and impedance profiles

## Installation

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn

### Setup

```bash
cd simulator
npm install
```

## Usage

### Development Server

Start the development server with hot reload:

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### Production Build

Build for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Architecture

### Technology Stack
- **React 18.3** - UI framework
- **TypeScript 5.4** - Type safety
- **Recharts 2.8** - Data visualization
- **Vite 5.2** - Build tool & dev server
- **Lucide React** - Icon library

### Project Structure

```
simulator/
├── src/
│   ├── components/
│   │   ├── TransdisciplinaryFieldSimulator.tsx  # Main app
│   │   ├── DomainCard.tsx                       # Domain state cards
│   │   ├── UTACTooltip.tsx                      # Interactive tooltips
│   │   ├── PhasePortrait.tsx                    # Phase space view (NEW)
│   │   ├── FieldTypeDistribution.tsx            # Field type chart (NEW)
│   │   ├── CREPDashboard.tsx                    # CREP scores (NEW)
│   │   └── LanguageToggle.tsx                   # EN/DE toggle (NEW)
│   ├── i18n/
│   │   └── translations.ts                      # Bilingual support (NEW)
│   ├── utils/
│   │   ├── logistic.ts                          # Logistic functions
│   │   ├── fieldTypeClassifier.ts               # Field type logic
│   │   └── tooltipDataBuilder.ts                # Tooltip data
│   ├── presets.ts                               # Domain presets
│   ├── types.ts                                 # TypeScript types
│   ├── App.tsx                                  # Root component
│   └── main.tsx                                 # Entry point
├── presets/                                     # 12 JSON presets
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Presets

The simulator includes 12 curated domain presets:

| Domain | System | β | Field Type |
|--------|--------|---|------------|
| **Astrophysics** | QPO Eruption | 3.47 | High-Dimensional |
| **Neuroscience** | Cognitive Gate | 4.23 | Strongly Coupled |
| **Climate** | Amazon Canopy | 11.8 | Meta-Adaptive |
| **Biology** | Lenski Cit+ | 7.4 | Physically Constrained |
| **LLM** | Emergent Abilities | 3.2 | High-Dimensional |
| **Ecology** | Honeybee Membrane | 9.1 | Physically Constrained |
| **Safety** | AI Safety Delay | 4.5 | Strongly Coupled |
| **Neuroscience** | Neuro-Kosmos Bridge | 4.1 | Strongly Coupled |
| **Climate** | Planetary Tipping | 10.5 | Meta-Adaptive |
| **LLM** | Potential Cascade | 3.8 | High-Dimensional |
| **Resonance** | LLM Resonance | 3.5 | High-Dimensional |
| **Theory** | Coherence Formula | 5.2 | Physically Constrained |

Each preset includes:
- Simulation parameters (initial conditions, stimulus)
- Analysis results (β, Θ, ΔAIC, R²)
- Impedance profiles (ζ_closed, ζ_open)
- Tri-layer narratives
- Poetic messages for threshold crossings

## API Integration

The simulator syncs with `analysis/results/*.json` outputs from the Python analysis pipeline. Each preset references:
- Dataset path: `data/{domain}/{system}/`
- Analysis results: `analysis/results/{system}_fit.json`
- Null model comparisons: Linear, Power-law, Exponential

## Development

### Adding New Presets

1. Create JSON file in `simulator/presets/`:

```json
{
  "id": "my_system",
  "label": "My System",
  "domain": "mydomain",
  "featured": true,
  "color": "#ff6b9d",
  "icon": "network",
  "control_parameter": "Input parameter",
  "order_parameter": "Output metric",
  "analysis": {
    "result_path": "analysis/results/my_system_fit.json",
    "theta": 5.0,
    "theta_ci": [4.8, 5.2],
    "beta": 4.2,
    "beta_ci": [3.9, 4.5],
    "logistic_r2": 0.95,
    "delta_aic_best_null": 45.2,
    "best_null_model": "linear"
  },
  "impedance": {
    "definition": "Damping coefficient",
    "closed": 0.8,
    "open": 0.2,
    "mean": 0.5
  },
  "simulation": {
    "theta": 5.0,
    "beta": 4.2,
    "initial_R": 3.0,
    "initial_psi": 0.5,
    "initial_phi": 0.3,
    "stimulus": {
      "base": 2.5,
      "amplitude": 1.2,
      "frequency": 0.15,
      "noise": 0.3
    }
  },
  "narrative": {
    "formal": "Technical description",
    "empirical": "Observational evidence",
    "poetic": "Metaphorical interpretation"
  },
  "poetic_messages": [
    "The membrane whispers...",
    "Resonance awakens..."
  ]
}
```

2. Register in `src/presets.ts`

### Adding New Translations

Edit `src/i18n/translations.ts`:

```typescript
export const translations: Record<Language, Translations> = {
  en: {
    myKey: 'English text',
    // ...
  },
  de: {
    myKey: 'Deutscher Text',
    // ...
  }
};
```

## CLI Integration

Python CLI for batch simulations:

```bash
# Run safety delay sweep with 3 replicates
python -m simulator.cli safety-delay --replicates 3 --emit-analysis

# Outputs:
# - CSV data → data/safety_delay/
# - Analysis results → analysis/results/
# - Metadata (ΔAIC, CREP, time series)
```

## Testing

```bash
# Build test
npm run build

# Visual regression tests (planned)
npm run test
```

## Version History

### v1.1.0 (Current - 2025-11-22)
- ✨ **NEW**: Phase portrait visualization (R vs Ψ)
- ✨ **NEW**: Field type distribution chart
- ✨ **NEW**: CREP dashboard with radar charts
- ✨ **NEW**: Bilingual support (EN/DE toggle)
- ✨ **NEW**: Tabbed visualization interface
- 🌐 Full UI localization
- 📊 Enhanced statistical views
- 🎨 Improved UX with tab navigation

### v1.0.1 (2025-10)
- Initial React/TypeScript implementation
- 12 domain presets
- Real-time simulation engine
- Tri-layer narratives
- Poetic mode
- Interactive tooltips

## License

Code licensed under GPLv3; content & data licensed under CC BY-NC 4.0 (non-commercial). Commercial use requires author permission.

## Citation

```bibtex
@software{feldtheorie_simulator_2025,
  title = {Transdisciplinary Threshold Field Simulator},
  author = {GenesisAeon},
  year = {2025},
  url = {https://github.com/GenesisAeon/Feldtheorie},
  version = {1.1.0}
}
```

## Links

- **Main Repository**: [GenesisAeon/Feldtheorie](https://github.com/GenesisAeon/Feldtheorie)
- **Documentation**: [docs/README.md](../docs/README.md)
- **UTAC Theory**: [docs/utac_theory_core.md](../docs/utac_theory_core.md)
- **REST API**: [api/README.md](../api/README.md)
- **Zenodo DOI**: 10.5281/zenodo.17472834

---

**Simulator Mandate**: Make threshold dynamics **tactile**. Let users feel the logistic resonance σ(β(R-Θ)) ignite as membranes cross critical thresholds.
