""" Core game mechanics as a pure environment.

Exported Classes:
-----------------
    GameEnv: Core mechanics of the game.

Exported Variables:
-------------------
    Play (type): Type of a play.
    Roll (type): Type of a roll.
"""

from __future__ import annotations

__all__ = ['GameEnv', 'Play', 'Roll']

from collections import deque
from copy import deepcopy
from typing import Any, Sequence
from warnings import warn
import itertools
import random

from numpy.typing import NDArray
import numpy as np
import tabulate

from .rules import GameRules


Play = int
Roll = list[dict[int, int]]


class GameEnv:
    """ Class with core mechanics of a game, external to players.

    Logic is the following: playing a game is following a succession of
    steps. After one step was done -- see `one_step` --, `next_step` is
    updated. It is set to `None` if further information is needed, at
    which point `resume` will stop and `one_step` won't advance.

    Attributes:
    -----------
        bills_pool (NDArray[int]): See `GameRules`.
        casinos_min (NDArray[int]): See `GameRules`.
        max_dice (int): See `GameRules`.
        num_casinos (int): See `GameRules`.
        num_collectors (int): See `GameRules`.
        num_colours (int): See `GameRules`.
        num_players (int): See `GameRules`.
        num_rounds: See `GameRules`.
        num_xtr_players (int): See `GameRules`.
        order (Sequence[int | None] | bool): Attribute specified at
            instanciation. See `__init__` for details.
        solo_num_distrib (int): See `GameRules`.
        starter (int | bool): Attribute specified at instanciation. See
            `__init__` for details.
        starting_dice (NDArray[int]): See `GameRules`.
        with_xtr (bool): See `GameRules`.
        xtr_collect (bool): See `GameRules`.

    Attributes Upon Use:
    --------------------
        bills (deque): Bills remaining in the "bank".
        casinos_bills (list[list[int]]): Bills under all casinos.
        current_player_index (int): Explicit.
        current_round (int): Explicit. Is `0` before first round.
        dice (NDArray[int]): Locates every dice of the game. Shape
            `(P + C, P + X)` where `P` is the number of players
            (throwing dice), `X` is the number of "extra" players (not
            throwing dice) and `C` is the number of casinos.
        first_player_index (int): Index of the first player of the
            current round.
        is_over (bool | None): Whether or not the game is over. Is
            `None` before game initialization.
        next_step (Callable): The next bound method to call to advance.
            Is `None` when the game is over or when the instance needs
            either a roll or a play to continue.
        played (Play | None): The moved that was just played if not
            `None`.
        players_index_cycle (deque): The cycle of next players to come
            in the current round. Players without dice don't appear
            after the end of their last turn.
        rolled (Roll | None): The roll that was just made if not `None`.
        round_order (deque): The order of players in the current round.
        scores (NDArray[int]): Shape `(num_collectors, 2)`. Every line
            is the colour's `[tot_bills, num_bills]` where `tot_bills`
            is the total value of bills won and `num_bills` is the
            number of bills won.

    Properties:
    -----------
        casinos_dice [get, set] (NDArray[int]): Subarray of `self.dice`,
            of shape `(C, P + X)` with above notations. Row `i`
            corresponds to casino `i`.
        current_dice [get, set] (NDArray[int]): Dice of current player.

    Methods:
    --------
        __call__: Runs the game for potentially multiple steps.
        __init__: Constructor for `GameEnv`.
        colours_name: Outputs list of names associated with all colours.
        dice_to_roll: Number of dice of each colour to roll.
        from_rules: To instanciate from a `GameRules` instance.
        get_gains: The gains of players given precomputed winners.
        get_rules: Exports rules as `GameRules` instance.
        get_winners: Computes the winners for each casino.
        legal_plays: Returns legal plays given `self.rolled`.
        one_step: Advances the game by one step.
        play: Gives instance a playing move.
        rank_order: Returns index from best to worst.
        rankings: Returns ranks, starting from `0`. Equals are computed.
        reset: Sets next step to initialization. Use to restart a game.
        roll: Gives instance a roll.
        roll_is_ok: Sanity check on the roll.
        rolled_asarray: Formats `self.rolled` as an occurrence array.
        show: Shows infos, board, roll and scores.
        show_board: Shows dice, bills under casinos and scores.
        show_infos: Shows infos such as round number or next players.
        show_roll: Shows the dice recently rolled.
        show_scores: Show the current scores and rankings.

    Internal Methods:
    -----------------
        _draw_bills
        _end_game
        _end_round
        _end_turn
        _give_bills
        _load_rules
        _init_round_order
        _initialize_dice
        _initialize_game
        _initialize_round
        _initialize_turn
        _move_dice
        _ordinal
        _reset_roll_and_play
        _solo_special_distribute
        _update_survival
    """
    def __init__(
            self,
            *,
            order: Sequence[int | None] | bool = False,
            starter: int | bool = False,
            rules: GameRules | None = None,
            **ruleset: Any) -> None:
        """ Constructor for `GameEnv`.

        Arguments:
        ----------
            order (Sequence[int | None] | bool): When passed as a
                `Sequence`, completely or partially sets the relative
                order between players. It is possible to set only parts
                of the cycle by specifying a portion of the cycle and by
                using `None` instead of integer indexes. Every `None`
                element of the sequence is replaced randomly at game
                initialization by an unspecified index. For example, in
                a 5-player game, `order=(3, None, 1)` means that player
                `1` will be placed 2 turns after player `3` in the
                cycle, but the relative position of `0`, `2` and `4` is
                still set randomly at game initialization. When passed
                as `bool`: `True` is equivalent to `range(num_players)`
                and `False` is equivalent to `()`. Defaults to `False`.
            rules (GameRules | None): Rules to use if not `None`.
                Defaults to `None`.
            starter (int | bool): When passed as `int`, the index of the
                first player of first round. When passed as `bool`:
                `True` is equivalent to `order[0]` -- or what the first
                element of `order` is after game initialization. `False`
                is equivalent to choosing randomly at game
                initialization. Defaults to `False`.
            **ruleset (Any): Ignored if `rules is not None`. See
                `GameRules`.
        """
        rules = GameRules(**ruleset) if rules is None else deepcopy(rules)
        self._load_rules(rules)
        self.order = deepcopy(order)
        self.starter = starter
        self.reset()

    ########################
    #      PROPERTIES      #
    ########################

    @property
    def current_dice(self) -> NDArray[int]:
        return self.dice[self.current_player_index]

    @current_dice.setter
    def current_dice(self, value: NDArray[int]):
        """ Setter for `current_dice` property. """
        self.dice[self.current_player_index] = value

    @property
    def casinos_dice(self) -> NDArray[int]:
        return self.dice[self.num_players:]

    @casinos_dice.setter
    def casinos_dice(self, value: NDArray[int]):
        """ Setter for `casinos_dice` property. """
        self.dice[self.num_players:] = value

    ########################
    #         API          #
    ########################

    def reset(self) -> None:
        """ Sets next step to initialization. Use to restart a game.

        The same rules will be used. Order of players may change if it
        was left unspecified in `self.order`. Same thing for `starter`.
        """
        self.next_step = self._initialize_game
        self.is_over = None

    def __call__(self, steps: int | None = None) -> bool:
        """ Runs the game for `steps` steps or for as long as possible.

        Returns:
        --------
            `True` if the game is over after call, `False` otherwise.

        Raises:
        -------
            AssertionError if the following is false:
                - `steps is None or steps >= 0`.
        """
        assert steps is None or steps >= 0
        while steps != 0 and self.one_step():
            steps = steps and steps - 1
        return self.is_over

    def one_step(self) -> bool:
        """ Advances the game by one step.

        Returns:
        --------
            Value of bool `self.next_step is not None` after the step.
        """
        if self.next_step is None:
            warn("Game is already over!" if self.is_over else "No next step!",
                 stacklevel=2)
        else:
            self.next_step()
        return self.next_step is not None

    def roll(self, rolled: Roll) -> None:
        """ Gives instance a roll.

        Warning: No sanity check for dice availability, sign, type...!

        Arguments:
        ----------
            rolled (Roll): List, for each colour, or occurence dict of
                rolled dice.
            """
        self.rolled = rolled
        self.next_step = None

    def play(self, played: Play) -> None:
        """ Gives instance a playing move.

        The playing move must be legal here.
        """
        assert played in self.legal_plays()
        self.played = played
        self.next_step = self._end_turn

    def get_rules(self) -> GameRules:
        """ Exports rules as a `GameRules` instance. """
        keys = (
            'bills_pool',
            'casinos_min',
            'num_rounds',
            'solo_num_distrib',
            'starting_dice',
            'xtr_collect')
        return GameRules(**{k: getattr(self, k) for k in keys})

    ########################
    #      GAME LOGIC      #
    ########################

    def _initialize_game(self) -> None:
        self.is_over = False
        # Shuffle bills. Rules say only once at start? Unclear...
        self.bills = deque(self.bills_pool)
        random.shuffle(self.bills)
        # Scores
        self.casinos_bills = [[] for _ in range(self.num_casinos)]
        self.scores = np.full((self.num_collectors, 2), 0)
        # Game state init
        self.current_round = 0
        self._init_round_order()
        self.next_step = self._initialize_round

    def _init_round_order(self) -> None:
        """ Uses construction arguments to define a playing order.

        See `__init__` documentation for processing behaviour of `order`
        and `starter`.

        Raises:
        -------
            AssertionError if something went subtly wrong :)
        """
        # Order
        n = self.num_players
        R = range(n)
        if isinstance(self.order, bool):
            specified_order = R if self.order else ()
        else:
            specified_order = self.order[:n]
        order = []
        lacking_indexes = list(set(R) - set(specified_order))
        random.shuffle(lacking_indexes)
        for v in specified_order:  # Assumed `None` or in `R`.
            order.append(lacking_indexes.pop() if v is None else v)
        order.extend(lacking_indexes)
        self.round_order = deque(order)
        # Starter
        if isinstance(self.starter, bool):
            starter = order[0] if self.starter else random.choice(R)
        else:
            starter = self.starter
        self.round_order.rotate(- self.round_order.index(starter) + 1)
        # Sanity checks
        assert len(order) == n and set(order) == set(R)

    def _end_game(self) -> None:
        self.is_over = True
        self.next_step = None

    ########################
    #     ROUND LOGIC      #
    ########################

    def _initialize_round(self) -> None:
        self.current_round += 1
        self._initialize_dice()
        self._draw_bills()
        self.round_order.rotate(-1)
        self.players_index_cycle = deque(self.round_order)
        self.first_player_index = self.round_order[0]
        self.next_step = self._initialize_turn

    def _initialize_dice(self) -> None:
        """ Casinos are empty, players get their starting dice.

        Special case of 1-player game handled.
        """
        casinos_dice = np.full((self.num_casinos, self.num_colours), 0)
        self.dice = np.r_[self.starting_dice, casinos_dice]
        if self.num_players == 1:
            self._solo_special_distribute()

    def _solo_special_distribute(self) -> None:
        """ In 1-player game, rounds start by special distribution. """
        for xtr_idx in random.sample(range(1, self.num_xtr_players + 1),
                                     self.solo_num_distrib):
            for _ in range(self.dice[0, xtr_idx]):
                dice = int(self.num_casinos * random.random())
                self.casinos_dice[dice, xtr_idx] += 1
            self.dice[0, xtr_idx] = 0

    def _draw_bills(self) -> None:
        """ Places bills under every casino at the start of a round.

        Under each casino, bills are sorted in ascending order.
        """
        for i in range(self.num_casinos):
            total = 0
            while total < self.casinos_min[i] and self.bills:
                bill = self.bills.popleft()
                self.casinos_bills[i].append(bill)
                total += bill
            self.casinos_bills[i].sort()

    def _give_bills(self) -> None:
        """ Gives won bills to players at the end of a round.

        Hypothesis: Casinos bills are sorted in ascending order.
        """
        # Looping over casinos
        for casino_bills, winners in zip(self.casinos_bills,
                                         self.get_winners()):
            # While there are still bills under this casino
            while casino_bills:
                bill = casino_bills.pop()
                # If there are still collecting winners
                if winners and (winner := winners.pop()) < self.num_collectors:
                    self.scores[winner] += [bill, 1]
                else:
                    self.bills.append(bill)

    def _end_round(self) -> None:
        self._give_bills()
        self.next_step = (
            self._initialize_round
            if self.current_round < self.num_rounds
            else self._end_game)

    ########################
    #      TURN LOGIC      #
    ########################

    def _initialize_turn(self) -> None:
        self._reset_roll_and_play()
        self.current_player_index = self.players_index_cycle.popleft()
        self.players_index_cycle.append(self.current_player_index)
        self.next_step = None

    def _reset_roll_and_play(self) -> None:
        self.played = self.rolled = None

    def _end_turn(self) -> None:
        self._move_dice()
        self._update_survival()
        self.next_step = (
            self._initialize_turn
            if self.players_index_cycle
            else self._end_round)

    def _move_dice(self) -> None:
        """ Moves dice from player to casino after roll and play.

        Hypothesis: `self.rolled` and `self.played` are properly set.
        """
        to_move = np.array([
            sub_roll.get(self.played, 0)
            for sub_roll in self.rolled])
        self.current_dice -= to_move
        self.casinos_dice[self.played] += to_move

    def _update_survival(self) -> None:
        """ Removes current player that doesn't have any dice left. """
        if not self.current_dice.any():
            self.players_index_cycle.pop()

    ########################
    #        UTILS         #
    ########################

    def _load_rules(self, rules: GameRules) -> None:
        """ Sets rule-related attributes according to `rules`. """
        attributes = (
            'bills_pool',
            'casinos_min',
            'max_dice',
            'num_casinos',
            'num_collectors',
            'num_colours',
            'num_players',
            'num_rounds',
            'num_xtr_players',
            'starting_dice',
            'solo_num_distrib',
            'with_xtr',
            'xtr_collect')
        for attr in attributes:
            setattr(self, attr, getattr(rules, attr))

    def dice_to_roll(self) -> NDArray[int]:
        """ Number of dice of each colour to roll. """
        if self.num_players == 1:
            return np.clip(self.current_dice, None, 1)
        else:
            return self.current_dice

    def roll_is_ok(self, rolled: Roll) -> bool:
        """ Sanity check on the roll.

        It checks the following three things:
            - The values rolled are authorized values,
            - For each value, the number of dice is positive,
            - The total number of dice rolled is coorect.
        """
        authorized = set(range(self.num_casinos))
        for num, sub_roll in zip(self.dice_to_roll(), rolled, strict=True):
            dice_val = set(sub_roll)
            dice_pos = [n >= 0 for d, n in sub_roll.items() if d in authorized]
            num_dice = sum(n for d, n in sub_roll.items() if d in authorized)
            if (dice_val <= authorized
                    and all(dice_pos)
                    and num_dice == num):
                continue
            break
        else:
            return True
        return False

    def rolled_asarray(self) -> NDArray[int]:
        """ Formats `self.rolled` as an occurrence array.

        Output has shape `(self.num_casinos, self.num_colours)`.
        """
        assert self.rolled is not None
        res = np.full(self.casinos_dice.shape, 0)
        for i, sub_roll in enumerate(self.rolled):
            for dice, qty in sub_roll.items():
                res[dice, i] = qty
        return res

    def legal_plays(self) -> set[int]:
        """ Returns legal plays given `self.rolled`.

        Careful, no sanitation of the roll.
        """
        assert self.rolled is not None, "No dice were rolled!"
        return set.union(*map(set, self.rolled))

    def get_winners(
            self,
            *,
            casinos_dice: NDArray[int] | None = None) -> list[list[int]]:
        """ Computes the winners for each casino, in reverse order.

        Following the rules, only players with dice and with a unique
        number of dice win. First (returned in last position) winner is
        the player with the most dice.

        Example: If number of dice on a casino are [1, 2, 4, 2, 0, 3],
        winners are [0, 5, 2]

        Implementation specific to the game, for low `self.max_dice`.
        For higher values, simpler implementation might be faster. To
        test eventually.

        Arguments:
        ----------
            casinos_dice (NDArray[int]): If not `None`, value to use
                instead of `self.casinos_dice`. Defaults to `None`. The
                *Warning*: if `max(cainos_dice) > self.max_dice`, which
                doesn't happen in normal use cases, an `IndexError` will
                occur.
        """
        if casinos_dice is None:
            casinos_dice = self.casinos_dice
        winners = []
        for casino_dice in casinos_dice:
            uniques = []
            occ = [2] + [0] * self.max_dice
            for val in casino_dice:
                occ[val] += 1
            for i, val in enumerate(casino_dice):
                if occ[val] == 1:
                    uniques.append(i)
            winners.append(sorted(uniques, key=casino_dice.__getitem__))
        return winners

    def get_gains(
            self,
            winners: list[list[int]],
            *,
            casinos_bills: list[list[int]] | None = None,
            who_unique: int | Sequence[int] | None = None) -> NDArray[int]:
        """ The gains of players given precomputed winners.

        Arguments:
        ----------
            winners (list[list[int]]): Precomputed winners for each
                casino of interest. Must have same length than
                `casinos_bills`.
            casinos_bills (list[list[int]] | None): If not `None`, the
                bills to win at every casino of interest. If `None`,
                equivalent to `self.casinos_bills`. Defaults to `None`.
            who_unique (int | Sequence[int] | None): If a `Sequance`,
                the gains of only these players will be computed. If an
                `int`, equivalent to `[who_unique]` but a bit faster. If
                `None`, equivalent to `range(self.num_collectors)`. As
                the name suggests, every index in `who_unique` must be
                unique. Defaults to `None`.

        Returns:
        --------
            gains (NDArray[int]): Gains associated to indexes in
                `who_unique`. Shape is `(len(who_unique), 2)` if
                `who_unique` is a `Sequence` and `(2,)` if an `int`.
        """
        if casinos_bills is None:
            casinos_bills = self.casinos_bills
        if isinstance(who_unique, int):
            gains = np.full(2, 0)
            for casino_winners, casino_bills in zip(winners,
                                                    casinos_bills,
                                                    strict=True):
                for winner, bill in zip(casino_winners[::-1],
                                        casino_bills[::-1]):
                    if winner == who_unique:
                        gains += [bill, 1]
                        continue
        else:
            if who_unique is None:
                who_unique = range(self.num_collectors)
            who_map = {w: i for i, w in enumerate(who_unique)}
            gains = np.full((len(who_unique), 2), 0)
            for casino_winners, casino_bills in zip(winners,
                                                    casinos_bills,
                                                    strict=True):
                for winner, bill in zip(casino_winners[::-1],
                                        casino_bills[::-1]):
                    if (idx := who_map.get(winner, None)) is not None:
                        gains[idx] += [bill, 1]
        return gains

    @staticmethod
    def _ordinal(n: int) -> str:
        """ 12 -> '12th', 23 -> '23rd' etc... """
        if 11 <= n % 100 <= 13:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return str(n) + suffix

    def rank_order(self,
                   *,
                   scores: NDArray[int] | None = None) -> NDArray[int]:
        """ Returns index from best to worst.

        Order between equal scores is `np.lexsort`-dependant.

        Arguments:
        ----------
            scores (NDArray[int]): If not `None`, value to use instead
                of `self.scores`. Defaults to `None`.
        """
        if scores is None:
            scores = self.scores
        order = np.flip(np.lexsort(np.rot90(scores)))
        return order

    def rankings(self, *, scores: NDArray[int] | None = None) -> NDArray[int]:
        """ Returns ranks, starting from `0`. Equals are computed.

        Arguments:
        ----------
            scores (NDArray[int]): If not `None`, value to use instead
                of `self.scores`. Defaults to `None`.
        """
        if scores is None:
            scores = self.scores
        order = self.rank_order(scores=scores)
        ranks = np.argsort(order)
        for i, ii in itertools.pairwise(order):
            if all(scores[ii] == scores[i]):
                ranks[ii] = ranks[i]
        return ranks

    def colours_name(
            self,
            *,
            players_name: Sequence[str] | None = None) -> NDArray:
        """ Outputs list of names associated with all colours. """
        out = (list(players_name)
               if players_name is not None
               else [f'Player {i}' for i in range(self.num_players)])
        if self.with_xtr:
            out += [f'Xtr {i}' for i in range(self.num_xtr_players)]
        out = np.array(out)
        return out

    ########################
    #    VISUALIZATION     #
    ########################

    def show(self,
             *,
             players_name: Sequence[str] | None = None,
             show_infos: bool = True,
             show_board: bool = True,
             show_roll: bool = True,
             show_scores: bool = True) -> None:
        if show_infos and not self.is_over:
            self.show_infos(players_name=players_name)
        if show_board:
            self.show_board(players_name=players_name)
        if show_roll and self.rolled is not None:
            self.show_roll(players_name=players_name)
        if show_scores:
            self.show_scores(players_name=players_name)

    def show_infos(self, *, players_name: Sequence[str] | None = None) -> None:
        """ Displays some info about current state.

        Example:
        --------
            ```
            Round: 4/4
            ► Player 0 ▹ Player 2 ▹ Player 1 ▹ ...
            ```
        """
        names = self.colours_name(players_name=players_name)
        print(f"\nRound: {self.current_round}/{self.num_rounds}")
        if self.players_index_cycle:
            coming = list(names[self.players_index_cycle])
            coming = [' '] + coming[-1:] + coming[:-1] + ['...']
            coming_str = ' ▹ '.join(coming)
            coming_str = coming_str.strip().replace('▹', '►', 1)
            print(coming_str)

    def show_board(self, *, players_name: Sequence[str] | None = None) -> None:
        """ Shows `self.dice` in a nice format.

        The headers of the columns of extra players determines whether
        (`✓`) or not (`✗`) they collect dice.

        Example:
        --------
            ```
            Board State:
            ╭───────────────┬──────────────┬───┬───┬───┬┬───╮
            │ Score / Bills │ Owned by     │ ▿ │ ▼ │   ││ ✗ │
            ├───────────────┼──────────────┼───┼───┼───┼┼───┤
            │    240000 (4) │ Player 0     │ 8 │   │   ││ 2 │
            │    250000 (5) │ ► Player 1 ◄ │   │ 8 │   ││ 2 │
            │    260000 (4) │ Player 2 (*) │   │   │ 5 ││ 2 │
            ├───────────────┼──────────────┼───┼───┼───┼┼───┤
            │   30000 50000 │ Casino 0     │   │   │   ││   │
            │         80000 │ Casino 1     │   │   │   ││   │
            │   20000 30000 │ Casino 2     │   │   │   ││   │
            │         50000 │ Casino 3     │   │   │ 3 ││   │
            │   20000 30000 │ Casino 4     │   │   │   ││   │
            │         50000 │ Casino 5     │   │   │   ││   │
            ╰───────────────┴──────────────┴───┴───┴───┴┴───╯
            ```
        """
        # Headers
        P, X = self.num_players, self.num_xtr_players
        xtr_symb = '✓' if self.xtr_collect else '✗'
        round_over = not bool(self.players_index_cycle)
        headers = (['Score / Bills', 'Owned by']
                   + [''] * (P + (X > 0))
                   + [xtr_symb] * X)
        if not round_over:
            headers[self.players_index_cycle[0] + 2] = '▿'  # Next player
            headers[self.current_player_index + 2] = '▼'  # Current player
        # Table
        lines = []
        # Players
        names = self.colours_name(players_name=players_name)
        for i, tot, num, name, dice in zip(range(P),
                                           *self.scores.T,
                                           names,
                                           self.dice):
            score_str = f"{tot} ({num})"
            if i == self.first_player_index:
                name = f"{name} (*)"
            if not round_over and i == self.current_player_index:
                name = f"► {name} ◄"
            line = [score_str, name]
            lines.append(line)
        # Casinos
        for i, (bills, dice) in enumerate(zip(self.casinos_bills,
                                              self.casinos_dice)):
            bills_str = ' '.join(map(str, bills))
            line = [bills_str, f'Casino {i}']
            lines.append(line)
        # Dice
        for line, dice in zip(lines, self.dice):
            dice = dice.astype(str)
            np.place(dice, dice == '0', [''])
            line.extend(dice if X == 0 else np.insert(dice, P, ''))
        # Tabulate
        colalign = ('right', 'left') + ('center',) * (len(headers) - 2)
        tablefmt = "rounded_outline"
        MIN_PADDING_bak = tabulate.MIN_PADDING
        tabulate.MIN_PADDING = 0
        table = tabulate.tabulate(lines,
                                  headers=headers,
                                  colalign=colalign,
                                  tablefmt=tablefmt)
        tabulate.MIN_PADDING = MIN_PADDING_bak
        # Thiner empty column by hand
        table_lines = table.split('\n')
        if X > 0:
            line_x = table_lines[1]
            sep = tabulate._table_formats[tablefmt].datarow.sep
            assert sep.strip() != '', "Choose a `tablefmt` with column sep."
            ir = line_x.rfind(sep, 0, line_x.find(xtr_symb))
            il = line_x.rfind(sep, 0, ir)
            table_lines = [line[:il+1] + line[ir:] for line in table_lines]
        # Horizontal Sep by hand (cuz bugged)
        table_lines = table_lines[:P+3] + [table_lines[2]] + table_lines[P+3:]
        table = '\n'.join(table_lines)
        print("\nBoard State:")
        print(table)

    def show_roll(self, *, players_name: Sequence[str] | None = None) -> None:
        """ Shows `self.rolled` in a nice format.

        Examples:
        ---------
            - With `self.xtr_collect is True`:
            ```
            Just Rolled:
            ╭────────────┬──────────────┬───────────────────╮
            │     Scores │ Players      │       Dice        │
            ├────────────┼──────────────┼───────────────────┤
            │ 240000 (5) │ ► Player 0 ◄ │ 0 0 │ 3 │ 4 4 │ 5 │
            │ 130000 (4) │ Xtr 0        │     │ 3 │     │   │
            ╰────────────┴──────────────┴───────────────────╯
            ```

            - With `self.xtr_collect is False`:
            ```
            Just Rolled:
            ╭────────────┬──────────────┬───────────────────────────╮
            │     Scores │ Players      │           Dice            │
            ├────────────┼──────────────┼───────────────────────────┤
            │ 250000 (5) │ ► Player 1 ◄ │ 0 │ 1 │ 2 2 │ 4   │ 5 5 5 │
            │      - (-) │ Xtr 0        │   │   │     │ 4 4 │       │
            ╰────────────┴──────────────┴───────────────────────────╯
            ```
        """
        if self.rolled is None:
            return
        # Scores with order
        order = self.rank_order()
        names = self.colours_name(players_name=players_name)
        # Roll strings
        D = range(self.num_casinos)
        max_d = np.array([max(sub_roll.get(dice, 0)
                              for sub_roll in self.rolled)
                          for dice in D])

        def dice_str(sub_roll, dice):  # E.g. `'4  '`.
            d = str(dice)
            k = sub_roll.get(dice, 0)
            return ' '.join([d] * k + [' ' * len(d)] * (max_d[dice] - k))
        all_sub_roll_str = np.array([' │ '.join(dice_str(sub_roll, dice)
                                                for dice in D if max_d[dice])
                                     for sub_roll in self.rolled])
        # Tabulate
        lines = []
        for i in order:
            sub_roll_str = all_sub_roll_str[i]
            if sub_roll_str.strip(' │'):
                name = names[i]
                if i == self.first_player_index:
                    name += ' (*)'
                if i == self.current_player_index:
                    name = f"► {name} ◄"
                tot, num = self.scores[i]
                line = [f"{tot} ({num})", name, sub_roll_str]
                lines.append(line)
        for i in range(self.num_collectors, self.num_colours):
            sub_roll_str = all_sub_roll_str[i]
            if sub_roll_str.strip(' │'):
                name = names[i]
                line = ["- (-)", name, sub_roll_str]
                lines.append(line)
        headers = ('Scores', 'Players', 'Dice')
        colalign = ('right', 'left', 'center')
        PRESERVE_WHITESPACE_bak = tabulate.PRESERVE_WHITESPACE
        MIN_PADDING_bak = tabulate.MIN_PADDING
        tabulate.PRESERVE_WHITESPACE = True
        tabulate.MIN_PADDING = 0
        table = tabulate.tabulate(lines,
                                  headers=headers,
                                  colalign=colalign,
                                  tablefmt="rounded_outline")
        tabulate.PRESERVE_WHITESPACE = PRESERVE_WHITESPACE_bak
        tabulate.MIN_PADDING = MIN_PADDING_bak
        # TODO
        print("\nJust Rolled:")
        print(table)

    def show_scores(
            self,
            *,
            players_name: Sequence[str] | None = None) -> None:
        """ Shows scores in a nice format.

        Example:
        --------
            - With `self.xtr_collect is True`:
            ```
            Rankings:
            ╭────────────┬──────────────┬─────╮
            │     Scores │ Players      │  #  │
            ├────────────┼──────────────┼─────┤
            │ 250000 (4) │ Player 2 (*) │ 1st │
            │ 240000 (5) │ ► Player 0 ◄ │ 2nd │
            │ 240000 (5) │ Player 1     │ 2nd │
            │ 130000 (4) │ Xtr 0        │ 4th │
            ╰────────────┴──────────────┴─────╯
            ```

            - With `self.xtr_collect is False`:
            ```
            Rankings:
            ╭────────────┬──────────────┬─────╮
            │     Scores │ Players      │  #  │
            ├────────────┼──────────────┼─────┤
            │ 260000 (4) │ Player 2 (*) │ 1st │
            │ 250000 (5) │ ► Player 1 ◄ │ 2nd │
            │ 240000 (4) │ Player 0     │ 3rd │
            ╰────────────┴──────────────┴─────╯
            ```
        """
        names = self.colours_name(players_name=players_name)
        round_over = not bool(self.players_index_cycle)
        # Rankings
        order = self.rank_order()
        ordered_scores = self.scores[order]
        ranks = np.arange(self.num_collectors)
        for i, (s, ss) in enumerate(itertools.pairwise(ordered_scores)):
            if np.all(s == ss):
                ranks[i+1] = ranks[i]
        # Headers and align
        headers = ('Scores', 'Players', '#')
        colalign = ('right', 'left', 'center')
        # Table
        lines = []
        for rank, i, (tot, num) in zip(ranks, order, ordered_scores):
            name = names[i]
            if i == self.first_player_index:
                name += ' (*)'
            if not round_over and i == self.current_player_index:
                name = f"► {name} ◄"
            line = [f"{tot} ({num})", name, self._ordinal(rank + 1)]
            lines.append(line)
        MIN_PADDING_bak = tabulate.MIN_PADDING
        tabulate.MIN_PADDING = 0
        table = tabulate.tabulate(lines,
                                  headers=headers,
                                  colalign=colalign,
                                  tablefmt="rounded_outline")
        tabulate.MIN_PADDING = MIN_PADDING_bak
        # Show
        print("\nLive Rankings:")
        print(table)
