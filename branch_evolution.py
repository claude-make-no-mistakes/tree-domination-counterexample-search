"""Search repeated-branch mutations for a strict domination-coefficient valley."""

from argparse import ArgumentParser
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
from random import Random

from domination import coefficients, edge_list, rooted_tree, states, strict_valley, tree_order, valley_score
from seeded_search import candidate_band, curvature, prufer_edges


def make_seeds():
    figures = json.loads(Path(__file__).with_name("published-seeds.json").read_text(encoding="utf-8"))
    roots = []
    for entry in figures:
        order = len(entry["prufer"]) + 2
        edges = list(prufer_edges(entry["prufer"]))
        roots.extend(rooted_tree(order, edges, root) for root in range(order))

    paths = [()]
    for _ in range(5):
        paths.append((paths[-1],))
    for path in paths[1:]:
        for multiplicity in (3, 5, 8, 13):
            fan = (path,) * multiplicity
            roots.append((fan,) * 3)
            roots.append(tuple(sorted((fan, fan, path))))
    return tuple(dict.fromkeys(roots))


def subtrees(shape):
    yield shape
    for child in shape:
        yield from subtrees(child)


def edit(shape, pools, max_order, rng):
    parents = []
    here = shape
    while here and rng.random() < 0.55:
        index = rng.randrange(len(here))
        parents.append((here, index))
        here = here[index]
    children = list(here)
    move = rng.randrange(4)
    if move == 0 and children:
        chosen = rng.choice(children)
        children.remove(chosen)
        if rng.randrange(2):
            children = [child for child in children if child != chosen]
    elif move == 1 and children:
        chosen = rng.choice(children)
        amount = rng.choice((1, 2, 3, max(1, children.count(chosen))))
        children.extend([chosen] * amount)
    else:
        chosen = rng.choice(pools)
        children.extend([chosen] * rng.choice((1, 1, 1, 2, 3)))
    here = tuple(sorted(children))
    for parent, index in reversed(parents):
        here = tuple(sorted(parent[:index] + (here,) + parent[index + 1:]))
    return here if 3 <= tree_order(here) <= max_order else None


@dataclass
class Profile:
    shape: tuple
    order: int
    bend: Fraction
    center: int | None
    valley: Fraction
    slopes: tuple[int, int] | None
    band: tuple[int, int]

    def record(self):
        counts = coefficients(self.shape)
        return {
            "order": self.order,
            "band": self.band,
            "curvature": str(self.bend),
            "center": self.center,
            "triplet": None if self.center is None else counts[self.center - 1:self.center + 2],
            "valley_score": str(self.valley),
            "slope_positions": self.slopes,
            "edges": edge_list(self.shape),
        }


def run(trials, initial_seed, max_order):
    rng = Random(initial_seed)
    seeds = tuple(shape for shape in make_seeds() if tree_order(shape) <= max_order)
    pool = list(dict.fromkeys(
        branch for shape in seeds for branch in subtrees(shape) if tree_order(branch) <= max_order // 3
    ))
    if not seeds or not pool:
        raise ValueError("increase the order cap to accommodate starting trees")
    elites, seen = {}, set()
    best_curve = best_valley = None
    positive_curvatures = 0
    all_nonconcave = 0
    witnesses = False
    for i in range(trials):
        if i < len(seeds):
            shape = seeds[i]
        else:
            start = rng.choice(seeds) if not elites or rng.randrange(5) == 0 else rng.choice(tuple(elites.values())).shape
            shape = edit(start, pool, max_order, rng)
        if shape is None or shape in seen:
            continue
        seen.add(shape)
        order = tree_order(shape)
        counts = coefficients(shape)
        valley = strict_valley(counts)
        if valley is not None:
            print(json.dumps({"witness": True, "seed": initial_seed, "order": order,
                              "valley": valley, "edges": edge_list(shape),
                              "coefficients": counts}), flush=True)
            witnesses = True
            break
        band = candidate_band(shape, counts)
        bend, center = curvature(counts, *band)
        score, slopes = valley_score(counts)
        candidate = Profile(shape, order, bend, center, score, slopes, band)
        positive_curvatures += bend > 0
        all_nonconcave += any(b * b < a * c for a, b, c in zip(counts, counts[1:], counts[2:]))
        for objective, value in enumerate((bend, score)):
            bucket = (objective, order // 24, (band[1] - band[0]) // 12)
            previous = elites.get(bucket)
            if previous is None or value * order > ((previous.bend, previous.valley)[objective]
                                                    * previous.order):
                elites[bucket] = candidate
        if best_curve is None or bend * order > best_curve.bend * best_curve.order:
            best_curve = candidate
        if best_valley is None or score * order > best_valley.valley * best_valley.order:
            best_valley = candidate
        if len(seen) % 512 == 0:
            states.cache_clear()
    print(json.dumps({"seed": initial_seed, "trials": i + 1, "max_order": max_order,
                      "scored": len(seen), "non_log_concave": all_nonconcave,
                      "positive_central_curvatures": positive_curvatures, "witness": witnesses,
                      "best_curvature": best_curve.record() if best_curve else None,
                      "closest_valley": best_valley.record() if best_valley else None}), flush=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=20261126)
    parser.add_argument("--max-order", type=int, default=240)
    args = parser.parse_args()
    if args.trials < 1 or args.max_order < 31:
        parser.error("use a positive trial count and an order cap of at least 31")
    run(args.trials, args.seed, args.max_order)
