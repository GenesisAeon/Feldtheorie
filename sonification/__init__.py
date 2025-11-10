"""
UTAC Sonification - The Sound of Criticality
=============================================

Transform threshold dynamics into audio.

Modules:
    utac_sonification - Main sonification engine

Usage:
    from sonification import UTACsonifier

    sonifier = UTACsonifier()
    audio, metadata = sonifier.sonify_transition(beta=4.5, theta=100)
"""

from .utac_sonification import UTACsonifier, FIELD_TYPE_PROFILES

__version__ = "1.0.0"
__all__ = ["UTACsonifier", "FIELD_TYPE_PROFILES"]
