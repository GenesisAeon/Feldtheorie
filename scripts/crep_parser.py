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

# ============================================================================
# Codex Integration (v2-pr-0019)
# ============================================================================

def sigil_to_codex_entry(sigil, timestamp):
    """Convert a ParsedSigil to a codexfeedback entry format."""
    core = sigil.core
    logistic_frame = sigil.logistic_frame
    tri_layer = sigil.data["sigil"]["tri_layer"]
    
    # Generate codex ID from sigil ID (maintain traceability)
    codex_id = f"sigil-{core['id']}"
    
    return {
        "id": codex_id,
        "title": core["title"],
        "scope": [str(sigil.path.relative_to(Path.cwd()))],
        "parameters": {
            "R": logistic_frame.get("R", "Sigillin activation level"),
            "Theta": logistic_frame.get("Theta", 0.66),
            "beta": logistic_frame["beta"],
        },
        "resonance": f"Sigillin {core['type']} artifact with CREP: {sigil.crep}",
        "status": core["status"],
        "notes": {
            "formal": tri_layer.get("formal", ""),
            "empirical": tri_layer.get("empirical", ""),
            "poetic": tri_layer.get("poetic", ""),
        },
        "timestamp": timestamp,
        "source": "crep_parser --write-codex",
    }


def load_codex_trilayer(codex_dir):
    """Load existing codexfeedback YAML and JSON."""
    yaml_path = codex_dir / "codexfeedback.yaml"
    json_path = codex_dir / "codexfeedback.json"
    
    if not yaml_path.exists():
        raise SigilValidationError(f"Codex YAML not found: {yaml_path}")
    if not json_path.exists():
        raise SigilValidationError(f"Codex JSON not found: {json_path}")
    
    with yaml_path.open("r", encoding="utf-8") as f:
        codex_yaml = yaml.safe_load(f)
    
    with json_path.open("r", encoding="utf-8") as f:
        codex_json = json.load(f)
    
    return codex_yaml, codex_json


def write_codex_trilayer(codex_dir, codex_yaml, codex_json):
    """Write updated codexfeedback to YAML, JSON, and MD (Trilayer!)."""
    import sys
    yaml_path = codex_dir / "codexfeedback.yaml"
    json_path = codex_dir / "codexfeedback.json"
    md_path = codex_dir / "codexfeedback.md"
    
    # Write YAML
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.dump(codex_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Write JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(codex_json, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    # Generate MD from entries
    md_content = generate_codex_markdown(codex_yaml)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(md_content)


def generate_codex_markdown(codex_yaml):
    """Generate Markdown representation of codexfeedback."""
    lines = ["# Codex Feedback Matrix\n\n"]
    lines.append(f"**Project:** {codex_yaml['meta']['project']}\n\n")
    lines.append(f"**Version:** {codex_yaml['meta']['current_release']['version']}\n\n")
    lines.append(f"**Status:** {codex_yaml['meta']['current_release']['status']}\n\n")
    lines.append(f"**Updated:** {codex_yaml['meta']['updated']}\n\n")
    lines.append("---\n\n")
    lines.append("## Entries\n\n")
    
    for entry in codex_yaml["entries"]:
        lines.append(f"### {entry['id']}: {entry['title']}\n\n")
        lines.append(f"**Status:** {entry.get('status', 'active')}\n\n")
        lines.append(f"**Scope:** {', '.join(entry.get('scope', []))}\n\n")
        
        params = entry.get("parameters", {})
        lines.append(f"**Parameters:** β={params.get('beta', 'N/A')}, Θ={params.get('Theta', 'N/A')}\n\n")
        lines.append(f"**Resonance:** {entry.get('resonance', '')}\n\n")
        
        if "notes" in entry:
            notes = entry["notes"]
            lines.append("**Formal Thread:**\n\n")
            lines.append(f"{notes.get('formal', '')}\n\n")
            lines.append("**Empirical Thread:**\n\n")
            lines.append(f"{notes.get('empirical', '')}\n\n")
            lines.append("**Poetic Thread:**\n\n")
            lines.append(f"{notes.get('poetic', '')}\n\n")
        
        lines.append("---\n\n")
    
    return "".join(lines)


def append_to_codex(sigils, codex_dir, timestamp):
    """Append parsed sigils to codexfeedback.* (Trilayer!)"""
    import sys
    try:
        codex_yaml, codex_json = load_codex_trilayer(codex_dir)
    except SigilValidationError as exc:
        print(f"Error loading codex: {exc}", file=sys.stderr)
        return 1
    
    # Convert sigils to codex entries
    new_entries = [sigil_to_codex_entry(sigil, timestamp) for sigil in sigils]
    
    # Check for ID collisions
    existing_ids = {entry["id"] for entry in codex_yaml["entries"]}
    collisions = [entry["id"] for entry in new_entries if entry["id"] in existing_ids]
    if collisions:
        print(f"Warning: Skipping {len(collisions)} entries with existing IDs: {collisions}", file=sys.stderr)
        new_entries = [e for e in new_entries if e["id"] not in existing_ids]
    
    if not new_entries:
        print("No new entries to add to codex.", file=sys.stderr)
        return 0
    
    # Append to YAML and JSON
    codex_yaml["entries"].extend(new_entries)
    codex_json["entries"].extend(new_entries)
    
    # Update metadata
    codex_yaml["meta"]["updated"] = timestamp
    codex_json["meta"]["updated"] = timestamp
    
    # Write Trilayer
    try:
        write_codex_trilayer(codex_dir, codex_yaml, codex_json)
        print(f"✅ Added {len(new_entries)} entries to codex (Trilayer: YAML, JSON, MD)")
        for entry in new_entries:
            print(f"   - {entry['id']}: {entry['title']}")
        return 0
    except Exception as exc:
        print(f"Error writing codex: {exc}", file=sys.stderr)
        return 1



def create_argument_parser():
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
    parser.add_argument(
        "--write-codex",
        action="store_true",
        help="Automatically write parsed Sigillins as entries to seed/codexfeedback.*",
    )
    parser.add_argument(
        "--codex-dir",
        default="seed",
        help="Directory containing codexfeedback.* files (default: seed/)",
    )
    return parser


def main(argv=None):
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
        return 2

    # Write to codex if requested
    if args.write_codex:
        codex_dir = Path(args.codex_dir).resolve()
        timestamp = args_timestamp()
        return_code = append_to_codex(sigils, codex_dir, timestamp)
        if return_code != 0:
            return return_code

    # Standard output
    output = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
