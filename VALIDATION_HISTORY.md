# VALIDATION_HISTORY.md

**Generated:** 2026-07-19
**GenesisAeon / Feldtheorie — Empirical Validation History**

---

## How to read this document

Every entry below is labelled with exactly one status, and the label is a claim
about *how this session verified it*, not about scientific merit:

| Label | Meaning |
|---|---|
| **LIVE** | Actually executed this session, locally, with the exact command shown. Numbers are real output, not copied from any prior report. |
| **DOCUMENTED** | Claimed in that version's own `RELEASE_NOTES_*.md`/`CHANGELOG.md`. Not independently re-derived or re-executed this session. May well be true — just not re-verified here. |
| **NOT REPRODUCIBLE** | The release notes cite a specific number and a specific source file/dataset, and that exact source could not be found in the current repository, or the file that *was* found cannot produce the cited number (e.g. wrong row count for the stated statistical test). |
| **STUB / PLANNED** | The version's own documentation says the data is staged, mocked, or pending — i.e. it says so itself, this isn't an accusation. |

Nothing in this document adjusts a validation's own stated threshold to make it
pass. Where a number could not be reproduced, that is reported as a fact about
this session's ability to reproduce it — not a claim that the underlying
science is wrong.

---

## Why this document exists (the CI bug)

Every version of Feldtheorie ships its own validation scripts, but the V8 CI
job (`.github/workflows/v8-validation.yml`, "Run Live Validation Suite") never
actually completed a run: it embedded a large Python program inside a
double-quoted `python -c "..."` shell string, and one line —
`print(f'2. Kleiber'\''s Law...')` — used a bash single-quote-escaping idiom
(`'\''`) that isn't valid Python syntax at all (it produces a stray
backslash-apostrophe token outside any string literal). On top of that, a
second, independent bug in the same block —
`{\"✅ PASS\" if ... else \"❌ FAIL\"}` — put a backslash inside an f-string
`{}` expression, which Python 3.11 (the version this workflow pins) rejects
outright (relaxed only in 3.12+). Either bug alone would have crashed the
step before it printed anything.

**Fix applied:** rather than re-encode the same print statements a *third*
time inline in the YAML (which is how the bug was introduced — the CI step
duplicated logic that already existed, correctly, in
`models/consciousness_integration.py`'s own `if __name__ == "__main__":`
block), the step now does two much smaller things via a heredoc
(`python - <<'PY' ... PY`, which bash passes through with zero
interpretation):
1. `runpy.run_module("models.consciousness_integration", run_name="__main__")`
   — runs the already-correct, already-tested display code directly, with no
   duplication.
2. A short, separate falsification check (`sys.exit(1)` if any of the three
   numeric deviations exceeds its stated threshold) — restoring the actual
   functional purpose of this CI step, which the syntax error had always
   prevented from ever running.

Verified locally end-to-end (see "V8" section below) by extracting the exact
`run:` block YAML delivers to bash and executing it directly — exit 0, full
output, `validation_status=passed` written to `$GITHUB_OUTPUT`. **Confirmed
in real GitHub Actions CI too**, not just locally: pushing this fix
triggered an actual `V8 Consciousness Framework Validation` run (the
`v8-validation.yml` path filter only matches changes to
`models/*.py`/`tests/test_consciousness_integration.py`, so the fix commit
itself — which only touched the workflow file — never triggered a real
run; a follow-up commit fixing stale docstrings, below, did). Both the
`V8.0 Empirical Validation Suite` job and the `β-Domain Clustering
Analysis` job came back **green** for the first time in this workflow's
history (both had failed on every prior recorded run, back to the
earliest visible history on 2026-06-17).

Two independently-drafted fixes were considered and rejected before writing
this one:
- The task prompt's own suggested heredoc sketch was structurally correct
  (a heredoc avoids the quoting problem) but used placeholder field names
  that don't match this codebase's real dataclasses.
- A fix proposed by GitHub Copilot (`FeldtheorieV8FixGitHubCopilot.txt`)
  switched to a heredoc but **introduced a new, different syntax error**:
  `print(\"2. Kleiber's Law...\")`. A backslash immediately after `(` is not
  valid Python outside a string literal — heredocs need *no* escaping at all
  for an apostrophe inside a plain double-quoted string, so every `\"..\"`
  in that patch would itself have failed to parse. Confirmed via
  `ast.parse()` before rejecting it, not on inspection alone.

