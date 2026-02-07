from __future__ import annotations

from analysis.hfo2_interface_spec import get_hfo2_interface_contract


def test_hfo2_contract_exposes_required_sections() -> None:
    contract = get_hfo2_interface_contract()

    assert set(contract.keys()) == {"name", "inputs", "outputs", "constraints", "notes"}
    assert "pulse_sequence" in contract["inputs"]
    assert "sigma_phi_estimate" in contract["outputs"]
