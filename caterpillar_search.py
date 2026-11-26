"""Exact searches for failures of log-concavity or unimodality in caterpillars.

For order at least three, the nonleaf vertices of a caterpillar form its
canonical spine, determined up to reversal. Its end vertices have leaves.
Deleting a spine edge between two vertices with leaves preserves every
dominating set: an unselected vertex with leaves is dominated by its own
selected leaves. The domination polynomial then factors over the components.
Log-concavity is preserved by products of polynomials with nonnegative,
gap-free, log-concave coefficients. Thus the exhaustive scan checks only
spines with no consecutive positive leaf counts, including stars and paths.
"""

import argparse
import json
import random
import struct
from collections.abc import Iterator
from fractions import Fraction
from math import comb

from domination import coefficients, rooted_tree, strict_valley


def packing_width(order: int) -> int:
    """Use a coefficient base strictly greater than 2**order."""
    width = order // 8 + 1
    return next((size for size in (1, 2, 4, 8) if size >= width), width)


def unpack(packed: int, width: int, order: int) -> tuple[int, ...]:
    data = packed.to_bytes(width * (order + 1), "little")
    if width <= 8:
        symbol = {1: "B", 2: "H", 4: "I", 8: "Q"}[width]
        return struct.unpack(f"<{order + 1}{symbol}", data)
    return tuple(int.from_bytes(data[i:i + width], "little")
                 for i in range(0, len(data), width))


def spine_step(
    state: tuple[int, int, int], leaves: int, bits: int, binomial: int
) -> tuple[int, int, int]:
    """Apply the usual three rooted states after extending the spine."""
    chosen, dominated, waiting = state
    extended = (chosen + dominated + waiting) << bits
    if leaves:
        return extended * binomial, (chosen + dominated) << (bits * leaves), 0
    return extended, chosen, dominated


def spine_coefficients(spine: tuple[int, ...]) -> tuple[int, ...]:
    order = len(spine) + sum(spine)
    width = packing_width(order)
    bits = 8 * width
    state = (0, 1, 0)
    for leaves in spine:
        state = spine_step(state, leaves, bits, ((1 << bits) + 1) ** leaves)
    return unpack(state[0] + state[1], width, order)


def spine_edges(spine: tuple[int, ...]) -> list[tuple[int, int]]:
    edges = [(i, i + 1) for i in range(len(spine) - 1)]
    vertex = len(spine)
    for i, leaves in enumerate(spine):
        edges.extend((i, leaf) for leaf in range(vertex, vertex + leaves))
        vertex += leaves
    return edges


def first_log_concavity_failure(counts: tuple[int, ...]) -> int | None:
    return next((i for i in range(1, len(counts) - 1)
                 if counts[i] * counts[i] < counts[i - 1] * counts[i + 1]), None)


def witness(spine: tuple[int, ...], counts: tuple[int, ...], failure: int) -> dict:
    edges = spine_edges(spine)
    order = len(counts) - 1
    for root in (0, order - 1):
        if coefficients(rooted_tree(order, edges, root)) != counts:
            raise RuntimeError(f"general tree recurrence disagrees for spine {spine}")
    return {"order": order, "spine": spine, "edges": edges, "coefficients": counts,
            "log_concavity_failure": failure, "valley": strict_valley(counts)}


