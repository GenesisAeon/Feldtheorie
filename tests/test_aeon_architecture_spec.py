from __future__ import annotations

from pathlib import Path

from aeon.modules.architecture_spec import (
    CORE_MODULE_REGISTRY,
    extract_aeon_layers,
    get_core_module_contracts,
)


def test_extract_aeon_layers_from_bauplan() -> None:
    source = Path("releases/V6-Plans_etc/Finalize/architecture/ChatGPT5.1_AeonV1.0Bauplan.txt")
    layers = extract_aeon_layers(source)

    assert set(layers.keys()) >= {"nullkern", "aeonshell", "agent_layer", "physical_layer"}
    assert "zeitlose" in layers["nullkern"].description.lower() or "zuständ" in layers["nullkern"].description.lower()


def test_core_module_contracts_cover_requested_components() -> None:
    contracts = get_core_module_contracts()

    required = {
        "MasterGPT",
        "TutorGPT",
        "AeonShell",
        "Sigillin",
        "CREP",
        "GenesisMath",
        "BioGPT",
        "CosmoGPT",
        "UnifiedMandala",
    }
    assert required.issubset(set(contracts.keys()))

    for name in required:
        assert contracts[name]["responsibility"]
        assert contracts[name]["interfaces"]


def test_registry_is_stable_and_sorted() -> None:
    assert CORE_MODULE_REGISTRY
    names = [m.name for m in CORE_MODULE_REGISTRY]
    assert names == sorted(names)
