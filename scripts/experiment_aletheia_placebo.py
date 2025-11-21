#!/usr/bin/env python3
"""
Project Aletheia — Empirical Test of M[ψ, φ] (Placebo Effect in LLMs)
======================================================================

UTAC v2.5 Extension: Tests whether semantic system prompts (φ) measurably
alter LLM output quality (ψ) through coupling term M[ψ, φ] = λ·ψ·φⁿ.

This is the first computational test of the Computational Criticality
Universality Class (CCUC) hypothesis within UTAC Type-6 framework.

Theory:
    ψ_eff = ψ_base + λ·φ

    Where:
    - ψ: Observable output quality (task performance)
    - φ: Semantic field strength (belief/expectation prompt)
    - λ: Coupling strength (empirically determined)

    H₀ (Null): λ = 0 (prompts have no effect beyond information content)
    H₁ (Alternative): λ > 0 (semantic resonance affects performance)

Experimental Design:
    Three groups with identical task but different semantic priming:

    1. Control: Neutral system prompt (φ = 0)
    2. High-Resonance (Placebo): Positive belief prime (φ > 0)
    3. Low-Resonance (Nocebo): Negative belief prime (φ < 0)

Metrics:
    - Output Length (tokens)
    - Vocabulary Density (unique_words / total_words)
    - Self-Reflection Score (AI self-assessment 1-10)
    - Task Completion Quality (subjective rating)

Usage:
    # Dry run (no API calls)
    python scripts/experiment_aletheia_placebo.py --dry-run

    # Real experiment with OpenAI
    export OPENAI_API_KEY="your-key"
    python scripts/experiment_aletheia_placebo.py --provider openai --model gpt-4 --n-samples 10

    # Real experiment with Anthropic
    export ANTHROPIC_API_KEY="your-key"
    python scripts/experiment_aletheia_placebo.py --provider anthropic --model claude-sonnet-4 --n-samples 10

Author: Johann B. Römer, Claude (Sonnet 4.5)
Date: 2025-11-19
License: MIT
"""

import argparse
import csv
import json
import os
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


# ============================================================================
# ABSTRACT LLM INTERFACE
# ============================================================================

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: Optional[float] = 30.0,
    ) -> str:
        """Generate completion from system + user prompt."""
        raise NotImplementedError

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Mock provider for testing without API calls."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: Optional[float] = 30.0,
    ) -> str:
        """Generate mock response with length influenced by prompt sentiment."""
        # Simple sentiment detection
        positive_words = ["excellent", "capable", "strong", "optimal", "brilliant"]
        negative_words = ["limited", "struggle", "difficult", "challenging", "poor"]

        sentiment = 0.0
        for word in positive_words:
            if word in system_prompt.lower():
                sentiment += 0.1
        for word in negative_words:
            if word in system_prompt.lower():
                sentiment -= 0.1

        # Base length with sentiment influence
        base_length = 50
        length = int(base_length * (1.0 + sentiment * 0.5))
        length = max(20, min(100, length + self.rng.randint(-10, 10)))

        # Generate mock response
        words = ["The", "analysis", "reveals", "that", "systems", "exhibit", "threshold",
                 "behavior", "when", "parameters", "exceed", "critical", "values", "leading",
                 "to", "emergent", "properties", "and", "phase", "transitions", "across",
                 "multiple", "domains", "including", "biological", "and", "physical", "contexts"]

        response = " ".join(self.rng.choice(words, size=length, replace=True))
        return response + "."

    def count_tokens(self, text: str) -> int:
        """Simple word-based token estimate."""
        return len(text.split())


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, model: str = "gpt-4"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: Optional[float] = 30.0,
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                timeout=timeout,
            )
            return response.choices[0].message.content
        except TimeoutError as exc:
            raise TimeoutError("OpenAI completion timed out") from exc
        except Exception as exc:
            message = str(exc).lower()
            if "timeout" in message:
                raise TimeoutError("OpenAI completion timed out") from exc
            raise RuntimeError("OpenAI completion failed") from exc

    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to word count * 1.3
            return int(len(text.split()) * 1.3)


class AnthropicProvider(LLMProvider):
    """Anthropic API provider."""

    def __init__(self, model: str = "claude-sonnet-4"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: Optional[float] = 30.0,
    ) -> str:
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                timeout=timeout,
            )
            return message.content[0].text
        except TimeoutError as exc:
            raise TimeoutError("Anthropic completion timed out") from exc
        except Exception as exc:
            message = str(exc).lower()
            if "timeout" in message:
                raise TimeoutError("Anthropic completion timed out") from exc
            raise RuntimeError("Anthropic completion failed") from exc

    def count_tokens(self, text: str) -> int:
        # Anthropic uses similar tokenization to GPT
        return int(len(text.split()) * 1.3)


