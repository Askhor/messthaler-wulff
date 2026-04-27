import sys
from typing import Any

import networkx as nx
from networkx import Graph

from messthaler_wulff import mylog
from messthaler_wulff.utils import priority_stack


class QBVSimulation:
    """QBV stands for Quadratic Binary Vector, simulating quadratic forms on binary vectors."""
    INSIDE = 1
    OUTSIDE = 0

    def __init__(self, graph: Graph) -> None:
        """
                Initialize the QBV simulation with a given graph.

                Args:
                    graph (Graph): A NetworkX graph representing the binary vector structure.

                Raises:
                    SystemExit: If the graph is invalid due to being directed or lacking weights.
                """
        check_graph_validity(graph)
        self.graph: Graph = graph
        self.nodes: set[Any] = set()
        self.deltas: dict[Any, int] = {node: self.graph.nodes[node]["weight"] for node in
                                       mylog.tqdm(self.graph.nodes, desc="Calculating initial deltas")}
        self.size: int = 0
        self.energy: int = 0
        self.boundaries = [priority_stack(), priority_stack()]

        for node in mylog.tqdm(self.graph.nodes, desc="Initialising outside boundary"):
            self.boundaries[self.OUTSIDE].set(node, self.deltas[node])

    def chi(self, node: Any) -> int:
        """
              Compute the chi value for a given node.

              Args:
                  node (Any): The node for which to compute chi.

              Returns:
                  int: 1 if the node is in the current QBV state, 0 otherwise.
              """
        return 1 if node in self.nodes else 0

    def delta(self, node: Any) -> int:
        delta = self.graph.nodes[node]["weight"]

        for n in self.graph.neighbors(node):
            delta += 2 * self.graph.edges[node, n]["weight"] * self.chi(n)

        return delta

    def is_uniform(self, node: Any) -> bool:
        """
                Check if a node is uniform regarding its neighbors.

                Args:
                    node (Any): The node to check.

                Returns:
                    bool: True if all neighbors have the same QBV state as the node; otherwise False.
                """
        value = node in self.nodes
        return all(value == (n in self.nodes) for n in self.graph.neighbors(node))

    def toggle(self, node: Any) -> None:
        """
                Toggle the state of a node between inside and outside.

                Args:
                    node (Any): The node to toggle.
                """
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
    """
        Check if the provided graph is valid for the QBV simulation.

        Args:
            graph (Graph): The graph to validate.

        Raises:
            SystemExit: If the graph is invalid (directed, unweighted edges, or inconsistent weights).
        """
    error = False

    if graph.is_directed():
        print("The graph is directed")
        error = True

    if not nx.is_weighted(graph):
        print("Not all edges in the graph have weights")
        error = True

    for a, data in mylog.tqdm(graph.nodes(data=True), desc="Checking nodes"):
        if "weight" not in data:
            print(f"The node {a} in the graph was not assigned a weight")
            error = True

    for a, b in mylog.tqdm(graph.edges, desc="Checking edges"):
        if graph.edges[a, b]["weight"] != graph.edges[b, a]["weight"]:
            print(f"The edge ({a}, {b}) has a different weight to ({b}, {a})")
            error = True

    if error:
        sys.exit(-1)