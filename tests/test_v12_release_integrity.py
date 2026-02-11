from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = REPO_ROOT / "releases" / "v12.0.0"
YAML_MANIFEST = RELEASE_DIR / "v12_release_manifest.yaml"
JSON_MANIFEST = RELEASE_DIR / "v12_release_manifest.json"
MD_MANIFEST = RELEASE_DIR / "v12_release_manifest.md"
RELEASE_FILES = [
    RELEASE_DIR / "README.md",
    RELEASE_DIR / "RELEASE_NOTES_v12.0.0.md",
    RELEASE_DIR / "GITHUB_RELEASE_BODY.md",
    YAML_MANIFEST,
    JSON_MANIFEST,
    MD_MANIFEST,
]


@pytest.mark.skipif(yaml is None, reason="PyYAML is not installed")
def test_manifest_trilayer_consistency_and_artifact_existence() -> None:
    yaml_payload = yaml.safe_load(YAML_MANIFEST.read_text(encoding="utf-8"))
    json_payload = json.loads(JSON_MANIFEST.read_text(encoding="utf-8"))

    assert yaml_payload["release"]["version"] == "12.0.0"
    assert json_payload["release"]["version"] == "12.0.0"
    assert yaml_payload["release"] == json_payload["release"]
    assert yaml_payload["baseline"] == json_payload["baseline"]
    assert yaml_payload["logistic_state"] == json_payload["logistic_state"]

    yaml_artifacts = [entry["path"] for entry in yaml_payload["artifacts"]]
    json_artifacts = [entry["path"] for entry in json_payload["artifacts"]]
    assert yaml_artifacts == json_artifacts

    for artifact in yaml_artifacts:
        assert (REPO_ROOT / artifact).exists(), f"Missing artifact listed in manifest: {artifact}"


def test_markdown_manifest_matches_release_metadata() -> None:
    md_text = MD_MANIFEST.read_text(encoding="utf-8")

    assert "**Version:** 12.0.0" in md_text
    assert "**Reference Value:** `fb42ac8`" in md_text
    assert "**σ(β(R-Θ)):** release-ready" in md_text


def test_release_files_do_not_contain_todo_or_placeholders() -> None:
    marker_candidates = ("TODO-V11", "TODO:", "placeholder")
    for file_path in RELEASE_FILES:
        text = file_path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in marker_candidates:
            if marker == "placeholder":
                assert marker not in lowered, f"Found unresolved marker '{marker}' in {file_path}"
            else:
                assert marker not in text, f"Found unresolved marker '{marker}' in {file_path}"


def test_release_directory_has_no_png_or_tmp_files() -> None:
    forbidden_suffixes = {".png", ".tmp"}
    forbidden = [p for p in RELEASE_DIR.iterdir() if p.is_file() and p.suffix.lower() in forbidden_suffixes]
    assert forbidden == []
