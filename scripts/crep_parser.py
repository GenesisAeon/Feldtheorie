"""Sigillin CREP parser and validator.

This tool ingests Sigillin YAML artefacts, validates their logistic framing,
and exports CREP summaries so downstream automation can tune ζ(R) controllers.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Tuple

import yaml


SIGIL_TYPES = {"order", "dynamics", "meaning", "shadow"}
SIGIL_STATUSES = {"draft", "primed", "active", "resonant", "archived"}
CREP_KEYS = ("coherence", "resilience", "empathy", "propagation")
REQUIRED_SECTIONS = {
    "core": ("id", "type", "title", "version", "status"),
    "logistic_frame": ("R", "Theta", "beta", "zeta"),
    "crep": CREP_KEYS,
    "tri_layer": ("formal", "empirical", "poetic"),
}


class SigilValidationError(Exception):
    """Raised when a sigil violates the schema constraints."""


@dataclass
class ParsedSigil:
    path: Path
    data: Dict

    @property
    def core(self) -> Dict:
        return self.data["sigil"]["core"]

    @property
    def logistic_frame(self) -> Dict:
        return self.data["sigil"]["logistic_frame"]

    @property
    def crep(self) -> Dict[str, float]:
        return self.data["sigil"]["crep"]

    def summary(self) -> Dict:
        anchors = self.data["sigil"].get("anchors", [])
        return {
            "id": self.core["id"],
            "type": self.core["type"],
            "title": self.core["title"],
            "status": self.core["status"],
            "beta": self.logistic_frame["beta"],
            "zeta": self.logistic_frame["zeta"],
            "anchors": [a.get("path") for a in anchors],
            "crep": {key: float(self.crep[key]) for key in CREP_KEYS},
            "path": str(self.path.as_posix()),
        }


def load_yaml(path: Path) -> Dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as exc:  # pragma: no cover - defensive guard
        raise SigilValidationError(f"Failed to parse YAML in {path}: {exc}") from exc


def validate_structure(data: Dict, path: Path) -> None:
    if not isinstance(data, dict):
        raise SigilValidationError(f"Sigil at {path} must be a mapping.")
    for key in ("meta", "sigil"):
        if key not in data:
            raise SigilValidationError(f"Sigil at {path} missing top-level key: {key}")

    sigil = data["sigil"]
    if not isinstance(sigil, dict):
        raise SigilValidationError(f"sigil block at {path} must be a mapping.")

    for section, required_keys in REQUIRED_SECTIONS.items():
        if section not in sigil:
            raise SigilValidationError(f"Sigil at {path} missing section: {section}")
        block = sigil[section]
        if not isinstance(block, dict):
            raise SigilValidationError(f"Section {section} at {path} must be a mapping.")
        for key in required_keys:
            if key not in block:
                raise SigilValidationError(
                    f"Section {section} at {path} missing required key: {key}"
                )

    anchors = sigil.get("anchors", [])
    if not isinstance(anchors, list):
        raise SigilValidationError(f"anchors section at {path} must be a list if present.")
    for anchor in anchors:
        if not isinstance(anchor, dict):
            raise SigilValidationError(f"Anchor in {path} must be a mapping.")
        if "path" not in anchor or "kind" not in anchor:
            raise SigilValidationError(
                f"Anchor in {path} must define both 'path' and 'kind'."
            )


def validate_semantics(parsed: ParsedSigil) -> None:
    core = parsed.core
    logistic_frame = parsed.logistic_frame
    crep = parsed.crep

    if core["type"] not in SIGIL_TYPES:
        raise SigilValidationError(
            f"Sigil {core['id']} has invalid type '{core['type']}'."
        )
    if core["status"] not in SIGIL_STATUSES:
        raise SigilValidationError(
            f"Sigil {core['id']} has invalid status '{core['status']}'."
        )

    try:
        beta_value = float(logistic_frame["beta"])
    except (TypeError, ValueError) as exc:
        raise SigilValidationError(
            f"Sigil {core['id']} provides non-numeric β: {logistic_frame['beta']}"
        ) from exc
    if beta_value < 0.5:
        raise SigilValidationError(
            f"Sigil {core['id']} reports β={beta_value}, below minimum 0.5."
        )
    parsed.data["sigil"]["logistic_frame"]["beta"] = beta_value

    for key in CREP_KEYS:
        value = crep[key]
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise SigilValidationError(
                f"Sigil {core['id']} has non-numeric CREP value for {key}: {value}"
            ) from exc
        if not 0.0 <= numeric <= 1.0:
            raise SigilValidationError(
                f"Sigil {core['id']} has CREP value outside [0, 1] for {key}: {numeric}"
            )
        parsed.data["sigil"]["crep"][key] = numeric


def parse_sigils(paths: Iterable[Path], validate: bool = False) -> List[ParsedSigil]:
    parsed_sigils: List[ParsedSigil] = []
    for path in paths:
        data = load_yaml(path)
        if validate:
            validate_structure(data, path)
        parsed = ParsedSigil(path=path, data=data)
        if validate:
            validate_semantics(parsed)
        parsed_sigils.append(parsed)
    return parsed_sigils


def aggregate_crep(sigils: Iterable[ParsedSigil]) -> Dict[str, float]:
    values: Dict[str, List[float]] = {key: [] for key in CREP_KEYS}
    for sigil in sigils:
        for key in CREP_KEYS:
            try:
                values[key].append(float(sigil.crep[key]))
            except (TypeError, ValueError):
                continue
    return {key: mean(vals) if vals else 0.0 for key, vals in values.items()}


def collect_paths(args: argparse.Namespace) -> Tuple[List[Path], Path | None]:
    root: Path | None = None
    paths: List[Path] = []

    if args.examples:
        root = Path("seed/sigillin/examples").resolve()
        paths.extend(sorted(root.glob("*.yaml")))

    if args.directory:
        directory = Path(args.directory).resolve()
        root = root or directory
        paths.extend(sorted(directory.glob("*.yaml")))

    for file_path in args.files:
        path = Path(file_path).resolve()
        root = root or path.parent
        paths.append(path)

    unique_paths = []
    seen = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        if path.name == "sigillin_schema.yaml":
            continue
        if path.is_file():
            unique_paths.append(path)

    if not unique_paths:
        raise SigilValidationError("No sigil files supplied.")

    return unique_paths, root


def build_summary(sigils: List[ParsedSigil], validate: bool) -> Dict:
    return {
        "generated_at": args_timestamp(),
        "validated": validate,
        "count": len(sigils),
        "crep_average": aggregate_crep(sigils),
        "sigils": [sigil.summary() for sigil in sigils],
    }


def args_timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Parse Sigillin YAML files and emit CREP/logistic summaries.",
    )
    parser.add_argument(
        "files", nargs="*", help="Explicit Sigillin files to parse."
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Directory containing Sigillin YAML files (non-recursive).",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Parse the canonical examples in seed/sigillin/examples.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Enforce schema constraints and numeric bounds while parsing.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write the JSON summary. Defaults to stdout.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    try:
        paths, root = collect_paths(args)
        sigils = parse_sigils(paths, validate=args.validate)
        summary = build_summary(sigils, args.validate)
        if root is not None:
            summary["root"] = str(root)
    except SigilValidationError as exc:
        parser.error(str(exc))
        return 2  # pragma: no cover - parser.error exits, but keep explicit return

    output = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
