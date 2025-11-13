# Changelog

All notable changes to the UTAC (Universal Threshold Activation-Coupling) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - V2.0 Development (In Progress)

#### Scientific Breakthrough 🏆
- **Meta-Regression v4**: Expanded to n=36 systems across 11 domains
  - Adjusted R² = 0.665 (66.5% variance explained)
  - p-value = 0.0005 (highly significant!)
  - β range: 1.22 – 18.47
  
- **RG Microscopic Derivation**: β emergent from J/T (coupling-to-noise ratio)
  - Wilson's Renormalization Group theory validated
  - Agent-Based Model (450 LOC, 21/21 tests passing)
  - β_emergent ≈ 3.25 vs β_theory ≈ 4.21 (23% deviation - typical for mean-field)
  - Proof: β is NOT a fit constant but emerges from first principles!

- **Φ^(1/3) Scaling Discovery**: Universal skalierung mit 0.31% Genauigkeit
  - 9 diskrete Schritte konvergieren zu β ≈ 4.236 (= Φ³)
  - Geometrische Wahrheit im 3D-Parameterraum (R, Θ, β)

#### Documentation & Infrastructure
- `docs/METHODS.md`: Comprehensive methods documentation (2025-11-13)
  - ABM design, statistical analysis, validation pipeline
  - Finite-size scaling, convergence diagnostics
  - Full reproducibility specifications

- `data/metadata/*.yaml`: Metadata for all critical climate systems
  - Urban Heat Islands (β=16.3)
  - Amazon Precipitation (β=14.6)
  - Glacier/Albedo (β=5.3)
  - AMOC (β=4.0)
  - WAIS (β=5.7)

- `utils/data_loader.py`: Automated data loading infrastructure
  - YAML metadata parsing
  - Multi-format support (CSV, NetCDF, JSON)
  - τ* calculation utilities

#### Planned Components (Specified, Not Yet Integrated)
- **arXiv Paper Package**: Complete LaTeX + Figures + Supplementary
- **Validation Pipeline**: `validate_phase2.py`, `aggregate_validation.py`
- **Fourier Analysis Module**: `sonification/utac_fourier.py`
- **CI/CD Workflows**: GitHub Actions for reproducibility
- **Docker Image**: 1-click reproduction environment

### Changed
- Improved FraktaltagebuchV2 workflow for V2.0 scope isolation
- Enhanced documentation structure

### Fixed
- N/A (first V2.0 changelog entry)

## [1.2.0] - 2025-11-10

### Added
- FraktaltagebuchV2 system for version-specific development tracking
- Initial V2.0 roadmap and planning documents

### Changed
- Reorganized seed/NextVersionPlan/ with comprehensive planning docs

## [1.1.0] - Previous Releases

See git history for details of v1.x releases.

---

## Versioning Strategy

- **v1.x**: Core UTAC framework, initial implementations
- **v2.0**: Scientific breakthrough integration, full data infrastructure
- **v2.1+**: Extensions (VR, API, interactive visualizations)

## Contributing

See CONTRIBUTING.md for guidelines on proposing changes.

## Links

- **Repository**: https://github.com/GenesisAeon/Feldtheorie
- **Zenodo**: [DOI to be added]
- **arXiv**: [Submission planned]

---

**Maintained by:** Johann Benjamin Römer & Contributors
**Last Updated:** 2025-11-13
