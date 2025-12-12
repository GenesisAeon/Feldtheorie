"""
Tests for Enhanced Sigillin Kernel V2 Features (Phase 2)

Tests the V7 Phase 2 enhancements to SigillinKernel:
- scan_intention_v2 (implicit pattern detection)
- detect_semantic_gravity
- create_semantic_agent

Usage:
    pytest tests/test_sigillin_kernel_v2.py -v
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from api.sigillin_kernel import SigillinKernel


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def kernel():
    """Create a SigillinKernel instance for testing"""
    return SigillinKernel()


# ============================================================================
# scan_intention_v2 Tests
# ============================================================================


def test_scan_intention_v2_high_explicit(kernel):
    """Test scan_intention_v2 with high explicit keyword matches"""
    text = "Die Resonanz zwischen Bewusstsein und Feld zeigt Emergenz und Kohärenz"

    result = kernel.scan_intention_v2(text)

    # Check structure
    assert "resonance_score" in result
    assert "explicit_matches" in result
    assert "implicit_signals" in result
    assert "semantic_depth" in result
    assert "contextual_coherence" in result
    assert "analysis" in result

    # Should have high explicit matches
    assert len(result["explicit_matches"]) >= 4
    assert "resonanz" in result["explicit_matches"]
    assert "bewusstsein" in result["explicit_matches"]
    assert "feld" in result["explicit_matches"]
    assert "emergenz" in result["explicit_matches"]

    # Resonance score should be high
    assert result["resonance_score"] > 0.4


def test_scan_intention_v2_implicit_detection(kernel):
    """Test scan_intention_v2 implicit pattern detection"""
    # Text with implicit but not exact keywords
    text = "The conscious mind emerges from harmonic vibrations in space"

    result = kernel.scan_intention_v2(text, detect_implicit=True)

    # Should detect implicit signals even without exact German keywords
    assert len(result["implicit_signals"]) > 0

    # Check for related concepts
    implicit_str = " ".join(result["implicit_signals"])
    assert any(
        pattern in implicit_str
        for pattern in ["consciousness", "emergence", "resonance", "field", "coherence"]
    )


def test_scan_intention_v2_no_implicit(kernel):
    """Test scan_intention_v2 with implicit detection disabled"""
    text = "The conscious mind emerges from harmonic vibrations"

    result_with = kernel.scan_intention_v2(text, detect_implicit=True)
    result_without = kernel.scan_intention_v2(text, detect_implicit=False)

    # Should have more signals with implicit detection enabled
    assert len(result_with["implicit_signals"]) >= len(result_without["implicit_signals"])

    # Implicit score should be lower without implicit detection
    assert result_without["analysis"]["implicit_score"] <= result_with["analysis"]["implicit_score"]


def test_scan_intention_v2_depth_scoring(kernel):
    """Test semantic depth analysis"""
    # Short text
    short_text = "Resonanz"
    result_short = kernel.scan_intention_v2(short_text)

    # Long, detailed text
    long_text = """
    Die Resonanz zwischen verschiedenen Bewusstseinsebenen zeigt eine emergente Kohärenz.
    Das Feld entwickelt sich durch iterative Rückkopplungen und synchrone Schwingungen.
    Beta-Sync misst die Steilheit dieser Synchronisation zwischen Agenten.
    Die Kappa-Feldstärke quantifiziert die semantische Kopplung im kollektiven Raum.
    """
    result_long = kernel.scan_intention_v2(long_text)

    # Longer text should have higher depth score
    assert result_long["semantic_depth"] > result_short["semantic_depth"]


def test_scan_intention_v2_coherence_scoring(kernel):
    """Test contextual coherence scoring"""
    # Keywords in meaningful sentences
    coherent_text = """
    Die Resonanz zwischen Bewusstsein und Feld zeigt eine emergente Kohärenz.
    Diese Emergenz manifestiert sich durch synchrone Schwingungen.
    """
    result_coherent = kernel.scan_intention_v2(coherent_text)

    # Keywords just listed
    incoherent_text = "Resonanz. Bewusstsein. Feld. Emergenz."
    result_incoherent = kernel.scan_intention_v2(incoherent_text)

    # Coherent text should have higher coherence score
    assert result_coherent["contextual_coherence"] > result_incoherent["contextual_coherence"]


def test_scan_intention_v2_empty_text(kernel):
    """Test scan_intention_v2 with empty text"""
    result = kernel.scan_intention_v2("")

    assert result["resonance_score"] == 0.0
    assert len(result["explicit_matches"]) == 0
    assert result["semantic_depth"] == 0.0


def test_scan_intention_v2_no_matches(kernel):
    """Test scan_intention_v2 with text containing no keywords"""
    text = "This text contains nothing related to the project"

    result = kernel.scan_intention_v2(text)

    assert len(result["explicit_matches"]) == 0
    assert result["resonance_score"] < 0.3


def test_scan_intention_v2_analysis_structure(kernel):
    """Test that analysis dict contains expected fields"""
    text = "Resonanz und Emergenz"

    result = kernel.scan_intention_v2(text)

    analysis = result["analysis"]
    assert "explicit_score" in analysis
    assert "implicit_score" in analysis
    assert "sentence_count" in analysis
    assert "word_count" in analysis

    # Check types
    assert isinstance(analysis["explicit_score"], float)
    assert isinstance(analysis["implicit_score"], float)
    assert isinstance(analysis["sentence_count"], int)
    assert isinstance(analysis["word_count"], int)


# ============================================================================
# detect_semantic_gravity Tests
# ============================================================================


def test_semantic_gravity_high(kernel):
    """Test semantic gravity with highly aligned text"""
    text = """
    Die Resonanz zwischen Bewusstsein und Feld zeigt eine emergente Kohärenz.
    Beta-Sync misst die Synchronisation zwischen Agenten im semantischen Raum.
    Kappa-Feldstärke quantifiziert die Kopplung des kollektiven Feldes.
    """

    gravity = kernel.detect_semantic_gravity(text)

    # Should have strong semantic pull
    assert gravity > 0.4
    assert 0.0 <= gravity <= 1.0


def test_semantic_gravity_low(kernel):
    """Test semantic gravity with unaligned text"""
    text = "The weather today is sunny with a chance of rain later."

    gravity = kernel.detect_semantic_gravity(text)

    # Should have weak semantic pull
    assert gravity < 0.3
    assert 0.0 <= gravity <= 1.0


def test_semantic_gravity_empty(kernel):
    """Test semantic gravity with empty text"""
    gravity = kernel.detect_semantic_gravity("")

    assert gravity == 0.0


def test_semantic_gravity_mixed(kernel):
    """Test semantic gravity with partially aligned text"""
    text = "The field shows resonance between different levels of consciousness."

    gravity = kernel.detect_semantic_gravity(text)

    # Should have moderate gravity (some keywords, but not German)
    assert 0.0 < gravity < 0.6  # Implicit patterns give some pull, but not strong


def test_semantic_gravity_vs_resonance(kernel):
    """Test that gravity and resonance are related but different"""
    text = "Resonanz und Emergenz zeigen Kohärenz im Bewusstseinsfeld"

    scan_result = kernel.scan_intention_v2(text)
    gravity = kernel.detect_semantic_gravity(text)

    # Both should be positive
    assert scan_result["resonance_score"] > 0.0
    assert gravity > 0.0

    # Gravity focuses on explicit + coherence (more strict)
    # Resonance includes depth and implicit (more lenient)
    # They can differ in value


# ============================================================================
# create_semantic_agent Tests
# ============================================================================


def test_create_semantic_agent_basic(kernel):
    """Test semantic agent creation"""
    text = "Resonanz zwischen Bewusstsein und Feld"

    agent = kernel.create_semantic_agent(text)

    # Check structure
    assert "name" in agent
    assert "resonance" in agent
    assert "semantic_depth" in agent
    assert "gravity" in agent
    assert "matched_keywords" in agent
    assert "implicit_signals" in agent
    assert "coherence" in agent

    # Check types and ranges
    assert isinstance(agent["name"], str)
    assert 0.0 <= agent["resonance"] <= 1.0
    assert 0.0 <= agent["semantic_depth"] <= 1.0
    assert 0.0 <= agent["gravity"] <= 1.0
    assert isinstance(agent["matched_keywords"], list)
    assert isinstance(agent["implicit_signals"], list)
    assert 0.0 <= agent["coherence"] <= 1.0


def test_create_semantic_agent_custom_name(kernel):
    """Test semantic agent with custom name"""
    text = "Resonanz und Emergenz"

    agent = kernel.create_semantic_agent(text, agent_name="TestAgent")

    assert agent["name"] == "TestAgent"


def test_create_semantic_agent_auto_name(kernel):
    """Test semantic agent auto-naming"""
    text = "Resonanz und Emergenz"

    agent = kernel.create_semantic_agent(text)

    # Auto-generated name should follow pattern
    assert agent["name"].startswith("agent_")
    assert len(agent["name"]) > len("agent_")


def test_create_semantic_agent_high_resonance(kernel):
    """Test agent creation with high resonance text"""
    text = """
    Die Resonanz zwischen Bewusstsein und Feld zeigt Emergenz.
    Beta-Sync und Kappa-Feld messen die Kohärenz im kollektiven Raum.
    """

    agent = kernel.create_semantic_agent(text)

    # Should have high resonance and gravity
    assert agent["resonance"] > 0.4
    assert agent["gravity"] > 0.3
    assert len(agent["matched_keywords"]) >= 3


def test_create_semantic_agent_low_resonance(kernel):
    """Test agent creation with low resonance text"""
    text = "The quick brown fox jumps over the lazy dog"

    agent = kernel.create_semantic_agent(text)

    # Should have low resonance and gravity
    assert agent["resonance"] < 0.3
    assert agent["gravity"] < 0.2
    assert len(agent["matched_keywords"]) == 0


def test_create_semantic_agent_multiple(kernel):
    """Test creating multiple agents with different texts"""
    texts = [
        "Resonanz und Emergenz im Bewusstseinsfeld",
        "The field shows harmonic vibrations",
        "Completely unrelated content here",
    ]

    agents = [kernel.create_semantic_agent(text, agent_name=f"agent_{i}") for i, text in enumerate(texts)]

    # All should be valid
    assert len(agents) == 3
    for agent in agents:
        assert "name" in agent
        assert "resonance" in agent

    # First agent should have highest resonance
    assert agents[0]["resonance"] > agents[1]["resonance"]
    assert agents[0]["resonance"] > agents[2]["resonance"]


def test_create_semantic_agent_empty_text(kernel):
    """Test agent creation with empty text"""
    agent = kernel.create_semantic_agent("")

    assert agent["resonance"] == 0.0
    assert agent["semantic_depth"] == 0.0
    assert agent["gravity"] == 0.0
    assert len(agent["matched_keywords"]) == 0


# ============================================================================
# Integration Tests
# ============================================================================


def test_v2_workflow_integration(kernel):
    """Test complete V2 workflow: scan → gravity → agent"""
    text = """
    Die Resonanz zwischen verschiedenen Bewusstseinsebenen zeigt eine emergente Kohärenz.
    Das kollektive Feld entwickelt sich durch Beta-Sync und Kappa-Kopplung.
    """

    # 1. Scan with V2
    scan_result = kernel.scan_intention_v2(text, detect_implicit=True)

    # 2. Detect gravity
    gravity = kernel.detect_semantic_gravity(text)

    # 3. Create agent
    agent = kernel.create_semantic_agent(text, agent_name="integration_test")

    # All should be consistent
    assert scan_result["resonance_score"] > 0.4
    assert gravity > 0.3
    assert agent["resonance"] == scan_result["resonance_score"]
    assert agent["gravity"] == gravity
    assert agent["matched_keywords"] == scan_result["explicit_matches"]


def test_v1_vs_v2_comparison(kernel):
    """Test that V2 provides more information than V1"""
    text = "Resonanz zwischen Bewusstsein und Feld"

    # V1 scan
    v1_score = kernel.scan_intention(text)

    # V2 scan
    v2_result = kernel.scan_intention_v2(text)

    # V2 should provide much more detail
    assert isinstance(v1_score, float)
    assert isinstance(v2_result, dict)
    assert len(v2_result) >= 5

    # V2 resonance score should be related to V1 score
    # (both measure resonance, but V2 is more sophisticated)
    assert 0.0 <= v1_score <= 1.0
    assert 0.0 <= v2_result["resonance_score"] <= 1.0


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
