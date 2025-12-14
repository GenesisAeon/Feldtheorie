"""Unit tests for the ECHO-I runner utilities."""

from __future__ import annotations

import sys
import types
from importlib import util
from pathlib import Path


def load_echo_one_module():
    module_path = Path(__file__).resolve().parents[1] / "analysis" / "experiments" / "run_echo_one.py"
    spec = util.spec_from_file_location("run_echo_one", module_path)
    assert spec is not None and spec.loader is not None

    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


ECHO_ONE = load_echo_one_module()


def test_tags_endpoint_supports_base_and_generate_urls():
    assert (
        ECHO_ONE.tags_endpoint("http://localhost:11434/api/generate")
        == "http://localhost:11434/api/tags"
    )
    assert (
        ECHO_ONE.tags_endpoint("http://localhost:11434/api/generate/")
        == "http://localhost:11434/api/tags"
    )
    assert (
        ECHO_ONE.tags_endpoint("http://localhost:11434/api")
        == "http://localhost:11434/api/tags"
    )


def test_list_available_models_uses_tags_endpoint(monkeypatch):
    requested_urls: list[str] = []

    def fake_get(url: str, timeout: int):
        requested_urls.append(url)

        class FakeResponse:
            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"models": [{"name": "alpha"}, {"name": "beta"}]}

        return FakeResponse()

    monkeypatch.setattr(ECHO_ONE, "requests", types.SimpleNamespace(get=fake_get))

    names = ECHO_ONE.list_available_models("http://localhost:11434/api")

    assert names == {"alpha", "beta"}
    assert requested_urls[-1].endswith("/api/tags")
