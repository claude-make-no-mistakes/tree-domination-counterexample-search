"""Replay the closed domination polynomial identity for the root construction."""

import json

from domination import coefficients, tree_order


def family(leaves, branches, copies):
    star = ((),) * leaves
    hub = (star,) * branches
    return ((),) + (hub,) * copies


def evaluate(counts, x):
    value = 0
    for coefficient in reversed(counts):
        value = value * x + coefficient
    return value


def formula(leaves, branches, copies, x):
    star = x * (1 + x) ** leaves + x ** leaves
    hub = (1 + x) * star ** branches
    waiting = x ** (leaves * branches)
    return x * ((1 + x) * hub ** copies + (hub - waiting) ** copies)


if __name__ == "__main__":
    checks = cases = 0
    for leaves in range(1, 5):
        for branches in range(1, 5):
            for copies in range(1, 7):
                shape = family(leaves, branches, copies)
                counts = coefficients(shape)
                # Degree + 1 distinct integer evaluations determine a polynomial.
                order = tree_order(shape)
                for x in range(-(order // 2), (order + 1) // 2 + 1):
                    if evaluate(counts, x) != formula(leaves, branches, copies, x):
                        raise RuntimeError(f"identity failed at {(leaves, branches, copies, x)}")
                    checks += 1
                cases += 1
    print(json.dumps({"trees": cases, "integer_evaluations": checks}))
