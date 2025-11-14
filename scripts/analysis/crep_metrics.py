#!/usr/bin/env python3
"""
CREP Metrics Analysis
=====================

CREP: Coherence, Resonance, Emergence, Poetics

Computes multi-dimensional system health metrics for tipping point analysis.

**Coherence (C)**: Internal consistency of Early Warning Signals
  - Variance & AR(1) alignment
  - Spectral coherence
  - Trend correlation

**Resonance (R)**: Cross-system coupling strength
  - Inter-system correlations
  - Cascade potential
  - Field coupling

**Emergence (E)**: Novel dynamics appearing near tipping point
  - Bifurcation detection
  - Regime shift indicators
  - Novelty score

**Poetics (P)**: Narrative/interpretive dimension
  - System status metaphor
  - Urgency score
  - Legibility (how clear is the signal?)

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple


class CREPAnalyzer:
    """Compute CREP metrics for tipping point systems."""

    def __init__(self, results_path: str = None):
        """Initialize CREP analyzer.

        Args:
            results_path: Path to analysis results directory
        """
        if results_path is None:
            results_path = Path(__file__).parent / "results"

        self.results_path = Path(results_path)
        self.systems_data = {}
        self.crep_scores = {}

    def load_data(self):
        """Load all analysis results."""
        # Load adapter outputs
        for system in ['wais', 'amoc', 'coral']:
            adapter_file = self.results_path / f"{system}_adapter_output.json"
            with open(adapter_file, 'r') as f:
                self.systems_data[system] = {'adapter': json.load(f)}

        # Load beta fits
        beta_file = self.results_path / "beta_fits_v3.json"
        with open(beta_file, 'r') as f:
            beta_data = json.load(f)
            for system in ['WAIS', 'AMOC', 'Coral']:
                sys_key = system.lower()
                self.systems_data[sys_key]['beta'] = beta_data['systems'][system]

        # Load EWS
        ews_file = self.results_path / "ews_analysis_v3.json"
        with open(ews_file, 'r') as f:
            ews_data = json.load(f)
            for system in ['WAIS', 'AMOC', 'Coral']:
                sys_key = system.lower()
                self.systems_data[sys_key]['ews'] = ews_data['systems'][system]

    def compute_coherence(self, system: str) -> Dict:
        """Compute Coherence (C): Internal consistency of EWS.

        Coherence measures how aligned different Early Warning Signals are.
        High coherence = strong, consistent signal. Low = noisy/ambiguous.

        Args:
            system: System name ('wais', 'amoc', 'coral')

        Returns:
            dict: Coherence metrics
        """
        ews = self.systems_data[system]['ews']

        # Extract EWS components
        variance_trend = ews['variance_ews']['trend']
        ar1_trend = ews['ar1_ews']['trend']
        var_increase = ews['variance_ews']['increase_percent']
        ar1_increase = ews['ar1_ews']['increase_percent']

        # Component 1: Trend alignment (both τ positive and significant)
        both_positive = (variance_trend['tau'] > 0 and ar1_trend['tau'] > 0)
        both_significant = (variance_trend['significant'] and ar1_trend['significant'])
        trend_alignment = 1.0 if (both_positive and both_significant) else (
            0.5 if both_positive else 0.0
        )

        # Component 2: Magnitude consistency (both increasing or both stable)
        var_increasing = var_increase > 5.0
        ar1_increasing = ar1_increase > 5.0
        magnitude_consistency = 1.0 if (var_increasing and ar1_increasing) else (
            0.3 if (var_increasing or ar1_increasing) else 0.0
        )

        # Component 3: Kendall τ correlation between variance and AR(1) trends
        tau_correlation = abs(variance_trend['tau'] * ar1_trend['tau'])  # Product of τ values

        # Overall coherence (weighted average)
        coherence_score = (
            0.40 * trend_alignment +
            0.35 * magnitude_consistency +
            0.25 * tau_correlation
        )

        return {
            'score': float(coherence_score),
            'components': {
                'trend_alignment': float(trend_alignment),
                'magnitude_consistency': float(magnitude_consistency),
                'tau_correlation': float(tau_correlation)
            },
            'interpretation': self._interpret_coherence(coherence_score)
        }

    def compute_resonance(self, system: str) -> Dict:
        """Compute Resonance (R): Cross-system coupling strength.

        Resonance measures how strongly this system is coupled to others.
        High resonance = potential for cascades. Low = isolated.

        Args:
            system: System name ('wais', 'amoc', 'coral')

        Returns:
            dict: Resonance metrics
        """
        # For now: theoretical coupling based on known physical connections
        # WAIS ↔ AMOC: Meltwater input weakens AMOC
        # AMOC ↔ Coral: Temperature/circulation affects coral habitat
        # Coral ↔ WAIS: Weak coupling (both affected by global temp)

        coupling_matrix = {
            'wais': {
                'amoc': 0.75,  # Strong: WAIS meltwater → AMOC weakening
                'coral': 0.25  # Weak: Both respond to global warming
            },
            'amoc': {
                'wais': 0.60,  # Moderate: AMOC collapse → regional cooling affects WAIS
                'coral': 0.70  # Strong: AMOC affects Atlantic coral via SST/circulation
            },
            'coral': {
                'wais': 0.15,  # Very weak
                'amoc': 0.35   # Moderate: Coral death → albedo feedback → circulation
            }
        }

        # Get coupling strengths to other systems
        couplings = coupling_matrix[system]

        # Component 1: Average coupling strength
        avg_coupling = np.mean(list(couplings.values()))

        # Component 2: Cascade potential (max coupling × system proximity to tipping)
        adapter = self.systems_data[system]['adapter']
        distance_to_tip = adapter['statistics']['current_state']['distance_to_tipping']
        proximity = 1.0 - distance_to_tip
        max_coupling = max(couplings.values())
        cascade_potential = max_coupling * proximity

        # Component 3: Bi-directional coupling (how symmetric is the coupling?)
        # Higher symmetry = stronger resonance
        bidirectional_score = 0.0
        for other_sys, strength in couplings.items():
            reverse_strength = coupling_matrix[other_sys][system]
            symmetry = 1.0 - abs(strength - reverse_strength)
            bidirectional_score += symmetry
        bidirectional_score /= len(couplings)

        # Overall resonance
        resonance_score = (
            0.35 * avg_coupling +
            0.45 * cascade_potential +
            0.20 * bidirectional_score
        )

        return {
            'score': float(resonance_score),
            'components': {
                'average_coupling': float(avg_coupling),
                'cascade_potential': float(cascade_potential),
                'bidirectional_symmetry': float(bidirectional_score)
            },
            'couplings': {k: float(v) for k, v in couplings.items()},
            'interpretation': self._interpret_resonance(resonance_score)
        }

    def compute_emergence(self, system: str) -> Dict:
        """Compute Emergence (E): Novel dynamics near tipping point.

        Emergence measures how much "new" behavior is appearing.
        High emergence = system entering novel regime. Low = business as usual.

        Args:
            system: System name ('wais', 'amoc', 'coral')

        Returns:
            dict: Emergence metrics
        """
        adapter = self.systems_data[system]['adapter']
        beta = self.systems_data[system]['beta']
        ews = self.systems_data[system]['ews']

        # Component 1: Logistic preference (ΔAIC > 2 = nonlinear emerging)
        delta_aic = beta['goodness_of_fit']['delta_aic']
        nonlinearity_score = min(1.0, max(0.0, delta_aic / 20.0))  # Normalize to [0,1]

        # Component 2: Critical slowing detection
        critical_slowing = 1.0 if ews['critical_slowing_detected'] else 0.0

        # Component 3: Spectral reddening (shift to low-frequency dominance)
        reddening = ews['spectral_ews']['reddening_ratio']
        spectral_novelty = min(1.0, reddening / 30.0)  # Normalize

        # Component 4: Distance traveled from initial state
        # (Variance increase as proxy for state space exploration)
        var_increase = ews['variance_ews']['increase_percent']
        state_exploration = min(1.0, abs(var_increase) / 200.0)

        # Overall emergence
        emergence_score = (
            0.30 * nonlinearity_score +
            0.30 * critical_slowing +
            0.25 * spectral_novelty +
            0.15 * state_exploration
        )

        return {
            'score': float(emergence_score),
            'components': {
                'nonlinearity': float(nonlinearity_score),
                'critical_slowing': float(critical_slowing),
                'spectral_novelty': float(spectral_novelty),
                'state_exploration': float(state_exploration)
            },
            'interpretation': self._interpret_emergence(emergence_score)
        }

    def compute_poetics(self, system: str) -> Dict:
        """Compute Poetics (P): Narrative/interpretive dimension.

        Poetics measures the "story quality" and urgency of the system.
        High poetics = clear, compelling narrative. Low = ambiguous story.

        Args:
            system: System name ('wais', 'amoc', 'coral')

        Returns:
            dict: Poetics metrics
        """
        adapter = self.systems_data[system]['adapter']
        beta = self.systems_data[system]['beta']
        ews = self.systems_data[system]['ews']

        # Component 1: Urgency (proximity to tipping)
        distance = adapter['statistics']['current_state']['distance_to_tipping']
        urgency = 1.0 - distance

        # Component 2: Legibility (how clear is the signal? R² as proxy)
        r2 = beta['goodness_of_fit']['r2_logistic']
        legibility = r2  # High R² = clear story

        # Component 3: Dramatic arc (is there a compelling trend?)
        var_tau = ews['variance_ews']['trend']['tau']
        ar1_tau = ews['ar1_ews']['trend']['tau']
        dramatic_tension = (abs(var_tau) + abs(ar1_tau)) / 2.0

        # Component 4: Status metaphor (post-tipping systems have "complete" narratives)
        status = adapter['metadata']['status']
        if 'TIPPED' in status:
            narrative_completeness = 1.0
        elif 'TIPPING' in status or 'WEAKENING' in status:
            narrative_completeness = 0.7
        else:
            narrative_completeness = 0.3

        # Overall poetics
        poetics_score = (
            0.35 * urgency +
            0.25 * legibility +
            0.20 * dramatic_tension +
            0.20 * narrative_completeness
        )

        # Generate narrative
        narrative = self._generate_narrative(system, urgency, legibility, status)

        return {
            'score': float(poetics_score),
            'components': {
                'urgency': float(urgency),
                'legibility': float(legibility),
                'dramatic_tension': float(dramatic_tension),
                'narrative_completeness': float(narrative_completeness)
            },
            'narrative': narrative,
            'interpretation': self._interpret_poetics(poetics_score)
        }

    def analyze_system(self, system: str) -> Dict:
        """Compute full CREP analysis for a system.

        Args:
            system: System name ('wais', 'amoc', 'coral')

        Returns:
            dict: Complete CREP metrics
        """
        C = self.compute_coherence(system)
        R = self.compute_resonance(system)
        E = self.compute_emergence(system)
        P = self.compute_poetics(system)

        # Overall CREP score (geometric mean)
        crep_overall = (C['score'] * R['score'] * E['score'] * P['score']) ** 0.25

        return {
            'system': system.upper(),
            'coherence': C,
            'resonance': R,
            'emergence': E,
            'poetics': P,
            'overall_crep': float(crep_overall),
            'rating': self._rate_crep(crep_overall)
        }

    def analyze_all(self) -> Dict:
        """Analyze all systems."""
        for system in ['wais', 'amoc', 'coral']:
            self.crep_scores[system] = self.analyze_system(system)

        return self.crep_scores

    def export_results(self, output_path: str = None):
        """Export CREP results as JSON."""
        if output_path is None:
            output_path = self.results_path / "crep_metrics_v3.json"

        output_path = Path(output_path)

        export = {
            'metadata': {
                'analysis': 'CREP Metrics',
                'version': '1.0.0',
                'components': {
                    'C': 'Coherence - Internal consistency of EWS',
                    'R': 'Resonance - Cross-system coupling',
                    'E': 'Emergence - Novel dynamics',
                    'P': 'Poetics - Narrative dimension'
                },
                'generated': np.datetime64('now').astype(str) + 'Z'
            },
            'systems': self.crep_scores
        }

        with open(output_path, 'w') as f:
            json.dump(export, f, indent=2)

        return str(output_path)

    # ==================== Helper Methods ====================

    @staticmethod
    def _interpret_coherence(score: float) -> str:
        if score > 0.7:
            return "High coherence - EWS strongly aligned"
        elif score > 0.4:
            return "Moderate coherence - mixed signals"
        else:
            return "Low coherence - weak/inconsistent signals"

    @staticmethod
    def _interpret_resonance(score: float) -> str:
        if score > 0.6:
            return "High resonance - strong cascade potential"
        elif score > 0.3:
            return "Moderate resonance - some coupling"
        else:
            return "Low resonance - isolated system"

    @staticmethod
    def _interpret_emergence(score: float) -> str:
        if score > 0.6:
            return "High emergence - entering novel regime"
        elif score > 0.3:
            return "Moderate emergence - nonlinear dynamics appearing"
        else:
            return "Low emergence - linear/stable regime"

    @staticmethod
    def _interpret_poetics(score: float) -> str:
        if score > 0.7:
            return "High poetics - clear, urgent narrative"
        elif score > 0.4:
            return "Moderate poetics - developing story"
        else:
            return "Low poetics - ambiguous narrative"

    @staticmethod
    def _rate_crep(score: float) -> str:
        if score > 0.7:
            return "CRITICAL"
        elif score > 0.5:
            return "HIGH"
        elif score > 0.3:
            return "MODERATE"
        else:
            return "LOW"

    @staticmethod
    def _generate_narrative(system: str, urgency: float, legibility: float, status: str) -> str:
        """Generate poetic narrative for system."""
        if system == 'wais':
            if urgency > 0.7:
                return "The ice remembers. Variance rises like ancient breath. The sheet trembles at the threshold."
            else:
                return "The ice sheet sleeps restlessly. Subtle tremors. The melt accelerates, but the collapse waits."

        elif system == 'amoc':
            if 'TIPPED' in status:
                return "The current has turned. FovS crosses zero. The Atlantic forgets how to flow. Europe will freeze."
            else:
                return "The conveyor weakens. The North Atlantic holds its breath. Recovery time lengthens."

        elif system == 'coral':
            if 'TIPPED' in status:
                return "The reefs are silent. 100% bleached. Calcium graveyards stretch beneath warming seas. The first fallen threshold."
            else:
                return "The coral bleaches in waves. DHW rises. The symbiosis fractures. The reef forgets color."

        return "System dynamics evolving."


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='CREP Metrics Analysis')
    parser.add_argument('--system', type=str, choices=['wais', 'amoc', 'coral', 'all'], default='all')
    parser.add_argument('--output', type=str, help='Output JSON path')

    args = parser.parse_args()

    analyzer = CREPAnalyzer()
    analyzer.load_data()

    print("🎨 CREP Metrics Analysis")
    print("=" * 70)
    print("C: Coherence | R: Resonance | E: Emergence | P: Poetics")
    print("=" * 70)

    if args.system == 'all':
        results = analyzer.analyze_all()

        for system, metrics in results.items():
            print(f"\n📊 {system.upper()}")
            print("─" * 70)
            print(f"   Coherence (C):  {metrics['coherence']['score']:.3f} - {metrics['coherence']['interpretation']}")
            print(f"   Resonance (R):  {metrics['resonance']['score']:.3f} - {metrics['resonance']['interpretation']}")
            print(f"   Emergence (E):  {metrics['emergence']['score']:.3f} - {metrics['emergence']['interpretation']}")
            print(f"   Poetics (P):    {metrics['poetics']['score']:.3f} - {metrics['poetics']['interpretation']}")
            print(f"\n   Overall CREP:   {metrics['overall_crep']:.3f} [{metrics['rating']}]")
            print(f"\n   Narrative: \"{metrics['poetics']['narrative']}\"")

    else:
        metrics = analyzer.analyze_system(args.system)
        print(f"\n📊 {metrics['system']}")
        print("─" * 70)
        print(f"   Coherence (C):  {metrics['coherence']['score']:.3f}")
        print(f"   Resonance (R):  {metrics['resonance']['score']:.3f}")
        print(f"   Emergence (E):  {metrics['emergence']['score']:.3f}")
        print(f"   Poetics (P):    {metrics['poetics']['score']:.3f}")
        print(f"\n   Overall CREP:   {metrics['overall_crep']:.3f} [{metrics['rating']}]")

    # Export
    output_path = analyzer.export_results(output_path=args.output)
    print(f"\n✅ CREP metrics exported to {output_path}")
    print("=" * 70)


if __name__ == '__main__':
    main()