A second, unrelated but also-broken CI job was found in the same pass:
`coverage-check` required `--cov-fail-under=85` but only reached 59%,
because the `if __name__ == "__main__":` CLI-demo block (lines 722–805,
correctly never exercised by unit tests) had no coverage exclusion. Added
the standard `exclude_lines` entries to `[tool.coverage.report]` in
`pyproject.toml` — locally, this gives 100% coverage on the gated module
and the exact CI command (`pytest tests/test_consciousness_integration.py
--cov=... --cov-fail-under=85`) passes, re-verified from a clean
`.coverage` cache. **However, the real CI run of this job still came back
red** (`Test Coverage Check`, same job name it's always had — it also
failed on every run before this fix). Could not diagnose why the local
and CI results diverge: GitHub's job-logs API requires repo-admin auth
this session doesn't have (`403: Must have admin rights to Repository`),
and the public run/job-list endpoints only report pass/fail, not step
output. Ruled out the obvious candidates (no `.coveragerc`/`setup.cfg`/
`tox.ini` that could be shadowing `pyproject.toml`'s coverage section;
same `pytest-cov`/`coverage` versions locally as would resolve fresh from
PyPI). Reporting this honestly as **attempted, verified locally, not
confirmed in real CI** rather than claiming it's fixed — see "Known open
items" below.

---

## V8 (PyPI v6.0.0 / GitHub v13.0.0) — LIVE, executed this session

```bash
python -m models.consciousness_integration
```

| Empirical Law | Predicted | Observed | Deviation | Threshold | Status |
|---|---|---|---|---|---|
| Cosmic Matter-Dipole Alignment (Böhme et al., 2025) | v_RIG = 1352.0676 km/s | 1370.0 ± 170.0 km/s | 1.33% | < 10% | **PASS** |
| Kleiber's Law (Metabolic Scaling) | b = 0.750000 | b = 0.750000 | 0.00% | < 5% | **PASS** — see caveat below |
| Neural Integration Frequency (Sahu et al., 2013) | f = 13.5207 MHz | 13.50 MHz | 0.15% | < 5% | **PASS** |
| Specious Present (Δt_Q) | 150 ms (typical) | 100–300 ms (literature range) | n/a | in-range | **PASS** (descriptive, not a deviation test) |

These are the actual numbers this session's run produced — not the numbers in
either `FeldtheorieVALIDATION_HISTORYGitHubCopilot.txt` (which cites
1351.79 km/s / 1.35% deviation / 13.518 MHz / 0.13%) or the task prompt's
`KNOWN_V8_RESULTS` block (same figures). Both are close but not identical to
what actually executing the code produces today; the difference traces to
`ALPHA_INV = 137.03599206` in `models/unified_constants.py` giving
`v_RIG = 1352.0676 km/s`, not the `1351.7868` previously cited in that
module's own docstring example. Small (~0.02%), doesn't change any
PASS/FAIL verdict — but it's a real, checkable discrepancy between
documentation and code, so this session's docstring examples (this one and
8 others with the same root cause) were corrected to match; see "Known
open items" below for the full list of what changed.

**Honesty caveat on "Kleiber's Law: PASS":** `validate_kleiber_scaling()`
hardcodes *both* `b_predicted = 3.0/4.0` and `b_observed = 0.75` as literal
constants in the same function — they are not independently measured or
fetched from any dataset at runtime. A 0.00% deviation here is therefore
tautological (two hardcoded numbers compared to each other), not evidence
that the framework's prediction matches an external measurement it doesn't
already contain. The *ANOVA statistics attached to this same result*
(`F(4,73)=185.3, p<1e-20, η²=0.91`, describing a 78-system β-clustering
analysis) are also literal constants in the function — not computed from any
data file this session could locate. See "The 78-β-values claim" below.

β-Domain Clustering (`get_beta_domain_clustering()`, also run live): 5
domains (Information, Geophysical, Biology, Climate, Neurodegeneration),
`phi_attractor` values match `Φ^(n/3)` for n=3,3,4,5,5 as documented; one
domain (Neurodegeneration) has `deviation_percent = NaN` due to a
zero/near-zero denominator in that domain's specific calculation — not
investigated further, flagged as a minor open item below.

---

## The "78 β-values" claim — UPDATE: origin document found (archaeology sprint, 2026-07-19)

`RELEASE_NOTES_v6.0.0.md` states its own data source explicitly:
```
data/beta_estimates.csv    # 78 validated β-values across 5 domains
```
This exact path **does not exist anywhere in the repository's current state or
git history** (checked via `git log --all -- data/beta_estimates.csv`: no
results). The only similarly-named file at that location is
`data/derived/beta_estimates.csv` — 36 rows (not 78), incompatible with the
cited `df=(4,73)` (requires exactly 78 observations across 5 groups). This
part of the original finding (2026-07-19, first VALIDATION_HISTORY.md pass)
stands.

