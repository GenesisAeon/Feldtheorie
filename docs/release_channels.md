# Release Channels

> **Purpose:** Explain the dual-channel release strategy so contributors and users
> know which version number applies where.

---

## Two Channels, One Repository

Feldtheorie maintains **two independent versioning streams** that serve
different audiences and governance rules:

| Aspect | Package Channel | Research Channel |
|--------|----------------|-----------------|
| **What** | Python package SemVer | Narrative release labels |
| **Example** | `5.0.0` | `v10.2 Platinum`, `9.0.0-alpha` |
| **Governs** | `pyproject.toml`, `pip install`, Zenodo DOI | README badges, release notes, scientific papers |
| **Audience** | Developers, CI, PyPI | Researchers, collaborators, publications |
| **Bump rule** | SemVer (major.minor.patch) | Milestone-driven, may include codenames |
| **Source of truth** | `VERSION.yaml → package_version` | `VERSION.yaml → release_stream / stable_version / alpha_version` |
| **Sync tool** | `scripts/update_version.py --apply` | Same tool updates README badges |

---

## Why Two Channels?

The research programme (UTAC, Tesseract physics, entropy governance) evolves
on a narrative arc — `v6 Entropy`, `v9 Harmonic Emergence`, `v10 Platinum` —
that reflects conceptual milestones rather than code-breaking changes.

The Python package, however, follows strict **Semantic Versioning** to ensure
`pip install feldtheorie` remains predictable:

- **Major** — Breaking API changes (e.g. renamed analysis entry points)
- **Minor** — New features that are backward-compatible
- **Patch** — Bug fixes, documentation, metadata updates

These two streams are **intentionally decoupled**: a narrative jump from v10 to
v12 does not imply a package major bump.  Conversely, a package 5.x → 6.0
major version may occur without a new narrative milestone.

---

## VERSION.yaml Structure

```yaml
# Package Channel
package_version: "5.0.0"

# Research Channel
release_stream: "v10.2 Platinum"
stable_version: "6.0.0"
alpha_version: "9.0.0-alpha"
```

All downstream references (pyproject.toml, README badges, release metadata)
are derived from this file by `scripts/update_version.py`.

---

## Governance Rules

1. **Single source of truth:** Edit `VERSION.yaml`, then run
   `python scripts/update_version.py --apply` to propagate.
2. **CI enforcement:** The `doc-freshness-guard` workflow runs
   `update_version.py --check` on every push to verify consistency.
3. **No orphan bumps:** Never edit `pyproject.toml` version or README badges
   directly — always go through `VERSION.yaml`.
4. **Codename convention:** Research channel releases may carry codenames
   (Platinum, Gardener, Oracle) that appear in `release_stream` but not in
   the package version.

---

## Mapping Table (Current)

| Research Label | Package Version | Status |
|---------------|----------------|--------|
| v13.0.0 | 6.0.0 | Current |
| v12.0.0 AFET Consolidation | 5.0.0 | Superseded |
| v10.2 Platinum | 5.0.0 | Superseded |
| v9.0.0-alpha | 5.0.0 | Alpha |
| v6.0.0 Entropy | 5.0.0 | Stable baseline |

---

## Release Checklist

When cutting a release, ensure:

1. `VERSION.yaml` reflects the new version(s)
2. `python scripts/update_version.py --apply` runs clean
3. `python scripts/update_badges.py --apply` syncs test counts
4. `python scripts/check_field_health.py` passes (Field Health Contract)
5. `python scripts/check_claim_evidence.py` shows 0 missing artifacts
6. `CHANGELOG.md` and `NEWS.md` are updated
7. `CITATION.cff` DOI matches the Zenodo release
