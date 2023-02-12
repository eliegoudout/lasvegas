# 🎲 Las Vegas 🎲

This package revolves around _Las Vegas_, the dice boardgame edited by [Ravensburger](https://www.ravensburger.fr/produits/jeux-de-soci%C3%A9t%C3%A9/jeux-d-ambiance/las-vegas-26745/index.html). It provides:

- a CLI playing mode against humans and/or (possibly custom) agents, with customizable rules,
- a simple confrontation tool for multiple agents.
- an agnostic game environment, for agent implementing and/or training.


## ⚙️ Installation ⚙️

At least **Python 3.10** is required. You have two options for installing `lasvegas`.

##### Install with `pip`

```
python3 -m pip install lasvegas
```

##### Install from source

From the folder of your choice -- _e.g._ `~/workspace/` --, run the following commands.
```
git clone https://github.com/eliegoudout/lasvegas
cd lasvegas/
python3 -m pip install .
```

##### Once installed

From your Python interpreter, you should now be able to `import lasvegas`.
```pycon
>>> import lasvegas
```

#### 🤓 Requirements 🤓

- [numpy](https://github.com/numpy/numpy)
- [tabulate](https://github.com/astanin/python-tabulate)
- [tqdm](https://github.com/tqdm/tqdm)

</details>

## 🤜 Play with friends 🤛

With `play_vs`, let's start a 3-player game: **me** vs **you** vs (a bad) **bot**:
```pycon
>>> lasvegas.play_vs(3, humans=["Me", "You"])
Round: 1/4
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

You are then prompted to play.

#### `Roll` table

By default, in games with 2, 3 or 4 participants, in addition to their 8 `Own` dice, players are given neutral -- or `Xtr` -- dice. In the above example, `You` rolled 10 dice (8 `Own` plus 2 `Xtr`) and got, for example, 1 neutral `2`. In the above situation, the set of legal moves is `{1, 2, 5}`.

#### `Players` table

The players order is randomized at the beginning of the game and cycles from top to bottom.

Every round, the starting player is the owner of the _first player chip_ `(*)`. At the end of a round, he or she gives it to the next player. You can see in the `Players` table that the `bot` currently has the _first player chip_.

After having played, the `bot` has 6 `Own` + 2 `Xtr` dice left and `You` will play next -- marker `► xxx ◄`.

The current scores are written in the leftmost column.

#### `Casinos` table

It shows how many dice of each player -- or neutral dice -- are on each casino. The dice columns are ordered from left to right corresponding to players in the `Players` table from top to bottom. The column marked `×` corresponds to neutral dice and the column of the current player is highlighted with the marker `▼`.

The leftmost column of the table lists all winnable bills in the current round on each casino. By default, they add up to at least `50.000` and are reset every round.


## 🤖 Benchmark agents 🤖

If you want to benchmark an implemented agent against others, you can use the `confront` function. For example, we can test a `greedy_shy` agent against two uniformly random players -- represented by `None` in the code bellow -- in a 1000-games faceoff. 
```pycon
>>> my_agent = lasvegas.policies.greedy_shy  # Toy example
>>> lasvegas.confront(my_agent, None, None, games=1000)
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

In case of draws during games, players who are ex-aequo are assigned the best of their ranks. For example, if only the 2<sup>nd</sup> and the 3<sup>rd</sup> players are equal in a 4-player game, then ranks 1, 2, 2 and 4 are assigned.

The table also shows the average score policies got at given ranks. For example, `greedy_shy` scored `502849` on average when winning during the 1000 simulated games.

### 🧠 Implement your own agent 🧠

An agent is defined by its `Policy`, which is simply a function `Callable[Game, Play]`, where `Play = int | None`. Playing `None` means playing uniformly at random.

##### Simple examples

```pycon
>>> # Imports for type hinting
>>> from lasvegas.core import Play
>>> from lasvegas.game import Game
>>> 
>>> # Plays the smallest casino number available
>>> def smallest(game: Game) -> Play:
...     return min(game._legal_plays())
... 
>>> # Plays the most `Own` dice possible
>>> def spender(game: Game) -> Play:
...     return max(game._legal_plays(),
...                key=lambda d: game.roll_own[d])
... 
```
```pycon
>>> confront(smallest, spender, greedy_shy, None, games=1000)
100%|██████████████████████████████████████████| 1000/1000 [00:01<00:00, 545.05it/s]
Match in 1000 games:
╭──────────────────────┬─────┬────────┬─────┬────────┬─────┬────────┬─────┬────────╮
│ Policy               │ 1st │   with │ 2nd │   with │ 3rd │   with │ 4th │   with │
├──────────────────────┼─────┼────────┼─────┼────────┼─────┼────────┼─────┼────────┤
│ Policy 0: smallest   │  74 │ 396081 │ 255 │ 317804 │ 334 │ 264072 │ 337 │ 198338 │
│ Policy 1: spender    │ 128 │ 405312 │ 295 │ 329729 │ 281 │ 259395 │ 296 │ 196655 │
│ Policy 2: greedy_shy │ 701 │ 447461 │ 192 │ 350000 │  77 │ 286234 │  30 │ 232333 │
│ Policy 3: None       │ 105 │ 413048 │ 264 │ 321667 │ 304 │ 263586 │ 327 │ 190061 │
╰──────────────────────┴─────┴────────┴─────┴────────┴─────┴────────┴─────┴────────╯
```

##### Learning

To implement learning-based agents (_e.g._ with RL), you might first consider writing an `observation` function that extracts the `Game` state in the desired form, before passing it to a _learning environment_ built on the side. A good place to start can be [Stable Baselines3](https://stable-baselines3.readthedocs.io/en/master/).

### 🏆 A.I. Competition -- Leaderboard 🏆

A leaderboard might be setup later, comparing the best submitted A.I.'s. In _competition mode_, agents will only use `GameEnv` attributes (so they can't, for example, ask the opponents what they would play).


## 🛠️ API 🛠️

The game as an agnostic _gaming environment_ is implemented in `lasvegas/core/`. For now, please refer to the related docstring for any information.

```pycon
>>> help(lasvegas.core)
```
