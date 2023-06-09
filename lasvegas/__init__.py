""" Las Vegas (boardgame) API package.

Exported Classes:
-----------------
    BasePlayer: Contains player's name and behaviour.
    Game: Class to run games with player instances.
    GameEnv: Core mechanics of the game.
    GameRules: Class to set (eventually custom) rules.
    Human: Sub-class of `BasePlayer` destined for CLI use.

Exported Functions:
-------------------
    confront: Confronts different policies in a multiple-games match.
    play_vs: Play a game in CLI.
"""

__all__ = [
    'BasePlayer',
    'Game',
    'GameEnv',
    'GameRules',
    'Human',
    'confront',
    'play_vs',
]
__author__ = "Élie Goudout"
__version__ = "0.2.0"

from .act import BasePlayer, Human
from .core import GameEnv, GameRules
from .game import Game
from .interactive import confront, play_vs
