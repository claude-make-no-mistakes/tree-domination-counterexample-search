#include "nauty.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LIMIT 28

struct child_products {
    uint32_t permissive[LIMIT + 1];
    uint32_t internal[LIMIT + 1];
    uint32_t waiting[LIMIT + 1];
    int degree;
};

static uint64_t checked, nonconcave, nonunimodal;
static uint64_t coefficient_sums[LIMIT + 1];
static int order;

#ifdef STRUCTURAL_FILTER
static uint64_t evaluated;

/* This sieve applies only where the minimum-order support reduction applies. */
static int retained(const int *par, int n)
{
    uint32_t neighbors[LIMIT] = {0};
    for (int v = 1; v < n; ++v) {
        int parent = par[v + 1] - 1;
        neighbors[v] |= UINT32_C(1) << parent;
        neighbors[parent] |= UINT32_C(1) << v;
    }
    uint32_t leaves = 0, supports = 0;
    for (int v = 0; v < n; ++v)
        if (neighbors[v] && !(neighbors[v] & (neighbors[v] - 1))) {
            leaves |= UINT32_C(1) << v;
            supports |= neighbors[v];
        }
    for (uint32_t remaining = supports; remaining; remaining &= remaining - 1)
        if (neighbors[__builtin_ctz(remaining)] & supports) return 0;
    uint32_t bare = ((UINT32_C(1) << n) - 1) & ~(leaves | supports);
    for (uint32_t remaining = bare; remaining; remaining &= remaining - 1) {
        int v = __builtin_ctz(remaining);
        uint32_t near = neighbors[v];
        for (uint32_t adjacent = near; adjacent; adjacent &= adjacent - 1)
            near |= neighbors[__builtin_ctz(adjacent)];
        near &= bare ^ (UINT32_C(1) << v);
        if (near & (near - 1)) return 1;
    }
    return 0;
}
#endif

/* At all stages the entries count subsets of at most LIMIT vertices. */
static void multiply(uint32_t *p, int a, const uint32_t *q, int b)
{
    uint32_t result[LIMIT + 1] = {0};
    for (int i = 0; i <= a; ++i)
        for (int j = 0; j <= b; ++j)
            result[i + j] += p[i] * q[j];
    memcpy(p, result, (size_t) (a + b + 1) * sizeof(*p));
}

static void print_record(FILE *out, const int *par, int n, const uint32_t *coefficients,
                         int bad_concavity, int valley)
{
    fprintf(out, "{\"order\":%d,\"non_log_concave\":%d,\"nonunimodal\":%d,"
                 "\"parents\":[", n, bad_concavity, valley);
    for (int v = 2; v <= n; ++v) fprintf(out, "%s%d", v == 2 ? "" : ",", par[v]);
    fputs("],\"coefficients\":[", out);
    for (int k = 0; k <= n; ++k) fprintf(out, "%s%" PRIu32, k ? "," : "", coefficients[k]);
    fputs("]}\n", out);
    fflush(out);
}

void domination_scan(FILE *out, int *par, int n)
{
    if (n < 1 || n > LIMIT) {
        fprintf(stderr, "order must be 1 through %d\n", LIMIT);
        exit(EXIT_FAILURE);
    }
    order = n;
    ++checked;
    for (int v = 2; v <= n; ++v)
        if (par[v] < 1 || par[v] >= v) {
            fputs("unexpected gentreeg parent order\n", stderr);
            exit(EXIT_FAILURE);
        }
#ifdef STRUCTURAL_FILTER
    if (!retained(par, n)) return;
    ++evaluated;
#endif
    struct child_products dp[LIMIT + 1];
    for (int v = 1; v <= n; ++v) {
        dp[v].permissive[0] = dp[v].internal[0] = dp[v].waiting[0] = 1;
        dp[v].degree = 0;
    }

    for (int v = n; v >= 2; --v) {
        const struct child_products *child = &dp[v];
        struct child_products *parent = &dp[par[v]];
        const int d = child->degree;
        uint32_t internal[LIMIT + 1], waiting[LIMIT + 1], permissive[LIMIT + 1];
        for (int k = 0; k <= d + 1; ++k) {
            uint32_t selected = k ? child->permissive[k - 1] : 0;
            uint32_t unselected = k <= d ? child->internal[k] : 0;
            waiting[k] = k <= d ? unselected - child->waiting[k] : 0;
            internal[k] = selected + waiting[k];
            permissive[k] = selected + unselected;
        }
        multiply(parent->permissive, parent->degree, permissive, d + 1);
        multiply(parent->internal, parent->degree, internal, d + 1);
        multiply(parent->waiting, parent->degree, waiting, d + 1);
        parent->degree += d + 1;
    }
    if (dp[1].degree != n - 1) {
        fputs("unexpected tree order in recurrence\n", stderr);
        exit(EXIT_FAILURE);
    }
    uint32_t coefficients[LIMIT + 1];
    for (int k = 0; k <= n; ++k) {
        uint32_t selected = k ? dp[1].permissive[k - 1] : 0;
        uint32_t absent = k < n ? dp[1].internal[k] - dp[1].waiting[k] : 0;
        coefficients[k] = selected + absent;
        coefficient_sums[k] += coefficients[k];
    }
    int fell = 0, valley = 0, bad = 0;
    for (int k = 1; k <= n; ++k) {
        if (coefficients[k] > coefficients[k - 1] && fell) valley = 1;
        if (coefficients[k] < coefficients[k - 1]) fell = 1;
        if (k < n && (uint64_t) coefficients[k] * coefficients[k]
                     < (uint64_t) coefficients[k - 1] * coefficients[k + 1])
            bad = 1;
    }
    if (valley || (bad && !nonconcave)) print_record(out, par, n, coefficients, bad, valley);
    nonconcave += (uint64_t) bad;
    nonunimodal += (uint64_t) valley;
}

void domination_summary(nauty_counter total, double cpu)
{
    (void) cpu;
    if ((uint64_t) total != checked) {
        fputs("tree generation and evaluation counts differ\n", stderr);
        exit(EXIT_FAILURE);
    }
    printf("{\"order\":%d,\"trees\":%" PRIu64, order, checked);
#ifdef STRUCTURAL_FILTER
    printf(",\"evaluated\":%" PRIu64, evaluated);
#endif
    printf(",\"non_log_concave\":%" PRIu64 ",\"nonunimodal\":%" PRIu64
           ",\"coefficient_sums\":[", nonconcave, nonunimodal);
    for (int k = 0; k <= order; ++k)
        printf("%s%" PRIu64, k ? "," : "", coefficient_sums[k]);
    puts("]}");
}
