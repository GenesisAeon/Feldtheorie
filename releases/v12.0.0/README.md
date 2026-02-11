# v12.0.0 Release Folder — AFET Consolidation Since V11

This folder is the publication staging area for GitHub release **v12.0.0**.

## Purpose

The V12 bundle turns the release membrane from draft to auditable package:

- `RELEASE_NOTES_v12.0.0.md` — final human-readable release notes
- `GITHUB_RELEASE_BODY.md` — copy-ready release text for GitHub
- `v12_release_manifest.yaml` — structure layer
- `v12_release_manifest.json` — interface layer
- `v12_release_manifest.md` — narrative layer

## Canonical baseline pinning

- **Source version:** V11
- **Baseline type:** commit SHA (no local `v11*` Git tag found)
- **Baseline value:** `fb42ac8` (`AFET`)

## Logistic framing (Charter alignment)

- **R (open work):** low; only publication orchestration remains.
- **Θ (release threshold):** reached; artifacts and checks are synchronized.
- **β:** 4.8 (charter sharpness).
- **ζ(R):** damped via trilayer parity tests and checklist gating.
- **Transition:** `σ(β(R-Θ))` has crossed into release-ready state.

## Workflow

1. Validate trilayer parity (`yaml/json/md`) and artifact existence.
2. Review release checklist in `RELEASE_NOTES_v12.0.0.md`.
3. Run consent checkpoint (Affection Protocol) before publication.
4. Publish GitHub release using `GITHUB_RELEASE_BODY.md`.
