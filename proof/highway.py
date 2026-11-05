"""
Proof that the L^(K-1)R ant keeps building its highway forever, for every K >= K0.

Run the symbolic ant until one highway period (P right turns) is fully under way,
take snapshots of all square residues at right turn i and at right turn j = i + P,
and record the set V of squares touched between them. The highway repeats for
ever if:
  (a) the ant faces the same way at i and j, and is shifted by D;
  (b) every square c in V holds at j, shifted by D, the residue it held at i;
  (c) the squares the highway will reach next have never been visited by time j:
      no square of (V + kD) minus (V + (k-1)D), k >= 1, is visited by time j.
Then by induction each period is an exact shifted copy of the one before.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symbolic
from symbolic import Aff, ZERO, RSTATE, sign, DX, DY


def run_with_snapshots(snap_events):
    res = {}
    x = y = 0
    d = 0
    steps = Aff(0)
    rturns = 0
    snaps = {}
    touched = set()
    want = sorted(snap_events)
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
            if rturns in want:
                snaps[rturns] = dict(res=dict(res), pos=(x, y), d=d, steps=steps,
                                     touched=set(touched))
                touched = set()
                if rturns == want[-1]:
                    return snaps
        else:
            d = (d + 3) & 3
            res[(x, y)] = v + Aff(1)
        x += DX[d]
        y += DY[d]
        steps = steps + Aff(1)


P = 10
i = 7600
j = i + P
s = run_with_snapshots([i, j])
Si, Sj = s[i], s[j]
D = (Sj["pos"][0] - Si["pos"][0], Sj["pos"][1] - Si["pos"][1])
V = Sj["touched"]                      # squares touched during right turns i..j
H = set(Sj["res"].keys())              # every square visited by time j
shift = lambda c, k=1: (c[0] + k * D[0], c[1] + k * D[1])

a = Si["d"] == Sj["d"]
b = all(Sj["res"].get(shift(c), ZERO) == Si["res"].get(c, ZERO) for c in V)
# (c): fronts A_k = (V+kD) - (V+(k-1)D); check k = 1 directly, and all k >= 2
# with a linear measure f growing along D.
f = lambda c: c[0] * D[0] + c[1] * D[1]
A1 = {shift(c) for c in V} - V
c1 = not (A1 & H)
fD = f(D)
maxH = max(f(c) for c in H)
minA2 = min(f(c) for c in A1) + fD     # every A_k, k >= 2, lies at f >= this
c2 = fD > 0 and minA2 > maxH

print("shift per period D        :", D)
print("steps per period          :", Sj["steps"] - Si["steps"])
print("(a) same direction        :", a)
print("(b) residues repeat on V  :", b, f"({len(V)} squares)")
print("(c) next front unvisited  :", c1, "| all later fronts unvisited:", c2)
print("valid for every K >=      :", symbolic.K0)
