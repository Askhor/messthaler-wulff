import abc
from typing import Protocol, Self

from messthaler_wulff.datastructures.graph import Graph


class Result(list[int]):

    @staticmethod
    def better(a: int, b: int) -> int:
        if a == -1:
            return b
        if b == -1:
            return a
        return min(a, b)

    @classmethod
    def initial(cls, n: int) -> Self:
        return cls([-1] * n)

    def combine(self, other: Self) -> Self:
        return Result(map(self.better, zip(self, other)))

    def put(self, n: int, E: int):
        if n >= len(self): return
        self[n] = self.better(self[n], E)


class Solver[T: Graph](Protocol):
    @abc.abstractmethod
    @staticmethod
    def solve(graph: Graph, nodes: list[int], n: int) -> Result:
        ...
