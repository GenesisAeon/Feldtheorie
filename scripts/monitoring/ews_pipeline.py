#!/usr/bin/env python3
"""
Automated Early Warning Signals (EWS) Pipeline
===============================================

Phase 4: v3-feat-p4-001

Automated monitoring pipeline for tipping point Early Warning Signals.

Features:
- Loads latest data from adapters
- Computes EWS metrics (Variance, AR(1), Spectral)
- Detects trends (Kendall τ)
- Generates alerts for critical thresholds
- Exports alerts as JSON for Sigillin integration

Thresholds:
- Variance increase > 50%: WARNING
- Variance increase > 100%: CRITICAL
- AR(1) > 0.70: WARNING
- AR(1) > 0.80: CRITICAL
- Kendall τ > 0.5 and p < 0.05: WARNING
- Kendall τ > 0.7 and p < 0.01: CRITICAL

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats

# Import EWS analyzer from existing script
sys.path.append(str(Path(__file__).parent.parent / "analysis"))
from ews_analysis import EWSAnalyzer


class EWSPipeline:
    """Automated EWS monitoring pipeline."""

    def __init__(self, results_path: str = None):
        """Initialize pipeline.

        Args:
            results_path: Path to analysis results directory
        """
        if results_path is None:
            results_path = Path(__file__).parent.parent / "analysis" / "results"

        self.results_path = Path(results_path)
        self.analyzer = EWSAnalyzer()
        self.alerts = []

    def load_latest_data(self) -> Dict:
        """Load latest adapter outputs.

        Returns:
            dict: Latest data for all systems
        """
        systems = {}

        for system in ['wais', 'amoc', 'coral']:
            adapter_file = self.results_path / f"{system}_adapter_output.json"

            if not adapter_file.exists():
                print(f"⚠️  Warning: {adapter_file} not found, skipping {system.upper()}")
                continue

            with open(adapter_file, 'r') as f:
                systems[system] = json.load(f)

        return systems

    def check_ews_thresholds(self, system: str, ews_result: Dict) -> List[Dict]:
        """Check EWS metrics against alert thresholds.

        Args:
            system: System name
            ews_result: EWS analysis result from EWSAnalyzer

        Returns:
            list: Alert objects
        """
        alerts = []

        # Variance thresholds
        var_increase = ews_result['variance_ews']['increase_percent']
        var_tau = ews_result['variance_ews']['trend']['tau']
        var_p = ews_result['variance_ews']['trend']['p_value']

        if var_increase > 100:
            alerts.append({
                'system': system.upper(),
                'metric': 'Variance',
                'level': 'CRITICAL',
                'value': var_increase,
                'threshold': 100,
                'message': f"Variance increase extremely high: {var_increase:.1f}%",
                'trend_tau': var_tau,
                'trend_p': var_p
            })
        elif var_increase > 50:
            alerts.append({
                'system': system.upper(),
                'metric': 'Variance',
                'level': 'WARNING',
                'value': var_increase,
                'threshold': 50,
                'message': f"Variance increase elevated: {var_increase:.1f}%",
                'trend_tau': var_tau,
                'trend_p': var_p
            })

        # AR(1) thresholds
        ar1_increase = ews_result['ar1_ews']['increase_percent']
        ar1_tau = ews_result['ar1_ews']['trend']['tau']
        ar1_p = ews_result['ar1_ews']['trend']['p_value']
        ar1_late = ews_result['ar1_ews']['late_period_mean']

        if ar1_late > 0.80:
            alerts.append({
                'system': system.upper(),
                'metric': 'AR(1)',
                'level': 'CRITICAL',
                'value': ar1_late,
                'threshold': 0.80,
                'message': f"AR(1) critically high: {ar1_late:.3f} (recovery time very long)",
                'trend_tau': ar1_tau,
                'trend_p': ar1_p
            })
        elif ar1_late > 0.70:
            alerts.append({
                'system': system.upper(),
                'metric': 'AR(1)',
                'level': 'WARNING',
                'value': ar1_late,
                'threshold': 0.70,
                'message': f"AR(1) elevated: {ar1_late:.3f} (recovery time lengthening)",
                'trend_tau': ar1_tau,
                'trend_p': ar1_p
            })

        # Kendall τ trend thresholds (combined variance + AR(1))
        if var_tau > 0.7 and var_p < 0.01 and ar1_tau > 0.5:
            alerts.append({
                'system': system.upper(),
                'metric': 'EWS Trends',
                'level': 'CRITICAL',
                'value': {'var_tau': var_tau, 'ar1_tau': ar1_tau},
                'threshold': {'var_tau': 0.7, 'ar1_tau': 0.5},
                'message': f"Strong increasing trends in both EWS (Var τ={var_tau:.3f}, AR(1) τ={ar1_tau:.3f})",
                'trend_tau': (var_tau + ar1_tau) / 2,
                'trend_p': min(var_p, ar1_p)
            })
        elif (var_tau > 0.5 and var_p < 0.05) or (ar1_tau > 0.5 and ar1_p < 0.05):
            alerts.append({
                'system': system.upper(),
                'metric': 'EWS Trends',
                'level': 'WARNING',
                'value': {'var_tau': var_tau, 'ar1_tau': ar1_tau},
                'threshold': {'var_tau': 0.5, 'ar1_tau': 0.5},
                'message': f"Moderate increasing trends detected (Var τ={var_tau:.3f}, AR(1) τ={ar1_tau:.3f})",
                'trend_tau': (var_tau + ar1_tau) / 2,
                'trend_p': min(var_p, ar1_p)
            })

        # Critical slowing detection
        if ews_result['critical_slowing_detected']:
            alerts.append({
                'system': system.upper(),
                'metric': 'Critical Slowing',
                'level': 'CRITICAL',
                'value': True,
                'threshold': 'Both Var and AR(1) trends significant',
                'message': f"Critical slowing down detected! System approaching tipping point.",
                'trend_tau': (var_tau + ar1_tau) / 2,
                'trend_p': min(var_p, ar1_p)
            })

        # Spectral reddening
        spectral_red = ews_result['spectral_ews']['reddening_ratio']
        if spectral_red > 20:
            alerts.append({
                'system': system.upper(),
                'metric': 'Spectral Reddening',
                'level': 'CRITICAL',
                'value': spectral_red,
                'threshold': 20,
                'message': f"Extreme spectral reddening: {spectral_red:.2f} (low-freq dominance)",
                'trend_tau': None,
                'trend_p': None
            })
        elif spectral_red > 15:
            alerts.append({
                'system': system.upper(),
                'metric': 'Spectral Reddening',
                'level': 'WARNING',
                'value': spectral_red,
                'threshold': 15,
                'message': f"High spectral reddening: {spectral_red:.2f}",
                'trend_tau': None,
                'trend_p': None
            })

        return alerts

    def check_system_status(self, system: str, adapter_data: Dict) -> List[Dict]:
        """Check system-specific status indicators.

        Args:
            system: System name
            adapter_data: Adapter output data

        Returns:
            list: Status alerts
        """
        alerts = []

        if system == 'wais':
            current = adapter_data['statistics']['current_state']
            distance = current['distance_to_tipping']

            if distance < 0.20:
                alerts.append({
                    'system': 'WAIS',
                    'metric': 'Distance to Tipping',
                    'level': 'CRITICAL',
                    'value': distance,
                    'threshold': 0.20,
                    'message': f"WAIS critically close to tipping point: {distance*100:.1f}%",
                    'trend_tau': None,
                    'trend_p': None
                })
            elif distance < 0.30:
                alerts.append({
                    'system': 'WAIS',
                    'metric': 'Distance to Tipping',
                    'level': 'WARNING',
                    'value': distance,
                    'threshold': 0.30,
                    'message': f"WAIS approaching tipping point: {distance*100:.1f}%",
                    'trend_tau': None,
                    'trend_p': None
                })

        elif system == 'amoc':
            stats = adapter_data['statistics']

            # FovS crossing
            if stats['early_warning_signals'].get('fovs_crossed_zero'):
                alerts.append({
                    'system': 'AMOC',
                    'metric': 'FovS Indicator',
                    'level': 'CRITICAL',
                    'value': stats['current_state']['fovs_indicator'],
                    'threshold': 0.0,
                    'message': f"AMOC FovS crossed zero! System TIPPED (FovS={stats['current_state']['fovs_indicator']:.3f})",
                    'trend_tau': None,
                    'trend_p': None
                })

            # Weakening rate
            if stats['trends'].get('weakening_accelerating'):
                alerts.append({
                    'system': 'AMOC',
                    'metric': 'Weakening Rate',
                    'level': 'WARNING',
                    'value': stats['trends']['weakening_rate_Sv_per_year'],
                    'threshold': -0.05,
                    'message': f"AMOC weakening accelerating: {stats['trends']['weakening_rate_Sv_per_year']:.3f} Sv/year",
                    'trend_tau': None,
                    'trend_p': None
                })

        elif system == 'coral':
            assessment = adapter_data['statistics']['tipping_assessment']

            if assessment['tipped']:
                alerts.append({
                    'system': 'CORAL',
                    'metric': 'Tipping Status',
                    'level': 'CRITICAL',
                    'value': adapter_data['statistics']['current_state']['bleaching_percent'],
                    'threshold': 99.0,
                    'message': f"Coral reefs FULLY TIPPED: {adapter_data['statistics']['current_state']['bleaching_percent']:.1f}% bleached",
                    'trend_tau': None,
                    'trend_p': None
                })

        return alerts

    def run_pipeline(self) -> Dict:
        """Run full EWS monitoring pipeline.

        Returns:
            dict: Pipeline results with alerts
        """
        print("🔄 EWS Pipeline Running...")
        print("=" * 70)

        # Load latest data
        systems_data = self.load_latest_data()

        if not systems_data:
            print("❌ No data loaded, exiting.")
            return {'status': 'error', 'message': 'No data found'}

        # Analyze each system
        all_alerts = []

        for system, adapter_data in systems_data.items():
            print(f"\n📊 Analyzing {system.upper()}...")

            # Run EWS analysis
            if system == 'wais':
                ews_result = self.analyzer.analyze_wais()
            elif system == 'amoc':
                ews_result = self.analyzer.analyze_amoc()
            elif system == 'coral':
                ews_result = self.analyzer.analyze_coral()
            else:
                continue

            # Check EWS thresholds
            ews_alerts = self.check_ews_thresholds(system, ews_result)
            system_alerts = self.check_system_status(system, adapter_data)

            alerts = ews_alerts + system_alerts

            if alerts:
                print(f"   ⚠️  {len(alerts)} alerts generated")
                for alert in alerts:
                    level_emoji = '🔴' if alert['level'] == 'CRITICAL' else '⚠️'
                    print(f"   {level_emoji} [{alert['level']}] {alert['metric']}: {alert['message']}")
            else:
                print(f"   ✅ No alerts")

            all_alerts.extend(alerts)

        # Summary
        print("\n" + "=" * 70)
        print(f"🔔 Total Alerts: {len(all_alerts)}")

        critical_count = len([a for a in all_alerts if a['level'] == 'CRITICAL'])
        warning_count = len([a for a in all_alerts if a['level'] == 'WARNING'])

        print(f"   🔴 CRITICAL: {critical_count}")
        print(f"   ⚠️  WARNING: {warning_count}")

        # Build result
        result = {
            'pipeline_run': {
                'timestamp': datetime.now().isoformat() + 'Z',
                'systems_analyzed': list(systems_data.keys()),
                'alerts_generated': len(all_alerts)
            },
            'alerts': all_alerts,
            'summary': {
                'total': len(all_alerts),
                'critical': critical_count,
                'warning': warning_count
            }
        }

        return result

    def export_alerts(self, result: Dict, output_path: str = None):
        """Export alerts as JSON.

        Args:
            result: Pipeline result from run_pipeline()
            output_path: Output JSON path
        """
        if output_path is None:
            output_path = self.results_path / "ews_pipeline_alerts.json"

        output_path = Path(output_path)

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n✅ Alerts exported to {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Automated EWS Pipeline')
    parser.add_argument('--output', type=str, help='Output JSON path for alerts')

    args = parser.parse_args()

    pipeline = EWSPipeline()
    result = pipeline.run_pipeline()

    if result.get('status') == 'error':
        sys.exit(1)

    pipeline.export_alerts(result, output_path=args.output)

    # Exit with error code if critical alerts
    if result['summary']['critical'] > 0:
        print("\n🔴 CRITICAL alerts detected!")
        sys.exit(2)
    elif result['summary']['warning'] > 0:
        print("\n⚠️  WARNING alerts detected")
        sys.exit(1)
    else:
        print("\n✅ No alerts - systems stable")
        sys.exit(0)


if __name__ == '__main__':
    main()
