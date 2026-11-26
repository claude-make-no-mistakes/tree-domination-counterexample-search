# Tree domination polynomial unimodality

A tree counterexample must have at least three bare vertices in one component of the graph that joins bare vertices at tree distance at most two. A bare vertex is neither a leaf nor adjacent to a leaf. The proof factors the domination polynomial and establishes log-concavity for both kinds of two-vertex component. The same paper shows that domination roots of trees of diameter six are dense in the complex plane, and that trees of diameter at most five omit an open region. The unrestricted tree unimodality conjecture remains open. [Paper](bare-pairs-and-zeros.pdf) · [Exact pair checks](pair-components-check.json)

The earlier separation theorem also applies to connected simple graphs of order at least three when all pairs of bare vertices are at distance at least three. [Separation paper](paper.pdf) · [Proof](SEPARATED-VERTICES.md)

In a minimum-order counterexample, deleting all edges between supports either leaves a single component or leaves components whose domination polynomials all fail log-concavity. A support is a vertex adjacent to a leaf. The exact checks through order 26 imply that the supports are independent in any minimum-order counterexample of order at most 53. [Support-edge paper](support-edges.pdf) · [Proof in Markdown](SUPPORT-EDGES.md)

## Exact searches

| Scope | Checked | Nonunimodal | Non-log-concave |
| --- | ---: | ---: | ---: |
| Every nonisomorphic tree through order 25 | 167,879,146 | 0 | 0 |
| Order-26 trees with independent supports and a bare component of size at least three | 26,126,173 | 0 | 0 |
| Independent-support caterpillars through order 32 | 10,171,872 | 0 | 0 |
| Repeated-branch mutations with order cap 420 | 11,809 rooted shapes | 0 | 1,460 |
| Structured branch parameters with at most 600 vertices | 7,158 | 0 | 633 |
| Rooted types encountered during leaf rewiring at order 96 | 15,784 | 0 | 0 |
| Rooted types sampled with exactly two bare vertices at distance one or two and order at most 350 | 5,396 | 0 | 0 |
| Seeded mutations scored in the allowable degree band, order at most 110 | 29,365 | 0 | 0 in the band |
| Unordered pairs of non-log-concave factors, joined order at most 450 | 28,281 | 0 | 25,698 |
| Reduced catalogue, orders 20–27 with at most 12 nonleaf vertices | 8,942,013 | 0 | 0 |

