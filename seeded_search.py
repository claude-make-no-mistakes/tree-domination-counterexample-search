"""Search the only degrees where weak unimodality can fail on a tree."""

import argparse
import json
import random
from fractions import Fraction
from pathlib import Path

from domination import coefficients, edge_list, rooted_tree, strict_valley


def independence(shape):
    """Return independence optima with the root absent and with it present."""
    children = [independence(child) for child in shape]
    return sum(max(a, b) for a, b in children), 1 + sum(a for a, _ in children)


def candidate_band(shape, counts):
    """Interior of the band left by Beaton and Schoonhoven, Theorems 6 and 16."""
    order = len(counts) - 1
    gamma = next(i for i, count in enumerate(counts) if count)
    upper_gamma = max(independence(shape))
    return (order + 2 * gamma + 1) // 3 + 1, (order + 2 * upper_gamma) // 3 - 1


def curvature(counts, first, last):
    """Largest relative excess of neighbor product over the middle square."""
    best = None
    for k in range(first, last + 1):
        middle = counts[k] ** 2
        neighbors = counts[k - 1] * counts[k + 1]
        excess, scale = neighbors - middle, neighbors + middle
        if best is None or excess * best[1] > best[0] * scale:
            best = excess, scale, k
    return (Fraction(-1), None) if best is None else (Fraction(*best[:2]), best[2])


def prufer_edges(word):
    """Decode the one-indexed Prüfer words printed in the published figures."""
    degrees = [1] * (len(word) + 2)
    for v in word:
        degrees[v - 1] += 1
    for v in word:
        leaf = degrees.index(1)
        yield leaf, v - 1
        degrees[leaf] = 0
        degrees[v - 1] -= 1
    yield tuple(v for v, degree in enumerate(degrees) if degree)


def mutate(order, edges, rng, limit):
    move = rng.randrange(6)
    if move == 0 and order < limit:
        return order + 1, edges + [(rng.randrange(order), order)]
    if move == 1 and order > 20:
        degrees = [0] * order
        for a, b in edges:
            degrees[a] += 1
            degrees[b] += 1
        leaf = rng.choice([v for v, degree in enumerate(degrees) if degree == 1])
        return order - 1, [(a - (a > leaf), b - (b > leaf)) for a, b in edges if leaf not in (a, b)]
    index = rng.randrange(len(edges))
    a, b = edges[index]
    if rng.randrange(2):
        a, b = b, a
    remaining = edges[:index] + edges[index + 1:]
    adjacency = [[] for _ in range(order)]
    for p, q in remaining:
        adjacency[p].append(q)
        adjacency[q].append(p)
    detached = {a}
    frontier = [a]
    for v in frontier:
        for w in adjacency[v]:
            if w not in detached:
                detached.add(w)
                frontier.append(w)
    alternatives = [v for v in range(order) if v not in detached and v != b]
    if not alternatives:
        return order, edges
    return order, remaining + [(a, rng.choice(alternatives))]


def encode_record(name, shape, counts, band, score, center):
    order = len(counts) - 1
    return {"name": name, "order": order, "band": band, "curvature": str(score),
            "center": center, "edge_list": edge_list(shape),
            "triplet": None if center is None else counts[center - 1:center + 2],
            "valley": strict_valley(counts)}


def run(seeds, trials, limit, seed):
    rng = random.Random(seed)
    starts = []
    for entry in seeds:
        order = len(entry["prufer"]) + 2
        edges = list(prufer_edges(entry["prufer"]))
        shape = rooted_tree(order, edges)
        counts = coefficients(shape)
        offset = entry["first_degree"]
        if tuple(entry["first_counts"]) != counts[offset:offset + len(entry["first_counts"])]:
            raise ValueError(f"published figure coefficients disagree for {entry['name']}")
        band = candidate_band(shape, counts)
        score, center = curvature(counts, *band)
        record = encode_record(entry["name"], shape, counts, band, score, center)
        record["log_concavity_failures"] = [k for k in range(1, order)
                                           if counts[k]**2 < counts[k-1] * counts[k+1]]
        print(json.dumps(record), flush=True)
        starts.append((order, edges, score * order))

    if limit < max(s[0] for s in starts):
        raise ValueError("order limit must accommodate every seed")
    seen = set()
    best = None
    positive = 0
    for iteration in range(trials):
        if iteration % 400 == 0:
            order, edges, score = starts[(iteration // 400) % len(starts)]
        size, proposal = mutate(order, edges, rng, limit)
        shape = rooted_tree(size, proposal)
        if shape in seen:
            continue
        seen.add(shape)
        counts = coefficients(shape)
        band = candidate_band(shape, counts)
        candidate, center = curvature(counts, *band)
        valley = strict_valley(counts)
        if valley is not None and candidate <= 0:
            raise RuntimeError("the central-band curvature missed a strict valley")
        positive += candidate > 0
        ranking = candidate * size
        if best is None or (ranking, -size) > best[:2]:
            best = ranking, -size, encode_record("best", shape, counts, band, candidate, center)
        if valley is not None:
            print(json.dumps({"witness": encode_record("witness", shape, counts, band, candidate, center),
                              "coefficients": counts}), flush=True)
            break
        if ranking >= score or rng.randrange(40) == 0:
            order, edges, score = size, proposal, ranking
    print(json.dumps({"trials": trials, "seed": seed, "max_order": limit, "scored": len(seen),
                      "positive_central_curvatures": positive, "best": best[2] if best else None}),
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=40000)
    parser.add_argument("--max-order", type=int, default=110)
    parser.add_argument("--seed", type=int, default=20261127)
    args = parser.parse_args()
    seeds = json.loads(Path(__file__).with_name("published-seeds.json").read_text(encoding="utf-8"))
    run(seeds, args.trials, args.max_order, args.seed)


if __name__ == "__main__":
    main()
