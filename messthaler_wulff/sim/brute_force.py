from typing import Any

from networkx import Graph

from messthaler_wulff.sim.qbv_simulation import QBVSimulation


def _gen_impl(sim: QBVSimulation, nodes: list[Any], index: int):
    """
        Recursive implementation to generate all possible states of the QBV simulation by toggling nodes.

        Args:
            sim (QBVSimulation): The current QBV simulation instance.
            nodes (list[Any]): A list of nodes to toggle.
            index (int): The current index in the list of nodes.

        Yields:
            QBVSimulation: The simulation state after toggling nodes.
        """
    if index == len(nodes):
        yield sim
        return

    node = nodes[index]

    yield from _gen_impl(sim, nodes, index + 1)
    sim.toggle(node)
    yield from _gen_impl(sim, nodes, index + 1)
    sim.toggle(node)


def generate_states(graph: Graph):
    """
        Generate all possible states of the QBV simulation for a given graph.

        Args:
            graph (Graph): A NetworkX graph representing the structure to simulate.

        Yields:
            QBVSimulation: The current state of the QBV simulation as all nodes are toggled.
        """
    sim = QBVSimulation(graph)
    nodes = list(graph.nodes)

    yield from _gen_impl(sim, nodes, 0)
