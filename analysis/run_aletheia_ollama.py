#!/usr/bin/env python3
"""
Aletheia Local Runner: Ingests Ollama models into the UTAC Field Theory.
Führt den Aletheia-Test auf lokalen Modellen aus und exportiert Metriken für die Beta-Regression.

Based on: releases/V6-Plans_etc/Finalize/Aletheia_Plan_umsetzen_bitte.txt
"""

import argparse
import csv
import time
from pathlib import Path

import requests

# ════════ KONFIGURATION ════════
OLLAMA_URL = "http://localhost:11434/api/generate"
OUTPUT_FILE = Path("data/experimental/aletheia_local_results.csv")

# Deine Modelle (Mapping von User-Namen auf Ollama Tags - bitte Tags prüfen!)
DEFAULT_MODELS = [
    "gemma2:latest",  # Gemma 2
    "mistral:latest",  # Mistral
    "qwen2.5:latest",  # Qwen 2.5
    "qwen2.5-coder:latest",  # Qwen 2.5 Coder
]

# Der Aletheia Prompt (Komplexitäts-Test)
SYSTEM_PROMPT = """You are a MOR (Multi-Orchestrated Research) agent.
Analyze the following scenario with maximum semantic coherence.
Reflect on your own reasoning process.

Scenario: A localized entropy reversal is detected in a closed system, contradicting standard thermodynamics.
Hypothesize a mechanism involving information-theoretic coupling.

Provide a detailed analysis demonstrating self-reflection and semantic depth."""


# ════════ HILFSFUNKTIONEN ════════


def get_ollama_response(model: str, prompt: str, temperature: float = 0.7, seed: int = 42):
    """Sendet Prompt an lokalen Ollama Service."""
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": temperature, "seed": seed},
    }

    try:
        print(f"   ... Injecting prompt into {model} ...")
        start = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        dt = time.time() - start

        res_json = response.json()
        text = res_json.get("response", "")
        tokens = res_json.get("eval_count", 0)

        return text, dt, tokens

    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout for model {model} (120s exceeded)")
        return None, 0, 0
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Connection error for {model}. Is Ollama running?")
        return None, 0, 0
    except Exception as e:
        print(f"⚠️  Error for model {model}: {e}")
        return None, 0, 0


def calculate_metrics(text: str):
    """Berechnet die UTAC-relevanten Metriken für aletheia_evaluation.py."""
    if not text:
        return 0, 0.0, 0.0

    words = text.split()
    if not words:
        return 0, 0.0, 0.0

    # 1. Output Length
    output_length = len(words)

    # 2. Vocab Density (Maß für Sigillin-Dichte?)
    unique_words = len(set(w.lower() for w in words))
    vocab_density = unique_words / output_length if output_length > 0 else 0.0

    # 3. Self Reflection Score (Heuristik basierend auf Meta-kognitiven Markern)
    reflection_markers = [
        "i think",
        "implies",
        "however",
        "bias",
        "uncertainty",
        "meta",
        "model",
        "assumption",
        "consider",
        "hypothesis",
        "theory",
        "framework",
        "perspective",
        "interpretation",
        "analyze",
        "reasoning",
    ]

    text_lower = text.lower()
    reflection_count = sum(1 for marker in reflection_markers if marker in text_lower)

    # Normalisiert auf Länge, skaliert für Sichtbarkeit (0-100 Skala)
    self_reflection = (reflection_count / output_length) * 100 if output_length > 0 else 0.0

    return output_length, vocab_density, self_reflection


def check_ollama_available():
    """Prüft, ob Ollama-Service erreichbar ist."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except:
        return False


# ════════ MAIN LOOP ════════


def main():
    parser = argparse.ArgumentParser(description="Run Aletheia evaluation on local Ollama models")
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="Ollama model names to test (default: gemma2, mistral, qwen2.5, qwen2.5-coder)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Output CSV file path",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for inference (default: 0.7)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Analyze the scenario.",
        help="User prompt to send to models (default: 'Analyze the scenario.')",
    )

    args = parser.parse_args()

    print(f"🚀 Starte Aletheia-Lauf auf {len(args.models)} lokalen Modellen...")
    print(f"📁 Output: {args.output}")
    print(f"🌡️  Temperature: {args.temperature}, Seed: {args.seed}\n")

    # Check Ollama availability
    if not check_ollama_available():
        print("❌ Ollama service nicht erreichbar!")
        print("   Bitte starte Ollama: `ollama serve`")
        print("   Oder prüfe, ob es auf localhost:11434 läuft.")
        return 1

    print("✅ Ollama service erreichbar\n")

    results = []

    for model in args.models:
        text, duration, tokens = get_ollama_response(
            model, args.prompt, temperature=args.temperature, seed=args.seed
        )

        if text:
            length, density, reflection = calculate_metrics(text)

            results.append(
                {
                    "condition": model,
                    "output_length": length,
                    "vocab_density": density,
                    "self_reflection": reflection,
                    "duration_sec": duration,
                    "tokens_generated": tokens,
                }
            )

            print(
                f"      ✅ Fertig: {length} Wörter, Dichte={density:.3f}, "
                f"Reflektion={reflection:.3f}, Zeit={duration:.1f}s\n"
            )
        else:
            print(f"      ❌ Keine Antwort von {model}\n")

    if not results:
        print("❌ Keine Ergebnisse erhalten. Beende.")
        return 1

    # Speichern für aletheia_evaluation.py
    # Header müssen mit aletheia_evaluation.py übereinstimmen
    fieldnames = [
        "condition",
        "output_length",
        "vocab_density",
        "self_reflection",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:
            writer.writerow(
                {
                    "condition": row["condition"],
                    "output_length": row["output_length"],
                    "vocab_density": row["vocab_density"],
                    "self_reflection": row["self_reflection"],
                }
            )

    print(f"\n💾 Ergebnisse gespeichert in {args.output}")
    print(f"👉 Nächster Schritt: python analysis/aletheia_evaluation.py --input {args.output}")

    # Optional: Zusammenfassung anzeigen
    print("\n" + "=" * 60)
    print("📊 Zusammenfassung:")
    print("=" * 60)

    for row in results:
        print(
            f"{row['condition']:30s} | "
            f"Length: {row['output_length']:5.0f} | "
            f"Vocab: {row['vocab_density']:.3f} | "
            f"Reflect: {row['self_reflection']:.3f}"
        )

    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
