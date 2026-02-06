"""Tests for Aeon architecture completion modules (M1-M3 + telemetry)."""

from __future__ import annotations

import numpy as np

from aeon.modules.genesis_orchestrator import GenesisOrchestrator
from aeon.modules.knowledge_system import KnowledgeSystem
from aeon.nullkern.zero_point_kernel import Nullkern
from aeon.shell.grammar import AeonShellParser, AeonShellGenerator


def test_aeonshell_parser_and_generator_roundtrip() -> None:
    parser = AeonShellParser()
    generator = AeonShellGenerator()
    statement = "⟨ψ|OIPK|τ*⟩ ⊗ [β=4.8, Θ=0.5, ζ=-0.1] → Type-VI-Risk"

    parsed = parser.parse(statement)

    assert parsed.state_terms == ["ψ", "OIPK", "τ*"]
    assert parsed.params["β"] == 4.8
    assert parsed.params["Θ"] == 0.5
    assert parsed.params["ζ"] == -0.1
    assert parsed.consequence == "Type-VI-Risk"

    regenerated = generator.generate(parsed)
    assert parser.parse(regenerated) == parsed


def test_nullkern_formal_model_and_state_projection() -> None:
    kernel = Nullkern(beta_target=0.6, kappa=0.4)
    formal = kernel.formalize_dynamics(resource=0.7, threshold=0.5)

    assert "activation_equation" in formal
    assert formal["state_vector"]["beta"] == kernel.state.beta
    assert 0.0 <= formal["activation_probability"] <= 1.0


def test_genesis_orchestrator_delegation_and_telemetry() -> None:
    kernel = Nullkern(beta_target=0.2, kappa=0.3)
    knowledge = KnowledgeSystem()
    orchestrator = GenesisOrchestrator(kernel=kernel, knowledge_system=knowledge)

    result = orchestrator.delegate(
        "MasterGPT",
        "summarize",
        {"topic": "UTAC", "content": "σ(β(R-Θ)) guides threshold transitions."},
    )

    assert result["agent"] == "MasterGPT"
    assert result["status"] == "completed"

    telemetry = orchestrator.get_aletheia_telemetry(resource=0.75, threshold=0.5)
    assert set(["kappa_metric", "sigma_metric", "aleph_metric"]).issubset(telemetry.keys())
    assert 0.0 <= telemetry["sigma_metric"] <= 1.0


def test_knowledge_system_upsert_and_query() -> None:
    ks = KnowledgeSystem()
    ks.upsert("utac.core", "UTAC uses logistic membrane dynamics and null models.")
    ks.upsert("aeon.shell", "AeonShell expresses symbolic operators like β, Θ and ζ.")

    hits = ks.query("logistic membrane")
    assert hits
    assert hits[0]["entry_id"] == "utac.core"


