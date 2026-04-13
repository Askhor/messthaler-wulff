from typing import Sequence, Self

import numpy as np

from messthaler_wulff.datastructures import Universe
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.decorators import hacky_instance_cache

type Vector = Sequence[int]





class Lattice(Graph, Universe[Vector, int]):
    """A graph given by a neighborhood and all possible translations of it"""

    def __init__(self, neighborhood: UniformNeighborhood) -> None:
        self.neighborhood = neighborhood
        self.keys: dict[Vector, int] = {neighborhood.zero: Graph.ZERO}
        self.values: list[Vector] = [neighborhood.zero]
        self._neighbors: list[tuple[int]] = []

    def intern(self, node: Vector) -> int:
        """Get the canonical representation of a vector for this lattice"""
        assert len(
            node) == self.neighborhood.dimension, f"Vector {node} is not of dimension {self.neighborhood.dimension}"

        if node in self.keys:
            return self.keys[node]

        key = len(self.values)
        self.values.append(node)
        self.keys[node] = key
        return key

    def repr(self, node: int) -> Vector:
        assert isinstance(node, int)
        assert self.exists(node)
        return self.values[node]

    def exists(self, node: int) -> bool:
        return node < len(self.values)

    @property
    def max_degree(self) -> int:
        return self.neighborhood.degree

    @property
    def size(self) -> int:
        return -1

    @hacky_instance_cache("_neighbors")
    def neighbors(self, node: int) -> Sequence[int]:
        assert isinstance(node, int)
        assert self.exists(node)

        value = self.values[node]
        neighbors = tuple(
            self.intern(self.neighborhood.neighbor(value, i))
            for i in range(self.neighborhood.degree))

        assert len(
            neighbors) == self.neighborhood.degree, f"Should have {self.neighborhood.degree} neighbors, not {len(neighbors)}"

        return neighbors

    def walk_path(self, node: int, indices: Sequence[int]) -> int:
        for i in indices:
            node = self.neighbors(node)[i]
        return node
