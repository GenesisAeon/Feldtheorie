"""Geophysical structures and planetary body dynamics.

This module provides base classes for planetary bodies with layered structures
that can interact with extreme astrophysical phenomena.
"""
from __future__ import annotations


class PlanetaryBody:
    """Base class for celestial bodies with compositional layers.

    Attributes
    ----------
    name : str
        Identifier for this planetary body.
    layers : List[Dict]
        Stack of compositional layers from core (index 0) to surface (index -1).
        Each layer contains: {'name': str, 'comp': str, 'mass': float}
    stripped_mass : float
        Total mass that has been ablated from this body.
    """

    def __init__(self, name: str = "Unnamed Body"):
        self.name = name
        self.layers: list[dict] = []
        self.stripped_mass: float = 0.0

    def visualize_layers(self) -> None:
        """Print a visual representation of current layer structure."""

        print(f"\n🌍 {self.name} — Layered Structure:")
        print("-" * 50)

        if not self.layers:
            print("   ❌ No layers remaining (complete destruction)")
            return

        # Display from outermost to innermost
        for i, layer in enumerate(reversed(self.layers)):
            depth_marker = "  " * i
            emoji = self._layer_emoji(layer['comp'])
            print(
                f"{depth_marker}{emoji} {layer['name']:20s} | "
                f"{layer['comp']:12s} | Mass: {layer['mass']:8.1f}"
            )

        print("-" * 50)
        print(f"Total stripped mass: {self.stripped_mass:.1f}")

    def _layer_emoji(self, composition: str) -> str:
        """Return emoji representation based on layer composition."""

        emoji_map = {
            'DIAMOND': '💎',
            'CRYSTAL': '💎',
            'SILICATES': '🪨',
            'ROCK': '🪨',
            'IRON': '🔩',
            'METAL': '🔩',
            'HYDROGEN': '💨',
            'HELIUM': '💨',
            'GAS': '💨',
        }
        return emoji_map.get(composition.upper(), '⚫')

    def total_mass(self) -> float:
        """Calculate current total mass of all layers."""
        return sum(layer['mass'] for layer in self.layers)


__all__ = ["PlanetaryBody"]
