"""
Project Champollion: Entropy-Based Decipherment Auditorium

This module implements a multi-agent system for deciphering unknown semiotic
systems using UTAC (Universal Theory of Adaptive Criticality) principles.

The decipherment process is modeled as a threshold crossing:
    σ(β(R - Θ)) = S_coherence / S_max

Where:
    R: Decipherment effort (accumulated context)
    Θ: Critical insight threshold (the "Rosetta moment")
    β: Structural steepness (how quickly clarity emerges)
    S_coherence: Semantic coherence score
    S_max: Maximum possible coherence
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


class PatternAgent:
    """
    Agent specialized in syntactic pattern recognition.

    Identifies repetitions, n-grams, statistical regularities, and structural
    patterns such as word boundaries and grammatical structures.
    """

    def __init__(self, n_gram_range: tuple[int, int] = (1, 3)):
        """
        Initialize the PatternAgent.

        Args:
            n_gram_range: Tuple of (min_n, max_n) for n-gram analysis
        """
        self.n_gram_range = n_gram_range
        self.detected_patterns: dict[str, int] = {}

    def find_structure(self, sequence: str, return_top_k: int = 10) -> dict[str, Any]:
        """
        Identify syntactic patterns in the input sequence.

        Args:
            sequence: The unknown text/symbol sequence
            return_top_k: Number of top patterns to return

        Returns:
            Dictionary containing:
                - 'n_grams': Top n-gram patterns with frequencies
                - 'repetitions': Detected repetitive structures
                - 'candidate_boundaries': Possible word/phrase boundaries
        """
        if not sequence:
            return {
                "n_grams": [],
                "repetitions": [],
                "candidate_boundaries": [],
                "entropy": 0.0,
            }

        min_n, max_n = self.n_gram_range
        ngram_counts: dict[str, int] = {}
        for n in range(min_n, max_n + 1):
            for idx in range(len(sequence) - n + 1):
                ngram = sequence[idx : idx + n]
                ngram_counts[ngram] = ngram_counts.get(ngram, 0) + 1

        sorted_ngrams = sorted(ngram_counts.items(), key=lambda item: item[1], reverse=True)
        top_ngrams = [
            {"pattern": pattern, "count": count, "length": len(pattern)}
            for pattern, count in sorted_ngrams[:return_top_k]
        ]

        repetitions = [
            {
                "pattern": pattern,
                "count": count,
                "length": len(pattern),
            }
            for pattern, count in sorted_ngrams
            if count > 1 and len(pattern) > 1
        ]

        candidate_boundaries = self._candidate_boundaries(sequence)

        return {
            "n_grams": top_ngrams,
            "repetitions": repetitions[:return_top_k],
            "candidate_boundaries": candidate_boundaries,
            "entropy": self._calculate_pattern_entropy(sequence),
        }

    def _calculate_pattern_entropy(self, sequence: str) -> float:
        """
        Calculate Shannon entropy of the symbol sequence.

        Args:
            sequence: Input symbol sequence

        Returns:
            Shannon entropy in bits
        """
        if not sequence:
            return 0.0

        # Character frequency distribution
        freq_dist = {}
        for char in sequence:
            freq_dist[char] = freq_dist.get(char, 0) + 1

        # Normalize to probabilities
        total = len(sequence)
        probs = np.array([count / total for count in freq_dist.values()])

        # Shannon entropy: H = -Σ p(x) log₂ p(x)
        entropy = -np.sum(probs * np.log2(probs + 1e-10))

        return entropy

    def _candidate_boundaries(self, sequence: str) -> list[int]:
        if len(sequence) < 3:
            return []
        if " " in sequence:
            return [idx for idx, char in enumerate(sequence) if char == " "]

        bigram_counts: dict[str, int] = {}
        for idx in range(len(sequence) - 1):
            bigram = sequence[idx : idx + 2]
            bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1

        frequencies = np.array(list(bigram_counts.values()), dtype=float)
        if frequencies.size == 0:
            return []
        threshold = float(np.percentile(frequencies, 20))

        boundaries: list[int] = []
        for idx in range(1, len(sequence)):
            bigram = sequence[idx - 1 : idx + 1]
            if bigram_counts.get(bigram, 0) <= threshold:
                boundaries.append(idx)
        return boundaries


class ContextAgent:
    """
    Agent specialized in semantic hypothesis generation.

    Proposes meaning mappings based on context, builds provisional lexicons,
    and generates translation candidates.
    """

    def __init__(self, context_corpus: list[str] | None = None):
        """
        Initialize the ContextAgent.

        Args:
            context_corpus: Optional list of known texts for context
        """
        self.context_corpus = context_corpus or []
        self.provisional_lexicon: dict[str, list[str]] = {}

    def hypothesize_meanings(
        self, syntax_hypotheses: dict[str, Any], confidence_threshold: float = 0.5
    ) -> list[dict[str, Any]]:
        """
        Generate semantic hypotheses based on syntactic patterns.

        Args:
            syntax_hypotheses: Output from PatternAgent
            confidence_threshold: Minimum confidence for hypotheses

        Returns:
            List of semantic hypotheses with confidence scores
        """
        hypotheses = []
        ngrams = syntax_hypotheses.get("n_grams", [])
        if not ngrams:
            return hypotheses

        max_count = max((entry.get("count", 1) for entry in ngrams), default=1)
        context_tokens = self._context_tokens()

        for entry in ngrams:
            pattern = entry.get("pattern", "")
            count = entry.get("count", 0)
            confidence = float(count) / float(max_count)
            translation = self._map_pattern_to_context(pattern, context_tokens)
            coherence = self._compute_coherence_score(translation, self.context_corpus)
            if confidence >= confidence_threshold or coherence >= confidence_threshold:
                hypotheses.append(
                    {
                        "pattern": pattern,
                        "translation": translation,
                        "confidence": confidence,
                        "coherence": coherence,
                    }
                )

        return hypotheses

    def _compute_coherence_score(self, hypothesis: str, context: list[str]) -> float:
        """
        Compute semantic coherence score for a translation hypothesis.

        Args:
            hypothesis: Proposed translation
            context: Context corpus for comparison

        Returns:
            Coherence score in [0, 1]
        """
        if not hypothesis or not context:
            return 0.0

        hypothesis_tokens = set(hypothesis.lower().split())
        context_tokens = set(" ".join(context).lower().split())
        if not hypothesis_tokens or not context_tokens:
            return 0.0
        overlap = hypothesis_tokens.intersection(context_tokens)
        return float(len(overlap) / len(hypothesis_tokens.union(context_tokens)))

    def _context_tokens(self) -> list[str]:
        return list({token for token in " ".join(self.context_corpus).split() if token})

    def _map_pattern_to_context(self, pattern: str, context_tokens: list[str]) -> str:
        if not context_tokens:
            return f"concept_{pattern}"
        pattern_set = set(pattern)
        best_token = None
        best_score = -1.0
        for token in context_tokens:
            token_set = set(token)
            score = len(pattern_set.intersection(token_set))
            if score > best_score:
                best_score = score
                best_token = token
        return best_token or f"concept_{pattern}"


class SigillinScribe:
    """
    Agent specialized in entropy validation and hypothesis testing.

    Validates translation candidates against entropy minimization criteria
    and computes ΔAIC scores for competing hypotheses.
    """

    def __init__(self, baseline_entropy: float | None = None):
        """
        Initialize the SigillinScribe.

        Args:
            baseline_entropy: Maximum entropy (null hypothesis)
        """
        self.baseline_entropy = baseline_entropy
        self.validation_history: list[dict[str, Any]] = []

    def validate(
        self, hypotheses: list[dict[str, Any]], original_sequence: str
    ) -> tuple[dict[str, Any] | None, float]:
        """
        Validate translation hypotheses using entropy and ΔAIC criteria.

        Args:
            hypotheses: List of translation hypotheses from ContextAgent
            original_sequence: Original undeciphered sequence

        Returns:
            Tuple of (best_hypothesis, delta_aic) or (None, 0) if no valid hypothesis
        """
        if not hypotheses:
            return None, 0.0

        null_entropy = self.baseline_entropy
        if null_entropy is None:
            null_entropy = self._shannon_entropy(original_sequence)

        best_hypothesis = None
        best_delta_aic = -np.inf

        for hypothesis in hypotheses:
            translation = hypothesis.get("translation", "")
            hypothesis_entropy = self._shannon_entropy(translation)
            delta_aic = self._compute_delta_aic(null_entropy, hypothesis_entropy)
            record = {
                "hypothesis": hypothesis,
                "null_entropy": null_entropy,
                "hypothesis_entropy": hypothesis_entropy,
                "delta_aic": delta_aic,
            }
            self.validation_history.append(record)

            if delta_aic > best_delta_aic:
                best_delta_aic = delta_aic
                best_hypothesis = hypothesis

        if best_delta_aic < 10:
            return None, float(best_delta_aic)

        return best_hypothesis, float(best_delta_aic)

    def _shannon_entropy(self, sequence: str) -> float:
        if not sequence:
            return 0.0
        freq_dist: dict[str, int] = {}
        for char in sequence:
            freq_dist[char] = freq_dist.get(char, 0) + 1
        total = len(sequence)
        probs = np.array([count / total for count in freq_dist.values()])
        return float(-np.sum(probs * np.log2(probs + 1e-10)))

    def _compute_delta_aic(
        self,
        null_entropy: float,
        hypothesis_entropy: float,
        k_null: int = 1,
        k_hypothesis: int = 10,
    ) -> float:
        """
        Compute ΔAIC between null model and hypothesis.

        ΔAIC = 2(k₁ - k₀) + 2(log L₀ - log L₁)

        Args:
            null_entropy: Entropy under null (random) model
            hypothesis_entropy: Entropy under deciphered hypothesis
            k_null: Number of parameters in null model
            k_hypothesis: Number of parameters in hypothesis model

        Returns:
            ΔAIC score (positive values favor hypothesis)
        """
        # Simplified ΔAIC using entropy as proxy for log-likelihood
        # In practice, would compute proper likelihood ratios
        delta_k = k_hypothesis - k_null
        delta_logL = null_entropy - hypothesis_entropy  # Higher entropy = lower likelihood

        delta_aic = 2 * delta_k + 2 * delta_logL

        return delta_aic


def load_cipher_text(filepath: Path) -> str:
    """
    Load cipher text from CSV file.

    Args:
        filepath: Path to CSV file with 'symbol_sequence' column

    Returns:
        Concatenated symbol sequence
    """
    sequences = []

    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "symbol_sequence" in row:
                sequences.append(row["symbol_sequence"])

    return "".join(sequences)


def main():
    """Main entry point for the Champollion decipherment auditorium."""
    parser = argparse.ArgumentParser(
        description="UTAC-based decipherment of unknown semiotic systems"
    )
    parser.add_argument(
        "--input", type=Path, required=True, help="Path to CSV file with cipher text"
    )
    parser.add_argument(
        "--method",
        choices=["entropy_descent", "pattern_first", "context_first"],
        default="entropy_descent",
        help="Decipherment strategy",
    )
    parser.add_argument("--output", type=Path, help="Optional output path for results (JSON)")

    args = parser.parse_args()

    # Load cipher text
    print(f"Loading cipher text from {args.input}")
    cipher_text = load_cipher_text(args.input)
    print(f"Loaded {len(cipher_text)} symbols")

    # Initialize agents
    print("Initializing multi-agent auditorium...")
    pattern_agent = PatternAgent()
    context_agent = ContextAgent()
    scribe = SigillinScribe()

    # Phase 1: Pattern recognition
    print("\n[PatternAgent] Analyzing syntactic structure...")
    syntax_hypotheses = pattern_agent.find_structure(cipher_text)
    print(f"  - Baseline entropy: {syntax_hypotheses['entropy']:.3f} bits")

    # Phase 2: Semantic mapping
    print("\n[ContextAgent] Generating semantic hypotheses...")
    meaning_hypotheses = context_agent.hypothesize_meanings(syntax_hypotheses)
    print(f"  - Generated {len(meaning_hypotheses)} hypotheses")

    # Phase 3: Validation
    print("\n[SigillinScribe] Validating against entropy minimization...")
    best_translation, delta_aic = scribe.validate(meaning_hypotheses, cipher_text)

    if delta_aic >= 10:
        print(f"\n✅ Decipherment successful! ΔAIC = {delta_aic:.2f}")
        print(f"Translation: {best_translation}")
    else:
        print(f"\n⚠️  No significant decipherment found (ΔAIC = {delta_aic:.2f} < 10)")

    # Save results if requested
    if args.output:
        results = {
            "cipher_length": len(cipher_text),
            "baseline_entropy": syntax_hypotheses["entropy"],
            "delta_aic": delta_aic,
            "best_translation": best_translation,
            "method": args.method,
        }

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
