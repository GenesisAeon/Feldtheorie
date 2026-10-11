"""Display-only checks: pinned snapshots and synthetic corruption, never research runs."""
import ast
import hashlib
import json
import shutil
import threading
import urllib.error
import urllib.request

import pytest

from experiments.mandala_memory import studies


@pytest.fixture
def copy_data(tmp_path):
    target = tmp_path / "data"
    shutil.copytree(studies.DATA, target)
    return target


def repin(root, monkeypatch, mutate=None):
    """Test-only manifest update to exercise semantic validation after byte validation."""
    m = json.loads((root / "manifest.json").read_bytes())
    if mutate:
        mutate(m)
    for source in m["sources"].values():
        b = (root / source["file"]).read_bytes()
        source["sha256"] = hashlib.sha256(b).hexdigest()
        source["sha256_lf"] = hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()
    b = json.dumps(m).encode()
    (root / "manifest.json").write_bytes(b)
    monkeypatch.setattr(studies, "MANIFEST_SHA256", hashlib.sha256(b).hexdigest())


@pytest.mark.parametrize("sid", studies.IDS)
def test_all_values_are_original_with_provenance(sid):
    before = {p: p.read_bytes() for p in studies.DATA.rglob("*") if p.is_file()}
    data = studies.load_study(sid)
    assert data["integrity"] == "verified" and data["panels"]
    sources = {s["id"]: json.loads(studies.source_bytes(sid, s["id"])) for s in data["sources"]
               if s["id"].endswith(("result", "evaluation", "prediction"))}
    for panel in data["panels"]:
        assert panel["evidence"] and data["scope"]
        fields = [f for r in panel["rows"] for f in r["cells"]] + [m["field"] for m in panel["metrics"]]
        for field in fields:
            original = sources[field["source"]]
            for part in field["pointer"].strip("/").split("/"):
                part = part.replace("~1", "/").replace("~0", "~")
                original = original[int(part)] if isinstance(original, list) else original[part]
            assert field["value"] == original
    assert all(p.read_bytes() == b for p, b in before.items())


@pytest.mark.parametrize("mutation", ["byte", "missing", "erratum", "manifest", "eol"])
def test_corruption_blocks_whole_study(copy_data, mutation):
    p = copy_data / "sources/m9-result.json"
    if mutation == "byte":
        p.write_bytes(p.read_bytes() + b" ")
    elif mutation == "missing":
        p.unlink()
    elif mutation == "erratum":
        (copy_data / "sources/m9-erratum.md").unlink()
    elif mutation == "manifest":
        p = copy_data / "manifest.json"
        p.write_bytes(p.read_bytes() + b" ")
    else:
        p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    with pytest.raises(studies.IntegrityError):
        studies.load_study("m9", copy_data)
    if mutation != "manifest":
        assert studies.load_study("m12", copy_data)["integrity"] == "verified"


@pytest.mark.parametrize("mutation", ["run", "release", "field", "nan", "infinity", "duplicate"])
def test_semantics_fail_closed_even_with_reviewed_new_hash(copy_data, monkeypatch, mutation):
    p = copy_data / "sources/m10-evaluation.json"
    d = json.loads(p.read_bytes())
    if mutation == "run": d["run_id"] = "smoke-or-aborted"
    if mutation == "release": d["release"]["released"] = False
    if mutation == "field": del d["confirmatory"]["contrasts"]["H-N"]["delta_hat"]
    if mutation == "nan": d["confirmatory"]["contrasts"]["H-N"]["delta_hat"] = float("nan")
    text = json.dumps(d)
    if mutation == "infinity": text = text[:-1] + ', "overflow":1e999}'
    if mutation == "duplicate": text = text[:-1] + ', "mode":"dev"}'
    p.write_text(text, encoding="utf-8")
    repin(copy_data, monkeypatch)
    with pytest.raises(studies.IntegrityError): studies.load_study("m10", copy_data)


def test_missing_pointer_prevents_numbers(copy_data, monkeypatch):
    repin(copy_data, monkeypatch, lambda m: m["studies"]["m12"]["panels"][0]["rows"][0]["cells"][0].update(pointer="/not_there"))
    with pytest.raises(studies.IntegrityError): studies.load_study("m12", copy_data)


