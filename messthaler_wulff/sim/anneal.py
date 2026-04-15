import random
import time
from collections import defaultdict
from typing import Iterator, Any

import tqdm
from networkx import Graph

from messthaler_wulff.lattice import CommonLattice
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


def main():
    k = 200
    n = 100
    t = 1000
    g = CommonLattice.fcc.value.graph(n)

    a = Anneal(g, k)
    best = defaultdict(lambda: 1000000000)

    pbar = tqdm.tqdm(a.generate_states())

    start = time.time()
    last_log = time.time()


    for s in pbar:
        if s.energy < best[s.size]:
            best[s.size] = s.energy
        if time.time() - start > t:
            break
        if time.time() - last_log > 1:
            last_log = time.time()
            pbar.set_postfix({str(k): str(v) for k,v in best.items()})


    print(*best.items())


if __name__ == '__main__':
    main()
