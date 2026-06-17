"""Tests for hardware.neuromorphic.hfo2_detailed_spec."""

from __future__ import annotations

import json

from hardware.neuromorphic.hfo2_detailed_spec import (
    BOM_ENTRIES,
    HfO2ChipSpec,
    generate_all_specs,
    generate_bom_csv,
    generate_manufacturing_protocol,
    generate_spec_json,
)
from theory.afet import AFETConstants


class TestHfO2ChipSpec:
    def test_default_spec_values(self) -> None:
        spec = HfO2ChipSpec()
        assert spec.physical.hfo2_thickness_nm == 20.0
        assert spec.electrical.impedance_ohm == 221.74
        assert spec.electrical.resonance_freq_hz == AFETConstants.FREQ_RES
        assert spec.thermal.max_operating_temp_C == 87.0
        assert spec.thermal.sigma_phi_threshold == AFETConstants.SIGMA_PHI

    def test_cmos_compatible(self) -> None:
        spec = HfO2ChipSpec()
        assert spec.integration.cmos_compatible is True


class TestBOM:
    def test_bom_entries_non_empty(self) -> None:
        assert len(BOM_ENTRIES) > 0

    def test_bom_csv_generation(self, tmp_path) -> None:
        path = tmp_path / "bom.csv"
        generate_bom_csv(path)
        assert path.exists()
        content = path.read_text()
        assert "part" in content
        assert "TOTAL" in content

    def test_bom_total_positive(self) -> None:
        total = sum(e["cost_usd"] * e["qty"] for e in BOM_ENTRIES)
        assert total > 0


class TestManufacturingProtocol:
    def test_protocol_generated(self, tmp_path) -> None:
        spec = HfO2ChipSpec()
        path = tmp_path / "protocol.md"
        generate_manufacturing_protocol(spec, path)
        assert path.exists()
        content = path.read_text()
        assert "Manufacturing Protocol" in content
        assert "ALD" in content  # Atomic Layer Deposition
        assert "sigma_Phi" in content


class TestSpecJSON:
    def test_json_output(self, tmp_path) -> None:
        spec = HfO2ChipSpec()
        path = tmp_path / "spec.json"
        generate_spec_json(spec, path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "1.0"
        assert data["electrical"]["impedance_ohm"] == 221.74


class TestGenerateAllSpecs:
    def test_generates_all_files(self, tmp_path) -> None:
        payload = generate_all_specs(output_dir=tmp_path)
        assert (tmp_path / "hfo2_spec_v1.json").exists()
        assert (tmp_path / "bom.csv").exists()
        assert (tmp_path / "manufacturing_protocol.md").exists()
        assert (tmp_path / "hfo2_spec_v1.pdf").exists()
        assert "version" in payload
