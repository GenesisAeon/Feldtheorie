import math

import numpy as np
import pytest

from models.coherence_term import (
    MandalaCoherence,
    mandala_coherence,
    semantic_coupling_term,
    coherence_measure,
    _broadcast_fields,
)


class TestMandalaCoherenceDataclass:
    """Test MandalaCoherence dataclass."""

    def test_to_dict_returns_all_fields(self) -> None:
        """to_dict should return all fields."""
        coherence = MandalaCoherence(
            covariance=0.5, normalised=0.8, gate=0.6, zeta=0.9
        )
        result = coherence.to_dict()

        assert result == {
            "covariance": 0.5,
            "normalised": 0.8,
            "gate": 0.6,
            "zeta": 0.9,
        }


class TestMandalaCoherence:
    """Test mandala_coherence function."""

    def test_mandala_coherence_returns_covariance_and_gate(self) -> None:
        """Should compute coherence with logistic gating."""
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

    def test_mandala_coherence_raises_on_length_mismatch(self) -> None:
        """Should raise ValueError when lengths don't match."""
        psi = [0.1, 0.5]
        phi = [0.1, 0.5, 0.9]

        with pytest.raises(ValueError, match="same length"):
            mandala_coherence(psi, phi)

    def test_mandala_coherence_raises_on_empty_input(self) -> None:
        """Should raise ValueError for empty input."""
        with pytest.raises(ValueError, match="at least one sample"):
            mandala_coherence([], [])

    def test_mandala_coherence_single_point(self) -> None:
        """Should handle single point gracefully."""
        result = mandala_coherence([0.5], [0.7])
        assert result.covariance == 0.0  # No variance with single point
        assert result.normalised == 0.0

    def test_mandala_coherence_perfect_correlation(self) -> None:
        """Should return normalised ~1.0 for perfect correlation."""
        psi = [1.0, 2.0, 3.0, 4.0]
        phi = [1.0, 2.0, 3.0, 4.0]

        result = mandala_coherence(psi, phi)
        assert math.isclose(result.normalised, 1.0, abs_tol=1e-6)

    def test_mandala_coherence_zero_variance(self) -> None:
        """Should handle zero variance gracefully."""
        psi = [0.5, 0.5, 0.5]
        phi = [0.3, 0.7, 0.5]

        result = mandala_coherence(psi, phi)
        assert result.normalised == 0.0  # No variance in psi


class TestSemanticCouplingTerm:
    """Test semantic_coupling_term function."""

    def test_semantic_coupling_term_matches_expected_modulation(self) -> None:
        """Should compute coupling with logistic gating."""
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

    def test_semantic_coupling_term_scalar_broadcast(self) -> None:
        """Scalar invocation should align with array broadcast."""
        scalar_coupling = semantic_coupling_term(0.8, 0.3, lambda_coupling=0.4, phi_exponent=2.0)
        array_coupling = semantic_coupling_term([0.8], [0.3], lambda_coupling=0.4, phi_exponent=2.0)
        assert np.isclose(scalar_coupling, array_coupling[0])

    def test_semantic_coupling_term_negative_phi(self) -> None:
        """Should handle negative phi with sign preservation."""
        psi = np.array([0.5])
        phi = np.array([-0.3])
        coupling = semantic_coupling_term(psi, phi, lambda_coupling=0.5, phi_exponent=2.0)

        # Should be negative due to sign preservation
        assert coupling[0] < 0

    def test_semantic_coupling_term_zero_lambda(self) -> None:
        """Should return zero with zero coupling strength."""
        psi = np.array([0.5, 1.0])
        phi = np.array([0.3, 0.7])
        coupling = semantic_coupling_term(psi, phi, lambda_coupling=0.0)

        np.testing.assert_allclose(coupling, [0.0, 0.0])


class TestCoherenceMeasure:
    """Test coherence_measure function."""

    def test_coherence_measure_matches_mandala_normalised(self) -> None:
        """Should match mandala_coherence normalised field."""
        psi = np.array([0.2, 0.6, 1.0, 1.4])
        phi = np.array([0.1, 0.5, 0.9, 1.3])

        mandala = mandala_coherence(psi.tolist(), phi.tolist())
        direct = coherence_measure(psi, phi)

        assert math.isclose(direct, mandala.normalised)

    def test_coherence_measure_single_point_returns_zero(self) -> None:
        """Should return 0 for single point."""
        zero_direct = coherence_measure([1.0], [2.0])
        assert zero_direct == 0.0

    def test_coherence_measure_zero_std(self) -> None:
        """Should return 0 when std is zero."""
        # Constant psi
        result = coherence_measure([0.5, 0.5, 0.5], [0.1, 0.5, 0.9])
        assert result == 0.0

    def test_coherence_measure_perfect_correlation(self) -> None:
        """Should return 1.0 for perfect correlation."""
        psi = [1.0, 2.0, 3.0]
        phi = [1.0, 2.0, 3.0]
        result = coherence_measure(psi, phi)
        assert math.isclose(result, 1.0, abs_tol=1e-6)

    def test_coherence_measure_negative_correlation(self) -> None:
        """Should return negative for negative correlation."""
        psi = [1.0, 2.0, 3.0]
        phi = [3.0, 2.0, 1.0]
        result = coherence_measure(psi, phi)
        assert result < 0

    def test_coherence_measure_clips_to_range(self) -> None:
        """Should clip result to [-1, 1]."""
        psi = np.random.randn(50)
        phi = np.random.randn(50)
        result = coherence_measure(psi, phi)
        assert -1.0 <= result <= 1.0


class TestBroadcastFields:
    """Test _broadcast_fields helper function."""

    def test_broadcast_fields_same_shape(self) -> None:
        """Should return arrays unchanged when shapes match."""
        psi = np.array([1.0, 2.0, 3.0])
        phi = np.array([0.5, 1.0, 1.5])

        psi_out, phi_out = _broadcast_fields(psi, phi)

        np.testing.assert_array_equal(psi_out, psi)
        np.testing.assert_array_equal(phi_out, phi)

    def test_broadcast_fields_scalar_phi(self) -> None:
        """Should broadcast scalar phi to match psi shape."""
        psi = np.array([1.0, 2.0, 3.0])
        phi = np.array([0.5])

        psi_out, phi_out = _broadcast_fields(psi, phi)

        assert phi_out.shape == psi_out.shape
        np.testing.assert_array_equal(phi_out, [0.5, 0.5, 0.5])

    def test_broadcast_fields_broadcastable_shapes(self) -> None:
        """Should broadcast phi to psi shape when possible."""
        psi = np.array([[1.0, 2.0], [3.0, 4.0]])
        phi = np.array([0.5, 1.0])

        psi_out, phi_out = _broadcast_fields(psi, phi)

        assert phi_out.shape == psi_out.shape

    def test_broadcast_fields_raises_on_incompatible(self) -> None:
        """Should raise ValueError for incompatible shapes."""
        psi = np.array([1.0, 2.0, 3.0])
        phi = np.array([0.5, 1.0])

        with pytest.raises(ValueError, match="broadcastable"):
            _broadcast_fields(psi, phi)
