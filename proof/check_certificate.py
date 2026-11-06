"""
check_certificate.py — check proof/certificate.txt without trusting the program that wrote it.

Usage:  python3 proof/check_certificate.py

The checker replays the ant L^(K-1)R from the empty grid, one certificate line at a time,
keeping its own record of every square's count as a pair (a, b) meaning a + b*K.
It searches for nothing and makes no choices: it only checks that each line is a legal
move for EVERY K >= 4, using one rule:

    a + b*K >= c for every K >= 4   exactly when   b >= 0 and a + 4b >= c.

Checks made:
  * every line's position, direction and count agree with the replay;
  * every count stays a real colour, 0 <= count <= K - 1, for every K >= 4;
  * single step: the turn is R exactly when the count is K - 1 for every K >= 4
    (count = -1 + 1*K), and L only when count <= K - 2 for every K >= 4;
  * spin of n laps (Lemma 9 of the paper): n >= 1 and n <= (K - 1) - count for each of
    the four squares, for every K >= 4; spins are not allowed to touch the box edge
    before the ant first leaves the box;
  * the edge mark E is exactly where the replay first leaves the box B.
Then it computes, from its own replay:
  * the step and right turn at which the ant first leaves the box;
  * the highway conditions (a)-(c) of the periodicity lemma at right turns 11 and 21;
  * the 10 gaps between right turns in that period, and that no cyclic shift by 1, 2 or
    5 places leaves them unchanged for any K >= 4 (so 16K - 12 is the shortest period);
  * that the trace is not periodic from the step before right turn 11.
"""
import os
import sys

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)
HERE = os.path.dirname(os.path.abspath(__file__))
inequalities = 0


def fail(msg, line_no):
    print(f"CHECK FAILED at line {line_no}: {msg}")
    sys.exit(1)


def at_least(e, c):
    """a + bK >= c for every K >= 4."""
    global inequalities
    inequalities += 1
    a, b = e
    return b >= 0 and a + 4 * b >= c


def is_colour(v):
    """0 <= v <= K - 1 for every K >= 4."""
    return at_least(v, 0) and at_least((-1 - v[0], 1 - v[1]), 0)


def outside(x, y):
    return x <= -1500 or x >= 1499 or y <= -1500 or y >= 1499


