# Deleting edges between supports in a smallest counterexample

In a tree, a support is a vertex adjacent to a leaf. A bare vertex is neither a leaf nor a support. In a tree with at least three vertices, the supports and leaves are disjoint.

**Reduction.** Delete every edge joining two supports from a smallest tree whose domination polynomial is nonunimodal. If this gives at least two components, each component has a non-log-concave domination polynomial. In particular, each component contains at least two bare vertices at distance at most two. The exact catalogue through order 19 also implies that any smallest counterexample of order at most 39 has no edge joining two supports.

## Factorization at support edges

If a support is selected, it dominates itself. If it is omitted, every leaf adjacent to it must be selected and hence dominates it. Thus an edge between two supports has no effect on domination. All original leaves remain adjacent to their supports when the support–support edges are deleted. Conversely, adding an edge between supports of two disjoint trees of order at least three has no effect on which sets dominate the union. It makes the union a tree.

Let $T_1,\ldots,T_r$ be the components after the deletions. Each component contains an original support. Otherwise it would consist of bare vertices, all of which keep their original degree of at least two, which is impossible in a finite tree. A component may consist of an original support and its only leaf. In that case keep track of the original support endpoint.

The domination polynomial of the original tree is $\prod_i D_{T_i}(x)$. Given any nonempty subcollection, join successive components at original supports to obtain a tree whose domination polynomial is the product over that subcollection. In a two-vertex component the chosen endpoint stays the original support and its original leaf stays a leaf. Any support–support edge added between distinct components only joins vertices whose domination is already ensured by their local leaf choices.

## Why each factor must fail log-concavity

A nonnegative finite log-concave sequence with contiguous support preserves unimodality under convolution. To see this, write $h=b*a$ with $b$ unimodal, extend both sequences by zero, and set $s_i=b_i-b_{i-1}$. The positive indices of $s$ precede its negative indices. Write $h_k-h_{k-1}=P_k-N_k$ with

$$P_k=\sum_{i:s_i>0}s_i a_{k-i},\qquad N_k=\sum_{j:s_j<0}(-s_j)a_{k-j}.$$

For $k<l$ and $i<j$, log-concavity gives $a_{l-i}a_{k-j}\leq a_{k-i}a_{l-j}$. If the left product is positive, the two indices on the right lie between the two on the left, and the sums of the indices agree. Otherwise the inequality follows from nonnegativity. Summing gives $P_lN_k\leq P_kN_l$. Thus $P_k<N_k$ cannot be followed by $P_l>N_l$. This proves the closure statement.

Suppose some $D_{T_i}$ is log-concave. Domination polynomials have contiguous positive support between their minimum degree and their degree, since supersets of a dominating set still dominate. Remove the $i$th component and join the remaining components through their original supports. The resulting tree has smaller order and hence has a unimodal domination polynomial by minimality. Convolution with $D_{T_i}$ would make the original tree unimodal, a contradiction. Each factor is therefore non-log-concave. Each factor on two vertices has polynomial $2x+x^2$, so it cannot occur. In every other component each original support remains a support and no original bare vertex changes degree or obtains a leaf neighbor. The separation theorem then gives the claimed close pair in every component. [Separation theorem](SEPARATED-VERTICES.md)

The exhaustive [catalogue through order 19](catalogue.jsonl) finds every such polynomial log-concave. If $r\geq2$, the last argument gives $|T_i|\geq20$ for every $i$, hence $|T|\geq40$. This order bound uses the finite enumeration. The factor restriction holds at all orders.
