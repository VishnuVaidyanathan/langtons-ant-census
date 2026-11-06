"""
highway.py — proof that the ant L^(K-1)R builds its highway from step 24K - 17 onward,
with shortest period exactly 16K - 12 steps, for every K >= 4.

The ant is run with K kept as a symbol (see symbolic.py) up to its 21st right turn.

1. Periodicity (Lemma 10 of the paper), with i = 11 and P = 10 right turns:
   (a) the ant faces the same way after right turns i and j = i + P, shifted by D;
   (b) every square c touched between them holds at j, shifted by D, the count it held at i;
   (c) the squares the highway will reach next have never been visited by time j.
   Then every later period is an exact shifted copy of this one.
2. Shortest period: the 10 gaps between consecutive right turns in one period are affine
   in K. A shorter period would make the cyclic list of gaps repeat after s = 1, 2 or 5
   places; for each s some pair of gaps differs for every K >= 4.
3. Exact start: the trace is periodic from the step of right turn 11 (24K - 17), and not
   from the step before, because that step is a right turn while the step one period
   later is a left turn, for every K >= 4.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symbolic
from symbolic import Aff, ZERO, RSTATE, sign, DX, DY


def run_with_snapshots(last):
    """Run to right turn `last`; snapshot after every right turn."""
    res = {}
    x = y = 0
    d = 0
    steps = Aff(0)
    rturns = 0
    snaps = {}
    touched = set()
    while True:
        cells = []
        cx, cy, cd = x, y, d
        for _ in range(4):
            cells.append((cx, cy))
            cd = (cd + 3) & 3
            cx += DX[cd]
            cy += DY[cd]
        rems = [RSTATE - res.get(c, ZERO) for c in cells]
        if all(sign(r) > 0 for r in rems):
            n = rems[0]
            for r in rems[1:]:
                if sign(r - n) < 0:
                    n = r
            for c in cells:
                res[c] = res.get(c, ZERO) + n
                touched.add(c)
            steps = steps + n.scale(4)
            continue
        v = res.get((x, y), ZERO)
        touched.add((x, y))
        if v == RSTATE:
            d = (d + 1) & 3
            res[(x, y)] = ZERO
            rturns += 1
            # `steps` = index of this step (moves made before it)
            snaps[rturns] = dict(res=dict(res), pos=(x, y), d=d, steps=steps,
                                 touched=set(touched))
            touched = set()
            if rturns == last:
                return snaps
        else:
            d = (d + 3) & 3
            res[(x, y)] = v + Aff(1)
        x += DX[d]
        y += DY[d]
        steps = steps + Aff(1)


def differs_for_all(e1, e2, K_min=4):
    """True if e1 != e2 for every integer K >= K_min."""
    a, b = e1.p - e2.p, e1.q - e2.q          # e1 - e2 = a + bK
    if b == 0:
        return a != 0
    if a % b != 0:
        return True
    return -a // b < K_min                    # only zero at K = -a/b


def periodicity(snaps, i, P):
    Si, Sj = snaps[i], snaps[i + P]
    D = (Sj["pos"][0] - Si["pos"][0], Sj["pos"][1] - Si["pos"][1])
    V = set()
    for t in range(i + 1, i + P + 1):
        V |= snaps[t]["touched"]
    H = set(Sj["res"])
    shift = lambda c: (c[0] + D[0], c[1] + D[1])
    f = lambda c: c[0] * D[0] + c[1] * D[1]
    A = {shift(c) for c in V} - V
    a = Si["d"] == Sj["d"]
    b = all(Sj["res"].get(shift(c), ZERO) == Si["res"].get(c, ZERO) for c in V)
    c = (not (A & H)) and f(D) > 0 and min(f(x) for x in A) + f(D) > max(f(x) for x in H)
    return D, Sj["steps"] - Si["steps"], a, b, c, len(V)


if __name__ == "__main__":
    I, P = 11, 10
    snaps = run_with_snapshots(I + P)
    D, period, a, b, c, nV = periodicity(snaps, I, P)
    print("highway start: right turn", I, "at step", snaps[I]["steps"])
    print("shift per period D          :", D)
    print("steps per period            :", period)
    print("(a) same direction          :", a)
    print("(b) counts repeat, shifted  :", b, f"({nV} squares)")
    print("(c) squares ahead unvisited :", c)

    gaps = [snaps[t + 1]["steps"] - snaps[t]["steps"] for t in range(I, I + P)]
    print("gaps in one period          :", [str(g) for g in gaps])
    shortest = all(any(differs_for_all(gaps[n], gaps[(n + s) % P]) for n in range(P))
                   for s in (1, 2, 5))
    print("no shorter period, K >= 4   :", shortest)

    gap_before = snaps[I]["steps"] - snaps[I - 1]["steps"]   # right turn I-1 is the step before
    gap_later = snaps[I + P]["steps"] - snaps[I + P - 1]["steps"]
    exact = gap_before == Aff(1) and differs_for_all(gap_later, Aff(1))
    print("not periodic one step earlier:", exact,
          f"(step before is a right turn; one period later the gap is {gap_later})")
    print("valid for every K >=        :", symbolic.K0)
    ok = a and b and c and shortest and exact and D == (-2, 2) and period == Aff(-12, 16) \
        and snaps[I]["steps"] == Aff(-17, 24)
    print("HIGHWAY PROOF COMPLETE" if ok else "HIGHWAY PROOF FAILED")
    sys.exit(0 if ok else 1)
