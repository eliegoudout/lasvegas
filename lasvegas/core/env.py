""" Core game mechanics as a pure environment.

Exported Classes:
-----------------
    GameEnv: Core mechanics of the game.

Exported Variables:
-------------------
    Play (type): Type of a play.
    Roll (type): Type of a roll.
"""

__all__ = ['GameEnv', 'Play', 'Roll']

from typing import Iterable
from warnings import warn

from collections import deque
import random

from .rules import GameRules


class _PopableCycle:
    """ Creates a cycle with popable previous element.

    Used for players index cycle.
    """
    def __init__(self, iterable: Iterable, *, first: int = 0) -> None:
        """ Constructor for `_PopableCycle`.

        Arguments:
        ----------
            iterable (Iterable): Defines the elements of the cycle.
            first (int): Index of the starting element of the cycle.
        """
        self.deque = deque(iterable)
        self.deque.rotate(- first)

    def __iter__(self):
        return self

    def __next__(self):
        item = self.deque.popleft()
        self.deque.append(item)
        return item

    def delete_prev(self):
        self.deque.pop()


Play = int | None
Roll = list[list[int]]


class GameEnv(GameRules):
    """ Class with core mechanics of a game, external to players.

    Logic is the following: playing a game is following a succession of
    steps. After one step was done (see `one_step`, `next_step` is
    updated. It is set to `None` if further information is needed, at
    which point `resume` will stop and `one_step` won't advance.

    New Attributes:
    ---------------
        is_over (bool): Whether or not the game is over.
        max_dice (int): Maximum number of dice of one type that can be
            at the same casino.
        next_step (Callable | None): The next step to be executed. If
            `None`, the game will pause.
        with_xtr (bool): Whether or not the game is played with neutral
            dice.

    New Properties:
    ---------------
        [get, set] curr_own_dice (int): Number of `Own` dice of current
            player.
        [get, set] curr_xtr_dice (int): Number of `Xtr` dice of current
            player.

    New Attributes Upon Use:
    ------------------------
        casinos_bills (list[list[int]]): The winnable bills under each
            casinos.
        casinos_dice (list[list[int]]): The dice placed on each casinos.
        current_round (int): The number of the current round.
        current_player_index (int): Index of current player.
        first_player_index (int): Index of the first player of the
            current round.
        played (Play): The move that was played.
        players_bills (list[list[int]]): The bills won by players.
        players_index_cycle (_PopableCycle): Cycle of remaining players
            index.
        players_own_dice (int): Number of `Own` dice of players.
        players_xtr_dice (int): Number of `Xtr` dice of players.
            Attribute is never initialized if not `self.with_xtr`!
        roll_own (list[int] | None): Rolled `Own` dice.
        roll_xtr (list[int] | None): Rolled `Xtr` dice.

    New Methods:
    ------------
        __call__: Advances the game by an arbitrary number of steps or
            until forced pause.
        one_step: Advances game by one step.
        play: Gives instance a playing move.
        roll: Gives instance a roll.

    New Internal Methods:
    ---------------------
        _change_first_player
        _change_player
        _draw_bills
        _end_game
        _end_round
        _end_turn
        _get_winners
        _give_bills
        _initialize_dice
        _initialize_game
        _initialize_round
        _initialize_turn
        _legal_plays
        _move_dice
        _reset_roll_and_play
        _update_survival
    """
    def __init__(self, **ruleset) -> None:
        """ Constructor for `GameEnv`.

        Arguments:
        ----------
            **ruleset (Any): See `GameRules`.
        """
        super().__init__(**ruleset)
        self.with_xtr = self.num_xtr_dice > 0
        self.max_dice = max(self.num_own_dice,
                            self.num_players * self.num_xtr_dice)
        self.next_step = self._initialize_game  # Bound method for next step
        self.is_over = False

    ########################
    #         API          #
    ########################

    def __call__(self, steps=None) -> bool:
        """ Runs the game for `steps` steps or for as long as possible.

        Returns:
        --------
            `True` if the game is over after call, `False` otherwise.
        """
        if steps is None:
            while self.one_step():
                pass
        else:
            step = 0
            while self.one_step() and step < steps:
                step += 1
        return self.is_over

    def one_step(self) -> bool:
        """ Advances game by one step.

        Returns:
        --------
            Value of `self.next_step is not None` after the step.
        """
        if self.next_step is None:
            warn("Game is already over!" if self.is_over else "No next step!",
                 stacklevel=2)
        else:
            self.next_step()
        return self.next_step is not None

    def roll(self, roll_: Roll) -> None:  # Careful, no sanity check
        """ Gives instance a roll.

        Arguments:
        ----------
            roll_ (Roll): `roll_[0]` is the number of occurrences of
                dice `0` to `self.num_casinos - 1` of his or her colour,
                that the player rolled. If `self.with_xtr`,then
                `roll_[1]` is the same for neutral (extra) dice.
            """
        self.roll_own = roll_[0]
        if self.with_xtr:
            self.roll_xtr = roll_[1]
        self.next_step = None

    def play(self, played: Play) -> None:
        """ Gives instance a playing move.

        The playing move must be legal here.
        """
        assert played in self._legal_plays()
        self.played = played
        self.next_step = self._end_turn

    ########################
    #      GAME LOGIC      #
    ########################

    def _initialize_game(self) -> None:
        self.players_bills = [[] for _ in range(self.num_players)]
        self.first_player_index = - 1
        self.current_round = - 1
        self.next_step = (
            self._initialize_round
            if self.num_rounds > 0
            else self._end_game)

    def _end_game(self) -> None:
        self.is_over = True
        self.next_step = None

    ########################
    #     ROUND LOGIC      #
    ########################

    def _initialize_round(self) -> None:
        self._draw_bills()
        self._initialize_dice()
        self._change_first_player()
        self.next_step = self._initialize_turn

    def _end_round(self) -> None:
        self._give_bills()
        self.next_step = (
            self._initialize_round
            if self.current_round + 1 < self.num_rounds
            else self._end_game)

    def _draw_bills(self) -> None:
        """ Places bills under every casino at the start of a round.

        Bills are sorted in ascending order.
        """
        random.shuffle(self.bills)
        self.casinos_bills = [[] for _ in range(self.num_casinos)]
        for i in range(self.num_casinos):
            total = 0
            while total < self.casinos_min[i]:
                bill = self.bills.pop()
                self.casinos_bills[i].append(bill)
                total += bill
            self.casinos_bills[i].sort()

    def _initialize_dice(self) -> None:
        """ Empties casinos dice and gives players their dice back.

        For casinos dice, if `self.with_xtr`, the neutral (xtr) dice are
        placed in last position of `casinos_dice[i]`.
        """
        # Empty casinos
        self.casinos_dice = [
            [0] * (self.num_players + self.with_xtr)
            for _ in range(self.num_casinos)
            ]
        # Give players dice
        self.players_own_dice = [self.num_own_dice] * self.num_players
        if self.with_xtr:
            self.players_xtr_dice = [self.num_xtr_dice] * self.num_players

    def _change_first_player(self):
        """ To simulate passing first player chip after a round. """
        self.current_round += 1
        self.first_player_index = ((self.first_player_index + 1)
                                   % self.num_players)
        self.players_index_cycle = _PopableCycle(range(self.num_players),
                                                 first=self.first_player_index)

    def _give_bills(self) -> None:
        """ Gives won bills to players at the end of a round.

        Hypothesis: Casinos bills are sorted (ascending) and neutral
        dice are stored in last position of `casino_dice[i]`.
        """
        # Looping over casinos
        for i, winners in enumerate(self._get_winners()):
            # While there are still bills to win, and winners to claim them
            while self.casinos_bills[i] and winners:
                winner = winners.pop()
                bill = self.casinos_bills[i].pop()
                if winner < self.num_players:  # Actual player
                    self.players_bills[winner].append(bill)
                else:  # Fictional player (xtr dice)
                    self.bills.append(bill)
            # Giving back remaining bills to the game
            self.bills += self.casinos_bills[i]

    ########################
    #      TURN LOGIC      #
    ########################

    def _initialize_turn(self) -> None:
        self._change_player()
        self._reset_roll_and_play()
        self.next_step = None

    def _end_turn(self) -> None:
        self._move_dice()
        self._update_survival()
        self.next_step = (
            self._initialize_turn
            if self.players_index_cycle.deque
            else self._end_round)

    def _change_player(self) -> None:
        self.current_player_index = next(self.players_index_cycle)

    def _reset_roll_and_play(self) -> None:
        self.played = self.roll_own = self.roll_xtr = None

    def _move_dice(self) -> None:
        """ Moves dice from player to casino after roll and play.

        Hypothesis: Roll and play have are properly set.
        """
        casino_dice = self.casinos_dice[self.played]
        self.curr_own_dice -= self.roll_own[self.played]
        casino_dice[self.current_player_index] += self.roll_own[self.played]
        if self.with_xtr:
            self.curr_xtr_dice -= self.roll_xtr[self.played]
            casino_dice[self.num_players] += self.roll_xtr[self.played]

    def _update_survival(self) -> None:
        """ Removes current player that doesn't have any dice left. """
        if (self.curr_own_dice == 0
                and (not self.with_xtr or self.curr_xtr_dice == 0)):
            self.players_index_cycle.delete_prev()

    ########################
    #        UTILS         #
    ########################

    def _legal_plays(self) -> set[int]:
        """ Returns legal plays for a given roll.

        Careful, no sanitation of the roll.
        """
        return (
            {i for i, x in enumerate(self.roll_own) if (x or self.roll_xtr[i])}
            if self.with_xtr
            else {i for i, x in enumerate(self.roll_own) if x})

    def _get_winners(self) -> list[list[int]]:
        """ Computes the winners for each casino, in reverse order.

        Following the rules, only players with dice and with a unique number
        of dice win. First (returned in last position) winner is the player
        with the most dice.

        Example: If number of dice on a casino are [1, 2, 4, 2, 0, 3],
        winners are [0, 5, 2]

        Implementation specific to the game, for low `self.max_dice`.
        """
        winners = []
        for i in range(self.num_casinos):
            casino_dice = self.casinos_dice[i]
            uniques = []
            occ = [2] + [0] * self.max_dice
            for val in casino_dice:
                occ[val] += 1
            for i, val in enumerate(casino_dice):
                if occ[val] == 1:
                    uniques.append(i)
            winners.append(sorted(uniques, key=lambda i: casino_dice[i]))
        return winners

    ########################
    #      PROPERTIES      #
    ########################

    @property
    def curr_own_dice(self) -> int:
        """ Returns current player's number of own dice. """
        return self.players_own_dice[self.current_player_index]

    @curr_own_dice.setter
    def curr_own_dice(self, value: int) -> None:
        """ Setter for `curr_own_dice` property. """
        self.players_own_dice[self.current_player_index] = value

    @property
    def curr_xtr_dice(self) -> int:
        """ Returns current player's number of xtr dice. """
        return self.players_xtr_dice[self.current_player_index]

    @curr_xtr_dice.setter
    def curr_xtr_dice(self, value: int) -> None:
        """ Setter for `curr_xtr_dice` property. """
        self.players_xtr_dice[self.current_player_index] = value
