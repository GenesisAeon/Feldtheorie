"""Tests for PSRM mapper."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.neuro_profile_model import (  # noqa: E402
    NeuroProfileModel,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.psrm_mapper import (  # noqa: E402
    build_psrm_map,
)


def test_psrm_map_structure() -> None:
    rng = np.random.default_rng(5)
    series = rng.normal(0.0, 1.0, 512)
    model = NeuroProfileModel()
    result = model.analyze(
        series,
        consent_granted=True,
        consent_token="psrm-test-token",
        subject_id="tester",
    )
    map_data = build_psrm_map(
        result,
        config=model.config,
        source="synthetic_1khz_eeg",
        hardware_tier="simulated",
        calibration_status="pending",
    )
    payload = map_data.payload
    assert payload["layer_1_signal"]["crep_aggregate"] == result.crep.aggregate
    assert payload["layer_2_intention"]["calibration_status"] == "pending"
    assert payload["layer_3_context"]["ethics_consent"] is True
