#!/usr/bin/env python3
"""Generate a Zenodo metadata file from preprint sources.

The script crawls Markdown and LaTeX sources, extracts title, authors,
and abstract snippets, and assembles a `.zenodo.json` suitable for
uploading the preprints bundle.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class PreprintMetadata:
    """Lightweight container for extracted preprint metadata."""

    path: Path
    title: str
    authors: List[str]
    abstract: str


MARKDOWN_EXTENSIONS = {".md", ".markdown"}
LATEX_EXTENSIONS = {".tex"}


def parse_args() -> argparse.Namespace:
    """Configure and parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Extract metadata from Markdown/LaTeX preprints and build a Zenodo JSON payload."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help=(
            "Files or directories to scan for preprints. Directories are searched recursively. "
            "If omitted, the finalized and source paper folders are used."
        ),
    )
    parser.add_argument(
        "--output",
        default="releases/V6-Plans_etc/Finalize/.zenodo.json",
        help="Destination path for the generated Zenodo metadata JSON file.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Override the Zenodo record title. If omitted, a bundle title is synthesized.",
    )
    return parser.parse_args()


def normalize_space(text: str) -> str:
    """Collapse whitespace to single spaces for compact metadata fields."""

    return re.sub(r"\s+", " ", text).strip()


def clean_author(text: str) -> str:
    """Remove Markdown emphasis and surrounding punctuation from author strings."""

    cleaned = normalize_space(text)
    cleaned = cleaned.strip("* _")
    cleaned = cleaned.strip(",;")
    return cleaned


def extract_markdown_metadata(path: Path) -> PreprintMetadata | None:
    """Extract metadata from a Markdown preprint."""

    lines = path.read_text(encoding="utf-8").splitlines()
    title = None
    authors: List[str] = []
    abstract_lines: List[str] = []

    for line in lines:
        if title is None:
            match = re.match(r"^#\s+(.*)$", line.strip())
            if match:
                title = match.group(1).strip()
                continue
        author_match = re.match(r"^\s*\*?\*?Authors\*?\*?:\s*(.+)$", line.strip(), re.IGNORECASE)
        if author_match:
            raw_authors = re.split(r"[,;]|\band\b", author_match.group(1))
            authors = [clean_author(author) for author in raw_authors if clean_author(author)]

    abstract_start = None
    for idx, line in enumerate(lines):
        if re.match(r"^#{1,6}\s*abstract\b", line.strip(), re.IGNORECASE):
            abstract_start = idx + 1
            break
    if abstract_start is not None:
        for line in lines[abstract_start:]:
            if re.match(r"^#{1,6}\s+", line):
                break
            abstract_lines.append(line)

    if title is None:
        return None

    return PreprintMetadata(
        path=path,
        title=title,
        authors=authors,
        abstract=normalize_space(" ".join(abstract_lines)) if abstract_lines else "",
    )


def extract_latex_metadata(path: Path) -> PreprintMetadata | None:
    """Extract metadata from a LaTeX preprint."""

    content = path.read_text(encoding="utf-8")
    title_match = re.search(r"\\title\{(?P<title>.+?)\}", content, re.DOTALL)
    author_match = re.search(r"\\author\{(?P<authors>.+?)\}", content, re.DOTALL)
    abstract_match = re.search(
        r"\\begin\{abstract\}(?P<abstract>.+?)\\end\{abstract\}", content, re.DOTALL
    )

    if not title_match:
        return None

    authors: List[str] = []
    if author_match:
        raw_authors = re.split(r"\\and|\\\\", author_match.group("authors"))
        authors = [clean_author(author) for author in raw_authors if clean_author(author)]

    abstract = ""
    if abstract_match:
        abstract = normalize_space(abstract_match.group("abstract"))

    return PreprintMetadata(
        path=path,
        title=normalize_space(title_match.group("title")),
        authors=authors,
        abstract=abstract,
    )


def extract_metadata(path: Path) -> PreprintMetadata | None:
    """Dispatch metadata extraction based on file extension."""

    suffix = path.suffix.lower()
    if suffix in MARKDOWN_EXTENSIONS:
        return extract_markdown_metadata(path)
    if suffix in LATEX_EXTENSIONS:
        return extract_latex_metadata(path)
    return None


def iter_source_files(paths: Iterable[str]) -> Iterable[Path]:
    """Yield Markdown/LaTeX sources from provided paths."""

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in MARKDOWN_EXTENSIONS | LATEX_EXTENSIONS:
                yield path
            continue
        for candidate in path.rglob("*"):
            if candidate.suffix.lower() in MARKDOWN_EXTENSIONS | LATEX_EXTENSIONS:
                yield candidate


def build_creators(preprints: list[PreprintMetadata]) -> list[dict[str, str]]:
    """Construct a Zenodo creators list with unique authors preserving order."""

    seen = set()
    creators: list[dict[str, str]] = []
    for preprint in preprints:
        for author in preprint.authors:
            if author not in seen:
                seen.add(author)
                creators.append({"name": author})
    if not creators:
        creators.append({"name": "Feldtheorie Contributors"})
    return creators


def build_description(preprints: list[PreprintMetadata]) -> str:
    """Compose a Markdown description summarizing the bundled preprints."""

    lines = ["Auto-generated Zenodo bundle for Feldtheorie preprints.", "", "Included works:"]
    for preprint in preprints:
        authors = ", ".join(preprint.authors) if preprint.authors else "Unknown authors"
        abstract = preprint.abstract or "No abstract detected."
        lines.append(f"- **{preprint.title}** ({authors}): {abstract}")
    lines.append("")
    lines.append(
        "Metadata extracted automatically from Markdown/LaTeX sources; edit this description in the Zenodo UI if manual curation is needed."
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    inputs = (
        args.inputs
        or ["releases/V6-Plans_etc/Finalize/papers", "releases/V6-Plans_etc/papers"]
    )

    sources = list(iter_source_files(inputs))
    preprints: list[PreprintMetadata] = []
    for source in sources:
        metadata = extract_metadata(source)
        if metadata:
            preprints.append(metadata)

    if not preprints:
        raise SystemExit("No preprint metadata could be extracted; verify the input paths.")

    record_title = args.title or f"Feldtheorie preprints bundle ({len(preprints)} works)"

    payload = {
        "upload_type": "publication",
        "publication_type": "preprint",
        "title": record_title,
        "creators": build_creators(preprints),
        "description": build_description(preprints),
        "language": "eng",
        "access_right": "open",
        "keywords": ["v_RIG", "Loihi", "κ", "Feldtheorie"],
        "notes": "Prepared via scripts/prepare_zenodo_upload.py",
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote Zenodo metadata for {len(preprints)} preprints to {output_path}")


if __name__ == "__main__":
    main()
