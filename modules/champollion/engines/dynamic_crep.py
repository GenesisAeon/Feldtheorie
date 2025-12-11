#!/usr/bin/env python3
"""
Dynamic CREP Calculator Engine
===============================

A generalized metric calculation system that reads metric definitions from
a YAML configuration and dynamically applies algorithms to repository data.

This implements the "Define Top-Down, Measure Bottom-Up" principle:
- Metrics are defined centrally in config/sigillin_core_definition.yaml
- Measurements are performed on aggregated folder metadata
- Results propagate upward through the folder hierarchy

KEY FEATURES:
- Generic: Works with any metric framework (CREP, ROI, Quality, etc.)
- Extensible: Add new algorithms without changing core logic
- Robust: Stub implementations allow testing without real data
- Fractal: Same metrics apply at all scales (file → folder → repo)

Author: Feldtheorie Governance Engine
License: MIT
Version: 1.0.0
"""

import math
import random
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml


class DynamicMetricEngine:
    """
    Dynamically calculates metrics based on YAML configuration.

    This class is intentionally generic - it doesn't know about CREP.
    It reads any metric definition and applies the specified algorithms.
    """

    def __init__(self, config_path: Path | None = None):
        """
        Initialize the engine with a configuration file.

        Args:
            config_path: Path to sigillin_core_definition.yaml
                        If None, searches in standard locations
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self.metrics = self.config.get("active_metrics", {})
        self.algorithm_params = self.config.get("algorithm_params", {})

        # Registry of calculation algorithms
        self.algorithm_registry: dict[str, Callable] = {
            "calculate_coherence": self.calculate_coherence,
            "calculate_resonance": self.calculate_resonance,
            "calculate_emergence": self.calculate_emergence,
            "calculate_potential": self.calculate_potential,
            # Aliases for generic use
            "std_dev_consistency": self.calculate_coherence,
            "link_density": self.calculate_resonance,
            "beta_calc_stub": self.calculate_emergence,
            "keyword_density": self.calculate_potential,
        }

    def _find_config(self) -> Path:
        """Find the configuration file in standard locations."""
        search_paths = [
            Path.cwd() / "config" / "sigillin_core_definition.yaml",
            Path(__file__).parent.parent.parent.parent / "config" / "sigillin_core_definition.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return path

        raise FileNotFoundError(f"Could not find sigillin_core_definition.yaml in: {search_paths}")

    def _load_config(self) -> dict[str, Any]:
        """Load and parse the YAML configuration."""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded metric config: {self.config_path}")
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config {self.config_path}: {e}")

    # =========================================================================
    # MAIN CALCULATION INTERFACE
    # =========================================================================

    def calculate_all_metrics(self, aggregated_data: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate all enabled metrics for a folder.

        Args:
            aggregated_data: The aggregated metadata from recursive_diamond_indexer
                            (output of aggregate_folder_metadata)

        Returns:
            Dictionary with metric results and aggregate score
        """
        results = {
            "metrics": {},
            "aggregate_score": 0.0,
            "weighted_components": {},
            "timestamp": aggregated_data.get("timestamp", ""),
            "folder": aggregated_data.get("folder_name", "unknown"),
        }

        total_weight = 0.0
        weighted_sum = 0.0

        # Calculate each enabled metric
        for metric_key, metric_def in self.metrics.items():
            if not metric_def.get("enabled", True):
                continue  # Skip disabled metrics

            algorithm_name = metric_def.get("algorithm")
            weight = metric_def.get("weight", 1.0)

            # Get the calculation function
            algorithm_func = self.algorithm_registry.get(algorithm_name)

            if not algorithm_func:
                print(
                    f"⚠️  Warning: Algorithm '{algorithm_name}' not found for metric '{metric_key}'"
                )
                continue

            # Calculate the metric value
            try:
                value = algorithm_func(aggregated_data, metric_def)

                results["metrics"][metric_key] = {
                    "label": metric_def.get("label", metric_key),
                    "value": round(value, 4),
                    "weight": weight,
                    "weighted_value": round(value * weight, 4),
                    "threshold_status": self._check_threshold(
                        value, metric_def.get("thresholds", {})
                    ),
                }

                # Accumulate for aggregate score
                weighted_sum += value * weight
                total_weight += weight

            except Exception as e:
                print(f"⚠️  Error calculating metric '{metric_key}': {e}")
                results["metrics"][metric_key] = {
                    "label": metric_def.get("label", metric_key),
                    "value": 0.0,
                    "error": str(e),
                }

        # Calculate aggregate score
        if total_weight > 0:
            aggregate_score = weighted_sum / total_weight

            # Normalize if configured
            if self.config.get("aggregation", {}).get("normalize", True):
                aggregate_score = max(0.0, min(1.0, aggregate_score))

            results["aggregate_score"] = round(aggregate_score, 4)

        return results

    def _check_threshold(self, value: float, thresholds: dict[str, float]) -> str:
        """Determine threshold status (excellent/good/warning/critical)."""
        if not thresholds:
            return "unknown"

        if value >= thresholds.get("excellent", float("inf")):
            return "excellent"
        elif value >= thresholds.get("good", float("inf")):
            return "good"
        elif value >= thresholds.get("warning", float("inf")):
            return "warning"
        elif value >= thresholds.get("critical", 0):
            return "critical"
        else:
            return "critical"

    # =========================================================================
    # METRIC CALCULATION ALGORITHMS
    # =========================================================================

    def calculate_coherence(self, data: dict[str, Any], metric_def: dict[str, Any]) -> float:
        """
        Calculate Coherence: Internal consistency of the folder.

        Based on:
        - Confidence score variance (low variance = high coherence)
        - Keyword alignment across subfolders
        - Origin diversity (mixed origins = potential inconsistency)

        Returns: Score in range [0, 1] typically, higher = more coherent
        """
        params = self.algorithm_params.get("coherence", {})

        coherence_score = 1.0  # Start optimistic

        # 1. Confidence variance check
        if params.get("use_confidence_variance", True):
            confidence_scores = data.get("confidence_scores", [])
            if len(confidence_scores) > 1:
                mean_conf = sum(confidence_scores) / len(confidence_scores)
                variance = sum((x - mean_conf) ** 2 for x in confidence_scores) / len(
                    confidence_scores
                )
                std_dev = math.sqrt(variance)

                # Lower std_dev = higher coherence
                coherence_from_variance = 1.0 - min(std_dev, 1.0)
                coherence_score *= coherence_from_variance

        # 2. Keyword alignment (how many keywords are shared vs unique)
        if params.get("use_keyword_alignment", True):
            keywords = data.get("keywords", [])
            subfolder_contexts = data.get("subfolder_contexts", [])

            if keywords and subfolder_contexts:
                # Count keyword overlap with subfolders
                folder_kw_set = set(keywords)
                overlap_count = 0
                total_comparisons = 0

                for sf in subfolder_contexts:
                    sf_keywords = set(sf.get("keywords", []))
                    if sf_keywords:
                        overlap = len(folder_kw_set & sf_keywords)
                        overlap_count += overlap
                        total_comparisons += len(sf_keywords)

                if total_comparisons > 0:
                    keyword_coherence = overlap_count / total_comparisons
                    coherence_score *= 0.7 + 0.3 * keyword_coherence  # Weighted blend

        # 3. Origin diversity penalty
        if params.get("use_origin_diversity", True):
            origins = data.get("origins", {})
            num_origins = len([k for k, v in origins.items() if v > 0])

            # Fewer origins = more coherent (single source of truth)
            if num_origins > 0:
                origin_coherence = 1.0 / num_origins  # Inverse relationship
                coherence_score *= 0.8 + 0.2 * origin_coherence

        return min(coherence_score, 1.0)  # Cap at 1.0

    def calculate_resonance(self, data: dict[str, Any], metric_def: dict[str, Any]) -> float:
        """
        Calculate Resonance: Connectivity to other parts of the system.

        Based on:
        - Number of subfolders (more connections = higher resonance)
        - Keyword density and overlap
        - Internal reference counting (future: parse files for links)

        Returns: Score in range [0, 1+], where >1 indicates high connectivity
        """
        params = self.algorithm_params.get("resonance", {})

        resonance_score = 0.0

        # 1. Subfolder connectivity
        num_subfolders = data.get("total_subfolders", 0)
        if num_subfolders > 0:
            # Logarithmic scale: more folders = more resonance, but diminishing returns
            resonance_score += math.log(num_subfolders + 1) / 3.0

        # 2. Keyword overlap (shared vocabulary = resonance)
        if params.get("count_keyword_overlap", True):
            keywords = data.get("keywords", [])
            subfolder_contexts = data.get("subfolder_contexts", [])

            if keywords and subfolder_contexts:
                overlap_ratios = []
                for sf in subfolder_contexts:
                    sf_kw = set(sf.get("keywords", []))
                    folder_kw = set(keywords)
                    if sf_kw and folder_kw:
                        overlap = len(sf_kw & folder_kw) / len(folder_kw)
                        overlap_ratios.append(overlap)

                if overlap_ratios:
                    avg_overlap = sum(overlap_ratios) / len(overlap_ratios)
                    resonance_score += avg_overlap * 0.5

        # 3. Metadata file count (more metadata = more documented connections)
        num_metadata = len(data.get("metadata_files", []))
        if num_metadata > 0:
            resonance_score += min(num_metadata / 10.0, 0.3)  # Cap contribution

        # Apply decay factor if distant connections exist
        decay = params.get("decay_factor", 1.0)
        resonance_score *= decay

        return resonance_score

    def calculate_emergence(self, data: dict[str, Any], metric_def: dict[str, Any]) -> float:
        """
        Calculate Emergence: Novelty and phase transition indicators.

        For Feldtheorie: This would analyze Ising model beta (β) and entropy.
        For general use: Stub returns a simulated value based on file diversity.

        STUB MODE (default):
        - Generates semi-random value with deterministic seed from folder path
        - Adds variance based on file type diversity

        Returns: Score in range [0, 2], where >1 indicates high emergence
        """
        params = self.algorithm_params.get("emergence", {})
        mode = params.get("mode", "stub")

        if mode == "stub":
            # Deterministic randomness from folder name
            folder_name = data.get("folder_name", "default")
            random.seed(hash(folder_name) % 10000)

            base_emergence = random.uniform(0.5, 1.5)

            # Add variance from file diversity
            file_types = data.get("file_types", {})
            diversity_bonus = len(file_types) / 10.0  # More types = more emergence

            # Add noise
            randomness = params.get("stub_randomness", 0.3)
            noise = random.uniform(-randomness, randomness)

            emergence_score = base_emergence + diversity_bonus + noise

            return max(0.0, emergence_score)  # No negative emergence

        elif mode == "entropy":
            # Shannon entropy of file types
            file_types = data.get("file_types", {})
            if not file_types:
                return 0.5  # Default

            total_files = sum(file_types.values())
            entropy = 0.0
            base = params.get("entropy_base", 2)

            for count in file_types.values():
                if count > 0:
                    p = count / total_files
                    entropy -= p * math.log(p, base)

            # Normalize to [0, 1+]
            max_entropy = math.log(len(file_types), base) if len(file_types) > 1 else 1.0
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

            return normalized_entropy

        elif mode == "beta_ising":
            # Placeholder for future Ising model integration
            # Would require time-series data and statistical physics calculations
            print("⚠️  Warning: 'beta_ising' mode not yet implemented, using stub")
            return self.calculate_emergence(data, {**metric_def, "mode": "stub"})

        else:
            return 0.5  # Default fallback

    def calculate_potential(self, data: dict[str, Any], metric_def: dict[str, Any]) -> float:
        """
        Calculate Potential: Future capacity and growth opportunities.

        Based on:
        - TODO/FIXME markers in documentation
        - Keyword density (rich vocabulary = potential for expansion)
        - Presence of experimental/draft markers

        Returns: Score in range [0, 1], higher = more potential
        """
        params = self.algorithm_params.get("potential", {})
        markers = metric_def.get("markers", ["TODO", "FIXME", "DRAFT"])

        potential_score = 0.0

        # 1. Keyword density (more keywords = more conceptual richness)
        keywords = data.get("keywords", [])
        total_files = data.get("total_files", 1)

        keyword_density = len(keywords) / max(total_files, 1)
        keyword_contribution = min(keyword_density / 5.0, 0.4)  # Cap at 0.4

        weight = params.get("keyword_density_weight", 0.6)
        potential_score += keyword_contribution * weight

        # 2. TODO marker detection (scan file contents if enabled)
        if params.get("scan_file_contents", False):
            # This would require reading files - expensive operation
            # For now, use a stub based on folder characteristics

            # Assume folders with many metadata files have more TODOs
            num_metadata = len(data.get("metadata_files", []))
            todo_estimate = min(num_metadata / 5.0, 0.3)
            potential_score += todo_estimate * (1.0 - weight)

        # 3. Subfolder count (more structure = more room to grow)
        num_subfolders = data.get("total_subfolders", 0)
        if num_subfolders > 0:
            structure_potential = min(math.log(num_subfolders + 1) / 5.0, 0.3)
            potential_score += structure_potential

        return min(potential_score, 1.0)  # Cap at 1.0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def calculate_folder_sigillin(
    aggregated_data: dict[str, Any], config_path: Path | None = None
) -> dict[str, Any]:
    """
    Convenience function: Calculate all metrics for a folder in one call.

    Args:
        aggregated_data: Output from recursive_diamond_indexer.aggregate_folder_metadata()
        config_path: Optional path to config (auto-detected if None)

    Returns:
        Dictionary with all metric results
    """
    engine = DynamicMetricEngine(config_path=config_path)
    return engine.calculate_all_metrics(aggregated_data)


