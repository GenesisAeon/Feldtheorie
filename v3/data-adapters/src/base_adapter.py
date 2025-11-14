"""
Base Adapter for UTAC V3 Real Data Integration
Phase 4, Week 1-2: Real Data Integration

This module provides the abstract base class for all data adapters,
implementing common functionality for fetching, caching, and transforming
real-world data into UTAC-compatible formats.

Trilayer Integration:
- YAML: System state structure (R, Θ, β)
- JSON: API responses and metadata
- MD: Human-readable data narratives

Author: Claude (MOR Agent)
Date: 2025-11-14
Version: 0.1.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
import hashlib
import os

import numpy as np
import pandas as pd
from scipy import stats
import requests


# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class UTACState:
    """
    UTAC system state at a given timestamp.

    Attributes:
        system_id: Unique identifier (e.g., 'wais', 'amoc', 'coral')
        timestamp: Observation time (ISO 8601)
        R: Current state variable (dimensionless, normalized)
        Theta: Threshold value
        beta: Diagnostic steepness parameter
        sigma: Sigmoid activation σ(β(R-Θ))
        status: System status (STABLE, MONITORING, WATCH, WARNING, ALERT, TIPPING, POST-TIPPING)
        metadata: Additional system-specific data
    """
    system_id: str
    timestamp: str
    R: float
    Theta: float
    beta: float
    sigma: float
    status: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_yaml_str(self) -> str:
        """Convert to YAML string (Ordnungs-Sigillin)."""
        return f"""---
system_id: {self.system_id}
timestamp: {self.timestamp}
state:
  R: {self.R:.6f}
  Theta: {self.Theta:.6f}
  beta: {self.beta:.6f}
  sigma: {self.sigma:.6f}
