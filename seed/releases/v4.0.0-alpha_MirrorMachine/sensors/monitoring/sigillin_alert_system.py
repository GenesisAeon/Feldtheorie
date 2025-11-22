#!/usr/bin/env python3
"""
Sigillin Alert System
=====================

Phase 4: v3-feat-p4-002

Transforms EWS Pipeline alerts into Sigillin trilayer format (YAML/JSON/MD).

Sigillin Integration:
- Reads alerts from EWS pipeline
- Generates trilayer semantic memory entries
- Creates alert documents with formal/empirical/poetic threads
- Exports to Sigillin-compatible format

Alert Document Structure:
  id: alert-{timestamp}-{system}
  level: CRITICAL | WARNING
  system: WAIS | AMOC | CORAL
  metric: Variance | AR(1) | FovS | etc.
  formal: Technical alert details
  empirical: Measurements and thresholds
  poetic: Narrative interpretation

Author: Claude Sonnet 4.5
Date: 2025-11-14
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class SigillinAlertSystem:
    """Generates Sigillin-compatible alert documents."""

    def __init__(self, alerts_path: str = None, output_dir: str = None):
        """Initialize alert system.

        Args:
            alerts_path: Path to EWS pipeline alerts JSON
            output_dir: Output directory for Sigillin docs
        """
        if alerts_path is None:
            alerts_path = Path(__file__).parent.parent / "analysis" / "results" / "ews_pipeline_alerts.json"

        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "seed" / "FraktaltagebuchV3" / "alerts"

        self.alerts_path = Path(alerts_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_alerts(self) -> Dict:
        """Load alerts from EWS pipeline.

        Returns:
            dict: Pipeline alerts
        """
        with open(self.alerts_path, 'r') as f:
            return json.load(f)

    def generate_poetic_narrative(self, alert: Dict) -> str:
        """Generate poetic interpretation for alert.

        Args:
            alert: Alert object

        Returns:
            str: Poetic narrative
        """
        system = alert['system']
        metric = alert['metric']
        level = alert['level']

        # System-specific metaphors
        system_metaphors = {
            'WAIS': "The ice sheet",
            'AMOC': "The great conveyor",
            'CORAL': "The reef"
        }

        metaphor = system_metaphors.get(system, "The system")

        # Level-specific urgency
        if level == 'CRITICAL':
            urgency = "screams"
            action = "collapses"
        else:
            urgency = "whispers"
            action = "trembles"

        # Metric-specific narratives
        narratives = {
            'Variance': f"{metaphor} {urgency}. The variance explodes. Memory of every perturbation. The system cannot forget its wounds.",
            'AR(1)': f"{metaphor} {urgency}. Recovery time lengthens. The system remembers longer, responds slower. Critical slowing approaches.",
            'EWS Trends': f"{metaphor} {urgency}. Both signals rise together. Variance and AR(1) aligned. The membrane thins.",
            'Critical Slowing': f"{metaphor} {urgency}. The system slows. Recovery fails. The attractor weakens. The basin shifts.",
            'Spectral Reddening': f"{metaphor} {urgency}. Low frequencies dominate. The slow modes awaken. Collapse frequency resonates.",
            'Distance to Tipping': f"{metaphor} {action}. The threshold approaches. R → Θ. The membrane is thin.",
            'FovS Indicator': f"{metaphor} has crossed. The Atlantic forgets its rhythm. The freshwater overshoot. Europe will freeze.",
            'Weakening Rate': f"{metaphor} weakens. Each year slower. The meltwater brake. The conveyor stalls.",
            'Tipping Status': f"{metaphor} has fallen. The first threshold. The calcium graveyards. 100% bleached."
        }

        narrative = narratives.get(metric, f"{metaphor} signals change.")

        # Add urgency markers
        if level == 'CRITICAL':
            narrative += f"\n\n🔴 CRITICAL. Immediate attention required."
        else:
            narrative += f"\n\n⚠️  WARNING. Monitor closely."

        return narrative

    def create_alert_document(self, alert: Dict, timestamp: str) -> Dict:
        """Create Sigillin trilayer alert document.

        Args:
            alert: Alert object
            timestamp: ISO timestamp

        Returns:
            dict: Sigillin document (trilayer structure)
        """
        # Generate ID
        alert_id = f"alert-{timestamp.replace(':', '').replace('-', '').split('.')[0]}-{alert['system'].lower()}-{alert['metric'].replace(' ', '-').lower()}"

        # Formal thread: Technical details
        formal_thread = {
            'system': alert['system'],
            'metric': alert['metric'],
            'level': alert['level'],
            'value': alert['value'],
            'threshold': alert['threshold'],
            'trend': {
                'tau': alert.get('trend_tau'),
                'p_value': alert.get('trend_p')
            } if alert.get('trend_tau') is not None else None
        }

        # Empirical thread: Measurements
        empirical_thread = {
            'message': alert['message'],
            'timestamp': timestamp,
            'measurements': {
                'current_value': alert['value'],
                'threshold_value': alert['threshold'],
                'exceedance': self._compute_exceedance(alert)
            }
        }

        # Poetic thread: Narrative
        poetic_thread = {
            'narrative': self.generate_poetic_narrative(alert),
            'urgency': 'MAXIMUM' if alert['level'] == 'CRITICAL' else 'HIGH',
            'status_metaphor': self._get_status_metaphor(alert)
        }

        # Build document
        document = {
            'id': alert_id,
            'type': 'ews_alert',
            'timestamp': timestamp,
            'formal': formal_thread,
            'empirical': empirical_thread,
            'poetic': poetic_thread,
            'metadata': {
                'generated_by': 'Sigillin Alert System v1.0',
                'source': 'EWS Pipeline',
                'version': '1.0.0'
            }
        }

        return document

    def _compute_exceedance(self, alert: Dict) -> float:
        """Compute how much the value exceeds threshold.

        Args:
            alert: Alert object

        Returns:
            float: Exceedance factor (value / threshold)
        """
        try:
            if isinstance(alert['value'], dict):
                # Complex value (e.g., EWS Trends)
                return None

            if isinstance(alert['threshold'], (int, float)) and alert['threshold'] != 0:
                return float(alert['value']) / float(alert['threshold'])
            else:
                return None
        except:
            return None

    def _get_status_metaphor(self, alert: Dict) -> str:
        """Get status metaphor for alert.

        Args:
            alert: Alert object

        Returns:
            str: Status metaphor
        """
        system = alert['system']
        level = alert['level']

        metaphors = {
            ('WAIS', 'CRITICAL'): "The giant awakens, ice forgets solidity",
            ('WAIS', 'WARNING'): "The sheet trembles, the membrane thins",
            ('AMOC', 'CRITICAL'): "The conveyor stalls, the current forgets",
            ('AMOC', 'WARNING'): "The flow weakens, the rhythm breaks",
            ('CORAL', 'CRITICAL'): "The reefs silence, calcium graveyards expand",
            ('CORAL', 'WARNING'): "The symbiosis fractures, color fades"
        }

        return metaphors.get((system, level), "The system changes")

    def generate_trilayer_files(self, document: Dict):
        """Generate YAML, JSON, and MD files for alert document.

        Args:
            document: Sigillin alert document
        """
        doc_id = document['id']

        # YAML
        yaml_path = self.output_dir / f"{doc_id}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(document, f, default_flow_style=False, sort_keys=False)

        # JSON
        json_path = self.output_dir / f"{doc_id}.json"
        with open(json_path, 'w') as f:
            json.dump(document, f, indent=2)

        # Markdown (human-readable)
        md_path = self.output_dir / f"{doc_id}.md"
        self._generate_markdown(document, md_path)

    def _generate_markdown(self, document: Dict, output_path: Path):
        """Generate Markdown alert document.

        Args:
            document: Sigillin document
            output_path: Output path for MD file
        """
        formal = document['formal']
        empirical = document['empirical']
        poetic = document['poetic']

        level_emoji = '🔴' if formal['level'] == 'CRITICAL' else '⚠️'

        md_content = f"""# {level_emoji} {formal['level']}: {formal['system']} - {formal['metric']}

