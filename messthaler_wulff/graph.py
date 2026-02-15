import abc
from typing import Self, Sequence

import numpy as np

from messthaler_wulff.decorators import hacky_instance_cache

type Key = int
type Vector = Sequence[int]


class Graph(abc.ABC):
    """Represent an abstract graph. Can be subclassed to create finite graphs, lattices, etc."""
    ZERO = 0

    @property
    @abc.abstractmethod
    def max_degree(self) -> int:
        pass

    def degree(self, node: Key) -> int:
        return len(self.neighbors(node))

    @abc.abstractmethod
    def neighbors(self, node: Key) -> Sequence[Key]:
        """The index-th neighbor of the node 'node'. The index may be
        at most one less than what 'degree' returns for this node"""
        pass


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

    @classmethod
    def from_transform(cls, transform: np.ndarray) -> Self:
        raise NotImplementedError()

class Lattice(Graph):
    """A graph given by a neighborhood and all possible translations of it"""

    def __init__(self, neighborhood: UniformNeighborhood) -> None:
        self.neighborhood = neighborhood
        self.keys: dict[Vector, Key] = {neighborhood.zero: Graph.ZERO}
        self.values: list[Vector] = [neighborhood.zero]
        self._neighbors: list[tuple[Key]] = []


    def intern(self, node: Vector) -> Key:
        """Get the canonical representation of a vector for this lattice"""
        assert len(node) == self.neighborhood.dimension, f"Vector {node} is not of dimension {self.neighborhood.dimension}"

        if node in self.keys:
            return self.keys[node]

        key = len(self.values)
        self.values.append(node)
        self.keys[node] = key
        return key

    def exists(self, node: Key) -> bool:
        return node < len(self.values)

    @property
    def max_degree(self) -> int:
        return self.neighborhood.degree

    @hacky_instance_cache("_neighbors")
    def neighbors(self, node: Key) -> Sequence[Key]:
        assert isinstance(node, int)
        assert self.exists(node)

        value = self.values[node]
        neighbors = tuple(
            self.intern(self.neighborhood.neighbor(value, i))
            for i in range(self.neighborhood.degree))

        assert len(
            neighbors) == self.neighborhood.degree, f"Should have {self.neighborhood.degree} neighbors, not {len(neighbors)}"

        return neighbors

    def walk_path(self, node: Key, indices: Sequence[int]) -> Key:
        for i in indices:
            node = self.neighbors(node)[i]
        return node