status: {self.status}
---"""


@dataclass
class EWSSignals:
    """
    Early Warning Signals for critical transitions.

    Based on Scheffer et al. (2009, Nature) and Dakos et al. (2012, PLoS ONE).

    Attributes:
        variance: Variance of detrended time series
        ar1: Lag-1 autocorrelation
        spectral_reddening: Low-frequency power ratio
        kendall_tau_variance: Kendall tau for variance trend
        kendall_tau_ar1: Kendall tau for AR(1) trend
        p_value_variance: P-value for variance trend
        p_value_ar1: P-value for AR(1) trend
    """
    variance: float
    ar1: float
    spectral_reddening: float
    kendall_tau_variance: float
    kendall_tau_ar1: float
    p_value_variance: float
    p_value_ar1: float

    def is_critical(self, alpha: float = 0.05) -> bool:
        """
        Determine if system shows critical slowing down.

        Returns True if both variance and AR(1) show significant increasing trends.
        """
        return (self.p_value_variance < alpha and self.kendall_tau_variance > 0 and
                self.p_value_ar1 < alpha and self.kendall_tau_ar1 > 0)


class BaseAdapter(ABC):
    """
    Abstract base class for all UTAC data adapters.

    Implements:
    - HTTP fetching with retry logic
    - Local caching with TTL
    - Time series preprocessing
    - EWS calculation
    - UTAC state computation
    """

    def __init__(
        self,
        system_id: str,
        cache_dir: Optional[Path] = None,
        cache_ttl_hours: int = 24,
        max_retries: int = 3
    ):
        """
        Initialize base adapter.

        Args:
            system_id: Unique system identifier
            cache_dir: Directory for caching fetched data
            cache_ttl_hours: Cache time-to-live in hours
            max_retries: Maximum HTTP request retries
        """
        self.system_id = system_id
        self.cache_dir = cache_dir or Path('./cache')
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"{__name__}.{system_id}")

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized {self.__class__.__name__} for {system_id}")

    @abstractmethod
    def fetch_raw_data(self, start_date: datetime, end_date: datetime) -> Any:
        """
        Fetch raw data from external source.

        Must be implemented by subclasses.

        Args:
            start_date: Start of time range
            end_date: End of time range

        Returns:
            Raw data in source-specific format
        """
        pass

    @abstractmethod
    def transform_to_timeseries(self, raw_data: Any) -> pd.DataFrame:
        """
        Transform raw data to standardized time series.

        Must be implemented by subclasses.

        Args:
            raw_data: Raw data from fetch_raw_data()

        Returns:
            DataFrame with columns: ['timestamp', 'value', ...]
        """
        pass

    @abstractmethod
    def estimate_beta(self, timeseries: pd.DataFrame) -> Tuple[float, float]:
        """
        Estimate β parameter from time series data.

        Must be implemented by subclasses.

        Args:
            timeseries: Standardized time series DataFrame

        Returns:
            Tuple of (beta_mean, beta_std)
        """
        pass

    def fetch_with_cache(
        self,
        url: str,
        params: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> requests.Response:
        """
        Fetch URL with local caching.

        Args:
            url: Target URL
            params: Query parameters
            force_refresh: Bypass cache

        Returns:
            HTTP response
        """
        # Generate cache key
        cache_key = hashlib.md5(
            f"{url}{json.dumps(params or {}, sort_keys=True)}".encode()
        ).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache
        if not force_refresh and cache_file.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < self.cache_ttl:
                self.logger.debug(f"Cache hit: {cache_key}")
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    response = requests.Response()
                    response._content = json.dumps(cached_data['content']).encode()
                    response.status_code = 200
                    return response

        # Fetch with retry
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                # Cache response
                with open(cache_file, 'w') as f:
                    json.dump({
                        'url': url,
                        'params': params,
                        'timestamp': datetime.now().isoformat(),
                        'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    }, f)

                return response

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise

        raise RuntimeError(f"Failed to fetch {url} after {self.max_retries} attempts")

    def detrend_timeseries(self, ts: pd.Series, method: str = 'linear') -> pd.Series:
        """
        Detrend time series for EWS calculation.

        Args:
            ts: Time series
            method: 'linear' or 'gaussian' (Gaussian kernel smoothing)

        Returns:
            Detrended time series
        """
        if method == 'linear':
            # Linear detrending
            x = np.arange(len(ts))
            slope, intercept = np.polyfit(x, ts.values, 1)
            trend = slope * x + intercept
            return pd.Series(ts.values - trend, index=ts.index)

        elif method == 'gaussian':
            # Gaussian kernel smoothing (bandwidth = 50% of time series length)
            from scipy.ndimage import gaussian_filter1d
            sigma = len(ts) * 0.25
            trend = gaussian_filter1d(ts.values, sigma)
            return pd.Series(ts.values - trend, index=ts.index)

        else:
            raise ValueError(f"Unknown detrending method: {method}")

    def calculate_ews(
        self,
        timeseries: pd.DataFrame,
        window_size: Optional[int] = None,
        detrend_method: str = 'gaussian'
    ) -> EWSSignals:
        """
        Calculate Early Warning Signals.

        Implements rolling window approach from Dakos et al. (2012).

        Args:
            timeseries: DataFrame with 'value' column
            window_size: Rolling window size (default: 50% of series length)
            detrend_method: Detrending method

        Returns:
            EWSSignals object
        """
        ts = timeseries['value'].dropna()

        if window_size is None:
            window_size = len(ts) // 2

        # Detrend
        detrended = self.detrend_timeseries(ts, method=detrend_method)

        # Rolling variance
        rolling_var = detrended.rolling(window=window_size).var()

        # Rolling AR(1)
        def calc_ar1(x):
            if len(x) < 2:
                return np.nan
            return np.corrcoef(x[:-1], x[1:])[0, 1]

        rolling_ar1 = detrended.rolling(window=window_size).apply(calc_ar1, raw=True)

        # Spectral reddening (low-freq / high-freq power)
        from scipy import signal
        freqs, psd = signal.periodogram(detrended.dropna())
        low_freq_power = psd[freqs < np.median(freqs)].sum()
        high_freq_power = psd[freqs >= np.median(freqs)].sum()
        spectral_reddening = low_freq_power / high_freq_power if high_freq_power > 0 else np.inf

        # Kendall tau trends
        import pymannkendall as mk

        # Remove NaN values for trend test
        var_clean = rolling_var.dropna()
        ar1_clean = rolling_ar1.dropna()

        mk_var = mk.original_test(var_clean)
        mk_ar1 = mk.original_test(ar1_clean)

        return EWSSignals(
            variance=rolling_var.iloc[-1],
            ar1=rolling_ar1.iloc[-1],
            spectral_reddening=spectral_reddening,
            kendall_tau_variance=mk_var.z if hasattr(mk_var, 'z') else 0.0,
            kendall_tau_ar1=mk_ar1.z if hasattr(mk_ar1, 'z') else 0.0,
            p_value_variance=mk_var.p,
            p_value_ar1=mk_ar1.p
        )

    def compute_utac_state(
        self,
        R: float,
        Theta: float,
        beta: float,
        timestamp: datetime,
        metadata: Optional[Dict] = None
    ) -> UTACState:
        """
        Compute UTAC state from R, Θ, β.

        Args:
            R: Current state variable
            Theta: Threshold
            beta: Steepness parameter
            timestamp: Observation time
            metadata: Additional metadata

        Returns:
            UTACState object
        """
        # Sigmoid activation
        sigma = 1 / (1 + np.exp(-beta * (R - Theta)))

        # Determine status based on σ-tiers (from PHASE4_ROADMAP.md)
        if sigma < 0.1:
            status = "STABLE"
        elif sigma < 0.3:
            status = "MONITORING"
        elif sigma < 0.5:
            status = "WATCH"
        elif sigma < 0.7:
            status = "WARNING"
        elif sigma < 0.9:
            status = "ALERT"
        elif sigma < 0.99:
            status = "TIPPING"
        else:
            status = "POST-TIPPING"

        return UTACState(
            system_id=self.system_id,
            timestamp=timestamp.isoformat(),
            R=R,
            Theta=Theta,
            beta=beta,
            sigma=sigma,
            status=status,
            metadata=metadata or {}
        )

    def get_current_state(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> UTACState:
        """
        Get current UTAC state for this system.

        Main entry point for adapters.

        Args:
            start_date: Start of data range (default: 5 years ago for stable β estimation)
            end_date: End of data range (default: now)

        Returns:
            Current UTACState
        """
        # Default date range (5 years for stable β estimation)
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365*5)

        self.logger.info(f"Fetching state for {self.system_id} ({start_date.date()} to {end_date.date()})")

        # Fetch and transform data
        raw_data = self.fetch_raw_data(start_date, end_date)
        timeseries = self.transform_to_timeseries(raw_data)

        # Estimate β
        beta_mean, beta_std = self.estimate_beta(timeseries)

        # Calculate EWS
        ews = self.calculate_ews(timeseries)

        # Get current R value (most recent observation)
        current_value = timeseries['value'].iloc[-1]

        # Theta is system-specific, must be provided by subclass
        # For now, use a placeholder that subclasses should override
        Theta = self._get_threshold()

        # Normalize R relative to Theta (subclass-specific)
        R = self._normalize_state(current_value, Theta)

        # Compute UTAC state
        state = self.compute_utac_state(
            R=R,
            Theta=Theta,
            beta=beta_mean,
            timestamp=end_date,
            metadata={
                'beta_std': beta_std,
                'ews': asdict(ews),
                'raw_value': current_value,
                'n_observations': len(timeseries)
            }
        )

        self.logger.info(f"State: R={R:.3f}, Θ={Theta:.3f}, β={beta_mean:.2f}±{beta_std:.2f}, σ={state.sigma:.3f} ({state.status})")

        return state

    @abstractmethod
    def _get_threshold(self) -> float:
        """Get system-specific threshold Θ. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _normalize_state(self, value: float, threshold: float) -> float:
        """Normalize state variable to R. Must be implemented by subclasses."""
        pass


if __name__ == "__main__":
    print("BaseAdapter module for UTAC V3 Phase 4")
    print("This is an abstract base class. Use GRACEAdapter, RAPIDAdapter, or NOAAAdapter.")
