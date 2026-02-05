"""Tests for LanternNet index building and σ(β(R-Θ)) readiness alignment."""
from __future__ import annotations

from pathlib import Path

from scripts.update_lantern_net import build_lantern_net


def _sample_lantern_hub(readiness: float | None) -> dict:
    return {
        "meta": {
            "version": "v13.0.0",
            "created": "2026-02-05T14:46:37+00:00",
            "logistic_frame": {"zeta": "ledger-zeta", "sigma": 0.5},
            "summary": {},
            "sources": {},
        },
        "lanterns": [
            {
                "id": "exp-neuroprofile-001",
                "name": "NeuroProfile Resonance Bridge",
                "order_parameter": "sigma_phi_proxy",
                "type": "experiment",
                "domain": "neuro",
                "status": "active",
                "readiness": readiness,
                "theta": 0.72,
                "beta": 4.8,
                "data_assets": [],
            }
        ],
    }


def _sample_bootstrap_ledger() -> dict:
    return {
        "meta": {"document": "Bootstrap Ledger – LanternNet", "version": "v13.0.0"},
        "entries": [
            {
                "id": "bootstrap-run-0007",
                "module": "NeuroProfile Resonance Bridge",
                "module_id": "exp-neuroprofile-001",
                "logistic_parameters": {
                    "R": 0.91,
                    "Theta": 0.67,
                    "beta": 6.1,
                    "zeta": "ledger-zeta-override",
                },
                "sigma_phi_range": [0.12, 0.44],
            }
        ],
    }


def test_ledger_logistic_parameters_override_defaults() -> None:
    """Ledger-derived (R, Θ, β, ζ) should override defaults near σ(β(R-Θ))."""
    payload = build_lantern_net(
        lantern_hub=_sample_lantern_hub(readiness=None),
        bootstrap_ledger=_sample_bootstrap_ledger(),
        crep_ledger=None,
    )

    lantern = payload["lanterns"][0]
    logistic = lantern["logistic_parameters"]

    assert logistic["R"] == 0.91
    assert logistic["Theta"] == 0.67
    assert logistic["beta"] == 6.1
    assert logistic["zeta"] == "ledger-zeta-override"
    assert lantern["readiness"] == 0.91


def test_readiness_prefers_config_when_provided() -> None:
    """Config readiness should remain when present, even if ledger R exists."""
    payload = build_lantern_net(
        lantern_hub=_sample_lantern_hub(readiness=0.42),
        bootstrap_ledger=_sample_bootstrap_ledger(),
        crep_ledger=None,
    )

    lantern = payload["lanterns"][0]
    logistic = lantern["logistic_parameters"]

    assert lantern["readiness"] == 0.42
    assert logistic["R"] == 0.91


def test_documentation_and_coverage_detection(tmp_path: Path, monkeypatch) -> None:
    """Documentation and test coverage should resolve relative to base_path."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    readme_path = doc_dir / "README.md"
    methodology_path = doc_dir / "methodology.md"
    roadmap_path = doc_dir / "roadmap.md"
    readme_path.write_text("# Lantern README\n", encoding="utf-8")
    methodology_path.write_text("# Lantern Methodology\n", encoding="utf-8")
    roadmap_path.write_text("# Lantern Roadmap\n", encoding="utf-8")

    test_path = tmp_path / "tests" / "test_module.py"
    test_path.parent.mkdir()
    test_path.write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.update_lantern_net.MODULE_TEST_MAPPINGS",
        {"exp-neuroprofile-001": ["tests/test_module.py"]},
    )

    lantern_hub = _sample_lantern_hub(readiness=0.77)
    lantern_hub["lanterns"][0]["documentation"] = {
        "readme": "docs/README.md",
        "methodology": "docs/methodology.md",
        "roadmap": "docs/roadmap.md",
    }

    payload = build_lantern_net(
        lantern_hub=lantern_hub,
        bootstrap_ledger=None,
        crep_ledger=None,
        base_path=tmp_path,
    )

    lantern = payload["lanterns"][0]
    assert lantern["documentation"]["readme"] == "docs/README.md"
    assert lantern["morfit_layers"]["documentation"] == "active"
    assert lantern["test_coverage"]["status"] == "passing"


def test_mandala_bridge_validation(tmp_path: Path) -> None:
    """Mandala bridge status should validate when the PSRM schema exists."""
    schema_path = tmp_path / "schemas" / "psrm_map.schema.json"
    schema_path.parent.mkdir(parents=True)
    schema_path.write_text("{}", encoding="utf-8")

    payload = build_lantern_net(
        lantern_hub=_sample_lantern_hub(readiness=0.88),
        bootstrap_ledger=None,
        crep_ledger=None,
        base_path=tmp_path,
    )

    mandala = payload["lanterns"][0]["mandala_bridge"]
    assert mandala["status"] == "validated"
    assert mandala["schema"] == "schemas/psrm_map.schema.json"
