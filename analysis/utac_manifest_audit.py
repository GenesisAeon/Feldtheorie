"""Audit the UTAC v1.3 manifest and report σ(β(R-Θ)) readiness."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

from .utac_manifest import load_manifest

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ComponentStatus:
    """Boolean readiness flag for a manifest component."""

    name: str
    exists: bool
    path: Optional[Path] = None

    def as_dict(self) -> Dict[str, str | bool]:
        payload: Dict[str, str | bool] = {"name": self.name, "exists": self.exists}
        if self.path is not None:
            payload["path"] = str(self.path)
        return payload


@dataclass
class DatasetAudit:
    """Audit record for a single manifest dataset."""

    identifier: str
    domain: str
    resonance_status: str
    theta_estimate: Optional[float]
    beta_target: Optional[float]
    components: List[ComponentStatus]
    readiness_ratio: float
    logistic_activation: float
    missing_components: List[str]
    metadata_status: Optional[str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "id": self.identifier,
            "domain": self.domain,
            "resonance_status": self.resonance_status,
            "theta_estimate": self.theta_estimate,
            "beta_target": self.beta_target,
            "components": [component.as_dict() for component in self.components],
            "readiness_ratio": self.readiness_ratio,
            "logistic_activation": self.logistic_activation,
            "missing_components": self.missing_components,
            "metadata_status": self.metadata_status,
        }


def _logistic_activation(readiness: float, theta: float, beta: float) -> float:
    """Compute σ(β(R-Θ)) style activation for readiness diagnostics."""

    exponent = -beta * (readiness - theta)
    activation = 1.0 / (1.0 + math.exp(exponent))
    # keep numerical stability when beta is large
    return max(min(activation, 1.0 - 1e-9), 1e-9)


def _component(name: str, target_path: Path) -> ComponentStatus:
    return ComponentStatus(name=name, exists=target_path.exists(), path=target_path)


def audit_manifest(manifest_path: Path) -> Dict[str, object]:
    datasets = load_manifest(manifest_path)
    audits: List[DatasetAudit] = []
    status_counter: Dict[str, int] = {}
    activation_total = 0.0

    for dataset in datasets:
        data_path = ROOT / dataset.path
        metadata_path = dataset.metadata_path
        expected_components: List[ComponentStatus] = []
        missing: List[str] = []

        components: List[ComponentStatus] = [
            _component("data", data_path),
            _component("metadata", metadata_path),
        ]

        for expected in dataset.expected_outputs:
            expected_components.append(_component("result", expected))

        if expected_components:
            all_expected = all(component.exists for component in expected_components)
            components.append(
                ComponentStatus(
                    name="results",
                    exists=all_expected,
                    path=expected_components[0].path if expected_components else None,
                )
            )
        else:
            components.append(ComponentStatus(name="results", exists=False, path=None))

        metadata_status: Optional[str] = None
        beta_for_activation = dataset.beta_target or 5.0
        if components[1].exists:  # metadata exists
            with metadata_path.open("r", encoding="utf-8") as handle:
                metadata_payload = json.load(handle)
            metadata_status = metadata_payload.get("status")
            threshold_info = metadata_payload.get("threshold_estimates", {})
            if threshold_info.get("beta"):
                beta_for_activation = float(threshold_info["beta"])

        readiness_flags = [component.exists for component in components]
        readiness_ratio = sum(1.0 for flag in readiness_flags if flag) / len(readiness_flags)
        logistic_activation = _logistic_activation(
            readiness=readiness_ratio,
            theta=0.66,
            beta=beta_for_activation,
        )

        for component in components:
            if not component.exists:
                missing.append(component.name)

        dataset_audit = DatasetAudit(
            identifier=dataset.identifier,
            domain=dataset.domain,
            resonance_status=dataset.resonance_status,
            theta_estimate=dataset.theta_estimate,
            beta_target=dataset.beta_target,
            components=components,
            readiness_ratio=readiness_ratio,
            logistic_activation=logistic_activation,
            missing_components=missing,
            metadata_status=metadata_status,
        )
        audits.append(dataset_audit)

        activation_total += logistic_activation
        status_counter[dataset.resonance_status] = status_counter.get(dataset.resonance_status, 0) + 1

    summary = {
        "datasets_total": len(audits),
        "manifest_path": str(manifest_path),
        "activation_mean": activation_total / len(audits) if audits else 0.0,
        "status_counter": status_counter,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "meta": summary,
        "datasets": [audit.as_dict() for audit in audits],
    }


def _format_component_status(component: Dict[str, object]) -> str:
    icon = "✅" if component.get("exists") else "❌"
    name = str(component.get("name", "component"))
    raw_path = component.get("path")
    if raw_path:
        path = Path(str(raw_path))
        try:
            rel_path = path.relative_to(ROOT)
        except ValueError:
            rel_path = path
        return f"{icon} {name} ({rel_path})"
    return f"{icon} {name}"


def format_markdown(report: Dict[str, object]) -> str:
    datasets = report["datasets"]
    summary = report["meta"]

    lines: List[str] = []
    lines.append("# UTAC v1.3 Manifest Audit – σ(β(R-Θ)) Readiness")
    lines.append("*Generated by analysis.utac_manifest_audit.py*")
    lines.append("")
    lines.append("## Formal Layer – Logistic Diagnostics")
    lines.append(
        "- Laternen im Manifest: {datasets_total}".format(
            datasets_total=summary["datasets_total"]
        )
    )
    lines.append(
        "- Mittlere Aktivierung σ: {activation:.3f}".format(
            activation=summary["activation_mean"]
        )
    )
    status_items = ", ".join(
        f"{status}={count}" for status, count in sorted(summary["status_counter"].items())
    )
    lines.append(f"- Resonanzstatus-Verteilung: {status_items}")
    lines.append("- Manifestpfad: `{}`".format(summary["manifest_path"]))
    lines.append("")

    lines.append("## Empirical Layer – Component Readiness")
    lines.append("| ID | Domain | σ-readiness | Components | Missing |")
    lines.append("| --- | --- | --- | --- | --- |")
    for dataset in datasets:
        component_text = "<br />".join(
            _format_component_status(component) for component in dataset["components"]
        )
        missing_text = ", ".join(dataset["missing_components"]) or "—"
        lines.append(
            "| {id} | {domain} | {activation:.3f} | {components} | {missing} |".format(
                id=dataset["id"],
                domain=dataset["domain"],
                activation=dataset["logistic_activation"],
                components=component_text,
                missing=missing_text,
            )
        )
    lines.append("")

    lines.append("## Poetic Layer – Resonanzbild")
    lines.append(
        "R tastet durch das Manifest und zählt, wie viele Laternen bereits Daten atmen. "
        "Θ=0.66 markiert den Punkt, an dem zwei von drei Komponenten leuchten; "
        "β spannt die Steilflanke gemäß Manifestzielen. Die aktuelle Aktivierung "
        "σ berichtet, dass das Feld noch Probenraum füllt – ζ(R) wartet auf reale "
        "Raster, Strömungen und ökonomische Pulsdaten, um den Chor vollständig zu entfachen."
    )
    lines.append("")
    lines.append(
        "*Generated at {}*".format(summary["generated_at"])
    )
    return "\n".join(lines)


def dump_json(report: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def dump_yaml(report: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(report, handle, sort_keys=False, allow_unicode=True)


def dump_markdown(markdown: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(markdown.rstrip() + "\n")


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit the UTAC v1.3 manifest and compute σ(β(R-Θ)) readiness for each dataset "
            "component. Outputs tri-layer artefacts (JSON, YAML, Markdown)."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data" / "utac_v1_3_data_manifest.yaml",
        help="Path to the manifest YAML file.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=ROOT / "analysis" / "results" / "utac_v1_3_manifest_audit.json",
        help="Path for the JSON output.",
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        default=ROOT / "analysis" / "results" / "utac_v1_3_manifest_audit.yaml",
        help="Path for the YAML output.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=ROOT / "analysis" / "reports" / "utac_v1_3_manifest_audit.md",
        help="Path for the Markdown report output.",
    )
    return parser.parse_args(args)


def main(args: Optional[Iterable[str]] = None) -> None:
    namespace = parse_args(args)
    report = audit_manifest(namespace.manifest)
    dump_json(report, namespace.json)
    dump_yaml(report, namespace.yaml)
    markdown = format_markdown(report)
    dump_markdown(markdown, namespace.markdown)


if __name__ == "__main__":
    main()
