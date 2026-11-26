# Tree domination polynomial unimodality

A tree counterexample must contain two vertices at distance at most two that are neither leaves nor adjacent to leaves. The proof applies to every connected simple graph with at least three vertices under the separation condition. It factors its domination polynomial into log-concave polynomials. The unrestricted tree conjecture remains open. [Paper](paper.pdf) · [Proof in Markdown](SEPARATED-VERTICES.md)

## Exact searches

| Scope | Checked | Nonunimodal | Non-log-concave |
| --- | ---: | ---: | ---: |
| Every nonisomorphic tree through order 19 | 522,959 | 0 | 0 |
| Structured branch parameters with at most 600 vertices | 7,158 | 0 | 633 |
| Rooted types encountered during leaf rewiring at order 96 | 15,784 | 0 | 0 |
| Rooted types sampled with exactly two bare vertices at distance one or two and order at most 350 | 5,396 | 0 | 0 |

The structured run includes the family in Section 4 of Du, Heilman and Panova and varies branch lengths, multiplicities, and middle degrees. It counts parameter choices, which can produce the same tree. The two sampled runs deduplicate rooted shapes. The catalogue counts unlabeled trees. [Published family](https://arxiv.org/html/2605.02193v1#S4) · [Catalogue](catalogue.jsonl) · [Structured run](structured.jsonl) · [Leaf rewiring](mutations-96.jsonl) · [Close pairs](close-pairs.jsonl)

## Reproduce

Python 3.10 and NetworkX 3.3 were used. The catalogue and verification commands require NetworkX. The other search commands use the standard library.

```sh
python -B search.py catalogue 1 19
python -B search.py structured --max-order 600
python -B search.py mutations 96 --steps 16000 --seed 20261125
python -B search.py close-pairs --trials 6000 --max-order 350 --seed 20261126
python -B verify.py --brute-max 13 --factor-max 18
```

The exact three-state recurrence uses the root selected, the root dominated internally, and the root still requiring its parent. Each polynomial is encoded as a nonnegative integer with base a power of 256 strictly larger than $2^n$, where $n$ is the full tree order. In this base the products and sums representing disjoint selection cases have no coefficient carries. The checker compares the entire coefficient list with direct subset enumeration for all 2,288 trees through order 13, and with the proof's factorization for all 35,663 eligible trees from orders 3 through 18. [Verification output](verification.json)

A fresh GPT-6.2 Sol High referee checked the formulas against Liggett's theorem and independently reproduced the factorization and log-concavity by subset counts for all 1,620 eligible labeled connected graphs on three through six vertices. This model review complements the written proof and executable checks.

The July X announcement reports a split-graph counterexample. The November manuscript reports split and bipartite counterexamples and leaves the tree case open. [July announcement](https://x.com/28tomabou/status/2080621715307286809) · [November manuscript](https://evidencepress.org/releases/domination-polynomial-unimodality-counterexamples/)
