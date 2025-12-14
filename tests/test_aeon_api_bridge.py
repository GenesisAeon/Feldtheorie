"""Tests for the Aeon FastAPI bridge."""

import importlib

import pytest


def test_aeon_bridge_requires_fastapi(monkeypatch):
    """AeonBridge should refuse to initialize when FastAPI is unavailable."""

    api_bridge = importlib.import_module("aeon.api_bridge")

    # Force the FastAPI availability flag off to simulate missing dependency
    monkeypatch.setattr(api_bridge, "FASTAPI_AVAILABLE", False)

    with pytest.raises(ImportError, match="FastAPI not available"):
        api_bridge.AeonBridge(shell=object())
