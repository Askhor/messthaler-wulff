from collections import deque
from enum import Enum
from typing import Sequence, Self

import networkx as nx

type Vector = Sequence[int]


class UniformNeighborhood:
    """A neighborhood of nodes in a graph that has the same degree and structure at every point"""

    def __init__(self, neighbors: list[Vector]) -> None:
        self.dimension = len(neighbors[0])
        assert all(len(v) == self.dimension for v in neighbors)
        self._neighbors = neighbors
        self.degree = len(self._neighbors)
        self.zero = tuple([0] * self.dimension)

    def neighbor(self, node: Vector, index: int) -> Vector:
        neighbor = self._neighbors[index]
        assert len(node) == len(neighbor), f"Dimension mismatch between {node} and {neighbor}"

        return tuple(node[i] + neighbor[i] for i in range(len(node)))

    @classmethod
    def from_basis(cls, basis: list[Vector]) -> Self:
        """This function inserts the inverses of the basis vectors"""
        return cls([*basis, *(tuple(map(lambda x: -x, v)) for v in basis)])

    def graph(self, radius: int) -> nx.Graph:
        g = nx.Graph()
        g.add_node(self.zero, weight=self.degree, radius=0)

        queue = deque([self.zero])
        visited = set()

        while len(queue) > 0:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            r = g.nodes[node]["radius"]

            if r >= radius: continue

            for i in range(self.degree):
                n = self.neighbor(node, i)
                g.add_node(n, weight=self.degree, radius=r + 1)
                g.add_edge(node, n, weight=-1)
                queue.append(n)

        return g


class CommonLattice(Enum):
    square = UniformNeighborhood.from_basis([
        [1, 0],
        [0, 1]])

    cubic = UniformNeighborhood.from_basis([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]])

    triangular = UniformNeighborhood.from_basis([
        [1, 0],
        [1, 1],
        [0, 1]])

    fcc = UniformNeighborhood.from_basis([
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (-1, 0, 1), (1, -1, 0), (0, 1, -1)])
