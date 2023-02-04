""" Sub-package dealing with the rules and implementing core mechanics.

Nothing player-related is implemented here.

Exported Classes:
-----------------
    GameEnv: Core mechanics of the game.
    GameRules: Rules encoding.

Exported Variables:
-------------------
    Play (type): Type of a play.
    Roll (type): Type of a roll.
"""

__all__ = ['GameEnv', 'GameRules', 'Play', 'Roll']

from .env import GameEnv, Play, Roll
from .rules import GameRules
