"""
classify.py — turn the raw census rows into one row per distinct machine with a class.

Usage:  python3 classify.py data/census_raw.csv data/census.csv

Steps:
1. Remove repeating strings (a smaller string written several times, e.g. RLRL = RL twice):
   the ant walks exactly the same path, so the string is not a new machine.
2. Merge mirror twins (swap every L and R): the picture is the same, mirrored.
   Each pair is kept once, written in the form that comes first alphabetically
   (it starts with L).
3. Give each machine one class, tested in this order:
   highway    reached the grid edge and painted under 5% of the box it crossed
   triangle   box width/height ratio over 0.8, one diagonal half under 3% painted,
              the opposite half over 30% painted
   symmetric  colour_symmetry over 0.9 and fill under 0.95
   square     width/height ratio over 0.9 and fill over 0.86
              (or fill over 0.8 with edge_fill over 0.6)
   chaotic    everything else
"""
import csv
import sys

SWAP = str.maketrans("LR", "RL")


def is_primitive(s):
    k = len(s)
    return not any(k % p == 0 and s == s[:p] * (k // p) for p in range(1, k))


def classify(r):
    esc = int(r["escaped"])
    w, h = int(r["width"]), int(r["height"])
    fill, edge = float(r["fill"]), float(r["edge_fill"])
    ha, hb, hc, hd = (float(r[c]) for c in ("half_a", "half_b", "half_c", "half_d"))
    sym = float(r["colour_symmetry"])
    ratio = min(w, h) / max(w, h)
    triangle = any(full > 0.3 and empty < 0.03
                   for full, empty in ((ha, hb), (hb, ha), (hc, hd), (hd, hc)))
    if esc:
        return "highway" if fill < 0.05 else "chaotic"
    if w <= 4 and h <= 4:
        return "chaotic"
    if triangle and ratio > 0.8:
        return "triangle"
    if sym > 0.9 and fill < 0.95:
        return "symmetric"
    if ratio > 0.9 and (fill > 0.86 or (fill > 0.8 and edge > 0.6)):
        return "square"
    if sym > 0.9:
        return "symmetric"
    return "chaotic"


def main(src, dst):
    seen = set()
    out = []
    for r in csv.DictReader(open(src)):
        s = r["rule"]
        if not is_primitive(s):
            continue
        key = min(s, s.translate(SWAP))
        if key in seen:
            continue
        seen.add(key)
        out.append([r["K"], key, classify(r), r["steps"], r["width"], r["height"],
                    r["fill"], r["edge_fill"], r["colour_symmetry"]])
    with open(dst, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["K", "rule", "class", "steps_run", "width", "height",
                    "fill", "edge_fill", "colour_symmetry"])
        w.writerows(out)
    print(f"{len(out)} distinct machines written to {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
