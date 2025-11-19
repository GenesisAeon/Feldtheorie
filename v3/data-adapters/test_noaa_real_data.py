#!/usr/bin/env python3
"""
Test script for NOAA OISST real data fetching.

Usage:
    python test_noaa_real_data.py --region caribbean --days 30
    python test_noaa_real_data.py --region global --days 90 --plot

Author: Claude (MOR Agent)
Date: 2025-11-19
Phase: 4 Week 1-2 (Real Data Integration)
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from noaa_adapter import NOAAAdapter


def main():
    parser = argparse.ArgumentParser(description='Test NOAA OISST real data fetching')
    parser.add_argument('--region', default='great_barrier_reef',
                        choices=['global', 'great_barrier_reef', 'caribbean',
                                 'coral_triangle', 'red_sea', 'maldives'],
                        help='Reef region to fetch')
    parser.add_argument('--days', type=int, default=30,
                        help='Number of days to fetch (default: 30)')
    parser.add_argument('--real', action='store_true',
                        help='Use REAL NOAA data (default: synthetic)')
    parser.add_argument('--plot', action='store_true',
                        help='Plot results (requires matplotlib)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging')

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Initialize adapter
    logger.info(f"Initializing NOAA adapter for region: {args.region}")
    adapter = NOAAAdapter(region=args.region)

    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)

    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")

    # Fetch data
    try:
        logger.info(f"Fetching data (real={args.real})...")
        raw_data = adapter.fetch_raw_data(start_date, end_date, use_real_data=args.real)

        # Transform to time series
        ts = adapter.transform_to_timeseries(raw_data)

        logger.info(f"✅ Successfully fetched {len(ts)} data points")

        # Print summary
        print("\n" + "="*70)
        print(f"NOAA OISST Data Summary - {args.region.upper()}")
        print("="*70)
        print(f"Data source: {raw_data['metadata'].get('source', 'unknown')}")
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        print(f"Observations: {len(ts)}")
        print(f"\nSST Anomaly Statistics:")
        print(f"  Mean: {ts['value'].mean():.3f}°C")
        print(f"  Std:  {ts['value'].std():.3f}°C")
        print(f"  Min:  {ts['value'].min():.3f}°C")
        print(f"  Max:  {ts['value'].max():.3f}°C")
        print(f"\nDegree Heating Weeks (DHW):")
        print(f"  Mean: {ts['dhw'].mean():.2f}")
        print(f"  Max:  {ts['dhw'].max():.2f}")
        print(f"  Current: {ts['dhw'].iloc[-1]:.2f}")

        # Get UTAC state
        state = adapter.get_current_state()
        print(f"\n🌊 UTAC State:")
        print(f"  R (normalized): {state.R:.4f}")
        print(f"  Θ (threshold):  {state.Theta:.4f}")
        print(f"  β (steepness):  {state.beta:.2f}")
        print(f"  σ (sigmoid):    {state.sigma:.4f}")
        print(f"  Status: {state.status}")

        # Additional metrics
        metrics = adapter.get_additional_metrics(ts)
        print(f"\n📊 Coral Stress Metrics:")
        print(f"  Warming rate: {metrics['warming_rate_c_per_decade']:.3f}°C/decade")
        print(f"  Bleaching probability: {metrics['bleaching_probability']:.1%}")
        print(f"  Years since last MHW: {metrics['years_since_last_mhw']:.1f}")

        print("="*70)

        # Plot if requested
        if args.plot:
            try:
                import matplotlib.pyplot as plt
                import matplotlib.dates as mdates

                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

                # SST anomaly
                ax1.plot(ts['timestamp'], ts['value'], 'b-', label='SST Anomaly')
                ax1.axhline(adapter.THETA_TEMP_ANOMALY_C, color='r', linestyle='--',
                            label=f'Bleaching Threshold ({adapter.THETA_TEMP_ANOMALY_C}°C)')
                ax1.set_ylabel('SST Anomaly (°C)', fontsize=12)
                ax1.set_title(f'NOAA OISST - {args.region.replace("_", " ").title()}',
                              fontsize=14, fontweight='bold')
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                # DHW
                ax2.plot(ts['timestamp'], ts['dhw'], 'orange', label='Degree Heating Weeks')
                ax2.axhline(adapter.THETA_DHW, color='r', linestyle='--',
                            label=f'Mass Bleaching Threshold ({adapter.THETA_DHW} DHW)')
                ax2.axhline(adapter.THETA_DHW_MORTALITY, color='darkred', linestyle=':',
                            label=f'Mortality Threshold ({adapter.THETA_DHW_MORTALITY} DHW)')
                ax2.set_ylabel('DHW', fontsize=12)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.legend()
                ax2.grid(True, alpha=0.3)

                # Format x-axis
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
                plt.xticks(rotation=45)

                plt.tight_layout()

                # Save plot
                plot_file = f"noaa_oisst_{args.region}_{end_date.strftime('%Y%m%d')}.png"
                plt.savefig(plot_file, dpi=150, bbox_inches='tight')
                logger.info(f"📊 Plot saved to: {plot_file}")

                plt.show()

            except ImportError:
                logger.error("matplotlib not installed. Install with: pip install matplotlib")

        # Save data to JSON
        output_file = f"noaa_oisst_{args.region}_{end_date.strftime('%Y%m%d')}.json"
        import json
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': raw_data['metadata'],
                'state': {
                    'R': state.R,
                    'Theta': state.Theta,
                    'beta': state.beta,
                    'sigma': state.sigma,
                    'status': state.status
                },
                'metrics': metrics,
                'timeseries': {
                    'timestamps': ts['timestamp'].dt.strftime('%Y-%m-%d').tolist(),
                    'sst_anomaly_c': ts['value'].tolist(),
                    'dhw': ts['dhw'].tolist()
                }
            }, f, indent=2)

        logger.info(f"💾 Data saved to: {output_file}")

    except Exception as e:
        logger.error(f"❌ Error fetching data: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
