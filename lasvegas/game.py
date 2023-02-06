""" Module adding player logic to the core `GameEnv`.

Exported Classes:
-----------------
    Game: Adds player layer to core mechanics.
    Player: Contains player's name and behaviour.

Exported Variables:
-------------------
    Policy (type): Type of a policy (playing function).
    Roller (type): Type of a roller (rolling function).
"""

from __future__ import annotations

__all__ = ['Game', 'Player', 'Policy', 'Roller']

from typing import Callable
from warnings import warn

import random

from .core import GameEnv, Play, Roll


Policy = Callable["Game", Play]
Roller = Callable["Game", Roll]


class Player:
    """ Instances represent players, with rolling and playing behaviour.

    Attributes:
    -----------
        name (str): Name of the player.
        play_func (Policy | None): Playing function if
            `not wait_for_play`. In this case, if `None`, game will
            apply default behaviour.
        roll_func (Roller | None): Rolling function if
            `not wait_for_roll`. In this case, if `None`, game will
            apply default behaviour.
        wait_for_play (bool): If `True` game will stop upon player's
            turn to play.
        wait_for_roll (bool): If `True` game will stop upon player's
            turn to roll.

    Methods:
    --------
        __call__
    """
    def __init__(
            self,
            *,
            wait_for_roll: bool = False,
            roll_func: Roller | None = None,
            wait_for_play: bool = False,
            play_func: Policy | None = None,
            name: str | None = None) -> None:
        """ Constructs a Player instance.

        Arguments:
        ----------
            name (str): Name of the player.
            play_func (Policy): Playing function if `not wait_for_play`.
                In this case, if `None`, game will apply default
                behaviour.
            roll_func (Roller): Rolling function if `not wait_for_roll`.
                In this case, if `None`, game will apply default
                behaviour.
            wait_for_play (bool): If `True` game will stop upon player's
                turn to play.
            wait_for_roll (bool): If `True` game will stop upon player's
                turn to roll.
        """
        # Roll
        self.wait_for_roll = wait_for_roll
        if roll_func is not None and wait_for_roll:
            warn(f"Player {name}: Since `wait_for_roll` is True, `roll_func` "
                 f"is ignored.")
            roll_func = None
        self.roll_func = roll_func
        # Play
        self.wait_for_play = wait_for_play
        if play_func is not None and wait_for_play:
            warn(f"Player {name}: Since `wait_for_play` is True, `play_func` "
                 f"is ignored.")
            play_func = None
        self.play_func = play_func
        # Name
        self.name = name

    def __call__(self, action: str, game: Game) -> Play | Roll:
        """ Returns a play or a roll given `game`'s state.

        Arguments:
        ----------
            action (str): The action to take, from `{'play', 'roll'}`.
            game (Game): The game Player instance is playing in.

        Returns:
        --------
            The player's `action`.
        """
        if action == 'roll':
            if self.roll_func is not None:
                return self.roll_func(game)
            else:
                raise ValueError(f"Rolling behaviour of player '{self.name}' "
                                 f"is not specified!")
        elif action == 'play':
            if self.play_func is not None:
                return self.play_func(game)
            else:
                raise ValueError(f"Playing behaviour of player '{self.name}' "
                                 f"is not specified!")
        else:
            raise ValueError(f"Parameter `action` should be 'roll' or 'play' "
                             f"(got {action}.)")


class Game(GameEnv):
    """ Uses `Player` class to create playable games from `GameEnv`.

    New Attributes:
    ---------------
        given_players (list[Player]): Players explicitly provided upon
            instance creation.
        players (list[Player]): All players in the game (including
            potentially added bots)
        players_permutation (list[int]): Players are shuffled at the
            beginning according to this permutation.

    New Properties:
    ---------------
        [get] current_player (Player): Returns the currently playing
            `Player`.

    New internal Methods:
    ---------------------
        _assign_players
        _random_play
        _random_roll
        _player_play
        _player_roll

    Modified Methods:
    -----------------
        play
        roll

    Modified Internal Methods:
    --------------------------
        _initialize_turn
    """
    def __init__(
            self,
            players: list[Player] = [],
            /,
            **ruleset) -> None:
        """ Constructor for Game

        If not provided, the number of players is set to `len(players)`.

        Arguments:
        ----------
            players (list[Player]): Players for the game. Order doesn't
                matter since they're shuffled.
            **ruleset: See `GameEnv`. If `num_players` is greater than
                `len(players)`, bots are added.

        """
        num_players = ruleset.pop("num_players", len(players))
        assert num_players >= len(players)
        super().__init__(num_players=num_players, **ruleset)
        self.given_players = players
        self._assign_players()

    ########################
    #      GAME LOGIC      #
    ########################

    def _assign_players(self) -> None:
        # Add players
        num_to_add = self.num_players - len(self.given_players)
        added_bots = [Player(name=f"Bot {i}") for i in range(num_to_add)]
        self.players = self.given_players + added_bots
        # Fill default roll/policy
        for player in self.players:
            if not player.wait_for_roll:
                player.roll_func = player.roll_func or Game._random_roll
            if not player.wait_for_play:
                player.play_func = player.play_func or Game._random_play
        # Order
        self.players_permutation = list(range(self.num_players))
        random.shuffle(self.players_permutation)
        self.players = [self.players[i] for i in self.players_permutation]

    ########################
    #      TURN LOGIC      #
    ########################

    def _initialize_turn(self) -> None:
        super()._initialize_turn()
        self.next_step = self._player_roll

    def roll(self, roll_: Roll) -> None:
        super().roll(roll_)
        self.next_step = self._player_play

    def _player_roll(self) -> None:
        """ Makes current player roll if possible. """
        if self.current_player.wait_for_roll:
            self.next_step = None
        else:
            self.roll(self.current_player('roll', self))

    def play(self, played: Play) -> None:
        """ Same as `GameEnv.play` but random upon illegal play. """
        self.played = (played
                       if played in self._legal_plays()
                       else self._random_play())
        self.next_step = self._end_turn

    def _player_play(self) -> None:
        """ Makes current player play if possible. """
        if self.current_player.wait_for_play:
            self.next_step = None
        else:
            self.play(self.current_player('play', self))

    ########################
    #      TURN LOGIC      #
    ########################

    def _random_roll(self) -> Roll:
        """ Gives a random roll.

        Since we'll only draw a few random numbers, random.random() is
        faster than np.random.randint If we wanted to find a lot, we
        would better use NumPy. See:
        https://eli.thegreenplace.net/2018/slow-and-fast-methods-for-generating-random-integers-in-python/
        """
        N = self.num_casinos
        roll = []
        # Own dice
        roll_own = [0] * N
        for _ in range(self.curr_own_dice):
            roll_own[int(N * random.random())] += 1
        roll.append(roll_own)
        # Xtr dice
        if self.with_xtr:
            roll_xtr = [0] * self.num_casinos
            for _ in range(self.curr_xtr_dice):
                roll_xtr[int(N * random.random())] += 1
            roll.append(roll_xtr)
        # Return
        return roll

    def _random_play(self) -> Play:
        """ Gives a random play. """
        return random.choice(list(self._legal_plays()))

    ########################
    #      PROPERTIES      #
    ########################

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]
