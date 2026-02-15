from hypothesis import strategies as st, given

from messthaler_wulff.common_lattices import CommonLattice
from messthaler_wulff.graph import UniformNeighborhood, Lattice, Graph
from messthaler_wulff.priority_stack import defaultlist

strategy_graph = (st.one_of(list(map(st.just, CommonLattice)))
                  .map(lambda l: l.value)
                  .map(Lattice))


def test_uniform_neighborhood():
    n = UniformNeighborhood.from_basis([
        [0, 1],
        [1, 0]])
    n._neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    assert n.neighbor((0, 0), 0) == (0, 1)
    assert n.neighbor((0, 0), 1) == (1, 0)
    assert n.neighbor((0, 0), 2) == (0, -1)
    assert n.neighbor((0, 0), 3) == (-1, 0)

    assert n.neighbor((1, -1), 0) == (1, 0)
    assert n.neighbor((1, -1), 1) == (2, -1)
    assert n.neighbor((1, -1), 2) == (1, -2)
    assert n.neighbor((1, -1), 3) == (0, -1)


@given(st.lists(st.integers(), min_size=2, max_size=2).map(lambda l: tuple(l)))
def test_cubic_lattice(node: tuple):
    n = UniformNeighborhood.from_basis([
        [0, 1],
        [1, 0]])
    l = Lattice(n)

    key = l.intern(node)

    assert l.walk_path(key, [0, 2]) == key
    assert l.walk_path(key, [0, 1, 2, 3]) == key


@given(st.lists(st.integers(), min_size=2, max_size=2).map(lambda l: tuple(l)))
def test_hex_lattice(node: tuple):
    n = UniformNeighborhood.from_basis([
        [1, 0],
        [1, 1],
        [0, 1]])
    l = Lattice(n)

    key = l.intern(node)

    assert l.walk_path(key, [0, 3]) == key
    assert l.walk_path(key, [0, 2, 4]) == key


class DiscoverNeighbors:
    def __init__(self, lattice: Lattice, max_distance: int):
        self.max_distance = max_distance
        self.lattice: Lattice = lattice
        self.large: int = 2 ** 30
        self._distance = defaultlist(self.large)
        self._distance[0] = 0
        self._stack: list[int] = [0]

        self.discover()

    def discover(self):
        while len(self._stack) > 0:
            node = self._stack.pop()
            if self._distance[node] > self.max_distance:
                continue

            for n in self.lattice.neighbors(node):
                if self._distance[n] > self._distance[node] + 1:
                    self._distance[n] = self._distance[node] + 1
                    self._stack.append(n)


@given(strategy_graph, st.lists(st.integers(min_value=0, max_value=100), min_size=5, max_size=10))
def test_neighbor_gen(lattice: Lattice, path: list[int]):
    DiscoverNeighbors(lattice, len(path))
    before = frozenset(lattice._neighbors)
    lattice.walk_path(Graph.ZERO, [x % lattice.max_degree for x in path])
    assert before == frozenset(lattice._neighbors)