def main():
    lines = [l.split() for l in open(os.path.join(HERE, "certificate.txt")) if not l.startswith("#")]
    count = {}
    x = y = 0
    d = 0
    steps = (0, 0)              # moves made, as a + b*K
    rturns = 0
    edge_seen = False
    edge_info = None
    pending_edge = False
    touched = set()
    snaps = {}
    n_steps = n_spins = 0
    for no, f in enumerate(lines, 1):
        kind = f[0]
        if kind == "E":
            if not pending_edge:
                fail("edge mark where the ant is not leaving the box", no)
            pending_edge = False
            continue
        if pending_edge:
            fail("ant left the box but no edge mark follows", no)
        lx, ly, ld = int(f[1]), int(f[2]), int(f[3])
        if (lx, ly, ld) != (x, y, d):
            fail(f"position/direction {lx, ly, ld} but replay has {x, y, d}", no)
        if kind == "S":
            v = (int(f[4]), int(f[5]))
            if v != count.get((x, y), (0, 0)):
                fail(f"count {v} but replay has {count.get((x, y), (0, 0))}", no)
            if not is_colour(v):
                fail(f"count {v} is not a colour for every K >= 4", no)
            touched.add((x, y))
            if f[6] == "R":
                if v != (-1, 1):
                    fail("right turn on a square whose count is not K - 1", no)
                d = (d + 1) & 3
                count[(x, y)] = (0, 0)
                rturns += 1
                if rturns <= 21:
                    snaps[rturns] = dict(count=dict(count), pos=(x, y), d=d,
                                         steps=steps, touched=set(touched))
                    touched = set()
            elif f[6] == "L":
                if not at_least((-1 - v[0] - 1, 1 - v[1]), 0):   # (K-1) - v >= 1
                    fail("left turn on a square that may be at K - 1", no)
                d = (d + 3) & 3
                count[(x, y)] = (v[0] + 1, v[1])
            else:
                fail("turn must be L or R", no)
            x += DX[d]
            y += DY[d]
            steps = (steps[0] + 1, steps[1])
            n_steps += 1
            if not edge_seen and outside(x, y):
                edge_seen = True
                pending_edge = True
                edge_info = (steps, rturns)
        elif kind == "P":
            n = (int(f[4]), int(f[5]))
            cells = []
            cx, cy, cd = x, y, d
            for _ in range(4):
                cells.append((cx, cy))
                cd = (cd + 3) & 3
                cx += DX[cd]
                cy += DY[cd]
            if not edge_seen and any(outside(*c) for c in cells):
                fail("spin touches the edge before the edge is reached", no)
            if not at_least(n, 1):
                fail(f"spin of {n} laps is not at least 1 for every K >= 4", no)
            for c in cells:
                v = count.get(c, (0, 0))
                room = (-1 - v[0], 1 - v[1])                 # (K-1) - v
                if not at_least((room[0] - n[0], room[1] - n[1]), 0):
                    fail(f"spin of {n} laps would push square {c} past its R", no)
            for c in cells:
                v = count.get(c, (0, 0))
                count[c] = (v[0] + n[0], v[1] + n[1])
                if not is_colour(count[c]):
                    fail(f"square {c} leaves the colour range", no)
                touched.add(c)
            steps = (steps[0] + 4 * n[0], steps[1] + 4 * n[1])
            n_spins += 1
        else:
            fail(f"unknown line kind {kind}", no)

    fmt = lambda e: f"{e[1]}K {'+' if e[0] >= 0 else '-'} {abs(e[0])}"
    print(f"lines checked: {len(lines)} ({n_steps} single steps, {n_spins} spins)")
    print(f"inequalities checked for every K >= 4: {inequalities}")
    if edge_info is None:
        fail("the ant never left the box", len(lines))
    moves, rt = edge_info
    print(f"edge: right turns before it = {rt}, moves = {fmt(moves)}, "
          f"step number = {fmt((moves[0] - 1, moves[1]))}")

    I, P = 11, 10
    Si, Sj = snaps[I], snaps[I + P]
    D = (Sj["pos"][0] - Si["pos"][0], Sj["pos"][1] - Si["pos"][1])
    V = set()
    for t in range(I + 1, I + P + 1):
        V |= snaps[t]["touched"]
    H = set(Sj["count"])
    shift = lambda c: (c[0] + D[0], c[1] + D[1])
    f_ = lambda c: c[0] * D[0] + c[1] * D[1]
    A = {shift(c) for c in V} - V
    a = Si["d"] == Sj["d"]
    b = all(Sj["count"].get(shift(c), (0, 0)) == Si["count"].get(c, (0, 0)) for c in V)
    c = (not (A & H)) and f_(D) > 0 and min(f_(x) for x in A) + f_(D) > max(f_(x) for x in H)
    period = (Sj["steps"][0] - Si["steps"][0], Sj["steps"][1] - Si["steps"][1])
    start = Si["steps"]
    print(f"highway: from right turn {I} at step {fmt(start)}, shift {D} every {fmt(period)} steps")
    print(f"  (a) same direction: {a}   (b) counts repeat on {len(V)} squares: {b}   "
          f"(c) squares ahead unvisited: {c}")

    def differs(e1, e2):
        """e1 != e2 for every integer K >= 4 (e = (a, b) meaning a + bK)."""
        da, db = e1[0] - e2[0], e1[1] - e2[1]
        if db == 0:
            return da != 0
        return da % db != 0 or -da // db < 4

    gap = lambda t: (snaps[t + 1]["steps"][0] - snaps[t]["steps"][0],
                     snaps[t + 1]["steps"][1] - snaps[t]["steps"][1])
    gaps = [gap(t) for t in range(I, I + P)]
    shortest = all(any(differs(gaps[n], gaps[(n + s) % P]) for n in range(P)) for s in (1, 2, 5))
    exact = gap(I - 1) == (1, 0) and differs(gap(I + P - 1), (1, 0))
    print(f"  gaps: {[fmt(g) for g in gaps]}")
    print(f"  shortest period is {fmt(period)}: {shortest}   not periodic one step earlier: {exact}")
    ok = (rt == 7488 and moves == (-8970, 11980) and D == (-2, 2) and period == (-12, 16)
          and start == (-17, 24) and a and b and c and shortest and exact)
    print("CERTIFICATE VALID" if ok else "CERTIFICATE DOES NOT PROVE THE CLAIMS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
