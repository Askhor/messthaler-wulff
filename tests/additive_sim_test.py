import random

from hypothesis import given, strategies as st

from messthaler_wulff.additive_simulation import AdditiveSimulation, Mode
from messthaler_wulff.common_lattices import CommonLattice
from messthaler_wulff.graph import Graph, Lattice

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


from messthaler_wulff._additive_simulation import OmniSimulation


@given(strategy_graph, st.integers(min_value=10, max_value=100))
def test_compatibility(graph: Graph, steps: int):
    sim = AdditiveSimulation(graph)
    sim2 = OmniSimulation(
        lambda x: graph.neighbors(x), lambda: graph.max_degree, 0
    )

    for i in range(steps):
        mode = random.choice([Mode.BACKWARDS, Mode.FORWARDS])
        if sim.size == 0:
            mode = Mode.FORWARDS
        assert frozenset(sim.next(mode)) == frozenset(sim2.next_atoms(mode.index))
        node = random.choice(sim.next(mode))
        sim.move_to_boundary(node, mode)
        sim2.set_atom(node, sim2.boundaries[mode.index].atom2energy[node], mode.index)


def test_weirdness():
    graph = Lattice(CommonLattice.fcc.value)
    sim = AdditiveSimulation(graph)
    sim2 = OmniSimulation(
        lambda x: graph.neighbors(x), lambda: graph.max_degree, 0
    )

    for i in range(100_000):
        assert frozenset(sim.next(Mode.FORWARDS)) == frozenset(sim2.next_atoms(Mode.FORWARDS.index))
        assert frozenset(sim.boundary(Mode.BACKWARDS)) == frozenset(
            sim2.boundaries[Mode.BACKWARDS.index].atom2energy.keys())
        assert sim.energy == sim2.energy

        node = random.choice(sim.next(Mode.FORWARDS))

        assert sim.energy_delta(node, Mode.FORWARDS) == sim2.boundaries[Mode.FORWARDS.index].atom2energy[node]
        if sim.energy_delta(node, Mode.FORWARDS) > 0:
            break

        sim.toggle(node)
        sim2.set_atom(node, sim2.boundaries[Mode.FORWARDS.index].atom2energy[node], Mode.FORWARDS.index)


def test_weirdness2():
    graph = Lattice(CommonLattice.fcc.value)
    sim = AdditiveSimulation(graph)
    sim2 = OmniSimulation(
        lambda x: graph.neighbors(x), lambda: graph.max_degree, 0
    )

    for i in range(100_000):
        assert frozenset(sim.next(Mode.FORWARDS)) == frozenset(sim2.next_atoms(Mode.FORWARDS.index))
        assert frozenset(sim.boundary(Mode.BACKWARDS)) == frozenset(
            sim2.boundaries[Mode.BACKWARDS.index].atom2energy.keys())
        assert sim.energy == sim2.energy

        # node = random.choice(sim.next(Mode.FORWARDS))
        node, _ = sim2.next_atom(lambda l: random.randrange(l), Mode.FORWARDS.index)

        assert sim.energy_delta(node, Mode.FORWARDS) == sim2.boundaries[Mode.FORWARDS.index].atom2energy[node]
        if sim.energy_delta(node, Mode.FORWARDS) > 0:
            break

        sim.toggle(node)
        sim2.set_atom(node, sim2.boundaries[Mode.FORWARDS.index].atom2energy[node], Mode.FORWARDS.index)
