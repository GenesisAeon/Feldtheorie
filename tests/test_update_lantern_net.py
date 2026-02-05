"""Tests for LanternNet update script."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("update_lantern_net", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_lantern_net_matches_config():
    module = _load_module(Path("scripts/update_lantern_net.py"))
    lantern_hub = module._load_yaml(Path("v9_alpha/config/lantern_hub.yaml"))
    payload = module.build_lantern_net(lantern_hub)

    assert "lanterns" in payload
    assert len(payload["lanterns"]) == len(lantern_hub.get("lanterns", []))

    sample = payload["lanterns"][0]
    assert "module_name" in sample
    assert "logistic_parameters" in sample
    assert "ethics_tags" in sample
    assert "consent_requirements" in sample
    assert "documentation" in sample
    assert "morfit_layers" in sample


def test_write_trilayer_outputs(tmp_path):
    module = _load_module(Path("scripts/update_lantern_net.py"))
    lantern_hub = module._load_yaml(Path("v9_alpha/config/lantern_hub.yaml"))
    payload = module.build_lantern_net(lantern_hub)

    module.write_trilayer(tmp_path, payload)

    yaml_path = tmp_path / "lantern_net.yaml"
    json_path = tmp_path / "lantern_net.json"
    md_path = tmp_path / "lantern_net.md"

    assert yaml_path.exists()
    assert json_path.exists()
    assert md_path.exists()

    with yaml_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    assert len(loaded["lanterns"]) == len(payload["lanterns"])
    assert "consent_prompt" in loaded["meta"]
    assert "ledger_refs" in loaded["meta"]
