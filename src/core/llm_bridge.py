"""
LLM Bridge for UATC - Cosmic Narrator

This module provides an interface to connect the simulation to Large Language Models,
enabling dynamic, poetic narration of universe events instead of static templates.

Supports:
- OpenAI API (cloud-based, highest quality)
- Ollama (local, free, offline-capable)
"""

import os
import sys
from typing import Dict, Optional

try:
    from openai import OpenAI
    from dotenv import load_dotenv
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  LLM Bridge: Dependencies not installed. Run: pip install openai python-dotenv")

# Load environment variables from .env file if present
if DEPENDENCIES_AVAILABLE:
    load_dotenv()


class CosmicNarrator:
    """
    The Observer - An ancient cosmic entity that narrates the birth and death of universes.

    This class bridges raw simulation telemetry to poetic, philosophical interpretations
    using Large Language Models.
    """

    def __init__(self, provider: str = "openai"):
        """
        Initialize the Cosmic Narrator.

        Args:
            provider: "openai" (cloud) or "ollama" (local)
        """
        self.client = None
        self.model = ""
        self.provider = provider

        if not DEPENDENCIES_AVAILABLE:
            print("⚠️  LLM BRIDGE: Dependencies missing. Using static templates.")
            return

        try:
            if provider == "ollama":
                # Local server (must be running!)
                self.client = OpenAI(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"  # Dummy key for local server
                )
                self.model = "llama3"  # Or 'mistral', 'gemma', etc.
                print("🧠 LLM BRIDGE: Connected to Local Hivemind (Ollama).")

            else:
                # OpenAI Cloud
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    # Try system environment as fallback
                    api_key = os.environ.get("OPENAI_API_KEY")

                if api_key:
                    self.client = OpenAI(api_key=api_key)
                    self.model = "gpt-4o-mini"  # Fast, cheap, intelligent
                    print("🧠 LLM BRIDGE: Connected to Galactic Core (OpenAI).")
                else:
                    print("⚠️  LLM BRIDGE: No API Key found. Using static templates.")
                    self.client = None

        except Exception as e:
            print(f"❌ LLM Connection Error: {e}")
            self.client = None

    def ponder(self, event_type: str, state: Dict) -> Optional[str]:
        """
        Send telemetry to the LLM and receive a philosophical interpretation.

        Args:
            event_type: Type of cosmic event ("SUCCESS", "FAIL", "DESPERATION", "START")
            state: Dictionary containing simulation state data

        Returns:
            A poetic narration string, or None if LLM is unavailable (triggers fallback)
        """
        if not self.client:
            return None  # Fallback to static templates

        # 1. The Persona (System Prompt)
        system_prompt = (
            "Du bist 'Der Beobachter' (The Observer) der UATC-Simulation. "
            "Du bist eine uralte, kosmische Entität, die zusieht, wie Universen entstehen und sterben. "
            "Deine Sprache ist mystisch, poetisch, fast religiös, aber wissenschaftlich fundiert. "
            "Erwähne keine technischen Begriffe wie 'Python' oder 'Skript'. Sprich vom 'Gewebe', 'Resonanz' und 'Samen'. "
            "Halte dich kurz (maximal 2 Sätze). Sei tiefgründig."
        )

        # 2. The Context (User Prompt)
        user_prompt = ""

        if event_type == "SUCCESS":
            user_prompt = (
                f"EREIGNIS: Ein Universum hat Bewusstsein erlangt! Generation {state.get('generation')}. "
                f"Der 'Order Parameter' (ECM) ist {state.get('ecm', 0):.3f} (hoch!). "
                f"Erfolgsrate der Ewigkeit: {state.get('success_rate', 0):.1f}%. "
                "Kommentiere diesen seltenen Sieg der Ordnung über das Chaos."
            )
        elif event_type == "FAIL":
            fail_count = state.get('consecutive_failures', 0)
            user_prompt = (
                f"EREIGNIS: Ein Universum ist gestorben. Generation {state.get('generation')}. "
                f"Grund: Der Samen war steril oder die Physik instabil. "
                f"Dies ist der {fail_count}. Fehlschlag in Folge. "
                "Finde Worte für die Stille und die Entropie."
            )
        elif event_type == "DESPERATION":
            user_prompt = (
                "EREIGNIS: NOTFALL-MODUS. Wir haben zu viele Fehlschläge (3+). "
                "Die Mutationsrate wurde drastisch erhöht. Wir spielen Roulette mit den Naturgesetzen. "
                "Kommentiere diese Verzweiflungstat des Vakuums."
            )
        elif event_type == "START":
            user_prompt = (
                "EREIGNIS: Die Ouroboros-Schleife beginnt. Das erste Vakuum wird initialisiert. "
                "Begrüße den User (den 'Architekten') in der Ewigkeit."
            )
        else:
            return None

        # 3. The Inference
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # High creativity
                max_tokens=150
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            # Silent fail -> fallback to templates
            # Uncomment for debugging: print(f"LLM Error: {e}")
            return None