def format_metrics_for_display(metrics_result: dict[str, Any]) -> str:
    """
    Format metric results as a human-readable string for README insertion.

    Args:
        metrics_result: Output from calculate_all_metrics()

    Returns:
        Formatted markdown string
    """
    lines = []

    # Aggregate score with emoji
    score = metrics_result.get("aggregate_score", 0.0)
    if score >= 0.9:
        emoji = "🟢"
    elif score >= 0.7:
        emoji = "🟡"
    elif score >= 0.5:
        emoji = "🟠"
    else:
        emoji = "🔴"

    lines.append(f"**Aggregate Score:** {emoji} {score:.3f}")
    lines.append("")

    # Individual metrics
    lines.append("**Component Metrics:**")
    for key, metric in metrics_result.get("metrics", {}).items():
        label = metric.get("label", key)
        value = metric.get("value", 0.0)
        status = metric.get("threshold_status", "unknown")

        status_emoji = {
            "excellent": "🟢",
            "good": "🟡",
            "warning": "🟠",
            "critical": "🔴",
            "unknown": "⚪",
        }.get(status, "⚪")

        lines.append(f"- **{label}** ({key}): {status_emoji} {value:.3f}")

    return "\n".join(lines)


# =============================================================================
# CLI TESTING INTERFACE
# =============================================================================

