## Unreleased

##### 0.2.1dev

## Released

##### 0.2.0 – June 9, 2023

- `GameEnv.dice` is now a matrix regrouping players and casinos dice,
- New flexibility in defining `GameRules`. Enables solo mode.
- Better decoupling of `GameEnv`, `BasePlayer`, `Game`.
- Added `greedy_score` and `greedy_first`, removed `greedy_shy`.
- `confront` and `play_vs` now take `**gameargs`.
- Removed unused `_custom-imports.py` since `0.1.2`

##### 0.1.4 – March 29, 2023

- `perf` tool
- Rolls as `dict[int, int]` (a bit faster)

##### 0.1.3 – February 12, 2023

- Removed redundant `requirements.txt`

##### 0.1.2 – February 7, 2023

- `tqdm` required (simpler this way, and pretty standard anyways)
- Fixed metadata for Pypi
- Bump version number because conflict otherwise

##### 0.1.1 – February 6, 2023

- Created `changelog.md`
- Project renamed `lasvegas`
- Distributed on Pypi
