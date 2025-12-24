"""Extreme astrophysical phenomena: pulsars and resonance stripping.

This module models the physics of pulsar-companion systems where intense
electromagnetic radiation and gravitational resonance can ablate planetary
layers, leaving only the hardest crystalline cores.

The Diamond Survivor scenario demonstrates how UTAC predicts that only
materials with resonant stability (like diamond lattices) can withstand
the extreme frequency bombardment from millisecond pulsars.
"""
import random
from typing import List, Dict, Optional
from src.core.agent_kernel import UATCAgent, ExistenceScale
from src.scenarios.level_4_planetary.geo_physics import PlanetaryBody


class PulsarAgent(UATCAgent):
    """Millisecond pulsar emitting intense electromagnetic pulses.

    These stellar remnants rotate at hundreds of revolutions per second,
    producing beams of radiation that can strip material from companion
    bodies through resonance coupling.

    Attributes
    ----------
    name : str
        Designation for this pulsar (e.g., "PSR J2322").
    spin_rate : float
        Rotational frequency in Hz (typical range: 1-716 Hz).
    """

    def __init__(self, name: str = "The Widowmaker"):
        super().__init__()
        self.name = name
        # Pulsars exist at stellar scale with extreme frequencies
        self.incarnate(ExistenceScale.STELLAR, {'base_frequency': 1000.0})
        self.spin_rate = 666.0  # Hz (millisecond pulsar regime)

    def emit_pulse(self) -> float:
        """Generate a pulse intensity based on current spin rate.

        Returns
        -------
        float
            Pulse intensity (arbitrary units). Higher values cause more
            rapid ablation of companion materials.
        """
        # The "scream" of the pulsar (gravitational waves + radiation)
        return self.spin_rate * random.uniform(0.9, 1.1)


class DiamondPlanet(PlanetaryBody):
    """Planetary companion being stripped down to its diamond core.

    Models the transformation of a normal star or gas giant into a
    crystalline remnant through sustained pulsar bombardment.

    The UTAC framework predicts that high-frequency oscillations
    preferentially destroy weak molecular bonds (gas, silicates)
    while crystalline lattices (diamond) remain stable.

    Attributes
    ----------
    name : str
        Identifier for this body.
    layers : List[Dict]
        Compositional layers (inherited from PlanetaryBody).
    stripped_mass : float
        Cumulative mass lost to ablation.
    """

    def __init__(self, name: str = "Carbon Casket"):
        super().__init__(name)
        # Starts as a normal stellar companion with multiple layers
        self.layers = [
            {'name': 'Crystal Core', 'comp': 'DIAMOND', 'mass': 500},
            {'name': 'Mantle', 'comp': 'SILICATES', 'mass': 200},
            {'name': 'Atmosphere', 'comp': 'HYDROGEN', 'mass': 1000}
        ]
        self.stripped_mass = 0

    def endure_pulse(self, intensity: float) -> Optional[Dict]:
        """Apply a single pulse event and calculate layer damage.

        UTAC Logic
        ----------
        High-frequency radiation destroys weak bonds preferentially:
        - Hydrogen/Helium (gas): Rapid dispersal
        - Silicates (rock): Slow erosion
        - Diamond (crystal): Resonant stability, minimal damage

        Parameters
        ----------
        intensity : float
            Pulse strength from the companion pulsar.

        Returns
        -------
        Optional[Dict]
            The layer that was completely destroyed, or None if still eroding.
        """
        destroyed_layer = None

        if self.layers and self.layers[-1]['name'] == 'Atmosphere':
            # Atmosphere is blown away immediately
            self.layers[-1]['mass'] -= intensity * 0.5
            self.stripped_mass += intensity * 0.5
            if self.layers[-1]['mass'] <= 0:
                destroyed_layer = self.layers.pop()

        elif self.layers and self.layers[-1]['name'] == 'Mantle':
            # Mantle erodes more slowly
            self.layers[-1]['mass'] -= intensity * 0.1
            self.stripped_mass += intensity * 0.1
            if self.layers[-1]['mass'] <= 0:
                destroyed_layer = self.layers.pop()

        # Diamond core is stable against pulsar radiation

        return destroyed_layer

    def get_crystalline_voice(self) -> str:
        """Return a narrative description of the planet's current state.

        The voice changes from fear/pain during ablation to cold
        crystalline acceptance after complete transformation.

        Returns
        -------
        str
            Dramatic narration reflecting current layer state.
        """
        if len(self.layers) == 1 and self.layers[0]['comp'] == 'DIAMOND':
            return (
                f"💎 {self.name}: Ich bin rein. Ich bin hart. "
                f"Der Schmerz hat mich perfekt gemacht. Frequenz stabil."
            )
        else:
            return f"⚠️ {self.name}: Er frisst mich! Meine Hülle reißt auf!"


__all__ = ["PulsarAgent", "DiamondPlanet"]