**What's new:** a follow-up archaeology sprint through the repo's buried
early-development history found the actual origin document:
`archive/legacy_v1_v3/seed/RoadToV.3/UTAC Empirical Validation v2.0/
UTAC_v2.0_COMPLETE_ANALYSIS.md` (2025-11-15, duplicated verbatim at
`archive/legacy_v1_v3/seed/RoadToV.3/Action/` — same "seed mirrors a working
copy" pattern already seen for `beta_estimates.csv` and
`v4.0.0-alpha_MirrorMachine`). It states "Total Datasets: 8 (78 datapoints)"
and contains the identical `F(4,73)=185.3, p<10⁻²⁰, η²=0.91` table — **and
that table's own header reads "ANOVA Results (simulated from data)"**,
verbatim, in the source document itself (not a later paraphrase or
misquote). Every later release-notes generation (V6.0.0-beta, V6.0.0, V8,
V9) dropped that qualifier when repeating the number.

This changes the finding from "cannot be traced at all" to something more
precise and, honestly, more interesting:

- **The per-dataset β estimates are, at least in part, real and
  literature-cited.** Found real backing CSVs for 5 of the document's 8
  named datasets at `archive/legacy_v1_v3/seed/RoadToV.3/Claude-Datenpaket2/`
  — `Vaginal_Microbiome_CST_Transitions.csv` (8 rows), `Huntingtons_Disease_
  CAG_Threshold.csv` (10), `AMOC_Paleoclimate_Collapses.csv` (10, source:
  NGRIP ice core, confirmed by reading the file), `ALS_TDP43_Phase_
  Separation.csv` (10), `Oral_Microbiome_Periodontitis.csv` (10) — row
  counts match the document's own per-dataset table exactly, each row cites
  a specific real source (Patel et al. 2015 *Cell*, Gajer et al. 2012
  *Science* DOI:10.1126/science.1217991, NGRIP, ENROLL-HD, Human Microbiome
  Project). The remaining 3 named datasets (Neuronal Avalanches, Earthquake
  Gutenberg-Richter, Measles Herd Immunity) were not found as exact matches;
  a separate, differently-numbered 60-file "Claude-Datenpacket" has
  thematically similar files with different row counts (7-8, not 10) —
  likely a different data-gathering pass, not confirmed as the same source.
- **The summary statistics wrapping those real numbers were not computed
  from them.** "Simulated from data" is the document's own phrase — this
  reads as an illustrative table written to show what the analysis *would*
  look like, not actual `scipy.stats`/R output from the 5-8 real datasets
  above. Re-running a real one-way ANOVA on however many of the 5 confirmed
  real datasets can be assembled into comparable β-values would be a
  legitimate, concrete follow-up (not attempted this session — time-boxed).
- **V2's separately-cited `η²=0.735, p=0.0061` Field Type ANOVA** turned up
  in a different, adjacent piece of buried history:
  `archive/legacy_v1_v3/seed/FraktaltagebuchV2/` (an informal, dated,
  budget-tracked development journal — entries literally note remaining
  session budget in USD, e.g. "~2-3$ von 76$ remaining"). Multiple entries
  there reference "η²=0.735" as "Meta-Regression v2", but one entry
  explicitly qualifies it as **"conceptual validation"** rather than a
  from-data computation — same self-admitted-informal pattern as the ANOVA
  table above, not a dedicated, independently re-run computation. Not
  traced further given the volume of that journal (dozens of dated,
  narrative-style entries, each with its own set of self-graded ✅
  checkmarks) — a full audit of it is a separate, larger task.
- **V1's `β≈4.2±0.6` cross-domain claim** — still not traced to a specific
  script/dataset producing that exact figure, though it's consistent with
  the RG (renormalization-group) fixed-point framing used throughout the
  same V2 analysis document (β≈4.21, Wilson-Kogut, cited as the
  "Informational Systems" cluster center).

