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
Then it computes, from its own replay, the step and right turn at the edge and the
three highway conditions (a)-(c) of Lemma 10 at right turns 7,600 and 7,610.
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
                if rturns in (7600, 7610):
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

    Si, Sj = snaps[7600], snaps[7610]
    D = (Sj["pos"][0] - Si["pos"][0], Sj["pos"][1] - Si["pos"][1])
    V = Sj["touched"]
    H = set(Sj["count"])
    shift = lambda c: (c[0] + D[0], c[1] + D[1])
    f_ = lambda c: c[0] * D[0] + c[1] * D[1]
    A = {shift(c) for c in V} - V
    a = Si["d"] == Sj["d"]
    b = all(Sj["count"].get(shift(c), (0, 0)) == Si["count"].get(c, (0, 0)) for c in V)
    c1 = not (A & H)
    c2 = f_(D) > 0 and min(f_(c) for c in A) + f_(D) > max(f_(c) for c in H)
    period = (Sj["steps"][0] - Si["steps"][0], Sj["steps"][1] - Si["steps"][1])
    print(f"highway: shift {D}, steps per 10 right turns {fmt(period)}")
    print(f"  (a) same direction: {a}   (b) counts repeat on {len(V)} squares: {b}   "
          f"(c) squares ahead unvisited: {c1 and c2}")
    ok = (rt == 7488 and moves == (-8970, 11980) and D == (-2, 2)
          and period == (-12, 16) and a and b and c1 and c2)
    print("CERTIFICATE VALID" if ok else "CERTIFICATE DOES NOT PROVE THE CLAIMS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
