"""Integration (Feldtheorie AGENTS.md, Trilayer): every protocol artifact of the
lab has a YAML twin with identical content and a Markdown narrative."""
import json
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

from experiments.mandala_memory.tools import make_trilayer_twins as tw   # noqa: E402

PROTOCOL = Path(__file__).resolve().parents[1] / "protocol"


@pytest.mark.parametrize("stem", ["startkonfiguration", "m9_frozen_predictions", "m10_protokoll", "m11_protokoll"])
def test_yaml_twin_has_identical_content(stem):
    j = json.loads((PROTOCOL / f"{stem}.json").read_text(encoding="utf-8"))
    y = yaml.safe_load((PROTOCOL / f"{stem}.yaml").read_text(encoding="utf-8"))
    assert y == j


def test_m9_markdown_twin_names_the_frozen_hash():
    from experiments.mandala_memory.m9_evaluate import FROZEN_SHA256
    md = (PROTOCOL / "m9_frozen_predictions.md").read_text(encoding="utf-8")
    assert FROZEN_SHA256 in md and md.count("\n| h") == 24


def test_m10_markdown_twin_matches_the_current_protocol():
    import hashlib

    raw = (PROTOCOL / "m10_protokoll.json").read_bytes().replace(b"\r\n", b"\n")
    md = (PROTOCOL / "m10_protokoll.md").read_text(encoding="utf-8")
    assert hashlib.sha256(raw).hexdigest() in md, "regenerate the twins: tools/make_trilayer_twins.py"


@pytest.mark.parametrize("v", [1e-18, 3.4e-05, 1e20, -2.5e-300, 0.1, 0.0, 5e-324, 1.7976931348623157e308])
def test_float_scalars_survive_a_yaml_1_1_loader(v):
    assert yaml.safe_load(tw.yaml_scalar(v)) == v
    assert isinstance(yaml.safe_load(tw.yaml_scalar(v)), float)


def test_m11_markdown_twin_matches_the_current_protocol():
    import hashlib

    raw = (PROTOCOL / "m11_protokoll.json").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(raw).hexdigest() in (PROTOCOL / "m11_protokoll.md").read_text(encoding="utf-8")