The structured run includes the family in Section 4 of Du, Heilman and Panova and varies branch lengths, multiplicities, and middle degrees. It counts parameter choices, which can produce the same tree. The two sampled runs deduplicate rooted shapes. The catalogue counts unlabeled trees. [Published family](https://arxiv.org/html/2605.02193v1#S4) · [Catalogue](catalogue.jsonl) · [Structured run](structured.jsonl) · [Leaf rewiring](mutations-96.jsonl) · [Close pairs](close-pairs.jsonl)

The seeded search uses the published figures' Prüfer words and reproduces their listed coefficients. The join search uses 318 distinct non-log-concave polynomials. Its chosen representatives had no failures in the degree band where a valley could occur. [Search method](SEARCH-NOTES.md) · [Seeded run](seeded-search.jsonl) · [Join run](join-search.jsonl)

The reduced catalogue uses independent supports and requires a pair of bare vertices at distance at most two. By both reductions, a minimum-order counterexample on at most 27 vertices would therefore have at least 13 nonleaf vertices. The original run was stopped during the 13-nonleaf-vertex slice when the workspace drive filled. The archived slices through 12 were complete. [Reduced catalogue](reduced-catalogue.jsonl)

Deleting edges between supports factors a caterpillar into smaller caterpillars. Thus the independent-support scan covers all **536,920,064 caterpillar isomorphism classes through order 32** by convolution of log-concave sequences. The seeded searches checked 11,308 reduced spines with an order cap of 200 and 4,876 with a cap of 700. Neither found a valley or a violation of log-concavity. [Exhaustive caterpillar log](caterpillar-exhaustive.jsonl) · [Sample log](caterpillar-sampled.jsonl) · [Repeated-branch search](branch-evolution.jsonl)

The native scan evaluates exact coefficient arrays on the free trees from nauty's `gentreeg`. Every coefficient and intermediate product is bounded by the number of subsets of the current subtree. Aggregate counts and coefficient sums matched a separate Python enumeration through order 16. [Orders 20–25](exact-catalogue.jsonl) · [Controls](exact-scan-controls.jsonl)

The filtered scan visits all 279,793,450 order-26 trees and evaluates the 26,126,173 retained cases. When a tree has a support–support edge, deleting it gives smaller trees with log-concave polynomials by the order-25 result. Their product is log-concave. The paired-bare-vertex theorem handles all other filtered-out cases. Thus **every tree through order 26** has log-concave domination coefficients. [Order-26 ledger](exact-filtered.jsonl)

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
python -B check_pair_components.py
python -B check_root_family.py
python -B caterpillar_search.py verify --max-order 13
python -B caterpillar_search.py exhaustive --max-order 32
python -B caterpillar_search.py sample --min-order 32 --max-order 200 --trials 18000 --seed 20261126
python -B caterpillar_search.py sample --min-order 33 --max-order 700 --trials 6000 --seed 20261127
python -B branch_evolution.py --trials 16000 --max-order 420 --seed 20261221
```

For the native scan, set `NAUTY` to a configured nauty 2.9.3 source directory. The following GCC command uses a POSIX shell.

```sh
summary='-DSUMMARY(total,seconds)=do { extern void domination_summary(nauty_counter,double); domination_summary(total,seconds); } while (0)'
cc -O3 -DOUTPROC=domination_scan "$summary" -I "$NAUTY" \
  "$NAUTY/gentreeg.c" "$NAUTY/gtools.c" "$NAUTY/nauty.c" "$NAUTY/nautil.c" \
  "$NAUTY/naugraph.c" "$NAUTY/schreier.c" "$NAUTY/naurng.c" exact_scan.c -o exact_scan
python -B check_exact_scan.py ./exact_scan --max-order 16
for n in 20 21 22 23 24 25; do ./exact_scan -q "$n"; done
```

Add `-DSTRUCTURAL_FILTER` to the same build for the filtered scan. Run `python -B check_exact_scan.py ./exact_scan --filtered --max-order 16` against that binary before using `./exact_scan -q 26`. The resulting coefficient sums include only the retained trees.

The exact three-state recurrence uses the root selected, the root dominated internally, and the root still requiring its parent. Each polynomial is encoded as a nonnegative integer with base a power of 256 strictly larger than $2^n$, where $n$ is the full tree order. In this base the products and sums representing disjoint selection cases have no coefficient carries. The checker compares the entire coefficient list with direct subset enumeration for all 2,288 trees through order 13, and with the proof's factorization for all 35,663 eligible trees from orders 3 through 18. [Verification output](verification.json)

A fresh GPT-6.2 Sol High referee checked the formulas against Liggett's theorem and independently reproduced the factorization and log-concavity by subset counts for all 1,620 eligible labeled connected graphs on three through six vertices. This model review complements the written proof and executable checks.

A separate GPT-6.2 Sol High referee checked the support-edge proof and compared the reduced enumerator with direct enumeration. The exact sets of 640 eligible trees through order 13 agreed, including every valley test. Direct subset enumeration also reproduced every coefficient on the 54 eligible trees through order 10.

The new proof replay checks all 265 small pair profiles against the full rooted-state evaluator. The root identity agrees at enough distinct integer arguments to determine every coefficient for 96 trees in the family. A fresh GPT-6.2 Sol High review checked both arguments and the finite reduction.

The July X announcement reports a split-graph counterexample. The November manuscript reports split and bipartite counterexamples and leaves the tree case open. [July announcement](https://x.com/28tomabou/status/2080621715307286809) · [November manuscript](https://evidencepress.org/releases/domination-polynomial-unimodality-counterexamples/)
