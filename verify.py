"""Cross-check exact footprints with direct subset counts and leaf factorization."""

import argparse
import json
from math import comb
from pathlib import Path

from domination import coefficients, edge_list, rooted_tree, strict_valley
from search import catalogue


def direct_counts(order, edges):
    neighborhoods = [1 << v for v in range(order)]
    for first, second in edges:
        neighborhoods[first] |= 1 << second
        neighborhoods[second] |= 1 << first
    full = (1 << order) - 1
    covered = [0] * (1 << order)
    counts = [0] * (order + 1)
    for subset in range(1, 1 << order):
        bit = subset & -subset
        covered[subset] = covered[subset ^ bit] | neighborhoods[bit.bit_length() - 1]
        if covered[subset] == full:
            counts[subset.bit_count()] += 1
    return tuple(counts)


def multiply(first, second):
    counts = [0] * (len(first) + len(second) - 1)
    for i, a in enumerate(first):
        for j, b in enumerate(second):
            counts[i + j] += a * b
    return counts


def leaf_factorization(order, edges):
    adjacency = [set() for _ in range(order)]
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    leaves = {v for v, neighbors in enumerate(adjacency) if len(neighbors) == 1}
    supports = {v: len(neighbors & leaves) for v, neighbors in enumerate(adjacency)
                if neighbors & leaves}
    bare = set(range(order)) - leaves - supports.keys()
    claimed = set()
    for v in bare:
        if adjacency[v] & (bare | claimed):
            return None
        claimed.update(adjacency[v])

    def support_factor(t):
        result = [0] + [comb(t, j) for j in range(t + 1)]
        result[t] += 1
        return result

    counts = [1]
    for v in bare:
        block = [1, 1]
        total_leaves = 0
        for neighbor in adjacency[v]:
            t = supports[neighbor]
            block = multiply(block, support_factor(t))
            total_leaves += t
        block[total_leaves] -= 1
        counts = multiply(counts, block)
    for v in supports.keys() - claimed:
        counts = multiply(counts, support_factor(supports[v]))
    return tuple(counts)


def verify(brute_max, factor_max):
    brute = 0
    by_order = []
    for order, shapes in catalogue(1, max(brute_max, factor_max)):
        factored = 0
        for shape in shapes:
            edges = edge_list(shape)
            if order <= brute_max:
                expected = direct_counts(order, edges)
                for root in (0, order - 1):
                    if coefficients(rooted_tree(order, edges, root)) != expected:
                        raise RuntimeError(f"subset enumeration disagrees for {edges}")
                brute += 1
            if 3 <= order <= factor_max:
                result = leaf_factorization(order, edges)
                if result is None:
                    continue
                if result != coefficients(shape):
                    raise RuntimeError(f"factorization disagrees for {edges}")
                if any(b * b < a * c for a, b, c in zip(result, result[1:], result[2:])):
                    raise RuntimeError(f"factorization yields non-log-concavity for {edges}")
                factored += 1
        by_order.append([order, factored])
    return {"brute_force_trees": brute, "brute_force_max_order": brute_max,
            "factored_trees_by_order": by_order}


def verify_archived_witness(path):
    witness = json.loads(Path(path).read_text(encoding="utf-8"))
    order, edges = witness["order"], witness["edges"]
    expected = tuple(witness["coefficients"])
    for root in (0, order - 1):
        if coefficients(rooted_tree(order, edges, root)) != expected:
            raise ValueError("coefficient mismatch on replay")
    first, middle, last = witness["valley"]
    if not (0 <= first < middle < last <= order
            and expected[middle] < min(expected[first], expected[last])):
        raise ValueError("archived indices do not show a strict valley")
    if strict_valley(expected) is None:
        raise ValueError("no strict valley")
    return {"order": order, "valley": [first, middle, last]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brute-max", default=11, type=int)
    parser.add_argument("--factor-max", default=16, type=int)
    parser.add_argument("--witness")
    args = parser.parse_args()
    result = (verify_archived_witness(args.witness) if args.witness
              else verify(args.brute_max, args.factor_max))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
