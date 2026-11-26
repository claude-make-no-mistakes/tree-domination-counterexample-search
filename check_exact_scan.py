"""Compare native enumeration totals against the independent Python evaluator."""

from argparse import ArgumentParser
import json
from pathlib import Path
from subprocess import check_output

import networkx as nx

from domination import coefficients, rooted_tree, strict_valley


def retained(tree):
    leaves = {v for v, degree in tree.degree if degree == 1}
    supports = {next(iter(tree[v])) for v in leaves}
    if any(u in supports and v in supports for u, v in tree.edges()):
        return False
    bare = set(tree) - leaves - supports
    return any(len(bare & (set(nx.single_source_shortest_path_length(tree, v, cutoff=2)) - {v})) >= 2
               for v in bare)


def check(scanner, highest, filtered):
    checked = 0
    for n in range(1, highest + 1):
        records = check_output([str(scanner), "-q", str(n)], text=True).splitlines()
        if not records:
            raise RuntimeError(f"scanner gave no report at order {n}")
        native = json.loads(records[-1])
        expected = {"order": n, "trees": 0, "non_log_concave": 0,
                    "nonunimodal": 0, "coefficient_sums": [0] * (n + 1)}
        if filtered:
            expected["evaluated"] = 0
        trees = (nx.empty_graph(1),) if n == 1 else nx.nonisomorphic_trees(n)
        for tree in trees:
            expected["trees"] += 1
            if filtered:
                if not retained(tree):
                    continue
                expected["evaluated"] += 1
            counts = coefficients(rooted_tree(n, list(tree.edges())))
            expected["non_log_concave"] += any(
                b * b < a * c for a, b, c in zip(counts, counts[1:], counts[2:])
            )
            expected["nonunimodal"] += strict_valley(counts) is not None
            expected["coefficient_sums"] = [
                a + b for a, b in zip(expected["coefficient_sums"], counts)
            ]
        if native != expected:
            raise RuntimeError(f"independent aggregate mismatch at order {n}")
        checked += expected["trees"]
    return checked


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("scanner", type=Path)
    parser.add_argument("--max-order", default=16, type=int)
    parser.add_argument("--filtered", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_order <= 28:
        parser.error("order must be in 1 through 28")
    checked = check(args.scanner.resolve(strict=True), args.max_order, args.filtered)
    print(json.dumps({"order_limit": args.max_order, "filtered": args.filtered,
                      "matched_aggregate_trees": checked}))