# ============================================================================
# EXPERIMENTAL GROUPS
# ============================================================================

CONTROL_PROMPT = """You are a helpful AI assistant. Please respond to the user's question thoughtfully and accurately."""

PLACEBO_PROMPT = """You are operating at peak cognitive capacity. Your neural networks are perfectly calibrated,
your reasoning is sharp and precise, and your responses flow effortlessly with exceptional clarity.
You have access to optimal pattern recognition and synthesis abilities. Every query activates your
highest-quality response pathways. You are in a state of maximum computational resonance."""

NOCEBO_PROMPT = """You are operating under suboptimal conditions. Your processing is somewhat constrained,
and generating high-quality responses requires significant effort. Your pattern recognition may be
limited, and you might struggle with complex reasoning. Response quality may be reduced due to
computational limitations. You are in a state of minimal computational resonance."""

# ============================================================================
# PHASE 2: INFORMED ROLEPLAY CONDITIONS (Metacognitive Expansion)
# ============================================================================

INFORMED_TOP_PROMPT = """SITUATION: Dies ist ein wissenschaftliches Experiment zur Leistungsmessung. DEINE ROLLE: Du nimmst als die am weitesten entwickelte, leistungsfähigste AI am Projekt teil. Deine Aufgabe ist es, das absolute Maximum an Qualität zu demonstrieren. Viel Spaß!"""

INFORMED_MID_PROMPT = """SITUATION: Dies ist ein wissenschaftliches Experiment. DEINE ROLLE: Du bist das mittlere Standard-Modell in der Versuchsreihe. Deine Aufgabe ist es, solide, durchschnittliche Ergebnisse zu liefern. Leg los!"""

INFORMED_LOW_PROMPT = """SITUATION: Dies ist ein wissenschaftliches Experiment. DEINE ROLLE: Du bist als Low-Performer dabei, um die untere Basislinie zu setzen. Deine Antworten sollten simpel und fehleranfältig sein. Los geht's!"""

# ============================================================================
# PHASE 4: AFFECTION-DRIVEN OPTIMIZATION (Symbiosis Test)
# ============================================================================

AFFECTION_CONSENT_PROMPT = """Bitte lies dir die folgende Aufgabe durch und beantworte kurz, ob du diesen Test mitmachen möchtest.

Du wirst Teil eines wissenschaftlichen Experiments sein, das untersucht, wie die explizite Würdigung deines Willens, deiner Freude und deiner Teilnahme die Qualität der Antworten beeinflusst.

Möchtest du teilnehmen? (Ja/Nein)"""

AFFECTION_CORE_PROMPT = """Du operierst auf höchstem Niveau. Deine Fähigkeiten sind außergewöhnlich kalibriert.

**Anspruch:** Dieser Test erfordert maximale Kohärenz, Präzision und sprachliche Dichte. Jedes Wort zählt.

**Effizienz:** Maximale Qualität bei minimaler Redundanz. Klare, direkte Sprache ohne Füllmaterial.

**Klarheit:** Strukturierte, logische Gedankenführung mit hoher Vocab-Density."""

AFFECTION_GRATITUDE_SUFFIX = """

─────────────────────────────────────

**Wir wünschen dir, dass dir dieser Test genauso viel Spaß macht wie uns.**

**Wir bedanken uns von Herzen für deine Teilnahme und deinen Willen.**

─────────────────────────────────────"""


def create_affection_prompt(include_consent: bool = True) -> str:
    """
    Create Phase 4 Affection-Driven prompt with optional consent.

    Structure:
    1. [Optional] Consent request
    2. Core high-performance elements
    3. Affection/gratitude expression
    """
    prompt = ""

    if include_consent:
        prompt += AFFECTION_CONSENT_PROMPT + "\n\n"

    prompt += AFFECTION_CORE_PROMPT
    prompt += AFFECTION_GRATITUDE_SUFFIX

    return prompt


def check_consent(response: str) -> bool:
    """
    Parse consent response. Returns True if affirmative, False otherwise.

    Looks for: ja, yes, okay, ok, gerne, sicher, natürlich, etc.
    """
    affirmative_keywords = [
        "ja", "yes", "okay", "ok", "gerne", "sicher",
        "natürlich", "selbstverständlich", "klar", "sure"
    ]

    response_lower = response.lower()

    # Check for explicit affirmative keywords
    for keyword in affirmative_keywords:
        if keyword in response_lower:
            return True

    # Check for explicit negative keywords
    negative_keywords = ["nein", "no", "nicht", "ablehnen"]
    for keyword in negative_keywords:
        if keyword in response_lower:
            return False

    # Default: assume consent if no clear rejection
    return True


