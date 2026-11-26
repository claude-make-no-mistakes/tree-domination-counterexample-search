"""Enumerate trees with independent supports from their nonleaf cores."""

import argparse
import json

from domination import coefficients, edge_list, strict_valley


def independent_supports(core):
    leaves = {v for v in core if core.degree(v) == 1}
    neighbors = {v: set(core[v]) for v in core}
    if any(neighbors[v] & leaves for v in leaves):
        return
    blocked = leaves | set().union(*(neighbors[v] for v in leaves))
    optional = sorted(set(core) - blocked)

    def choices(index, chosen, excluded):
        if index == len(optional):
            yield tuple(sorted(chosen))
            return
        v = optional[index]
        yield from choices(index + 1, chosen, excluded)
        if v not in excluded:
            yield from choices(index + 1, chosen | {v}, excluded | neighbors[v])

    yield from choices(0, leaves, blocked)


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def core_ordering(core, root):
    vertices = [root]
    parent = {root: None}
    for v in vertices:
        for w in core[v]:
            if w != parent[v]:
                vertices.append(w)
                parent[w] = v
    children = {v: tuple(w for w in core[v] if w != parent[v]) for v in core}
    return list(reversed(vertices)), children


def decorated(ordering, support_counts):
    vertices, children = ordering
    shapes = {}
    for v in vertices:
        shapes[v] = tuple(sorted([shapes[w] for w in children[v]]
                                 + [()] * support_counts.get(v, 0)))
    return shapes[vertices[-1]]


def scan(min_order, max_order, max_core):
    import networkx as nx

    for size in range(3, max_core + 1):
        seen = set()
        trials = nonconcave = 0
        for core in nx.nonisomorphic_trees(size):
            orderings = [core_ordering(core, v) for v in nx.center(core)]
            for supports in independent_supports(core):
                bare = set(core) - set(supports)
                if not any(len((set(core[v]) | {v}) & bare) >= 2 for v in core):
                    continue
                for leaf_count in range(max(len(supports), min_order - size), max_order - size + 1):
                    for counts in compositions(leaf_count, len(supports)):
                        trials += 1
                        support_counts = dict(zip(supports, counts))
                        shape = min(decorated(ordering, support_counts) for ordering in orderings)
                        if shape in seen:
                            continue
                        seen.add(shape)
                        values = coefficients(shape)
                        valley = strict_valley(values)
                        if valley:
                            print(json.dumps({"core_order": size, "order": size + leaf_count,
                                              "edges": edge_list(shape), "valley": valley,
                                              "coefficients": values}), flush=True)
                            return
                        nonconcave += any(b*b < a*c for a, b, c in zip(values, values[1:], values[2:]))
        print(json.dumps({"core_order": size, "min_order": min_order, "max_order": max_order,
                          "color_and_leaf_assignments": trials, "distinct_trees": len(seen),
                          "non_log_concave": nonconcave, "witness": None}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-order", type=int, default=20)
    parser.add_argument("--max-order", type=int, default=26)
    parser.add_argument("--max-core", type=int, default=12)
    args = parser.parse_args()
    if not 4 <= args.min_order <= args.max_order or not 3 <= args.max_core < args.max_order:
        parser.error("order range or core bound is invalid")
    scan(args.min_order, args.max_order, args.max_core)


if __name__ == "__main__":
    main()
