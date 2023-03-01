""" Small package for simple performance measure in lasvegas.

Exported functions:
-------------------
    main: Runs multiple games and times execution.
"""

__all__ = ['main']

from typing import Any, Iterable

from time import perf_counter
from math import log10, ceil
from tqdm import tqdm
import numpy as np
import tabulate

from lasvegas.core import GameRules
from lasvegas.game import Player, Policy, Game


def main(policy: Policy | None = None,
         games: int = 1000,
         /,
         **ruleset: Any) -> None:
    """ Runs multiple games and times execution before displaying stats.

    Arguments:
    ----------
        policy (Policy | None): Policy used as all players in the game.
            If `None`, `Game` will use default -- uniformly random.
        games (int): Number of games to run and gather stats over.
        **ruleset (Any): Ruleset to use for performance measure. If
            `num_players` is not specified, all values from
            `GameRules.rulebook_min_players` to
            `GameRules.rulebook_max_players` will be tested.
    """
    all_num_players = (
        [ruleset.pop("num_players")]
        if "num_players" in ruleset
        else range(GameRules.rulebook_min_players,
                   GameRules.rulebook_max_players + 1))
    results = [
        run_ruleset(policy, games, num_players=num_players, **ruleset)
        for num_players in all_num_players]
    print(f"Game time for policy '{policy and policy.__name__}' "
          f"over {games} games:")
    display_results(all_num_players, results)


_TimeStat = tuple[float, float, float, float]


def run_ruleset(
        policy: Policy | None,
        games: int,
        **ruleset: Any) -> _TimeStat:
    """ Perf measurement logic, given a oplicy and ruleset.

    Elapsed time starts before `Game` instance creation and ends when
    the game is over:
    ```
    START                                                   END
      |game-instanciation-----game-is-played-----game-is-over|
    ```

    Arguments:
    ----------
        policy (Policy | None): Policy used for all players in the game.
        games (int): Number of games to run and time.
        **ruleset (Any): The ruleset used for measured game.

    Returns:
    --------
        mean, stdv, min_, max_ (_TimeStat): Respectively, the mean,
            standard deviation, min and max elapsed time over `games`
            games, in `ms`.
    """
    durations = np.zeros(games)
    num_players = ruleset["num_players"]
    players = [Player(play_func=policy) for _ in range(num_players)]
    for i in tqdm(range(games), desc=f"{num_players} players", leave=False):
        # Start
        start = perf_counter()
        Game(players)()
        # End
        end = perf_counter()
        durations[i] = end - start
    mean = np.mean(durations)
    stdv = np.std(durations)
    min_ = np.min(durations)
    max_ = np.max(durations)
    return mean, stdv, min_, max_


def display_results(
        all_num_players: Iterable[int],
        results: list[_TimeStat]) -> None:
    """ Displays results from multiple `run_ruleset` calls.

    Arguments:
    ----------
        all_num_players (Iterable[int]): All number of players tested.
        results: (list[_TimeStat]): The corresponding perf results.

    Example of output:
    ```
    Game time for policy 'None' over 1000 games:
    ╭─────────────┬─────────────┬─────────────┬─────────────┬────────────╮
    │ Num players │        Mean │         Std │         Min │        Max │
    ├─────────────┼─────────────┼─────────────┼─────────────┼────────────┤
    │           2 │ 0.000711025 │ 9.06734e-05 │ 0.000578454 │ 0.00165545 │
    │           3 │ 0.000890178 │ 0.000170405 │ 0.000722805 │ 0.0026636  │
    │           4 │ 0.00108281  │ 9.40196e-05 │ 0.000930123 │ 0.0018021  │
    │           5 │ 0.000998544 │ 9.2507e-05  │ 0.000860526 │ 0.00184985 │
    ╰─────────────┴─────────────┴─────────────┴─────────────┴────────────╯
    ```
    """
    headers = ["Num players", "Mean", "Std", "Min", "Max"]
    lines = [
        [num_players] + list(map(format_time, result))
        for num_players, result in zip(all_num_players, results)]
    print(tabulate.tabulate(lines, headers, "rounded_outline"))


def most_significant_digits(t: float) -> float:
    """ Returns the 3 most significant digits from a float """
    digit_count = 3
    magnitude = ceil(log10(t))
    digits = t // 10**(magnitude - digit_count)
    
    if magnitude % digit_count:
        magnitude_shift = digit_count - magnitude % digit_count
        digits /= 10**magnitude_shift

    return digits
    
def time_unit(t: float) -> str:
    """ Determines the unit of time """
    if t < 995e-9:
        unit = "ns"
    elif t < 995e-6:
        unit = "us"
    elif t < 995e-3:
        unit = "ms"
    else:
        unit = "ss"
    
    return unit

def format_time(t: float) -> str:
    """ Nicer format to read a (short) `float` duration in seconds. """
    if t < 1e-9:
        return f"{t * 1e9:.2f}ns"
        
    if t >= 1000:
        return f"{int(t)}ss"

    digits = most_significant_digits(t)
    unit = time_unit(t)
    return f"{digits:g}{unit}"
