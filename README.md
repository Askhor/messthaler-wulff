# The Messthaler-Wulff Project

Blazingly fast code for finding all crystals
(subsets of a graph) that can be constructed
using only transformations that locally minimize
surface energy.

## The Problem

Let $G$ be some graph and $C \subset G$ a crystal.
Furthermore let $\eta: G \rightarrow \wp(G)$ denote the neighbors
of a given node.
Then we can define the surface energy of the crystal $C$
as
$$
    \xi_C \coloneq \sum_{n \in C} l_n 
$$
where $l_n$ denotes the loneliness of the node $n$ and is
itself defined as
$$
    l_n \coloneq \# \{ n_0 \in \eta(n) \mid n_0 \not\in C \}
$$

The idea now is to find optimal $\xi_C$ by doing locally
minimizing transformations. We call a node $n$ optimal
in forwards mode if for the specific $C$ there is no node
$n_0$ such that $l_{n_0} < l_n$. The same definition can
be applied to backwards mode, for this however we use
$\bar l_n \coloneq \#\{ n_0 \in \eta(n) \mid n_0 \in C \}$.

A locally optimal addition is now simply a node with optimal $l_n$
and a locally optimal removal is a node with optimal $\bar l_n$.

Our goal in this project is to explore what crystals we can construct
by only using such locally optimal transformations.

## The Additive Simulation

This class encapsulates a current state representing a crystal
and methods to find out what locally optimal transformations
can be applied or to apply said transformations. It is optimized
to be able to support $O(1)$ operations. A simplified definition of
an additive simulation instance is $S_A = (\xi_C, B_0,B_1)$ where
$\xi_C$ is the energy of the current crystal and $B_i$ are the
boundaries, defined as follows:
$$
    B_0 = \{ n \in C \mid l_n > 0 \}
$$
$$
    B_1 = \{ n \not\in C \mid \bar l_n > 0 \}
$$
These are the backwards boundary and forwards boundary respectively.