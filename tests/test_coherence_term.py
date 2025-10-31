import math

from models.coherence_term import MandalaCoherence, mandala_coherence


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
