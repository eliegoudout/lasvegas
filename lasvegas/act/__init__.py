""" Sub-package with action-side functionalities.

It regroups rolling and playing functions plus classes for players.

Exported Classes:
-----------------
    BasePlayer: Contains player's name and behaviour.
    Human: Sub-class of `BasePlayer` destined for CLI use.

Exported Functions:
-------------------
    prompt_play: Shows env state + prompts user to enter a play in CLI.
    prompt_roll: Shows env state + prompts user to enter a roll in CLI.
    random_play: Gives a random play.
    random_roll: Gives a random roll.

Exported Variables:
-------------------
    Player (type): Type of a player, bound by `BasePlayer`.
    Policy (type): Type of a policy (playing function).
    Rollicy (type): Type of a roller (rolling function).
"""

__all__ = [
    'BasePlayer',
    'Human',
    'Player',
    'Policy',
    'Rollicy',
    'prompt_play',
    'prompt_roll',
    'random_play',
    'random_roll']

from .player import BasePlayer, Human, Player
from .policy import Policy, prompt_play, random_play
from .rollicy import Rollicy, prompt_roll, random_roll
