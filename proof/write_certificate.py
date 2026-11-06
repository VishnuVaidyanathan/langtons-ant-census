"""
write_certificate.py — run the symbolic L^(K-1)R ant and write down every action it takes.

Usage:  python3 proof/write_certificate.py      (writes proof/certificate.txt)

The run is the same as symbolic.py (K kept as a symbol, spins jumped over), from the
empty grid until just after the ant first leaves the box B. Its first 35 lines (up to
right turn 21) are all the highway proof needs; the rest gives the edge formula. Each line of the
certificate is one action, with the numbers it depends on:

  S x y d a b T      single step at square (x, y), facing d before turning; the square's
                     count before the visit is a + b*K; the ant turns T (L or R)
  P x y d na nb      spin: from square (x, y) facing d, n = na + nb*K laps of four left turns
  E                  the step just made took the ant out of the box B (the edge)

Directions: 0 up, 1 right, 2 down, 3 left; screen coordinates (up is y - 1).
The file is checked by check_certificate.py, which does not use this program.
"""
import os

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)
HERE = os.path.dirname(os.path.abspath(__file__))
LAST_RIGHT_TURN = 7489   # the edge comes after right turn 7,488


def add(u, v):
    return (u[0] + v[0], u[1] + v[1])


def sub(u, v):
    return (u[0] - v[0], u[1] - v[1])


def positive(e):
    """e = (a, b) meaning a + b*K; positive for all large K?"""
    return e[1] > 0 or (e[1] == 0 and e[0] > 0)


def outside(x, y):
    return x <= -1500 or x >= 1499 or y <= -1500 or y >= 1499


def main():
    count = {}
    x = y = 0
    d = 0
    rturns = 0
    edge = False
    lines = []
    while rturns < LAST_RIGHT_TURN:
        cells = []
        cx, cy, cd = x, y, d
        for _ in range(4):
            cells.append((cx, cy))
            cd = (cd + 3) & 3
            cx += DX[cd]
            cy += DY[cd]
        rems = [sub((-1, 1), count.get(c, (0, 0))) for c in cells]
        near_edge = not edge and any(outside(*c) for c in cells)
        if not near_edge and all(positive(r) for r in rems):
            n = rems[0]
            for r in rems[1:]:
                if positive(sub(n, r)):
                    n = r
            for c in cells:
                count[c] = add(count.get(c, (0, 0)), n)
            lines.append(f"P {x} {y} {d} {n[0]} {n[1]}")
            continue
        v = count.get((x, y), (0, 0))
        if v == (-1, 1):
            lines.append(f"S {x} {y} {d} {v[0]} {v[1]} R")
            d = (d + 1) & 3
            count[(x, y)] = (0, 0)
            rturns += 1
        else:
            lines.append(f"S {x} {y} {d} {v[0]} {v[1]} L")
            d = (d + 3) & 3
            count[(x, y)] = add(v, (1, 0))
        x += DX[d]
        y += DY[d]
        if not edge and outside(x, y):
            edge = True
            lines.append("E")
    header = [
        "# Certificate for the ant L^(K-1)R, K >= 4, from an empty grid.",
        "# Start: square (0, 0), facing 0 (up). Counts a b mean a + b*K.",
        f"# {len(lines)} actions, up to right turn {LAST_RIGHT_TURN}.",
    ]
    path = os.path.join(HERE, "certificate.txt")
    with open(path, "w") as f:
        f.write("\n".join(header + lines) + "\n")
    print(f"wrote {len(lines)} actions to {path}")


if __name__ == "__main__":
    main()
