""" Module defining `Rollicy` protocol and some rolling functions.

Exported Classes:
-----------------
    Rollicy (typing._ProtocolMeta): Type (protocol) of a "rollicy".

Exported Functions:
-------------------
    prompt_roll: Prompts the user to give a roll in CLI.
    random_roll: Gives a random roll.
"""

__all__ = ['Rollicy', 'prompt_roll', 'random_roll']

from typing import Any, Protocol, Sequence
import collections
import random

from ._utils import prompt_integers
from ..core import GameEnv, Roll


class Rollicy(Protocol):
    """ For type hinting. """
    def __call__(
        self,
        env: GameEnv,
        /,
        **kwargs: Any) -> Roll: ...


def random_roll(env: GameEnv, **__: Any) -> Roll:
    """ Gives a random roll.
    Since we'll only draw a few random numbers, random.random() is
    faster than np.random.randint If we wanted to find a lot, we
    would better use NumPy. See:
    https://eli.thegreenplace.net/2018/slow-and-fast-methods-for-generating-random-integers-in-python/
    """
    num_casinos = env.num_casinos
    roll = []
    for dice in env.dice_to_roll():
        sub_roll = dict()
        for _ in range(dice):
            rolled = int(num_casinos * random.random())
            sub_roll[rolled] = sub_roll.get(rolled, 0) + 1
        roll.append(sub_roll)
    return roll


def prompt_roll(
        env: GameEnv,
        *,
        players_name: Sequence[str] | None = None,
        **__) -> Roll:
    """ Shows env state and prompts user to enter a roll in CLI. """
    names = env.colours_name(players_name=players_name)
    roll = []
    for to_roll, name in zip(env.dice_to_roll(), names):
        if to_roll == 0:
            roll.append(dict())
            continue
        sub_roll_list = prompt_integers(f"Roll {to_roll} dice between 0 and "
                                        f"{env.num_casinos-1} for '{name}': ",
                                        to_roll,
                                        lambda d: 0 <= d < env.num_casinos)
        roll.append(dict(collections.Counter(sub_roll_list)))
    return roll
