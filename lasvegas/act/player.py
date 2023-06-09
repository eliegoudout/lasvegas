""" Player module.

Exported Classes:
-----------------
    Human: Sub-class of `BasePlayer` destined for CLI use.
    BasePlayer: Represents players, with rolling and playing behaviour.

Exported Variables:
-------------------
    Player (type): Type of a player, bound by `BasePlayer`.
"""

__all__ = ['BasePlayer', 'Human', 'Player']

from functools import cached_property
from typing import Any, TypeVar

from ..core import GameEnv, Play, Roll
from .policy import Policy, prompt_play
from .rollicy import Rollicy, prompt_roll


class BasePlayer:
    """ Instances represent players, with rolling and playing behaviour.

    Attributes:
    -----------
        name (str): Name of the player.
        play_func (Policy | None): Playing function or `None`.
        roll_func (Rollicy | None): Rolling function or `None`.

    Cached Properties:
    ------------------
        plays [get] (bool): `play_func is not None`.
        rolls [get] (bool): `roll_func is not None`.

    Methods:
    --------
        __call__: Returns a play or a roll given `env`'s state.
        __init__: Constructor for `BasePlayer`.
    """
    def __init__(
            self,
            *,
            name: str | None = None,
            play_func: Policy | None = None,
            roll_func: Rollicy | None = None) -> None:
        """ Constructs a Player instance.

        Arguments:
        ----------
            name (str | None): Name of the player. Defaults to `None`.
            play_func (Policy | None): Playing function or `None`.
                Defaults to `None`.
            roll_func (Rollicy | None): Rolling function or `None`.
                Defaults to `None`.
        """
        self.roll_func = roll_func
        self.play_func = play_func
        if name is None:
            roll_name = getattr(roll_func, '__name__', 'None')
            play_name = getattr(play_func, '__name__', 'None')
            name = f"{roll_name} -> {play_name}"
        self.name = name

    def __call__(
            self,
            action: str,
            env: GameEnv,
            **kwargs: Any) -> Play | Roll | None:
        """ Returns a play (or `None`) or a roll given `env`'s state.

        Arguments:
        ----------
            action (str): The action to take, from `{'play', 'roll'}`.
            env (GameEnv): The game environment player instance is
                playing in.
            **kwargs: Passed to the playing / rolling function.

        Returns:
        --------
            The player's `action`.

        Raises:
        -------
            ValueError if `action not in {'play', 'roll'}`.
            AssertionError if behaviour for `action` isn't defined.
        """
        if action == 'play':
            assert self.plays, "No playing behaviour is defined!"
            return self.play_func(env, **kwargs)
        elif action == 'roll':
            assert self.rolls, "No rolling behaviour is defined!"
            return self.roll_func(env, **kwargs)
        else:
            raise ValueError(f"Parameter `action` should be 'roll' or 'play' "
                             f"(got {action}).")

    @cached_property
    def plays(self) -> bool:
        return self.play_func is not None

    @cached_property
    def rolls(self) -> bool:
        return self.roll_func is not None


Player = TypeVar("Player", bound=BasePlayer)


class Human(BasePlayer):
    """ Sub-class of `BasePlayer` destined for CLI use. """
    def __init__(
            self,
            name: str | None = None,
            /, *,
            manual_roll: bool = False) -> None:
        """ Constructor for `Human`.

        Arguments:
        ----------
            name (str | None): Passed to `BasePlayer`. Defaults to
                `None`.
            manual_roll (bool): Whether or not to use `prompt_roll` as
                rollicy. Defaults to `False`.
        """
        super().__init__(name=name,
                         play_func=prompt_play,
                         roll_func=prompt_roll if manual_roll else None)
