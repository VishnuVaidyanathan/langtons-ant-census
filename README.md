# Multi-colour Langton's ants: a census for K ≤ 12 and a proof for the L^(K-1)R family

Code and data for the preprint

> Vishnu Vaidyanathan, *A Census of Multi-Colour Langton's Ants up to Twelve Colours, with an Exact Escape Formula and a Highway Proof for the Family L^(K-1)R*, SSRN preprint, 2026.

## What is here

| Path | What it does |
| --- | --- |
| `run_all.sh` | Rebuilds every number and figure in the paper from scratch (about two minutes). |
| `src/ant_census.c` | Runs all 2^K rule strings for one K and prints shape measures. |
| `src/classify.py` | Removes repeats and mirror twins and gives each machine a class. |
| `src/analyse.py` | Every census number and observation in the paper; writes `data/analysis.txt`. |
| `src/ant_visits.c` | One rule: the step it reaches the edge and the most visits to one square. |
| `src/ant_snap.c`, `src/make_figures.py` | The figures. |
| `proof/symbolic.py` | Runs L^(K-1)R once with K as a symbol: proves the escape formula for every K ≥ 4. |
| `proof/highway.py` | Proves the L^(K-1)R highway goes on forever, for every K ≥ 4. |
| `proof/highway_concrete.py` | The same highway test with plain numbers (used for K = 3). |
| `proof/skeleton.py` | The observations behind the proof, checked for several K. |
| `data/census.csv` | All 4,015 distinct machines with K = 2 to 12, class and measures. |
| `data/census_raw.csv` | The raw measures for all 8,188 rule strings. |
| `data/highways.txt`, `data/squares.txt` | The highway and square machines, grouped by K. |

## The ant

A rule string of K letters, each L or R. Every square holds a colour 0 to K−1, all 0 at the start.
The ant reads the colour c of its square, turns left if letter c+1 of the rule is L and right if it is R,
changes the square to (c+1) mod K, and steps forward. The classic Langton's ant is RL.

## Main results

* **Census.** Of 4,015 distinct machines with 2 to 12 colours: 2,723 chaotic, 790 square, 416 highway,
  83 symmetric, 3 triangle (after 1 million steps).
* **Hidden copies.** 164 of the highway machines never read their last letters and walk the same path
  as another machine; there are 252 different highway paths.
* **Theorem.** The ant L^(K-1)R reaches 1,500 squares from its start at step 26,969 + 11,980 (K − 3),
  and builds a highway forever, moving 2 squares diagonally every 16K − 12 steps, for every K ≥ 3.

## Reproduce

```
./run_all.sh
```

Needs a C compiler, Python 3, and (for the figures only) matplotlib and Pillow.

## Licence

MIT, see `LICENSE`.