**Alert ID:** `{document['id']}`
**Timestamp:** {document['timestamp']}
**System:** {formal['system']}
**Metric:** {formal['metric']}
**Level:** {level_emoji} **{formal['level']}**

---

## 📊 Formal Thread

### Alert Details

| Field | Value |
|-------|-------|
| **System** | {formal['system']} |
| **Metric** | {formal['metric']} |
| **Level** | {level_emoji} {formal['level']} |
| **Current Value** | {formal['value']} |
| **Threshold** | {formal['threshold']} |
"""

        if formal.get('trend'):
            tau_val = f"{formal['trend']['tau']:.3f}" if formal['trend']['tau'] is not None else 'N/A'
            p_val = f"{formal['trend']['p_value']:.4f}" if formal['trend']['p_value'] is not None else 'N/A'
            md_content += f"""
### Trend Analysis

| Field | Value |
|-------|-------|
| **Kendall τ** | {tau_val} |
| **p-value** | {p_val} |
"""

        md_content += f"""
---

## 🔬 Empirical Thread

### Message

{empirical['message']}

### Measurements

| Field | Value |
|-------|-------|
| **Current Value** | {empirical['measurements']['current_value']} |
| **Threshold** | {empirical['measurements']['threshold_value']} |
"""

        if empirical['measurements'].get('exceedance'):
            md_content += f"| **Exceedance Factor** | {empirical['measurements']['exceedance']:.2f}x |\n"

        md_content += f"""
