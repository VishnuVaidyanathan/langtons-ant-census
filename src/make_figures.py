"""
make_figures.py — the paper's figures, from data/census.csv and the C tools in ./build.

Usage:  python3 src/make_figures.py          (from the repository root)
Writes: figures/classes.png, figures/shares.pdf, figures/lkr_formula.pdf
"""
import collections
import csv
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, "build", "ant_snap")
VISITS = os.path.join(ROOT, "build", "ant_visits")
FIG = os.path.join(ROOT, "figures")
N = 1200
PAL = [(250, 249, 245), (44, 44, 42), (127, 119, 221), (29, 158, 117), (216, 90, 48),
       (212, 83, 126), (55, 138, 221), (186, 117, 23), (99, 153, 34), (136, 135, 128),
       (226, 75, 74), (93, 202, 165)]
rows = {r["rule"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data", "census.csv")))}


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def tile(rule, label, steps, size=300):
    raw = subprocess.run([SNAP, rule, str(steps)], capture_output=True).stdout
    im = Image.new("RGB", (N, N))
    im.putdata([PAL[b % len(PAL)] for b in raw])
    mask = Image.frombytes("L", (N, N), bytes(255 if b else 0 for b in raw))
    x0, y0, x1, y1 = mask.getbbox() or (0, 0, N, N)
    s = max(x1 - x0, y1 - y0) + 16
    cx, cy = (x0 + x1) // 2 + s, (y0 + y1) // 2 + s
    im = ImageOps.expand(im, border=s, fill=PAL[0])
    im = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).resize((size, size), Image.NEAREST)
    t = Image.new("RGB", (size, size + 30), (255, 255, 255))
    t.paste(im, (0, 0))
    ImageDraw.Draw(t).text((6, size + 6), label, fill=(40, 40, 40), font=font(16))
    return t


def grid(tiles, cols, title_rows=None):
    w, h = tiles[0].size
    n_rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (w + 10) + 10, n_rows * (h + 10) + 10), (255, 255, 255))
    for i, t in enumerate(tiles):
        out.paste(t, (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
    return out


# Figure 1: two examples of each class
examples = [("LRRRRRLLR", "square"), ("LRLLLLRLLR", "square"),
            ("LLRR", "symmetric"), ("LLRRRRLL", "symmetric"),
            ("LLRRRLRRRLLL", "triangle"), ("LLLLLLRRLRLL", "triangle"),
            ("LLLRRLLRL", "highway"), ("LRLRLRLRLRLL", "highway"),
            ("LLLRRLLLR", "chaotic"), ("LLRRLRRLL", "chaotic")]
tiles = []
for rule, cls in examples:
    assert rows[rule]["class"] == cls, (rule, rows[rule]["class"])
    steps = int(rows[rule]["steps_run"]) if cls == "highway" else 1000000
    tiles.append(tile(rule, f"{rule} ({cls})", steps, size=260))
grid(tiles, 2).save(os.path.join(FIG, "classes.png"))

# Figure 2: share of each class by K
CL = ["square", "highway", "symmetric", "triangle", "chaotic"]
COL = {"square": "#2a6fdb", "highway": "#1d9e75", "symmetric": "#d4537e",
       "triangle": "#d85a30", "chaotic": "#c4c2b8"}
cnt = collections.Counter((int(r["K"]), r["class"]) for r in rows.values())
Ks = list(range(2, 13))
fig, ax = plt.subplots(figsize=(6.5, 3.6))
left = [0.0] * len(Ks)
for c in CL:
    vals = [cnt[(K, c)] / sum(cnt[(K, cc)] for cc in CL) for K in Ks]
    ax.barh(Ks, vals, left=left, color=COL[c], label=c, height=0.7)
    left = [a + b for a, b in zip(left, vals)]
ax.set_yticks(Ks)
ax.invert_yaxis()
ax.set_ylabel("K (number of colours)")
ax.set_xlabel("share of distinct machines")
ax.set_xlim(0, 1)
ax.legend(ncol=5, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, 1.15), frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "shares.pdf"))
plt.close(fig)

# Figure 3: L^(K-1)R step it reaches the edge against K
pts = []
for K in list(range(3, 26)) + [30, 40, 50]:
    out = subprocess.run([VISITS, "L" * (K - 1) + "R"], capture_output=True, text=True).stdout.split()
    pts.append((K, int(out[1].split("=")[1])))
fig, ax = plt.subplots(figsize=(6.5, 3.2))
ks = [p[0] for p in pts]
ax.plot(ks, [26969 + 11980 * (k - 3) for k in ks], color="#888780", lw=1,
        label="26,969 + 11,980 (K - 3)")
ax.plot(ks, [p[1] for p in pts], "o", color="#2a6fdb", ms=4, label="measured")
ax.set_xlabel("K")
ax.set_ylabel("step it reaches the edge")
ax.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "lkr_formula.pdf"))
plt.close(fig)

print("figures written to", FIG)