**Bottom line, updated:** treat the `F(4,73)=185.3` statistic as **not
computed from real data** (confirmed, by the source document's own words),
while the *underlying per-domain β estimates* it's illustrating are, for at
least 5 of 8 named datasets, real and traceable to cited literature. This is
a more nuanced and more scientifically interesting finding than either
"fabricated" or "just missing" — the early development process appears to
have been genuinely rapid and exploratory (see the Fraktaltagebuch's
per-session dollar-budget tracking), with narrative/illustrative tables
written alongside real data-gathering, and the two got conflated in later,
more polished release notes that dropped the original "simulated"
qualifier.

---

## Version-by-version summary (V1–V13)

| Version | What it claims to validate | Concrete number cited? | Automated test found? | Status |
|---|---|---|---|---|
| **V1** (v1.0.1, v1.1.0) | Cross-domain UTF/UTAC logistic response — 6 domains (AI, climate, biology, neuroscience, socio-ecology, geophysics); β converges to ≈4.2±0.6 | Yes — per-domain β/Θ/ΔAIC/R² table | `simulation/threshold_sandbox.py` exists and is runnable; the cross-domain literature table itself is not a script output. Archaeology sprint (2026-07-19) searched `archive/legacy_v1_v3/` specifically for this figure — not traced to a specific script/dataset producing exactly β≈4.2±0.6, though consistent with the RG (renormalization-group) fixed-point framing used throughout the buried V2 analysis doc (β≈4.21, Wilson-Kogut). | DOCUMENTED |
| **V2** | "β is diagnostic of system architecture", not a universal constant — Field Type ANOVA | η²=0.735, p=0.0061; cross-domain β-correlation ρ=0.68, p<0.01 | Archaeology sprint (2026-07-19) found this referenced in `archive/legacy_v1_v3/seed/FraktaltagebuchV2/` — an informal, dated, per-session-dollar-budget-tracked development journal (e.g. "~2-3$ von 76$ remaining"). Multiple entries cite η²=0.735 as "Meta-Regression v2", but one entry explicitly qualifies it as **"conceptual validation"**, not a from-data computation — same self-admitted-informal pattern as V6's ANOVA table (see dedicated section above). Not traced to a dedicated, independently-rerunnable script; the journal itself is dozens of entries, a full audit is a separate task. | DOCUMENTED (traced to an informal source, not a computation) |
| **V3** | Not a distinct empirical-law validation in its own right — mostly infrastructure (`v3/data-adapters/`: real fetcher classes for RAPID-MOCHA/AMOC, GRACE, NOAA, USGS data, 2565 lines, has its own `test_noaa_real_data.py`) | n/a | The NOAA/USGS adapters have no equivalent in the current `scripts/adapters/` (which only has RAPID/GRACE/OISST) — genuinely unique, not superseded. Not executed this session (time-boxed) but not stub code either — real, structured fetcher classes. See "Archaeology sprint" section below for the full reactivation-candidate list. | DOCUMENTED (real code, not run) |
| **V4** | Mirror Machine criticality monitor (σ(β(R-Θ)) verdicts from live RAPID/GRACE/NOAA ingests); Aletheia relational-framing falsification | Qualitative (ΔAIC framework, no single headline number) | `scripts/monitoring/ews_pipeline.py`, `scripts/simulation/mirror_machine_auditorium.py` exist | DOCUMENTED |
| **V5** | α–Φ cosmic velocity structural isomorphism; social rigidity as an Ising field | Monte-Carlo null ensembles (`docs/science/v5_hypothesis_isomorphism.md`) | `models/cosmic_alpha_phi.py --runs 10000` and `models/social_rigidity_ising.py --sweep` are directly runnable scripts — **not executed this session** (time-boxed; flagged as a good next step, see TODO) | DOCUMENTED |
| **V6.0.0-beta / V6.0.0** | Ψ-wavefunction (tetrahedral symmetry, golden-ratio evolution); v_RIG Reality-Renderer; OIPK-Tesseract 4D simulation; "78 validated β-values" | F(4,73)=185.3, p<1e-20, η²=0.91; A₁₂<1e-5 falsification criterion for OIPK-Tesseract | Origin document found (archaeology sprint, 2026-07-19): the ANOVA table is self-labelled "simulated from data" in its own source; 5 of 8 named per-dataset β estimates ARE real and literature-cited — see dedicated section above for the full nuance | **PARTIALLY TRACED** (real per-dataset citations, simulated summary stats — see above; supersedes the original "NOT REPRODUCIBLE" verdict) |
| **V7** | Aeon Architecture (β/κ drift monitoring), Collective Field module, Selfmeta guardrails | "747/747 tests", "33/33 assertions" (per `releases/v7.0/github_release_notes.md`) | Yes — `tests/test_collective_field.py`, `tests/test_aeon_*.py` etc. **are part of this session's real full-suite run** (see below): all pass except 1 confirmed-flaky test unrelated to any change here | **LIVE** (via full suite) |
| **V8** | Cosmic dipole, Kleiber's Law, neural frequency, specious present (4 laws) | See dedicated section above | `tests/test_consciousness_integration.py` (22/22 pass) + `models/consciousness_integration.py` run directly | **LIVE** |
| **V8.1** | Ouroboros Engine narrative test cases (LLM-narrated universe-simulation events: SUCCESS/FAIL/DESPERATION) | Qualitative test-case walkthroughs, not a statistical validation in the same sense as V8 | Not evaluated this session (different domain — narrative/LLM behaviour, not a physical-law fit) | DOCUMENTED |
| **V9** | "Harmonic Emergence" — framed as unifying V1–V8 | None new | `v9_alpha/models/consciousness_integration.py` is a 5-line re-export shim of the root V8 module (confirmed by reading the file) — **no new empirical test exists in V9** | DOCUMENTED (shim, confirmed) |
| **V10** | Symbolic/governance "seed manifest" (σ_ϕ, entropy offset tolerance, "consciousness kernel") | None — no empirical law comparison in this version at all | None | DOCUMENTED (no empirical claim to test) |
| **V11** | "Resonant-Return" — β-fits on velocity dispersion / σΦ proxies vs. Gaia/JWST data | R=0.46, Θ=0.72, β=4.8, ζ(R)=0.19 | Explicitly self-described as staged: *"Staged Gaia + JWST stubs under `data/raw/` and `data/processed/` to anchor the empirical bridge"* | **STUB / PLANNED** (says so itself) |
| **V12** | Release-governance consolidation (AFET implementation, trilayer manifest parity) — not a new empirical-law validation | n/a | Automated release-consistency tests mentioned; not re-run separately (covered by the full suite run, which does not fail on anything V12-specific) | DOCUMENTED |
| **V13** (current, PyPI 6.0.0) | LanternNet integration — registers existing `models/` computational models as "Lanterns" with test mappings; not new empirical-law content | n/a | Same underlying `tests/` suite as V7/V8 | **LIVE** (via full suite) |

---

## Broader test-suite health (this session, real execution)

```bash
python -m pytest tests/ -q
```
**1227 tests collected, 1226 passed, 1 flaky (confirmed unrelated, see below).**
This is a much larger, real signal than the four V8 laws alone — the 86 files
under `tests/` cover nearly every version's architecture claims (Aeon, AFET,
collective field, RG flow, quantum AFET, climate β-pipeline, sigillin kernel,
etc.), not organized into per-version subdirectories the way the original
task prompt assumed (there is no `v1/`, `v2/` ... test layout; almost
everything lives in one flat `tests/` directory and accumulates across
versions in place).

