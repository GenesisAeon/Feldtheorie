# Ethics and Responsible Use

## Intended scope
The Universal Threshold Field programme investigates how the logistic quartet
\((R, \Theta, \beta, \zeta(R))\) captures switch-like transitions across domains.
It is a scientific exploration of threshold dynamics, not a turnkey policy or
safety prescription.  Results should inform, not replace, domain-specific
expert judgement.

## Responsible interpretation
1. **Contextual validation.** Threshold inferences must be checked against the
   data provenance documented in `data/*/*.metadata.json` and the statistical
   diagnostics exported by `analysis/`.
2. **Model limitations.** The logistic response is a deliberately simple proxy.
   Domains exhibiting multi-stage or hysteretic behaviour may require extended
   models; ΔAIC comparisons should be revisited before drawing strong claims.
3. **Uncertainty reporting.** Always communicate the bootstrap confidence
   intervals for \(\beta\) and \(\Theta\), the residual diagnostics, and null
   model outcomes.
4. **No anthropomorphism.** References to membranes or dawn choruses are
   metaphors.  They must not be interpreted as evidence of agency or
   consciousness in analysed systems.

## Misuse risks and mitigations
| Risk | Description | Mitigation |
|------|-------------|------------|
| Overclaiming universality | Treating \(\beta \approx 4.2\) as proven across all systems. | Require independent replication; publish ΔAIC and sample sizes. |
| Policy shortcuts | Applying thresholds directly to policy without domain expertise. | Pair findings with subject-matter review and cite uncertainties. |
| Data rights violations | Using proprietary or sensitive datasets without consent. | Restrict analyses to openly licensed data; document licenses in metadata. |
| Automation without oversight | Delegating judgement to the pipeline. | Keep human review in the loop and log all stochastic seeds. |

## Data governance
- Respect dataset licenses recorded in each metadata file.
- Remove personal or sensitive information before ingestion.
- Credit original data providers and cite canonical publications in manuscripts
  and notebooks.

## AI assistance transparency
Large language models contribute as writing and coding aides.  All generated
content is reviewed by human maintainers, and `AUTHORSHIP.md` explains the
responsibility split.  Automated tools must not be listed as co-authors in
external publications.

## Invitation for scrutiny
We invite independent replication.  Issues or pull requests that identify
statistical weaknesses, ethical concerns, or data provenance gaps will be
addressed promptly.  Please include references to the relevant JSON outputs or
notebooks so we can trace the logistic quartet end to end.
