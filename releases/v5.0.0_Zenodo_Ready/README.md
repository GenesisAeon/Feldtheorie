# Feldtheorie V5.0.0 - Zenodo Release Bundle

**Version:** 5.0.0
**Release Date:** 2025-11-23
**Status:** 🟢 READY FOR UPLOAD

---

## Contents

This directory contains everything needed to upload Feldtheorie V5.0.0 to Zenodo for DOI assignment and long-term archival.

### Core Documents

**1. ABSTRACT_ZENODO.md** (8.8 KB)
- Comprehensive abstract for Zenodo description field
- Includes keywords, citation format, and project overview
- Copy relevant sections to Zenodo metadata form

**2. Paper_1_The_Fractal_Engine.md** (18 KB)
- **Methodological paper** describing the fractal governance system
- Explains Champollion & Sigillin architecture
- **Status:** Production-ready software, fully validated
- Demonstrates 180 governed contexts with zero inconsistencies

**3. Paper_2_Hypothesis_137_Beta.md** (27 KB)
- **Theoretical note** on structural isomorphism hypotheses
- Describes cosmic scaling and social rigidity models
- **Status:** Active research, hypothesis testing phase
- Includes explicit limitations and falsification criteria

### Artifacts

**4. Feldtheorie_v5.0.0_Source.zip** (49.56 MB)
- Complete repository snapshot
- 2,173 files included
- Excludes: .git/, venv/, __pycache__, temporary files
- Ensures reproducibility for all results

**5. MANIFEST.txt** (310 KB)
- Complete file listing with metadata
- Includes file paths, sizes, SHA256 hashes, timestamps
- Enables integrity verification

**6. UPLOAD_CHECKLIST.md** (4.8 KB)
- Step-by-step Zenodo upload instructions
- Metadata field templates
- Post-publication checklist

### Utilities

**7. prepare_upload.py** (16 KB)
- Python script that generated these artifacts
- Can be re-run to regenerate ZIP and manifest
- Usage: `python prepare_upload.py [--dry-run]`

---

## Quick Start

### Option A: Upload to Zenodo Now

1. **Review papers** (convert to PDF if desired)
2. **Read UPLOAD_CHECKLIST.md**
3. **Go to https://zenodo.org/**
4. **Follow checklist instructions**

### Option B: Regenerate Artifacts

If you've made changes and need to refresh the ZIP:

```bash
# Dry run to preview
python prepare_upload.py --dry-run

# Regenerate artifacts
python prepare_upload.py
```

To recreate the Python environment used for the release scripts and analyses, install the pinned dependencies in this directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## V5 Scientific Reference Links

- **docs/v5_hypothesis_isomorphism.md** – canonical description of the 137‑β structural isomorphism question and its falsification paths.
- **docs/v5_validation_session_2025-11-23.md** – summary of Monte‑Carlo and look‑elsewhere scans (Operation Budget Burner), including the 0.8 % quantile placement of the preferred constant pair.
- **docs/v5_fit_mor_sigillin_review.md** – code review and MOR‑FIT compliance notes for the new cosmic and social models.

These references keep the Zenodo bundle anchored to the latest V5 validation results and make the empirical caveats discoverable from the release entry point.

## Packaging Profiles

- `--profile full` (default): archives the entire repository minus standard exclusions.
- `--profile slim`: excludes historical and heavy paths (`archive/`, `output/`, `results/`, `seed/`, `notebooks/`, `dags/`, `vr/`) to produce a reproducibility‑focused bundle for Zenodo while keeping code, papers, and core data intact.

The active profile is recorded inside `MANIFEST.txt` for provenance. Use the slim profile when Zenodo readers need a lean archive without losing the validated pipelines.

---

## The Strategy: "Repo as Proof"

This release follows the **"separate tools from theory"** principle:

### The Werkzeug (Tool) - Paper 1
- **Champollion & Sigillin** governance system
- **Status:** Production-ready, validated, operational
- **Claim:** "This system works and is useful for any research project"
- **Defense:** 180 governed contexts, zero inconsistencies, full CREP compliance

### The Theorie (Theory) - Paper 2
- **137-Beta Hypothesis** (cosmic scaling + social rigidity)
- **Status:** Active research, hypothesis testing
- **Claim:** "These correlations warrant investigation"
- **Defense:** Rigorous null hypothesis testing, explicit limitations, falsification criteria

**Why this works:**
1. Nobody can say "The code is bad" (the governance system is excellent)
2. Nobody can say "The physics is proven" (we label it as hypothesis)
3. The tool is universally useful (any research domain can adopt it)
4. The theory is honestly presented (we invite falsification)

**This makes the upload safe and defensible.**

---

## What to Upload to Zenodo

**Recommended order:**

1. **Paper_1_The_Fractal_Engine.md** (or PDF)
   - Type: Publication
   - Description: "Methodological paper on fractal governance"

2. **Paper_2_Hypothesis_137_Beta.md** (or PDF)
   - Type: Publication
   - Description: "Theoretical note on structural isomorphism (hypothesis)"

