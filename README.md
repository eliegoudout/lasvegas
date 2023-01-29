# 🎲 Las Vegas 🎲

This package revolves around _Las Vegas_, the dice boardgame edited by [Ravensburger](https://www.ravensburger.fr/produits/jeux-de-soci%C3%A9t%C3%A9/jeux-d-ambiance/las-vegas-26745/index.html). It provides:

- a CLI playing mode against humans and/or (possibly custom) agents, with customizable rules,
- a simple confrontation tool for multiple agents.
- an agnostic game environment, for agent implementing and/or training.


## ⚙️ Installation ⚙️

At least **Python 3.10** is required.

At the moment, the package is not referenced on PyPi and installation is done via direct cloning. From the folder of your choice -- _e.g._ `workspace/` --, run the following commands.
```
git clone https://github.com/eliegoudout/las-vegas
cd las-vegas/
pip install -r requirements.txt
```

From your Python interpreter, you should be able to `import las_vegas`.
```pycon
>>> import las_vegas
```

#### 🤓 Requirements 🤓

- [numpy](https://github.com/numpy/numpy)
- [tabulate](https://github.com/astanin/python-tabulate)
- [tqdm](https://github.com/tqdm/tqdm) (recommended for benchmarking)


## 🤜 Play with friends 🤛

Let's start a 3-player game: **me** vs **you** vs (a bad) **bot**:
```pycon
>>> las_vegas.play_vs(3, humans=["Me", "You"])
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

Every round, the starting player is the owner of the _first player chip_ `(*)`. At the end of a round, he or she gives it to the next player. You can see in the `Players` table that the **bot** curently has the _first player chip_ and that it is `You`'s turn to play -- marker `► xxx ◄`.

The current scores are written in the leftmost column.

#### `Casinos` table

It shows how many dice of each player -- or neutral dice -- are on each casino. The dice columns are ordered from left to right corresponding to players in the `Players` table from top to bottom. The column marked `×` corresponds to neutral dice and the column of the current player is highlighted with the marker `▼`.

The leftmost column of the table lists all winnable bills in the current round on each casino. By default, they add up to at least `50.000` and are reset every round.


## 🤖 Benchmark agents 🤖

If you want to benchmark an implemented agent against others, you can use the `confront` function. For example, we can test a `greedy_shy` agent against two uniformly random players -- represented by `None` in the code bellow -- in a 1000-games faceoff. 
```pycon
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

In case of draws during games, players who are ex-aequo are assigned the best of their ranks. For example, if only the 2nd and the 3rd players are equal in a 4-player game, then ranks 1, 2, 2 and 4 are assigned.

The table also shows the average score policies got at given ranks. For example, `greedy_shy` scored `502849` on average when winning during the 1000 simulated games.

### 🏆 A.I. Competition -- Leaderboard 🏆

A leaderboard might be setup later, comparing the best submitted A.I.'s.


## 🛠️ API 🛠️

The game as an agnostic environment is implemented in `las_vegas/core/`. For now, please refer to the related docstring for any information.

```pycon
>>> help(las_vegas.core)
```
