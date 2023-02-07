""" Module adding interactive functionality.

Exported functions:
-------------------
    confront: Confront policies in multiple games.
    play_vs: Play in CLI against humans and/or policies.
"""

__all__ = ['confront', 'play_vs']

from tqdm import tqdm
import numpy as np

from .game import Game, Player, Policy
from .policies import cli
from .ui import display_confront, display_game_state


def play_vs(
        num_players: int | None = None,
        /,
        *,
        policies: list[Policy | None] = [],
        humans: int | list[str] = 1,
        out: bool = False) -> None:
    """ Play a game in CLI.

    If `num_players` is not `None`, humans or policies may be omitted or
    added to match the number of players. This function priorities
    playing with humans over policies. If `num_players` is `None`, it is
    inferred from `humans` and `policies` and locally defined
    `_min_players`.

    Arguments:
    ----------
        num_players (int | None): Number of players if not `None`.
        policies (list[Policy | None]): List of policies to play against,
            `None` corresponding to `Game`'s builtin default policy.
        humans (int | list[str]): Number of human players or list of
            human player names.
        out (bool): Whether or not to return the game at the end.
    """
    _min_players = 2  # Arbitrary.
    players = []
    # Human players
    if isinstance(humans, int):
        for i in range(humans):
            players.append(Player(play_func=cli, name=f"Human {i}"))
    else:  # Names list
        for i, name in enumerate(humans):
            players.append(Player(play_func=cli, name=name))
    # Policy players
    for i, policy in enumerate(policies):
        players.append(Player(play_func=policy,
                              name=f"Policy {i}: {policy.__name__}"))
    # Setup game
    if num_players is None:
        g = Game(players, num_players=max(_min_players, len(players)))
    else:
        g = Game(players[:num_players], num_players=num_players)
    # Play and end
    g()
    print("Game ended in the following state:")
    display_game_state(g)
    if out:
        return g


def confront(
        *policies: Policy | None,
        games: int = 100,
        show: bool = True,
        out: bool = False) -> tuple | None:
    """ Confronts different policies in a `games`-games match.

    Results can be displayed in CLI and or output.
    If during a game several policies are ex-aequo, they all share the
    best of their ranks (e.g. 2nd, 3rd and 4th ex-aequo all become 2nd).

    Example of console output:
    ```
    >>> confront(None, lasvegas.policies.greedy_shy)
    Match in 100 games:
    ╭──────────────────────┬─────┬────────┬─────┬────────╮
    │ Policy               │ 1st │   with │ 2nd │   with │
    ├──────────────────────┼─────┼────────┼─────┼────────┤
    │ Policy 0: None       │  35 │ 506000 │  65 │ 381846 │
    │ Policy 1: greedy_shy │  66 │ 529848 │  34 │ 397059 │
    ╰──────────────────────┴─────┴────────┴─────┴────────╯
    ```

    Arguments:
    ----------
        *policies (Policy | None): Policies to confront.
        games (int): Number of games the match is played over.
        out (bool): Whether or not to return the results.
        show (bool): Whether or not to show the results in CLI.

    Returns:
    --------
        results (tuple | None): If not `None`, `(rankings, avg_scores)`,
            where the `i`th line of `rankings` is the number of times
            `i`th policy finished in each place (from 1st to last), and
            corresponding value in `avg_scores` is its average score
            at this rank.
    """
    n = len(policies)
    rankings = np.zeros((n, n))
    avg_scores = np.zeros((n, n))
    players = [
        Player(play_func=policy,
               name=f"Policy {i}: {policy and policy.__name__}")
        for i, policy in enumerate(policies)]
    # Match:
    # Loop over games
    for _ in tqdm(range(games)):
        g = Game(players)
        g()
        # Find winner
        scores = [(0, 0)] * n
        for i in range(n):
            bills = g.players_bills[i]
            scores[g.players_permutation[i]] = (sum(bills), len(bills))
        order = sorted(range(n), key=lambda i: scores[i], reverse=True)
        ranks = sorted(range(n), key=lambda i: order[i])
        # Reajust draws (if 2nd == 3rd, both 2nd)
        for s, i in list(enumerate(order)):
            if i == 0:
                continue
            if scores[i] == scores[order[s-1]]:
                ranks[i] = ranks[order[s-1]]
        # Update ranking: `i` reresents  policy index and `r` its rank.
        for i, r in enumerate(ranks):
            rankings[i][r] += 1
            avg_scores[i][r] += scores[i][0]
    avg_scores /= rankings
    result = rankings, avg_scores
    # Show (?)
    if show:
        display_confront(players, result, games)
    # Out (?)
    if out:
        return result
