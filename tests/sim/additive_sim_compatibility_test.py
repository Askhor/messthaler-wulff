import random

from hypothesis import given, strategies as st

from messthaler_wulff import fcc_transform
from messthaler_wulff.sim.additive_simulation import AdditiveSimulation, Mode
from messthaler_wulff.data.common_lattices import CommonLattice
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.datastructures.lattice import Lattice

strategy_graph = (st.one_of(list(map(st.just, CommonLattice)))
                  .map(lambda l: l.value)
                  .map(Lattice))

from messthaler_wulff._additive_simulation import OmniSimulation, SimpleNeighborhood


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
        sim.toggle(node)
        sim2.set_atom(node, sim2.boundaries[mode.index].atom2energy[node], mode.index)


@given(st.lists(
    st.tuples(
        st.one_of(list(map(st.just, Mode))),
        st.integers(min_value=0, max_value=10_000),
    ), max_size=3000
))
def test_compatibility2(steps: list[tuple[Mode, int]]):
    graph = Lattice(CommonLattice.fcc.value)
    sim = AdditiveSimulation(graph)
    sim2 = OmniSimulation(SimpleNeighborhood(fcc_transform()), None, (0, 0, 0, 0))

    def intern(n):
        return graph.intern(tuple(n[1:]))

    assert frozenset(sim.next(Mode.FORWARDS)) == frozenset(map(intern, sim2.next_atoms(1)))

    for i, (mode, index) in enumerate(steps):
        if sim.size == 0:
            mode = Mode.FORWARDS

        if sim.size > 0:
            assert frozenset(sim.next(Mode.BACKWARDS)) == frozenset(map(intern, sim2.next_atoms(0)))
        assert frozenset(sim.next(Mode.FORWARDS)) == frozenset(map(intern, sim2.next_atoms(1)))

        atom, energy = sim2.next_atom(lambda l: index % l, mode.index)
        assert isinstance(atom, tuple)
        assert isinstance(energy, int)
        sim2.adjust_atom_count(mode.index)
        sim2.set_atom(atom, energy, mode.index)
        node = intern(atom)
        sim.toggle(node)


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


del test_compatibility
del test_compatibility2
del test_weirdness
del test_weirdness2
