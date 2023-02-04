""" Module implementing UI-related functions.

Exported Functions:
-------------------
    display_casinos_state
    display_confront
    display_game_state
    display_players_state
    display_roll
    display_round
    prompt_integers
    prompt_play
"""

__all__ = [
    'display_casinos_state',
    'display_confront',
    'display_game_state',
    'display_players_state',
    'display_roll',
    'display_round',
    'prompt_integers',
    'prompt_play']

from typing import Callable, Iterable

import itertools
import tabulate

from .core import Play
from .game import Game, Player


Condition = Callable[[int], bool]


tabulate.MIN_PADDING = 0


def prompt_integers(message: str, n: int, *conditions: Condition) -> list[int]:
    """ Prompts the user to give `n` integers, obeying unary conditions.

    Arguments:
    ----------
        message (str): Message for the user.
        n (int): Number of expected integers.
        *conditions (Condition): Unary conditions that should be met by user
            inputs.
    """
    while True:
        # Prompt integers
        try:
            inputs = list(map(int, input(message).split()))
        except ValueError:
            print("Expected type `int`!")
            continue
        # Check number of inputs
        if len(inputs) != n:
            print(f"Expected {n} inputs (got {len(inputs)})!")
            continue
        # Check conditions are met
        for condition, value in itertools.product(conditions, inputs):
            if not condition(value):
                print(f"Invalid input: {value}!")
                break
        # All good
        else:
            return inputs


def prompt_play(game: Game) -> Play:
    """ Prompts user to play (with legal check). """
    return prompt_integers("Your play: ",
                           1,
                           lambda play: play in game._legal_plays())[0]


def prompt_roll(*_, **__):
    raise NotImplementedError


def display_game_state(game: Game) -> None:
    """ Prints human-readable state of the game in CLI.

    Example of output:
    ```
    Round: 3/4
    Casinos:
    ╭─────────────┬──────────┬───┬───┬───┬───┬───╮
    │       Bills │ Casinos  │   │ ▼ │   │   │ × │
    ├─────────────┼──────────┼───┼───┼───┼───┼───┤
    │       50000 │ Casino 0 │ 0 │ 0 │ 2 │ 1 │ 0 │
    │ 20000 90000 │ Casino 1 │ 1 │ 2 │ 3 │ 3 │ 1 │
    │ 30000 80000 │ Casino 2 │ 1 │ 1 │ 3 │ 0 │ 2 │
    │ 20000 40000 │ Casino 3 │ 0 │ 0 │ 0 │ 0 │ 0 │
    │       50000 │ Casino 4 │ 1 │ 0 │ 0 │ 3 │ 1 │
    │       50000 │ Casino 5 │ 4 │ 1 │ 0 │ 0 │ 2 │
    ╰─────────────┴──────────┴───┴───┴───┴───┴───╯
    Players:
    ╭────────┬──────────────────────────┬─────┬─────╮
    │ Scores │ Players                  │ Own │ Xtr │
    ├────────┼──────────────────────────┼─────┼─────┤
    │  90000 │ Bot 0                    │   1 │   0 │
    │ 250000 │ ►Human 1: Bob◄           │   4 │   2 │
    │ 120000 │ Policy 0: greedy_shy (*) │   0 │   0 │
    │ 110000 │ Human 0: Alice           │   1 │   0 │
    ╰────────┴──────────────────────────┴─────┴─────╯
    Roll:
    ╭─────┬───┬─────┬───┬───╮
    │ Own │   │ 2 2 │ 3 │ 4 │
    │ Xtr │ 1 │ 2   │   │   │
    ╰─────┴───┴─────┴───┴───╯
    ```
    """
    display_round(game)
    display_casinos_state(game)
    display_players_state(game)
    if game.roll_own is not None and not game.is_over:
        display_roll(game)


def display_round(game: Game) -> None:
    """ Prints human-readable current round of the game in CLI.

    Example of output can be found in `display_game_state` doc.
    """
    print(f"Round: {game.current_round + 1}/{game.num_rounds}")


