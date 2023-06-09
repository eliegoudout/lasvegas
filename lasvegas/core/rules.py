""" Module for rule setting. Contains rulebook infos.

Exported Classes:
-----------------
    GameRules: Rules encoding.
    RuleBook: Contains rulebook values.
"""

__all__ = ['GameRules', 'RuleBook']

from typing import Sequence

import numpy as np


class RuleBook:
    """ Rulebook values, used as default. """
    num_casinos: int = 6
    num_rounds: int = 4
    bills_pool: dict[int, int] = {
        10000: 5,
        20000: 7,
        30000: 7,
        40000: 5,
        50000: 6,
        60000: 5,
        70000: 5,
        80000: 4,
        90000: 4,
        }
    casinos_min: int = 50000
    num_own_dice: int = 8
    xtr_rules: dict[int, tuple[int, int, bool]] = {
        # num_players: (num_xtr_players, num_xtr_dice, xtr_collect)
        1: (5, 8, True),
        2: (1, 4, False),
        3: (1, 2, False),
        4: (1, 2, False),
        5: (0, 0, False),
        }
    solo_num_distrib: int = 1


class GameRules:
    """ Class to set (eventually custom) rules.

    Attributes:
    -----------
        bills_pool (NDArray[int]): Bills in the game.
        casinos_min (NDArray[int]): Minimum amount of money at each
            casino at every round. Length determines number of casinos.
        num_rounds (int): Number of rounds.
        solo_num_distrib (int): If in a 1-player game, the number of
            opponents whose entire dice set is distributed at the
        starting_dice (NDArray[int]): Describes dice of all players at
            the beginning of every round. Shape determines number of
            players and extra players. Should be `(P, P + X)` where `P`
            is the number of players (throwing dice) and `X` is the
            number of "extra" players (not throwing dice).
            beginning of every round. Else, `0`.
        xtr_collect (bool): Whether or not the "extra" players collect
            bills at the end of every round.

    Properties:
    -----------
        max_dice [get] (int): Max number of dice of one colour in the
            game.
        num_casinos [get] (int): Explicit.
        num_collectors [get] (int): `P + X if xtr_collect else P` with
            above notations.
        num_colours [get] (int): `P + X` with above notations.
        num_players [get] (int): Explicit.
        num_xtr_players [get] (int): Explicit.
        with_xtr [get] (bool): `X > 0` with above notations.

    Methods:
    --------
        __init__: Constructor for `GameRules`.
        __repr__: String representation of instance.

    Internal Methods:
    -----------------
        _sanity_check: Checks sanity of attributes (type, sign, ...).
    """
    def __init__(
            self,
            *,
            num_players: int | None = None,
            num_own_dice: int | None = None,
            num_xtr_players: int | None = None,
            num_xtr_dice: int | None = None,
            xtr_collect: bool | None = None,
            starting_dice: Sequence[Sequence[int]] | None = None,
            solo_num_distrib: int | None = None,  # Maybe later also list
            num_rounds: int | None = None,
            num_casinos: int | None = None,  # number of faces of dice
            casinos_min: int | Sequence[int] | None = None,
            bills_pool: dict[int, int] | Sequence[int] | None = None) -> None:
        """ Constructor for `GameRules`.

        Default values are derived from rulebook when possible. See
        `RuleBook`.

        Arguments:
        ----------
            bills_pool (dict[int, int] | Sequence[int] | None): Bills to
                use in the game in one of two possible formats: a
                dictionary of pairs `<bill value>: <quantity>`, or an
                `Sequence` listing the bills with repetitions. If
                `None`, rulebook default value is used. Defaults to
                `None`.
            casinos_min (int | Sequence[int] | None): Minimum amount of
                money at each casino at every round. If of type `int`,
                the same value will be used for every casino. If `None`,
                rulebook value is used. Defaults to `None`.
            starting_dice (Sequence[Sequence[int]] | None): Describes
                dice of all players. Shape must be `(P, P + X)` where
                `P` is the number of players (throwing dice) and `X` is
                the number of "extra" players (not throwing dice). The
                value of the matrix at row `i` and column `j` is the
                number of dice of the colour of player `j` that player
                `i` starts with. If `None`, is deduced from other
                parameters. Defaults to `None`.
            num_casinos (int | None): Ignored if `casinos_min` is
                provided as an `Sequence`. Number of casinos (i.e.
                number of faces of dice). If `None`, rulebook default
                value is used. Defaults to `None`.
            num_own_dice (int | None): Ignored if
                `starting_dice` is not `None`. Else, number of dice of
                their own colour every player starts with. If `None`,
                rulebook value is used. Defaults to `None`.
            num_players (int | None): Number of players. Ignored if
                `starting_dice` is not `None`. Defaults to `None`.
            num_rounds (int | None): Number of rounds. If `None`,
                rulebook value is used. Defaults to `None`.
            num_xtr_dice (int | None): Ignored if `starting_dice` is not
                `None`. Else, number of dice of every "extra" colour
                players start with. If `None`, rulebook value, when
                specified, is used. Defaults to `None`.
            num_xtr_players (int | None): Number of "extra" players. If
                `None`, rulebook value, when specified, is used.
                Defaults to `None`.
            solo_num_distrib (int | None): Set to `0` if not a 1-player
                game. Else, the number of opponents whose entire dice
                set is distributed at the beginning of every round. In
                that case, if `None`, rulebook value is used. Defaults
                to `None`.
            xtr_collect (bool | None): Whether or not the "extra"
                players collect bills at the end of every round. If
                `None`, rulebook value, when specified, is used.
                Defaults to `None`.

        Raises:
        -------
            ValueError if one of `num_players`, `num_xtr_players`,
                `num_xtr_dice` or `xtr_collect` cannot be set from
                context or rulebook.
            AssertionError is one of the sanity checks fails.
        """
        # Dice matrix
        if starting_dice is not None:
            self.starting_dice = np.array(starting_dice, dtype=int)
        else:
            if num_players in RuleBook.xtr_rules:
                if num_xtr_players is None:
                    num_xtr_players = RuleBook.xtr_rules[num_players][0]
                if num_xtr_dice is None:
                    num_xtr_dice = RuleBook.xtr_rules[num_players][1]
            elif num_players is None:
                raise ValueError("Rules lack `num_players` specification!")
            elif None in (num_xtr_players, num_xtr_dice):
                if num_xtr_players == 0:
                    num_xtr_dice = 0
                else:
                    raise ValueError(
                        f"With {num_players} players, rules must specify both "
                        f"`num_xtr_players` and `num_xtr_dice`!")
            if num_own_dice is None:
                num_own_dice = RuleBook.num_own_dice
            own = num_own_dice * np.eye(num_players, dtype=int)
            xtr = np.full((num_players, num_xtr_players), num_xtr_dice)
            self.starting_dice = np.c_[own, xtr]
        # Xtr collect
        num_players = len(self.starting_dice)
        num_xtr_players = len(self.starting_dice.T) - num_players
        if num_xtr_players == 0:
            self.xtr_collect = False
        elif xtr_collect is not None:
            self.xtr_collect = xtr_collect
        elif num_players in RuleBook.xtr_rules:
            self.xtr_collect = RuleBook.xtr_rules[num_players][2]
        else:
            raise ValueError(
                f"With {num_players} players, rules lack `xtr_collect` "
                f"specification!")
        # Solo number of dice set distributed
        if num_players > 1:
            self.solo_num_distrib = 0
        else:
            if solo_num_distrib is None:
                solo_num_distrib = RuleBook.solo_num_distrib
            self.solo_num_distrib = solo_num_distrib
        # Number of rounds
        if num_rounds is None:
            num_rounds = RuleBook.num_rounds
        self.num_rounds = num_rounds
        # Casinos min
        if casinos_min is not None and not isinstance(casinos_min, int):
            self.casinos_min = np.array(casinos_min, dtype=int)
        else:
            if num_casinos is None:
                num_casinos = RuleBook.num_casinos
            if casinos_min is None:
                casinos_min = RuleBook.casinos_min
            self.casinos_min = np.full(num_casinos, casinos_min)
        # Bills
        if bills_pool is None:
            bills_pool = RuleBook.bills_pool
        self.bills_pool = np.array(
            [bill
             for val, qty in bills_pool.items()
             for bill in [val] * qty]
            if isinstance(bills_pool, dict)
            else bills_pool,
            dtype=int)
        # Sanity check
        self._sanity_check()

    def __repr__(self) -> str:
        cls_name = type(self).__name__
        attr_str = ', '.join([f"{k}={repr(v)}" for k, v in vars(self).items()])
        return f"{cls_name}({attr_str})"

    def _sanity_check(self) -> None:
        """ Raises AssertionError if sanity checks on attributes fail. """
        # Bills
        assert self.bills_pool.dtype == int
        assert np.all(self.bills_pool > 0)
        # Casinos_min
        assert self.casinos_min.dtype == int
        assert np.all(self.casinos_min > 0)
        # Dice_matrix
        assert self.starting_dice.dtype == int
        assert 0 < len(self.starting_dice) <= len(self.starting_dice.T)
        assert np.all(self.casinos_min >= 0)
        assert self.starting_dice.any(axis=0).all()
        # Num_rounds
        assert isinstance(self.num_rounds, int) and self.num_rounds > 0
        # Solo number of dice set distributed
        assert isinstance(self.solo_num_distrib, int)
        num_xtr_players = len(self.starting_dice.T) - len(self.starting_dice)
        assert 0 <= self.solo_num_distrib <= num_xtr_players
        # Xtr_collect
        assert isinstance(self.xtr_collect, bool)

    ########################
    #      PROPERTIES      #
    ########################

    @property
    def num_casinos(self) -> int:
        return len(self.casinos_min)

    @property
    def num_players(self) -> int:
        return len(self.starting_dice)

    @property
    def num_colours(self) -> int:
        return len(self.starting_dice.T)

    @property
    def num_xtr_players(self) -> int:
        return self.num_colours - self.num_players

    @property
    def num_collectors(self) -> int:
        return self.num_colours if self.xtr_collect else self.num_players

    @property
    def with_xtr(self) -> bool:
        return self.num_xtr_players > 0

    @property
    def max_dice(self) -> int:
        return max(self.starting_dice.sum(axis=0))
