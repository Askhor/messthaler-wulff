import math
from collections import defaultdict
from functools import partial
from typing import Sequence, Iterable

from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.decorators import compose


class FiniteGraph(Graph):
    def __init__(self) -> None:
        self._max_degree: int = 0
        self._neighbors: list[list[int]] = [list()]

    def node(self) -> int:
        new_node = len(self._neighbors)
        self._neighbors.append([])
        return new_node

    def _add_neighbor(self, node: int, neighbor: int) -> None:
        ns = self._neighbors[node]
        ns.append(neighbor)

        if len(ns) > self._max_degree:
            self._max_degree = len(ns)

    def edge(self, a: int, b: int) -> None:
        assert a != b
        assert not self.is_edge(a, b)

        self._add_neighbor(a, b)
        self._add_neighbor(b, a)

    def try_edge(self, a: int, b: int) -> None:
        assert a != b
        if self.is_edge(a, b): return
        self.edge(a, b)

    @property
    def size(self) -> int:
        return len(self._neighbors)

    @property
    def max_degree(self) -> int:
        return self._max_degree

    def neighbors(self, node: int) -> Sequence[int]:
        return self._neighbors[node]


def subgraph(graph: Graph, nodes: Iterable[int]) -> Graph:
    out = FiniteGraph()
    new_nodes: defaultdict[int, int] = defaultdict(out.node)
    new_nodes[0] = Graph.ZERO

    for node in nodes:
        new_node = new_nodes[node]
        for n in graph.neighbors(node):
            new_n = new_nodes[n]
            out.try_edge(new_node, new_n)

    return out


def metric_ball(graph: Graph, radius: int, center: int = Graph.ZERO) -> Iterable[int]:
    distances = defaultlist(math.inf)
    distances[0] = 0

    visited = set()
    stack = [0]

    while len(stack) > 0:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)

        yield node

        for neighbor in graph.neighbors(node):
            if distances[node] + 1 < distances[neighbor]:
                distances[neighbor] = distances[node] + 1

            if distances[neighbor] <= radius:
                stack.append(neighbor)


@partial(compose, "\n".join)
def visualise_graph(graph: Graph) -> str:
    assert graph.size > 0
    visited = set()
    stack = [0]

    while len(stack) > 0:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)

        yield f"Node {node} {graph.neighbors(node)}"

        for neighbor in graph.neighbors(node):
            stack.append(neighbor)
