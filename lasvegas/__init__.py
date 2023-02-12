""" Las Vegas (boardgame) API package.

Exported Functions:
-------------------
    confront: Confront multiple policies over multiple games!
    play_vs: Play with friends and/or bots.
"""

__all__ = ["confront", "play_vs"]
__author__ = "Élie Goudout"
__version__ = "0.1.3"

from .interactive import confront, play_vs
