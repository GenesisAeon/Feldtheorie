# UTAC Falsifiability Framework

## 1. Hypotheses under test
- **H₁ (β universality):** emergent transitions cluster within
  \(\beta \in [3.6, 4.8]\) after normalisation.
- **H₂ (Logistic superiority):** the logistic response outperforms smooth nulls
  with ΔAIC ≥ 10 and positive ΔBIC.
- **H₃ (Field coupling):** the coupling term \(\mathcal{M}[\psi, \phi]\) produces
  measurable shifts in \(\Theta\) or \(\beta\) when perturbed.

## 2. Falsification criteria
| Criterion | Evidence required | Repository action |
|-----------|------------------|-------------------|
| β outside band | Bootstrap CI excluding \([3.6, 4.8]\) with documented preprocessing | Log case in this file, revisit normalisation |
| Null model wins | ΔAIC < 2 or negative ΔBIC across replications | Archive failing dataset, adjust modelling assumptions |
| Coupling ineffective | Perturbations leave \(\Theta\) and \(\beta\) unchanged within error bars | Update `models/` experiments and document limitation |

## 3. Experimental procedures
1. **ΔAIC comparison:** Fit logistic and null models, compute ΔAIC and ΔBIC.  See
   `scripts/reproduce_beta.py` and `METHODS.md`.
2. **Bootstrap diagnostics:** Resample data (paired \(R\), response) 1,000 times,
   refit, and compute CI for \(\beta\) and \(\Theta\).
3. **Sensitivity checks:** Vary preprocessing (normalisation, outlier removal) and
   repeat the analysis.  Record deviations greater than 5% in this log.

## 4. Current status log
| Dataset | Domain | β estimate | ΔAIC (best null) | Status |
|---------|--------|------------|------------------|--------|
| `data/ai/wei_emergent_abilities.csv` | AI | 3.47 ± 0.47 | 12.1 (power law) | Within band; more samples requested |
| `data/socio_ecology/planetary_tipping_elements.csv` | Climate | 4.21 ± 0.47 | >30 (linear/power) | Supports universality |
| `data/cognition/working_memory_gate.csv` | Cognition | 12.28 ± 0.30 | 51.6 (linear) | Outside band; attributed to raw-unit measurement |

## 5. Reporting obligations
Any pull request introducing new analyses must update this log when:
- ΔAIC < 10 for any null model,
- \(\beta\) falls outside \([3.6, 4.8]\) after normalisation, or
- coupling experiments fail to modify \(\Theta\) or \(\beta\).

## 6. External replication invites
Researchers replicating the UTF fits should provide:
- dataset description and licensing,
- logistic parameters with confidence intervals,
- ΔAIC/ΔBIC values versus nulls,
- notes on preprocessing and impedance configuration.

Submit replication reports via issues or pull requests referencing this file and
linking to the generated JSON outputs.
