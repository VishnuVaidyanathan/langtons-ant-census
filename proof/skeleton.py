"""
skeleton.py — the observations behind the proof, checked with plain numbers.

For the ant L^(K-1)R and several K, run until it is 1,500 squares from the start and check:
  1. the right turns happen at the same squares, facing the same way, for every K;
  2. each gap of left turns between two right turns equals its K = 3 value plus
     g * (K - 3), with g = 0 or 4;
  3. every square's visit count equals its K = 3 count plus m * (K - 3).
"""
import collections

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


def run(K):
    g = {}
    x = y = 0
    d = 0
    gap = 0
    events = []
    while not (x <= -1500 or x >= 1499 or y <= -1500 or y >= 1499):
        v = g.get((x, y), 0)
        right = v % K == K - 1
        if right:
            events.append((x, y, (d + 1) & 3, gap))
            gap = 0
        else:
            gap += 1
        d = (d + 1) & 3 if right else (d + 3) & 3
        g[(x, y)] = v + 1
        x += DX[d]
        y += DY[d]
    return events, g


Ks = (3, 4, 5, 6, 7, 10, 20)
R = {K: run(K) for K in Ks}
e3, g3 = R[3]
print("right turns before the edge:", {K: len(R[K][0]) for K in Ks})
same = all([e[:3] for e in R[K][0]] == [e[:3] for e in e3] for K in Ks)
print("1. same squares and directions for every K:", same)

growth = [R[4][0][n][3] - e3[n][3] for n in range(len(e3))]
ok2 = all(R[K][0][n][3] == e3[n][3] + growth[n] * (K - 3) for K in Ks for n in range(len(e3)))
print("2. gaps grow linearly:", ok2, "| growth per colour:", dict(collections.Counter(growth)),
      "| total per colour:", sum(growth))

m = {c: R[4][1][c] - g3[c] for c in g3}
ok3 = all(set(R[K][1]) == set(g3) and all(R[K][1][c] == g3[c] + m[c] * (K - 3) for c in g3) for K in Ks)
print("3. visits(K) = visits(3) + m*(K-3) on every square:", ok3,
      "| values of m:", dict(collections.Counter(m.values())))
