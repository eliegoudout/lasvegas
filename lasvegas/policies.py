""" Module containing policies

Exported Functions:
-------------------
    cli: Policy to play from CLI.
    greedy_shy: A toy example of handcrafted policy.
"""

__all__ = ['cli', 'greedy_shy']

from .core import Play
from .game import Game
from .ui import display_game_state, prompt_play


def cli(game: Game) -> Play:
    """ For human in game, prompts the user to play in CLI. """
    display_game_state(game)
    return prompt_play(game)


def greedy_shy(game: Game) -> Play:
    """ Greedy but shy policy (non-uniform toy example).

    Tries to win big first bills in close fights, but abandons if too
    far from winning them. Has ~65% winrate in 1v1 against random.
    """
    best_casinos = sorted(range(game.num_casinos),
                          key=lambda i: game.casinos_bills[i][0],
                          reverse=True)
    me = game.current_player_index
    for i in best_casinos:
        if i not in game._legal_plays():
            continue
        casino_dice = game.casinos_dice[i]
        advantage = min([casino_dice[me] - dice
                         for adv, dice in enumerate(casino_dice)
                         if adv != me])
        if -1 <= advantage <= 1:
            return i
    # No good move: `game` will choose at random
    return None
