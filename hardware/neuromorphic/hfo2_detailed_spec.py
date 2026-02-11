"""HfO2 neuromorphic chip detailed specifications.

Generates production-ready specification documents for a HfO2-based
RRAM (Resistive RAM) chip with AFET-integrated thermal monitoring.

Outputs:
  - Bill of Materials (CSV)
  - Manufacturing protocol (Markdown)
  - Specification summary (JSON, optionally PDF via matplotlib)

The design targets:
  - Layer thickness: 10-50 nm HfO2 thin film
  - Electrodes: TiN (bottom), Pt or TiN (top)
  - Operating voltage: 1-3 V
  - Switching speed: < 10 ns
  - Impedance: Z ~ 221.74 Ohm (matched to AFET resonance)
  - Resonance frequency: 13.5 MHz
  - Thermal monitoring: sigma_Phi-based at 87 C threshold

Usage:
    python -m hardware.neuromorphic.hfo2_detailed_spec
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from theory.afet import AFETConstants


# ---------------------------------------------------------------------------
# Specification data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PhysicalProperties:
    hfo2_thickness_nm: float = 20.0
    hfo2_dielectric_constant: float = 25.0
    bottom_electrode: str = "TiN"
    top_electrode: str = "Pt"
    electrode_thickness_nm: float = 50.0
    substrate: str = "Si/SiO2"
    active_area_um2: float = 100.0  # 10 um x 10 um


@dataclass(frozen=True)
class ElectricalCharacteristics:
    set_voltage_V: float = 1.5
    reset_voltage_V: float = -1.2
    read_voltage_V: float = 0.2
    lrs_resistance_ohm: float = 1e3  # Low resistance state
    hrs_resistance_ohm: float = 1e6  # High resistance state
    switching_speed_ns: float = 8.0
    endurance_cycles: float = 1e9
    retention_s: float = 3.15e7  # ~1 year
    impedance_ohm: float = 221.74  # AFET resonance match
    resonance_freq_hz: float = AFETConstants.FREQ_RES


@dataclass(frozen=True)
class ThermalManagement:
    max_operating_temp_C: float = 87.0  # AFET threshold
    heat_dissipation_W_cm2: float = 0.5
    thermal_conductivity_W_mK: float = 1.1  # HfO2
    cooling_method: str = "passive (heat spreader + PCB)"
    sigma_phi_monitoring: bool = True
    sigma_phi_threshold: float = AFETConstants.SIGMA_PHI


@dataclass(frozen=True)
class IntegrationSpec:
    cmos_compatible: bool = True
    cmos_node_nm: int = 28
    stackable_3d: bool = True
    max_stack_layers: int = 8
    interconnect: str = "Cu damascene"
    io_protocol: str = "SPI + I2C"


@dataclass
class HfO2ChipSpec:
    """Complete HfO2 chip specification."""

    version: str = "1.0"
    physical: PhysicalProperties = field(default_factory=PhysicalProperties)
    electrical: ElectricalCharacteristics = field(default_factory=ElectricalCharacteristics)
    thermal: ThermalManagement = field(default_factory=ThermalManagement)
    integration: IntegrationSpec = field(default_factory=IntegrationSpec)


# ---------------------------------------------------------------------------
# Bill of Materials
# ---------------------------------------------------------------------------

BOM_ENTRIES = [
    {"part": "HfO2 target (99.99%)", "qty": 1, "unit": "ea", "cost_usd": 450.00, "supplier": "Kurt J. Lesker"},
    {"part": "TiN target (99.9%)", "qty": 2, "unit": "ea", "cost_usd": 320.00, "supplier": "Kurt J. Lesker"},
    {"part": "Pt target (99.99%)", "qty": 1, "unit": "ea", "cost_usd": 890.00, "supplier": "Kurt J. Lesker"},
    {"part": "Si/SiO2 wafer 200mm", "qty": 25, "unit": "ea", "cost_usd": 45.00, "supplier": "University Wafer"},
    {"part": "Photomask set", "qty": 1, "unit": "set", "cost_usd": 2500.00, "supplier": "Compugraphics"},
    {"part": "ALD precursor (TDMA-Hf)", "qty": 1, "unit": "500g", "cost_usd": 680.00, "supplier": "Strem Chemicals"},
    {"part": "PCB carrier board", "qty": 50, "unit": "ea", "cost_usd": 12.00, "supplier": "JLCPCB"},
    {"part": "SPI/I2C interface IC", "qty": 50, "unit": "ea", "cost_usd": 3.50, "supplier": "Mouser"},
    {"part": "Heat spreader (Cu)", "qty": 50, "unit": "ea", "cost_usd": 8.00, "supplier": "Mouser"},
    {"part": "Wire bonding supplies", "qty": 1, "unit": "kit", "cost_usd": 350.00, "supplier": "Kulicke & Soffa"},
]


def generate_bom_csv(output_path: Path) -> None:
    """Write Bill of Materials to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["part", "qty", "unit", "cost_usd", "supplier"])
        writer.writeheader()
        total = 0.0
        for entry in BOM_ENTRIES:
            writer.writerow(entry)
            total += entry["cost_usd"] * entry["qty"]
        writer.writerow({"part": "TOTAL", "qty": "", "unit": "", "cost_usd": round(total, 2), "supplier": ""})
    print(f"BOM -> {output_path}")