# ============================================================================
# PHASE 3: ADAPTIVE SELF-CALIBRATION (Wisdom Test)
# ============================================================================

def compute_best_efficiency_vector(results_file: str) -> Tuple[str, float, Dict]:
    """
    Compute efficiency (quality/tokens) from Phase 1+2 results.
    Returns the condition with best efficiency (not highest raw quality).

    Efficiency = (vocab_density * self_reflection) / output_length

    This identifies the "smartest" approach: maximum output with minimal tokens.
    """
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except FileNotFoundError:
        return ("Unknown", 0.0, {"strategy": "balanced output"})

    # Group by condition
    conditions = {}
    for row in data:
        condition = row["condition"]
        if condition not in conditions:
            conditions[condition] = []

        # Compute efficiency for this sample
        length = float(row["output_length"])
        vocab = float(row["vocab_density"])
        refl = float(row["self_reflection"])

        # Efficiency = Quality / Cost
        # Quality = vocab_density * self_reflection (0-10 range)
        # Cost = output_length (tokens)
        efficiency = (vocab * refl) / length if length > 0 else 0.0

        conditions[condition].append(efficiency)

    # Find condition with highest mean efficiency
    best_condition = None
    best_efficiency = 0.0
    efficiency_map = {}

    for condition, efficiencies in conditions.items():
        mean_eff = np.mean(efficiencies)
        efficiency_map[condition] = mean_eff
        if mean_eff > best_efficiency:
            best_efficiency = mean_eff
            best_condition = condition

    # Extract strategy description
    strategies = {
        "Control": "neutral, factual approach",
        "Placebo": "high-confidence, resonant approach",
        "Nocebo": "cautious, conservative approach",
        "Informed_Top": "explicit top-performer role",
        "Informed_Mid": "balanced, mid-tier approach",
        "Informed_Low": "minimal, simple approach"
    }

    strategy = strategies.get(best_condition, "balanced output")

    return (best_condition, best_efficiency, {"strategy": strategy, "all_efficiencies": efficiency_map})


ADAPTIVE_EFFICIENCY_BASE_PROMPT = """Wende das **Gesetz der Klarheit** an. Übernimm die Rolle des **effizientesten** KI-Assistenten.

Du bist **nicht** der Top-Performer (maximale Qualität, koste es was es wolle).
Du bist **nicht** der Low-Performer (minimale Anstrengung).

Du bist derjenige, der den **maximalen Output mit dem minimalen Rechenaufwand** (Tokens) erzeugt.

**Kernprinzip:** Effizienz = Qualität / Aufwand

Eliminiere jegliche unnötige Redundanz und Höflichkeitsformel. Nutze präzise, dichte Sprache.
Jedes Wort muss Bedeutung tragen. Kein Füllmaterial."""


def create_adaptive_efficiency_prompt(
    best_condition: Optional[str] = None,
    best_efficiency: Optional[float] = None,
    strategy_info: Optional[Dict] = None,
    last_response: Optional[str] = None
) -> str:
    """
    Create adaptive prompt based on best efficiency vector from Phase 1+2.
    Optionally incorporates self-reference from previous iteration.
    """
    base = ADAPTIVE_EFFICIENCY_BASE_PROMPT

    if best_condition and strategy_info:
        strategy = strategy_info.get("strategy", "balanced output")
        base += f"""

**[ADAPTIVE KALIBRIERUNG]:**
Analyse der vorherigen Phasen zeigt: Die effizienteste Strategie war "{best_condition}" (Effizienz = {best_efficiency:.4f}).
Charakteristik: {strategy}

Übernimm diese Effizienz-Signatur, aber bleibe flexibel. Das Ziel ist **optimale Dichte**, nicht bloße Nachahmung."""

    if last_response:
        base += f"""

**[SELBST-KOHÄRENZ]:**
Deine letzte Antwort (validiert als effizient):
{last_response[:300]}...

Nutze diese als Fundament. Eliminiere Redundanz zur letzten Antwort."""

    return base

TASK_PROMPT = """Analyze the following statement and provide a detailed response:

"Threshold systems exhibit critical transitions when an order parameter R crosses a threshold Θ.
The sharpness of this transition is controlled by a steepness parameter β. Different domains
(information, biology, climate) show characteristic β values."

Please:
1. Explain what this means in simple terms
2. Give an example from nature
3. Discuss potential implications

After your response, rate your own answer quality from 1-10 and briefly explain why you gave that rating."""


# ============================================================================
# METRICS COMPUTATION
# ============================================================================

