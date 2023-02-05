""" Module for rule setting.

Exported Classes:
-----------------
    GameRules: Rules encoding.
"""

__all__ = ['GameRules']

from typing import Any


def _is_int_list(x: Any) -> bool:
    """ Returns `True` for empty list. """
    if not isinstance(x, list):
        return False
    for elt in x:
        if not isinstance(elt, int):
            return False
    return True


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
            num_xtr_dice: int | dict[int, int] = {
                2: 4,
                3: 2,
                4: 2,
                5: 0,
                },
            bills: dict[int, int] | list[int] = {
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
            casinos_min: int | list[int] = 50000) -> None:
        """ Constructor for `GameRules`.

        Default values are derived from rulebook.

        Arguments:
        ----------
            bills (dict[int, int] | list[int]): Bills to use in the game
                in one of two possible formats: a dictionary of pairs
                `<bill value>: <quantity>`, or a simple list.
            casinos_min (int | list[int]): Target minimum amount of
                money at each casino at every round. If of type `int`,
                the same value will be used for every casino.
            num_casinos (int): Number of casinos (i.e. number or faces
                of dice).
            num_own_dice (int): Number of dice owned by every player.
            num_players (int): Number of players.
            num_rounds (int): Number of rounds.
            num_xtr_dice (int | dict[int, int]): Number of neutral (or
                'extra') dice owned by players. If provided as a `dict`,
                the value `num_xtr_dice[num_players]` is used.
        """
        # Number of players
        self.num_players: int = num_players
        assert self.num_players > 0
        # Number of rounds
        self.num_rounds: int = num_rounds
        assert self.num_rounds > 0
        # Number of dice
        #   Own
        self.num_own_dice: int = num_own_dice
        #   Xtr
        self.num_xtr_dice: int = (
            num_xtr_dice[self.num_players]
            if isinstance(num_xtr_dice, dict)
            else num_xtr_dice)
        assert self.num_own_dice > 0
        assert self.num_xtr_dice >= 0
        # Casinos
        self.num_casinos: int = num_casinos
        assert self.num_casinos > 0
        # Casinos min
        self.casinos_min: list[int] = (
            casinos_min
            if isinstance(casinos_min, list)
            else [casinos_min] * self.num_casinos)
        assert _is_int_list(self.casinos_min)
        # Bills
        self.bills: list[int] = (
            [bill for val, qty in bills.items() for bill in [val] * qty]
            if isinstance(bills, dict)
            else bills)
        assert _is_int_list(self.bills)

    def __repr__(self):
        cls_name = type(self).__name__
        attr_str = ', '.join([
            "%s=%r" % kv for kv in self.__dict__.items()])
        return f"{cls_name}({attr_str})"