def display_casinos_state(game: Game) -> None:
    """ Prints human-readable state of casinos in CLI.

    Example of output can be found in `display_game_state` doc.
    """
    # Style
    bill_sep = ' '
    current_player_marker = '▼'
    neutral_player_marker = '×'
    # Headers
    players_header = [''] * game.num_players
    if game.with_xtr:
        players_header.append(neutral_player_marker)
    if not game.is_over:
        players_header[game.current_player_index] = current_player_marker
    headers = ['Bills', 'Casinos'] + players_header
    # Table
    lines = []
    for num in range(game.num_casinos):
        bills = game.casinos_bills[num]
        bills_str = bill_sep.join(map(str, bills))
        dice = game.casinos_dice[num]
        lines.append([bills_str, f"Casino {num}"] + dice)
    # Print
    print("Casinos:")
    print(tabulate.tabulate(lines,
                            headers,
                            "rounded_outline",
                            colalign=('right',)))


def display_players_state(game: Game) -> None:
    """ Prints human-readable state of players in CLI.

    Example of output can be found in `display_game_state` doc.
    """
    # Style
    headers = ['Scores', 'Players', 'Own', 'Xtr']
    ukn_name = '<ukn>'
    first_player_fmt = "{} (*)"
    current_player_fmt = "► {} ◄"
    # Logic
    lines = []
    for index, bills in enumerate(game.players_bills):
        displayed_name = game.players[index].name or ukn_name
        if index == game.first_player_index and not game.is_over:
            displayed_name = first_player_fmt.format(displayed_name)
        if index == game.current_player_index and not game.is_over:
            displayed_name = current_player_fmt.format(displayed_name)
        line = [sum(bills), displayed_name, game.players_own_dice[index]]
        if game.with_xtr:
            line.append(game.players_xtr_dice[index])
        lines.append(line)
    # Print
    print("Players:")
    print(tabulate.tabulate(lines, headers, "rounded_outline"))


def display_roll(game: Game) -> None:
    """ Prints human-readable roll in CLI.

    Example of output can be found in `display_game_state` doc.
    """
    # Logic
    rolls = [game.roll_own] + ([game.roll_xtr] if game.with_xtr else [])
    no_dice = set.intersection(*[{i for i, v in enumerate(roll) if v == 0}
                                 for roll in rolls])
    lines = []
    for title, roll in zip(['Own', 'Xtr'], rolls):
        line = [title]
        # Loop of dice values
        for value, quantity in enumerate(roll):
            if value not in no_dice:
                value_dice_str = ' '.join([str(value)] * quantity)
                line.append(value_dice_str)
        lines.append(line)
    # Print
    print("Roll:")
    print(tabulate.tabulate(lines, tablefmt="rounded_outline"))


def display_confront(players: list[Player], result: tuple, games: int) -> None:
    """ Prints human-readable results of policy confrontation.

    Example of output can be found in `.interactive.confront` doc.
    """
    ordinal = _ordinal_generator()
    headers = ["Policy"] + [x
                            for _ in range(len(players))
                            for x in [next(ordinal), 'with']]
    lines = []
    for p, r, s in zip(players, *result):
        line = [p.name] + [x for r_s in zip(r, s) for x in r_s]
        lines.append(line)
    print(f"Match in {games} games:")
    print(tabulate.tabulate(lines, headers, "rounded_outline"))


def _ordinal_generator() -> Iterable[int]:  # From ChatGPT
    """ Generates '1st', '2nd', '3rd', etc... """
    i = 1
    while True:
        if i % 10 == 1 and i % 100 != 11:
            yield str(i) + "st"
        elif i % 10 == 2 and i % 100 != 12:
            yield str(i) + "nd"
        elif i % 10 == 3 and i % 100 != 13:
            yield str(i) + "rd"
        else:
            yield str(i) + "th"
        i += 1
