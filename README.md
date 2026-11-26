# Tree domination polynomial unimodality

A tree counterexample must contain two vertices at distance at most two that are neither leaves nor adjacent to leaves. The proof applies to every connected simple graph with at least three vertices under the separation condition. It factors its domination polynomial into log-concave polynomials. The unrestricted tree conjecture remains open. [Paper](paper.pdf) · [Proof in Markdown](SEPARATED-VERTICES.md)

In a minimum-order counterexample, deleting all edges between supports either leaves a single component or leaves components whose domination polynomials all fail log-concavity. A support is a vertex adjacent to a leaf. The exact checks through order 19 then imply that the supports are independent in any minimum-order counterexample of order at most 39. [Support-edge paper](support-edges.pdf) · [Proof in Markdown](SUPPORT-EDGES.md)

## Exact searches

| Scope | Checked | Nonunimodal | Non-log-concave |
| --- | ---: | ---: | ---: |
| Every nonisomorphic tree through order 19 | 522,959 | 0 | 0 |
| Structured branch parameters with at most 600 vertices | 7,158 | 0 | 633 |
| Rooted types encountered during leaf rewiring at order 96 | 15,784 | 0 | 0 |
| Rooted types sampled with exactly two bare vertices at distance one or two and order at most 350 | 5,396 | 0 | 0 |
| Seeded mutations scored in the allowable degree band, order at most 110 | 29,365 | 0 | 0 in the band |
| Unordered pairs of non-log-concave factors, joined order at most 450 | 28,281 | 0 | 25,698 |
| Reduced catalogue, orders 20–27 with at most 12 nonleaf vertices | 8,942,013 | 0 | 0 |

The structured run includes the family in Section 4 of Du, Heilman and Panova and varies branch lengths, multiplicities, and middle degrees. It counts parameter choices, which can produce the same tree. The two sampled runs deduplicate rooted shapes. The catalogue counts unlabeled trees. [Published family](https://arxiv.org/html/2605.02193v1#S4) · [Catalogue](catalogue.jsonl) · [Structured run](structured.jsonl) · [Leaf rewiring](mutations-96.jsonl) · [Close pairs](close-pairs.jsonl)

The seeded search uses the published figures' Prüfer words and reproduces their listed coefficients. The join search uses 318 distinct non-log-concave polynomials. Its chosen representatives had no failures in the degree band where a valley could occur. [Search method](SEARCH-NOTES.md) · [Seeded run](seeded-search.jsonl) · [Join run](join-search.jsonl)

The reduced catalogue uses independent supports and requires a pair of bare vertices at distance at most two. By both reductions, a minimum-order counterexample on at most 27 vertices would therefore have at least 13 nonleaf vertices. The original run was stopped during the 13-nonleaf-vertex slice when the workspace drive filled. The archived slices through 12 were complete. [Reduced catalogue](reduced-catalogue.jsonl)

## Reproduce

Python 3.10 and NetworkX 3.3 were used. The catalogue and verification commands require NetworkX. The other search commands use the standard library.

```sh
python -B search.py catalogue 1 19
python -B search.py structured --max-order 600
python -B search.py mutations 96 --steps 16000 --seed 20261125
python -B search.py close-pairs --trials 6000 --max-order 350 --seed 20261126
python -B verify.py --brute-max 13 --factor-max 18
python -B seeded_search.py --trials 40000 --max-order 110 --seed 20261127
python -B join_search.py --max-factor-order 350 --max-total-order 450
python -B reduced_catalogue.py --min-order 20 --max-order 27 --max-core 12
```

The exact three-state recurrence uses the root selected, the root dominated internally, and the root still requiring its parent. Each polynomial is encoded as a nonnegative integer with base a power of 256 strictly larger than $2^n$, where $n$ is the full tree order. In this base the products and sums representing disjoint selection cases have no coefficient carries. The checker compares the entire coefficient list with direct subset enumeration for all 2,288 trees through order 13, and with the proof's factorization for all 35,663 eligible trees from orders 3 through 18. [Verification output](verification.json)

A fresh GPT-6.2 Sol High referee checked the formulas against Liggett's theorem and independently reproduced the factorization and log-concavity by subset counts for all 1,620 eligible labeled connected graphs on three through six vertices. This model review complements the written proof and executable checks.

A separate GPT-6.2 Sol High referee checked the support-edge proof and compared the reduced enumerator with direct enumeration. The exact sets of 640 eligible trees through order 13 agreed, including every valley test. Direct subset enumeration also reproduced every coefficient on the 54 eligible trees through order 10.

The July X announcement reports a split-graph counterexample. The November manuscript reports split and bipartite counterexamples and leaves the tree case open. [July announcement](https://x.com/28tomabou/status/2080621715307286809) · [November manuscript](https://evidencepress.org/releases/domination-polynomial-unimodality-counterexamples/)
