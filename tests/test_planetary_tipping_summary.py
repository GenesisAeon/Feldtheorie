"""Regression tests for the planetary tipping logistic summary export."""

import pytest

from analysis.planetary_tipping_elements_fit import (
    AggregateLogistic,
    LogisticElement,
    calculate_universal_beta_evidence,
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
    assert aggregate_summary["beta_mean"] == pytest.approx(4.2)
    assert aggregate_summary["beta_mean_observed"] == pytest.approx(4.2)
    assert aggregate_summary["beta_median"] == pytest.approx(4.2)
    assert aggregate_summary["beta_canonical"] == pytest.approx(4.2)
    assert aggregate_summary["beta_std"] == pytest.approx(0.282842712474619)
    assert aggregate_summary["beta_sem"] == pytest.approx(0.2)
    assert aggregate_summary["beta_sem_ci95"] == pytest.approx([3.808, 4.592])
    assert aggregate_summary["beta_ci_width_mean"] == pytest.approx(0.9)
    assert aggregate_summary["beta_ci_width_std"] == pytest.approx(0.1414213562373095)
    assert aggregate_summary["beta_iqr"] == pytest.approx(0.2)
    assert aggregate_summary["n_elements"] == 2

    beta_note = next(note for note in summary["hypotheses"] if note["id"] == "beta_universality")
    assert beta_note["evidence"]["beta_mean"] == pytest.approx(4.2)
    assert beta_note["evidence"]["beta_mean_observed"] == pytest.approx(4.2)
    assert beta_note["evidence"]["beta_median"] == pytest.approx(4.2)
    assert beta_note["evidence"]["beta_canonical"] == pytest.approx(4.2)
    assert beta_note["evidence"]["beta_std"] == pytest.approx(0.282842712474619)
    assert beta_note["evidence"]["beta_sem"] == pytest.approx(0.2)
    assert beta_note["evidence"]["beta_sem_ci95"] == pytest.approx([3.808, 4.592])
    assert beta_note["evidence"]["beta_ci_width_mean"] == pytest.approx(0.9)
    assert beta_note["evidence"]["beta_ci_width_std"] == pytest.approx(0.1414213562373095)
    assert beta_note["evidence"]["beta_iqr"] == pytest.approx(0.2)
    assert beta_note["evidence"]["n_elements"] == 2
    assert beta_note["status"] == "inconclusive"


def test_beta_universality_status_supported_when_band_and_aic_align() -> None:
    elements = [
        LogisticElement(
            id="alpha",
            label="Alpha Membrane",
            theta=1.0,
            beta=3.8,
            theta_ci95=[0.9, 1.1],
            beta_ci95=[3.5, 4.1],
            logistic_r2=0.98,
            impedance="ζ(R) = 1.1 - 0.3 · σ",
            null_deltas={},
        ),
        LogisticElement(
            id="beta",
            label="Beta Membrane",
            theta=1.1,
            beta=4.0,
            theta_ci95=[1.0, 1.2],
            beta_ci95=[3.7, 4.3],
            logistic_r2=0.99,
            impedance="ζ(R) = 1.2 - 0.2 · σ",
            null_deltas={},
        ),
        LogisticElement(
            id="gamma",
            label="Gamma Membrane",
            theta=1.2,
            beta=4.2,
            theta_ci95=[1.1, 1.3],
            beta_ci95=[3.9, 4.5],
            logistic_r2=0.995,
            impedance="ζ(R) = 1.3 - 0.1 · σ",
            null_deltas={},
        ),
    ]

    aggregate = AggregateLogistic(
        theta=1.1,
        beta=4.0,
        theta_ci95=[1.0, 1.2],
        beta_ci95=[3.8, 4.2],
        r2=0.99,
        aic=-80.0,
        ss_res=0.005,
        impedance_mean=1.2,
        impedance_std=0.05,
        null_models={
            "linear": {"delta_aic": 45.0},
            "power_law": {"delta_aic": 40.0},
        },
    )

    summary = compile_summary(elements, aggregate, generated_at="2026-01-01T00:00:00Z")
    beta_note = next(note for note in summary["hypotheses"] if note["id"] == "beta_universality")
    assert beta_note["status"] == "supported"


def test_beta_universality_status_contradicted_when_beta_outside_band() -> None:
    elements = [
        LogisticElement(
            id="alpha",
            label="Alpha Membrane",
            theta=1.0,
            beta=5.1,
            theta_ci95=[0.9, 1.1],
            beta_ci95=[4.9, 5.3],
            logistic_r2=0.98,
            impedance="ζ(R) = 1.1 - 0.3 · σ",
            null_deltas={},
        ),
        LogisticElement(
            id="beta",
            label="Beta Membrane",
            theta=1.1,
            beta=5.0,
            theta_ci95=[1.0, 1.2],
            beta_ci95=[4.8, 5.2],
            logistic_r2=0.99,
            impedance="ζ(R) = 1.2 - 0.2 · σ",
            null_deltas={},
        ),
        LogisticElement(
            id="gamma",
            label="Gamma Membrane",
            theta=1.2,
            beta=4.9,
            theta_ci95=[1.1, 1.3],
            beta_ci95=[4.7, 5.1],
            logistic_r2=0.995,
            impedance="ζ(R) = 1.3 - 0.1 · σ",
            null_deltas={},
        ),
    ]

    aggregate = AggregateLogistic(
        theta=1.1,
        beta=5.0,
        theta_ci95=[1.0, 1.2],
        beta_ci95=[4.9, 5.1],
        r2=0.99,
        aic=-82.0,
        ss_res=0.004,
        impedance_mean=1.2,
        impedance_std=0.05,
        null_models={
            "linear": {"delta_aic": 60.0},
            "power_law": {"delta_aic": 55.0},
        },
    )

    summary = compile_summary(elements, aggregate, generated_at="2026-01-01T00:00:00Z")
    beta_note = next(note for note in summary["hypotheses"] if note["id"] == "beta_universality")
    assert beta_note["status"] == "contradicted"


def test_beta_statistics_fallback_to_aggregate_when_elements_absent() -> None:
    elements: list[LogisticElement] = []
    aggregate = AggregateLogistic(
        theta=1.3,
        beta=4.21,
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

    aggregate_summary = summary["aggregate"]
    assert aggregate_summary["beta_mean"] == pytest.approx(4.21)
    assert aggregate_summary["beta_mean_observed"] is None
    assert aggregate_summary["beta_median"] is None
    assert aggregate_summary["beta_canonical"] == pytest.approx(4.21)
    assert aggregate_summary["beta_std"] is None
    assert aggregate_summary["beta_sem"] is None
    assert aggregate_summary["beta_ci_width_mean"] is None
    assert aggregate_summary["beta_iqr"] is None

    beta_note = next(note for note in summary["hypotheses"] if note["id"] == "beta_universality")
    assert beta_note["status"] == "inconclusive"
    assert beta_note["evidence"]["beta_mean"] == pytest.approx(4.21)
    assert beta_note["evidence"]["beta_mean_observed"] is None
    assert beta_note["evidence"]["beta_median"] is None
    assert beta_note["evidence"]["beta_canonical"] == pytest.approx(4.21)
    assert beta_note["evidence"]["beta_ci_width_mean"] is None
    assert beta_note["evidence"]["beta_iqr"] is None

    coupled_note = next(note for note in summary["hypotheses"] if note["id"] == "coupled_resonance")
    assert coupled_note["evidence"]["beta_range"] == pytest.approx([4.21, 4.21])
    assert coupled_note["evidence"]["theta_span"] is None

    assert "4.21" in summary["tri_layer"]["formal"]


def test_calculate_universal_beta_evidence_reports_sample_metrics() -> None:
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

    evidence = calculate_universal_beta_evidence(elements, aggregate_beta=4.2)
    assert evidence["sample_size"] == 2
    assert evidence["beta_mean"] == pytest.approx(4.2)
    assert evidence["beta_mean_observed"] == pytest.approx(4.2)
    assert evidence["beta_median"] == pytest.approx(4.2)
    assert evidence["beta_ci_width_mean"] == pytest.approx(0.9)
    assert evidence["beta_iqr"] == pytest.approx(0.2)


def test_calculate_universal_beta_evidence_handles_empty_sequence() -> None:
    evidence = calculate_universal_beta_evidence([], aggregate_beta=4.21)
    assert evidence["sample_size"] == 0
    assert evidence["beta_mean"] == pytest.approx(4.21)
    assert evidence["beta_mean_observed"] is None
    assert evidence["beta_median"] is None
    assert evidence["beta_iqr"] is None
