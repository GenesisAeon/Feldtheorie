# v12.0.0 Release Folder (Draft) – AFET Consolidation Since V11

This folder is the **repo-conformant staging area** for the GitHub release **V12**.

## Purpose

Prepare a clear, auditable release package for work completed since V11, including:
- release notes (`RELEASE_NOTES_v12.0.0.md`)
- machine-readable manifest in tri-layer form (`v12_release_manifest.{yaml,json,md}`)
- GitHub release text draft (`GITHUB_RELEASE_BODY.md`)

## Logistic framing (Charter alignment)

- **R (open work):** medium; release text should still be finalized against the exact V11 baseline.
- **Θ (activation threshold):** reached for release scaffolding and structure.
- **β:** `4.8` (charter default sharpness).
- **ζ(R):** currently damped through structured artifacts and explicit TODO markers.
- Transition state: `σ(β(R-Θ))` is on the steep flank—scaffold is active, final curation pending.

## Suggested finalization workflow

1. Confirm the canonical V11 reference (tag, commit, or folder baseline).
2. Generate commit/file delta for `V11..HEAD`.
3. Fill placeholders in `RELEASE_NOTES_v12.0.0.md` and `GITHUB_RELEASE_BODY.md`.
4. Keep tri-layer parity between `v12_release_manifest.yaml/json/md`.

