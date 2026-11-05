/*
 * ant_snap.c — run one rule string and write the final grid as raw bytes.
 *
 * Usage:  ant_snap RULE STEPS > grid.bin
 * Output: 1200 x 1200 bytes, row by row, each the colour (0..K-1) of a square.
 * The run stops early if the ant comes within one square of the grid edge.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 1200
static unsigned char g[N * N];

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s RULE STEPS\n", argv[0]); return 1; }
    const char *r = argv[1];
    int K = strlen(r);
    long T = atol(argv[2]);
    const int dx[4] = {0, 1, 0, -1}, dy[4] = {-1, 0, 1, 0};
    int x = N / 2, y = N / 2, d = 0;
    for (long s = 0; s < T; s++) {
        int k = y * N + x, q = g[k];
        d = r[q] == 'R' ? (d + 1) & 3 : (d + 3) & 3;
        g[k] = (q + 1) % K;
        x += dx[d]; y += dy[d];
        if (x < 1 || y < 1 || x >= N - 1 || y >= N - 1) break;
    }
    fwrite(g, 1, N * N, stdout);
    return 0;
}
