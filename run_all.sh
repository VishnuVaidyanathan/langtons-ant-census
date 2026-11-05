#!/usr/bin/env bash
# Rebuild every result in the paper from scratch.
# Needs: a C compiler (gcc or cc), Python 3, matplotlib and Pillow (figures only).
# Takes about two minutes on a laptop.
set -euo pipefail
cd "$(dirname "$0")"
CC=${CC:-gcc}
mkdir -p build data figures

echo "== Building the C tools"
for t in ant_census ant_visits ant_snap; do
    "$CC" -O2 -o "build/$t" "src/$t.c"
done

echo "== Census: every rule string for K = 2 to 12, 1 million steps each"
echo "K,rule,escaped,steps,width,height,fill,edge_fill,half_a,half_b,half_c,half_d,colour_symmetry" > data/census_raw.csv
for K in $(seq 2 12); do
    ./build/ant_census "$K" 1000000 >> data/census_raw.csv
done
python3 src/classify.py data/census_raw.csv data/census.csv

echo "== Census numbers and observations"
python3 src/analyse.py

echo "== Proof: the L^(K-1)R formula and highway, for every K >= 4"
python3 proof/symbolic.py
python3 proof/highway.py
echo "== Proof certificate: write it, then check it with the independent checker"
python3 proof/write_certificate.py
python3 proof/check_certificate.py
echo "== Proof: K = 3 with plain numbers"
python3 proof/highway_concrete.py 3
echo "== Supporting observations"
python3 proof/skeleton.py

echo "== Figures"
python3 src/make_figures.py
