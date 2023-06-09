🎲 Las Vegas 🎲
================

This package revolves around *Las Vegas*, the dice boardgame edited by [Ravensburger](https://www.ravensburger.fr/produits/jeux-de-soci%C3%A9t%C3%A9/jeux-d-ambiance/las-vegas-26745/index.html) and provides:

- a CLI playing mode against humans and/or (possibly custom) agents, with highly customizable rules,
- a simple confrontation tool for multiple agents,
- an agnostic game environment, for agent implementation/training.

### Table of contents

[**⚙️ Getting started**](#%EF%B8%8F-getting-started-%EF%B8%8F)<br>
[**📜 Custom rules**](#-custom-rules-)<br>
[**🎮 Game environment**](#-game-environment-)<br>
[**🤖 Agents**](#-agents-)<br>
[**🏆 A.I. Competition -- Leaderboard**](#-ai-competition----leaderboard-)<br>
[**⏱ Execution time analysis**](#-execution-time-analysis-)<br>
[**⚖️ License**](#%EF%B8%8F-license-%EF%B8%8F)<br>
[**🚧 Contributing**](#-contributing-)<br>
[**🙏 Contributors**](#-contributors-)<br>


## ⚙️ Getting started ⚙️

### 0. Requirements

**Python 3.10** or higher is required. The package depends on the following third-party packages: [numpy](https://github.com/numpy/numpy), [tabulate](https://github.com/astanin/python-tabulate), [tqdm](https://github.com/tqdm/tqdm).

### 1. Install with `pip`

```bash
python3 -m pip install lasvegas
```

<details>
    <summary>... or from source.</summary>

From the folder of your choice -- *e.g.* `~/workspace/` --, execute the following commands.

```bash
git clone https://github.com/eliegoudout/lasvegas
cd lasvegas/
python3 -m pip install .
```

</details>

### 2. Check your installation

From your python interpreter, you should be able to import the package:

```python
import lasvegas
```

<details>
    <summary>Package summary</summary>

```
NAME
    lasvegas - Las Vegas (boardgame) API package.

DESCRIPTION
    Exported Classes:
    -----------------
        BasePlayer: Contains player's name and behaviour.
        Game: Class to run games with player instances.
        GameEnv: Core mechanics of the game.
        GameRules: Class to set (eventually custom) rules.
        Human: Sub-class of `BasePlayer` destined for CLI use.  

    Exported Functions: 
    ------------------- 
        confront: Confronts different policies in a multiple-games match.   
        play_vs: Play a game in CLI.    

PACKAGE CONTENTS
    act (package)
    core (package)
    game
    interactive
```

</details>

<details>
    <summary>Relevant package structure</summary>

```
lasvegas/
 ├─ act/
 │   ├─ player.py
 │   │      BasePlayer
 │   │      Human
 │   ├─ policy.py
 │   │      Policy
 │   │      greedy_first
 │   │      greedy_score
 │   │      prompt_play
 │   │      random_play
 │   └─ rollicy.py
 │          Rollicy
 │          prompt_roll
 │          random_roll
 ├─ core/
 │   ├─ env.py
 │   │      GameEnv
 │   │      Play
 │   │      Roll
 │   └─ rules.py
 │          GameRules
 │          RuleBook
 ├─ game.py
 │      Game
 └─ interactive.py
        confront
        play_vs
```

</details>

### 3. Start a game with `play_vs`

This function creates an appropriate `Game` instance and calls its `run` method. For example, you can quickly start a solo game,

```python
from lasvegas import play_vs
play_vs()  # Solo (default)
```

or make *Alice* and *Bob* face a *Bot*.

```python
play_vs(3, humans=["Alice", "Bob"])  # 3-player game with a Bot
```

### 4. Quick breakdown

Let's break down what *Bob* might see during his turn.

#### The Summary

```
Round 1/4
► Bob ▹ Alice ▹ Bot 0 ▹ ...
```

<details>
    <summary>Click for details</summary>

The first line is explicit. The second line lists the current player and the upcoming ones. Players with no more dice in the current round are not showed. The Ellipsis indicates a loop around.

</details>

#### The Board State

```
Board State:
╭───────────────────┬───────────┬───┬───┬───┬┬───╮
│     Score / Bills │ Owned by  │ ▿ │ ▼ │   ││ ✗ │
├───────────────────┼───────────┼───┼───┼───┼┼───┤
│             0 (0) │ Alice     │ 8 │   │   ││ 2 │
│             0 (0) │ ► Bob ◄   │   │ 8 │   ││ 2 │
│             0 (0) │ Bot 0 (*) │   │   │ 7 ││ 1 │
├───────────────────┼───────────┼───┼───┼───┼┼───┤
│             50000 │ Casino 0  │   │   │   ││   │
│             90000 │ Casino 1  │   │   │   ││   │
│             60000 │ Casino 2  │   │   │ 1 ││ 1 │
│       30000 90000 │ Casino 3  │   │   │   ││   │
│ 10000 20000 50000 │ Casino 4  │   │   │   ││   │
│             70000 │ Casino 5  │   │   │   ││   │
╰───────────────────┴───────────┴───┴───┴───┴┴───╯
```

<details>
    <summary>Click for details</summary>

The first column shows both the scores of the players as `<total score> (<number of bills won>)` and the bills to win at every casino this round.

Every line shows how many dice of every type are at the corresponding player/casino. The first dice columns refer to players (same order than players lines), and the last columns refer to extra players.

In the header, `▼` denotes the current player and `▿` the next one. Regarding the extra players columns, depending on whether or not they collect bills and have their own score, the header is `✓` or `✗`. The first player of the current round has the *first player chip* `(*)`, and the current player is highlighted like `► this ◄`.

</details>

#### The Roll Table

```
Just Rolled:
╭────────┬─────────┬─────────────────────────╮
│ Scores │ Players │          Dice           │
├────────┼─────────┼─────────────────────────┤
│  0 (0) │ ► Bob ◄ │ 0 0 │ 1 1 │ 2 │ 3 3 │ 4 │
│  - (-) │ Xtr 0   │ 0   │     │ 2 │     │   │
╰────────┴─────────┴─────────────────────────╯
```

<details>
    <summary>Click for details</summary>

This is formatted to resemble what a player would see in real life after having sorted every dice rolled. For example, one can quickly see that `Bob` rolled three `0`s, one of which is from `Xtr 0`'s. Since this extra player doesn't collect bills, it has no score.

</details>

#### Live Rankings

```
Live Rankings:
╭────────┬───────────┬─────╮
│ Scores │ Players   │  #  │
├────────┼───────────┼─────┤
│  0 (0) │ Bot 0 (*) │ 1st │
│  0 (0) │ ► Bob ◄   │ 1st │
│  0 (0) │ Alice     │ 1st │
╰────────┴───────────┴─────╯
```

<details>
    <summary>Click for details</summary>

This is explicit. When players are ex aequo, they are assigned the same -- best -- rank,

</details>

#### You are now prompted to play 👇

```
Your Play: █
```

Good luck! 🍀


## 📜 Custom rules 📜

The rules are **highly customizable** in numerous ways, let's have a quick overview -- refer to `help(GameRules)` for full documentation.

### 1. Number of players

It is possible to play with `num_players > 5`. Since the [Rulebook](rules.pdf) doesn't cover this case, it is then necessary to specify the number of extra players `num_xtr_players` and if any, their number of dice `num_xtr_dice` as well as whether or not they collect bills at the end of every round, with `xtr_collect`.

### 2. Number of dice

The number of dice of regular players `num_own_dice` always defaults to `8`.

A fun extension of the game consists in giving players dice from other players. This can be done in an arbitrary way by directly passing a `starting_dice` 2d-matrix, where coefficient at index `ij` is the number of dice of colour `j` that player `i` starts with. The shape of such a matrix is necessarily `(num_players, num_players + num_xtr_players)`. Thus, if used, this keyword automatically defines those two variables.

```pycon
>>> play_vs(starting_dice=[[7, 1, 3], [2, 6, 3]])
[...]
├───────────────────┼─────────────────┼───┼───┼┼───┤
│             0 (0) │ ► Human 0 (*) ◄ │ 7 │ 1 ││ 3 │
│             0 (0) │ Bot 0           │ 2 │ 6 ││ 3 │
├───────────────────┼─────────────────┼───┼───┼┼───┤
```

### 3. Players order

It is possible to partially or completely set the players order for the first round. By default, the order is completely randomized at game initialiazation. But you can control it in 2 ways: via the round `order` -- *i.e.* "who comes after who?" -- and the `starter` -- *i.e.* "who starts the game?".

Here is an example from `GameEnv` docstring:

> In a 5-player game, `order=(3, None, 1)` means that player `1` will be placed 2
> turns after player `3` in the cycle, but the relative position of `0`, `2` and `4` is still set randomly at game initialization.

In this example, it is still possible to set `starter=4` for example.

### 4. Miscellaneous

In addition, you can also modify the number of **faces of dice** -- which corresponds to the number of casinos --, all the **bills** in the game, how much money should be at a **minimum under each casino** individually, the number of **rounds** and even, in **solo** games, how many extra players distribute their dice at the beginning of every round.

As an example, you can try to win a solo game in ***Master*** mode, from the [Rulebook](rules.pdf):

```python
play_vs(num_own_dice=1, solo_num_distrib=2)
```


## 🎮 Game Environment 🎮

From the bottom up, a `Game` instance consists of:

- a set of rules,
- a core environment, built on top of rules,
- players with individual playing and rolling behaviours.

The environment is an instance of `GameEnv`.

<details>
    <summary>Click to show the attributes/properties of a `GameEnv` instance.</summary>

```
Attributes:
-----------
    bills_pool (NDArray[int])        num_xtr_players (int)
    casinos_min (NDArray[int])       order (Sequence[int | None] | bool)
    max_dice (int)                   solo_num_distrib (int)
    num_casinos (int)                starter (int | bool)
    num_collectors (int)             starting_dice (NDArray[int])
    num_colours (int)                with_xtr (bool)
    num_players (int)                xtr_collect (bool)
    num_rounds

Attributes Upon Use:
--------------------
    bills (deque)                    next_step (Callable)
    casinos_bills (list[list[int]])  played (Play | None)
    current_player_index (int)       players_index_cycle (deque)
    current_round (int)              rolled (Roll | None)
    dice (NDArray[int])              round_order (deque)
    first_player_index (int)         scores (NDArray[int])
    is_over (bool | None)

Properties:
-----------
    casinos_dice [get, set] (NDArray[int])
    current_dice [get, set] (NDArray[int])
```

</details>


## 🤖 Agents 🤖

An **agent** is simply a player -- human or not -- defined by its playing and rolling behaviours. You can instanciate one with

```python
from lasvegas import BasePlayer
BasePlayer(name='My Agent', play_func=my_policy, roll_func=my_rollicy)
```

### 1. Policy

#### Definition

The primary purpose of this package is to provide a *policy* implementation/evaluation framework. In our context, a `Policy` is any such function,

```python
def my_policy(env: GameEnv, **__: Any) -> Play | None:
```

that outputs a `Play` (`int`) given an environment snapshot. If it outputs `None`, then `Game.default_policy` -- *i.e.* `random_play` by default -- is called. *Don't mind `**__`, it is only used by the game instance to pass players names when playing from CLI, for nicer display.*

#### Custom policy

As an example, here's a policy that avoids playing many dice:
```python
from typing import Any
from lasvegas.core import GameEnv, Play

def saver(env: GameEnv, **__: Any) -> Play:
    """ Plays the least dice possible. """
    return min(env.legal_plays(),
               key=lambda play: sum(sub_roll.get(play, 0)
                                    for sub_roll in env.rolled))
```

### 2. Rollicy

You can also define a **custom rolling behaviour** for your agent. This allows to simulate biased dice or, for example,  to manually enter rolls in CLI with the implemented rollicy `prompt_roll`:

```pycon
>>> from lasvegas.act import BasePlayer, prompt_play, prompt_roll
>>> my_player = BasePlayer("Alice", play_func=prompt_play, roll_func=prompt_roll)
```

which is equivalent to the simpler

```pycon
>>> from lasvegas import Human
>>> my_player = Human("Alice", manual_roll=True)
```

*__Note__: In solo games, the action of distributing one bot's dice at the beginning of every round is seen as an environment action. As such, the dice throw uses `random_roll` and not the player's `Rollicy`.*


## 🏆 A.I. Competition -- Leaderboard 🏆

### 1. Benchmarking

The package comes with a simple benchmarking function, `confront`, which runs multiple games between given policies and sums up the results.

For example, let's see how our previously defined policy, `saver`, does against package-embedded `greedy_first`:

```pycon
>>> from lasvegas import confront
>>> confront(saver, greedy_first)
Match in 100 games:
╭────────────────────────┬─────┬──────────────┬─────┬──────────────╮
│ Policy                 │ 1st │ with         │ 2nd │ with         │
├────────────────────────┼─────┼──────────────┼─────┼──────────────┤
│ Policy 0: saver        │  17 │ 477059 (8.6) │  83 │ 334096 (6.4) │
│ Policy 1: greedy_first │  83 │ 532289 (8.7) │  17 │ 401176 (6.8) │
╰────────────────────────┴─────┴──────────────┴─────┴──────────────╯
```

### 2. Competition 🥇🥈🥉

If you are interested in defining one or more competition formats, leaderboards will be held and updated here! This is your chance to leave your mark for posterity while improving your AI skills and potentially helping the community. 🤗


## ⏱ Execution time analysis ⏱

From sources, in the root folder, you can measure the time it takes for games to be played using the light embeded `perf` package:

- From CLI: `python3 -m perf [<num_games>]` for default uniformly random policy,
- From python interpreter: by importing `perf` as a package and using the `main` function. This allows you to specify the tested policy and custom game settings.

Output should look like this:
```console
$ python3 -m perf
Game time for policy 'None' (over 100 games):
╭─────────────┬──────────┬──────────┬──────────┬──────────╮
│ Num players │ Mean     │ Std      │ Min      │ Max      │
├─────────────┼──────────┼──────────┼──────────┼──────────┤
│           1 │ 5.530 ms │ 522.1 us │ 4.876 ms │ 7.929 ms │
│           2 │ 1.627 ms │ 196.1 us │ 1.391 ms │ 2.626 ms │
│           3 │ 2.013 ms │ 168.7 us │ 1.698 ms │ 2.873 ms │
│           4 │ 2.615 ms │ 207.4 us │ 2.309 ms │ 3.758 ms │
│           5 │ 2.723 ms │ 225.8 us │ 2.450 ms │ 3.794 ms │
╰─────────────┴──────────┴──────────┴──────────┴──────────╯
```
*__Note__: Dependencies should be installed.*


## ⚖️ License ⚖️

This package is distributed under the [MIT License](LICENSE).


## 🚧 Contributing 🚧

Questions, [issues](https://github.com/eliegoudout/lasvegas/issues), [discussions](https://github.com/eliegoudout/lasvegas/discussions) and [pull requests](https://github.com/eliegoudout/lasvegas/pulls) are welcome! Please do not hesitate to [contact me](mailto:eliegoudout@hotmail.com).


## 🙏 Contributors 🙏

Élie Goudout, Csongor Pilinszki-Nagy.
