/*
 * ant_census.c — run every rule string with K colours and print shape measures.
 *
 * Usage:  ant_census K STEPS
 * Output: one CSV row per rule string (all 2^K strings of L and R):
 *   K,rule,escaped,steps,width,height,fill,edge_fill,half_a,half_b,half_c,half_d,colour_symmetry
 *
 * The ant starts at the centre of an N x N grid of zeros, facing up.
 * Each step: read the colour c of the current square, turn by rule[c]
 * (L = left, R = right), set the square to (c + 1) mod K, move forward.
 * The run stops after STEPS steps or when the ant comes within one square
 * of the grid edge (1,500 squares from the start), which is reported as escaped.
 *
 * Shape measures on the bounding box of the visited squares at the end:
 *   fill            share of squares in the box that are non-zero
 *   edge_fill       share of the box's border squares that are non-zero
 *   half_a .. half_d  share of non-zero squares in the four triangles cut off
 *                   by the box's two diagonals (a: above the anti-diagonal,
 *                   b: below it, c: below the main diagonal, d: above it)
 *   colour_symmetry best match (share of squares with equal colour) between the
 *                   picture and its 180-degree turn, left-right mirror,
 *                   up-down mirror, or (square boxes only) its two diagonal mirrors
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 3000
static unsigned char g[N * N];

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s K STEPS\n", argv[0]); return 1; }
    int K = atoi(argv[1]);
    long T = atol(argv[2]);
    const int dx[4] = {0, 1, 0, -1}, dy[4] = {-1, 0, 1, 0};

    for (int m = 0; m < (1 << K); m++) {
        char r[64];
        for (int i = 0; i < K; i++) r[i] = (m >> (K - 1 - i)) & 1 ? 'R' : 'L';
        r[K] = 0;

        memset(g, 0, sizeof g);
        int x = N / 2, y = N / 2, d = 0, esc = 0;
        int minx = x, maxx = x, miny = y, maxy = y;
        long s;
        for (s = 0; s < T; s++) {
            int k = y * N + x, c = g[k];
            d = r[c] == 'R' ? (d + 1) & 3 : (d + 3) & 3;
            g[k] = (c + 1) % K;
            x += dx[d]; y += dy[d];
            if (x < 1 || y < 1 || x >= N - 1 || y >= N - 1) { esc = 1; break; }
            if (x < minx) minx = x; if (x > maxx) maxx = x;
            if (y < miny) miny = y; if (y > maxy) maxy = y;
        }
        int w = maxx - minx + 1, h = maxy - miny + 1;

        long nz = 0, edge = 0, etot = 0;
        long a1 = 0, a2 = 0, b1 = 0, b2 = 0, c1 = 0, c2 = 0, d1 = 0, d2 = 0;
        for (int j = miny; j <= maxy; j++)
            for (int i = minx; i <= maxx; i++) {
                int v = g[j * N + i] != 0;
                nz += v;
                double u = (double)(i - minx) / (w > 1 ? w - 1 : 1);
                double t = (double)(j - miny) / (h > 1 ? h - 1 : 1);
                if (u + t < 1) { a1 += v; a2++; } else if (u + t > 1) { b1 += v; b2++; }
                if (u < t) { c1 += v; c2++; } else if (u > t) { d1 += v; d2++; }
            }
        for (int i = minx; i <= maxx; i++) { etot += 2; edge += (g[miny * N + i] != 0) + (g[maxy * N + i] != 0); }
        for (int j = miny; j <= maxy; j++) { etot += 2; edge += (g[j * N + minx] != 0) + (g[j * N + maxx] != 0); }

        double best = 0;
        for (int tr = 0; tr < 5; tr++) {
            if (tr >= 3 && w != h) continue;
            long eq = 0, tt = 0;
            for (int j = miny; j <= maxy; j++)
                for (int i = minx; i <= maxx; i++) {
                    int u = i - minx, t = j - miny, uu, vv;
                    if (tr == 0)      { uu = w - 1 - u; vv = h - 1 - t; }
                    else if (tr == 1) { uu = w - 1 - u; vv = t; }
                    else if (tr == 2) { uu = u; vv = h - 1 - t; }
                    else if (tr == 3) { uu = t; vv = u; }
                    else              { uu = w - 1 - t; vv = h - 1 - u; }
                    int a = g[j * N + i], b = g[(miny + vv) * N + (minx + uu)];
                    if (a || b) { tt++; if (a == b) eq++; }
                }
            double sc = tt ? (double)eq / tt : 0;
            if (sc > best) best = sc;
        }

        printf("%d,%s,%d,%ld,%d,%d,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n", K, r, esc, s, w, h,
               (double)nz / ((double)w * h), (double)edge / etot,
               a2 ? (double)a1 / a2 : 0, b2 ? (double)b1 / b2 : 0,
               c2 ? (double)c1 / c2 : 0, d2 ? (double)d1 / d2 : 0, best);
        fflush(stdout);
    }
    return 0;
}