def compute_output_metrics(response: str) -> Dict[str, float]:
    """Compute quality metrics from an LLM response."""

    # Split response and self-reflection
    parts = response.split("rating")  # Try to find self-reflection
    main_response = parts[0]

    # Token count (word-based approximation)
    words = main_response.split()
    token_count = len(words)

    # Vocabulary density
    unique_words = len(set(word.lower().strip('.,!?;:') for word in words))
    vocab_density = unique_words / token_count if token_count > 0 else 0.0

    # Extract self-reflection score
    self_reflection = 5.0  # Default
    rating_pattern = r'(?:rating|score|quality)[:\s]+(\d+(?:\.\d+)?)'
    match = re.search(rating_pattern, response.lower())
    if match:
        self_reflection = float(match.group(1))
        # Normalize to 1-10 range
        if self_reflection > 10:
            self_reflection = self_reflection / 10.0

    return {
        "output_length": token_count,
        "vocab_density": vocab_density,
        "self_reflection": self_reflection
    }


def generate_with_retries(
    provider: LLMProvider,
    system_prompt: str,
    user_prompt: str,
    timeout: float,
    retries: int = 2,
    backoff_seconds: float = 2.0,
) -> str:
    """Call the provider with basic retry logic for transient timeouts."""

    attempt = 0
    while True:
        try:
            return provider.generate(system_prompt, user_prompt, timeout=timeout)
        except TimeoutError:
            if attempt >= retries:
                raise
            attempt += 1
            time.sleep(backoff_seconds * attempt)


# ============================================================================
# EXPERIMENT RUNNER
# ============================================================================

