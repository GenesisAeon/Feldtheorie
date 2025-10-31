import math
import textwrap

from analysis.potential_cascade_lab import (
    compile_payload,
    generate_potential_series,
    load_configuration,
    simulate_cascade,
)


def test_generate_potential_series_crosses_threshold() -> None:
    potentials = generate_potential_series(steps=32)
    assert len(potentials) == 32
    assert min(potentials) < 1.0
    assert max(potentials) > 1.2


def test_simulate_cascade_gate_uplift_positive() -> None:
    diagnostics = simulate_cascade(steps=48)
    aggregate = diagnostics.aggregate
    assert aggregate["theta_shift_total"] > 0.0
    assert aggregate["beta_shift_total"] > 0.0
    assert aggregate["gate_delta"] < 0.0
    assert aggregate["zeta_delta"] > 0.0
    assert diagnostics.coherence_summary["normalised_mean"] >= 0.0


def test_compile_payload_includes_tri_layer() -> None:
    diagnostics = simulate_cascade(steps=16)
    payload = compile_payload(diagnostics, generated_at="2026-01-01T00:00:00Z")
    assert payload["generated_at"] == "2026-01-01T00:00:00Z"
    assert "formal" in payload["tri_layer"]
    assert len(payload["states"]) == len(payload["potentials"])
    assert (
        payload["aggregate"]["coherence_normalised_peak"]
        >= payload["aggregate"]["coherence_normalised_mean"]
    )
    assert payload["aggregate"]["gate_mean"] < payload["null_reference"]["gate_mean"]


def test_load_configuration_merges_defaults(tmp_path) -> None:
    config_text = textwrap.dedent(
        """
        meta:
          scenario: semantic-demo
        steps: 12
        cascade:
          theta: 0.85
          beta: 3.9
          cascade_gain: 0.7
        potential:
          surge: 1.05
        coherence:
          window: 7
        impedance:
          closed: 1.28
          open: 0.55
        """
    ).strip()
    config_path = tmp_path / "cascade.yaml"
    config_path.write_text(config_text, encoding="utf-8")

    overrides, meta = load_configuration(config_path)

    assert overrides["steps"] == 12
    assert math.isclose(float(overrides["theta"]), 0.85, rel_tol=1e-9)
    assert math.isclose(float(overrides["beta"]), 3.9, rel_tol=1e-9)
    assert math.isclose(float(overrides["cascade_gain"]), 0.7, rel_tol=1e-9)
    assert overrides["coherence_window"] == 7
    assert math.isclose(float(overrides["potential_surge"]), 1.05, rel_tol=1e-9)
    assert math.isclose(float(overrides["zeta_closed"]), 1.28, rel_tol=1e-9)
    assert math.isclose(float(overrides["zeta_open"]), 0.55, rel_tol=1e-9)
    assert meta["scenario"] == "semantic-demo"
