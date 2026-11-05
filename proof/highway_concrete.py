"""
highway_concrete.py — the highway test of highway.py for one given K, with plain numbers.

Usage:  python3 proof/highway_concrete.py K
Used for K = 3, which the symbolic run (valid for K >= 4) does not cover,
and as a cross-check of the symbolic result at any K.
"""
import sys

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


def run_with_snapshots(K, snap_events):
    res = {}
    x = y = 0
    d = 0
    steps = 0
    rturns = 0
    snaps = {}
    touched = set()
    want = sorted(snap_events)
    while True:
        v = res.get((x, y), 0)
        touched.add((x, y))
        if v == K - 1:
            d = (d + 1) & 3
            res[(x, y)] = 0
            rturns += 1
            if rturns in want:
                snaps[rturns] = dict(res=dict(res), pos=(x, y), d=d, steps=steps,
                                     touched=set(touched))
                touched = set()
                if rturns == want[-1]:
                    return snaps
        else:
            d = (d + 3) & 3
            res[(x, y)] = v + 1
        x += DX[d]
        y += DY[d]
        steps += 1


K = int(sys.argv[1])
P, i = 10, 7600
j = i + P
s = run_with_snapshots(K, [i, j])
Si, Sj = s[i], s[j]
D = (Sj["pos"][0] - Si["pos"][0], Sj["pos"][1] - Si["pos"][1])
V = Sj["touched"]
H = set(Sj["res"].keys())
shift = lambda c: (c[0] + D[0], c[1] + D[1])
f = lambda c: c[0] * D[0] + c[1] * D[1]
A1 = {shift(c) for c in V} - V
a = Si["d"] == Sj["d"]
b = all(Sj["res"].get(shift(c), 0) == Si["res"].get(c, 0) for c in V)
c1 = not (A1 & H)
c2 = f(D) > 0 and min(f(c) for c in A1) + f(D) > max(f(c) for c in H)
print(f"K = {K}: shift {D}, steps per period {Sj['steps'] - Si['steps']} (16K-12 = {16 * K - 12})")
print("(a) same direction       :", a)
print("(b) residues repeat on V :", b, f"({len(V)} squares)")
print("(c) fronts unvisited     :", c1, c2)
