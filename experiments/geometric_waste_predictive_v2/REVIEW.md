# Protocol and implementation review

Status: independent review pending. The frozen protocol has an implementation and a completed development run; confirmatory data remain unopened. See [IMPLEMENTATION.md](IMPLEMENTATION.md) and [DEVELOPMENT.md](DEVELOPMENT.md). A merge of the prior experiment does not by itself document its independent recomputation.

Review these questions before approving a runner for confirmatory evaluation:

1. Can the chosen cellular rule, fixed half density and two held-out families answer the stated narrow prediction question?
2. Are sensor access, quantization and unequal acquisition costs clear? The shared budget is eight transmitted bits, not equal entropy or equal energy.
3. Is the MICRO comparator informative enough to provide a useful alternative, and does COARSE distinguish representation effects from added microscopic information? Proposed changes belong in a new protocol version before data are inspected.
4. Are exact symmetries and duplicate rejection handled without quietly changing family membership or sample counts?
5. Is every model choice based only on training and validation? Are all twenty models frozen before any test states or scores are exposed?
6. Are repeat-level uncertainty, the chosen practical threshold and the per-family guard appropriate? Twenty repeats do not come with an established power guarantee.
7. Are claim boundaries explicit? A successful finite benchmark does not establish a universal entropy law or dominance over all sensors.

Record reviewer, reviewed protocol commit, mathematical ambiguities, design changes requested, implementation gates, and verdict. Retain every prior version and any negative review.
