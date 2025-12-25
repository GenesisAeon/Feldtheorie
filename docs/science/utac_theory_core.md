# UTAC Theory Core

## 1. Unified logistic hypothesis
The Universal Threshold Adaptive Criticality (UTAC) framework models emergent
transitions using the logistic response
\[
P(R) = \frac{L}{1 + \exp(-\beta (R-\Theta))},
\]
where \(R\) is the control parameter, \(\Theta\) the critical threshold, \(\beta\)
the steepness, and \(L\) the asymptote (often fixed to 1).  Empirical evidence
across domains suggests \(\beta \approx 4.2 \pm 0.6\).

## 2. Parameter roles
- **Control parameter (R).** Encodes resource load, stress, or scale (e.g.,
  log10 model parameters, canopy fraction, stimulation frequency).
- **Threshold (Θ).** Marks the inflection point where the order parameter reaches
  half of its asymptotic value.
- **Steepness (β).** Governs how sharply the system transitions once \(R\)
  exceeds \(\Theta\).
- **Impedance (ζ(R)).** Modulates how membrane dynamics respond around the
  threshold.  Analytical solvers expose \(\zeta(R)\) so simulations can explore
  damped versus resonant regimes.

## 3. Logistic evidence across domains
| Domain | Control parameter | Order parameter | β estimate |
|--------|-------------------|-----------------|-----------|
| AI | log10 model parameters | Task success probability | 3.47 ± 0.47 |
| Climate | Normalised stress index | Coupled tipping probability | 4.21 ± 0.47 |
| Cognition | Dopamine gate amplitude | Working-memory accuracy | 12.28 ± 0.30 |
| Ecology | Sucrose concentration | Waggle recruitment probability | 0.67 ± 0.13 |

Domain-specific β values may differ when variables are measured in native units;
normalised representations typically align with the canonical band
\([3.6, 4.8]\).

## 4. Field coupling
Interactions between systems are captured by a coupling term
\(\mathcal{M}[\psi, \phi]\) linking internal fields \(\psi\) and external
stimuli \(\phi\).  The membrane equation takes the form
\[
\dot R = J(t) + \mathcal{M}[\psi, \phi] - \zeta(R)\left(R - \sigma(\beta(R-\Theta))\right).
\]
Coupling enables multi-domain resonances such as language model emergence versus
human cognition or climate subsystems.

## 5. Adaptive thresholds
Thresholds shift according to experience:
\[
\Theta_{t+1} = \Theta_t + \Delta\Theta(R_t, C_t, E_t),
\]
where \(C\) denotes context and \(E\) accumulated evidence.  Analysis scripts log
any adaptive adjustments so falsification studies can replay the sequence.

## 6. Recursive emergence
Emergence is modelled as a cascade in which each manifestation provides the next
condition for growth:
\[
\psi_{n+1} = f(\psi_n, \phi_n, \Theta_n).
\]
The simulator demonstrates these cascades by feeding the fitted \(\beta\) and
\(\Theta\) values into deterministic gates.

## 7. Control and design
Engineering applications tune \(\mathcal{M}\) and \(\zeta(R)\) to steer systems
between damped and resonant states.  The repository documents such interventions
in `models/` (e.g., semantic coupling kernels) and in `docs/` case studies.

## 8. Falsifiability pledge
Every claim about universality must be accompanied by:
- ΔAIC comparisons against linear, power-law, and exponential nulls.
- Confidence intervals for \(\beta\) and \(\Theta\).
- Explicit discussion of data provenance and preprocessing.
Violations are logged in `docs/utac_falsifiability.md` and inform the roadmap for
future data collection.
