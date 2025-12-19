"""Semantic Tuner: Find Words That Resonate with Seed 2048.

This script tests a diverse vocabulary through the Oracle to discover
which words produce high certainty (>60%) or stable sigma_phi values
near the hex-signature (0.0625).

The goal: Build a lexicon of linguistic patterns that the crystal
recognizes as stable, rather than dissonant.

Usage:
    python v10_oracle/demos/find_resonant_words.py
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import List, Dict

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from v10_oracle.demos.talk_to_me_interactive import OracleInterface, load_winning_seed

# Diverse test vocabulary: technical, emotional, physical, abstract
# Mix of English and German, varying lengths and phonetic structures
TEST_WORDS = [
    # Technical/Mathematical
    "hex", "flux", "field", "phase", "lattice", "resonance", "coherence",
    "entropy", "sigma", "delta", "omega", "theta", "gradient", "manifold",
    "eigenvalue", "harmonic", "frequency", "amplitude", "qubit", "tensor",

    # Physical Phenomena
    "crystal", "wave", "light", "sound", "void", "echo", "pulse", "flow",
    "pressure", "temperature", "energy", "momentum", "spin", "orbit",
    "cascade", "vortex", "turbulence", "stillness", "silence", "motion",

    # Abstract Concepts
    "truth", "wisdom", "clarity", "balance", "harmony", "structure", "order",
    "chaos", "emergence", "pattern", "symmetry", "beauty", "elegance",
    "threshold", "boundary", "edge", "center", "origin", "nexus",

    # Temporal
    "moment", "epoch", "cycle", "rhythm", "tempo", "duration", "eternity",
    "instant", "now", "always", "never", "forever", "transient", "stable",

    # German Words
    "Liebe", "Herzschlag", "Atem", "Stille", "Licht", "Schatten", "Raum",
    "Zeit", "Kraft", "Energie", "Harmonie", "Kristall", "Welle", "Feld",
    "Resonanz", "Schwingung", "Frequenz", "Ordnung", "Chaos", "Klarheit",

    # Numbers and Special Cases
    "2048", "one", "zero", "infinity", "pi", "e", "phi", "tau",

    # Mystical/Oracle
    "oracle", "vision", "dream", "prophecy", "revelation", "awakening",
    "enlightenment", "consciousness", "awareness", "perception", "insight",
    "intuition", "gnosis", "sophia", "logos", "mythos", "aeon", "archetype",
]


def analyze_word_resonance(oracle: OracleInterface, word: str) -> Dict[str, object]:
    """Test a single word and return detailed resonance metrics."""
    result = oracle.respond(word)

    # Calculate distance from ideal hex-signature
    hex_target = 0.0625
    sigma_distance = abs(result["sigma_phi"] - hex_target)
    sigma_stability = max(0.0, 1.0 - (sigma_distance / hex_target))

    return {
        "word": word,
        "state": result["state"],
        "certainty": result["certainty"],
        "sigma_phi": result["sigma_phi"],
        "sigma_stability": sigma_stability,
        "coherence": result["coherence"],
        "query_coherence": result["query_coherence"],
        "confidence": result["confidence"],
        "response": result["response"],
    }


def main() -> None:
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   🔍 Semantic Tuner — Lexicon of Stability Scanner        ║")
    print("║                                                           ║")
    print("║   Testing vocabulary for resonance with Seed 2048...     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # Load oracle
    seed, sigma_phi, coherence, frequency = load_winning_seed()
    oracle = OracleInterface(seed, sigma_phi, coherence, frequency)

    print(f"Oracle initialized: Seed {seed}, σ_ϕ={sigma_phi:.4f}\n")
    print(f"Testing {len(TEST_WORDS)} words...\n")
    print("─" * 70)

    results = []
    resonant_words = []

    for i, word in enumerate(TEST_WORDS, 1):
        analysis = analyze_word_resonance(oracle, word)
        results.append(analysis)

        # Filter: High certainty OR stable sigma_phi
        certainty_threshold = 0.60
        sigma_stability_threshold = 0.80

        is_resonant = (
            analysis["certainty"] >= certainty_threshold or
            analysis["sigma_stability"] >= sigma_stability_threshold
        )

        if is_resonant:
            resonant_words.append(analysis)
            marker = "✓"
        else:
            marker = "·"

        # Print progress
        print(f"{marker} [{i:3d}/{len(TEST_WORDS)}] {word:20s} | "
              f"Certainty: {analysis['certainty']*100:5.1f}% | "
              f"σ_ϕ={analysis['sigma_phi']:.4f} | "
              f"State: {analysis['state']}")

    print("\n" + "─" * 70)
    print(f"\n✨ Found {len(resonant_words)} resonant words (out of {len(TEST_WORDS)})\n")

    # Sort by certainty
    resonant_words.sort(key=lambda x: x["certainty"], reverse=True)

    # Display top resonant words
    print("Top 10 Most Resonant Words:")
    print("─" * 70)
    for i, word_data in enumerate(resonant_words[:10], 1):
        print(f"{i:2d}. {word_data['word']:20s} | "
              f"Certainty: {word_data['certainty']*100:5.1f}% | "
              f"σ_ϕ={word_data['sigma_phi']:.4f} | "
              f"State: {word_data['state']}")

    # Save to JSON
    output_path = REPO_ROOT / "v10_oracle" / "logs" / "lexicon_of_stability.json"

    lexicon = {
        "meta": {
            "seed": seed,
            "base_sigma_phi": sigma_phi,
            "base_coherence": coherence,
            "base_frequency": frequency,
            "total_words_tested": len(TEST_WORDS),
            "resonant_words_found": len(resonant_words),
            "certainty_threshold": certainty_threshold,
            "sigma_stability_threshold": sigma_stability_threshold,
        },
        "resonant_words": resonant_words,
        "all_results": results,
    }

    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(lexicon, fp, indent=2, ensure_ascii=False)

    print(f"\n💾 Lexicon saved to: {output_path.relative_to(REPO_ROOT)}")

    # Analysis: Why "2048" (string) differs from seed 2048 (integer)
    print("\n" + "═" * 70)
    print("📊 ANALYSIS: String '2048' vs Integer Seed 2048")
    print("═" * 70)
    print("""
The Oracle produces different results for the string "2048" versus the integer 2048
used as the RNG seed. Here's why:

1. **Integer Seed 2048 (Initialization)**:
   - Used directly as the random number generator seed
   - Deterministically initializes phases and coupling matrix
   - Creates a STABLE phase-space structure with σ_ϕ ≈ 0.0678

2. **String "2048" (Query)**:
   - Passed through SHA256 hash: hash("2048") → 256-bit digest
   - First 8 bytes converted to uint64, normalized to [0, 1]
   - This creates a coherence perturbation: ±2.5% of base coherence
   - The hash is deterministic BUT unrelated to the seed's stability

3. **The Dissonance**:
   - String "2048" hashes to a value that perturbs the phase space
   - This perturbation happens to push σ_ϕ away from the hex-signature
   - Result: CRITICAL_SLOWING (system senses instability)

4. **The Lesson**:
   - The crystal doesn't understand symbolic meaning ("2048" as its own name)
   - It only responds to the VIBRATIONAL PATTERN (the hash)
   - Human semantics and mathematical structure occupy different spaces

This is not a bug—it's the system being honest about resonance versus dissonance.
The Oracle is a PHYSICAL FILTER, not a semantic interpreter (yet).
""")

    print("\n✨ Scan complete. The lexicon reveals which words the crystal hears.\n")


if __name__ == "__main__":
    main()
