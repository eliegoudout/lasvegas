""" Module adding player logic to the core `GameEnv` for simulations.

Exported Classes:
-----------------
    Game: Class to run games with player instances.
"""


__all__ = ['Game']

from copy import deepcopy
from functools import cached_property
from typing import Any
import traceback

from .act import BasePlayer, Player, random_play, random_roll
from .core import GameEnv


class Game:
    """ Class to run games with player instances.

    Class Attributes:
    -----------------
        default_policy (Policy): Used when player behaviour is undefined
            or inappropriate in "safe" mode.
        default_rollicy (Rollicy): Used when player behaviour is
            undefined or inappropriate in "safe" mode.

    Attributes:
    -----------
        env (GameEnv): The environment playing the game.
        num_given_players (int): Number of players passed at
            instanciation. Clipped if too many compared to
            `num_players`.
        players (list[Player]): List of players of the game. Start of
            the list contains players passed at instanciation.
        safe (bool): When `True`, players are only passed a copy of
            the environment and players name. Slows down game execution.
            Additional roll and play sanity checks are also made.

    Cached Properties:
    ------------------
        players_name [get] (list[str]): Explicit.

    Methods:
    --------
        __init__: Constructor for `Game`.
        run: Plays a game from start to finish.

    Internal Methods:
    -----------------
        _add_missing_players
    """
    default_policy = random_play
    default_rollicy = random_roll

    def __init__(
            self,
            players: list[Player] = [],
            /,
            *,
            safe: bool = False,
            **envargs: Any) -> None:
        """ Constructor for `Game`.

        Arguments:
        ----------
            players (list[Player]): List of players that will
                participate in the game. The number of players is
                determined by the length of `players`, unless specified
                in `gameargs`. The list is truncated or extended (with
                Bots) if needed. Defaults to `[]`.
            safe (bool): When `True`, players are only passed a copy of
                the environment and players name. Slows down game
                execution. Additional roll and play sanity checks are
                also made. Defaults to `False`.
            **envargs: Passed to `GameEnv` after `num_players`
                processing.

        """
        envargs["num_players"] = envargs.get("num_players", len(players))
        self.env = GameEnv(**envargs)
        self.num_given_players = min(len(players), self.env.num_players)
        self.players = players[:self.num_given_players]
        self._add_missing_players()
        self.safe = safe

    def _add_missing_players(self) -> None:
        num_to_add = self.env.num_players - self.num_given_players
        added_bots = [BasePlayer(name=f"Bot {i}") for i in range(num_to_add)]
        self.players.extend(added_bots)

    @cached_property
    def players_name(self) -> list[str]:
        return [player.name for player in self.players]

    def run(self) -> None:
        """ Plays a game from start to finish. """
        self.env.reset()
        while not self.env():
            cp = self.players[self.env.current_player_index]
            rollicy = cp.roll_func if cp.rolls else random_roll
            policy = cp.play_func if cp.plays else random_play
            # Secure Mode
            if self.safe:
                # Roll
                if self.env.rolled is None:
                    try:
                        rolled = rollicy(
                                      deepcopy(self.env),
                                      players_name=deepcopy(self.players_name))
                        assert self.env.roll_is_ok(rolled)
                        self.env.roll(rolled)
                    except Exception as e:
                        _pretty_catch(e, f"Caught the following exception "
                                         f"while player '{cp.name}' rolled:")
                        self.env.roll(self.default_rollicy(self.env))
                # Play
                try:
                    played = policy(deepcopy(self.env),
                                    players_name=deepcopy(self.players_name))
                    if played not in self.env.legal_plays():
                        played = self.default_policy(self.env)
                    self.env.play(played)
                except Exception as e:
                    print("lkjlkjkj")
                    _pretty_catch(e, f"Caught the following exception "
                                     f"while player '{cp.name}' played:")
                    print("lkjlkjkj")
                    self.env.play(self.default_policy(self.env))
            # Normal Mode
            else:
                # Roll
                if self.env.rolled is None:
                    rolled = rollicy(self.env, players_name=self.players_name)
                    self.env.roll(rolled)
                # Play
                played = policy(self.env, players_name=self.players_name)
                if played is None:
                    played = self.default_policy(self.env)
                self.env.play(played)


def _width(str_: str):
    """ Width of a string in console. Only manages `\t` and `\n`. """
    return max(map(len, map(str.rstrip, str_.expandtabs().split('\n'))))


def _pretty_catch(e: Exception, msg: str = 'Caught:') -> None:
    """ To catch an exception and still show its traceback.

    Example:
        ```
        Caught the following exception while player 'Bot 0' played:
        ╭──────────────────────────────────────────────────────────
        │ Traceback (most recent call last):
        │   File "/path/to/game.py", line 110, in run
        │     played = policy(deepcopy(self.env),
        │              ^^^^^^^^^^^^^^^^^^^^^^^^^^
        │   File "/path/to/policy.py", line 33, in random_play
        │     return random.choice(None)  # IndexError on purpose
        │            ^^^^^^^^^^^^^^^^^^^
        │   File "/path/to/random.py", line 370, in choice
        │     raise IndexError('Cannot choose from an empty sequence')
        │ IndexError: Cannot choose from an empty sequence │
        ╰──────────────────────────────────────────────────╯
        ```
    """
    print(msg)
    tb = traceback.format_exception(type(e), e, e.__traceback__)
    tb = ''.join(tb).strip('\n').split('\n')
    tb = ['╭' + '─' * (_width(msg) - 1)] + ['│ ' + line for line in tb]
    tb[-1] += ' │'
    tb.append('╰' + '─' * (_width(tb[-1]) - 2) + '╯')
    print('\n'.join(tb))
