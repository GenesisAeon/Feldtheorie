"""Regression guard for Jason Wei integration fits."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis import llm_beta_extractor


@pytest.fixture(name="output_path")
def fixture_output_path(tmp_path: Path) -> Path:
    return tmp_path / "wei_payload.json"


def test_llm_beta_band_alignment(output_path: Path) -> None:
    payload = llm_beta_extractor.run_analysis(output_path=output_path)

    assert output_path.exists(), "run_analysis should emit the JSON summary"
    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == written

    aggregate = payload["aggregate"]
    assert aggregate["within_canonical_band"] is False
    assert aggregate["delta_aic_min"] > 10.0
    assert aggregate["beta_mean"] == pytest.approx(3.4695114626, rel=1e-9)
    assert aggregate["beta_std"] == pytest.approx(0.4655112774, rel=1e-9)
    assert aggregate["theta_mean"] == pytest.approx(9.9216914349, rel=1e-9)
    assert aggregate["theta_std"] == pytest.approx(0.1010680811, rel=1e-9)
    assert aggregate["canonical_band"][0] == pytest.approx(3.6)
    assert aggregate["canonical_band"][1] == pytest.approx(4.8)

    tasks = {summary["task"]: summary for summary in payload["tasks"]}
    assert set(tasks) == {
        "ipa_transliteration",
        "last_letter_concatenation",
        "multistep_arithmetic",
    }
    for summary in tasks.values():
        assert summary["falsification_pass"] is True
        assert summary["delta_aic"] > 10.0
        assert summary["cross_entropy_drop"] > 0.5
        assert summary["logistic"]["r_squared"] > summary["null_power_law"]["r_squared"]


def test_llm_beta_requires_known_task(output_path: Path) -> None:
    with pytest.raises(ValueError):
        llm_beta_extractor.run_analysis(output_path=output_path, tasks=["nonexistent"])
