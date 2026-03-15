import logging

from pyscipopt import Model

from messthaler_wulff.data.common_lattices import CommonLattice
from messthaler_wulff.datastructures.defaultlist import defaultlist
from messthaler_wulff.datastructures.finite_graphs import metric_ball
from messthaler_wulff.datastructures.graph import Graph
from messthaler_wulff.datastructures.lattice import Lattice

log = logging.getLogger("messthaler_wulff")


def solve(graph: Graph, nodes: list[int], atoms: int):
    model = Model("Test")
    variables = [model.addVar(f"node-{graph.repr(node)}", "B") for i, node in enumerate(nodes)]
    indices = defaultlist(-1)
    for i, node in enumerate(nodes):
        indices[node] = i

    f = [sum(variables[indices[neigh]] for neigh in graph.neighbors(node)
             if indices[neigh] != -1) for i, node in enumerate(nodes)]
    contributions = [variables[i] * (graph.degree(node) - f[i]) for i, node in enumerate(nodes)]
    expression = sum(contributions)
    constraint = sum(variables) == atoms

    z = model.addVar("z", "I")

    model.setObjective(z, sense="minimize")
    model.addCons(constraint)
    model.addCons(z >= expression)
    model.optimize()

    for v in variables:
        match model.getVal(v):
            case 0:
                pass
            case 1:
                log.debug(v)
            case _:
                assert False, model.getVal(v)
    log.debug(f"{model.getObjVal()=}")


def main():
    graph = Lattice(CommonLattice.fcc.value)

    solve(graph, list(metric_ball(graph, 10)), 80)


if __name__ == "__main__":
    main()
