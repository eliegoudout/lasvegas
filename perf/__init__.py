""" Small package for simple performance measure in lasvegas.

Exported functions:
-------------------
    main: Runs multiple games and times execution.
"""

__all__ = ['main']

from typing import Any, Iterable

from math import ceil, log10
from time import perf_counter
from tqdm import tqdm
import numpy as np
import tabulate

from lasvegas.core import GameRules
from lasvegas.game import Player, Policy, Game


TimeStat = tuple[float, float, float, float]


def main(policy: Policy | None = None,
         games: int = 1000,
         out: bool = False,
         /,
         **ruleset: Any) -> list[TimeStat] | None:
    """ Runs multiple games and times execution before displaying stats.

    Arguments:
    ----------
        policy (Policy | None): Policy used as all players in the game.
            If `None`, `Game` will use default -- uniformly random.
        games (int): Number of games to run and gather stats over.
        out (bool): Default is `False`, meaning results are only
            displayed. If `True`, results are only returned.
        **ruleset (Any): Ruleset to use for performance measure. If
            `num_players` is not specified, all values from
            `GameRules.rulebook_min_players` to
            `GameRules.rulebook_max_players` will be tested.

    Returns:
    --------
        results (list[TimeStat] | None): If `out`, list of all
            `(mean, stdv, min_, max_)` game time for every number of
            players tested.
    """
    all_num_players = (
        [ruleset.pop("num_players")]
        if "num_players" in ruleset
        else range(GameRules.rulebook_min_players,
                   GameRules.rulebook_max_players + 1))
    results = [
        run_ruleset(policy, games, num_players=num_players, **ruleset)
        for num_players in all_num_players]
    if out:
        return results
    else:
        print(f"Game time for policy '{policy and policy.__name__}' "
              f"over {games} games:")
        display_results(all_num_players, results)


def run_ruleset(
        policy: Policy | None,
        games: int,
        **ruleset: Any) -> TimeStat:
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
        mean, stdv, min_, max_ (TimeStat): Respectively, the mean,
            standard deviation, min and max elapsed time over `games`
            games, in `ms`.

    Raises:
    -------
        `AssertionError` if `not games > 0`.
    """
    assert games > 0
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
        results: list[TimeStat]) -> None:
    """ Displays results from multiple `run_ruleset` calls.

    Arguments:
    ----------
        all_num_players (Iterable[int]): All number of players tested.
        results: (list[TimeStat]): The corresponding perf results.

    Example of output:
    ```
    Game time for policy 'None' over 1000 games:
    ╭─────────────┬──────────┬──────────┬──────────┬──────────╮
    │ Num players │ Mean     │ Std      │ Min      │ Max      │
    ├─────────────┼──────────┼──────────┼──────────┼──────────┤
    │           2 │ 674.6 us │ 112.9 us │ 533.4 us │ 1.566 ms │
    │           3 │ 776.3 us │ 64.76 us │ 670.5 us │ 1.223 ms │
    │           4 │ 1.007 ms │ 152.7 us │ 841.8 us │ 2.440 ms │
    │           5 │ 918.3 us │ 75.86 us │ 809.7 us │ 1.457 ms │
    ╰─────────────┴──────────┴──────────┴──────────┴──────────╯
    ```
    """
    headers = ["Num players", "Mean", "Std", "Min", "Max"]
    lines = [
        [num_players] + list(map(format_time, result))
        for num_players, result in zip(all_num_players, results)]
    print(tabulate.tabulate(lines, headers, "rounded_outline"))


def format_time(duration: float, num_digits: int = 4) -> str:
    """ Formats a `float` duration in seconds to a readable `str`.

    A few examples with `num_digits = 4` are given below, showcasing
    some special cases.
    ```
    ╭───────────────┬────────────────┬───────────────────────────────────────╮
    │   Duration    │     Result     │                  Comment              │
    ├───────────────┼────────────────┼───────────────────────────────────────┤
    │      1.5      │    1.500 ss    │ Significant 0's added                 │
    │      0.56789  │    567.9 ms    │ Last digit is rounded...              │
    │      0.99995  │    1.000 ss    │ ...which can lead to precision loss   │
    │      0.12345  │    123.4 ms    │ Rounds half to even (python built-in) │
    │   1234        │    1234. ss    │ Point is added for constant witdh     │
    │  12345        │    12345 ss    │ One more digit for longer durations   │
    │ 123456        │ AssertionError │ Exceeded max duration                 │
    │     -1        │ AssertionError │ Negative duration                     │
    │      0        │    0.000 as    │ Smallest unit for shorter durations   │
    │      5.67e-20 │    0.057 as    │ Precision is worse near 0.            │
    ╰───────────────┴────────────────┴───────────────────────────────────────╯
    ```

    Implementation heavily relies on following facts:
        - Consecutive units have constant ratio of `10 ** 3`,
        - Highest unit is the unit of `duration`'s encoding.

    Arguments:
    ----------
        duration (float): Expressed in seconds, duration to format. Must
            satisfy `0 <= duration < 10 ** (num_digits + 1) - .5`.
        num_digits (int): Number of significant digits to display.
            Larger durations can have one more and shorter durations
            less -- see examples above.

    Returns:
    --------
        (str): Formated duration -- _e.g._ `'567.9 ms'`.

    Raises:
    -------
        `AssertionError` if either `num_digits < 3` or
            `not 0 <= duration < 10 ** (num_digits + 1) - .5`
    """
    units = ['ss', 'ms', 'us', 'ns', 'ps', 'fs', 'as']
    max_pow = 3 * (len(units) - 1)
    n = num_digits
    assert n >= 3
    assert 0 <= duration < 10 ** (n+1) - .5, "Duration out of bounds."
    # Special case 0
    if duration == 0:
        return f"{0:.{n-1}f} " + units[-1]
    # Retrieve left shift for significant part
    left_shift = ceil(- log10(duration)) + n - 1
    significant = round(duration * 10 ** left_shift)
    # Special case `0.0099996` -> `'10.00ms'`
    if significant == 10 ** n:
        significant //= 10
        left_shift -= 1
    # If `duration` is barely too big: remove floating point
    if left_shift == -1:
        return f"{round(duration)} " + units[0]
    # Nominal case
    elif left_shift < max_pow + n:
        unit_index = max(0, 1 + (left_shift - n) // 3)
        y = significant * 10 ** (3 * unit_index - left_shift)
        n_left = int(log10(y) + 1)
        unit = units[unit_index]
        return f"{y:.{max(0, n-n_left)}f}{'.' if n == n_left else ''} " + unit
    # If so small that smallest unit loses precision
    else:
        return f"{duration * 10 ** max_pow:.{n-1}f} " + units[-1]
