""" Module for rule setting.

Exported Classes:
-----------------
    GameRules: Rules encoding.
"""

__all__ = ['GameRules']

from typing import Any


def _is_int(x: Any) -> bool:
    return isinstance(x, int)


def _is_int_list(xl: Any) -> bool:
    """ Returns `True` for empty list. """
    return isinstance(xl, list) and all(map(_is_int, xl))


class GameRules:
    """ Root class of a game, to set (eventually custom) rules.

    Attributes:
    -----------
        bills (list[int]): List of bills in the game.
        casinos_min (list[int]): Target minimum value under each casino
            every round.
        num_casinos (int): Number of casinos (i.e. number or faces of
            dice).
        num_own_dice (int): Number of dice owned by every player.
        num_players (int): Number of players.
        num_rounds (int): Number of rounds.
        num_xtr_dice (int): Number of neutral (or 'extra') dice owned by
            players.
    """
    # Just for info. 1-player version excluded for now.
    rulebook_min_players: int = 2
    rulebook_max_player: int = 5

    def __init__(
            self,
            *,
            num_players: int,
            num_rounds: int = 4,
            num_casinos: int = 6,  # number of faces of dice
            num_own_dice: int = 8,
            num_xtr_dice: int | None = None,
            num_xtr_dice_dict: dict[int, int] = {
                2: 4,
                3: 2,
                4: 2,
                5: 0,
                },
            bills: list[int] | None = None,
            bills_dict: dict[int, int] = {
                10000: 5,
                20000: 7,
                30000: 7,
                40000: 5,
                50000: 6,
                60000: 5,
                70000: 5,
                80000: 4,
                90000: 4,
                },
            casinos_min: list[int] | None = None,
            casino_min: int = 50000) -> None:
        """ Constructor for `GameRules`.

        Default values are derived from rulebook.

        Arguments:
        ----------
            bills (list[int] | None): List of bills to use if not
                `None`.
            bills_dict (dict[int, int]): Dictionnary of bills to use as
                `bill_value: quantity` pairs, if `bills == None`.
            casino_min (int): Target minimum value at every casino at
                every round if `casinos_min == None`.
            casinos_min (list[int] | None): Casino-specific target
                minimum value at every round.
            num_casinos (int): Number of casinos (i.e. number or faces
                of dice).
            num_own_dice (int): Number of dice owned by every player.
            num_players (int): Number of players.
            num_rounds (int): Number of rounds.
            num_xtr_dice (int | None): Number of neutral (or 'extra')
                dice owned by players.
            num_xtr_dice_dict (dict[int, int]): Same as `num_xtr_dice`
                but for multiple possible values of `num_players`. Pairs
                `num_players: num_xtr_dice`.
        """
        # Number of players
        self.num_players = num_players
        assert _is_int(self.num_players) and self.num_players > 0
        # Number of rounds
        self.num_rounds = num_rounds
        assert _is_int(self.num_rounds) and self.num_rounds > 0
        # Number of dice
        #   Own
        self.num_own_dice = num_own_dice
        assert _is_int(self.num_own_dice) and self.num_own_dice >= 0
        #   Xtr
        self.num_xtr_dice = (
            num_xtr_dice_dict[self.num_players]
            if num_xtr_dice is None
            else num_xtr_dice)
        assert _is_int(self.num_xtr_dice) and self.num_xtr_dice >= 0
        assert self.num_own_dice + self.num_xtr_dice > 0
        # Casinos
        self.num_casinos = num_casinos
        assert _is_int(self.num_casinos) and self.num_casinos > 0
        # Casinos min
        self.casinos_min = (
            [casino_min] * self.num_casinos
            if casinos_min is None
            else casinos_min)
        assert _is_int_list(self.casinos_min)
        # Bills
        self.bills = (
            [bill for val, num in bills_dict.items() for bill in [val] * num]
            if bills is None
            else bills)
        assert _is_int_list(self.bills)
