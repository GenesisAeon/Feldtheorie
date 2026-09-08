"""Tests for analysis/multiple_testing_correction.py.

Regression coverage for the 2026-09-08 fix: aic_to_likelihood_ratio_p()
was missing the parameter-count correction term entirely (silently
assumed k_logistic == k_null), and even corrected, is not a valid
likelihood-ratio test for the non-nested models this module actually
compares (logistic vs linear/exponential/power-law). Both properties
are locked in here so neither regresses silently.
"""

from __future__ import annotations

import warnings

import pytest
from analysis.multiple_testing_correction import (
    aic_to_likelihood_ratio_p,
    akaike_relative_likelihood,
)


def test_aic_to_p_applies_parameter_count_correction() -> None:
    """chi2_stat must be delta_aic + 2*(k_logistic - k_null), not delta_aic alone."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Equal parameter counts -> zero correction term -> df=0 -> defined as p=1.0.
        p_equal_k = aic_to_likelihood_ratio_p(10.0, k_logistic=2, k_null=2)
        # Real parameter counts used by reproduce_beta.py: logistic k=3, null k=2.
        p_real_k = aic_to_likelihood_ratio_p(10.0, k_logistic=3, k_null=2)

    assert p_equal_k == 1.0
    assert p_real_k == pytest.approx(0.0005320055051392103, abs=1e-12)
    assert p_real_k != p_equal_k


def test_aic_to_p_warns_that_models_are_not_nested() -> None:
    """Every call must surface the non-nested-models caveat -- this is not
    a bug fix that can be applied silently, since the underlying test is
    still not statistically valid for this module's actual comparisons."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        aic_to_likelihood_ratio_p(5.0)
    assert len(caught) == 1
    assert "not nested" in str(caught[0].message)


def test_aic_to_p_non_positive_delta_aic_is_one() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert aic_to_likelihood_ratio_p(0.0) == 1.0
        assert aic_to_likelihood_ratio_p(-3.0) == 1.0


def test_akaike_relative_likelihood_matches_burnham_anderson_formula() -> None:
    """exp(-delta_aic/2), valid for non-nested models unlike the chi-squared path."""
    import math

    assert akaike_relative_likelihood(10.0) == pytest.approx(math.exp(-5.0))
    assert akaike_relative_likelihood(0.0) == 1.0
    assert akaike_relative_likelihood(-1.0) == 1.0


def test_akaike_relative_likelihood_decreases_with_larger_delta_aic() -> None:
    small = akaike_relative_likelihood(2.0)
    large = akaike_relative_likelihood(20.0)
    assert large < small