3. **Feldtheorie_v5.0.0_Source.zip**
   - Type: Software
   - Description: "Complete repository snapshot for reproducibility"

4. **MANIFEST.txt**
   - Type: Other
   - Description: "File listing with integrity hashes"

**Optional but recommended:**
- Convert Markdown papers to PDF for better readability
- Tools: Pandoc, Typora, or online converters

---

## Metadata Template

Copy this for Zenodo:

**Title:**
```
Feldtheorie V5: A Fractal Governance System for Structural Isomorphism Research
```

**Authors:**
```
Johann Benjamin Römer (Primary)
Genesis Aeon (Framework)
MOR Collective (Contributors)
```

**Keywords:**
```
fractal-governance, research-software-engineering, UTAC, structural-isomorphism,
null-hypothesis-testing, cosmic-scaling, social-phase-transitions,
empirical-validation, reproducible-research, 137-beta
```

**License:**
```
Software: MIT License
Documentation: CC BY 4.0
```

**Related Identifiers:**
```
https://github.com/GenesisAeon/Feldtheorie
```

See UPLOAD_CHECKLIST.md for complete metadata template.

---

## Data Availability & Licensing Notes

- **Open datasets only:** Include public or pseudonymized datasets in the Zenodo bundle. Omit sensitive social datasets; if needed, provide access instructions instead of raw records.
- **Default licenses:** Code remains MIT; documentation and shared data default to CC BY 4.0. Ensure any added datasets are license-compatible and cite provenance in `MANIFEST.txt` entries.
- **User-supplied data hooks:** Social rigidity notebooks and `data/grounding` loaders accept external CSV inputs—document any custom files in the upload description so reviewers understand how to reproduce results safely.

---

## Post-Upload TODO

After getting the DOI from Zenodo:

1. **Update README.md** with DOI badge:
   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
   ```

2. **Update citation** in ABSTRACT_ZENODO.md with actual DOI

3. **Create GitHub release** linking to Zenodo DOI

4. **Archive this directory** with DOI information

---

## Review Actions from V5 Assessment

The assessment PDF (`Analyse und EinschätzungreleaseV5.pdf`) highlighted several gaps to address before the public upload. We will:

- **Empirical social-data validation:** Link any real Gini/Load datasets only after anonymization and document provenance; keep the social model labeled as unvalidated until results exist.
- **Alternative constant comparisons:** Preserve Monte-Carlo comparisons against alternative constant pairs and report ΔAIC/Bayes factors alongside the 137-β framing.
- **Look-elsewhere transparency:** Surface the Operation Budget Burner scans and validation-session quantiles (see reference links above) so readers understand the preferred constant pair is notable but not unique.
- **Concise navigation:** Keep this bundle as the entry point for Zenodo and reference detailed theory/method documents from here to reduce overload for new readers.

These adjustments keep the governance/tooling claims reproducible while ensuring the hypothesis remains clearly marked as active research.

---

## Verification

**Before uploading, verify:**

```bash
# Check ZIP integrity
unzip -t Feldtheorie_v5.0.0_Source.zip

# Count files
unzip -l Feldtheorie_v5.0.0_Source.zip | wc -l
# Should show ~2173 files (full profile) or fewer when using --profile slim

# Check archive size
ls -lh Feldtheorie_v5.0.0_Source.zip
# Should be ~50 MB

# Review manifest
head -n 20 MANIFEST.txt
tail -n 20 MANIFEST.txt
```

**All checks should pass before upload.**

---

## Troubleshooting

**Problem:** ZIP file too large for Zenodo (>50 GB limit)
- **Solution:** Current size is 49.56 MB, well under limit

**Problem:** Need to make changes after generating artifacts
- **Solution:** Make changes, re-run `prepare_upload.py`

**Problem:** Papers look bad in Markdown on Zenodo
- **Solution:** Convert to PDF using pandoc:
  ```bash
  pandoc Paper_1_The_Fractal_Engine.md -o Paper_1.pdf
  pandoc Paper_2_Hypothesis_137_Beta.md -o Paper_2.pdf
  ```

**Problem:** Forgot to exclude something from ZIP
- **Solution:** Edit EXCLUSIONS in `prepare_upload.py`, re-run

---

## Design Philosophy

This release embodies three principles:

**1. Transparency**
- All methods documented
- All code open-source
- All limitations explicit

**2. Reproducibility**
- Complete source snapshot
- Version-pinned dependencies
- Integrity hashes for verification

**3. Intellectual Honesty**
- Tools labeled as "production"
- Theory labeled as "hypothesis"
- Falsification criteria provided
- Negative results welcomed

**This is how science should be done.**

---

## Contact

**Repository:** https://github.com/GenesisAeon/Feldtheorie
**Issues:** https://github.com/GenesisAeon/Feldtheorie/issues

---

**Generated:** 2025-11-23
**Script Version:** 5.0.0
**Status:** 🚀 READY FOR ZENODO

---

**Next action: Read UPLOAD_CHECKLIST.md and proceed to Zenodo.**
