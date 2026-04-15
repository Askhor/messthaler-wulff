import random
from typing import Iterator, Any

from networkx import Graph

from messthaler_wulff.sim.qbv_simulation import QBVSimulation


class Anneal:
    def __init__(self, graph: Graph, upper_bound: int) -> None:
        assert 0 < upper_bound <= len(graph), upper_bound

        self.graph = graph
        self.sim = QBVSimulation(graph)
        self.upper_bound = upper_bound

    def random_direction(self) -> int:
        while True:
            if self.sim.size <= 0:
                return self.sim.OUTSIDE
            elif self.sim.size >= self.upper_bound:
                return self.sim.INSIDE
            else:
                return random.getrandbits(1)

    def walk_random_node(self) -> Any:
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
        yield self.sim
        while True:
            self.walk_random_node()
            yield self.sim
