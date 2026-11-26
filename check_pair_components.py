"""Exact coefficient checks for the finite part of the paired-bare proof."""

from collections import defaultdict
from math import comb
import json

from domination import coefficients, rooted_tree


def partitions(total, low=1):
    if total == 0:
        yield ()
    for first in range(low, total + 1):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def multiply(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            out[i + j] += left * right
    return out


def h(t):
    out = [comb(t, j) for j in range(t + 1)]
    out[t - 1] += 1
    return out


def product(parts):
    value = [1]
    for t in parts:
        value = multiply(value, h(t))
    return value


def remove(poly, at, amount):
    for i, count in enumerate(amount, start=at):
        poly[i] -= count


def local_polynomial(left, right, shared):
    a, b = product(left), product(right)
    alpha, beta = sum(left) - len(left), sum(right) - len(right)
    if shared is None:
        result = multiply(multiply(a, b), [1, 2, 1])
        remove(result, alpha, b)
        remove(result, beta, a)
        result[alpha + beta] += 1
        return result
    delta = shared - 1
    result = multiply(multiply(multiply(a, b), h(shared)), [1, 2, 1])
    remove(result, alpha + delta, multiply(b, [1, 1]))
    remove(result, beta + delta, multiply(a, [1, 1]))
    result[alpha + beta + delta] += 1
    return result


def pair_tree(left, right, shared):
    edges = []
    order = 2

    def grow_support(endpoint, leaves, other=None):
        nonlocal order
        center = order
        order += 1
        edges.append((endpoint, center))
        if other is not None:
            edges.append((other, center))
        for _ in range(leaves):
            edges.append((center, order))
            order += 1

    if shared is None:
        edges.append((0, 1))
    else:
        grow_support(0, shared, 1)
    for bare, parts in enumerate((left, right)):
        for count in parts:
            grow_support(bare, count)
    return order, edges


def profiles(limit):
    for total in range(1, limit + 1):
        for shared in range(total):
            private = total - shared
            for left_size in range(1, private + 1):
                for left in partitions(left_size):
                    for right in partitions(private):
                        if left_size < private or left <= right:
                            yield total, left, right, shared or None


def check(limit=5):
    results = defaultdict(lambda: {"profiles": 0, "minimum_margin": None})
    for total, left, right, shared in profiles(limit):
        base = local_polynomial(left, right, shared)
        order, edges = pair_tree(left, right, shared)
        offset = len(left) + len(right) + (shared is not None)
        expected = (0,) * offset + tuple(base)
        if expected != coefficients(rooted_tree(order, edges)):
            raise RuntimeError(f"coefficient mismatch in {(left, right, shared)}")
        margin = min(y * y - x * z for x, y, z in zip(base, base[1:], base[2:]))
        if margin < 0 or min(base) < 1:
            raise RuntimeError(f"log-concavity or support failed in {(left, right, shared)}")
        row = results[2 if shared else 1, total]
        row["profiles"] += 1
        smallest = row["minimum_margin"]
        row["minimum_margin"] = margin if smallest is None else min(margin, smallest)
    return [{"distance": distance, "larger_leaf_total": total, **row}
            for (distance, total), row in sorted(results.items())]


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
