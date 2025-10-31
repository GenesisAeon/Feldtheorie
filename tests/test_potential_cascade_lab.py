from analysis.potential_cascade_lab import (
    compile_payload,
    generate_potential_series,
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
