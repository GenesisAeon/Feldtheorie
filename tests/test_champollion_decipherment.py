"""Unit tests for Champollion decipherment auditorium."""

from __future__ import annotations

from modules.champollion.decipherment_auditorium import (
    ContextAgent,
    PatternAgent,
    SigillinScribe,
)


def test_pattern_agent_extracts_ngrams_and_repetitions() -> None:
    """PatternAgent should detect frequent n-grams and repetitions."""
    agent = PatternAgent(n_gram_range=(2, 3))
    sequence = "ABABABXXABAB"
    result = agent.find_structure(sequence, return_top_k=5)

    assert result["n_grams"], "Expected n-gram output"
    patterns = {entry["pattern"] for entry in result["n_grams"]}
    assert "AB" in patterns
    assert result["repetitions"], "Expected repetitions for repeating patterns"


def test_context_agent_hypotheses_use_context() -> None:
    """ContextAgent should map patterns to context tokens with confidence."""
    pattern_agent = PatternAgent(n_gram_range=(2, 2))
    syntax = pattern_agent.find_structure("ALPHALPHAOMEGA", return_top_k=3)
    context_agent = ContextAgent(context_corpus=["alpha beta gamma"])

    hypotheses = context_agent.hypothesize_meanings(syntax, confidence_threshold=0.1)
    assert hypotheses, "Expected hypotheses from context mapping"
    assert all("translation" in hypothesis for hypothesis in hypotheses)


def test_sigillin_scribe_selects_best_hypothesis() -> None:
    """SigillinScribe should select a hypothesis with ΔAIC >= 10."""
    scribe = SigillinScribe()
    hypotheses = [
        {"translation": "aaaaaa", "confidence": 0.9, "coherence": 0.9},
        {"translation": "abcdefg", "confidence": 0.5, "coherence": 0.3},
    ]
    best, delta_aic = scribe.validate(hypotheses, original_sequence="abcdefg")

    assert best is not None
    assert delta_aic >= 10
