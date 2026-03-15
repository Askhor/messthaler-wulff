import abc
from typing import Sequence


class Graph(abc.ABC):
    """Represent an abstract graph. Can be subclassed to create finite graphs, lattices, etc."""
    ZERO = 0  # The zero node must always exist in every graph (no empty graph)

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """The size of this graph or -1 if it is infinite"""
        ...

    @property
    @abc.abstractmethod
    def max_degree(self) -> int:
        ...

    @abc.abstractmethod
    def neighbors(self, node: int) -> Sequence[int]:
        ...

    def degree(self, node: int) -> int:
        return len(self.neighbors(node))

    def is_edge(self, a: int, b: int) -> bool:
        x = b in self.neighbors(a)
        y = a in self.neighbors(b)

        assert x == y
        return x
