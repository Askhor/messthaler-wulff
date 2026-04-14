import math
from typing import Iterable

from messthaler_wulff.datastructures.graph import Graph

from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.decorators import compose


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