if __name__ == "__main__":
    """Test the engine with dummy data."""
    print("=" * 80)
    print("Testing Dynamic Metric Engine")
    print("=" * 80)

    # Create dummy aggregated data (simulates indexer output)
    dummy_data = {
        "folder_name": "test_folder",
        "folder_path": "modules/test",
        "timestamp": "2025-11-23T12:00:00Z",
        "total_files": 15,
        "total_subfolders": 3,
        "metadata_files": [
            {"file": "meta1.json", "origin": "empirical", "confidence": 0.9},
            {"file": "meta2.json", "origin": "empirical", "confidence": 0.85},
        ],
        "subfolder_contexts": [
            {
                "folder": "subfolder1",
                "summary": "Test 1",
                "confidence": 0.88,
                "total_items": 5,
                "keywords": ["test", "data"],
            },
            {
                "folder": "subfolder2",
                "summary": "Test 2",
                "confidence": 0.92,
                "total_items": 7,
                "keywords": ["test", "analysis"],
            },
        ],
        "origins": {"empirical": 2},
        "confidence_scores": [0.9, 0.85, 0.88, 0.92],
        "governance_violations": [],
        "keywords": ["test", "data", "analysis", "machine_learning"],
        "file_types": {".py": 10, ".md": 3, ".json": 2},
    }

    # Calculate metrics
    engine = DynamicMetricEngine()
    results = engine.calculate_all_metrics(dummy_data)

    # Display results
    print("\n📊 Metric Calculation Results:")
    print("-" * 80)
    print(f"Folder: {results['folder']}")
    print(f"Aggregate Score: {results['aggregate_score']:.4f}")
    print()

    for key, metric in results["metrics"].items():
        print(f"{key} ({metric['label']}):")
        print(f"  Value: {metric['value']:.4f}")
        print(f"  Weight: {metric['weight']}")
        print(f"  Weighted: {metric['weighted_value']:.4f}")
        print(f"  Status: {metric['threshold_status']}")
        print()

    print("\n📝 Formatted for README:")
    print("-" * 80)
    print(format_metrics_for_display(results))
    print()
