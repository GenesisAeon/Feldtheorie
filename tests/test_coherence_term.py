import math

import numpy as np

from models.coherence_term import (
    MandalaCoherence,
    mandala_coherence,
    semantic_coupling_term,
    coherence_measure,
)


def test_mandala_coherence_returns_covariance_and_gate() -> None:
    psi = [0.1, 0.5, 0.9, 1.3]
    phi = [0.0, 0.4, 0.8, 1.0]

    result = mandala_coherence(psi, phi, theta=0.2, beta=5.0)

    assert isinstance(result, MandalaCoherence)
    assert result.covariance > 0
    assert 0.0 <= result.normalised <= 1.0
    assert 0.0 <= result.gate <= 1.0
    assert result.zeta <= 1.3
    assert result.zeta >= 0.6
    # Symmetry: swapping inputs should keep the magnitude of coherence identical.
    swapped = mandala_coherence(phi, psi, theta=0.2, beta=5.0)
    assert math.isclose(result.normalised, swapped.normalised)
    assert math.isclose(result.gate, swapped.gate)


def test_semantic_coupling_term_matches_expected_modulation() -> None:
    psi = np.array([0.2, 0.5, 0.8])
    phi = np.array([0.1, 0.2, -0.3])

    coupling = semantic_coupling_term(
        psi,
        phi,
        lambda_coupling=0.4,
        phi_exponent=2.0,
        theta=0.3,
        beta=4.2,
    )

    gate = 1.0 / (1.0 + np.exp(-4.2 * (psi - 0.3)))
    expected = 0.4 * psi * np.sign(phi) * (np.abs(phi) ** 2.0) * gate

    np.testing.assert_allclose(coupling, expected)

    # Scalar invocation should align with array broadcast behaviour.
    scalar_coupling = semantic_coupling_term(0.8, 0.3, lambda_coupling=0.4, phi_exponent=2.0)
    assert np.isclose(scalar_coupling, semantic_coupling_term([0.8], [0.3], lambda_coupling=0.4)[0])


def test_coherence_measure_matches_mandala_normalised() -> None:
    psi = np.array([0.2, 0.6, 1.0, 1.4])
    phi = np.array([0.1, 0.5, 0.9, 1.3])

    mandala = mandala_coherence(psi.tolist(), phi.tolist())
    direct = coherence_measure(psi, phi)

    assert math.isclose(direct, mandala.normalised)

    zero_direct = coherence_measure([1.0], [2.0])
    assert zero_direct == 0.0
