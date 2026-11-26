"""Find nonunimodal products and realize them by joining two supports."""

import argparse
import json
from itertools import combinations_with_replacement
from operator import itemgetter
from pathlib import Path

from domination import coefficients, edge_list, rooted_tree, strict_valley
from search import structured
from seeded_search import independence, prufer_edges


def candidate_shapes(limit):
    seeds = json.loads(Path(__file__).with_name("published-seeds.json").read_text(encoding="utf-8"))
    for seed in seeds:
        word = seed["prufer"]
        if len(word) + 2 <= limit:
            yield rooted_tree(len(word) + 2, list(prufer_edges(word)))
    yield from structured(limit)


def library(limit):
    by_polynomial = {}
    for shape in candidate_shapes(limit):
        counts = coefficients(shape)
        if strict_valley(counts) is not None:
            raise ValueError(f"Individual tree is already a counterexample: {edge_list(shape)}")
        if any(b*b < a*c for a, b, c in zip(counts, counts[1:], counts[2:])):
            by_polynomial.setdefault(counts, shape)
    return by_polynomial


def join(left, right):
    left_edges, right_edges = edge_list(left), edge_list(right)
    shift = len(left_edges) + 1

    def support(edges):
        degrees = [0] * (len(edges) + 1)
        for a, b in edges:
            degrees[a] += 1
            degrees[b] += 1
        for a, b in edges:
            if degrees[a] == 1:
                return b
            if degrees[b] == 1:
                return a
        raise ValueError("expected a tree with a support")

    joined = left_edges + [(a + shift, b + shift) for a, b in right_edges]
    return joined + [(support(left_edges), support(right_edges) + shift)]


def run(factor_limit, total_limit):
    catalog = library(factor_limit)
    width = (total_limit + 8) // 8
    items = sorted(((len(counts) - 1, shape, max(independence(shape)), int.from_bytes(b"".join(
        count.to_bytes(width, "little") for count in counts), "little"))
                   for counts, shape in catalog.items()), key=itemgetter(0))
    tested = positive_curvature = positive_central = 0
    first_positive = None
    for (n, left, alpha_left, p), (m, right, alpha_right, q) in combinations_with_replacement(items, 2):
        order = n + m
        if order > total_limit:
            continue
        packed = (p*q).to_bytes(width * (order + 1), "little")
        counts = tuple(int.from_bytes(packed[i:i + width], "little")
                       for i in range(0, len(packed), width))
        tested += 1
        valley = strict_valley(counts)
        violations = [k for k in range(1, order) if counts[k]**2 < counts[k-1] * counts[k+1]]
        violation = violations[0] if violations else None
        gamma = next(k for k, count in enumerate(counts) if count)
        band = ((order + 2 * gamma + 1) // 3 + 1, (order + 2 * (alpha_left + alpha_right)) // 3 - 1)
        central = any(band[0] <= k <= band[1] for k in violations)
        positive_curvature += bool(violations)
        positive_central += central
        if valley is not None and not central:
            raise RuntimeError("the central-band curvature missed a strict valley")
        if valley is not None or (violation is not None and first_positive is None):
            edges = join(left, right)
            if coefficients(rooted_tree(order, edges)) != counts:
                raise RuntimeError("exact product and joined tree disagree")
            record = {"order": order, "factor_orders": [n, m], "edges": edges,
                      "valley": valley, "band": band, "first_log_concavity_failure": violation,
                      "coefficient_triplet": counts[violation - 1:violation + 2]}
            if valley is not None:
                print(json.dumps({"witness": record, "coefficients": counts}), flush=True)
                break
            first_positive = record
    print(json.dumps({"factor_order_limit": factor_limit, "total_order_limit": total_limit,
                      "distinct_non_log_concave_factors": len(items), "tested_pairs": tested,
                      "non_log_concave_pairs": positive_curvature,
                      "pairs_non_log_concave_in_band": positive_central,
                      "first_non_log_concave_pair": first_positive}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-factor-order", type=int, default=350)
    parser.add_argument("--max-total-order", type=int, default=450)
    args = parser.parse_args()
    run(args.max_factor_order, args.max_total_order)


if __name__ == "__main__":
    main()
