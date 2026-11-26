"""Search small catalogues, structured families, and leaf-move neighborhoods."""

import argparse
import json
import random

from domination import coefficients, edge_list, rooted_tree, strict_valley, tree_order, valley_score


def structured(order_limit):
    leaf = ()
    whisker = (leaf,)
    paths = [leaf]
    for _ in range(11):
        paths.append((paths[-1],))
    # Section 4 of arXiv:2605.02193 uses (length, middle degree, hairs) = (3, 3, 0).
    for path in range(1, 7):
        for middle in range(1, 7):
            for fan in range(1, 33):
                branch = ((paths[path - 1],) * fan,) * middle
                for copies in range(1, 13):
                    shape = (whisker,) + (branch,) * copies
                    if tree_order(shape) > order_limit:
                        break
                    yield shape
    for path in range(1, 13):
        for copies in range(2, min(order_limit // path, 100)):
            yield (paths[path - 1],) * copies


def catalogue(first, last):
    from networkx import nonisomorphic_trees
    for order in range(first, last + 1):
        if order == 1:
            yield order, [()]
        else:
            trees = nonisomorphic_trees(order)
            yield order, (rooted_tree(order, list(t.edges), max(t, key=t.degree)) for t in trees)


def mutations(steps, seed, order):
    rng = random.Random(seed)
    edges = []
    score = None
    seen = set()
    for step in range(steps):
        if step % 400 == 0 or not edges:
            scale = 1 + rng.randrange(5)
            edges = [(vertex, max(rng.randrange(vertex) for _ in range(scale)))
                     for vertex in range(1, order)]
            score = None
        if score is None:
            proposal = edges
        else:
            degrees = [0] * order
            for first, second in edges:
                degrees[first] += 1
                degrees[second] += 1
            leaf = rng.choice([v for v in range(order) if degrees[v] == 1])
            old_edge = next(edge for edge in edges if leaf in edge)
            neighbor = old_edge[0] if old_edge[1] == leaf else old_edge[1]
            new_neighbor = rng.choice([v for v in range(order) if v not in (leaf, neighbor)])
            proposal = edges.copy()
            proposal[proposal.index(old_edge)] = leaf, new_neighbor
        shape = rooted_tree(order, proposal, order // 3)
        if shape in seen:
            continue
        seen.add(shape)
        counts = coefficients(shape)
        candidate, _ = valley_score(counts)
        if score is None or candidate >= score or rng.randrange(64) == 0:
            edges, score = proposal, candidate
        yield shape, counts


def close_pairs(trials, seed, order_limit):
    rng = random.Random(seed)
    seen = set()
    for _ in range(trials):
        maximum_leaves = rng.choice((2, 4, 8, 16, 32, 64))
        groups = [[rng.randint(1, maximum_leaves) for _ in range(rng.randint(1, 8))]
                  for _ in range(2)]
        distance = rng.randint(1, 2)
        edges = [(v, v + 1) for v in range(distance)]
        next_vertex = distance + 1
        for end, counts in zip((0, distance), groups):
            for count in counts:
                support = next_vertex
                edges.append((end, support))
                edges.extend((support, leaf) for leaf in range(support + 1, support + 1 + count))
                next_vertex += count + 1
        if distance == 2:
            count = rng.randint(1, maximum_leaves)
            edges.extend((1, leaf) for leaf in range(next_vertex, next_vertex + count))
            next_vertex += count
        if next_vertex > order_limit:
            continue
        shape = rooted_tree(next_vertex, edges)
        if shape not in seen:
            seen.add(shape)
            yield shape, coefficients(shape)


def scan(shapes, label, **metadata):
    best = None
    total = 0
    failures = 0
    for total, (shape, counts) in enumerate(shapes, start=1):
        order = len(counts) - 1
        actual_valley = strict_valley(counts)
        score, positions = valley_score(counts)
        if (score > 0) != (actual_valley is not None):
            raise RuntimeError("the two unimodality checks disagree")
        failures += any(b * b < a * c for a, b, c in zip(counts, counts[1:], counts[2:]))
        normalized_score = score * order
        if best is None or normalized_score > best[0]:
            best = normalized_score, order, score, positions, shape
        if actual_valley is not None:
            print(json.dumps({"family": label, **metadata, "tested": total, "order": order,
                              "edges": edge_list(shape), "valley": actual_valley,
                              "coefficients": counts}), flush=True)
            return True
    closest = None
    if best is not None:
        normalized_score, order, score, positions, shape = best
        closest = {"order": order, "score": str(score), "normalized_score": float(normalized_score),
                   "positions": positions, "edges": edge_list(shape)}
    print(json.dumps({"family": label, **metadata, "tested": total, "witness": None,
                      "log_concavity_failures": failures, "closest": closest}), flush=True)
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    exact = modes.add_parser("catalogue")
    exact.add_argument("first", type=int)
    exact.add_argument("last", type=int)
    family = modes.add_parser("structured")
    family.add_argument("--max-order", type=int, default=125)
    mutation = modes.add_parser("mutations")
    mutation.add_argument("order", type=int)
    mutation.add_argument("--steps", type=int, default=5000)
    mutation.add_argument("--seed", type=int, default=20261125)
    pairs = modes.add_parser("close-pairs")
    pairs.add_argument("--trials", type=int, default=3000)
    pairs.add_argument("--max-order", type=int, default=350)
    pairs.add_argument("--seed", type=int, default=20261126)
    args = parser.parse_args()
    if args.mode == "catalogue":
        if not 1 <= args.first <= args.last:
            parser.error("use 1 <= first <= last")
        for order, shapes in catalogue(args.first, args.last):
            if scan(((shape, coefficients(shape)) for shape in shapes), "catalogue", order=order):
                break
    elif args.mode == "structured":
        scan(((shape, coefficients(shape)) for shape in structured(args.max_order)),
             "structured", max_order=args.max_order)
    elif args.mode == "mutations":
        if args.order < 3:
            parser.error("leaf mutations require order at least three")
        scan(mutations(args.steps, args.seed, args.order), "mutations",
             order=args.order, steps=args.steps, seed=args.seed)
    else:
        scan(close_pairs(args.trials, args.seed, args.max_order), "close-pairs",
             trials=args.trials, seed=args.seed, max_order=args.max_order)


if __name__ == "__main__":
    main()
