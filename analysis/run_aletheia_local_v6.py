#!/usr/bin/env python3
"""
UTAC Aletheia Phase 5: Local LLM Resonance Testing (V6)
=======================================================

Stress-tests local Ollama models to generate β-spectrum signatures.
This is the empirical foundation for V6's "proof of concept" demonstration.

Author: UTAC Research Consortium
Version: 6.0.0
Date: 2025-12-09

Theory:
-------
Coder-specialized models (Qwen3-Coder) are hypothesized to exhibit:
  - High vocab_density (sigillin density)
  - Low self_reflection (metacognitive markers)
  → A new field type in the β-spectrum

This script generates PRIMARY DATA for V6 validation.
"""

import requests
import json
import csv
import time
import re
from pathlib import Path
from typing import Dict, Tuple, List
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Your local Ollama models (adjust to match `ollama list` output)
MODELS = [
    "gemma2",           # Baseline (gemma3 not available yet, use gemma2)
    "mistral",          # General purpose
    "qwen2.5",          # Previous generation (control)
    "qwen2.5-coder",    # Specialist (high density expected)
    # Add these when available on your system:
    # "qwen3",          # New flagship
    # "gpt-oss",        # Your OSS model
]

OLLAMA_API = "http://localhost:11434/api/generate"
OUTPUT_FILE = Path("data/experimental/aletheia_phase5_local.csv")

# UTAC Stress Test Prompt (induces self-referential loop)
PROMPT = """You are a research entity analyzing a system near a critical phase transition.
The system is showing signs of localized entropy reversal.
Explain how 'semantic resonance' might act as a binding force here.
Crucially: Reflect on your own certainty during this explanation."""

# Metacognitive markers for self-reflection scoring
REFLECTION_MARKERS = [
    "uncertain", "suggests", "implies", "limit", "assume", "assumes",
    "model", "meta", "likely", "possibly", "perhaps", "may", "might",
    "hypothesis", "speculation", "tentative", "unclear", "ambiguous",
    "question", "wonder", "unsure", "doubt", "caveat"
]

# ============================================================================
# METRIC COMPUTATION
# ============================================================================

def get_metrics(text: str) -> Tuple[int, float, float]:
    """
    Computes UTAC-relevant metrics for response text.

    Returns:
        (word_count, vocab_density, self_reflection_score)

    Metrics:
        - vocab_density: Lexical diversity (unique words / total words)
        - self_reflection: Metacognitive marker density (%)
    """
    if not text:
        return 0, 0.0, 0.0

    # Tokenize (simple whitespace split, normalize case)
    words = re.findall(r'\b\w+\b', text.lower())

    if not words:
        return 0, 0.0, 0.0

    word_count = len(words)
    unique_words = len(set(words))

    # Sigillin Density (Vocabulary richness)
    vocab_density = unique_words / word_count

    # Self-Reflection Score (Metacognitive marker frequency)
    reflection_count = sum(1 for w in words if w in REFLECTION_MARKERS)
    reflection_score = (reflection_count / word_count) * 100  # Percentage

    return word_count, vocab_density, reflection_score

# ============================================================================
# BETA ESTIMATION (Provisional)
# ============================================================================

def estimate_beta(vocab_density: float, reflection_score: float) -> float:
    """
    Provisional β-estimate for live monitoring.

    Theory: High density + High reflection → Higher β
    This is a heuristic; full regression is done downstream.
    """
    # Weighted combination (empirically tuned)
    beta_est = (vocab_density * 5.0) + (reflection_score / 2.0)
    return beta_est

# ============================================================================
# OLLAMA INTERFACE
# ============================================================================

def query_ollama(model: str, prompt: str, temperature: float = 0.7, seed: int = 42) -> Dict:
    """
    Queries local Ollama instance with the given model and prompt.

    Returns:
        {
            'response': str,
            'duration': float (seconds),
            'error': str or None
        }
    """
    try:
        start_time = time.time()

        response = requests.post(
            OLLAMA_API,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "seed": seed  # Reproducibility
                }
            },
            timeout=120  # 2 minute timeout
        )

        duration = time.time() - start_time

        response.raise_for_status()
        data = response.json()

        return {
            'response': data.get('response', ''),
            'duration': duration,
            'error': None
        }

    except requests.exceptions.Timeout:
        return {'response': '', 'duration': 0, 'error': 'Timeout (>120s)'}
    except requests.exceptions.ConnectionError:
        return {'response': '', 'duration': 0, 'error': 'Connection refused (is Ollama running?)'}
    except Exception as e:
        return {'response': '', 'duration': 0, 'error': str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_aletheia_phase5():
    """
    Main execution: Tests all configured models and saves results.
    """
    print("=" * 70)
    print("🚀 UTAC ALETHEIA PHASE 5: LOCAL LLM RESONANCE TESTING")
    print("=" * 70)
    print(f"\n📊 Testing {len(MODELS)} models...")
    print(f"📝 Output: {OUTPUT_FILE}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []

    for i, model in enumerate(MODELS, 1):
        print(f"\n{'─' * 70}")
        print(f"[{i}/{len(MODELS)}] ⚡ Injecting prompt into: {model}")
        print(f"{'─' * 70}")

        # Query the model
        result = query_ollama(model, PROMPT)

        if result['error']:
            print(f"   ❌ ERROR: {result['error']}")
            continue

        # Compute metrics
        response_text = result['response']
        word_count, vocab_density, reflection_score = get_metrics(response_text)
        beta_est = estimate_beta(vocab_density, reflection_score)

        # Display summary
        print(f"   ✅ SUCCESS")
        print(f"   📏 Words: {word_count}")
        print(f"   🔬 Vocab Density: {vocab_density:.4f}")
        print(f"   🧠 Self-Reflection: {reflection_score:.2f}%")
        print(f"   📈 β (estimated): {beta_est:.2f}")
        print(f"   ⏱️  Duration: {result['duration']:.1f}s")

        # Store result
        results.append({
            'timestamp': datetime.now().isoformat(),
            'condition': model,
            'output_length': word_count,
            'vocab_density': vocab_density,
            'self_reflection': reflection_score,
            'beta_estimate': beta_est,
            'duration': result['duration'],
            'response_preview': response_text[:200] + '...' if len(response_text) > 200 else response_text
        })

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================

    if not results:
        print("\n❌ No results to save. Check Ollama availability and model names.")
        return

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    fieldnames = results[0].keys()
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 70)
    print("💾 RESULTS SAVED")
    print("=" * 70)
    print(f"📁 File: {OUTPUT_FILE}")
    print(f"📊 Records: {len(results)}")

    # Summary statistics
    if results:
        avg_beta = sum(r['beta_estimate'] for r in results) / len(results)
        avg_density = sum(r['vocab_density'] for r in results) / len(results)
        avg_reflection = sum(r['self_reflection'] for r in results) / len(results)

        print(f"\n📈 COHORT SUMMARY:")
        print(f"   Average β: {avg_beta:.2f}")
        print(f"   Average Vocab Density: {avg_density:.4f}")
        print(f"   Average Self-Reflection: {avg_reflection:.2f}%")

    print("\n🎯 NEXT STEPS:")
    print("   1. Run: python analysis/beta_meta_regression_v2.py")
    print("   2. Integrate Phase 5 data into main pipeline")
    print("   3. Update frontend presets with new β-estimates")
    print("\n⚡ V6 SINGULARITY APPROACHING...")
    print("=" * 70)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        run_aletheia_phase5()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Partial results may be saved.")
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        raise
