# Release Guide

This is a short pointer document. The authoritative release process for
Feldtheorie is described in [`docs/release_channels.md`](docs/release_channels.md),
which documents the project's **dual-channel versioning** scheme:

- **Package Channel** (`VERSION.yaml → package_version`) — strict SemVer,
  governs `pyproject.toml` and PyPI.
- **Research Channel** (`VERSION.yaml → release_stream` /
  `stable_version` / `alpha_version`) — narrative milestone labels,
  governs README badges, release notes, and the git tags
  (`v*.*.*`) that trigger `.github/workflows/release.yml`.

These two channels are intentionally decoupled — see
`docs/release_channels.md` for the full rationale and the release
checklist (`VERSION.yaml` → `update_version.py --apply` →
`update_badges.py --apply` → `check_field_health.py` →
`check_claim_evidence.py` → `CHANGELOG.md`/`NEWS.md` → `CITATION.cff`).

## Cutting a release

1. Follow the "Release Checklist" in `docs/release_channels.md`.
2. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z` (research-channel
   label, may not equal the package SemVer — see above).
3. `.github/workflows/release.yml` builds, publishes to PyPI, creates the
   GitHub Release, and (once `ZENODO_TOKEN` is configured) archives to
   Zenodo using `.zenodo.json`.

## GenesisAeon-ecosystem dependency pins

If this package ever depends on other `GenesisAeon/*` packages, pin them
with `>=` lower bounds matching the minimum version that provides the API
this package relies on — avoid exact (`==`) pins for ecosystem
dependencies.
