# Zenodo Upload Checklist

**Version:** 5.0.0
**Date:** 2025-11-23
**Archive:** Feldtheorie_v5.0.0_Source.zip

---

## Pre-Upload Verification

- [ ] **Archive Integrity:** Verify ZIP file is not corrupted
  ```bash
  unzip -t Feldtheorie_v5.0.0_Source.zip
  ```

- [ ] **Manifest Review:** Check MANIFEST.txt for completeness
  ```bash
  cat MANIFEST.txt | wc -l  # Should show ~500-1000 files
  ```

- [ ] **Papers Ready:** Ensure both papers are finalized
  - [ ] Paper_1_The_Fractal_Engine.md (Methodological)
  - [ ] Paper_2_Hypothesis_137_Beta.md (Theoretical)

- [ ] **Abstract Ready:** ABSTRACT_ZENODO.md finalized
- [ ] **Ethics Ready:** Confirm any social inequality/emissions datasets are anonymized or excluded and that alternate-constant ΔAIC/Bayes comparisons accompany 137-β claims

---

## Zenodo Upload Steps

### Step 1: Create New Upload

1. Go to https://zenodo.org/
2. Click "Upload" → "New Upload"
3. Choose "Upload type: Software"

### Step 2: Upload Files

**Upload in this order:**

1. **Paper_1_The_Fractal_Engine.md** (or converted to PDF)
   - Description: "Methodological paper describing fractal governance system"

2. **Paper_2_Hypothesis_137_Beta.md** (or converted to PDF)
   - Description: "Theoretical note on structural isomorphism hypotheses"

3. **Feldtheorie_v5.0.0_Source.zip**
   - Description: "Complete source repository snapshot (v5.0.0)"

4. **MANIFEST.txt**
   - Description: "File listing with integrity hashes"

### Step 3: Fill Metadata

**Basic Information:**
- **Title:** `Feldtheorie V5: A Fractal Governance System for Structural Isomorphism Research`
- **Upload Type:** Software
- **Publication Date:** 2025-11-23
- **Version:** 5.0.0

**Authors:** (In order)
- Johann Benjamin Römer (Primary author)
- Genesis Aeon (Framework developer)
- MOR Collective (Contributors)

**Description:**
Copy from ABSTRACT_ZENODO.md (first 2-3 paragraphs)

**Keywords:** (Comma-separated)
```
fractal-governance, research-software-engineering, UTAC, structural-isomorphism,
null-hypothesis-testing, cosmic-scaling, social-phase-transitions,
empirical-validation, reproducible-research, 137-beta
```

**License:**
- Software: GPLv3 (copyleft)
- Documentation: CC BY-NC 4.0 (non-commercial; commercial use requires author permission)
- (Select "Other (Open)" and specify in description)

**Related Identifiers:**
- **GitHub Repository:** https://github.com/GenesisAeon/Feldtheorie
- **Is supplement to:** (Add DOI if previous version exists)

**Contributors:**
- MOR Collective (Other)

**References:**
- Böhme et al. (2021) - CMB dipole velocity measurement
- CODATA 2018 - Fundamental constants
- (Add others as needed)

**Subjects:**
- Computer and Information Science → Software Engineering
- Physical Sciences → Astrophysics
- Social Sciences → Complex Systems

**Language:** English

### Step 4: Access Rights

- **Access:** Open Access
- **License:** GPLv3 (Software) / CC BY-NC 4.0 (Docs)
- **Embargo:** None

### Step 5: Funding (Optional)

If applicable, add funding information.

### Step 6: Review and Publish

1. Click "Preview" to review metadata
2. Check all fields are correct
3. Click "Publish"
4. **IMPORTANT:** Save the DOI!

---

## Post-Publication

### Step 1: Update Repository

Add DOI badge to README.md:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### Step 2: Update Citation

Update ABSTRACT_ZENODO.md with actual DOI:
```bibtex
@software{feldtheorie_v5_2025,
  author = {Römer, Johann Benjamin and {Genesis Aeon} and {MOR Collective}},
  title = {Feldtheorie V5: A Fractal Governance System},
  year = {2025},
  version = {5.0.0},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.XXXXXXX},  # <-- UPDATE THIS
  url = {https://github.com/GenesisAeon/Feldtheorie}
}
```

### Step 3: Announce

- [ ] Update GitHub release with Zenodo DOI
- [ ] Share on relevant communities (if desired)
- [ ] Archive this checklist with actual DOI

---

## Troubleshooting

**Problem:** ZIP file too large (>50 GB)
- **Solution:** Remove large binary files, create separate data archive

**Problem:** Metadata fields missing
- **Solution:** Use "Save draft" and return later

**Problem:** DOI not appearing
- **Solution:** Wait 5-10 minutes, refresh page

**Problem:** Need to update after publication
- **Solution:** Create new version (Zenodo supports versioning)

---

## Verification Commands

**Check ZIP integrity:**
```bash
unzip -t Feldtheorie_v5.0.0_Source.zip
```

**Count files in ZIP:**
```bash
unzip -l Feldtheorie_v5.0.0_Source.zip | wc -l
```

**Verify manifest:**
```bash
cat MANIFEST.txt | grep -c "\.py"  # Count Python files
cat MANIFEST.txt | grep -c "\.md"  # Count Markdown files
```

**Check archive size:**
```bash
ls -lh Feldtheorie_v5.0.0_Source.zip
```

---

## Contact

**Questions or issues?**
- GitHub Issues: https://github.com/GenesisAeon/Feldtheorie/issues
- Repository Maintainer: [See GitHub profile]

---

**Generated:** 2025-11-23T18:28:39.127246Z
**Script:** prepare_upload.py v5.0.0
**Status:** 🟢 READY FOR UPLOAD