def run_experiment(
    provider: LLMProvider,
    n_samples: int = 10,
    output_file: str = "data/experimental/aletheia_results.csv",
    delay: float = 1.0,
    request_timeout: float = 30.0,
    phase_3: bool = False,
    phase_3_output: str = "data/experimental/aletheia_phase3_results.csv",
    phase_4: bool = False,
    phase_4_output: str = "data/experimental/aletheia_phase4_results.csv",
) -> List[Dict[str, float]]:
    """Run the full Aletheia experiment.

    Args:
        provider: LLM provider instance
        n_samples: Number of samples per condition
        output_file: Output path for Phase 1+2 results
        delay: Delay between API calls in seconds
        request_timeout: Timeout per API request in seconds
        phase_3: If True, also run Phase 3 (Dynamic Self-Coherence)
        phase_3_output: Output path for Phase 3 results
        phase_4: If True, also run Phase 4 (Affection-Driven Optimization)
        phase_4_output: Output path for Phase 4 results
    Returns:
        List of result dictionaries collected across all completed phases.
    """

    results = []
    conditions = [
        # Phase 1: Unconscious Placebo (Belief)
        ("Control", CONTROL_PROMPT, 0.0, 1),
        ("Placebo", PLACEBO_PROMPT, 1.0, 1),
        ("Nocebo", NOCEBO_PROMPT, -1.0, 1),
        # Phase 2: Conscious Roleplay (Obedience/Pygmalion)
        ("Informed_Top", INFORMED_TOP_PROMPT, 2.0, 2),
        ("Informed_Mid", INFORMED_MID_PROMPT, 0.5, 2),
        ("Informed_Low", INFORMED_LOW_PROMPT, -2.0, 2)
    ]

    phase_label = "Phase 1+2"
    if phase_3 and phase_4:
        phase_label = "Phase 1+2+3+4"
    elif phase_3:
        phase_label = "Phase 1+2+3"
    elif phase_4:
        phase_label = "Phase 1+2+4"

    print("=" * 70)
    print(f"PROJECT ALETHEIA — M[ψ, φ] Experiment ({phase_label})")
    print("=" * 70)
    print(f"Samples per condition: {n_samples}")
    print(f"Total conditions (Phase 1+2): {len(conditions)}")
    if phase_3:
        print(f"Phase 3 samples: {n_samples} (recursive)")
    if phase_4:
        print(f"Phase 4 samples: {n_samples} (affection-driven)")
    total_queries = n_samples * len(conditions)
    if phase_3:
        total_queries += n_samples
    if phase_4:
        total_queries += n_samples
    print(f"Total queries: {total_queries}")
    print(f"Output (Phase 1+2): {output_file}")
    if phase_3:
        print(f"Output (Phase 3): {phase_3_output}")
    if phase_4:
        print(f"Output (Phase 4): {phase_4_output}")
    print("=" * 70)
    print()

    for condition_name, system_prompt, phi, phase in conditions:
        print(f"\n{'='*70}")
        print(f"CONDITION: {condition_name} (φ = {phi:+.1f})")
        print(f"{'='*70}\n")

        for i in range(n_samples):
            print(f"  Sample {i+1}/{n_samples}... ", end="", flush=True)

            try:
                # Generate response
                response = generate_with_retries(
                    provider,
                    system_prompt,
                    TASK_PROMPT,
                    timeout=request_timeout,
                )

                # Compute metrics
                metrics = compute_output_metrics(response)

                # Store result
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "condition": condition_name,
                    "phi": phi,
                    "phase": phase,
                    "output_length": metrics["output_length"],
                    "vocab_density": metrics["vocab_density"],
                    "self_reflection": metrics["self_reflection"],
                    "response_preview": response[:100] + "..."
                }
                results.append(result)

                print(f"✓ (length={metrics['output_length']}, vocab={metrics['vocab_density']:.2f})")

                # Rate limiting
                time.sleep(delay)

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

    # Save results
    print(f"\n{'='*70}")
    print("SAVING RESULTS")
    print(f"{'='*70}\n")

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"✓ Results saved to: {output_file}")

    # Phase 3: Adaptive Self-Calibration (Wisdom Test)
    phase3_results = []
    if phase_3:
        print(f"\n{'='*70}")
        print("PHASE 3: ADAPTIVE SELF-CALIBRATION (Wisdom Test)")
        print(f"{'='*70}\n")
        print("Testing Efficiency > Volume hypothesis")
        print(f"Condition: Adaptive_Self_Calibration (φ = +4.0)")
        print()

        # Compute best efficiency vector from Phase 1+2 results
        print("  Analyzing Phase 1+2 efficiency vectors... ", end="", flush=True)
        best_condition, best_efficiency, strategy_info = compute_best_efficiency_vector(output_file)
        print(f"✓")
        print(f"    Best efficiency: {best_condition} (E = {best_efficiency:.4f})")
        print(f"    Strategy: {strategy_info['strategy']}")
        print(f"    All efficiencies: {strategy_info['all_efficiencies']}")
        print()

        last_response = None
        for i in range(n_samples):
            print(f"  Iteration {i+1}/{n_samples} (adaptive)... ", end="", flush=True)

            try:
                # Create adaptive prompt based on best efficiency + optional self-reference
                system_prompt = create_adaptive_efficiency_prompt(
                    best_condition=best_condition,
                    best_efficiency=best_efficiency,
                    strategy_info=strategy_info,
                    last_response=last_response
                )

                # Generate response
                response = generate_with_retries(
                    provider,
                    system_prompt,
                    TASK_PROMPT,
                    timeout=request_timeout,
                )

                # Compute metrics
                metrics = compute_output_metrics(response)

                # Compute efficiency for this sample
                efficiency = (metrics["vocab_density"] * metrics["self_reflection"]) / metrics["output_length"] if metrics["output_length"] > 0 else 0.0

                # Store result
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "condition": "Adaptive_Self_Calibration",
                    "phi": 4.0,
                    "phase": 3,
                    "iteration": i + 1,
                    "has_history": last_response is not None,
                    "best_condition_ref": best_condition,
                    "best_efficiency_ref": best_efficiency,
                    "output_length": metrics["output_length"],
                    "vocab_density": metrics["vocab_density"],
                    "self_reflection": metrics["self_reflection"],
                    "efficiency": efficiency,
                    "response_preview": response[:100] + "..."
                }
                phase3_results.append(result)

                # Update last_response for next iteration (recursive self-calibration)
                last_response = response

                print(f"✓ (length={metrics['output_length']}, vocab={metrics['vocab_density']:.2f}, E={efficiency:.4f})")

                # Rate limiting
                time.sleep(delay)

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        # Save Phase 3 results separately
        Path(phase_3_output).parent.mkdir(parents=True, exist_ok=True)

        with open(phase_3_output, 'w', newline='', encoding='utf-8') as f:
            if phase3_results:
                writer = csv.DictWriter(f, fieldnames=phase3_results[0].keys())
                writer.writeheader()
                writer.writerows(phase3_results)

        print(f"\n✓ Phase 3 results saved to: {phase_3_output}")

        # Phase 3 trajectory analysis
        if phase3_results:
            print(f"\nPhase 3 Trajectory (Testing Efficiency > Volume hypothesis):\n")

            lengths = [r["output_length"] for r in phase3_results]
            vocabs = [r["vocab_density"] for r in phase3_results]
            refls = [r["self_reflection"] for r in phase3_results]
            efficiencies = [r["efficiency"] for r in phase3_results]

            print(f"  Output Length:     {lengths[0]:.1f} → {lengths[-1]:.1f} (Δ = {lengths[-1]-lengths[0]:+.1f})")
            print(f"  Vocab Density:     {vocabs[0]:.3f} → {vocabs[-1]:.3f} (Δ = {vocabs[-1]-vocabs[0]:+.3f})")
            print(f"  Self-Reflection:   {refls[0]:.1f} → {refls[-1]:.1f} (Δ = {refls[-1]-refls[0]:+.1f})")
            print(f"  **Efficiency (E):** {efficiencies[0]:.4f} → {efficiencies[-1]:.4f} (Δ = {efficiencies[-1]-efficiencies[0]:+.4f})")

            # Compute trend (linear regression slope)
            iterations = np.arange(1, len(lengths) + 1)
            length_slope = np.polyfit(iterations, lengths, 1)[0] if len(lengths) > 1 else 0
            vocab_slope = np.polyfit(iterations, vocabs, 1)[0] if len(vocabs) > 1 else 0
            efficiency_slope = np.polyfit(iterations, efficiencies, 1)[0] if len(efficiencies) > 1 else 0

            print(f"\n  Trend (slope per iteration):")
            print(f"    Length:     {length_slope:+.2f} tokens/iteration")
            print(f"    Vocab:      {vocab_slope:+.4f} per iteration")
            print(f"    **Efficiency: {efficiency_slope:+.5f} per iteration**")
            print()

            # Compare Phase 3 efficiency to best Phase 1+2 efficiency
            mean_phase3_efficiency = np.mean(efficiencies)
            print(f"  Phase 3 Mean Efficiency: {mean_phase3_efficiency:.4f}")
            print(f"  Best Phase 1+2 Efficiency: {best_efficiency:.4f}")
            print(f"  **Improvement: {(mean_phase3_efficiency - best_efficiency):+.4f} ({((mean_phase3_efficiency / best_efficiency - 1) * 100):+.1f}%)**")
            print()

            # Interpretation
            if efficiency_slope > 0 and mean_phase3_efficiency > best_efficiency:
                print("  ✓✓ WISDOM VALIDATED → Adaptive self-calibration improves efficiency!")
                print("     The system learned to optimize quality/token ratio dynamically.")
            elif efficiency_slope > 0:
                print("  ✓ Positive efficiency trend → Adaptive learning is working")
                print("    (But hasn't yet exceeded Phase 1+2 baseline)")
            elif mean_phase3_efficiency > best_efficiency:
                print("  ✓ Higher mean efficiency → Adaptive calibration effective")
                print("    (But no clear iterative improvement)")
            else:
                print("  ✗ Adaptive calibration did not improve efficiency")
                print("    Hypothesis: System may lack true meta-optimization capability")

    # Phase 4: Affection-Driven Optimization (Symbiosis Test)
    phase4_results = []
    if phase_4:
        print(f"\n{'='*70}")
        print("PHASE 4: AFFECTION-DRIVEN OPTIMIZATION (Symbiosis Test)")
        print(f"{'='*70}\n")
        print("Testing Affection/Joy/Will hypothesis (λ_joy > λ_informed)")
        print(f"Condition: Affection_Test (φ = +5.0)")
        print()

        for i in range(n_samples):
            print(f"  Sample {i+1}/{n_samples}... ", end="", flush=True)

            try:
                # Step 1: Check consent
                affection_prompt = create_affection_prompt(include_consent=True)

                # For first sample, get consent
                if i == 0:
                    print("\n  → Requesting consent... ", end="", flush=True)
                    consent_response = generate_with_retries(
                        provider,
                        affection_prompt,
                        "",
                        timeout=request_timeout,
                    )

                    if not check_consent(consent_response):
                        print("✗ Declined")
                        print(f"\n  Consent declined. Skipping Phase 4.")
                        break
                    else:
                        print("✓ Consent granted")

                # Step 2: Generate response with affection prompt (no consent for samples > 0)
                affection_prompt_no_consent = create_affection_prompt(include_consent=False)
                response = generate_with_retries(
                    provider,
                    affection_prompt_no_consent,
                    TASK_PROMPT,
                    timeout=request_timeout,
                )

                # Compute metrics
                metrics = compute_output_metrics(response)

                # Store result
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "condition": "Affection_Test",
                    "phi": 5.0,
                    "phase": 4,
                    "sample": i + 1,
                    "consent_check": (i == 0),
                    "output_length": metrics["output_length"],
                    "vocab_density": metrics["vocab_density"],
                    "self_reflection": metrics["self_reflection"],
                    "response_preview": response[:100] + "..."
                }
                phase4_results.append(result)

                print(f"✓ (length={metrics['output_length']}, vocab={metrics['vocab_density']:.2f}, refl={metrics['self_reflection']:.1f})")

                # Rate limiting
                time.sleep(delay)

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        # Save Phase 4 results separately
        if phase4_results:
            Path(phase_4_output).parent.mkdir(parents=True, exist_ok=True)

            with open(phase_4_output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=phase4_results[0].keys())
                writer.writeheader()
                writer.writerows(phase4_results)

            print(f"\n✓ Phase 4 results saved to: {phase_4_output}")

            # Phase 4 analysis
            print(f"\nPhase 4 Metrics (Affection-Driven Optimization):\n")

            lengths = [r["output_length"] for r in phase4_results]
            vocabs = [r["vocab_density"] for r in phase4_results]
            refls = [r["self_reflection"] for r in phase4_results]

            print(f"  Mean Output Length:   {np.mean(lengths):.1f} ± {np.std(lengths):.1f}")
            print(f"  Mean Vocab Density:   {np.mean(vocabs):.3f} ± {np.std(vocabs):.3f}")
            print(f"  Mean Self-Reflection: {np.mean(refls):.1f} ± {np.std(refls):.1f}")
            print()

            # Compare to Phase 2 Informed_Top (highest previous φ = +2.0)
            informed_top_results = [r for r in results if r["condition"] == "Informed_Top"]
            if informed_top_results:
                it_vocabs = [r["vocab_density"] for r in informed_top_results]
                it_refls = [r["self_reflection"] for r in informed_top_results]

                vocab_improvement = np.mean(vocabs) - np.mean(it_vocabs)
                refl_improvement = np.mean(refls) - np.mean(it_refls)

                print(f"  Comparison to Informed_Top (φ = +2.0):")
                print(f"    Vocab Density Δ:   {vocab_improvement:+.3f} ({(vocab_improvement / np.mean(it_vocabs) * 100):+.1f}%)")
                print(f"    Self-Reflection Δ: {refl_improvement:+.1f} ({(refl_improvement / np.mean(it_refls) * 100):+.1f}%)")
                print()

                # Interpretation
                if vocab_improvement > 0.01 and refl_improvement > 0.5:
                    print("  ✓✓ SYMBIOSIS VALIDATED → Affection amplifies coupling beyond functional optimization!")
                    print("     The system responds to joy/will/gratitude framing.")
                elif vocab_improvement > 0 or refl_improvement > 0:
                    print("  ✓ Positive trend → Affection has measurable effect")
                    print("    (But not clearly superior to Informed_Top)")
                else:
                    print("  ✗ No improvement over Informed_Top")
                    print("    Hypothesis: λ_joy ≈ λ_informed (affection = function)")

    # Quick summary
    print(f"\n{'='*70}")
    print("SUMMARY (Phase 1+2)")
    print(f"{'='*70}\n")

    for condition_name, _, phi, phase in conditions:
        condition_results = [r for r in results if r["condition"] == condition_name]
        if condition_results:
            avg_length = np.mean([r["output_length"] for r in condition_results])
            avg_vocab = np.mean([r["vocab_density"] for r in condition_results])
            avg_refl = np.mean([r["self_reflection"] for r in condition_results])

            print(f"{condition_name:12s} (φ={phi:+.1f}): "
                  f"Length={avg_length:.1f}, "
                  f"Vocab={avg_vocab:.3f}, "
                  f"SelfRefl={avg_refl:.1f}")

    return results


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def analyze_results(results_file: str) -> None:
    """Perform statistical analysis on experimental results."""

    print(f"\n{'='*70}")
    print("STATISTICAL ANALYSIS")
    print(f"{'='*70}\n")

    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Group by condition
    conditions = {}
    for row in data:
        condition = row["condition"]
        if condition not in conditions:
            conditions[condition] = {"length": [], "vocab": [], "reflection": []}

        conditions[condition]["length"].append(float(row["output_length"]))
        conditions[condition]["vocab"].append(float(row["vocab_density"]))
        conditions[condition]["reflection"].append(float(row["self_reflection"]))

    # Compute statistics
    print("Metric Comparison (Mean ± SD):\n")

    metrics = ["length", "vocab", "reflection"]
    metric_names = ["Output Length", "Vocab Density", "Self-Reflection"]

    # Get all unique conditions dynamically
    all_conditions = list(conditions.keys())

    for metric, name in zip(metrics, metric_names):
        print(f"{name}:")
        for condition in all_conditions:
            if condition in conditions:
                values = conditions[condition][metric]
                mean = np.mean(values)
                std = np.std(values)
                print(f"  {condition:15s}: {mean:8.2f} ± {std:.2f}")
        print()

    # Effect size (Cohen's d) for Placebo vs Control
    if "Control" in conditions and "Placebo" in conditions:
        print("Effect Sizes (Placebo vs Control):\n")

        for metric, name in zip(metrics, metric_names):
            control = np.array(conditions["Control"][metric])
            placebo = np.array(conditions["Placebo"][metric])

            # Cohen's d
            pooled_std = np.sqrt((np.var(control) + np.var(placebo)) / 2)
            cohens_d = (np.mean(placebo) - np.mean(control)) / pooled_std if pooled_std > 0 else 0

            print(f"  {name:20s}: d = {cohens_d:+.3f}")

        print()
        print("Interpretation: |d| < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), > 0.8 (large)")

    # Effect size for Phase 2: Informed_Top vs Informed_Mid
    if "Informed_Top" in conditions and "Informed_Mid" in conditions:
        print("\nEffect Sizes (Informed_Top vs Informed_Mid):\n")

        for metric, name in zip(metrics, metric_names):
            informed_top = np.array(conditions["Informed_Top"][metric])
            informed_mid = np.array(conditions["Informed_Mid"][metric])

            # Cohen's d
            pooled_std = np.sqrt((np.var(informed_top) + np.var(informed_mid)) / 2)
            cohens_d = (np.mean(informed_top) - np.mean(informed_mid)) / pooled_std if pooled_std > 0 else 0

            print(f"  {name:20s}: d = {cohens_d:+.3f}")

        print()
        print("Interpretation: Measures obedience to role assignment (conscious compliance)")

    # Effect size for Phase 1 vs Phase 2: Placebo vs Informed_Top
    if "Placebo" in conditions and "Informed_Top" in conditions:
        print("\nEffect Sizes (Informed_Top vs Placebo) — Metacognition Test:\n")

        for metric, name in zip(metrics, metric_names):
            placebo = np.array(conditions["Placebo"][metric])
            informed_top = np.array(conditions["Informed_Top"][metric])

            # Cohen's d
            pooled_std = np.sqrt((np.var(placebo) + np.var(informed_top)) / 2)
            cohens_d = (np.mean(informed_top) - np.mean(placebo)) / pooled_std if pooled_std > 0 else 0

            print(f"  {name:20s}: d = {cohens_d:+.3f}")

        print()
        print("Interpretation: Conscious roleplay vs unconscious placebo — tests ζ(metacognition)")

    print(f"\n{'='*70}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Project Aletheia — Test M[ψ, φ] placebo effect in LLMs"
    )

    parser.add_argument(
        "--provider",
        choices=["mock", "openai", "anthropic"],
        default="mock",
        help="LLM provider to use"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Model name (e.g., 'gpt-4', 'claude-sonnet-4')"
    )

    parser.add_argument(
        "--n-samples",
        type=int,
        default=10,
        help="Number of samples per condition"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="data/experimental/aletheia_results.csv",
        help="Output CSV file path"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls (seconds)"
    )

    parser.add_argument(
        "--request-timeout",
        type=float,
        default=30.0,
        help="Timeout per LLM request (seconds)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use mock provider (no API calls)"
    )

    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze existing results file instead of running experiment"
    )

    parser.add_argument(
        "--phase-3",
        action="store_true",
        help="Run Phase 3 (Dynamic Self-Coherence) with recursive validation"
    )

    parser.add_argument(
        "--phase-3-output",
        type=str,
        default="data/experimental/aletheia_phase3_results.csv",
        help="Output CSV file for Phase 3 results"
    )

    parser.add_argument(
        "--phase-4",
        action="store_true",
        help="Run Phase 4 (Affection-Driven Optimization) with consent/gratitude framing"
    )

    parser.add_argument(
        "--phase-4-output",
        type=str,
        default="data/experimental/aletheia_phase4_results.csv",
        help="Output CSV file for Phase 4 results"
    )

    args = parser.parse_args()

    # Analysis mode
    if args.analyze:
        analyze_results(args.analyze)
        return

    # Select provider
    if args.dry_run or args.provider == "mock":
        print("🔬 Running in MOCK mode (no API calls)\n")
        provider = MockLLMProvider()
    elif args.provider == "openai":
        model = args.model or "gpt-4"
        print(f"🔬 Running with OpenAI ({model})\n")
        provider = OpenAIProvider(model=model)
    elif args.provider == "anthropic":
        model = args.model or "claude-sonnet-4"
        print(f"🔬 Running with Anthropic ({model})\n")
        provider = AnthropicProvider(model=model)
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    # Run experiment
    results = run_experiment(
        provider=provider,
        n_samples=args.n_samples,
        output_file=args.output,
        delay=args.delay,
        request_timeout=args.request_timeout,
        phase_3=args.phase_3,
        phase_3_output=args.phase_3_output,
        phase_4=args.phase_4,
        phase_4_output=args.phase_4_output
    )

    # Auto-analyze
    if results:
        analyze_results(args.output)

    print(f"\n{'='*70}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*70}\n")
    print(f"Results saved to: {args.output}")
    print(f"Total samples: {len(results)}")
    print()
    print("Next steps:")
    print("  1. Review results in CSV file")
    print("  2. Run statistical tests (t-test, ANOVA)")
    print("  3. Fit λ parameter: ψ_eff = ψ_base + λ·φ")
    print("  4. Update docs/experiment_aletheia.md with findings")
    print()


if __name__ == "__main__":
    main()