@pytest.mark.parametrize("mutation", ["above_one", "reversed", "decision_int", "null", "assertion_int"])
def test_value_semantics_fail_closed(copy_data, monkeypatch, mutation):
    """Byte-valid (re-pinned) but semantically invalid values must not be displayed."""
    p = copy_data / "sources/m12-evaluation.json"
    d = json.loads(p.read_bytes())
    t = d["confirmatory"]["tests"]["R-a"]
    if mutation == "above_one": d["descriptive"]["conditions"]["c0"]["B"] = 1.5
    if mutation == "reversed": t["ci95_t"] = t["ci95_t"][::-1]
    if mutation == "decision_int": t["rejected"] = 1
    if mutation == "null": t["mean"] = None                  # field is not nullable
    if mutation == "assertion_int": d["release"]["released"] = 1  # 1 == True, but not a bool
    p.write_text(json.dumps(d), encoding="utf-8")
    repin(copy_data, monkeypatch)
    with pytest.raises(studies.IntegrityError): studies.load_study("m12", copy_data)


def test_sources_outside_snapshot_are_rejected(copy_data, monkeypatch):
    outside = copy_data.parent / "outside.md"
    outside.write_bytes((copy_data / "sources/m9-erratum.md").read_bytes())
    repin(copy_data, monkeypatch, lambda m: m["sources"]["m9-erratum"].update(file="../outside.md"))
    with pytest.raises(studies.IntegrityError): studies.load_study("m9", copy_data)
    with pytest.raises(studies.IntegrityError): studies.source_bytes("m9", "m9-erratum", copy_data)


def test_lf_binding_accepts_crlf_pinned_target(copy_data, monkeypatch):
    """sha256_lf bindings compare line-ending-normalised bytes; the raw pin still guards the copy."""
    p = copy_data / "sources/m9-prediction.json"
    p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    repin(copy_data, monkeypatch)
    assert studies.load_study("m9", copy_data)["integrity"] == "verified"


def test_catalog_has_no_numbers():
    assert [set(entry) for entry in studies.catalog()] == [{"id", "title"}] * len(studies.IDS)
    assert [entry["id"] for entry in studies.catalog()] == list(studies.IDS)


def test_loader_has_no_research_imports():
    tree = ast.parse(__import__("pathlib").Path(studies.__file__).read_text(encoding="utf-8"))
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert set(imports) <= {"__future__", "hashlib", "json", "math", "pathlib"}


@pytest.mark.parametrize("sid,source", [("../m9", "m9-result"), ("m9", "../manifest.json"), ("m9", "m12-result")])
def test_source_allowlist(sid, source):
    with pytest.raises(KeyError): studies.source_bytes(sid, source)


def test_http_studies_never_compute_or_log(tmp_path, monkeypatch):
    from experiments.mandala_memory import serve
    def forbidden(*a, **kw): raise AssertionError("Study request attempted research or exploration")
    for name in ("explore", "lab", "_log", "build_trace", "networks", "benchmark_lab_curve"):
        monkeypatch.setattr(serve, name, forbidden)
    monkeypatch.setattr(serve, "EXPLORE_DIR", tmp_path / "explore")
    server = serve.make_server(0, tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert server.server_address[0] == "127.0.0.1"
        for route in ("/api/studies", "/api/studies/m12", "/api/studies/m9/sources/m9-erratum"):
            with urllib.request.urlopen(base + route) as response:
                assert response.status == 200 and response.headers["Cache-Control"] == "no-store"
                assert response.read()
        for path in ("/api/studies/unknown", "/api/studies/m9/sources/m12-result", "/api/studies/m9/sources/../../secret"):
            with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(base + path)
            assert e.value.code == 404
        monkeypatch.setattr(studies, "load_study", lambda *a: (_ for _ in ()).throw(studies.IntegrityError("private path")))
        with pytest.raises(urllib.error.HTTPError) as e: urllib.request.urlopen(base + "/api/studies/m12")
        assert e.value.code == 409
        payload = json.loads(e.value.read())
        assert payload["integrity"] == "failed" and "panels" not in payload and "private" not in str(payload)
        assert not (tmp_path / "explore").exists()
    finally:
        server.shutdown(); server.server_close(); thread.join()
