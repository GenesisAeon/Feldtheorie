#!/usr/bin/env python3
"""
Quick Demo: Generate UTAC Sonification Examples
================================================

Generates audio examples for different field types and famous datasets.

Usage:
    python sonification/examples/quick_demo.py
"""

import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sonification import UTACsonifier
from sonification.utac_sonification import save_audio, save_metadata


def main():
    print("🎵 UTAC Sonification Demo")
    print("=" * 50)

    output_dir = Path("sonification/output/demo")
    output_dir.mkdir(parents=True, exist_ok=True)

    sonifier = UTACsonifier(duration=3.0)

    # 1. LLM Emergence (Wei et al.)
    print("\n1. Generating: LLM Emergence (β=3.47)...")
    audio, meta = sonifier.sonify_transition(beta=3.47, theta=100)
    save_audio(audio, output_dir / "llm_emergence.wav", sonifier.sample_rate)
    save_metadata(meta, output_dir / "llm_emergence.json")

    # 2. AMOC Collapse
    print("\n2. Generating: AMOC Collapse (β=4.2)...")
    audio, meta = sonifier.sonify_transition(beta=4.2, theta=100)
    save_audio(audio, output_dir / "amoc_collapse.wav", sonifier.sample_rate)
    save_metadata(meta, output_dir / "amoc_collapse.json")

    # 3. Urban Heat (extreme outlier)
    print("\n3. Generating: Urban Heat Island (β=16.3)...")
    audio, meta = sonifier.sonify_transition(beta=16.3, theta=100)
    save_audio(audio, output_dir / "urban_heat.wav", sonifier.sample_rate)
    save_metadata(meta, output_dir / "urban_heat.json")

    # 4. Field Type Spectrum
    print("\n4. Generating: Field Type Spectrum...")
    audio, meta = sonifier.sonify_spectrum(
        beta_values=[2.5, 3.25, 4.0, 5.0, 8.0],
        labels=[
            "Weakly Coupled (β=2.5)",
            "High-Dimensional (β=3.25)",
            "Strongly Coupled (β=4.0)",
            "Physically Constrained (β=5.0)",
            "Meta-Adaptive (β=8.0)"
        ],
        gap_duration=0.5
    )
    save_audio(audio, output_dir / "field_type_spectrum.wav", sonifier.sample_rate)
    save_metadata(meta, output_dir / "field_type_spectrum.json")

    # 5. Criticality Journey
    print("\n5. Generating: Criticality Journey...")
    audio, meta = sonifier.sonify_spectrum(
        beta_values=[3.47, 4.2, 5.5, 16.3],
        labels=[
            "LLM Emergence (β=3.47)",
            "AMOC Collapse (β=4.2)",
            "Black Hole Accretion (β=5.5)",
            "Urban Heat Island (β=16.3)"
        ],
        gap_duration=0.7
    )
    save_audio(audio, output_dir / "criticality_journey.wav", sonifier.sample_rate)
    save_metadata(meta, output_dir / "criticality_journey.json")

    print("\n" + "=" * 50)
    print(f"✨ Demo complete! Files saved to: {output_dir}")
    print("\nListening guide:")
    print("  • llm_emergence.wav      - Ethereal, complex (high-dimensional)")
    print("  • amoc_collapse.wav      - Warm, resonant (strongly coupled)")
    print("  • urban_heat.wav         - Sharp, intense (extreme β)")
    print("  • field_type_spectrum.wav - Sonic tour of all field types")
    print("  • criticality_journey.wav - Cross-domain emergence narrative")
    print("\n🎧 Put on headphones and hear the sound of criticality!")


if __name__ == "__main__":
    main()