**4 real bugs found and fixed in this run** (all the same class: Windows
console/file encoding defaulting to `cp1252` instead of UTF-8 — the identical
pattern found and fixed across ~12 other GenesisAeon packages this same
week; would not have affected the actual GitHub Actions CI, which runs on
`ubuntu-latest` with a UTF-8 locale by default, but is a real portability bug
regardless of platform):
- `scripts/validation/check_readiness_declared_actual.py`,
  `scripts/validation/check_status_drift_score.py` — printed `✅`/`❌`
  without `sys.stdout.reconfigure(encoding="utf-8")`; added the guard.
- `api/server.py` (2 call sites) — `open(path)` without `encoding="utf-8"`
  when reading preset/analysis JSON files.
- `tests/test_profiling_generator.py` — `Path.read_text()` without
  `encoding="utf-8"` when reading back a generated HTML report.
- Fixing the *scripts* above then exposed a **second**, related bug: the
  *tests* that shell out to these scripts via `subprocess.run(...,
  capture_output=True, text=True)` didn't pass `encoding="utf-8"` either —
  once the child process correctly emitted UTF-8, the parent test process
  tried to decode those bytes as `cp1252` and crashed the same way, just on
  the other side of the pipe. Fixed all 5 `subprocess.run` call sites across
  `tests/test_readiness_declared_actual_check.py` and
  `tests/test_status_drift_score.py`.

**1 flaky test, confirmed unrelated:** `tests/test_aeon_agents.py::
test_collective_consensus_detection` failed once in the full 1227-test run
but passed 3/3 times when run in isolation immediately after — pre-existing
test-order/shared-state flakiness, not something this session's changes
caused or fixed.

---

## Archaeology sprint (2026-07-19) — buried version directories, second real CI fix

Follow-up sprint: map every buried, pre-V8 version snapshot in this repo
(many versions were never merged into the current root-level `models/`/
`tests/` structure — they sit as isolated subfolders from an earlier,
less experienced phase of development), scan for syntax bugs the same
class as the V8 CI fix, and identify anything worth reactivating.

**Repo-wide syntax scan**: `ast.parse()` against all 595 `.py` files in
the repo — **0 syntax errors**. The V8 CI bug (`v8-validation.yml`) was
isolated, not a systemic pattern across old code. Also manually checked
the 6 other workflows with inline `python -c` blocks
(`doc-freshness-guard.yml`, `narrative-science-sync.yml`,
`sigillin-health.yml`, `sigillin-loop.yml`,
`sigillin-selfmeta-check.yml`, `utac-guards.yml`) for the same
apostrophe/backslash-in-f-string class of bug — all clean, verified by
actually extracting the exact `run:` block via PyYAML and executing it
through bash (not just reading it: an initial pass mistakenly ran
`ast.parse()` on the raw, still-bash-escaped YAML text and got a false
positive on `doc-freshness-guard.yml` — running it through actual bash
first, as bash itself un-escapes `\"` inside a double-quoted context,
showed it was correct all along).

