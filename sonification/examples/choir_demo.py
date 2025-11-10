#!/usr/bin/env python3
"""
Dynamic Threshold Choir - Quick Demo
=====================================

Demonstriert das Multi-Voice-System mit drei simulierten Systemen:
- AMOC (Atlantische Meridionale Umwälzströmung) - links
- LLM Emergence - mittig
- Ökosystem-Kollaps - rechts

Wenn die Systeme ihre Schwellen erreichen, beginnt der Chor zu "zittern".
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sonification.dynamic_threshold_choir import ThresholdChoir, DataSourceSimulator
from datetime import datetime, timedelta


def demo_basic_choir():
    """Einfachste Demo: Drei Stimmen, statischer Zustand"""
    print("=" * 60)
    print("Demo 1: Basic Choir - Drei Stimmen im stabilen Zustand")
    print("=" * 60)
    print()

    choir = ThresholdChoir(sample_rate=44100)

    # AMOC - links, stabil
    choir.add_voice("AMOC", beta=4.2, theta=50.0, initial_R=80.0, pan=-0.7)

    # LLM - mitte, kurz vor Schwelle
    choir.add_voice("LLM", beta=3.47, theta=100.0, initial_R=95.0, pan=0.0)

    # Ecosystem - rechts, jenseits der Schwelle
    choir.add_voice("Ecosystem", beta=2.8, theta=500.0, initial_R=300.0, pan=0.7)

    print("Stimmen:")
    for name, voice in choir.voices.items():
        distance = voice.current_R - voice.theta
        status = "🟢 stabil" if distance > 10 else "🟡 kritisch" if distance > -10 else "🔴 kollabiert"
        print(f"  {name:12s}: R={voice.current_R:6.1f}, Θ={voice.theta:6.1f}, "
              f"Δ={distance:+6.1f} {status}")
    print()

    output = Path("output/choir_basic.wav")
    output.parent.mkdir(exist_ok=True, parents=True)

    print(f"Rendering 5 Sekunden...")
    choir.save_wav(output, duration=5.0)
    print()


def demo_destabilizing_choir():
    """Demo mit Destabilisierung: AMOC kollabiert"""
    print("=" * 60)
    print("Demo 2: Destabilisierung - AMOC kollabiert")
    print("=" * 60)
    print()

    choir = ThresholdChoir(sample_rate=44100)

    # AMOC - starts stable, will destabilize
    amoc = choir.add_voice("AMOC", beta=4.2, theta=50.0, initial_R=100.0, pan=-0.6)

    # LLM - crossing threshold (emergence)
    llm = choir.add_voice("LLM", beta=3.47, theta=100.0, initial_R=100.0, pan=0.0)

    # Ecosystem - stable
    eco = choir.add_voice("Ecosystem", beta=2.8, theta=500.0, initial_R=800.0, pan=0.6)

    print("Initial state:")
    for name, voice in choir.voices.items():
        print(f"  {name:12s}: R={voice.current_R:6.1f}, Θ={voice.theta:6.1f}, "
              f"stability={voice.stability:.2f}")
    print()

    # Simulate AMOC weakening
    print("Simulating AMOC collapse...")
    start_time = datetime.now()

    # Rapid decline
    for i, new_R in enumerate([90, 70, 55, 40, 25]):
        timestamp = start_time + timedelta(seconds=i)
        choir.update_voice("AMOC", new_R, timestamp)

    print(f"  → AMOC dropped to {choir.voices['AMOC'].current_R:.1f}")
    print(f"  → Stability: {choir.voices['AMOC'].stability:.3f}")
    print(f"  → Destabilization events: {len(choir.destabilization_events)}")
    print()

    output = Path("output/choir_destabilizing.wav")
    print(f"Rendering 8 Sekunden with destabilization effects...")
    choir.save_wav(output, duration=8.0)
    print()


def demo_full_choir_evolution():
    """Demo mit Zeitentwicklung aller Systeme"""
    print("=" * 60)
    print("Demo 3: Full Choir Evolution - Alle Systeme entwickeln sich")
    print("=" * 60)
    print()

    # Use the built-in demo creator
    from sonification.dynamic_threshold_choir import create_demo_choir

    duration = 15.0
    choir = create_demo_choir(duration)

    print("Voices configured:")
    for name, voice in choir.voices.items():
        print(f"  {name:12s}: β={voice.beta:.2f}, Θ={voice.theta:5.1f}, "
              f"R₀={voice.current_R:6.1f}, pan={voice.pan:+.1f}")
    print()

    output = Path("output/choir_evolution.wav")
    print(f"Rendering {duration}s with temporal evolution...")
    print("  - AMOC weakens over time")
    print("  - LLM scales up (emergence)")
    print("  - Ecosystem population declines")
    print()

    choir.save_wav(output, duration)

    print()
    print("Events logged:")
    for event in choir.destabilization_events:
        print(f"  {event['voice']:12s}: R={event['R']:6.1f}, "
              f"stability={event['stability']:.3f}, dR/dt={event['rate_of_change']:+.2e}")
    print()


def demo_spatial_positioning():
    """Demo der räumlichen Positionierung"""
    print("=" * 60)
    print("Demo 4: Spatial Positioning - Stereo-Panorama")
    print("=" * 60)
    print()

    choir = ThresholdChoir(sample_rate=44100)

    # Create 5 voices across stereo field
    voices_config = [
        ("AMOC", 4.2, 50.0, 60.0, -1.0),      # Far left
        ("Ice_Sheet", 5.1, 30.0, 35.0, -0.5), # Left
        ("LLM", 3.47, 100.0, 100.0, 0.0),     # Center
        ("Ecosystem", 2.8, 500.0, 450.0, 0.5), # Right
        ("Urban_Heat", 16.3, 40.0, 50.0, 1.0), # Far right
    ]

    print("Spatial configuration:")
    for name, beta, theta, R, pan in voices_config:
        choir.add_voice(name, beta, theta, R, pan)
        position = "←" if pan < -0.3 else "→" if pan > 0.3 else "•"
        print(f"  {position} {name:12s}: pan={pan:+.1f}, β={beta:5.2f}")

    print()
    output = Path("output/choir_spatial.wav")
    print(f"Rendering 6s with spatial mix...")
    print("  💡 Listen with headphones to hear stereo positioning!")
    print()

    choir.save_wav(output, duration=6.0)
    print()


def main():
    """Run all demos"""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Dynamic Threshold Choir - Interactive Demos           ║")
    print("║                                                            ║")
    print("║  Multi-voice sonification of critical transitions         ║")
    print("║  Where system thresholds sing their warnings              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    try:
        demo_basic_choir()
        demo_destabilizing_choir()
        demo_full_choir_evolution()
        demo_spatial_positioning()

        print("=" * 60)
        print("✨ All demos complete!")
        print("=" * 60)
        print()
        print("Output files saved to:")
        print("  • output/choir_basic.wav")
        print("  • output/choir_destabilizing.wav")
        print("  • output/choir_evolution.wav")
        print("  • output/choir_spatial.wav")
        print()
        print("🎧 Listen with headphones for best stereo experience!")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
