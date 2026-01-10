"""
Hardware Adapter
================

Part of the GenesisAeon Feldtheorie project.
License: LGPL-3.0-or-later

Abstraktionsschicht für EEG-Hardwareprofile. Die Profile binden R,
Θ und β an realistische Samplingraten und stabilisieren ζ(R), damit
σ(β(R-Θ)) nicht durch Hardware-Illusionen überschießt.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class HardwareProfile:
    tier: str
    channels: int
    sampling_rate_hz: int
    expected_auc: float
    crep_stability: float
    cost_usd: str


def load_hardware_profiles(config_path: str | Path) -> dict[str, HardwareProfile]:
    path = Path(config_path)
    payload: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    profiles: dict[str, HardwareProfile] = {}
    for tier, data in payload.get("profiles", {}).items():
        profiles[tier] = HardwareProfile(
            tier=tier,
            channels=int(data["channels"]),
            sampling_rate_hz=int(data["sampling_rate_hz"]),
            expected_auc=float(data["expected_auc"]),
            crep_stability=float(data["crep_stability"]),
            cost_usd=str(data["cost_usd"]),
        )
    return profiles
