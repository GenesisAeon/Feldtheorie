"""Read-only display of pinned study artifacts. Standard library only; no research imports.

The manifest is a NEW display snapshot, not a retrospective preregistration.
Read -> hash -> parse the SAME bytes on every request. No cache and no writes.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent / "study_data"
MANIFEST_SHA256 = "d3417b1345e88db53960247448f7651e596707f81397b58583858b5a2468c195"
IDS = ("m9", "m10", "m11", "m12")


class IntegrityError(ValueError):
    """The display snapshot cannot be verified. Never return partial study values."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data):
    def finite_float(text):
        value = float(text)
        if not math.isfinite(value):
            raise IntegrityError("Nichtendlicher JSON-Wert")
        return value
    def invalid(value):
        raise IntegrityError("Nichtendlicher JSON-Wert")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise IntegrityError("Doppelter JSON-Schlüssel")
            result[k] = v
        return result
    return json.loads(data, parse_constant=invalid, parse_float=finite_float, object_pairs_hook=unique)


def pointer(value, path):
    if not path.startswith("/"):
        raise IntegrityError("Ungültige Feldzuordnung")
    for part in path[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def _manifest(root):
    data = (root / "manifest.json").read_bytes()
    if digest(data) != MANIFEST_SHA256:
        raise IntegrityError("Anzeigemanifest stimmt nicht mit dem geprüften Code-Stand überein")
    return _json(data)


def _verified(study_id, root):
    if study_id not in IDS:
        raise KeyError(study_id)
    manifest = _manifest(root)
    study = manifest["studies"][study_id]
    buffers, values = {}, {}
    for sid in study["dependencies"]:
        spec = manifest["sources"][sid]
        path = (root / spec["file"]).resolve()
        if not path.is_relative_to(root.resolve()):
            raise IntegrityError("Quelle außerhalb des Anzeigesnapshots")
        data = path.read_bytes()
        if digest(data) != spec["sha256"]:
            raise IntegrityError(f"Prüfsumme abweichend: {sid}")
        buffers[sid] = data
        values[sid] = _json(data) if spec["kind"] == "json" else data.decode("utf-8-sig")
    for check in study["assertions"]:
        actual = pointer(values[check["source"]], check["pointer"])
        if type(actual) is not type(check["equals"]) or actual != check["equals"]:
            raise IntegrityError("Studienlauf oder gespeicherte Freigabe unpassend")
    for bind in study["bindings"]:
        actual = pointer(values[bind["source"]], bind["pointer"])
        if "target" in bind:
            data = buffers[bind["target"]]
            expected = digest(data.replace(b"\r\n", b"\n")) if bind["hash"] == "sha256_lf" else digest(data)
        else:
            expected = pointer(values[bind["other_source"]], bind["other_pointer"])
        if actual != expected:
            raise IntegrityError("Bindung zwischen Studienartefakten abweichend")
    return manifest, study, buffers, values


def _cell(field, values):
    value = pointer(values[field["source"]], field["pointer"])
    unit = field["unit"]
    if value is None and field.get("nullable"):
        pass
    elif unit == "decision":
        if type(value) is not bool:
            raise IntegrityError("Entscheidung ist kein Wahrheitswert")
    else:
        seq = value if unit.endswith("_interval") else [value]
        if not isinstance(seq, list) or (unit.endswith("_interval") and len(seq) != 2):
            raise IntegrityError("Intervall ungültig")
        for v in seq:
            if v is None and field.get("nullable"):
                continue
            if type(v) not in (int, float) or not math.isfinite(v):
                raise IntegrityError("Kennzahl nicht endlich")
            if unit.startswith("accuracy") or unit == "p":
                if not 0 <= v <= 1:
                    raise IntegrityError("Kennzahl außerhalb [0, 1]")
        if unit.endswith("_interval") and all(v is not None for v in seq) and seq[0] > seq[1]:
            raise IntegrityError("Intervall vertauscht")
    return {**field, "value": value}


def load_study(study_id, root=DATA):
    """Return selected ORIGINAL values, with provenance; never recompute aggregates."""
    try:
        manifest, study, _, values = _verified(study_id, Path(root))
        panels = []
        for panel in study["panels"]:
            rows = [{"label": r["label"], "cells": [_cell(f, values) for f in r["cells"]]} for r in panel["rows"]]
            metrics = [{"label": m["label"], "field": _cell(m["field"], values)} for m in panel.get("metrics", [])]
            panels.append({**panel, "rows": rows, "metrics": metrics})
        sources = [{"id": sid, "sha256": manifest["sources"][sid]["sha256"],
                    "anchor": manifest["sources"][sid]["anchor"],
                    "url": f"/api/studies/{study_id}/sources/{sid}"} for sid in study["dependencies"]]
        return {"id": study_id, "title": study["title"], "scope": study["scope"], "notes": study["notes"],
                "integrity": "verified", "snapshot_note": manifest["snapshot_note"],
                "manifest_sha256": MANIFEST_SHA256, "panels": panels, "sources": sources}
    except KeyError as e:
        if study_id not in IDS:
            raise
        raise IntegrityError("Pflichtfeld fehlt im Anzeigesnapshot") from e
    except (OSError, ValueError, TypeError, IndexError) as e:
        raise IntegrityError(str(e)) from e


def source_bytes(study_id, source_id, root=DATA):
    """Only allowlisted artifacts; revalidate the ENTIRE study before opening a source."""
    try:
        _, study, buffers, _ = _verified(study_id, Path(root))
        if source_id not in study["dependencies"]:
            raise KeyError(source_id)
        return buffers[source_id]
    except (OSError, ValueError, TypeError, IndexError) as e:
        raise IntegrityError(str(e)) from e


def catalog():
    # Stable labels even when the manifest is damaged: no numeric claims here.
    return [{"id": sid, "title": title} for sid, title in zip(IDS, (
        "Wie lange hält die Spur?", "Wie stört Ablenkung?",
        "Wie gut lässt sich die Spur auslesen?", "Bleibt der Auslesevorteil?"))]
