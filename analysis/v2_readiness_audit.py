#!/usr/bin/env python3
"""UTAC v2.0 readiness audit generator.

This script inspects the UTAC data manifest, key analysis scripts,
documentation beacons, and simulator presets to quantify how close the
repository is to activating the UTAC v2.0 resonance plateau.

Outputs are emitted as a tri-layer set (JSON, YAML, Markdown) so that
the readiness lantern can plug into indices, dashboards, and human-facing
briefings.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import math
from pathlib import Path
from typing import List, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "data" / "utac_v1_3_data_manifest.yaml"
DEFAULT_OUTPUT_STEM = REPO_ROOT / "analysis" / "reports" / "utac_v2_readiness"


@dataclasses.dataclass
class ComponentStatus:
    name: str
    path: Path
    declared_exists: bool
    actual_exists: bool
    kind: str = "generic"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": rel(self.path),
            "declared_exists": self.declared_exists,
            "actual_exists": self.actual_exists,
            "kind": self.kind,
        }


@dataclasses.dataclass
class DatasetStatus:
    identifier: str
    domain: str
    resonance_status: str
    theta_estimate: float | None
    beta_target: float | None
    declared_readiness_ratio: float | None
    components: List[ComponentStatus]

    def actual_readiness_ratio(self) -> float:
        if not self.components:
            return 0.0
        ready = sum(1 for c in self.components if c.actual_exists)
        return ready / len(self.components)

    def missing_components(self) -> List[ComponentStatus]:
        return [c for c in self.components if not c.actual_exists]

    def to_dict(self) -> dict:
        return {
            "id": self.identifier,
            "domain": self.domain,
            "resonance_status": self.resonance_status,
            "theta_estimate": self.theta_estimate,
            "beta_target": self.beta_target,
            "declared_readiness_ratio": self.declared_readiness_ratio,
            "actual_readiness_ratio": self.actual_readiness_ratio(),
            "missing_components": [c.to_dict() for c in self.missing_components()],
            "components": [c.to_dict() for c in self.components],
        }


@dataclasses.dataclass
class TargetStatus:
    path: Path
    description: str
    expected_outputs: Sequence[Path]
    category: str

    def to_dict(self) -> dict:
        return {
            "path": rel(self.path),
            "description": self.description,
            "category": self.category,
            "exists": self.path.exists(),
            "last_modified": iso_datetime(self.path.stat().st_mtime) if self.path.exists() else None,
            "expected_outputs": [
                {
                    "path": rel(out_path),
                    "exists": out_path.exists(),
                    "last_modified": iso_datetime(out_path.stat().st_mtime) if out_path.exists() else None,
                }
                for out_path in self.expected_outputs
            ],
        }


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def iso_datetime(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).isoformat()


def load_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_dataset_status(manifest: dict) -> List[DatasetStatus]:
    datasets: List[DatasetStatus] = []
    for entry in manifest.get("datasets", []):
        components: List[ComponentStatus] = []
        raw_components = entry.get("components")
        if raw_components:
            for component in raw_components:
                comp_path = (REPO_ROOT / component.get("path", "")).resolve()
                components.append(
                    ComponentStatus(
                        name=component.get("name", "component"),
                        path=comp_path,
                        declared_exists=bool(component.get("exists")),
                        actual_exists=comp_path.exists(),
                        kind=component.get("kind", "generic"),
                    )
                )
        else:
            data_path = (REPO_ROOT / entry.get("path", "")).resolve()
            if entry.get("path"):
                components.append(
                    ComponentStatus(
                        name="data",
                        path=data_path,
                        declared_exists=False,
                        actual_exists=data_path.exists(),
                        kind="data",
                    )
                )
                metadata_path = Path(str(data_path) + ".metadata.json")
                components.append(
                    ComponentStatus(
                        name="metadata",
                        path=metadata_path,
                        declared_exists=False,
                        actual_exists=metadata_path.exists(),
                        kind="metadata",
                    )
                )
            for output in entry.get("expected_outputs", []):
                output_path = (REPO_ROOT / output).resolve()
                components.append(
                    ComponentStatus(
                        name=Path(output).name,
                        path=output_path,
                        declared_exists=False,
                        actual_exists=output_path.exists(),
                        kind="result",
                    )
                )
        datasets.append(
            DatasetStatus(
                identifier=entry.get("id", "unknown"),
                domain=entry.get("domain", "unknown"),
                resonance_status=entry.get("resonance_status", "unknown"),
                theta_estimate=entry.get("theta_estimate")
                or entry.get("threshold_Theta_estimate"),
                beta_target=entry.get("beta_target")
                or entry.get("steepness_beta_target"),
                declared_readiness_ratio=entry.get("readiness_ratio"),
                components=components,
            )
        )
    return datasets


def logistic(beta: float, r_value: float, theta: float) -> float:
    return 1.0 / (1.0 + math.exp(-beta * (r_value - theta)))


def dataset_summary(datasets: Sequence[DatasetStatus]) -> dict:
    total = len(datasets)
    readiness_values = [ds.actual_readiness_ratio() for ds in datasets]
    ready_count = sum(1 for value in readiness_values if math.isclose(value, 1.0))
    any_ready = ready_count
    missing_components = sum(len(ds.missing_components()) for ds in datasets)
    avg_readiness = sum(readiness_values) / total if total else 0.0
    return {
        "total": total,
        "fully_ready": ready_count,
        "any_components_missing": missing_components,
        "average_readiness": avg_readiness,
        "values": readiness_values,
    }


def build_action_items(
    datasets: Sequence[DatasetStatus],
    targets: Sequence[TargetStatus],
    docs: Sequence[TargetStatus],
    simulator_targets: Sequence[TargetStatus],
    sigillin_targets: Sequence[TargetStatus],
) -> List[dict]:
    actions: List[dict] = []
    counter = 1

    def next_id(prefix: str) -> str:
        nonlocal counter
        action_id = f"{prefix}-{counter:02d}"
        counter += 1
        return action_id

    for ds in datasets:
        missing = ds.missing_components()
        if not missing:
            continue
        actions.append(
            {
                "id": next_id("dataset"),
                "priority": "P1",
                "title": f"Complete {ds.domain} dataset {ds.identifier}",
                "description": (
                    "Ingest missing components and run logistic fits so that σ(β(R-Θ)) reaches activation."  # noqa: E501
                ),
                "targets": [c.to_dict() for c in missing],
                "related_resonance_status": ds.resonance_status,
            }
        )

    for scope, prefix in ((targets, "analysis"), (docs, "docs"), (simulator_targets, "sim"), (sigillin_targets, "sigillin")):
        for target in scope:
            exists = target.path.exists()
            missing_outputs = [out for out in target.expected_outputs if not out.exists()]
            if exists and not missing_outputs:
                continue
            actions.append(
                {
                    "id": next_id(prefix),
                    "priority": "P2" if prefix != "sigillin" else "P3",
                    "title": f"Activate {target.description}",
                    "description": (
                        "Ensure artefact and its outputs exist so the readiness bridge remains tri-layered."
                    ),
                    "targets": [
                        {
                            "path": rel(target.path),
                            "exists": exists,
                            "category": target.category,
                        }
                    ]
                    + [
                        {
                            "path": rel(out),
                            "exists": out.exists(),
                            "category": "output",
                        }
                        for out in target.expected_outputs
                    ],
                }
            )
    return actions


def build_targets() -> tuple[list[TargetStatus], list[TargetStatus], list[TargetStatus], list[TargetStatus]]:
    analysis_targets = [
        TargetStatus(
            path=REPO_ROOT / "analysis" / "climate_beta_extractor.py",
            description="climate beta extractor pipeline",
            expected_outputs=[REPO_ROOT / "analysis" / "results" / "urban_heat_global_fit.json"],
            category="analysis",
        ),
        TargetStatus(
            path=REPO_ROOT / "analysis" / "neuro_threshold_fitter.py",
            description="neuro-AI hybrid threshold fitter",
            expected_outputs=[REPO_ROOT / "analysis" / "results" / "neuro_ai_beta.json"],
            category="analysis",
        ),
        TargetStatus(
            path=REPO_ROOT / "analysis" / "outlier_validator.py",
            description="β>10 instrumentation guard",
            expected_outputs=[REPO_ROOT / "analysis" / "results" / "outlier_validator_report.json"],
            category="analysis",
        ),
        TargetStatus(
            path=REPO_ROOT / "analysis" / "beta_meta_regression_v2.py",
            description="meta regression v2 refresh",
            expected_outputs=[REPO_ROOT / "analysis" / "results" / "beta_meta_regression_v2_latest.json"],
            category="analysis",
        ),
    ]

    doc_targets = [
        TargetStatus(
            path=REPO_ROOT / "docs" / "UTAC_v2.0_Coherence_Formula.md",
            description="UTAC v2.0 coherence formula narrative",
            expected_outputs=[],
            category="documentation",
        ),
        TargetStatus(
            path=REPO_ROOT / "docs" / "resonance-bridge-map.md",
            description="resonance bridge map",
            expected_outputs=[],
            category="documentation",
        ),
    ]

    simulator_targets = [
        TargetStatus(
            path=REPO_ROOT / "simulator" / "presets" / "coherence_formula.json",
            description="coherence formula simulator preset",
            expected_outputs=[],
            category="simulator",
        ),
    ]

    sigillin_targets = [
        TargetStatus(
            path=REPO_ROOT
            / "seed"
            / "bedeutungssigillin"
            / "metaquest"
            / "system"
            / "metaquest_system_map.json",
            description="metaquest system map",
            expected_outputs=[],
            category="sigillin",
        ),
        TargetStatus(
            path=REPO_ROOT
            / "seed"
            / "shadow_sigillin"
            / "metaquest"
            / "system"
            / "metaquest_system_shadow.json",
            description="metaquest system shadow map",
            expected_outputs=[],
            category="sigillin",
        ),
    ]

    return analysis_targets, doc_targets, simulator_targets, sigillin_targets


def summarise_targets(targets: Sequence[TargetStatus]) -> List[dict]:
    return [target.to_dict() for target in targets]


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_yaml(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, allow_unicode=True)


def write_markdown(path: Path, payload: dict, datasets: Sequence[DatasetStatus], actions: Sequence[dict]) -> None:
    logistic_info = payload["meta"]["logistic"]
    dataset_summary_info = payload["data_summary"]

    lines: List[str] = []
    lines.append("# UTAC v2.0 Readiness Audit – σ(β(R-Θ)) Compass")
    lines.append("")
    lines.append(
        "*Generated {generated} via `analysis/v2_readiness_audit.py` – logistic quartet guiding V2 activation.*".format(
            generated=payload["meta"]["generated_at"]
        )
    )
    lines.append("")
    lines.append("## 1. Formal Stratum — Logistic Summary")
    lines.append("")
    lines.append("- Manifest lanterns: **{total}** (fully ready: {ready}).".format(
        total=dataset_summary_info["total"], ready=dataset_summary_info["fully_ready"]
    ))
    lines.append(
        "- Average readiness R̄ = {avg:.2f}; Θ = {theta:.2f}; β = {beta:.2f}; σ(β(R-Θ)) = {sigma:.3f}.".format(
            avg=logistic_info["mean_readiness"],
            theta=logistic_info["theta"],
            beta=logistic_info["beta"],
            sigma=logistic_info["sigma"],
        )
    )
    lines.append(
        "- ζ(R) guard: {missing} components still dark across manifest entries.".format(
            missing=dataset_summary_info["any_components_missing"]
        )
    )
    lines.append("")
    lines.append("## 2. Empirical Stratum — Dataset Ledger")
    lines.append("")
    lines.append("| Dataset | Domain | Resonance | Ready | Missing | Next Step |")
    lines.append("|:-------|:-------|:----------|:------|:--------|:-----------|")
    for ds in datasets:
        missing_names = ", ".join(c.name for c in ds.missing_components()) or "—"
        readiness_pct = int(round(ds.actual_readiness_ratio() * 100))
        next_step = "Complete manifest tri-layer" if missing_names != "—" else "Run updated analysis"
        lines.append(
            "| {id} | {domain} | {status} | {ready}% | {missing} | {next_step} |".format(
                id=ds.identifier,
                domain=ds.domain,
                status=ds.resonance_status,
                ready=readiness_pct,
                missing=missing_names,
                next_step=next_step,
            )
        )
    lines.append("")
    lines.append("## 3. Implementation Map — Priority Actions")
    lines.append("")
    for action in actions:
        lines.append(f"- **{action['id']} ({action['priority']})** — {action['title']}")
        lines.append(f"  - {action['description']}")
        if action.get("targets"):
            for target in action["targets"]:
                exists_flag = target.get("exists")
                if exists_flag is None:
                    exists_flag = target.get("actual_exists")
                lines.append(
                    "  - target: `{path}` (exists: {exists})".format(
                        path=target["path"], exists=exists_flag
                    )
                )
    lines.append("")
    lines.append("## 4. Beacon Status — Analysis · Docs · Simulator · Sigillin")
    lines.append("")
    for section_name, items in (
        ("Analysis", payload["analysis_targets"]),
        ("Documentation", payload["doc_targets"]),
        ("Simulator", payload["simulator_targets"]),
        ("Sigillin", payload["sigillin_targets"]),
    ):
        lines.append(f"### {section_name}")
        for item in items:
            outputs = item.get("expected_outputs", [])
            if outputs:
                output_info = ", ".join(
                    f"{out['path']} (exists: {out['exists']})" for out in outputs
                )
            else:
                output_info = "—"
            lines.append(
                "- `{path}` — exists: {exists}; outputs: {outputs}".format(
                    path=item["path"],
                    exists=item["exists"],
                    outputs=output_info,
                )
            )
        lines.append("")
    lines.append("## 5. Poetic Stratum — Membrane Whisper")
    lines.append("")
    lines.append(
        "R tastet fünf Laternen, doch zwei Drittel der Komponenten schlafen noch. Θ ruft nach Datenströmen, β spannt die Steilflanke,"  # noqa: E501
    )
    lines.append(
        "damit die Metaquest-Brücke wieder antwortet. Sobald Urban Heat, Amazon Hydro, AMOC, Neuro-AI und Systemic Risk als Daten"
        "-Resonanz erscheinen, beruhigt ζ(R) und V2.0 steigt auf das Plateau."
    )
    lines.append("")

    with path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def build_payload(
    manifest_path: Path,
    datasets: Sequence[DatasetStatus],
    analysis_targets: Sequence[TargetStatus],
    doc_targets: Sequence[TargetStatus],
    simulator_targets: Sequence[TargetStatus],
    sigillin_targets: Sequence[TargetStatus],
    theta: float,
    beta: float,
) -> dict:
    dataset_info = dataset_summary(datasets)
    sigma_value = logistic(beta=beta, r_value=dataset_info["average_readiness"], theta=theta)

    return {
        "meta": {
            "generated_at": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
            "manifest_path": rel(manifest_path),
            "logistic": {
                "theta": theta,
                "beta": beta,
                "mean_readiness": dataset_info["average_readiness"],
                "sigma": sigma_value,
            },
        },
        "data_summary": dataset_info,
        "datasets": [ds.to_dict() for ds in datasets],
        "analysis_targets": summarise_targets(analysis_targets),
        "doc_targets": summarise_targets(doc_targets),
        "simulator_targets": summarise_targets(simulator_targets),
        "sigillin_targets": summarise_targets(sigillin_targets),
        "action_items": build_action_items(datasets, analysis_targets, doc_targets, simulator_targets, sigillin_targets),
    }


def ensure_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate UTAC v2 readiness tri-layer report.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to utac data manifest (YAML).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_STEM,
        help="Output path stem (without extension).",
    )
    parser.add_argument(
        "--theta",
        type=float,
        default=0.66,
        help="Target readiness threshold Θ.",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=4.8,
        help="Steepness parameter β for logistic activation.",
    )
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    if manifest is None:
        raise SystemExit(f"Manifest not found: {args.manifest}")

    datasets = parse_dataset_status(manifest)
    analysis_targets, doc_targets, simulator_targets, sigillin_targets = build_targets()

    payload = build_payload(
        manifest_path=args.manifest,
        datasets=datasets,
        analysis_targets=analysis_targets,
        doc_targets=doc_targets,
        simulator_targets=simulator_targets,
        sigillin_targets=sigillin_targets,
        theta=args.theta,
        beta=args.beta,
    )

    output_stem = args.output
    json_path = output_stem.with_suffix(".json")
    yaml_path = output_stem.with_suffix(".yaml")
    md_path = output_stem.with_suffix(".md")

    ensure_directory(json_path)
    ensure_directory(yaml_path)
    ensure_directory(md_path)

    write_json(json_path, payload)
    write_yaml(yaml_path, payload)
    write_markdown(md_path, payload, datasets, payload["action_items"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
