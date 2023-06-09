""" Module defining the `Policy` protocol and some policies.

Exported Classes:
-----------------
    Policy (typing._ProtocolMeta): Type (protocol) of a policy.

Exported Functions:
-------------------
    greedy_first: Greedy for relative score to first, then second, ...
    greedy_score: Greedy for maximum absolute score.
    prompt_play: Prompts the user to give a play in CLI.
    random_play: Gives a random play.
"""

__all__ = [
    'Policy',
    'greedy_first',
    'greedy_score',
    'prompt_play',
    'random_play',
]

from typing import Any, Protocol, Sequence
import random

import numpy as np

from ._utils import prompt_integers
from ..core import GameEnv, Play


class Policy(Protocol):
    """ For type hinting. """
    def __call__(
        self,
        env: GameEnv,
        /,
        **kwargs: Any) -> Play | None: ...


def random_play(env: GameEnv, **__: Any) -> Play:
    """ Chooses a random legal play. """
    return random.choice(list(env.legal_plays()))


def prompt_play(
        env: GameEnv,
        *,
        players_name: Sequence[str] | None = None,
        **__) -> Play:
    """ Shows env state and prompts user to enter a play in CLI. """
    env.show(players_name=players_name)
    return prompt_integers("Your Play: ", 1, env.legal_plays().__contains__)[0]


def greedy_score(env: GameEnv, **__: Any) -> Play:
    """ Greedy for maximum absolute score. """
    rolled_arr = env.rolled_asarray()

    def net_gain_with_play(play):
        """ Net gain on casino `play` if chosen, for current player. """
        # Winner before and after `play`
        winners_before, winners_after = env.get_winners(
            casinos_dice=[env.casinos_dice[play],
                          env.casinos_dice[play] + rolled_arr[play]])
        # Score on casino `play` before playing
        for winner, bill in zip(winners_before[::-1],
                                env.casinos_bills[play][::-1]):
            if winner == env.current_player_index:
                before, num_before = bill, 1
                break
        else:
            before, num_before = 0, 0
        # Score on casino `play` after playing
        for winner, bill in zip(winners_after[::-1],
                                env.casinos_bills[play][::-1]):
            if winner == env.current_player_index:
                return bill - before, 1 - num_before
        return -before, -num_before
    return max(env.legal_plays(), key=net_gain_with_play)


def greedy_first(env: GameEnv, **__: Any) -> Play:
    """ Greedy for relative score to first, then second, ...

    Can choose to finish third instead of second if it means ending
    closer to first.
    """
    # Current state, before playing
    winners_before = env.get_winners()
    casinos_gains_before = [env.get_gains(
                                [winners_before[casino]],
                                casinos_bills=[env.casinos_bills[casino]])
                            for casino in range(env.num_casinos)]
    round_gains_before = np.sum(casinos_gains_before, axis=0)
    scores_before = env.scores + round_gains_before
    # After every play was made
    winners_after = env.get_winners(
        casinos_dice=env.casinos_dice + env.rolled_asarray())
    casinos_gains_after = [env.get_gains(
                               [winners_after[casino]],
                               casinos_bills=[env.casinos_bills[casino]])
                           for casino in range(env.num_casinos)]

    def relative_scores_after(play: int) -> tuple[int]:
        """ Sorted scores diff (other minus own). Less is better. """
        scores_after = (scores_before
                        - casinos_gains_before[play]
                        + casinos_gains_after[play])
        scores_after -= scores_after[env.current_player_index]
        sorted_scores_after = scores_after[env.rank_order(scores=scores_after)]
        return tuple(sorted_scores_after.ravel())
    return min(env.legal_plays(), key=relative_scores_after)
