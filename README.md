# 🎲 Las Vegas 🎲

This package revolves around _Las Vegas_, the dice boardgame edited by [Ravensburger](https://www.ravensburger.fr/produits/jeux-de-soci%C3%A9t%C3%A9/jeux-d-ambiance/las-vegas-26745/index.html). It provides:

- a CLI playing mode, against humans and/or (possibly custom) agents,
- a simple confrontation tool for multiple agents.
- an agnostic game environment, for agent implementing training,

## 🤓 Requirements 🤓

- [numpy](https://github.com/numpy/numpy)
- [tabulate](https://github.com/astanin/python-tabulate)
- [tqdm](https://github.com/tqdm/tqdm) (recommended for benchmarking)


## 🤜 Play with friends 🤛

Let's start a game, **me** vs **you** vs a **bot** (3 players)! From the folder containing the package, simply type
```pycon
from las_vegas import *
play_vs(3, humans=["Me", "You"])
```

You are then prompted to play:
```pycon
>>> from las_vegas import *
>>> play_vs(3, humans=["Me", "You"])Round: 1/4
Casinos:
╭───────────────────┬──────────┬───┬───┬───┬───╮
│             Bills │ Casinos  │   │ ▼ │   │ × │
├───────────────────┼──────────┼───┼───┼───┼───┤
│       30000 50000 │ Casino 0 │ 2 │ 0 │ 0 │ 0 │
│             50000 │ Casino 1 │ 0 │ 0 │ 0 │ 0 │
│ 10000 10000 40000 │ Casino 2 │ 0 │ 0 │ 0 │ 0 │
│       20000 70000 │ Casino 3 │ 0 │ 0 │ 0 │ 0 │
│       20000 90000 │ Casino 4 │ 0 │ 0 │ 0 │ 0 │
│       20000 30000 │ Casino 5 │ 0 │ 0 │ 0 │ 0 │
╰───────────────────┴──────────┴───┴───┴───┴───╯
Players:
╭────────┬────────────────┬─────┬─────╮
│ Scores │ Players        │ Own │ Xtr │
├────────┼────────────────┼─────┼─────┤
│      0 │ Bot 0 (*)      │   6 │   2 │
│      0 │ ► You ◄        │   8 │   2 │
│      0 │ Me             │   8 │   2 │
╰────────┴────────────────┴─────┴─────╯
Roll:
╭─────┬─────────┬─────┬─────╮
│ Own │ 1 1 1 1 │ 2 2 │ 5 5 │
│ Xtr │ 1       │ 2   │     │
╰─────┴─────────┴─────┴─────╯
Your play: █
```

#### `Roll` table

By default, in games with 2, 3 or 4 participants, neutral -- or `Xtr` -- dice are rolled along with players' `Own` dice. In the above example, `You` rolled 10 dice (8 of your own plus 2 extra) and got, for example, one neutral `2`. Here, `You` can only choose a play in `{1, 2, 5}`.

#### `Players` table

The players cycle is randomized at the beginning of the game and the goes from top to bottom. Every round, the _first player chip_ is passed to the  players next to the one who had it before.

You can see in the `Players` table that the **bot** curently has the _first player chip_ -- marker `(*)` -- and that it is `You`'s turn to play -- marker `► xxx ◄`.

The scores are also written in the leftmost column.

#### `Casinos` table

It shows how many dice of each player -- or neutral dice -- are on each casino. The columns are ordered from left to right corresponding to players in the `Players` table from top to bottom. The column marked `×` corresponds to neutral dice and the column of the current player is highlighted with the marker `▼`.

The leftmost column shows which bills are winnable in the current round on each casino. By default, they add up to at least `50.000` and are reset every round.


## 🤖 Benchmark agents 🤖

If you want to benchmark an implemented agent against others, you can use the `confront` function. For example, we can test a `greedy_shy` agent against two uniformly random players -- represented by `None` in the code bellow -- in a 1000-games faceoff. 

```
import las_vegas
my_agent = las_vegas.policies.greedy_shy  # Toy example
las_vegas.confront(my_agent, None, None, games=1000)  # `None` represents the uniformly random policy.
```
```pycon
>>> import las_vegas
>>> my_agent = las_vegas.policies.greedy_shy  # Toy example
>>> las_vegas.confront(my_agent, my_agent, None, games=1000)
100%|███████████████████████████| 1000/1000 [00:01<00:00, 627.67it/s]
Match in 1000 games:
╭──────────────────────┬─────┬────────┬─────┬────────┬─────┬────────╮
│ Policy               │ 1st │   with │ 2nd │   with │ 3rd │   with │
├──────────────────────┼─────┼────────┼─────┼────────┼─────┼────────┤
│ Policy 0: greedy_shy │ 688 │ 502849 │ 243 │ 395597 │  69 │ 317536 │
│ Policy 1: None       │ 151 │ 461060 │ 386 │ 367047 │ 463 │ 276393 │
│ Policy 2: None       │ 166 │ 453554 │ 375 │ 368827 │ 459 │ 278889 │
╰──────────────────────┴─────┴────────┴─────┴────────┴─────┴────────╯
```

In case of draws during games, players who are ex-aequo are assigned the best of their ranks. As an example, if only the 2nd and the 3rd player are equal in a 4-player game, then ranks 1, 2, 2 and 4 are assigned.

The table also shows the average score policies got at given ranks. For example, `greedy_shy` scored `502849` on average when winning during the 1000 simulated games.


### 🏆 A.I. Competition -- Leaderboard 🏆

A leaderboard might be setup later, comparing the best submitted A.I.'s.


## 🛠️ API 🛠️

The game as an agnostic environment is implemented in `las_vegas/core/`. For now, please refer to the related docstring for any information.

```
help(las_vegas.core)
```
