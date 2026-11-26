# Log-concavity when vertices without leaf neighbors are separated

Let $G$ be a finite connected simple graph on at least three vertices. Call a vertex a leaf if it has degree one, a support if it has a leaf neighbor, and a bare vertex if it is neither a leaf nor a support. If every two bare vertices have distance at least three, then the domination polynomial of $G$ is log-concave. Its coefficients are consequently unimodal. In particular, any counterexample on a tree must contain two bare vertices at distance one or two.

## Factorization

Each leaf has a unique support, and the leaves and supports are disjoint. If a support $v$ has $t_v$ leaves, the weight of local choices containing $v$ is $x(1+x)^{t_v}$. When $v$ is absent, all its leaves must be selected. Their weight is $x^{t_v}$, and they dominate $v$. Thus the combined factor at a support is

$$f_t(x)=x(1+x)^t+x^t=xh_t(x),\qquad h_t(x)=(1+x)^t+x^{t-1}.$$

Extra edges among supports do not affect these choices. A bare vertex $u$ has only supports as neighbors. The support neighborhoods of distinct bare vertices are disjoint, since a common support would give distance two. For $b$ neighboring supports with leaf counts $t_1,\ldots,t_b$ and $S=\sum_i t_i$, the weight at $u$ and those support groups is

$$F(x)=(1+x)\prod_{i=1}^b f_{t_i}(x)-x^S.$$

The single forbidden contribution comes from leaving $u$ and every neighboring support unselected. Each such support then contributes all its leaves. This gives the complete domination polynomial as a product of the $F$ factors and the factors $f_t$ at unused supports.

## Log-concavity of the factors

Use ultra-log-concavity of order $N$, meaning that $a_j/\binom Nj$ is log-concave and the coefficients have contiguous support. Pad the sequence through degree $N$ with zeros. Liggett's convolution theorem adds the orders when multiplying generating polynomials. Ordinary log-concavity with contiguous support is also closed under convolution. [Liggett, Theorem 2](https://doi.org/10.1006/jcta.1997.2790) · [Gurvits's proof](https://www.kurims.kyoto-u.ac.jp/EMIS/journals/EJC/Volume_16/PDF/v16i1n5.pdf)

The polynomial $h_t$ is ultra-log-concave of order $3t$. The coefficients of $(1+x)^t$ divided by $\binom{3t}{j}$ have successive ratios $(t-j)/(3t-j)$ for $0\le j<t$. Adding one at $j=t-1$ improves the inequality centered there. For $t\ge3$ the only other affected interior inequality is at $j=t-2$. Its left-to-right ratio before normalization is

$$\frac{a_{t-2}^2}{a_{t-3}a_{t-1}}=\frac{t-1}{t-2}\frac{3t}{2(t+1)},$$

where $a_j=[x^j]h_t$. The binomial ratio required for order $3t$ is

$$\frac{\binom{3t}{t-2}^2}{\binom{3t}{t-3}\binom{3t}{t-1}}=\frac{t-1}{t-2}\frac{2t+3}{2t+2}.$$

The comparison is $3t\ge2t+3$. For $t=1$ the support has two coefficients, and for $t=2$ the only interior inequality improves. This proves the assertion for all $t\ge1$, so the factor $f_t$ is log-concave.

For a factor $F$ write $F=x^b(P-x^d)$, where $P=(1+x)\prod_i h_{t_i}$ and $d=S-b$. The coefficient sequence of $P$ is ultra-log-concave of order $1+3S$. Write it as $(p_j)$. Subtracting $x^d$ only makes the ordinary log-concavity test harder at $j=d$, since the coefficient decreases by one. For $d=0$ this is a boundary term and $p_0=2^b$. For $d\ge1$ the normalized inequalities imply

$$p_{d-1}p_{d+1}\le \frac{d}{d+1}p_d^2.$$

Here $p_d\ge\binom{S+1}{d}$ by retaining only the binomial summands in the $h_{t_i}$. A bare vertex has degree $b\ge2$, so $S+1=d+b+1\ge d+3$. Consequently $p_d\ge\binom{d+3}{d}\ge2(d+1)$. It follows that

$$ (p_d-1)^2-p_{d-1}p_{d+1}\ge \frac{p_d^2}{d+1}-2p_d+1\ge 1.$$

All factors have contiguous support and the product is therefore log-concave. The one- and two-vertex trees have polynomials $x$ and $2x+x^2$, respectively, and satisfy the same conclusion.
