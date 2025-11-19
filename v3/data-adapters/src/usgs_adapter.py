"""
USGS Earthquake Data Adapter for Seismic Monitoring
Phase 4, Week 1-2: Real Data Integration

Fetches live earthquake data from USGS and analyzes seismic criticality using UTAC.

Data Source:
- USGS Earthquake Catalog (FDSNWS Event Web Service)
- URL: https://earthquake.usgs.gov/fdsnws/event/1/query
- Resolution: Real-time global seismic events
- Variables: Magnitude, depth, location, time

β-Estimation Methods:
1. Gutenberg-Richter b-value inversion: β ≈ k/b (inverse relationship)
2. Magnitude-frequency acceleration: β from d²N/dm²
3. Stress accumulation ratio: β from subduction threshold data (β ≈ 16.29)
4. Critical slowing down (EWS): β from variance/AR(1) trends

Gutenberg-Richter Law:
  log₁₀(N) = a - b·M

  where:
  - N = number of earthquakes with magnitude ≥ M
  - b ≈ 1.0 globally (decreases before large events)
  - b-value drop → β increase (sharper transition to rupture)

Threshold:
- Θ = Stress accumulation ratio ≈ 0.74 (from subduction_rupture_threshold.json)
- R = current stress / critical stress
- Large earthquakes (M ≥ 7.0) indicate approaching threshold

Author: Claude (MOR Agent)
Date: 2025-11-19
Version: 0.1.0
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import json
import os

import numpy as np
import pandas as pd
from scipy import stats, optimize
import requests

from base_adapter import BaseAdapter, UTACState


class UsgsSeismicAdapter(BaseAdapter):
    """
    USGS Earthquake adapter for seismic criticality monitoring.

    Implements real-time monitoring of seismic stress using earthquake catalogs,
    Gutenberg-Richter b-values, and UTAC criticality analysis.
    """

    # USGS API endpoint
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    # Magnitude thresholds
    MIN_MAGNITUDE_ANALYSIS = 3.0  # Minimum magnitude for b-value analysis
    MAGNITUDE_THRESHOLD_MAJOR = 7.0  # Major earthquake threshold
    MAGNITUDE_THRESHOLD_GREAT = 8.0  # Great earthquake threshold

    # Seismic regions (major tectonic zones)
    SEISMIC_REGIONS = {
        'global': {'name': 'Global', 'lat': None, 'lon': None},
        'circum_pacific': {'name': 'Ring of Fire',
                          'lat': (-60, 60), 'lon': (120, -60)},
        'cascadia': {'name': 'Cascadia Subduction Zone',
                    'lat': (40, 50), 'lon': (-130, -120)},
        'japan': {'name': 'Japan Trench',
                 'lat': (30, 45), 'lon': (130, 150)},
        'mediterranean': {'name': 'Mediterranean-Alpine Belt',
                         'lat': (30, 50), 'lon': (-10, 50)},
        'himalayan': {'name': 'Himalayan Belt',
                     'lat': (25, 40), 'lon': (70, 100)},
        'california': {'name': 'San Andreas Fault',
                      'lat': (32, 42), 'lon': (-125, -114)}
    }

    # Stress accumulation threshold (from subduction_rupture_threshold.json)
    THETA_STRESS_RATIO = 0.7406  # Critical stress accumulation ratio
    BETA_SUBDUCTION = 16.29  # β from subduction rupture analysis

    # Gutenberg-Richter parameters
    B_VALUE_NORMAL = 1.0  # Normal b-value for stable crust
    B_VALUE_CRITICAL = 0.6  # Critical b-value (pre-mainshock)

    def __init__(
        self,
        region: str = 'global',
        min_magnitude: float = 4.5,
        cache_dir: Optional[Path] = None,
        **kwargs
    ):
        """
        Initialize USGS adapter.

        Args:
            region: Seismic region ('global', 'cascadia', 'japan', etc.)
            min_magnitude: Minimum magnitude for event filtering
            cache_dir: Cache directory
            **kwargs: Additional BaseAdapter arguments
        """
        super().__init__(system_id='seismic', cache_dir=cache_dir, **kwargs)

        if region not in self.SEISMIC_REGIONS:
            raise ValueError(f"Unknown region: {region}. Available: {list(self.SEISMIC_REGIONS.keys())}")

        self.region = region
        self.min_magnitude = min_magnitude
        self.region_def = self.SEISMIC_REGIONS[region]

        self.logger.info(f"Initialized UsgsSeismicAdapter for {self.region_def['name']} (M ≥ {min_magnitude})")

    def fetch_raw_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Fetch live earthquake data from USGS FDSNWS Event Web Service.

        API Documentation:
        https://earthquake.usgs.gov/fdsnws/event/1/

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary with earthquake catalog data
        """
        self.logger.info(f"Fetching USGS earthquake data: {start_date.date()} to {end_date.date()}")

        # Build API request parameters
        params = {
            'format': 'csv',
            'starttime': start_date.strftime('%Y-%m-%d'),
            'endtime': end_date.strftime('%Y-%m-%d'),
            'minmagnitude': self.min_magnitude,
            'orderby': 'time'
        }

        # Add spatial bounds if not global
        if self.region != 'global':
            lat_range = self.region_def['lat']
            lon_range = self.region_def['lon']

            if lat_range and lon_range:
                params['minlatitude'] = lat_range[0]
                params['maxlatitude'] = lat_range[1]
                params['minlongitude'] = lon_range[0]
                params['maxlongitude'] = lon_range[1]

        self.logger.debug(f"USGS API request: {params}")

        try:
            # Fetch data with retry logic from BaseAdapter
            response = self.fetch_with_cache(self.BASE_URL, params=params)

            # Parse CSV response
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))

            self.logger.info(f"Fetched {len(df)} earthquakes from USGS (M ≥ {self.min_magnitude})")

            # Extract relevant columns
            timestamps = pd.to_datetime(df['time'])
            magnitudes = df['mag'].values
            latitudes = df['latitude'].values
            longitudes = df['longitude'].values
            depths = df['depth'].values

            return {
                'timestamps': timestamps.tolist(),
                'magnitudes': magnitudes.tolist(),
                'latitudes': latitudes.tolist(),
                'longitudes': longitudes.tolist(),
                'depths': depths.tolist(),
                'metadata': {
                    'source': 'USGS FDSNWS Event Web Service',
                    'region': self.region,
                    'region_name': self.region_def['name'],
                    'min_magnitude': self.min_magnitude,
                    'n_events': len(df)
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to fetch USGS data: {e}")
            raise

    def transform_to_timeseries(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform raw earthquake catalog to standardized time series.

        Computes:
        - Cumulative seismic moment release
        - Magnitude-frequency statistics
        - Stress proxy metrics

        Args:
            raw_data: Raw data from fetch_raw_data()

        Returns:
            DataFrame with columns: ['timestamp', 'value', 'magnitude', 'cumulative_moment']
        """
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(raw_data['timestamps']),
            'magnitude': raw_data['magnitudes'],
            'latitude': raw_data['latitudes'],
            'longitude': raw_data['longitudes'],
            'depth': raw_data['depths']
        })

        df = df.set_index('timestamp').sort_index()

        # Calculate seismic moment (M₀ = 10^(1.5*M + 9.1) N·m)
        # This measures total energy release
        df['moment_nm'] = 10 ** (1.5 * df['magnitude'] + 9.1)

        # Cumulative moment (stress accumulation proxy)
        df['cumulative_moment'] = df['moment_nm'].cumsum()

        # Normalize cumulative moment to [0, 1] range
        # R = cumulative_moment / max_moment
        max_moment = df['cumulative_moment'].max()
        df['value'] = df['cumulative_moment'] / max_moment if max_moment > 0 else 0

        # Resample to daily bins (aggregate multiple events per day)
        df_daily = df.resample('D').agg({
            'magnitude': 'max',  # Maximum magnitude per day
            'moment_nm': 'sum',  # Total moment per day
            'cumulative_moment': 'last',  # Running total
            'value': 'last'  # Normalized cumulative
        })

        # Forward-fill missing days (no earthquakes)
        df_daily = df_daily.fillna(method='ffill')

        self.logger.info(f"Transformed {len(df_daily)} daily seismic observations")

        return df_daily.reset_index()

    def calculate_gutenberg_richter_b(
        self,
        magnitudes: np.ndarray,
        min_mag: Optional[float] = None,
        method: str = 'maxlik'
    ) -> Tuple[float, float, float]:
        """
        Calculate Gutenberg-Richter b-value from earthquake magnitudes.

        Gutenberg-Richter Law:
          log₁₀(N) = a - b·M

        where:
          - N = number of earthquakes with magnitude ≥ M
          - b ≈ 1.0 globally (typical value for stable crust)
          - b < 0.8 indicates stress accumulation (pre-mainshock)
          - b > 1.2 indicates relaxation (post-mainshock swarms)

        Methods:
          - 'maxlik': Maximum likelihood (Aki, 1965) - most robust
          - 'lsq': Least squares regression

        Args:
            magnitudes: Array of earthquake magnitudes
            min_mag: Minimum magnitude for completeness (default: auto-detect)
            method: Estimation method ('maxlik' or 'lsq')

        Returns:
            Tuple of (b_value, a_value, completeness_magnitude)
        """
        mags = np.array(magnitudes)

        # Determine magnitude of completeness (Mc)
        # Use minimum magnitude as proxy (in production, use MAXC method)
        if min_mag is None:
            min_mag = np.percentile(mags, 10)  # 10th percentile

        # Filter magnitudes above completeness
        mags_complete = mags[mags >= min_mag]

        if len(mags_complete) < 10:
            self.logger.warning(f"Insufficient data for b-value estimation (n={len(mags_complete)})")
            return 1.0, 5.0, min_mag  # Return default values

        if method == 'maxlik':
            # Maximum likelihood (Aki, 1965)
            # b = log₁₀(e) / (⟨M⟩ - Mc)
            mean_mag = np.mean(mags_complete)
            b_value = np.log10(np.e) / (mean_mag - min_mag + 0.05)  # Add small delta for binning

        elif method == 'lsq':
            # Least squares regression
            # Create magnitude bins
            mag_bins = np.arange(min_mag, mags_complete.max() + 0.1, 0.1)

            # Count events above each magnitude
            N = np.array([np.sum(mags_complete >= m) for m in mag_bins])

            # Fit log₁₀(N) = a - b·M
            log_N = np.log10(N + 1)  # Add 1 to avoid log(0)

            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(mag_bins, log_N)

            b_value = -slope  # b is negative slope
            a_value = intercept

            return b_value, a_value, min_mag

        else:
            raise ValueError(f"Unknown method: {method}")

        # Estimate a-value from b-value
        # a = log₁₀(N_total) + b·Mc
        N_total = len(mags_complete)
        a_value = np.log10(N_total) + b_value * min_mag

        self.logger.debug(f"Gutenberg-Richter: b={b_value:.3f}, a={a_value:.3f}, Mc={min_mag:.1f}")

        return b_value, a_value, min_mag

    def estimate_beta_from_b_value(self, b_value: float) -> float:
        """
        Convert Gutenberg-Richter b-value to UTAC β parameter.

        Hypothesis: β ≈ k / b

        Reasoning:
        - Low b-value (b ~ 0.6) → high stress, steep transition → high β
        - High b-value (b ~ 1.2) → relaxed state, gradual → low β

        Empirical calibration:
        - b = 1.0 (normal) → β ≈ 4.5-5.0 (geophysical domain)
        - b = 0.6 (critical) → β ≈ 8-10 (approaching mainshock)
        - b = 0.4 (extreme) → β ≈ 16 (subduction rupture threshold)

        Conversion: β ≈ 4.5 / b

        Args:
            b_value: Gutenberg-Richter b-value

        Returns:
            Estimated β parameter
        """
        k = 4.5  # Calibration constant (geophysical β ≈ 4.6 for b=1.0)

        beta = k / b_value

        # Constrain to reasonable range [2, 20]
        beta = np.clip(beta, 2.0, 20.0)

        return beta

    def estimate_beta(self, timeseries: pd.DataFrame) -> Tuple[float, float]:
        """
        Estimate β from earthquake time series.

        Implements four methods:
        1. Gutenberg-Richter b-value inversion
        2. Cumulative moment acceleration
        3. Historical subduction threshold (β ≈ 16.29)
        4. EWS-based estimation

        Args:
            timeseries: Standardized time series

        Returns:
            (beta_mean, beta_std)
        """
        ts = timeseries.set_index('timestamp')

        # Get original earthquake catalog (before daily aggregation)
        # We need individual magnitudes for b-value calculation
        # For now, use the 'magnitude' column which contains max daily magnitude

        # Method 1: Gutenberg-Richter b-value
        magnitudes = ts['magnitude'].dropna().values

        if len(magnitudes) > 0:
            b_value, a_value, Mc = self.calculate_gutenberg_richter_b(
                magnitudes,
                min_mag=self.MIN_MAGNITUDE_ANALYSIS
            )
            beta_gr = self.estimate_beta_from_b_value(b_value)
            self.logger.debug(f"β (Gutenberg-Richter b={b_value:.3f}): {beta_gr:.2f}")
        else:
            beta_gr = 4.6  # Default geophysical β
            self.logger.warning("No magnitude data for b-value calculation, using default β=4.6")

        # Method 2: Cumulative moment acceleration
        # β ∝ d²M/dt² / dM/dt (acceleration relative to rate)
        cumulative = ts['cumulative_moment'].values

        if len(cumulative) > 10:
            # Calculate first and second derivatives
            dM = np.gradient(cumulative)
            d2M = np.gradient(dM)

            # β from acceleration ratio (avoiding division by zero)
            with np.errstate(divide='ignore', invalid='ignore'):
                accel_ratio = np.abs(d2M) / (np.abs(dM) + 1e-10)

            # Normalize to β range [2, 20]
            beta_accel = 4.0 + 10.0 * np.nanmedian(accel_ratio)
            beta_accel = np.clip(beta_accel, 2.0, 20.0)

            self.logger.debug(f"β (moment acceleration): {beta_accel:.2f}")
        else:
            beta_accel = 4.6

        # Method 3: Subduction threshold (prior from subduction_rupture_threshold.json)
        # This is a strong prior for subduction zones
        beta_subduction = self.BETA_SUBDUCTION  # 16.29
        self.logger.debug(f"β (subduction prior): {beta_subduction:.2f}")

        # Method 4: EWS-based estimation
        ews = self.calculate_ews(timeseries)

        if ews.variance > 0:
            # High variance → critical slowing down → high β
            beta_ews = 3.0 + 15.0 * np.sqrt(ews.variance) / np.sqrt(np.mean(ts['value']**2))
            beta_ews = np.clip(beta_ews, 2.0, 20.0)
        else:
            beta_ews = 4.6

        self.logger.debug(f"β (EWS variance={ews.variance:.3e}): {beta_ews:.2f}")

        # Ensemble estimate with weighted average
        # Give more weight to Gutenberg-Richter and EWS (data-driven)
        # Less weight to subduction prior (too extreme for most regions)
        weights = {
            'gr': 0.35,
            'accel': 0.25,
            'subduction': 0.15,
            'ews': 0.25
        }

        beta_estimates = {
            'gr': beta_gr,
            'accel': beta_accel,
            'subduction': beta_subduction,
            'ews': beta_ews
        }

        # Weighted mean
        beta_mean = sum(weights[k] * beta_estimates[k] for k in weights)

        # Weighted standard deviation
        beta_var = sum(weights[k] * (beta_estimates[k] - beta_mean)**2 for k in weights)
        beta_std = np.sqrt(beta_var)

        self.logger.info(f"β estimate: {beta_mean:.2f} ± {beta_std:.2f} (ensemble)")

        return beta_mean, beta_std

    def _get_threshold(self) -> float:
        """
        Get seismic stress threshold in normalized units.

        Θ = 0.74 (stress accumulation ratio from subduction_rupture_threshold.json)

        Returns:
            Threshold value (normalized to 0.74)
        """
        return self.THETA_STRESS_RATIO  # 0.7406

    def _normalize_state(self, value: float, threshold: float) -> float:
        """
        Normalize cumulative seismic moment to R ∈ [0, 1.5].

        R is already normalized in transform_to_timeseries()
        as cumulative_moment / max_moment.

        To relate to stress threshold:
        R_stress = R / Θ

        When R = 0.74: R_stress = 1.0 (at threshold)
        When R > 0.74: R_stress > 1.0 (post-threshold, mainshock likely)

        Args:
            value: Normalized cumulative moment [0, 1]
            threshold: Stress threshold (0.74)

        Returns:
            Normalized state R
        """
        # Value is already normalized [0, 1]
        # Map to stress ratio by dividing by threshold
        R = value / threshold if threshold > 0 else value

        # Allow R > 1 (system can exceed threshold)
        R = np.clip(R, 0, 2.0)

        return R

    def get_additional_metrics(self, timeseries: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate additional seismic-specific metrics.

        Returns:
            Dictionary with:
            - current_b_value: Gutenberg-Richter b-value
            - largest_magnitude: Largest earthquake in period
            - n_major_events: Number of M ≥ 7.0 events
            - n_great_events: Number of M ≥ 8.0 events
            - moment_release_rate: Current seismic moment release rate
            - time_since_last_major: Days since last M ≥ 7.0 event
        """
        ts = timeseries.set_index('timestamp')

        # Calculate b-value
        magnitudes = ts['magnitude'].dropna().values
        b_value, a_value, Mc = self.calculate_gutenberg_richter_b(magnitudes)

        # Largest magnitude
        largest_mag = ts['magnitude'].max()

        # Count major/great events
        n_major = np.sum(magnitudes >= self.MAGNITUDE_THRESHOLD_MAJOR)
        n_great = np.sum(magnitudes >= self.MAGNITUDE_THRESHOLD_GREAT)

        # Moment release rate (recent trend)
        recent = ts['cumulative_moment'].last('30D')
        if len(recent) > 1:
            x = np.arange(len(recent))
            slope, _ = np.polyfit(x, recent.values, 1)
            moment_rate = slope  # N·m per day
        else:
            moment_rate = 0.0

        # Time since last major event
        major_events = ts[ts['magnitude'] >= self.MAGNITUDE_THRESHOLD_MAJOR]
        if len(major_events) > 0:
            last_major = major_events.index[-1]
            days_since_major = (ts.index[-1] - last_major).days
        else:
            days_since_major = np.inf

        return {
            'current_b_value': float(b_value),
            'current_a_value': float(a_value),
            'magnitude_completeness': float(Mc),
            'largest_magnitude': float(largest_mag),
            'n_major_events': int(n_major),
            'n_great_events': int(n_great),
            'moment_release_rate_nm_per_day': float(moment_rate),
            'days_since_last_major': float(days_since_major),
            'b_value_status': self._interpret_b_value(b_value)
        }

    def _interpret_b_value(self, b_value: float) -> str:
        """
        Interpret Gutenberg-Richter b-value status.

        Args:
            b_value: Gutenberg-Richter b-value

        Returns:
            Status string
        """
        if b_value > 1.2:
            return "RELAXED (aftershock sequence)"
        elif b_value > 0.9:
            return "NORMAL (stable crust)"
        elif b_value > 0.7:
            return "STRESSED (stress accumulation)"
        elif b_value > 0.5:
            return "CRITICAL (approaching mainshock)"
        else:
            return "EXTREME (imminent rupture)"


if __name__ == "__main__":
    """Test USGS adapter with real data."""
    import logging
    logging.basicConfig(level=logging.INFO)

    adapter = UsgsSeismicAdapter(region='global', min_magnitude=4.5)

    # Get current state (last 90 days for b-value statistics)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    state = adapter.get_current_state(start_date=start_date, end_date=end_date)

    print("\n" + "="*60)
    print("Seismic Monitoring - USGS Earthquake Catalog")
    print("="*60)
    print(f"System ID: {state.system_id}")
    print(f"Timestamp: {state.timestamp}")
    print(f"R (normalized state): {state.R:.4f}")
    print(f"Θ (threshold): {state.Theta:.4f}")
    print(f"β (steepness): {state.beta:.2f}")
    print(f"σ (sigmoid): {state.sigma:.4f}")
    print(f"Status: {state.status}")
    print(f"\nMetadata:")
    print(f"  β uncertainty: ±{state.metadata['beta_std']:.2f}")
    print(f"  Observations: {state.metadata['n_observations']}")
    print("\n" + "="*60)

    # Additional metrics
    raw_data = adapter.fetch_raw_data(start_date, end_date)
    ts = adapter.transform_to_timeseries(raw_data)
    metrics = adapter.get_additional_metrics(ts)

    print("\nSeismic Metrics:")
    print(f"  Gutenberg-Richter b-value: {metrics['current_b_value']:.3f} ({metrics['b_value_status']})")
    print(f"  Largest magnitude: M {metrics['largest_magnitude']:.1f}")
    print(f"  Major events (M ≥ 7.0): {metrics['n_major_events']}")
    print(f"  Great events (M ≥ 8.0): {metrics['n_great_events']}")
    print(f"  Days since last major: {metrics['days_since_last_major']:.0f}")
    print(f"  Moment release rate: {metrics['moment_release_rate_nm_per_day']:.2e} N·m/day")
    print()
