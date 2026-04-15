import sys
from typing import Any

import networkx as nx
from networkx import Graph

from messthaler_wulff.lattice import CommonLattice
from messthaler_wulff.utils import priority_stack


class QBVSimulation:
    INSIDE = 1
    OUTSIDE = 0

    def __init__(self, graph: Graph) -> None:
        check_graph_validity(graph)
        self.graph: Graph = graph
        self.nodes: set[Any] = set()
        self.deltas: dict[Any, int] = {node: self.graph.nodes[node]["weight"] for node in self.graph.nodes}
        self.size: int = 0
        self.energy: int = 0
        self.boundaries = [priority_stack(), priority_stack()]

        for node in self.graph.nodes:
            self.boundaries[self.OUTSIDE].set(node, self.deltas[node])

    def chi(self, node: Any) -> int:
        return 1 if node in self.nodes else 0

    def delta(self, node: Any) -> int:
        delta = self.graph.nodes[node]["weight"]

        for n in self.graph.neighbors(node):
            delta += 2 * self.graph.edges[node, n]["weight"] * self.chi(n)

        return delta

    def is_uniform(self, node: Any) -> bool:
        value = node in self.nodes
        return all(value == (n in self.nodes) for n in self.graph.neighbors(node))

    def toggle(self, node: Any) -> None:
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            self.nodes.add(node)

        chi = self.chi(node)

        for n in self.graph.neighbors(node):
            self.deltas[n] += sign(chi) * 2 * self.graph.edges[node, n]["weight"]
            self.boundaries[self.chi(n)].set(n, self.deltas[n])

        self.size += sign(chi)
        delta = self.deltas[node]
        self.energy += sign(chi) * delta

        self.boundaries[chi].set(node, delta)
        self.boundaries[1 - chi].unset(node)

    def __str__(self) -> str:
        return f"QBVS {self.energy}/{self.size}"


def sign(x: int) -> int:
    return 2 * x - 1


def check_graph_validity(graph: Graph):
    error = False

    if graph.is_directed():
        print("The graph is directed")
        error = True

    if not nx.is_weighted(graph):
        print("Not all edges in the graph have weights")
        error = True

    for a, data in graph.nodes(data=True):
        if "weight" not in data:
            print(f"The node {a} in the graph was not assigned a weight")
            error = True

    for a, b in graph.edges:
        if graph.edges[a, b]["weight"] != graph.edges[b, a]["weight"]:
            print(f"The edge ({a}, {b}) has a different weight to ({b}, {a})")
            error = True

    if error:
        sys.exit(-1)


class ID:
    def __getitem__(self, item):
        return item


def main():
    g = CommonLattice.square.value.graph(2)

    sim = QBVSimulation(g)
    print(next(iter(g)))
    print(sim)

    for node in [(0, 0), (0, 0), (0, 0), (1, 0), (0, 1), (1, 1)]:
        sim.toggle(node)
        print(sim)

    # nx.draw(g, ID())
    # plt.show()


if __name__ == "__main__":
    main()
