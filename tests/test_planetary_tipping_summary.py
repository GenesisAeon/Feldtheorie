"""Regression tests for the planetary tipping logistic summary export."""

from analysis.planetary_tipping_elements_fit import (
    AggregateLogistic,
    LogisticElement,
    compile_summary,
)


def test_compile_summary_tracks_beta_mean_and_timestamp() -> None:
    elements = [
        LogisticElement(
            id="alpha",
            label="Alpha Membrane",
            theta=1.2,
            beta=4.0,
            theta_ci95=[1.0, 1.4],
            beta_ci95=[3.6, 4.6],
            logistic_r2=0.98,
            impedance="ζ(R) = 1.3 - 0.4 · σ",
            null_deltas={},
        ),
        LogisticElement(
            id="beta",
            label="Beta Chorus",
            theta=1.4,
            beta=4.4,
            theta_ci95=[1.1, 1.7],
            beta_ci95=[4.0, 4.8],
            logistic_r2=0.99,
            impedance="ζ(R) = 1.2 - 0.3 · σ",
            null_deltas={},
        ),
    ]

    aggregate = AggregateLogistic(
        theta=1.3,
        beta=4.2,
        theta_ci95=[1.1, 1.5],
        beta_ci95=[3.9, 4.5],
        r2=0.987,
        aic=-42.0,
        ss_res=0.01,
        impedance_mean=1.25,
        impedance_std=0.08,
        null_models={
            "linear": {"delta_aic": 20.0},
            "power_law": {"delta_aic": 22.0},
        },
    )

    summary = compile_summary(elements, aggregate, generated_at="2026-01-01T00:00:00Z")

    assert summary["generated_at"] == "2026-01-01T00:00:00Z"

    aggregate_summary = summary["aggregate"]
    assert aggregate_summary["beta_mean"] == 4.2
    assert aggregate_summary["beta_band_width_mean"] == 0.9

    beta_note = next(note for note in summary["hypotheses"] if note["id"] == "beta_universality")
    assert beta_note["evidence"]["beta_mean"] == 4.2
    assert beta_note["evidence"]["beta_band_width_mean"] == 0.9