def reduced_spines(max_order: int) -> Iterator[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Yield a representative of each reversal class and its coefficient tuple."""
    width = packing_width(max_order)
    bits = 8 * width
    binomials = tuple(((1 << bits) + 1) ** a for a in range(max_order))
    start = (0, 1, 0)
    yield (0,), (0, 1)

    def extend(spine: tuple[int, ...], order: int, state: tuple[int, int, int]):
        if spine <= spine[::-1]:
            yield spine, unpack(state[0] + state[1], width, order)
        for zeros in range(1, max_order - order - 1):
            state = spine_step(state, 0, bits, 1)
            prefix = spine + (0,) * zeros
            for leaves in range(1, max_order - order - zeros):
                next_order = order + zeros + leaves + 1
                next_spine = prefix + (leaves,)
                # A terminal word with the smaller end on the right is redundant.
                # Appending any more requires a bare vertex, a support, and a leaf.
                if leaves < spine[0] and next_order + 3 > max_order:
                    continue
                next_state = spine_step(state, leaves, bits, binomials[leaves])
                yield from extend(next_spine, next_order, next_state)

    for leaves in range(1, max_order):
        yield from extend((leaves,), leaves + 1,
                          spine_step(start, leaves, bits, binomials[leaves]))


def expected_count(order: int) -> int:
    """Count reversal classes by stars and bars and Burnside's lemma."""
    oriented = fixed = 1  # The one-vertex spine, including the orders 1 and 2.
    for supports in range(2, (order + 1) // 3 + 1):
        excess = order - (3 * supports - 1)
        oriented += comb(excess + 2 * supports - 2, 2 * supports - 2)
        # In a palindrome there are supports - 1 equal pairs of parameters
        # and one central parameter that absorbs any residual excess.
        fixed += comb(excess // 2 + supports - 1, supports - 1)
    return (oriented + fixed) // 2


def exhaustive(max_order: int) -> dict:
    checked = [0] * (max_order + 1)
    non_log_concave = nonunimodal = 0
    for spine, counts in reduced_spines(max_order):
        order = len(counts) - 1
        checked[order] += 1
        failure = first_log_concavity_failure(counts)
        if failure is not None:
            record = witness(spine, counts, failure)
            print(json.dumps(record), flush=True)
            non_log_concave += 1
            nonunimodal += record["valley"] is not None
    expected = [0] + [expected_count(n) for n in range(1, max_order + 1)]
    if checked != expected:
        raise RuntimeError(f"enumerated counts {checked} disagree with {expected}")
    return {"max_order": max_order, "checked": sum(checked),
            "by_order": checked[1:], "non_log_concave": non_log_concave,
            "nonunimodal": nonunimodal}


def random_parameters(order: int, rng: random.Random) -> list[int]:
    supports = rng.randint(1, (order + 1) // 3)
    parts = 2 * supports - 1
    total = order - (3 * supports - 1)
    cuts = [0, *sorted(rng.sample(range(1, total + parts), parts - 1)), total + parts]
    return [right - left for left, right in zip(cuts, cuts[1:])]


def mutate(parameters: list[int], rng: random.Random) -> list[int]:
    modified = parameters.copy()
    for _ in range(rng.randint(1, 4)):
        source = rng.randrange(len(modified))
        target = rng.randrange(len(modified))
        moved = rng.randrange(modified[source])
        modified[source] -= moved
        modified[target] += moved
    return modified


def parameters_to_spine(parameters: list[int]) -> tuple[int, ...]:
    spine = [parameters[0]]
    for zeros, leaves in zip(parameters[1::2], parameters[2::2]):
        spine.extend([0] * zeros)
        spine.append(leaves)
    return min(tuple(spine), tuple(reversed(spine)))


def log_concavity_score(counts: tuple[int, ...]) -> Fraction:
    """Return the maximum of a[k-1]*a[k+1]/a[k]**2 on the positive support."""
    numerator, denominator = 0, 1
    for left, center, right in zip(counts, counts[1:], counts[2:]):
        if left and right:
            cross, square = left * right, center * center
            if cross * denominator > numerator * square:
                numerator, denominator = cross, square
    return Fraction(numerator, denominator)


def sample(trials: int, min_order: int, max_order: int, seed: int) -> dict:
    rng = random.Random(seed)
    best = {}
    seen = set()
    non_log_concave = nonunimodal = 0
    for _ in range(trials):
        order = rng.randint(min_order, max_order)
        leader = best.get(order)
        if leader is None or rng.random() < 0.35:
            parameters = random_parameters(order, rng)
        else:
            parameters = mutate(leader[1], rng)
        spine = parameters_to_spine(parameters)
        if spine in seen:
            continue
        seen.add(spine)
        counts = spine_coefficients(spine)
        score = log_concavity_score(counts)
        if leader is None or score > leader[0]:
            best[order] = (score, parameters, spine)
        if score > 1:
            failure = first_log_concavity_failure(counts)
            if failure is None:
                raise RuntimeError(f"score disagrees with failure check for spine {spine}")
            record = witness(spine, counts, failure)
            print(json.dumps(record), flush=True)
            non_log_concave += 1
            nonunimodal += record["valley"] is not None
    nearest = max(best.values(), key=lambda entry: entry[0])
    return {"seed": seed, "trials": trials, "checked": len(seen), "min_order": min_order,
            "max_order": max_order, "non_log_concave": non_log_concave,
            "nonunimodal": nonunimodal, "highest_ratio": str(nearest[0]),
            "highest_ratio_spine": nearest[2]}


def verify(max_order: int) -> dict:
    from verify import direct_counts

    checked = set()
    for spine, counts in reduced_spines(max_order):
        edges = spine_edges(spine)
        order = len(counts) - 1
        # Existing verifier counts subsets by their closed neighborhoods.
        if counts != direct_counts(order, edges):
            raise RuntimeError(f"direct subset count disagrees for spine {spine}")
        if counts != spine_coefficients(spine):
            raise RuntimeError(f"single-spine computation disagrees for spine {spine}")
        if spine in checked:
            raise RuntimeError(f"spine enumerated twice: {spine}")
        checked.add(spine)
    expected = sum(expected_count(n) for n in range(1, max_order + 1))
    if len(checked) != expected:
        raise RuntimeError(f"enumerated {len(checked)} distinct spines, expected {expected}")
    return {"brute_force_max_order": max_order, "brute_force_checked": len(checked)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    exact = modes.add_parser("exhaustive")
    exact.add_argument("--max-order", type=int, default=25)
    heuristic = modes.add_parser("sample")
    heuristic.add_argument("--min-order", type=int, default=32)
    heuristic.add_argument("--max-order", type=int, default=200)
    heuristic.add_argument("--trials", type=int, default=10000)
    heuristic.add_argument("--seed", type=int, default=20261126)
    verification = modes.add_parser("verify")
    verification.add_argument("--max-order", type=int, default=13)
    args = parser.parse_args()
    if args.mode in ("exhaustive", "verify"):
        if args.max_order < 1:
            parser.error("maximum order must be positive")
        scan = exhaustive if args.mode == "exhaustive" else verify
        result = scan(args.max_order)
    else:
        if not 2 <= args.min_order <= args.max_order or args.trials < 1:
            parser.error("sampling requires orders at least two and a positive trial count")
        result = sample(args.trials, args.min_order, args.max_order, args.seed)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
