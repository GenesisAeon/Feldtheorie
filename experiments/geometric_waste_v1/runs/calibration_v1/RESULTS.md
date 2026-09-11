# Exact calibration results

GW-EXACT-001 was executed after protocol and runner commit `620a5ce3425f9da741c6444e12ce5b26c029771e`. The baseline is Feldtheorie `546c606f6ca15acec152c14f99fa6806a839596a`. This result is an exhaustive calculation for two declared finite ensembles. It is not confirmation of the broad geometric-waste hypothesis.

## Results

| Ensemble | Observer | Residual entropy in bits per lattice | Bayes cell error fraction |
|---|---|---|---|
| uniform_all | identity | 0.000000 | 0.000000 |
| uniform_all | occupancy | 12.953450 | 0.401810 |
| uniform_all | block_counts | 7.877444 | 0.312500 |
| uniform_all | block_counts_boundary | 5.914209 | 0.312500 |
| uniform_all | block_counts_scrambled_11 | 5.398253 | 0.288622 |
| uniform_all | block_counts_scrambled_23 | 5.398451 | 0.288372 |
| uniform_all | block_counts_scrambled_47 | 5.400446 | 0.288766 |
| uniform_density_half | identity | 0.000000 | 0.000000 |
| uniform_density_half | occupancy | 13.651724 | 0.500000 |
| uniform_density_half | block_counts | 8.392551 | 0.338462 |
| uniform_density_half | block_counts_boundary | 6.330079 | 0.338462 |
| uniform_density_half | block_counts_scrambled_11 | 6.040198 | 0.318230 |
| uniform_density_half | block_counts_scrambled_23 | 6.042857 | 0.318803 |
| uniform_density_half | block_counts_scrambled_47 | 6.040988 | 0.318187 |

## Interpretation

At fixed density, block counts leave 8.392551 bits of uncertainty; adding boundary length leaves 6.330079 bits. The gain is 2.062472 bits. Cellwise Bayes reconstruction error remains 0.338462. In the uniform ensemble it likewise remains 0.312500 despite lower conditional entropy. More retained joint information therefore does not necessarily improve this particular cellwise loss. No temporal prediction task was run.

Scrambled boundary labels leave roughly 6.041 bits at fixed density and roughly 5.399 bits in the full ensemble, with lower cellwise error than the geometric observer. Their marginal distribution matches that of boundary length, but they constitute arbitrary nonlocal lookup metadata with different conditional information and implementation cost. These comparisons expose the danger of crediting geometry for the automatic benefit of additional information. They are not an algorithmic performance comparison or a rejection of a geometry-specific hypothesis. Three permutations provide no inferential p value.

## Validation and limits

Seven unit tests pass, including analytic binomial loss, identity and constant limits, complete support, hand-defined geometry, invariance under rotation/translation, and refusal to overwrite output. The full Feldtheorie test suite was not run: the new pilot is standalone and does not import existing repository modules. Runtime Python and NumPy versions and source hashes appear in results.json. The environment is not a certification against the full repository dependency constraints.

The ensemble has equal probability for every allowed array. It contains no dynamics, temperature, learned distribution, metric smoothing, holes/Betti estimator or gravitational field. No AIC or bootstrap interval is meaningful for this exhaustive count. The calculation was implemented and checked by the same assistant; independent AI review and human review are pending.

## Reproduce and continue

From the experiment directory run `python -m unittest -v test_exact`, then `python run_exact.py --output runs/reproduction_001`. Use a new destination for each run. Compare the numerical observers in results.json and inspect observation_classes.csv. Ignore Python-version metadata when comparing runs across environments, while retaining it as provenance.

The next registered task is GW-PRED-002: define structured ensembles, matched observation budgets and independent held-out families. Select the primary scientific target before fitting anything. This calibration is development evidence and must not become the holdout for that next test.
