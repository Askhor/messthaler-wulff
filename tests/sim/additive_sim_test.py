import random

from hypothesis import given, strategies as st

from messthaler_wulff.sim.additive_simulation import AdditiveSimulation, Mode
from messthaler_wulff.data.common_lattices import CommonLattice
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.datastructures.lattice import Lattice

strategy_graph = (st.one_of(list(map(st.just, CommonLattice)))
                  .map(lambda l: l.value)
                  .map(Lattice))


@given(strategy_graph)
def test_init(graph: Graph):
    sim = AdditiveSimulation(graph)
    sim.test_invariants()


@given(strategy_graph, st.integers(min_value=10, max_value=100))
def test_random(graph: Graph, steps: int):
    sim = AdditiveSimulation(graph)

    for i in range(steps):
        mode = random.choice([Mode.BACKWARDS, Mode.FORWARDS])
        if sim.size == 0:
            mode = Mode.FORWARDS
        node = random.choice(sim.next(mode))
        sim.toggle(node)
        sim.test_invariants()