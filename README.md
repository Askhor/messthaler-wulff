---
title: The Meßthaler-Wulff Project
author: Julia Meßthaler
---

Blazingly fast code for finding all crystals
(subsets of a graph) that can be constructed
using only transformations that locally minimize
surface energy.

## The Problem

Let $(G, E)$ be some graph and $N{}: G → \wp(G)$ denote the neighbors
of a given node, defined as
$$
  N{}(n) := \{ n_0 \in G \mid \{n_0, n\} \in E \}
$$

Now we can define a crystal as $c \subset G$ with $c$ finite.
This allows us to define the set of all crystals
$C := \{ c \subset G \mid c \text{ finite} \}$.

Now we can define the surface energy of the crystal $c$
(or arbitrary subsets of $G$) as
$$
  E_c := \sum_{n \in c} f_{G \setminus c}(n)
$$
where $f_M(n)$ denotes the "friendliness" of the node $n$ or 
how many friends it has defined as
$$
  f_M(n) := \# \{ n_0 \in N{}(n) \mid n_0 \in M \}
$$

The idea now is to find crystals $c$ such that $\frac{E_{c}}{\#c}$
is optimal.

    Note:
$$
    E_c = \sum_{n} χ_c(n) · (\#N{}(n) - f_c(n))
$$

$$
    = \sum_n χ_c(n) · \#N{}(n) - \sum_{a,b \in N{}(a)} χ_c(a) · χ_c(b)
$$

$$
    N{}' := (\#N{}(n_i))_{1 ≤ i ≤ B}
$$

$$
    E_c = (N{}'^\top · χ_c) - (χ_c^\top · A_G · χ_c)
$$

## The Crystal Graph

We can impose a graph structure on $C$ with the edges
$$
  T := \{ \{ c, c \setminus \{n\} \} \mid c \in C \text{ and } n \in c \}
$$
we call these the transformations and $(C,T)$ the transformation graph.

If we want to discover optimal crystals, then we must efficiently walk this
graph. Since this graph is very dense and very large, we must first
discuss some optimizations:

- [$O(1)$ transformations](#efficient-transformations)

## Efficient Transformations

In the code this is achieved using the stateful class `AdditiveSimulation` that walks
along the transformation graph. This class keeps track of two
important properties, namely $f_c(n)$ and $χ_c(n)$ for (almost) all
$n \in G$, we do not need to store the (possibly) infinite number of values, as
we can let $f_c(n)$ default to $0$ and $χ_c(n)$ to $0$.
$χ_c(n) \in \{0,1\}$ is the characteristic function of the set $c$
and is equal to $1$ exactly iff the node is in $c$.

To the characteristic function we can associate a sign using
$s: \{0,1\} → \{-1, 1\}$, defined as $s(x) = 2x - 1$.

Now let us take a look at what happens, if we walk along an edge $t \in T$.
Let $n$ be the single node that is affected by this transformation.

Let $φ$ be any specific integer quantity we are tracking, then let
$Δφ := φ' - φ$ be the difference between the old and the new value
of the quantity.

$χ_c$ is updated using $Δχ_c(n) = -s∘χ_c(n)$.

The friendliness $f_c(n)$ does not change. Instead, the friendliness of
each neighbor must be updated. So for each $n_0 \in N{}(n)$:
$Δ f_c(n_0) = -s∘χ_c(n)$.

For updating the Energy $E_c$ will first require some work. We already know
the update rule for neighbors $n_0$ of $n$. For nodes $n_0$ that are not $n$
or neighbors of $n$ the differential is $Δ f_c(n_0) = 0$, in essence this is
also not problematic.

However for $n$ the differential is more involved, as the transition makes
the node become part of or be excluded from the sum that defines $E_c$.
So its contribution is
$$
    -s∘χ_c(n) · f_{G \setminus c}(n) = -s∘χ_c(n) · [\#N{}(n) - f_c(n)]
$$

Now for the calculation:
$$
    Δ E_c   = \sum_{n_0 \in c} f_{G \setminus c}(n_0)
$$

$$
            = \left[ \sum_{n_0 \in N{}(n) ∩ c} Δ f_{G \setminus c}(n_0)\right] -s∘χ_c(n) · [\#N{}(n) - f_c(n)]
$$

$$
            = \left[ \sum_{n_0 \in N{}(n) ∩ c} s∘χ_c(n) \right] -s∘χ_c(n) · [\#N{}(n) - f_c(n)]
$$

$$
            = s∘χ_c(n) · f_c(n) -s∘χ_c(n) · [\#N{}(n) - f_c(n)]
$$

$$
            = s∘χ_c(n) · (2f_c(n) - \#N{}(n))
$$

## Min-Calculus

$$
    Q: ℤ^n → ℤ
$$

$$
    r_k: ℤ^{n-k} → ℤ
$$

$$
    \min(Q) = r_n
$$

$$
    r_0 = Q
$$

$$
    r_k = \min(r_{k-1}(0),r_{k-1}(1))
$$

### Solvers

---