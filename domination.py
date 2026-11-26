"""Exact domination polynomials of trees and a strict-valley search score."""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import prod


def rooted_tree(order, edges, root=0):
    if order < 1 or not 0 <= root < order or len(edges) != order - 1:
        raise ValueError("expected a nonempty tree with the supplied root")
    adjacency = [[] for _ in range(order)]
    for first, second in edges:
        if not (0 <= first < order and 0 <= second < order and first != second):
            raise ValueError("invalid edge")
        adjacency[first].append(second)
        adjacency[second].append(first)
    vertices = [root]
    visited = {root}
    children = [[] for _ in range(order)]
    for vertex in vertices:
        for neighbor in adjacency[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                vertices.append(neighbor)
                children[vertex].append(neighbor)
    if len(visited) != order:
        raise ValueError("edges are disconnected")
    shapes = [()] * order
    for vertex in reversed(vertices):
        shapes[vertex] = tuple(sorted(shapes[child] for child in children[vertex]))
    return shapes[root]


def edge_list(shape):
    vertices = [shape]
    edges = []
    for parent, children in enumerate(vertices):
        for child in children:
            edges.append((parent, len(vertices)))
            vertices.append(child)
    return edges


@lru_cache(maxsize=4096)
def tree_order(shape):
    return 1 + sum(tree_order(child) * count for child, count in Counter(shape).items())


@lru_cache(maxsize=8192)
def states(shape, bits):
    """Counts with root selected, dominated internally, or awaiting its parent."""
    chosen, dominated, waiting = [], [], []
    for child, count in Counter(shape).items():
        a, b, c = states(child, bits)
        chosen.append((a + b + c) ** count)
        dominated.append((a + b) ** count)
        waiting.append(b ** count)
    c = prod(waiting)
    return prod(chosen) << bits, prod(dominated) - c, c


def coefficients(shape):
    order = tree_order(shape)
    width = (order + 8) // 8
    chosen, dominated, _ = states(shape, width * 8)
    packed = (chosen + dominated).to_bytes(width * (order + 1), "little")
    return tuple(int.from_bytes(packed[i:i + width], "little")
                 for i in range(0, len(packed), width))


def valley_score(counts):
    """Best minimum of a relative adjacent decline and a later relative rise."""
    start = next(i for i, count in enumerate(counts) if count)
    if len(counts) - start < 3:
        return Fraction(-1), None
    decline = None
    best = None
    for k in range(start, len(counts) - 1):
        current, following = counts[k:k + 2]
        numerator, denominator = current - following, current + following
        if decline is not None:
            previous_numerator, previous_denominator, previous_k = decline
            if previous_numerator * denominator <= -numerator * previous_denominator:
                candidate = (previous_numerator, previous_denominator, previous_k, k)
            else:
                candidate = (-numerator, denominator, previous_k, k)
            if best is None or candidate[0] * best[1] > best[0] * candidate[1]:
                best = candidate
        if decline is None or numerator * decline[1] > decline[0] * denominator:
            decline = (numerator, denominator, k)
    return Fraction(best[0], best[1]), best[2:]


def strict_valley(counts):
    """Return three indices forming a strict valley, if one exists."""
    peak = 0
    valley = 0
    for i, count in enumerate(counts):
        if counts[valley] < min(counts[peak], count):
            return peak, valley, i
        if count >= counts[peak]:
            peak = valley = i
        elif count < counts[valley]:
            valley = i
    return None
