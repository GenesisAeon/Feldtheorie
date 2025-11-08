#!/usr/bin/env python3
"""Refresh the Zenodo metadata JSON with the current logistic release parameters."""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update .zenodo.json for a new release")
    parser.add_argument("--version", required=True, help="Semantic version string to embed")
    parser.add_argument(
        "--output",
        required=True,
        help="Destination path for the updated metadata JSON",
    )
    parser.add_argument(
        "--source",
        default=".zenodo.json",
        help="Input metadata template (defaults to .zenodo.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = pathlib.Path(args.source)
    payload = json.loads(source.read_text(encoding="utf-8"))

    today = datetime.date.today().isoformat()
    payload["version"] = args.version
    payload["publication_date"] = today

    title = payload.get("title")
    if isinstance(title, str):
        payload["title"] = re.sub(r"v[0-9.]+", f"v{args.version}", title)

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
