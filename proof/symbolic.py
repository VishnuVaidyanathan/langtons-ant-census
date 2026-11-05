"""
Symbolic run of the ant L^(K-1)R with K kept as a symbol.

Each square stores its count modulo K as an affine expression a + b*K
(0 <= value <= K-1 for every large K). A spin (laps round a 2x2 loop of
left turns) is jumped over in one go, its number of laps being an affine
expression in K. Every comparison between affine expressions is recorded
together with the smallest K from which its answer holds (K0).

If the run finishes, the result is valid for every K >= K0.
"""
import sys

DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)


class Aff:
    """p + q*K"""
    __slots__ = ("p", "q")

    def __init__(self, p, q=0):
        self.p, self.q = p, q

    def __add__(self, o):
        return Aff(self.p + o.p, self.q + o.q)

    def __sub__(self, o):
        return Aff(self.p - o.p, self.q - o.q)

    def scale(self, c):
        return Aff(self.p * c, self.q * c)

    def __eq__(self, o):
        return self.p == o.p and self.q == o.q

    def __hash__(self):
        return hash((self.p, self.q))

    def __repr__(self):
        if self.q == 0:
            return str(self.p)
        return f"{self.q}K{'+' if self.p >= 0 else '-'}{abs(self.p)}"


K0 = 3  # smallest K for which every decision made so far holds


def sign(e):
    """Sign of p + q*K for all large K; records the K from which it holds."""
    global K0
    if e.q == 0:
        return (e.p > 0) - (e.p < 0)
    s = 1 if e.q > 0 else -1
    # p + qK has sign s once K > -p/q
    bound = (-e.p) // e.q + 1 if e.q > 0 else (e.p) // (-e.q) + 1
    if bound > K0:
        K0 = bound
    return s


ZERO = Aff(0)
RSTATE = Aff(-1, 1)  # residue K-1: the square reads its R


def run(target=1500, extra_events=0):
    res = {}  # (x,y) -> Aff residue (count mod K)
    x = y = 0
    d = 0
    steps = Aff(0)  # number of moves made
    rturns = 0
    spins = 0
    reached = None
    events_after = 0
    log = []
    while True:
        # try to jump over a spin: 4 left turns that bring the ant back
        cells = []
        cx, cy, cd = x, y, d
        for _ in range(4):
            cells.append((cx, cy))
            cd = (cd + 3) & 3
            cx += DX[cd]
            cy += DY[cd]
        rems = [RSTATE - res.get(c, ZERO) for c in cells]  # visits left before R
        at_edge = reached is None and any(
            cx <= -target or cx >= target - 1 or cy <= -target or cy >= target - 1
            for cx, cy in cells)
        if not at_edge and all(sign(r) > 0 for r in rems):
            n = rems[0]
            for r in rems[1:]:
                if sign(r - n) < 0:
                    n = r
            for c in cells:
                res[c] = res.get(c, ZERO) + n
            steps = steps + n.scale(4)
            spins += 1
            continue
        # one ordinary step
        v = res.get((x, y), ZERO)
        if v == RSTATE:
            d = (d + 1) & 3
            res[(x, y)] = ZERO
            rturns += 1
            log.append((x, y, d, steps))
            if reached is not None:
                events_after += 1
                if events_after >= extra_events:
                    return reached, rturns, spins, log, res
        else:
            d = (d + 3) & 3
            res[(x, y)] = v + Aff(1)
        x += DX[d]
        y += DY[d]
        steps = steps + Aff(1)
        if reached is None and (x <= -target or x >= target - 1 or y <= -target or y >= target - 1):
            reached = steps
            if extra_events == 0:
                return reached, rturns, spins, log, res


if __name__ == "__main__":
    reached, rturns, spins, log, res = run()
    # the census counts the step index of the escaping move (moves - 1)
    print("moves to reach the edge:", reached)
    print("census step number     :", reached - Aff(1))
    print("right turns before edge:", rturns)
    print("spins jumped over      :", spins)
    print("valid for every K >=   :", K0)
