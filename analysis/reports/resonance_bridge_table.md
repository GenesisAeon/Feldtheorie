# Resonance Bridge Table

## Formal
This ledger collates logistic resonance fits across domains, recording $\Theta$, $\beta$, $R^2$, and the strongest $\Delta\mathrm{AIC}$ wins against smooth null models.

## Empirical
Entries draw from `analysis/results/*.json`; statistics summarise domain coverage, logistic accuracy, and impedance medians so reports and simulator presets remain in sync.

## Metaphorical
Each row is a lantern along the resonance bridge—bees, membranes, forests, and models singing as $R$ crosses $\Theta$ and the null breeze quiets.

### Cohort Statistics

*Datasets tallied:* 11
*Domain spread:* ai: 1, biology: 3, cognition: 2, geophysics: 1, socio_ecology: 2, synthetic: 2
*ΔAIC vs best null:* min=25.196, median=59.540, mean=111.160, max=498.148
*Logistic R²:* min=0.969, median=0.997, mean=0.993, max=1.000
*Impedance ζ̄:* min=0.978, median=1.179, mean=1.207, max=1.534

### Logistic Bridge

| Domain | Dataset | Θ | β | R² | ΔAIC (best null) | Best null | ζ̄ |
|--------|---------|---|---|----|------------------|-----------|----|
| cognition | adaptive_theta_plasticity | 0.477 | 10.860 | 0.990 | 37.700 | power_law | 0.978 |
| socio_ecology | amazon_resilience | 0.621 | 14.019 | 0.999 | 70.696 | power_law | 1.534 |
| synthetic | coupled_field_threshold | 0.509 | 5.658 | 0.998 | 4.981e+02 | cubic_polynomial | 1.108 |
| biology | honeybee_waggle_activation | 26.578 | 0.672 | 0.969 | 25.196 | linear | 1.113 |
| biology | lenski_citplus | 32.769 | 5.077 | 0.990 | 42.126 | linear | — |
| ai | llm_emergent_skill | 4.707 | 5.104 | 0.995 | 48.833 | power_law | 1.379 |
| geophysics | subduction_rupture_threshold | 0.741 | 16.290 | 1.000 | 1.487e+02 | power_law | 1.365 |
| biology | synaptic_release_threshold | 12.678 | 0.810 | 0.997 | 72.232 | power_law | 1.187 |
| synthetic | synthetic_threshold_sweep | 0.022 | 11.093 | 0.989 | 1.680e+02 | power_law | 1.000 |
| socio_ecology | urban_heat_canopy | 0.313 | 15.275 | 0.999 | 51.557 | linear | 1.231 |
| cognition | working_memory_gate | 0.579 | 12.284 | 0.999 | 59.540 | power_law | 1.170 |
