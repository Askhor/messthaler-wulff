import tqdm

from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.sim.crystal import Crystal
from messthaler_wulff.sim.energy import SurfaceEnergy
from messthaler_wulff.sim.quantity import CrystalQuantity
from messthaler_wulff.solvers import Result


def solve_part(graph: Graph, c: Crystal, E: SurfaceEnergy, nodes: list[int], i: int) -> Result:
    if i < 0:
        yield
        return
    k = nodes[i]

    yield from solve_part(graph, c, E, nodes, i - 1)
    c.toggle(k)
    yield from solve_part(graph, c, E, nodes, i - 1)
    c.toggle(k)


def solve(graph: Graph, nodes: list[int], n: int) -> Result:
    c = Crystal(graph)
    E: CrystalQuantity = SurfaceEnergy(c)

    res = Result.initial(n)

    for _ in tqdm.tqdm(solve_part(graph, c, E, nodes, len(nodes) - 1), total=2 ** len(nodes)):
        res.put(c.size, E.value)

    return res
