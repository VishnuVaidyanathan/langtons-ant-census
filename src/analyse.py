"""
analyse.py — every number in the paper's census and observation sections.

Usage:  python3 src/analyse.py            (from the repository root, after run_all.sh built ./build)
Writes: data/analysis.txt, data/highways.txt, data/squares.txt
"""
import collections
import csv
import os
import re
import statistics
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
VISITS = os.path.join(ROOT, "build", "ant_visits")
CLASSES = ["highway", "square", "triangle", "symmetric", "chaotic"]

rows = list(csv.DictReader(open(os.path.join(DATA, "census.csv"))))
out = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line)
    out.append(line)


def visits(rule, limit=100000000):
    o = subprocess.run([VISITS, rule, str(limit)], capture_output=True, text=True).stdout.split()
    return int(o[1].split("=")[1]), int(o[2].split("=")[1])


# 1. Counts by K and class -------------------------------------------------
say("== 1. Distinct machines by K and class ==")
cnt = collections.Counter((int(r["K"]), r["class"]) for r in rows)
say("K", *CLASSES, "total")
for K in range(2, 13):
    say(K, *[cnt[(K, c)] for c in CLASSES], sum(cnt[(K, c)] for c in CLASSES))
say("all", *[sum(cnt[(K, c)] for K in range(2, 13)) for c in CLASSES], len(rows))


# 2. Even runs and symmetry --------------------------------------------------
def even_runs(s):
    """True if, read in a circle, every run of equal letters has even length."""
    if len(set(s)) == 1:
        return False
    i = 0
    while s[i] == s[-1]:
        i += 1
    t = s[i:] + s[:i]
    return all(len(m) % 2 == 0 for m in re.findall(r"L+|R+", t))


say("\n== 2. Even-run rules versus the symmetric class ==")
tab = collections.Counter((even_runs(r["rule"]), r["class"]) for r in rows)
for k in sorted(tab):
    say(k, tab[k])

# 3. First letters --------------------------------------------------------------
say("\n== 3. Class shares by first three letters (K = 6 to 12) ==")
pre = collections.defaultdict(collections.Counter)
for r in rows:
    if int(r["K"]) >= 6:
        pre[r["rule"][:3]][r["class"]] += 1
for p in sorted(pre):
    t = sum(pre[p].values())
    say(p, t, {c: f"{pre[p][c] / t:.0%}" for c in CLASSES if pre[p][c]})

say("\n== 3b. Highways by first two letters, per K ==")
for K in range(3, 13):
    ll = sum(1 for r in rows if int(r["K"]) == K and r["class"] == "highway" and r["rule"][:2] == "LL")
    lr = sum(1 for r in rows if int(r["K"]) == K and r["class"] == "highway" and r["rule"][:2] == "LR")
    say(f"K={K} LL={ll} LR={lr}")
first_lr = min((int(r["steps_run"]), r["rule"]) for r in rows
               if r["class"] == "highway" and r["rule"][:2] == "LR" and int(r["K"]) == 7)
say("first LR highway (K = 7):", first_lr)

# 4. Hidden copies among highways -------------------------------------------------
say("\n== 4. Highways: letters actually read ==")


def root(p):
    """Shortest string whose repetition gives p."""
    for n in range(1, len(p) + 1):
        if len(p) % n == 0 and p == p[:n] * (len(p) // n):
            return p[:n]


hw = [r for r in rows if r["class"] == "highway"]
fam = collections.Counter()
paths = collections.defaultdict(list)
for r in hw:
    s = r["rule"]
    st, M = visits(s)
    read = s[:M] if M < len(s) else s          # letters the ant ever reads
    if M < len(s):
        fam[read] += 1
    paths[(root(read), st)].append(s)
say("highways:", len(hw), "| machines that never read their last letters:", sum(fam.values()))
for p, n in fam.most_common():
    say(f"  letters read {p:<14} same path as {root(p):<12} machines {n}")
say("truly different highway paths:", len(paths))

# 5. The L...LR family ------------------------------------------------------------------
say("\n== 5. L^(K-1)R: step it reaches the edge and most visits ==")
for K in list(range(3, 26)) + [30, 40, 50, 75, 100, 150, 200, 300, 500, 1000]:
    st, M = visits("L" * (K - 1) + "R")
    pred = 26969 + 11980 * (K - 3)
    say(f"K={K} steps={st} formula={pred} match={st == pred} maxvisits={M} 2K={2 * K}")

# 6. Slow growers ----------------------------------------------------------------------------
small = [r for r in rows if r["class"] != "highway" and max(int(r["width"]), int(r["height"])) < 40]
say("\n== 6. Non-highway machines under 40 squares wide after 1 million steps:", len(small))

open(os.path.join(DATA, "analysis.txt"), "w").write("\n".join(out) + "\n")

# Lists ------------------------------------------------------------------------------------------
for cls, name, key, note in (("highway", "highways.txt", "steps_run", "step it reached the edge"),
                             ("square", "squares.txt", "width", "square width after 1 million steps")):
    by = collections.defaultdict(list)
    for r in rows:
        if r["class"] == cls:
            by[int(r["K"])].append((r["rule"], int(r[key])))
    with open(os.path.join(DATA, name), "w") as f:
        f.write(f"All {sum(len(v) for v in by.values())} {cls} machines, K = 2 to 12\n")
        f.write(f"(mirror twins merged; L-first form) - rule, then {note}\n\n")
        for K in sorted(by):
            f.write(f"K = {K}  ({len(by[K])} machines)\n")
            order = sorted(by[K], key=lambda t: t[1] if cls == "highway" else -t[1])
            for rule, val in order:
                f.write(f"  {rule:<14}{val:>9,}\n")
            f.write("\n")

# Chaotic list ----------------------------------------------------------------------------------
by = collections.defaultdict(list)
for r in rows:
    if r["class"] == "chaotic":
        by[int(r["K"])].append(r)
with open(os.path.join(DATA, "chaotic.txt"), "w") as f:
    f.write(f"All {sum(len(v) for v in by.values())} chaotic machines, K = 2 to 12\n")
    f.write("(mirror twins merged; L-first form)\n")
    f.write("Rule, then the box width x height after 1 million steps, and the share of the box that is coloured\n\n")
    for K in sorted(by):
        f.write(f"K = {K}  ({len(by[K])} machines)\n")
        for r in sorted(by[K], key=lambda r: r["rule"]):
            f.write(f"  {r['rule']:<14}{r['width']:>5} x {r['height']:<5}{float(r['fill']) * 100:5.0f}%\n")
        f.write("\n")
