import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
YAML_PATH = ROOT / "entropy_geometric_waste.yaml"
JSON_PATH = ROOT / "entropy_geometric_waste.json"


def load_yaml():
    with YAML_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_json():
    with JSON_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_trilayer_keys_align():
    ydoc = load_yaml()
    jdoc = load_json()
    for key in ["meta", "sources", "theses", "bridges", "null_models", "falsifiability"]:
        assert key in ydoc, f"missing key '{key}' in YAML"
        assert key in jdoc, f"missing key '{key}' in JSON"

    for key in ["sources", "null_models"]:
        assert ydoc[key] == jdoc[key], f"Mismatch in {key} between YAML and JSON"


def test_utac_alignment_is_type6():
    ydoc = load_yaml()
    utac = ydoc["meta"].get("utac_alignment", {})
    assert utac.get("type") == "type-6-implosion", "UTAC alignment must remain type-6 implosion"
    readiness = utac.get("readiness_hooks", [])
    assert any(
        "UTAC v2.5" in hook for hook in readiness
    ), "Readiness hook should reference UTAC v2.5 bridge"


def test_thesis_fields_present():
    ydoc = load_yaml()
    theses = ydoc.get("theses", {})
    required = {"kubus_to_spiral", "topological_defects", "bekenstein_hawking_bridge"}
    assert required.issubset(theses.keys()), "All core theses must be present"
    for name in required:
        thesis = theses[name]
        assert "statement" in thesis and thesis["statement"], f"Thesis '{name}' needs a statement"
        assert (
            "observables" in thesis and thesis["observables"]
        ), f"Thesis '{name}' needs observables"
        assert (
            "falsifiability" in thesis and thesis["falsifiability"]
        ), f"Thesis '{name}' needs falsifiability hooks"


if __name__ == "__main__":
    test_trilayer_keys_align()
    test_utac_alignment_is_type6()
    test_thesis_fields_present()
    print("All entropy_geometric_waste checks passed.")
