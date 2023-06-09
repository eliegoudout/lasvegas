""" Module adding interactive functionalities to the package.

Exported functions:
-------------------
    confront: Confront policies in multiple games.
    play_vs: Play in CLI against humans and/or policies.
"""

__all__ = ['confront', 'play_vs']

import itertools

from numpy.typing import NDArray
from tqdm import tqdm
import numpy as np
import tabulate

from .act import BasePlayer, Human, Policy
from .game import Game, _width


def play_vs(
        num_players: int | None = None,
        /,
        *,
        humans: int | list[str] = 1,
        policies: list[Policy | None] = [],
        out: bool = False,
        **gameargs) -> Game | None:
    """ Play a game in CLI.

    If `num_players` is not `None`, humans or policies may be omitted or
    added to match the number of players. This function prioritizes
    playing with humans over policies. If `num_players` is `None`, it is
    inferred from `humans` and `policies` and locally defined.

    Arguments:
    ----------
        humans (int | list[str]): Number of human players or list of
            human player names.
        num_players (int | None): Number of players if not `None`.
        out (bool): Whether or not to return the game at the end.
        policies (list[Policy | None]): List of policies to play against,
            `None` corresponding to `Game.default policy`.
        **gameargs: Passed to `Game` after `num_players` processing.

    Returns:
    --------
        game (Game | None): If not `None`, the `Game` instance that was
            used to play.
    """
    players = []
    # Human players
    if isinstance(humans, int):
        for i in range(humans):
            players.append(Human(f"Human {i}"))
    else:  # Names list
        for name in humans:
            players.append(Human(name))
    # Policy players
    for i, policy in enumerate(policies):
        players.append(
            BasePlayer(play_func=policy,
                       name=f"Policy {i}: {policy and policy.__name__}"))
    # Setup game
    if num_players is not None:
        gameargs["num_players"] = num_players
    game = Game(players, **gameargs)
    game.run()
    msg = "Game ended in the following state:"
    print(f"\n{msg}\n" + '-' * _width(msg), end='')

    game.env.show(show_roll=False, show_infos=False)
    if out:
        return game


def confront(
        *policies: Policy | None,
        games: int = 100,
        show: bool = True,
        out: bool = False,
        **gameargs) -> tuple | None:
    """ Confronts different policies in a multiple-games match.

    Results can be displayed in CLI and or output.
    If during a game several policies are ex-aequo, they all share the
    best of their ranks (e.g. 2nd, 3rd and 4th ex-aequo all become 2nd).

    Example of console output:
    ```
    Match in 100 games:
    ╭────────────────────────┬─────┬───────────────┬─────┬──────────────╮
    │ Policy                 │ 1st │ with          │ 2nd │ with         │
    ├────────────────────────┼─────┼───────────────┼─────┼──────────────┤
    │ Policy 0: greedy_first │  71 │ 596338 (10.0) │  29 │ 416207 (7.3) │
    │ Policy 1: greedy_score │  29 │ 527586 (8.7)  │  71 │ 398028 (7.1) │
    ╰────────────────────────┴─────┴───────────────┴─────┴──────────────╯
    ```

    Arguments:
    ----------
        games (int): Number of games the match is played over.
        out (bool): Whether or not to return the results.
        show (bool): Whether or not to show the results in CLI.
        *policies (Policy | None): Policies to confront.
        **gameargs: Passed to `Game` after `num_players` processing.

    Returns:
    --------
        results (tuple | None): If not `None`, `(rankings, avg_scores)`,
            where the `i`th line of `rankings` is the number of times
            `i`th policy finished in each place (from 1st to last), and
            corresponding value in `avg_scores` is its average score
            at this rank as `[avg_tot_bills, avg_num_bills]`
    """
    P = len(policies)
    gameargs["num_players"] = P
    players = [BasePlayer(play_func=policy,
                          name=f"Policy {i}: {policy and policy.__name__}")
               for i, policy in enumerate(policies)]
    # Match:
    # Loop over games
    game = Game(players, **gameargs)
    rankings = np.zeros((P, game.env.num_collectors))
    avg_scores = np.zeros((P, game.env.num_collectors, 2))
    for _ in tqdm(range(games)):
        game.run()
        # Find winner
        order = game.env.rank_order()
        ordered_scores = game.env.scores[order]
        ranks = np.arange(game.env.num_collectors)
        for i, (s, ss) in enumerate(itertools.pairwise(ordered_scores)):
            if np.all(s == ss):
                ranks[i+1] = ranks[i]
        for score, rank, i_pol in zip(ordered_scores, ranks, order):
            if i_pol < P:
                rankings[i_pol, rank] += 1
                avg_scores[i_pol, rank] += score  # (tot, num)
    avg_scores /= np.expand_dims(rankings, axis=-1)
    result = rankings, avg_scores
    # Show (?)
    if show:
        gameargs.pop("num_players")
        _display_confront(game,
                          result,
                          games,
                          gameargs_str=str(gameargs or ''))
    # Out (?)
    if out:
        return result


def _display_confront(
        game: Game,
        result: tuple[NDArray[int], NDArray[float]],
        games: int,
        *,
        gameargs_str: str = '') -> None:
    """ Prints human-readable results of policy confrontation.

    Example of output can be found in `.interactive.confront` doc.
    """
    headers = ["Policy"] + [x
                            for i in range(game.env.num_collectors)
                            for x in [game.env._ordinal(i + 1), 'with']]
    lines = []
    for player, ranks_occ, avg_scores in zip(game.players, *result):
        line = [player.name]
        for rank_occ, (avg_tot, avg_num) in zip(ranks_occ, avg_scores):
            if np.isnan(avg_tot):
                line += [rank_occ, "- (-)"]
            else:
                line += [rank_occ,
                         f'{round(avg_tot)} ({round(avg_num, ndigits=1)})']
        lines.append(line)
    # Tabulate
    PADDING_bak = tabulate.MIN_PADDING
    tabulate.MIN_PADDING = 0
    table = tabulate.tabulate(lines, headers, "rounded_outline")
    tabulate.MIN_PADDING = PADDING_bak
    # Print
    print(f"Match in {games} games"
          f"{' with ' + gameargs_str + ':' if gameargs_str else ':'}")
    print(table)
