"""
UTAC Sonification - The Sound of Criticality
=============================================

Transform threshold dynamics into audio.

Modules:
    utac_sonification - Main sonification engine (single voice)
    dynamic_threshold_choir - Multi-voice real-time sonification

Usage:
    # Single voice
    from sonification import UTACsonifier

    sonifier = UTACsonifier()
    audio, metadata = sonifier.sonify_transition(beta=4.5, theta=100)

    # Multi-voice choir
    from sonification import ThresholdChoir

    choir = ThresholdChoir()
    choir.add_voice("AMOC", beta=4.2, theta=50.0)
    choir.add_voice("LLM", beta=3.47, theta=100.0)
    audio = choir.render(duration=10.0)
"""

from .utac_sonification import UTACsonifier, FIELD_TYPE_PROFILES
from .dynamic_threshold_choir import (
    ThresholdChoir,
    VoiceState,
    ChoirMetadata,
    DestabilizationEffects,
    DataSourceSimulator,
    create_demo_choir
)

__version__ = "1.1.0"
__all__ = [
    "UTACsonifier",
    "FIELD_TYPE_PROFILES",
    "ThresholdChoir",
    "VoiceState",
    "ChoirMetadata",
    "DestabilizationEffects",
    "DataSourceSimulator",
    "create_demo_choir"
]
