# Highways of the generalised Langton's ants L^(K-1)R, and a census up to 12 colours

Code and data for the preprint

> Vishnu Vaidyanathan, *Highways of the Generalised Langton's Ants L^(K-1)R from the Empty Grid:
> a Machine-Checked Proof, and a Census up to Twelve Colours*, 2026.

## Main results

* **Theorem.** For every K ≥ 4, the ant L^(K-1)R started on the empty grid is on a highway from step
  24K − 17 onward (and not from any earlier step), with shortest period exactly 16K − 12 steps, moving
  (−2, 2) each period. For K = 2k + 2 this completes the proof of the period-(32k + 20) highway of
  L^(2k+1)R stated as a sketch by Gajardo, Lutfalla and Rao (arXiv:2409.10124).
* **Proof method.** One run of the ant with K kept as a symbol (colours stored as a + bK, spins round
  2×2 loops taken in one step). The part the theorem needs is 35 lines, printed in the paper; the full
  certificate (12,735 lines) is checked by an independent program.
* **Census (experimental).** Of 4,015 distinct machines with 2 to 12 colours, from the empty grid after
  1 million steps: 2,723 chaotic, 790 square, 416 highway, 83 symmetric, 3 triangle. 164 of the highway
  machines are hidden copies of another machine; there are 252 different highway paths.

## What is here

| Path | What it does |
| --- | --- |
| `run_all.sh` | Rebuilds every number, table and figure from scratch (about two minutes). |
| `paper/paper.tex`, `paper/paper.pdf` | The preprint. |
| `proof/highway.py` | Checks the theorem: periodicity at right turns 11 and 21, shortest period, exact start. |
| `proof/symbolic.py` | The symbolic run of L^(K-1)R up to leaving the 2,998 × 2,998 box (Proposition 6). |
| `proof/write_certificate.py` | Writes `proof/certificate.txt`: every action of the symbolic run. |
| `proof/check_certificate.py` | Independent checker: replays the certificate and re-checks every claim for all K ≥ 4. |
| `proof/make_table.py` | Builds the paper's 35-line Table 1 from the certificate. |
| `proof/highway_concrete.py` | Plain step-by-step cross-check of the theorem for chosen K. |
| `proof/skeleton.py` | Observations behind Proposition 6, for several K. |
| `src/ant_census.c`, `src/classify.py`, `src/analyse.py` | The census and every number in it. |
| `src/ant_visits.c`, `src/ant_snap.c`, `src/make_figures.py` | Single-rule runs and the figures. |
| `data/census.csv` | All 4,015 distinct machines with class and measures. |
| `data/census_raw.csv` | Raw measures for all 8,188 rule words. |
| `data/highways.txt`, `data/squares.txt`, `data/chaotic.txt` | The highway, square and chaotic machines, grouped by K. |

## The ant

A rule word of K letters, each L or R. Every square holds a colour 0 to K−1, all 0 at the start.
The ant reads the colour c of its square, turns left if letter c+1 of the rule is L and right if it is R,
changes the square to (c+1) mod K, and steps forward. The classic Langton's ant is RL.

## Reproduce

```
./run_all.sh
```

Needs a C compiler, Python 3, and (for the figures only) matplotlib and Pillow.

## Licence

MIT, see `LICENSE`.
