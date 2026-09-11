# Geometric waste exact calibration v1

## Question and scope

For a finite binary lattice and a declared uniform ensemble, how much microscopic information is lost by each observation map? Does revealing a geometric boundary statistic reduce this loss, and how does that compare with revealing a scrambled statistic with the same marginal distribution?

This is an exact calibration of a proposed information measure, not a confirmatory test of the broad geometric-waste hypothesis. Adding any deterministic feature cannot increase conditional entropy. That inequality is a mathematical identity, not evidence that geometry is uniquely explanatory. No thermodynamic, gravitational, quantum or spacetime claim is tested here.

## Frozen design

- Protocol ID: GW-EXACT-001, version 1.0.0.
- System: all 65,536 binary 4 by 4 arrays; cell zero is the low-order bit and rows use C order.
- Ensembles: uniform over all arrays; uniform over the 12,870 arrays containing exactly eight ones. The latter controls density exactly.
- Observers: identity; total occupancy; the four labelled non-overlapping 2 by 2 block counts; block counts plus boundary length.
- Boundary length: count unequal horizontal and vertical nearest-neighbour pairs on the periodic square lattice. Each undirected edge is counted once; maximum 32. This is an interface statistic, not a Betti number or hole count.
- Primary quantity: H(X given Y), in bits per entire lattice. With a uniform finite ensemble, this is the weighted mean of log2 of each observation class size.
- Secondary quantity: minimum expected cellwise Hamming error, divided by 16, using the exact posterior of the declared ensemble. It measures reconstruction, not prediction of a future state.
- Null diagnostic: permute the boundary labels within each ensemble, retaining their marginal distribution, then add them to the block counts. Seeds 11, 23 and 47 are fixed before execution. This is deliberately a nonlocal lookup observer and has no claim to physical implementability. Three draws are diagnostics, not a significance test or a confidence interval.
- Export observation class sizes and posterior loss for the density-fixed block and block-plus-boundary observers. Microstates are generated exhaustively from the declared integer order, not sampled.

## Checks and interpretation

The identity observer must have zero conditional entropy and zero reconstruction error. A constant observer must lose log2 of the ensemble size. For fixed density, occupancy is constant. For independent fair binary cells, the block-count result must equal four times the corresponding analytic 2 by 2 block loss. Boundary fixtures include an empty field, one occupied cell, a vertical half-plane and a checkerboard. Rotations and translations must preserve periodic boundary length.

If any check fails, the calibration is unsuccessful and numerical scientific interpretation stops. If checks pass, the result establishes a reproducible operational definition for this finite ensemble. It does not establish a geometry-specific advantage. Comparison with scrambled metadata makes this limitation explicit. Finite-ensemble entropy and Bayes reconstruction error can disagree in their ranking or remain equal despite added information.

No fitted response curve, AIC, p value or bootstrap confidence interval is appropriate for this exhaustive calculation. Model-selection metrics and uncertainty estimation belong in a later experiment with estimated quantities and independent data. The repository notation R, Theta, beta, zeta(R), and sigma(beta(R-Theta)) is not instantiated: this calibration contains no resource-driven transition or logistic fit.

## Provenance and preservation

Conceptual source: Johann Benjamin Römer / GenesisAeon, [entropy_geometric_waste.md](https://github.com/GenesisAeon/Feldtheorie/blob/546c606f6ca15acec152c14f99fa6806a839596a/seed/theory/entropy_geometric_waste/entropy_geometric_waste.md). Original scope and historical text are retained.

Base repository commit: 546c606f6ca15acec152c14f99fa6806a839596a. Record the protocol and runner SHA256 hashes, Python and NumPy versions, ensemble definitions and diagnostic seeds in the result. Commit this protocol and runner before the first scientific run. This is an internally frozen pilot, not external preregistration.

The runner refuses to write into an existing output directory. A rerun must use a new directory. No historical source, result, branch or worktree is deleted. Evaluation in this delivery is by the implementing assistant; independent AI and human review remain pending. A future Scope adapter should link these artifacts rather than claim that Scope itself answers or adjudicates the hypothesis.

## Next experiment

GW-PRED-002 will ask whether geometry predicts description loss or future-state error beyond density, resolution and matched information budgets on unseen structured ensembles. Its distributions, train/test split, estimator validation, metric and practical effect threshold must be fixed in a new protocol. The outcome here will inform that design; it cannot be reused as its held-out evidence.