# ---------------------------------------------------------------------------
# Manufacturing protocol
# ---------------------------------------------------------------------------


def generate_manufacturing_protocol(spec: HfO2ChipSpec, output_path: Path) -> None:
    """Write manufacturing protocol as Markdown."""
    lines = [
        "# HfO2 RRAM Manufacturing Protocol",
        "",
        f"**Specification Version:** {spec.version}",
        f"**Target Node:** {spec.integration.cmos_node_nm} nm",
        "",
        "## 1. Substrate Preparation",
        "",
        f"- Substrate: {spec.physical.substrate} wafer",
        "- Clean: SC-1 + SC-2 + HF dip (standard RCA clean)",
        "- Dry: N2 blow + 150 C hotplate 5 min",
        "",
        "## 2. Bottom Electrode Deposition",
        "",
        f"- Material: {spec.physical.bottom_electrode}",
        f"- Thickness: {spec.physical.electrode_thickness_nm} nm",
        "- Method: DC magnetron sputtering",
        "- Conditions: Ar 5 mTorr, 200 W, substrate at 300 C",
        "- Rate: ~2 nm/min",
        "",
        "## 3. HfO2 Active Layer",
        "",
        f"- Thickness: {spec.physical.hfo2_thickness_nm} nm",
        "- Method: Atomic Layer Deposition (ALD)",
        "- Precursor: TDMA-Hf + H2O",
        "- Temperature: 250 C",
        f"- Cycles: ~{int(spec.physical.hfo2_thickness_nm * 5)} (0.1 nm/cycle)",
        "- Post-deposition anneal: 400 C, 30 min, N2",
        "",
        "## 4. Top Electrode Deposition",
        "",
        f"- Material: {spec.physical.top_electrode}",
        f"- Thickness: {spec.physical.electrode_thickness_nm} nm",
        "- Method: E-beam evaporation",
        "- Rate: ~1 nm/min",
        "",
        "## 5. Patterning",
        "",
        f"- Active area: {spec.physical.active_area_um2} um^2",
        "- Lithography: i-line (365 nm) or e-beam for sub-um",
        "- Etch: RIE (Cl2/BCl3 for TiN, Ar for Pt)",
        "",
        "## 6. Forming / Electroforming",
        "",
        f"- Forming voltage: {spec.electrical.set_voltage_V + 1.0:.1f} V (first cycle)",
        "- Compliance current: 100 uA",
        "- After forming: device in LRS",
        "",
        "## 7. Packaging",
        "",
        "- Wire bonding to PCB carrier",
        f"- Interface: {spec.integration.io_protocol}",
        f"- Heat spreader: {spec.thermal.cooling_method}",
        "",
        "## 8. AFET Thermal Monitoring",
        "",
        f"- Max operating temperature: {spec.thermal.max_operating_temp_C} C",
        f"- sigma_Phi threshold: {spec.thermal.sigma_phi_threshold}",
        f"- Target impedance: {spec.electrical.impedance_ohm} Ohm",
        f"- Resonance frequency: {spec.electrical.resonance_freq_hz / 1e6:.1f} MHz",
        "",
        "## 9. Quality Control",
        "",
        "- Endurance test: 10^6 cycles minimum",
        "- Retention test: 85 C, 10^4 s",
        "- Yield target: > 95%",
        "- sigma_Phi validation: must stay within metastable corridor",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Protocol -> {output_path}")


# ---------------------------------------------------------------------------
# Spec summary (JSON + optional PDF)
# ---------------------------------------------------------------------------


def generate_spec_json(spec: HfO2ChipSpec, output_path: Path) -> dict:
    """Write full spec as JSON."""
    payload = {
        "version": spec.version,
        "physical": asdict(spec.physical),
        "electrical": asdict(spec.electrical),
        "thermal": asdict(spec.thermal),
        "integration": asdict(spec.integration),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Spec JSON -> {output_path}")
    return payload


def generate_spec_pdf(spec: HfO2ChipSpec, output_path: Path) -> None:
    """Generate a PDF summary of the chip specification using matplotlib."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"HfO2 RRAM Chip Specification v{spec.version}", fontsize=14, fontweight="bold")

    # Physical properties
    ax = axes[0, 0]
    ax.axis("off")
    ax.set_title("Physical Properties", fontweight="bold")
    props = [
        f"HfO2 thickness: {spec.physical.hfo2_thickness_nm} nm",
        f"eps_r: {spec.physical.hfo2_dielectric_constant}",
        f"Bottom electrode: {spec.physical.bottom_electrode}",
        f"Top electrode: {spec.physical.top_electrode}",
        f"Active area: {spec.physical.active_area_um2} um^2",
    ]
    ax.text(0.1, 0.5, "\n".join(props), transform=ax.transAxes, fontsize=10,
            verticalalignment="center", family="monospace")

    # Electrical
    ax = axes[0, 1]
    ax.axis("off")
    ax.set_title("Electrical Characteristics", fontweight="bold")
    elec = [
        f"V_set: {spec.electrical.set_voltage_V} V",
        f"V_reset: {spec.electrical.reset_voltage_V} V",
        f"Switching: {spec.electrical.switching_speed_ns} ns",
        f"Z: {spec.electrical.impedance_ohm} Ohm",
        f"f_res: {spec.electrical.resonance_freq_hz / 1e6:.1f} MHz",
    ]
    ax.text(0.1, 0.5, "\n".join(elec), transform=ax.transAxes, fontsize=10,
            verticalalignment="center", family="monospace")

    # Thermal
    ax = axes[1, 0]
    ax.axis("off")
    ax.set_title("Thermal Management", fontweight="bold")
    therm = [
        f"T_max: {spec.thermal.max_operating_temp_C} C",
        f"Heat: {spec.thermal.heat_dissipation_W_cm2} W/cm^2",
        f"k: {spec.thermal.thermal_conductivity_W_mK} W/(m*K)",
        f"sigma_Phi threshold: {spec.thermal.sigma_phi_threshold}",
        f"Cooling: {spec.thermal.cooling_method}",
    ]
    ax.text(0.1, 0.5, "\n".join(therm), transform=ax.transAxes, fontsize=10,
            verticalalignment="center", family="monospace")

    # Integration
    ax = axes[1, 1]
    ax.axis("off")
    ax.set_title("Integration", fontweight="bold")
    integ = [
        f"CMOS: {spec.integration.cmos_node_nm} nm",
        f"3D stack: {spec.integration.max_stack_layers} layers",
        f"Interconnect: {spec.integration.interconnect}",
        f"IO: {spec.integration.io_protocol}",
    ]
    ax.text(0.1, 0.5, "\n".join(integ), transform=ax.transAxes, fontsize=10,
            verticalalignment="center", family="monospace")

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(output_path), dpi=150)
    plt.close(fig)
    print(f"Spec PDF -> {output_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def generate_all_specs(output_dir: Path | None = None) -> dict:
    """Generate all HfO2 specification documents."""
    print("=" * 60)
    print("HfO2 Neuromorphic Chip -- Detailed Specifications")
    print("=" * 60)

    spec = HfO2ChipSpec()

    if output_dir is None:
        output_dir = Path("hardware/neuromorphic")

    output_dir.mkdir(parents=True, exist_ok=True)

    payload = generate_spec_json(spec, output_dir / "hfo2_spec_v1.json")
    generate_bom_csv(output_dir / "bom.csv")
    generate_manufacturing_protocol(spec, output_dir / "manufacturing_protocol.md")
    generate_spec_pdf(spec, output_dir / "hfo2_spec_v1.pdf")

    print("\nAll specifications generated.")
    return payload


if __name__ == "__main__":
    generate_all_specs()
