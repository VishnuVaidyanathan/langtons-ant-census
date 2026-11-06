"""
highway_concrete.py — plain-number cross-check of the highway, for chosen K.

Usage:  python3 proof/highway_concrete.py K [K ...]

For each K, runs L^(K-1)R step by step from the empty grid (no symbols, no spins) and
measures from the sequence of turns alone:
  * the shortest period of the turn sequence once it repeats;
  * the first step from which it repeats;
  * how far the ant moves in one period.
For K >= 4 these should be 16K - 12, 24K - 17 and (-2, 2) (the theorem);
K = 3 (LLR) is different: period 18 from step 39, moving (-1, 1).
"""
import sys

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


def measure(K):
    n = 400 * K + 2000
    g = {}
    x = y = 0
    d = 0
    turns = []
    pos = []
    for _ in range(n):
        v = g.get((x, y), 0)
        right = v % K == K - 1
        turns.append(right)
        d = (d + 1) & 3 if right else (d + 3) & 3
        g[(x, y)] = v + 1
        x += DX[d]
        y += DY[d]
        pos.append((x, y))
    tail = turns[n // 2:]
    p = next(q for q in range(1, len(tail) // 3) if tail[q:] == tail[:-q])
    start = n - p
    while start > 0 and turns[start - 1] == turns[start - 1 + p]:
        start -= 1
    move = (pos[-1][0] - pos[-1 - p][0], pos[-1][1] - pos[-1 - p][1])
    return p, start, move


if __name__ == "__main__":
    ok = True
    for K in (int(a) for a in sys.argv[1:]):
        p, start, move = measure(K)
        line = f"K = {K}: period {p}, repeats from step {start}, moves {move}"
        if K >= 4:
            good = (p, start, move) == (16 * K - 12, 24 * K - 17, (-2, 2))
            ok &= good
            line += f"   (theorem: {16 * K - 12}, {24 * K - 17}, (-2, 2)) {'ok' if good else 'MISMATCH'}"
        print(line)
    sys.exit(0 if ok else 1)
