import random
from typing import Iterator, Any

from networkx import Graph

from messthaler_wulff.sim.qbv_simulation import QBVSimulation


class Anneal:
    """A class to perform simulated annealing on a given graph using QBVSimulation."""

    def __init__(self, graph: Graph, upper_bound: int) -> None:
        """
                Initialize the annealing process with a graph and an upper bound on node size.

                Args:
                    graph (Graph): A NetworkX graph representing the structure to be annealed.
                    upper_bound (int): The maximum number of nodes allowed in the QBV state.

                Raises:
                    AssertionError: If the upper bound is not within a valid range (0 < upper_bound <= graph size).
                """
        assert 0 < upper_bound <= len(graph), upper_bound

        self.graph = graph
        self.sim = QBVSimulation(graph)
        self.upper_bound = upper_bound

    def random_direction(self) -> int:
        """
                Randomly determine the direction for the next move in the annealing process.

                Returns:
                    int: 1 (INSIDE) if the simulation size exceeds the upper bound,
                         0 (OUTSIDE) if the simulation size is less than or equal to 0,
                         or a random bit (0 or 1) indicating the next direction.
                """
        while True:
            if self.sim.size <= 0:
                return self.sim.OUTSIDE
            elif self.sim.size >= self.upper_bound:
                return self.sim.INSIDE
            else:
                return random.getrandbits(1)

    def walk_random_node(self) -> Any:
        """
                Randomly select a node to toggle in the QBV simulation while ensuring validity.

                Returns:
                    Any: The node that was toggled.

                Raises:
                    AssertionError: If the toggled node does not meet size constraints.
                """
        direction = self.random_direction()
        forwards = self.sim.boundaries[direction]

        if direction == self.sim.OUTSIDE:
            level = forwards.min()
            assert level.random() not in self.sim.nodes
        else:
            level = forwards.max()
            assert level.random() in self.sim.nodes

        node = level.random()
        self.sim.toggle(node)

        assert 0 <= self.sim.size <= self.upper_bound, self.sim.size

        return node

    def generate_states(self) -> Iterator[QBVSimulation]:
        """
                Generate states of the QBV simulation iteratively.

                Yields:
                    Iterator[QBVSimulation]: The current state of the QBV simulation.
                """
        yield self.sim
        while True:
            self.walk_random_node()
            yield self.sim