**Second real CI fix found and confirmed**: `guard_digital_physics.yml`
("Guard Digital Physics" / `verify-hex-resonance` job) had failed on
every recorded run — found while investigating whether
`v11_gardener/core/beta_hexadecimal.py` (below) was relevant to it. Root
cause: the job has no Python/dependency setup at all, just checkout +
run. `from models.unified_constants import HEX_RESONANCE_BETA` executes
`models/__init__.py` first (accessing any submodule always runs the
parent package's `__init__` first), which eagerly imports 9 other
submodules, 5 of which import `numpy` directly — not part of the bare
`ubuntu-latest` Python, every other workflow that needs it installs it
explicitly. The resulting `ModuleNotFoundError` was being caught by the
guard's own except-clause and reported as "Non-Resonant Physics
Detected: unable to import HEX_RESONANCE_BETA (...)" — a misleading
message for what was actually a missing-dependency CI misconfiguration,
not a real constant drift. Fixed by adding the same Python
setup + `pip install numpy` steps every other workflow already uses.
**Confirmed in real GitHub Actions CI**: green for the first time on the
very next push.

**Buried directories surveyed** (the ones with actual `.py` content —
several other `releases/vX.Y` snapshots have zero Python files, pure
docs/data archives, and were only checked for any standout dataset, not
deep-reviewed):

| Directory | What's there | Verdict |
|---|---|---|
| `v3/data-adapters/` | Real fetcher classes: RAPID-MOCHA/AMOC, GRACE, **NOAA, USGS** (2565 lines, own `test_noaa_real_data.py`) | **Candidate.** NOAA/USGS adapters have no current equivalent (`scripts/adapters/` only has RAPID/GRACE/OISST) |
| `v9_alpha/models/` (excl. the already-known 3 shims) | 9 real, substantial modules (~4000 lines total): `frequency_tuner.py` (1264 lines), `emergence_metrics.py` (708), `em_field_calculator.py` (572), `network_visualizer.py` (470), `gardener_agent.py` (322), `sensorium.py` (268), `phase_dynamics.py` (133), `solar_driver.py` (193), `early_warning.py` (69, critical-slowing-down/lag-1-autocorrelation detector) | **Strongest candidate cluster.** None exist at root `models/`; has its own 7-file test suite already |
| `v11_gardener/core/beta_hexadecimal.py` | 350-line derivation/justification module for `HEX_RESONANCE_BETA` (three independent calculation methods, dated 2025-12-18) — the constant itself lives bare in current `models/unified_constants.py` with none of this derivation | **Candidate.** Directly relevant to the `HEX_RESONANCE_BETA` constant this sprint's second CI fix concerns |
| `releases/V6-Plans_etc/` (3 `.py` files) | `sigillin_kernel.py`, `crep_guard.py` (both differ substantially — 395 and 226 lines of diff — from current `api/sigillin_kernel.py`/`tools/crep_guard.py`, likely superseded drafts), `consensus_tracer.py` (no current equivalent, not examined in depth) | Low priority, except `consensus_tracer.py` unexamined |
| `releases/v4.0.0-alpha_MirrorMachine/` (+ identical `seed/releases/` copy — same "seed mirrors a working copy" pattern as `beta_estimates.csv`) | Adapters + monitoring + Mirror Machine sim | **Not a candidate** — `sensors/adapters/rapid_amoc_adapter.py` confirmed **byte-identical** (`diff`, 0 lines) to current `scripts/adapters/rapid_amoc_adapter.py`. Already fully migrated; contributes nothing new |
| `archive/v3_ideas/utac_klimakluft_visualization.py` (301 lines) | Visualization for the "klimakluft" (climate-crack) concept | Partial overlap with current `models/klimakluft_amplifier.py`/`scripts/klimakluft_analysis.py` (both already exist and already plot something) — not diffed, not confirmed redundant |
| `v10_oracle/` (`consciousness_kernel.py`, `semantic_bridge.py`, narrative/demo scripts, ~1764 lines) | Not evaluated in depth this session — more narrative/demo-flavored than V9's, lower priority | Not evaluated |

**Ranked reactivation candidates** (per this sprint's own explicit instruction: list only, no reactivation without an explicit follow-up decision):
1. `v9_alpha/models/{early_warning,phase_dynamics,em_field_calculator,emergence_metrics,frequency_tuner,gardener_agent,network_visualizer,sensorium,solar_driver}.py` — largest, most complete, most clearly non-duplicate; already has its own tests.
2. `v11_gardener/core/beta_hexadecimal.py` — small, directly relevant to a constant this sprint already touched.
3. `v3/data-adapters/src/{noaa_adapter,usgs_adapter}.py` — real external-data fetchers not covered by current adapters.
4. `releases/V6-Plans_etc/.../consensus_tracer.py` — unique, not reviewed in depth.

**Not reactivated, not moved, not renamed, nothing deleted** — per this
sprint's own instructions. This is a candidate list for a future,
explicit decision, not an action taken.

---

## Third and fourth real CI fixes (2026-07-21) — coverage-check and mypy

Two more CI jobs, both chronically red since before this session's
earliest visible history, root-caused and fixed this session:

**`coverage-check`** (`v8-validation.yml`): see the updated entry in
"Known open items" below — was previously flagged as "couldn't diagnose
without log access"; the user pasted the actual CI log, which gave the
real error (`ImportError: cannot load module more than once per
process`, a genuine `pytest-cov`/numpy interaction bug triggered
specifically by a dotted `--cov=` submodule path). Confirmed green in
real CI.

**`Lint (ruff + mypy)`** (`ci.yml`): had failed on *every* recorded run
since 2026-06-17. Root cause: `mypy src` computes module names relative
to `src` itself, but the codebase's own imports consistently use a
"src." prefix (`from src.scenarios.X import Y`) — since `src/` has no
`__init__.py`, mypy's implicit-namespace-package support lets the same
file resolve under *two* different names, and mypy refuses to check
anything at all once it detects this ("Source file found twice under
different module names"), which is why this job had never gotten past
3-5 files. Fixed with `mypy --explicit-package-bases src`, plus
`ignore_missing_imports` for `pandas`/`tqdm`/`plotly`/`requests` (no
stub packages installed by `.[dev]`, standard suppression already used
elsewhere in the ecosystem). Verified locally: mypy now checks all 44
source files (was stuck after 3-5) — **this still leaves the job red**,
since 23 genuine type errors are now visible that were previously
hidden behind the collection failure (real work, out of scope for this
fix — see the open item below for the list). One "Module X has no
attribute Y" cluster (`src/scenarios/level_0_vacuum.py` vs. the
same-named directory `src/scenarios/level_0_vacuum/`, which has no
`__init__.py`) was checked at runtime and confirmed to be a mypy-vs-
CPython namespace-package resolution difference, not an actual bug —
`import src.scenarios.level_0_vacuum` really does resolve to the `.py`
file at runtime, `Fluctuation`/`VacuumSimulation` are genuinely
accessible.

Also: a separately-reported `openai` missing-stub error could not be
reproduced locally (grepped the whole repo — only
`scripts/experiment_aletheia_placebo.py` imports `openai`, and nothing
under `src/` references that script, so `mypy src` shouldn't reach it).
Not added a speculative override; flagged in the workflow-fix commit in
case it resurfaces.

---

## Known open items (not fixed this session — out of scope / flagged for follow-up)

- **Re-run a real one-way ANOVA on the 5 confirmed-real per-dataset β
  estimates** found in `archive/legacy_v1_v3/seed/RoadToV.3/
  Claude-Datenpaket2/` (see the updated "78 β-values" section above) —
  would either genuinely replicate something close to the "simulated"
  `F(4,73)=185.3, η²=0.91` table, or show it doesn't hold up, either of
  which is more scientifically honest than repeating an admittedly-
  simulated number indefinitely. Needs assembling the 3 missing datasets
  (Neuronal Avalanches, Gutenberg-Richter, Measles) first, or explicitly
  reporting on the 5/8 subset.
- **`FraktaltagebuchV2`** (`archive/legacy_v1_v3/seed/FraktaltagebuchV2/`)
  is a large, informal, dated development journal with its own per-entry
  self-graded ✅ checkmarks (including the V2 "η²=0.735" claim, see
  above) — a full audit of what's real vs. narrative/conceptual in there
  is a separate, larger task not attempted this session.
- ~~**`coverage-check` job (`v8-validation.yml`) still fails in real CI**~~
  — **root-caused and fixed (2026-07-21)**, once the user pasted the
  actual CI log this session had no access to (no `gh`/token available;
  GitHub's job-logs API requires repo-admin auth). Real cause:
  `--cov=models.consciousness_integration` (a dotted submodule path)
  triggers a genuine `pytest-cov`/numpy interaction bug —
  `ImportError: cannot load module more than once per process` —
  reproduced locally in a clean, minimal venv (`uv venv`, only this
  job's own declared dependencies) via bisection: identical test run
  without `--cov` succeeds; `--cov=models` (the top-level package, not
  the dotted submodule) also succeeds; only the dotted-submodule form
  crashes. Unrelated to the earlier `exclude_lines`/coverage-percentage
  fix, which was necessary but not sufficient. Fixed by tracing via
  `--cov=models` and enforcing the 85% gate in a separate
  `coverage report --include='*/consciousness_integration.py'
  --fail-under=85` step — no new config file, doesn't touch the shared
  `pyproject.toml` coverage config used by `ci.yml`'s broader
  `--cov=src` runs. Verified end-to-end locally (fresh venv, exact
  extracted `run:` block via bash) and **confirmed green in real GitHub
  Actions CI** on the next push.
- **23 genuine mypy errors, now visible for the first time** (see above
  — `mypy --explicit-package-bases src`), across 13 files under `src/`.
  Not fixed this session (separate, real cleanup work). Worth
  prioritizing by risk — a few look like genuine potential runtime bugs,
  not just type-annotation nitpicks:
  - `src/core/llm_bridge.py:145`: `Item "None" of "str | None" has no
    attribute "strip"` — a real potential `AttributeError` if that code
    path executes with `None`, not just a missing annotation.
  - `src/scenarios/level_2_stellar/stellar_lifecycle.py:52,76`:
    `"ResonantEntity" has no attribute "agent_id"` — worth checking
    whether this is a real missing attribute or a stale reference to a
    renamed/removed field.
  - `src/interface/oracle_client.py:176,192,353`: three `str | None`
    vs. `str` mismatches, one on a return value — same class of
    "might actually crash" issue as the `llm_bridge.py` one above.
  - The remaining ~15 (assignment type mismatches, a missing variable
    annotation, `float`/`int` argument type issues in
    `atom_kernel.py`) look more like genuine-but-lower-risk annotation
    gaps.
- **The 78-β-values source dataset is missing** (see dedicated section
  above) — either locate it outside this repo, or regenerate/re-derive the
  ANOVA from `data/derived/beta_estimates.csv` (36 rows) and report the
  *actual* achievable statistic honestly, or correct the release notes to
  stop citing a dataset that isn't there.
- ~~**`docstring`/code constant mismatch**~~ — **fixed this session.** Running
  `doctest.testmod()` (with `ELLIPSIS`) against both modules found 8 stale
  doctest examples across `models/consciousness_integration.py` (impedance,
  v_RIG, cosmic-dipole deviation, neural-frequency events/spike, Planck
  slices, beta-domain names) and 1 in `models/unified_constants.py`
  (`calculate_vrig()`'s own example) — all traceable to the same
  ~0.02% `ALPHA_INV`-driven `v_RIG` drift, plus one unrelated stale example
  (domain names were lengthened elsewhere in the code but the old, shorter
  names were never updated in this one docstring). Updated all 9 to match
  what the code actually computes today; `doctest.testmod(...,
  optionflags=doctest.ELLIPSIS)` now reports 0 failures on both modules
  (was 8 and 1). None of these were previously enforced anywhere (no
  `--doctest-modules` in this repo's CI), so this was silent documentation
  drift, not a CI-visible bug — but it's the same "verify by executing"
  category as everything else in this document.
- **`BetaDomain` NaN deviation** for the Neurodegeneration domain in
  `get_beta_domain_clustering()` — not investigated (likely a division
  edge-case in that domain's specific bounds).
- **V5's two runnable validation scripts** (`models/cosmic_alpha_phi.py`,
  `models/social_rigidity_ising.py`) were not executed this session
  (time-boxed) — both take CLI arguments (`--runs`, `--sweep`) suggesting
  they're meant to be run on demand, not asserted in CI; a good next-session
  target for the same "LIVE" treatment V8 got here.
- **V1/V2's cross-domain literature tables** (β≈4.2 convergence, Field Type
  η²=0.735) are literature-sourced comparisons, not scripts — nothing to
  "run", but also nothing this session could independently check beyond
  confirming the release notes say what they say.
- `analysis/results/sandbox_beta_map.csv` (80 rows, synthetic
  `C_eff`/`D_eff`/`SNR` sweep with `beta_true` vs `beta_est` — a recovery
  simulation, not empirical data) was found while searching for the missing
  78-value dataset; it is a different, legitimate artifact (validates the
  β-estimation *method* against known-truth synthetic data) and should not
  be confused with the missing empirical dataset.

---

## Direct response to the external criticism this sprint was framed against

- **DeepSeek: "Concepts only within its own ecosystem"** — V8's four laws
  (Böhme et al. 2025, Kleiber 1932/West et al. 1997, Sahu et al. 2013,
  Wittmann 2011/Pöppel 2009) are genuinely external, independently-published
  reference points, confirmed by reading the actual citations in
  `models/consciousness_integration.py`. The comparison mechanism for one of
  the four (Kleiber's Law) is tautological as currently coded (see caveat
  above) — that's a real limitation, not addressed by this criticism being
  otherwise answerable.
- **Qwen: "Missing empirical validation"** — this document itself, plus the
  now-unblocked CI job, is the direct answer; but it should be read together
  with the "78 β-values... NOT REPRODUCIBLE" finding above, which is exactly
  the kind of gap this criticism was pointing at.
- **Gemini: "Validation gap"** — closed for V8 (CI runs now); explicitly
  *not* closed for V1–V7, V9–V13's headline statistics, which remain
  DOCUMENTED-not-reproduced or STUB per the table above.
