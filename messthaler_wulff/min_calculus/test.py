from pulp import *

from messthaler_wulff.data.common_lattices import CommonLattice
from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.datastructures.finite_graphs import metric_ball
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.datastructures.lattice import Lattice

log = logging.getLogger("messthaler_wulff")


def solve(graph: Graph, nodes: list[int], atoms: int):
    problem = LpProblem("MyProblem", LpMinimize)

    node_vars = [LpVariable(f"node{graph.repr(node)}", cat="Binary") for i, node in enumerate(nodes)]
    indices = defaultlist(-1)
    for i, node in enumerate(nodes):
        indices[node] = i

    f = [sum(node_vars[indices[neigh]] for neigh in graph.neighbors(node)
             if indices[neigh] != -1) for i, node in enumerate(nodes)]
    contributions = [node_vars[i] * graph.degree(node) - f[i] for i, node in enumerate(nodes)]
    expression = sum(contributions)
    problem += expression
    problem += sum(node_vars) == atoms

    status = problem.solve()
    log.debug(f"Status: {LpStatus[status]}")
    log.debug(f"{value(expression)=}")


def main():
    graph = Lattice(CommonLattice.triangular.value)

    solve(graph, list(metric_ball(graph, 10)), 100)


if __name__ == "__main__":
    main()