---

## 🎨 Poetic Thread

### Narrative

{poetic['narrative']}

### Status

- **Urgency:** {poetic['urgency']}
- **Metaphor:** "{poetic['status_metaphor']}"

---

## 🔗 Metadata

**Generated by:** {document['metadata']['generated_by']}
**Source:** {document['metadata']['source']}
**Version:** {document['metadata']['version']}

---

*This alert was automatically generated by the Sigillin Alert System based on Early Warning Signal monitoring.*
"""

        with open(output_path, 'w') as f:
            f.write(md_content)

    def process_all_alerts(self) -> Dict:
        """Process all alerts from EWS pipeline.

        Returns:
            dict: Processing summary
        """
        print("📨 Sigillin Alert System")
        print("=" * 70)

        # Load alerts
        pipeline_result = self.load_alerts()
        alerts = pipeline_result['alerts']
        timestamp = pipeline_result['pipeline_run']['timestamp']

        print(f"\n📥 Loaded {len(alerts)} alerts from EWS pipeline")
        print(f"   Timestamp: {timestamp}")

        # Process each alert
        documents_created = []

        for i, alert in enumerate(alerts, 1):
            print(f"\n📄 Processing alert {i}/{len(alerts)}: {alert['system']} - {alert['metric']}")

            # Create document
            document = self.create_alert_document(alert, timestamp)

            # Generate trilayer files
            self.generate_trilayer_files(document)

            documents_created.append(document['id'])

            level_emoji = '🔴' if alert['level'] == 'CRITICAL' else '⚠️'
            print(f"   {level_emoji} Created {document['id']}")

        # Summary
        print("\n" + "=" * 70)
        print(f"✅ Created {len(documents_created)} Sigillin alert documents")
        print(f"   Output: {self.output_dir}")

        return {
            'documents_created': len(documents_created),
            'document_ids': documents_created,
            'output_directory': str(self.output_dir)
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Sigillin Alert System')
    parser.add_argument('--alerts', type=str, help='Path to EWS pipeline alerts JSON')
    parser.add_argument('--output', type=str, help='Output directory for Sigillin docs')

    args = parser.parse_args()

    system = SigillinAlertSystem(alerts_path=args.alerts, output_dir=args.output)
    result = system.process_all_alerts()

    print(f"\n🎨 Trilayer documents generated:")
    for doc_id in result['document_ids']:
        print(f"   - {doc_id}.{{yaml,json,md}}")


if __name__ == '__main__':
    main()
