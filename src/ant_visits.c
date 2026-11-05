/*
 * ant_visits.c — run one rule string and report when it reaches the grid edge
 * and the largest number of visits any single square received.
 *
 * Usage:  ant_visits RULE [MAX_STEPS]       (MAX_STEPS default 100000000)
 * Output: RULE steps=S maxvisits=M
 *   S is the index (counting from 0) of the step whose move took the ant within
 *   one square of the edge of a 3000 x 3000 grid, i.e. 1,500 squares from the
 *   start; this is the "step it reaches the edge" used throughout the paper.
 *   If the edge is not reached, S = MAX_STEPS.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 3000
static unsigned int v[N * N];

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s RULE [MAX_STEPS]\n", argv[0]); return 1; }
    const char *r = argv[1];
    int K = strlen(r);
    long T = argc > 2 ? atol(argv[2]) : 100000000L;
    const int dx[4] = {0, 1, 0, -1}, dy[4] = {-1, 0, 1, 0};
    int x = N / 2, y = N / 2, d = 0;
    unsigned mx = 0;
    long s;
    for (s = 0; s < T; s++) {
        int k = y * N + x;
        unsigned q = v[k] % K;
        d = r[q] == 'R' ? (d + 1) & 3 : (d + 3) & 3;
        v[k]++;
        if (v[k] > mx) mx = v[k];
        x += dx[d]; y += dy[d];
        if (x < 1 || y < 1 || x >= N - 1 || y >= N - 1) break;
    }
    printf("%s steps=%ld maxvisits=%u\n", r, s, mx);
    return 0;
}
