import random
import time
from collections import defaultdict
from typing import Iterator, Any

import tqdm
from networkx import Graph

from messthaler_wulff import utils
from messthaler_wulff.lattice import CommonLattice
from messthaler_wulff.sim.qbv_simulation import QBVSimulation, sign
from messthaler_wulff.utils import setr


class Anneal:
    INSIDE = 0
    OUTSIDE = 1

    def __init__(self, graph: Graph, upper_bound: int) -> None:
        assert 0 < upper_bound <= len(graph), upper_bound

        self.graph = graph
        self.sim = QBVSimulation(graph)
        self.upper_bound = upper_bound

        self.boundaries: tuple[setr[Any], setr[Any]] = setr(), setr()
        self.boundaries[self.OUTSIDE].add(next(iter(graph.nodes)))

    def random_direction(self) -> int:
        while True:
            if self.sim.size <= 0:
                return self.OUTSIDE
            elif self.sim.size >= self.upper_bound:
                return self.INSIDE
            else:
                return random.getrandbits(1)

    def walk_random_node(self) -> Any:
        direction = self.random_direction()
        forwards = self.boundaries[direction]
        backwards = self.boundaries[1 - direction]

        assert len(forwards)
        node = forwards.random()

        delta = sign(direction) * self.sim.delta(node)

        # Whether to accept the change
        if random.random() > utils.clamped_line(-3, 0.8, 2, 0.2, delta):
            return self.walk_random_node()

        for n in self.graph.neighbors(node):
            chi = self.sim.chi(n)
            self.boundaries[1 - chi].add(n)

        forwards.remove(node)
        backwards.add(node)
        self.sim.toggle(node)

        return node

    def generate_states(self) -> Iterator[QBVSimulation]:
        yield self.sim
        while True:
            self.walk_random_node()
            yield self.sim


def main():
    g = CommonLattice.fcc.value.graph(20)

    a = Anneal(g, 10)
    best = defaultdict(lambda: 1000000000)

    start = time.time()

    for s in tqdm.tqdm(a.generate_states()):
        if s.energy < best[s.size]:
            best[s.size] = s.energy
        if time.time() - start > 10:
            break

    print(*best.items())


if __name__ == '__main__':
    main()
