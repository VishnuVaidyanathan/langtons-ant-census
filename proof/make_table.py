"""
make_table.py — write paper/table35.tex (Table 1 of the paper) from proof/certificate.txt:
every action of L^(K-1)R up to its 21st right turn, with the step at which it starts.

Usage:  python3 proof/make_table.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = ["up", "right", "down", "left"]


def expr(a, b):
    if b == 0:
        return f"{a}"
    k = "K" if b == 1 else f"{b}K"
    return f"${k}$" if a == 0 else f"${k}{'+' if a > 0 else '-'}{abs(a)}$"


rows = []
step = (0, 0)
rt = 0
for n, f in enumerate((l.split() for l in open(os.path.join(HERE, "certificate.txt"))
                       if not l.startswith("#")), 1):
    if f[0] == "E":
        continue
    head = f"{n} & {expr(*step)} & $({f[1]},{f[2]})$ & {DIRS[int(f[3])]}"
    if f[0] == "S":
        if f[6] == "R":
            rt += 1
        turn = f"right ({rt})" if f[6] == "R" else "left"
        rows.append(f"{head} & step & {expr(int(f[4]), int(f[5]))} & {turn} \\\\")
        step = (step[0] + 1, step[1])
        if rt == 21:
            break
    else:
        a, b = int(f[4]), int(f[5])
        laps = "1 lap" if (a, b) == (1, 0) else f"{expr(a, b)} laps"
        rows.append(f"{head} & spin & & {laps} \\\\")
        step = (step[0] + 4 * a, step[1] + 4 * b)

out = os.path.join(os.path.dirname(HERE), "paper", "table35.tex")
open(out, "w").write("\n".join(rows) + "\n")
print(f"wrote {len(rows)} rows to {out}")
