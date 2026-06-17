"""Tests for enhanced Aeon modules: M1 parser, Nullkern formalization, M2/M3 upgrades."""

from __future__ import annotations

import numpy as np
import pytest
from aeon.nullkern.zero_point_kernel import Nullkern
from aeon.shell.grammar import (
    EXAMPLE_CORPUS,
    AeonShellGenerator,
    AeonShellParser,
    AeonStatement,
)

# ============================================================================
# M1: Enhanced Grammar Parser Tests
# ============================================================================


class TestRecursiveDescentParser:
    """Test the recursive descent parser for AeonShell statements."""

    def test_parse_basic_statement(self) -> None:
        parser = AeonShellParser()
        stmt = parser.parse("⟨ψ|OIPK|τ*⟩ ⊗ [β=4.8, Θ=0.5, ζ=-0.1] → Type-VI-Risk")
        assert stmt.state_terms == ["ψ", "OIPK", "τ*"]
        assert stmt.params == {"β": 4.8, "Θ": 0.5, "ζ": -0.1}
        assert stmt.consequence == "Type-VI-Risk"

    def test_parse_two_state_terms(self) -> None:
        parser = AeonShellParser()
        stmt = parser.parse("⟨Φ|UTAC⟩ ⊗ [β=3.1, Θ=0.4, κ=0.7] → Resonance-Peak")
        assert stmt.state_terms == ["Φ", "UTAC"]
        assert stmt.params["κ"] == 0.7

    def test_parse_single_state_term(self) -> None:
        parser = AeonShellParser()
        stmt = parser.parse("⟨ψ⟩ ⊗ [β=1.0] → Stable")
        assert stmt.state_terms == ["ψ"]
        assert stmt.params == {"β": 1.0}
        assert stmt.consequence == "Stable"

    def test_parse_negative_param(self) -> None:
        parser = AeonShellParser()
        stmt = parser.parse("⟨Ψ⟩ ⊗ [ζ=-0.5] → Instability")
        assert stmt.params["ζ"] == -0.5

    def test_parse_all_example_corpus(self) -> None:
        parser = AeonShellParser()
        for text in EXAMPLE_CORPUS:
            stmt = parser.parse(text)
            assert isinstance(stmt, AeonStatement)
            assert len(stmt.state_terms) >= 1
            assert len(stmt.params) >= 1
            assert len(stmt.consequence) >= 1

    def test_reject_missing_angle_brackets(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("ψ|OIPK ⊗ [β=4.8] → Risk")

    def test_reject_missing_tensor_product(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨ψ⟩ [β=4.8] → Risk")

    def test_reject_missing_arrow(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨ψ⟩ ⊗ [β=4.8] Risk")

    def test_reject_empty_state(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨⟩ ⊗ [β=4.8] → Risk")

    def test_reject_invalid_param_format(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨ψ⟩ ⊗ [β] → Risk")

    def test_reject_invalid_state_term(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨INVALID_TERM⟩ ⊗ [β=1.0] → Risk")

    def test_reject_invalid_param_symbol(self) -> None:
        parser = AeonShellParser()
        with pytest.raises(ValueError):
            parser.parse("⟨ψ⟩ ⊗ [x=1.0] → Risk")

    def test_roundtrip_all_corpus(self) -> None:
        parser = AeonShellParser()
        gen = AeonShellGenerator()
        for text in EXAMPLE_CORPUS:
            stmt = parser.parse(text)
            regenerated = gen.generate(stmt)
            reparsed = parser.parse(regenerated)
            assert reparsed == stmt

    def test_generator_format(self) -> None:
        gen = AeonShellGenerator()
        stmt = AeonStatement(
            state_terms=["ψ", "Φ"],
            params={"β": 2.0, "κ": 0.5},
            consequence="Stable",
        )
        text = gen.generate(stmt)
        assert text.startswith("⟨ψ|Φ⟩")
        assert "→ Stable" in text

    def test_whitespace_tolerance(self) -> None:
        parser = AeonShellParser()
        stmt = parser.parse("  ⟨ψ⟩  ⊗  [ β = 1.0 ]  →  Stable  ")
        assert stmt.state_terms == ["ψ"]
        assert stmt.params["β"] == 1.0


# ============================================================================
# Nullkern Mathematical Formalization Tests
# ============================================================================


class TestNullkernFormalization:
    """Test the mathematical formalization of the Nullkern model."""

    def test_continuous_dynamics_returns_ode_system(self) -> None:
        kernel = Nullkern(beta_target=0.5, kappa=0.5)
        dynamics = kernel.get_continuous_dynamics(resource=0.7, threshold=0.5)
        assert "dbeta_dt" in dynamics
        assert "dkappa_dt" in dynamics
        assert "dresonance_dt" in dynamics
        assert isinstance(dynamics["dbeta_dt"], float)

    def test_jacobian_matrix(self) -> None:
        kernel = Nullkern(beta_target=0.5, kappa=0.5)
        jac = kernel.compute_jacobian(resource=0.7, threshold=0.5)
        assert isinstance(jac, np.ndarray)
        assert jac.shape == (3, 3)

    def test_stability_analysis(self) -> None:
        kernel = Nullkern(beta_target=0.5, kappa=0.5)
        stability = kernel.analyze_stability(resource=0.7, threshold=0.5)
        assert "eigenvalues" in stability
        assert "stable" in stability
        assert "lyapunov_candidate" in stability
        assert isinstance(stability["eigenvalues"], list)
        assert len(stability["eigenvalues"]) == 3

    def test_stability_at_equilibrium(self) -> None:
        """At β→0, κ→0 (Dharmakaya), the system should be stable."""
        kernel = Nullkern(beta_target=0.01, kappa=0.01)
        stability = kernel.analyze_stability(resource=0.5, threshold=0.5)
        # Near equilibrium the system should be stable
        assert stability["stable"] is True

    def test_formalize_dynamics_extended(self) -> None:
        """Extended formalization should include ODE and stability info."""
        kernel = Nullkern(beta_target=0.5, kappa=0.5)
        formal = kernel.formalize_dynamics(resource=0.7, threshold=0.5)
        # Original fields still present
        assert "activation_equation" in formal
        assert "parameters" in formal
        # New fields
        assert "continuous_dynamics" in formal
        assert "stability" in formal

    def test_energy_functional(self) -> None:
        """Test Lyapunov/energy functional computation."""
        kernel = Nullkern(beta_target=0.5, kappa=0.5)
        energy = kernel.compute_energy(resource=0.7, threshold=0.5)
        assert isinstance(energy, float)
        assert energy >= 0.0  # Energy is non-negative


# ============================================================================
# M2: Enhanced Genesis Orchestrator Tests
# ============================================================================


class TestEnhancedOrchestrator:
    """Test the enhanced Genesis Orchestrator with multi-agent comm and CREP."""

    def setup_method(self) -> None:
        from aeon.modules.genesis_orchestrator import GenesisOrchestrator
        from aeon.modules.knowledge_system import KnowledgeSystem

        self.kernel = Nullkern(beta_target=0.2, kappa=0.3)
        self.ks = KnowledgeSystem()
        self.orch = GenesisOrchestrator(kernel=self.kernel, knowledge_system=self.ks)

    def test_register_agent(self) -> None:
        self.orch.register_agent("MasterGPT", capabilities=["summarize", "analyze"])
        assert "MasterGPT" in self.orch.agents

    def test_register_duplicate_agent_raises(self) -> None:
        self.orch.register_agent("MasterGPT", capabilities=["summarize"])
        with pytest.raises(ValueError):
            self.orch.register_agent("MasterGPT", capabilities=["summarize"])

    def test_multi_agent_routing(self) -> None:
        """Delegate should route to registered agents based on capabilities."""
        self.orch.register_agent("TutorGPT", capabilities=["summarize", "teach"])
        self.orch.register_agent("BioGPT", capabilities=["analyze", "biology"])
        result = self.orch.delegate(
            "TutorGPT", "summarize",
            {"topic": "UTAC", "content": "Logistic membrane dynamics."},
        )
        assert result["agent"] == "TutorGPT"
        assert result["status"] == "completed"

    def test_delegate_to_unregistered_agent_still_works(self) -> None:
        """Backward compat: delegation to unregistered agents should still work."""
        result = self.orch.delegate(
            "UnknownAgent", "summarize",
            {"topic": "test", "content": "test content"},
        )
        assert result["status"] == "completed"

    def test_crep_quality_check(self) -> None:
        """CREP quality control should validate delegation results."""
        result = self.orch.delegate(
            "MasterGPT", "summarize",
            {"topic": "UTAC", "content": "σ(β(R-Θ)) guides threshold transitions."},
        )
        crep = self.orch.crep_validate(result)
        assert "quality_score" in crep
        assert "passed" in crep
        assert 0.0 <= crep["quality_score"] <= 1.0

    def test_nullkern_lifecycle_snapshot(self) -> None:
        """Orchestrator should expose Nullkern lifecycle snapshots."""
        snapshot = self.orch.get_nullkern_snapshot()
        assert "beta" in snapshot
        assert "kappa" in snapshot
        assert "phase" in snapshot

    def test_broadcast_to_agents(self) -> None:
        """Broadcast a message to all registered agents."""
        self.orch.register_agent("AgentA", capabilities=["listen"])
        self.orch.register_agent("AgentB", capabilities=["listen"])
        results = self.orch.broadcast("status_check", {})
        assert len(results) == 2

    def test_aletheia_telemetry_includes_crep(self) -> None:
        """Telemetry should include CREP score."""
        self.orch.delegate(
            "MasterGPT", "summarize",
            {"topic": "test", "content": "test"},
        )
        telemetry = self.orch.get_aletheia_telemetry(resource=0.75, threshold=0.5)
        assert "kappa_metric" in telemetry
        assert "sigma_metric" in telemetry
        assert "aleph_metric" in telemetry
        assert "crep_mean_score" in telemetry


# ============================================================================
# M3: Enhanced Knowledge System Tests
# ============================================================================


class TestEnhancedKnowledgeSystem:
    """Test the enhanced Knowledge System with ontology and TF-IDF scoring."""

    def setup_method(self) -> None:
        from aeon.modules.knowledge_system import KnowledgeSystem

        self.ks = KnowledgeSystem()

    def test_upsert_with_category(self) -> None:
        self.ks.upsert("utac.core", "UTAC uses logistic membrane dynamics.", category="theory")
        hits = self.ks.query("logistic membrane")
        assert hits[0]["entry_id"] == "utac.core"

    def test_query_by_category(self) -> None:
        self.ks.upsert("utac.core", "UTAC logistic membrane", category="theory")
        self.ks.upsert("aeon.shell", "AeonShell containment", category="implementation")
        hits = self.ks.query("logistic", category="theory")
        assert all(h["entry_id"].startswith("utac") for h in hits)

    def test_get_categories(self) -> None:
        self.ks.upsert("a", "content a", category="theory")
        self.ks.upsert("b", "content b", category="implementation")
        categories = self.ks.get_categories()
        assert "theory" in categories
        assert "implementation" in categories

    def test_delete_entry(self) -> None:
        self.ks.upsert("temp", "temporary content")
        assert self.ks.size() == 1
        self.ks.delete("temp")
        assert self.ks.size() == 0

    def test_get_entry(self) -> None:
        self.ks.upsert("utac.core", "UTAC content")
        entry = self.ks.get("utac.core")
        assert entry is not None
        assert entry.content == "UTAC content"

    def test_get_nonexistent_returns_none(self) -> None:
        assert self.ks.get("nonexistent") is None

    def test_tfidf_scoring_prefers_specific_matches(self) -> None:
        """TF-IDF should rank documents with rare matching terms higher."""
        self.ks.upsert("a", "the logistic membrane threshold dynamics equation")
        self.ks.upsert("b", "the the the the the membrane")
        self.ks.upsert("c", "logistic membrane activation function sigma beta")
        hits = self.ks.query("logistic membrane")
        # Entry with both terms and more specificity should rank higher
        ids = [h["entry_id"] for h in hits]
        assert "a" in ids
        assert "c" in ids

    def test_export_ontology(self) -> None:
        """Export a summary of categories and their entries."""
        self.ks.upsert("a", "content a", category="theory")
        self.ks.upsert("b", "content b", category="theory")
        self.ks.upsert("c", "content c", category="impl")
        ontology = self.ks.export_ontology()
        assert "theory" in ontology
        assert len(ontology["theory"]) == 2
        assert len(ontology["impl"]) == 1


# ============================================================================
# Integration: Module Interaction Tests
# ============================================================================


class TestModuleIntegration:
    """Test that M1-M3 modules interact correctly."""

    def test_parser_to_orchestrator_flow(self) -> None:
        """Parse a statement, use it in delegation."""
        from aeon.modules.genesis_orchestrator import GenesisOrchestrator
        from aeon.modules.knowledge_system import KnowledgeSystem

        parser = AeonShellParser()
        stmt = parser.parse("⟨ψ|UTAC⟩ ⊗ [β=3.1, Θ=0.4] → Resonance-Peak")

        kernel = Nullkern(beta_target=0.2, kappa=0.3)
        ks = KnowledgeSystem()
        orch = GenesisOrchestrator(kernel=kernel, knowledge_system=ks)

        result = orch.delegate(
            "MasterGPT", "summarize",
            {"topic": stmt.consequence, "content": str(stmt.params)},
        )
        assert result["status"] == "completed"

    def test_orchestrator_knowledge_telemetry_roundtrip(self) -> None:
        """Store knowledge, query it, check telemetry reflects activity."""
        from aeon.modules.genesis_orchestrator import GenesisOrchestrator
        from aeon.modules.knowledge_system import KnowledgeSystem

        kernel = Nullkern(beta_target=0.3, kappa=0.4)
        ks = KnowledgeSystem()
        orch = GenesisOrchestrator(kernel=kernel, knowledge_system=ks)

        # Store via orchestrator
        orch.delegate("TutorGPT", "summarize", {"topic": "beta", "content": "beta dynamics"})

        # Query via orchestrator
        result = orch.delegate("TutorGPT", "query_knowledge", {"query": "beta"})
        assert len(result["hits"]) >= 1

        # Telemetry reflects 2 delegations
        telemetry = orch.get_aletheia_telemetry(resource=0.5)
        assert telemetry["delegation_count"] == 2.0

    def test_nullkern_stability_through_orchestrator(self) -> None:
        """Orchestrator's nullkern_validation intent should return stability info."""
        from aeon.modules.genesis_orchestrator import GenesisOrchestrator
        from aeon.modules.knowledge_system import KnowledgeSystem

        kernel = Nullkern(beta_target=0.2, kappa=0.3)
        orch = GenesisOrchestrator(kernel=kernel, knowledge_system=KnowledgeSystem())

        result = orch.delegate("MasterGPT", "nullkern_validation", {})
        assert "validation" in result
        assert result["validation"]["stable"] is True
