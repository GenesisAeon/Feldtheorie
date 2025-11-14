#!/usr/bin/env python3
"""
Test script for UTAC V3 Data Adapters
Phase 4, Week 1-2: Real Data Integration

Validates:
1. All three adapters (GRACE, RAPID, NOAA)
2. β-estimation accuracy
3. WAIS transition: 3.42 → 13.5 ± 1.5
4. EWS calculation
5. UTAC state computation

Author: Claude (MOR Agent)
Date: 2025-11-14
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from datetime import datetime, timedelta
import logging

from grace_adapter import GRACEAdapter
from rapid_adapter import RAPIDAdapter
from noaa_adapter import NOAAAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_adapter(adapter, expected_beta_range, system_name):
    """
    Test a single adapter.

    Args:
        adapter: Adapter instance
        expected_beta_range: (min, max) tuple for expected β
        system_name: Human-readable system name
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Testing {system_name}")
    logger.info(f"{'='*80}")

    try:
        # Get current state
        state = adapter.get_current_state()

        # Validate state
        assert state is not None, "State is None"
        assert 0 <= state.R <= 2, f"R out of bounds: {state.R}"
        assert state.Theta == 1.0, f"Θ should be 1.0: {state.Theta}"
        assert 0 <= state.sigma <= 1, f"σ out of bounds: {state.sigma}"

        # Validate β
        beta_min, beta_max = expected_beta_range
        assert beta_min <= state.beta <= beta_max, \
            f"β out of expected range: {state.beta:.2f} (expected {beta_min}-{beta_max})"

        # Print results
        print(f"\n{system_name} Results:")
        print(f"  System ID: {state.system_id}")
        print(f"  R (normalized state): {state.R:.4f}")
        print(f"  Θ (threshold): {state.Theta:.4f}")
        print(f"  β (steepness): {state.beta:.2f} ± {state.metadata['beta_std']:.2f}")
        print(f"  σ (sigmoid): {state.sigma:.4f}")
        print(f"  Status: {state.status}")
        print(f"  Observations: {state.metadata['n_observations']}")

        # EWS signals
        ews = state.metadata['ews']
        print(f"\n  Early Warning Signals:")
        print(f"    Variance: {ews['variance']:.4f}")
        print(f"    AR(1): {ews['ar1']:.4f}")
        print(f"    Spectral reddening: {ews['spectral_reddening']:.4f}")
        print(f"    Critical slowing down: {ews['p_value_variance'] < 0.05 and ews['p_value_ar1'] < 0.05}")

        # Get additional metrics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*3)
        raw_data = adapter.fetch_raw_data(start_date, end_date)
        ts = adapter.transform_to_timeseries(raw_data)
        metrics = adapter.get_additional_metrics(ts)

        print(f"\n  System-Specific Metrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                if abs(value) > 1000:
                    print(f"    {key}: {value:.2e}")
                elif abs(value) < 0.01:
                    print(f"    {key}: {value:.4f}")
                else:
                    print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")

        logger.info(f"✓ {system_name} test PASSED")
        return True

    except Exception as e:
        logger.error(f"✗ {system_name} test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_wais_transition():
    """
    Validate WAIS β transition: 3.42 → 13.5 ± 1.5

    This is the critical success criterion for Week 1-2.
    """
    logger.info(f"\n{'='*80}")
    logger.info("Validating WAIS β Transition")
    logger.info(f"{'='*80}")

    # Old placeholder β (from seed/RoadToV.3/additional-systems.ts)
    beta_old = 3.42

    # New real data-driven β (from GRACE adapter)
    adapter = GRACEAdapter()
    state = adapter.get_current_state()
    beta_new = state.beta
    beta_std = state.metadata['beta_std']

    # Expected range: 13.5 ± 1.5 → [12.0, 15.0]
    beta_expected = 13.5
    beta_expected_std = 1.5

    print(f"\nβ Transition Validation:")
    print(f"  Old (placeholder): {beta_old:.2f}")
    print(f"  New (real data):   {beta_new:.2f} ± {beta_std:.2f}")
    print(f"  Expected:          {beta_expected:.2f} ± {beta_expected_std:.2f}")
    print(f"  Δβ:                {beta_new - beta_old:.2f} ({(beta_new/beta_old - 1)*100:+.1f}%)")

    # Validation
    if 12.0 <= beta_new <= 15.0:
        print(f"  ✓ β within expected range")
        logger.info("✓ WAIS β transition VALIDATED")
        return True
    else:
        print(f"  ✗ β outside expected range")
        logger.warning("✗ WAIS β transition OUT OF RANGE")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("UTAC V3 Data Adapters - Test Suite")
    print("Phase 4, Week 1-2: Real Data Integration")
    print("="*80)

    results = {}

    # Test 1: WAIS (GRACE)
    adapter_wais = GRACEAdapter()
    results['WAIS'] = test_adapter(
        adapter_wais,
        expected_beta_range=(12.0, 15.0),
        system_name="WAIS (West Antarctic Ice Sheet)"
    )

    # Test 2: AMOC (RAPID)
    adapter_amoc = RAPIDAdapter()
    results['AMOC'] = test_adapter(
        adapter_amoc,
        expected_beta_range=(8.7, 11.7),  # 10.2 ± 1.5
        system_name="AMOC (Atlantic Meridional Overturning Circulation)"
    )

    # Test 3: Coral (NOAA)
    adapter_coral = NOAAAdapter()
    results['Coral'] = test_adapter(
        adapter_coral,
        expected_beta_range=(6.0, 9.0),  # 7.5 ± 1.5
        system_name="Coral Reefs (Global)"
    )

    # Test 4: WAIS β transition validation
    results['WAIS_β_transition'] = validate_wais_transition()

    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)

    total = len(results)
    passed_count = sum(1 for v in results.values() if v)

    for test_name, test_passed in results.items():
        status = "✓ PASS" if test_passed else "✗ FAIL"
        print(f"  {test_name:30s} {status}")

    print(f"\nTotal: {passed_count}/{total} tests passed")

    if passed_count == total:
        print("\n🎉 All tests PASSED! Week 1-2 success criteria met.")
        logger.info("All tests passed.")
        return 0
    else:
        print(f"\n⚠️  {total - passed_count} test(s) FAILED.")
        logger.warning(f"{total - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
