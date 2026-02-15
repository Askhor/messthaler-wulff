from hypothesis import strategies as st, given

from messthaler_wulff.graph import UniformNeighborhood, Lattice


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
